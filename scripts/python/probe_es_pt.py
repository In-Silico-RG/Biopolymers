#!/usr/bin/env python3
"""Measure what Spanish and Portuguese search terms add to the regional counts.

Every number in this project so far came from English queries. If regional output published
in Spanish and Portuguese is systematically missed, the regional deficit reported in the
report is partly linguistic rather than real, and that has to be measured rather than
assumed.

The question is not how many records the Spanish and Portuguese strings return on their
own. It is how many they return that the English string does NOT, which needs a set
difference and therefore a record-level comparison, not a count comparison.

Writes outputs/tables/T30_language_variants.csv.
"""
import csv
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpora import CORE, ANCHORS, LATAM, COL, auth_headers, load, paren

ROOT = Path(__file__).resolve().parents[2]
TAB = ROOT / "outputs/tables"
BASE = "https://api.openalex.org/works"
MAILTO = "aldo.combariza@unisucre.edu.co"


def blocks(path):
    """Parse a '## name' sectioned query file into {name: string}."""
    out, name, buf = {}, None, []
    for line in (ROOT / "queries" / path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if name and buf:
                out[name] = " ".join(buf).strip()
            name, buf = line[3:].strip(), []
            continue
        if line.strip() and not line.lstrip().startswith("#"):
            buf.append(line.strip())
    if name and buf:
        out[name] = " ".join(buf).strip()
    return out


def get(params, tries=5):
    for a in range(tries):
        r = requests.get(BASE, params={**params, "mailto": MAILTO},
                         headers=auth_headers(), timeout=90)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503):
            time.sleep(3 * (a + 1))
            continue
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    raise RuntimeError("exhausted retries")


def count(search, geo=None):
    f = f"title_and_abstract.search:{search}"
    if geo:
        f += f",institutions.country_code:{geo}"
    return get({"filter": f, "per-page": 1})["meta"]["count"]


def ids(search, geo=None, cap=30000):
    """Every OpenAlex id matching a query, so the set difference is exact."""
    f = f"title_and_abstract.search:{search}"
    if geo:
        f += f",institutions.country_code:{geo}"
    out, cursor = set(), "*"
    while cursor and len(out) < cap:
        js = get({"filter": f, "per-page": 200, "cursor": cursor, "select": "id"})
        rows = js.get("results", [])
        if not rows:
            break
        out.update(r["id"] for r in rows)
        cursor = js["meta"].get("next_cursor")
        time.sleep(0.15)
    return out


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    es_core = load("p1_core_es_pt_v1.txt")
    anchors_es = blocks("p1_anchors_es_pt_v1.txt")

    pairs = [("core", paren(CORE), paren(es_core))]
    for k in ("cellulose", "pha", "lignin"):
        if k in anchors_es:
            pairs.append((k, paren(ANCHORS[k]), paren(anchors_es[k])))

    rows = []
    for name, en, es in pairs:
        for geo_name, geo in (("latam", LATAM), ("colombia", COL)):
            en_ids = ids(en, geo)
            es_ids = ids(es, geo)
            added = es_ids - en_ids
            rows.append({
                "block": name, "geo": geo_name,
                "english": len(en_ids), "spanish_portuguese": len(es_ids),
                "overlap": len(en_ids & es_ids), "added_by_es_pt": len(added),
                "added_pct_of_english": round(len(added) / len(en_ids) * 100, 2)
                if en_ids else None,
            })
            print(f"{name:10s} {geo_name:9s} EN={len(en_ids):>6,}  ES/PT={len(es_ids):>6,}  "
                  f"new={len(added):>5,}  (+{rows[-1]['added_pct_of_english']}%)")
            sys.stdout.flush()

    # World totals, for context only; the set difference is not computed at world scale.
    for name, en, es in pairs:
        rows.append({"block": name, "geo": "world",
                     "english": count(en), "spanish_portuguese": count(es),
                     "overlap": None, "added_by_es_pt": None,
                     "added_pct_of_english": None})

    with (TAB / "T30_language_variants.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {TAB / 'T30_language_variants.csv'}")


if __name__ == "__main__":
    main()
