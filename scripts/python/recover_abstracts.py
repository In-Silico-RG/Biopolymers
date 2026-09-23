#!/usr/bin/env python3
"""Recover missing abstracts from Crossref for records where OpenAlex has none.

38.5% of the harvested works carry no abstract in OpenAlex, and 99.5% of those do carry a
DOI. Crossref holds an abstract for a good share of them, as JATS XML in the `abstract`
field. Every share reported in docs/02_networks_and_screening.md rests on the works that
could be read, so closing this gap tightens all of them.

Output is data/processed/crossref_abstracts.jsonl, one {doi, id, abstract} per line,
appended as it goes so an interrupted run resumes instead of restarting.
"""
import json, re, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import requests

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "data/raw/openalex/records"
OUT = ROOT / "data/processed/crossref_abstracts.jsonl"
MAILTO = "aldo.combariza@unisucre.edu.co"
API = "https://api.crossref.org/works/"

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")
LEAD = re.compile(r"^\s*(abstract|summary|resumen)\s*[:.\-]?\s*", re.I)


def clean(jats):
    """Crossref abstracts are JATS XML. Strip the markup, keep the prose."""
    if not jats:
        return ""
    t = jats.replace("</jats:p>", " ").replace("</p>", " ")
    t = TAG.sub(" ", t)
    t = (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&quot;", '"').replace("&#x2013;", "-").replace("&nbsp;", " "))
    t = WS.sub(" ", t).strip()
    return LEAD.sub("", t).strip()


def targets():
    """Distinct works that have a DOI and no OpenAlex abstract."""
    out, seen = {}, set()
    for p in sorted(REC.glob("*.jsonl")):
        with p.open(encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                wid = r.get("id")
                if not wid or wid in seen:
                    continue
                seen.add(wid)
                if r.get("abstract_inverted_index"):
                    continue
                doi = (r.get("doi") or "").replace("https://doi.org/", "").strip()
                if doi:
                    out[wid] = doi
    return out


def fetch(item, retries=3):
    wid, doi = item
    for a in range(retries):
        try:
            r = requests.get(API + doi, timeout=45,
                             params={"mailto": MAILTO},
                             headers={"User-Agent": f"biopolymers-bibliometrics (mailto:{MAILTO})"})
            if r.status_code == 200:
                msg = r.json().get("message", {})
                return {"id": wid, "doi": doi, "abstract": clean(msg.get("abstract"))}
            if r.status_code == 404:
                return {"id": wid, "doi": doi, "abstract": "", "error": "404"}
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 * (a + 1)); continue
            return {"id": wid, "doi": doi, "abstract": "", "error": str(r.status_code)}
        except requests.RequestException as e:
            time.sleep(2 * (a + 1)); err = str(e)
    return {"id": wid, "doi": doi, "abstract": "", "error": f"retries: {locals().get('err','')}"}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if OUT.exists():
        with OUT.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    done.add(json.loads(line)["id"])
                except Exception:
                    pass
    todo = [(w, d) for w, d in targets().items() if w not in done]
    print(f"{len(done)} already fetched, {len(todo)} to go")
    n = got = 0
    with OUT.open("a", encoding="utf-8") as oh, ThreadPoolExecutor(max_workers=10) as ex:
        for res in ex.map(fetch, todo):
            oh.write(json.dumps(res, ensure_ascii=False) + "\n")
            n += 1; got += bool(res.get("abstract"))
            if n % 200 == 0:
                oh.flush()
                print(f"\r{n}/{len(todo)}  recovered {got} ({got/n*100:.1f}%)", end="")
                sys.stdout.flush()
    print(f"\r{n}/{len(todo)}  recovered {got} ({got/n*100:.1f}%) -> {OUT}")


if __name__ == "__main__":
    main()
