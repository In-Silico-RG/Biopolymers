#!/usr/bin/env python3
"""Rebuild the headline corpus on the combined English, Spanish and Portuguese vocabulary.

The language probe measured what Spanish and Portuguese terms add: +15% for Latin America
and +26% for Colombia on the core field, rising to +34% for Colombian PHA. Those were set
differences on the regional slices only. This harvests the combined string properly, so
every indicator can be recomputed on it.

The English-only corpora are kept and still reported. Replacing them silently would make
docs 01 and 02 unverifiable, and the gap between the two is itself the result.

Writes aggregates to data/raw/openalex/aggregates/ under names prefixed `comb_`.
"""
import csv
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpora import METHODS, LATAM, IBERO, COL, auth_headers, load, paren

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/raw/openalex/aggregates"
BASE = "https://api.openalex.org/works"
MAILTO = "aldo.combariza@unisucre.edu.co"
RUN_DATE = time.strftime("%Y-%m-%d")

FACETS = ["publication_year", "institutions.country_code", "type", "language",
          "open_access.is_oa", "primary_topic.id", "primary_location.source.id"]


def get(params, tries=6):
    for a in range(tries):
        try:
            r = requests.get(BASE, params={**params, "mailto": MAILTO},
                             headers=auth_headers(), timeout=90)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(4 * (a + 1))
                continue
            return {"_error": f"{r.status_code} {r.text[:200]}"}
        except requests.RequestException as e:
            time.sleep(4 * (a + 1))
            err = str(e)
    return {"_error": f"retries exhausted: {locals().get('err','')}"}


def corpora_combined():
    core = paren(load("p1_core_combined_v1.txt"))
    meth = paren(METHODS)
    anchors = {k: paren(load(f"p1_anchor_{k}_combined_v1.txt"))
               for k in ("cellulose", "pha", "lignin")}
    geos = {"world": None, "ibero": f"institutions.country_code:{IBERO}",
            "latam": f"institutions.country_code:{LATAM}",
            "colombia": f"institutions.country_code:{COL}"}
    c = {}
    for g, f in geos.items():
        c[f"comb_core_{g}"] = (core, f)
        c[f"comb_methods_{g}"] = (f"{core} AND {meth}", f)
    for name, a in anchors.items():
        for g in ("world", "latam", "colombia"):
            c[f"comb_anchor_{name}_{g}"] = (a, geos[g])
        c[f"comb_anchor_{name}_methods_world"] = (f"{a} AND {meth}", None)
        c[f"comb_anchor_{name}_methods_latam"] = (f"{a} AND {meth}", geos["latam"])
    return c


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, (search, extra) in corpora_combined().items():
        filt = f"title_and_abstract.search:{search}" + (f",{extra}" if extra else "")
        head = get({"filter": filt, "per-page": 1})
        n = head.get("meta", {}).get("count") if "_error" not in head else None
        print(f"{name:36s} {n if n is not None else head.get('_error','?')}")
        sys.stdout.flush()
        manifest.append({"corpus": name, "count": n, "run_date": RUN_DATE,
                         "geo_filter": extra or "", "error": head.get("_error", "")})
        if n is None:
            continue
        for facet in FACETS:
            js = get({"filter": filt, "group_by": facet, "per-page": 200})
            if "_error" in js:
                print(f"    ! {facet}: {js['_error']}")
                continue
            path = OUT / f"{name}__{facet.replace('.', '_')}.csv"
            with path.open("w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["key", "key_display_name", "count"])
                for g in js.get("group_by", []):
                    w.writerow([g.get("key"), g.get("key_display_name"), g.get("count")])
            time.sleep(0.2)
    with (OUT / "manifest_combined.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["corpus", "count", "run_date", "geo_filter", "error"])
        w.writeheader()
        w.writerows(manifest)
    print(f"\n{len(manifest)} corpora, manifest at {OUT / 'manifest_combined.csv'}")


if __name__ == "__main__":
    main()
