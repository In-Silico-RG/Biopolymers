#!/usr/bin/env python3
"""Screen OpenAlex records with DeepSeek: is this biopolymer materials research, and
which computational method does it actually use?

This exists because of the contamination measured in docs/01_bibliometric_mapping.md
section 6. The framing terms "biomacromolecule" and "natural polymer" pull protein and
nucleic-acid biophysics into the corpus, where molecular dynamics has been routine for
decades, so part of the measured method share is not biopolymer materials science. A
keyword rule cannot tell the two apart; reading the abstract can.

Every call is cached on a hash of the prompt, so a re-run costs nothing and the screening
is reproducible. The model's answer is data, not instruction: only the fields of the
schema are read, and anything else in the reply is discarded.

Usage:
    screen_abstracts.py <records.jsonl> [--limit N] [--out screened.csv]
"""
import argparse, hashlib, json, os, sys, threading, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path.home() / ".deepseek_cache"
API = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

SYSTEM = """You classify scientific abstracts for a bibliometric study of biopolymers.
Answer ONLY with a JSON object, no prose, no code fence, with exactly these keys:

"materials": true if the work studies a biopolymer as a MATERIAL (its synthesis,
  structure-property relations, processing, blends, composites, films, fibres,
  degradation, or application as a material). false if it studies a biological
  macromolecule for its BIOLOGICAL function (protein folding or function, enzyme
  mechanism, nucleic acid biology, drug binding), which is not biopolymer materials
  science even when the molecule is a natural polymer.
"polymer": the main biopolymer family, one of: cellulose, starch, chitosan, alginate,
  pectin, other_polysaccharide, lignin, pha, pla, protein, nucleic_acid, other, none.
"method": the main computational method, one of: md (molecular dynamics or coarse
  grained), qc (DFT, ab initio, quantum chemistry), qsar (QSAR, QSPR, descriptors,
  chemoinformatics), docking, ml (machine learning, deep learning, neural networks),
  generative (generative models, LLMs, inverse design), solubility (Hansen, COSMO-RS,
  group contribution), other_computational, none.
"experimental": true if the work also reports laboratory experiments.
"confidence": "high", "medium" or "low".

If the abstract is missing or unusable, return every field as null except confidence,
which is "low"."""


_RECOVERED = None


def recovered():
    """Abstracts pulled from Semantic Scholar, Europe PMC and Crossref for records where
    OpenAlex carries none. 4,113 of 9,433 such works were recovered on 2026-09-23, which
    is why the screening is re-run: every share in docs/02 rests on the works that could
    actually be read."""
    global _RECOVERED
    if _RECOVERED is None:
        _RECOVERED = {}
        p = ROOT / "data/processed/recovered_abstracts.jsonl"
        if p.exists():
            for line in p.open(encoding="utf-8"):
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("abstract"):
                    _RECOVERED[r["id"]] = r["abstract"]
    return _RECOVERED


def abstract_of(rec):
    """The record's own abstract, or a recovered one, or empty."""
    a = deabbrev(rec.get("abstract_inverted_index"))
    return a or recovered().get(rec.get("id"), "")


def deabbrev(inv):
    """OpenAlex stores abstracts as an inverted index; rebuild the text."""
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def ask(title, abstract, api_key, retries=4):
    prompt = f"TITLE: {title}\n\nABSTRACT: {abstract[:4000]}"
    key = hashlib.md5((MODEL + SYSTEM + prompt).encode()).hexdigest()
    CACHE.mkdir(exist_ok=True)
    cached = CACHE / f"{key}.json"
    if cached.exists():
        try:
            return json.loads(cached.read_text()), True
        except (json.JSONDecodeError, OSError):
            # Two threads can reach a corrupt entry at once; the second must not die
            # because the first already removed it.
            cached.unlink(missing_ok=True)
    body = {"model": MODEL,
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": prompt}],
            "temperature": 0, "response_format": {"type": "json_object"}}
    for a in range(retries):
        try:
            r = requests.post(API, json=body, timeout=120,
                              headers={"Authorization": f"Bearer {api_key}"})
            if r.status_code == 200:
                txt = r.json()["choices"][0]["message"]["content"]
                out = json.loads(txt)
                # Write through a temp file and rename, so a reader never sees a
                # half-written entry. The corrupt entries that crashed the first run came
                # from concurrent partial writes.
                tmp = cached.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
                tmp.write_text(json.dumps(out), encoding="utf-8")
                tmp.replace(cached)
                return out, False
            if r.status_code in (429, 500, 502, 503):
                time.sleep(3 * (a + 1)); continue
            return {"_error": f"HTTP {r.status_code}: {r.text[:200]}"}, False
        except (requests.RequestException, json.JSONDecodeError) as e:
            time.sleep(3 * (a + 1)); err = e
    return {"_error": f"exhausted retries: {locals().get('err','')}"}, False


FIELDS = ["materials", "polymer", "method", "experimental", "confidence"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("records")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--workers", type=int, default=8,
                    help="parallel requests; calls are independent and cached by prompt "
                         "hash, so order does not matter and a re-run is free")
    args = ap.parse_args()

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        sys.exit("DEEPSEEK_API_KEY is not set")

    import csv
    from concurrent.futures import ThreadPoolExecutor

    src = Path(args.records)
    out = Path(args.out) if args.out else ROOT / "data/processed" / f"screened_{src.stem}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)

    recs = []
    with src.open(encoding="utf-8") as fh:
        for line in fh:
            if args.limit and len(recs) >= args.limit:
                break
            recs.append(json.loads(line))

    done = [0]

    def work(rec):
        title = rec.get("display_name") or rec.get("title") or ""
        abstract = abstract_of(rec)
        res, cached = ask(title, abstract, api_key)
        done[0] += 1
        if done[0] % 50 == 0:
            print(f"\r{done[0]}/{len(recs)}", end=""); sys.stdout.flush()
        return rec, res, cached

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(work, recs))

    hits = sum(c for _, _, c in results)
    with out.open("w", newline="", encoding="utf-8") as oh:
        w = csv.writer(oh)
        w.writerow(["id", "doi", "year", "title"] + FIELDS + ["error"])
        for rec, res, _ in results:
            w.writerow([rec.get("id"), rec.get("doi"), rec.get("publication_year"),
                        rec.get("display_name") or rec.get("title") or ""]
                       + [res.get(f) for f in FIELDS] + [res.get("_error", "")])
    print(f"\r{len(results)} screened ({hits} from cache) -> {out}")


if __name__ == "__main__":
    main()
