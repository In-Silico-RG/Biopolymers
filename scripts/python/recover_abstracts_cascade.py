#!/usr/bin/env python3
"""Recover missing abstracts through a cascade of free sources.

Crossref was tried first and recovered only 2.1%. The cause is not the script: Elsevier,
which publishes much of this field, deposits no abstracts to Crossref at all. Verified
directly on three Elsevier DOIs, none of which carries an `abstract` key.

Semantic Scholar does hold them, and takes 100 DOIs per request instead of one, so it
leads the cascade. Europe PMC follows for the biomedical-adjacent remainder. Crossref
results already fetched are reused rather than re-requested.

Output: data/processed/recovered_abstracts.jsonl, one {id, doi, abstract, source} per line,
appended as it goes so an interrupted run resumes instead of restarting.
"""
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "data/raw/openalex/records"
PROC = ROOT / "data/processed"
OUT = PROC / "recovered_abstracts.jsonl"
CROSSREF = PROC / "crossref_abstracts.jsonl"
MAILTO = "aldo.combariza@unisucre.edu.co"

S2_BATCH = "https://api.semanticscholar.org/graph/v1/paper/batch"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
WS = re.compile(r"\s+")


def clean(t):
    return WS.sub(" ", (t or "")).strip()


def targets():
    """Distinct harvested works that have a DOI and no OpenAlex abstract."""
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
                doi = (r.get("doi") or "").replace("https://doi.org/", "").strip().lower()
                if doi:
                    out[wid] = doi
    return out


def load_done():
    """Everything already *attempted*, not only everything recovered.

    Recording only successes made every failed lookup be retried on the next run: a second
    pass spent thousands of calls re-asking for abstracts that three sources had already
    said they did not have. A work that has been through the full cascade is done, whatever
    the outcome.
    """
    done = {}
    for path, default in ((CROSSREF, "crossref"), (OUT, "?")):
        if not path.exists():
            continue
        for line in path.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("abstract"):
                done[r["id"]] = (r.get("source", default), r["abstract"])
            elif r.get("source") == "exhausted":
                done[r["id"]] = ("exhausted", "")
    return done


def s2_batch(dois, tries=5):
    for a in range(tries):
        try:
            r = requests.post(S2_BATCH, params={"fields": "abstract,externalIds"},
                              json={"ids": [f"DOI:{d}" for d in dois]}, timeout=90)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(4 * (a + 1))
                continue
            return None
        except requests.RequestException:
            time.sleep(4 * (a + 1))
    return None


def epmc_one(item, tries=3):
    wid, doi = item
    for a in range(tries):
        try:
            r = requests.get(EPMC,
                             params={"query": f'DOI:"{doi}"', "format": "json",
                                     "resultType": "core", "pageSize": 1},
                             timeout=45,
                             headers={"User-Agent": f"biopolymers (mailto:{MAILTO})"})
            if r.status_code == 200:
                res = r.json().get("resultList", {}).get("result", [])
                return wid, doi, clean(res[0].get("abstractText")) if res else ""
            time.sleep(2 * (a + 1))
        except (requests.RequestException, ValueError):
            time.sleep(2 * (a + 1))
    return wid, doi, ""


def main():
    all_t = targets()
    done = load_done()
    todo = {w: d for w, d in all_t.items() if w not in done}
    print(f"{len(all_t)} works without an OpenAlex abstract; "
          f"{len(done)} already recovered; {len(todo)} to try")

    with OUT.open("a", encoding="utf-8") as fh:
        # --- pass 1: Semantic Scholar, 100 DOIs per request ---
        items = list(todo.items())
        got1 = 0
        for i in range(0, len(items), 100):
            chunk = items[i:i + 100]
            res = s2_batch([d for _, d in chunk])
            if res:
                for (wid, doi), p in zip(chunk, res):
                    ab = clean((p or {}).get("abstract"))
                    if ab:
                        fh.write(json.dumps({"id": wid, "doi": doi, "abstract": ab,
                                             "source": "semantic_scholar"},
                                            ensure_ascii=False) + "\n")
                        todo.pop(wid, None)
                        got1 += 1
            fh.flush()
            print(f"\rS2 {min(i + 100, len(items))}/{len(items)}  recovered {got1}", end="")
            sys.stdout.flush()
            time.sleep(1.1)
        print(f"\rSemantic Scholar recovered {got1} of {len(items)}" + " " * 20)

        # --- pass 2: Europe PMC on what is left ---
        left = list(todo.items())
        got2 = 0
        with ThreadPoolExecutor(max_workers=6) as ex:
            for n, (wid, doi, ab) in enumerate(ex.map(epmc_one, left), 1):
                if ab:
                    fh.write(json.dumps({"id": wid, "doi": doi, "abstract": ab,
                                         "source": "europe_pmc"}, ensure_ascii=False) + "\n")
                    got2 += 1
                else:
                    # Mark the cascade as exhausted for this work so it is not retried.
                    fh.write(json.dumps({"id": wid, "doi": doi, "abstract": "",
                                         "source": "exhausted"}, ensure_ascii=False) + "\n")
                if n % 200 == 0:
                    fh.flush()
                    print(f"\rEPMC {n}/{len(left)}  recovered {got2}", end="")
                    sys.stdout.flush()
        print(f"\rEurope PMC recovered {got2} of {len(left)}" + " " * 20)

    total = len(load_done())
    print(f"\ntotal abstracts recovered: {total} of {len(all_t)} "
          f"({total / len(all_t) * 100:.1f}%)")


if __name__ == "__main__":
    main()
