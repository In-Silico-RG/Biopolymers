#!/usr/bin/env python3
"""Harvest full records for the combined-vocabulary corpora, so they can be screened.

The combined harvest so far produced aggregates only, which is enough for counts but not
for reading abstracts. The screened shares in docs 02 and 05 still rest on the English-only
denominator, which the language rebuild showed to be too small; this closes that gap.

Only the corpora the thesis actually reads closely are pulled. The combined world core
corpus is 150,122 works and is left to its aggregates, as the English one was.

Records already harvested under the English queries are re-fetched here rather than
diffed, because the screening cache keys on the prompt: an abstract already read costs
nothing to read again, so the simple path is also the cheap one.
"""
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpora import METHODS, LATAM, IBERO, COL, auth_headers, load, paren

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/raw/openalex/records"
BASE = "https://api.openalex.org/works"
MAILTO = "aldo.combariza@unisucre.edu.co"
MAX_RECORDS = 30000

FIELDS = ",".join([
    "id", "doi", "title", "display_name", "publication_year", "publication_date",
    "type", "language", "cited_by_count", "is_retracted", "fwci",
    "authorships", "countries_distinct_count", "institutions_distinct_count",
    "corresponding_institution_ids", "primary_location", "open_access",
    "primary_topic", "topics", "keywords", "concepts",
    "sustainable_development_goals", "awards", "funders",
    "referenced_works_count", "abstract_inverted_index",
])


def targets():
    core = paren(load("p1_core_combined_v1.txt"))
    meth = paren(METHODS)
    anchors = {k: paren(load(f"p1_anchor_{k}_combined_v1.txt"))
               for k in ("cellulose", "pha", "lignin")}
    geo = {"world": None, "ibero": f"institutions.country_code:{IBERO}",
           "latam": f"institutions.country_code:{LATAM}",
           "colombia": f"institutions.country_code:{COL}"}
    t = [
        ("comb_methods_world", f"{core} AND {meth}", None),
        ("comb_methods_ibero", f"{core} AND {meth}", geo["ibero"]),
        ("comb_methods_latam", f"{core} AND {meth}", geo["latam"]),
        ("comb_methods_colombia", f"{core} AND {meth}", geo["colombia"]),
        ("comb_core_colombia", core, geo["colombia"]),
        ("comb_core_latam", core, geo["latam"]),
    ]
    for name, a in anchors.items():
        t.append((f"comb_anchor_{name}_colombia", a, geo["colombia"]))
    return t


def get(params, tries=8):
    for a in range(tries):
        try:
            r = requests.get(BASE, params={**params, "mailto": MAILTO},
                             headers=auth_headers(), timeout=120)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(60, 4 * (a + 1) ** 2))
                continue
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
        except requests.RequestException:
            time.sleep(min(60, 4 * (a + 1) ** 2))
    raise RuntimeError("exhausted retries")


def harvest(name, search, extra):
    filt = f"title_and_abstract.search:{search}" + (f",{extra}" if extra else "")
    total = get({"filter": filt, "per-page": 1})["meta"]["count"]
    if total > MAX_RECORDS:
        print(f"{name:28s} SKIP ({total:,} > {MAX_RECORDS:,}; aggregates only)")
        return
    path = OUT / f"{name}.jsonl"
    n, cursor = 0, "*"
    with path.open("w", encoding="utf-8") as fh:
        while cursor:
            js = get({"filter": filt, "per-page": 200, "cursor": cursor, "select": FIELDS})
            rows = js.get("results", [])
            if not rows:
                break
            for w in rows:
                fh.write(json.dumps(w, ensure_ascii=False) + "\n")
                n += 1
            cursor = js["meta"].get("next_cursor")
            print(f"\r{name:28s} {n}/{total}", end="")
            sys.stdout.flush()
            time.sleep(0.15)
    print(f"\r{name:28s} {n}/{total} -> {path.name}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, search, extra in targets():
        try:
            harvest(name, search, extra)
        except Exception as e:
            print(f"{name:28s} ERROR {e}")


if __name__ == "__main__":
    main()
