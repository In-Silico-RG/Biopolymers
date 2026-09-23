#!/usr/bin/env python3
"""Harvest OpenAlex group-by aggregates for every corpus defined in corpora.py.

Aggregates, not records: counting 145,743 works one page at a time would take an hour and
tell us nothing the group_by endpoint does not. Full records are pulled separately, and
only for corpora small enough to justify it.

Writes one CSV per (corpus, facet) under data/raw/openalex/aggregates/, plus a
manifest.csv holding the corpus totals and the run date.
"""
import csv, sys, time
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpora import corpora

MAILTO = "aldo.combariza@unisucre.edu.co"
BASE = "https://api.openalex.org/works"
OUT = Path(__file__).resolve().parents[2] / "data/raw/openalex/aggregates"
RUN_DATE = time.strftime("%Y-%m-%d")

FACETS = [
    "publication_year",
    "institutions.country_code",
    "type",
    "language",
    "open_access.is_oa",
    "primary_topic.id",
    "primary_location.source.id",
    "authorships.institutions.lineage",
]


def get(params, tries=5):
    for a in range(tries):
        try:
            r = requests.get(BASE, params={**params, "mailto": MAILTO}, timeout=90)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(3 * (a + 1)); continue
            return {"_error": f"{r.status_code} {r.text[:200]}"}
        except requests.RequestException as e:
            time.sleep(3 * (a + 1)); err = str(e)
    return {"_error": f"exhausted retries: {locals().get('err','')}"}


def build_filter(search, extra):
    f = f"title_and_abstract.search:{search}"
    if extra:
        f += "," + extra
    return f


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, (search, extra) in corpora().items():
        filt = build_filter(search, extra)
        total = get({"filter": filt, "per-page": 1})
        n = total.get("meta", {}).get("count") if "_error" not in total else None
        print(f"{name:34s} total={n}")
        sys.stdout.flush()
        manifest.append({"corpus": name, "count": n, "run_date": RUN_DATE,
                         "geo_filter": extra or "", "error": total.get("_error", "")})
        if n is None:
            continue
        for facet in FACETS:
            js = get({"filter": filt, "group_by": facet, "per-page": 200})
            if "_error" in js:
                print(f"    ! {facet}: {js['_error']}")
                continue
            rows = js.get("group_by", [])
            path = OUT / f"{name}__{facet.replace('.', '_')}.csv"
            with path.open("w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["key", "key_display_name", "count"])
                for g in rows:
                    w.writerow([g.get("key"), g.get("key_display_name"), g.get("count")])
            time.sleep(0.2)
    with (OUT / "manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["corpus", "count", "run_date", "geo_filter", "error"])
        w.writeheader(); w.writerows(manifest)
    print(f"\nwrote {len(list(OUT.glob('*.csv')))} files to {OUT}")


if __name__ == "__main__":
    main()
