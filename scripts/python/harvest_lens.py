#!/usr/bin/env python3
"""Harvest the Lens scholarly API into data/raw/lens/.

Lens does have an API, so the manual CSV export in docs/03_source_triangulation.md is the
fallback, not the plan. Once a token exists this script replaces it and the Lens corpus
becomes as reproducible as the OpenAlex one.

Two API constraints shape the code. The offset method refuses to page past 10,000 records,
so anything larger must use the scroll cursor; and a scroll_id lives for only one minute,
so the loop must not pause between pages. Every corpus here is therefore scrolled, and
results are written as they arrive rather than held in memory.

Token: set LENS_API_TOKEN, or write it to ~/.lens_token. Request one at lens.org under
API & Data; the academic trial is the usual route.

Usage:
    harvest_lens.py                 # every block in queries/platform_lens_v1.txt
    harvest_lens.py L1 L5           # only these blocks
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
QFILE = ROOT / "queries" / "platform_lens_v1.txt"
OUT = ROOT / "data/raw/lens"
API = "https://api.lens.org/scholarly/search"

# Fields worth carrying. Mirrors the OpenAlex selection so the two corpora can be
# harmonised without special cases downstream.
INCLUDE = [
    "lens_id", "title", "abstract", "publication_type", "year_published",
    "date_published", "external_ids", "authors", "source", "languages",
    "scholarly_citations_count", "references_count", "fields_of_study",
    "keywords", "chemicals", "funding", "open_access", "is_open_access",
]

LATAM = ("AR OR BO OR BR OR CL OR CO OR CR OR CU OR DO OR EC OR GT OR HN OR MX OR "
         "NI OR PA OR PE OR PR OR PY OR SV OR UY OR VE")
IBERO = LATAM.replace("OR EC OR", "OR EC OR ES OR").replace("OR PY OR", "OR PT OR PY OR")

GEO = {"world": None,
       "latam": f"author.affiliation.address.country_code:({LATAM})",
       "ibero": f"author.affiliation.address.country_code:({IBERO})",
       "colombia": "author.affiliation.address.country_code:(CO)"}


def token():
    t = os.environ.get("LENS_API_TOKEN", "").strip()
    if t:
        return t
    p = Path.home() / ".lens_token"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    sys.exit("No Lens token. Set LENS_API_TOKEN or write it to ~/.lens_token. "
             "Request one at lens.org under API & Data.")


def load_blocks():
    """Parse the frozen query file into {code: query_string}.

    A block is a '## Lx — description' heading followed by its query lines. Lines that
    are comments, filter snippets or the L3 placeholder are skipped, since L3 is built
    here from L1 and L2 rather than stored.
    """
    blocks, code, buf = {}, None, []
    for line in QFILE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s*(L\d+)\b", line)
        if m:
            if code and buf:
                blocks[code] = " ".join(buf).strip()
            code, buf = m.group(1), []
            continue
        if code is None or line.lstrip().startswith("#") or not line.strip():
            continue
        if line.lstrip().startswith(("author.affiliation", "year_published", "(L1)")):
            continue
        buf.append(line.strip())
    if code and buf:
        blocks[code] = " ".join(buf).strip()
    if "L1" in blocks and "L2" in blocks:
        blocks["L3"] = f"({blocks['L1']}) AND ({blocks['L2']})"
    return blocks


def post(body, tok, tries=5):
    for a in range(tries):
        try:
            r = requests.post(API, json=body, timeout=120,
                              headers={"Authorization": f"Bearer {tok}",
                                       "Content-Type": "application/json"})
            if r.status_code in (200, 204):
                return r
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(4 * (a + 1))
                continue
            sys.exit(f"Lens API {r.status_code}: {r.text[:300]}")
        except requests.RequestException:
            time.sleep(4 * (a + 1))
    sys.exit("Lens API: exhausted retries")


def harvest(code, query, geo_name, tok):
    q = query if GEO[geo_name] is None else f"({query}) AND {GEO[geo_name]}"
    # 2026 is INCLUDED. It is incomplete, and it is flagged as such in every curve,
    # but it must be in the corpus: by 2026-09-23 the world method layer already held
    # 722 works against 610 for all of 2025, so excluding it would hide the
    # acceleration that the thesis is about.
    q = f"({q}) AND year_published:[1990 TO 2026]"
    path = OUT / f"{code}_{geo_name}.jsonl"
    body = {"query": {"query_string": {"query": q, "default_operator": "AND"}},
            "include": INCLUDE, "size": 500, "scroll": "1m"}
    n, total = 0, None
    with path.open("w", encoding="utf-8") as fh:
        while True:
            r = post(body, tok)
            if r.status_code == 204:
                break
            js = r.json()
            if total is None:
                total = js.get("total", 0)
                print(f"{code}_{geo_name}: {total} records")
            rows = js.get("data") or []
            if not rows:
                break
            for w in rows:
                fh.write(json.dumps(w, ensure_ascii=False) + "\n")
            n += len(rows)
            sid = js.get("scroll_id")
            if not sid:
                break
            # No sleep here on purpose: a scroll_id expires after one minute.
            body = {"scroll_id": sid, "scroll": "1m"}
            print(f"\r  {n}/{total}", end="")
            sys.stdout.flush()
    print(f"\r{code}_{geo_name}: {n}/{total} -> {path.name}")
    return {"block": code, "geo": geo_name, "records": n, "reported_total": total,
            "run_date": time.strftime("%Y-%m-%d"), "query": q}


def main():
    tok = token()
    OUT.mkdir(parents=True, exist_ok=True)
    blocks = load_blocks()
    wanted = sys.argv[1:] or ["L1", "L3", "L4", "L5", "L6"]
    runs = []
    for code in wanted:
        if code not in blocks:
            print(f"{code}: not found in {QFILE.name}")
            continue
        for geo in ("world", "latam", "colombia"):
            runs.append(harvest(code, blocks[code], geo, tok))
    (OUT / "manifest.json").write_text(json.dumps(runs, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
    print(f"\nmanifest written with {len(runs)} runs")


if __name__ == "__main__":
    main()
