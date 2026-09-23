#!/usr/bin/env python3
"""Download full OpenAlex records for the corpora small enough to warrant it.

Used for the Phase 2 methods corpus and the regional slices, which are the ones the thesis
reads closely. The Phase 1 world corpus is never downloaded whole; its aggregates come from
harvest_aggregates.py.

Writes newline-delimited JSON to data/raw/openalex/records/<corpus>.jsonl so a partial run
can be resumed and inspected without loading everything into memory.
"""
import json, sys, time
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpora import corpora, auth_headers

MAILTO = "aldo.combariza@unisucre.edu.co"
BASE = "https://api.openalex.org/works"
OUT = Path(__file__).resolve().parents[2] / "data/raw/openalex/records"
MAX_RECORDS = 30000  # anything larger is analysed through aggregates instead

TARGETS = [
    "methods_world", "methods_latam", "methods_ibero", "methods_colombia",
    "core_latam", "core_colombia",
    "anchor_pha_latam", "anchor_pha_colombia",
    "anchor_lignin_latam", "anchor_lignin_colombia",
    "anchor_cellulose_colombia",
    "anchor_cellulose_methods_latam", "anchor_pha_methods_latam",
    "anchor_lignin_methods_latam",
]

# "grants" is not a select field on this API version; awards and funders are.
# countries_distinct_count and institutions_distinct_count are carried because the
# international-collaboration share is computed from them rather than from parsing
# authorships by hand.
FIELDS = ",".join([
    "id", "doi", "title", "display_name", "publication_year", "publication_date",
    "type", "language", "cited_by_count", "is_retracted", "fwci",
    "authorships", "countries_distinct_count", "institutions_distinct_count",
    "corresponding_institution_ids", "primary_location", "open_access",
    "primary_topic", "topics", "keywords", "concepts",
    "sustainable_development_goals", "awards", "funders",
    "referenced_works_count", "abstract_inverted_index",
])


def get(params, tries=6):
    for a in range(tries):
        try:
            r = requests.get(BASE, params={**params, "mailto": MAILTO},
                             headers=auth_headers(), timeout=120)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(3 * (a + 1)); continue
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
        except requests.RequestException:
            time.sleep(3 * (a + 1))
    raise RuntimeError("exhausted retries")


def harvest(name, search, extra):
    filt = f"title_and_abstract.search:{search}" + (f",{extra}" if extra else "")
    head = get({"filter": filt, "per-page": 1})
    total = head["meta"]["count"]
    if total > MAX_RECORDS:
        print(f"{name:32s} SKIP ({total} > {MAX_RECORDS}; use aggregates)")
        return
    path = OUT / f"{name}.jsonl"
    n, cursor = 0, "*"
    with path.open("w", encoding="utf-8") as fh:
        while cursor:
            js = get({"filter": filt, "per-page": 200, "cursor": cursor,
                      "select": FIELDS})
            for w in js["results"]:
                fh.write(json.dumps(w, ensure_ascii=False) + "\n")
                n += 1
            cursor = js["meta"].get("next_cursor")
            if not js["results"]:
                break
            print(f"\r{name:32s} {n}/{total}", end="")
            sys.stdout.flush()
            time.sleep(0.15)
    print(f"\r{name:32s} {n}/{total}  -> {path.name}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c = corpora()
    for name in TARGETS:
        search, extra = c[name]
        try:
            harvest(name, search, extra)
        except Exception as e:
            print(f"{name:32s} ERROR {e}")


if __name__ == "__main__":
    main()
