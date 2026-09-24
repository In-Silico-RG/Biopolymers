#!/usr/bin/env python3
"""Recompute the headline indicators on the combined vocabulary, beside the English-only ones.

Both are reported. The English-only figures are what docs 01 and 02 were built on, and the
gap between the two is the measure of how much an English-language bibliometric count
understates Latin American output. Replacing one with the other would destroy that result.

Writes outputs/tables/T33_combined_vs_english.csv and T34_combined_context_comparison.csv.
"""
import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AGG = ROOT / "data/raw/openalex/aggregates"
TAB = ROOT / "outputs/tables"

Y0, Y1 = 1990, 2026
LAST_COMPLETE, PARTIAL = 2025, 2026
WIN0, WIN1 = 2015, 2025


def years(corpus):
    p = AGG / f"{corpus}__publication_year.csv"
    if not p.exists():
        return pd.Series(dtype=int)
    d = pd.read_csv(p)
    d = d[pd.to_numeric(d["key"], errors="coerce").notna()].copy()
    d["key"] = d["key"].astype(int)
    s = d.set_index("key")["count"].sort_index()
    return s[(s.index >= Y0) & (s.index <= Y1)]


def total(manifest, corpus):
    row = manifest[manifest["corpus"] == corpus]
    return int(row["count"].iloc[0]) if len(row) else None


def cagr(s, a, b):
    if a not in s.index or b not in s.index or s.get(a, 0) <= 0:
        return float("nan")
    return ((s[b] / s[a]) ** (1 / (b - a)) - 1) * 100


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    men = pd.read_csv(AGG / "manifest.csv")
    mcb = pd.read_csv(AGG / "manifest_combined.csv")

    # --- T33: what the combined vocabulary adds, corpus by corpus ---
    pairs = ([(f"core_{g}", f"comb_core_{g}") for g in ("world", "ibero", "latam", "colombia")]
             + [(f"methods_{g}", f"comb_methods_{g}") for g in
                ("world", "ibero", "latam", "colombia")]
             + [(f"anchor_{a}_{g}", f"comb_anchor_{a}_{g}")
                for a in ("cellulose", "pha", "lignin")
                for g in ("world", "latam", "colombia")])
    rows = []
    for en, cb in pairs:
        e, c = total(men, en), total(mcb, cb)
        if e is None or c is None:
            continue
        rows.append({"corpus": en, "english_only": e, "combined": c,
                     "added": c - e,
                     "added_pct": round((c - e) / e * 100, 2) if e else None})
    t33 = pd.DataFrame(rows)
    t33.to_csv(TAB / "T33_combined_vs_english.csv", index=False)

    # --- T34: the context comparison, rebuilt on the combined vocabulary ---
    out = []
    for ctx, label in [("world", "World"), ("ibero", "Ibero-America"),
                       ("latam", "Latin America"), ("colombia", "Colombia")]:
        cs, ms = years(f"comb_core_{ctx}"), years(f"comb_methods_{ctx}")
        win = lambda s: int(s[(s.index >= WIN0) & (s.index <= WIN1)].sum())
        cw, mw = win(cs), win(ms)
        oa = AGG / f"comb_core_{ctx}__open_access_is_oa.csv"
        oa_pct = None
        if oa.exists():
            d = pd.read_csv(oa)
            tot = d["count"].sum()
            tr = d.loc[d["key_display_name"].astype(str).str.lower() == "true", "count"].sum()
            oa_pct = round(tr / tot * 100, 1) if tot else None
        out.append({
            "context": label,
            "total_all_years": total(mcb, f"comb_core_{ctx}"),
            f"core_{WIN0}_{WIN1}": cw,
            "share_of_world_pct": None,
            f"cagr_{WIN0}_{WIN1}_pct": round(cagr(cs, WIN0, WIN1), 2),
            f"methods_{WIN0}_{WIN1}": mw,
            "methods_share_pct": round(mw / cw * 100, 2) if cw else None,
            "open_access_pct": oa_pct,
            f"core_{PARTIAL}_ytd": int(cs.get(PARTIAL, 0)),
            f"methods_{PARTIAL}_ytd": int(ms.get(PARTIAL, 0)),
        })
    t34 = pd.DataFrame(out)
    w = t34.loc[t34["context"] == "World", f"core_{WIN0}_{WIN1}"].iloc[0]
    t34["share_of_world_pct"] = (t34[f"core_{WIN0}_{WIN1}"] / w * 100).round(2)
    t34.to_csv(TAB / "T34_combined_context_comparison.csv", index=False)

    # --- T35: country ranking on the combined vocabulary ---
    p = AGG / "comb_core_world__institutions_country_code.csv"
    if p.exists():
        d = pd.read_csv(p)
        d["country_code"] = (d["key"].astype(str).str.rsplit("/", n=1).str[-1])
        m = AGG / "comb_methods_world__institutions_country_code.csv"
        if m.exists():
            dm = pd.read_csv(m)
            dm["cc"] = dm["key"].astype(str).str.rsplit("/", n=1).str[-1]
            d["methods_count"] = d["country_code"].map(
                dict(zip(dm["cc"], dm["count"]))).fillna(0).astype(int)
            d["methods_share_pct"] = (d["methods_count"] / d["count"] * 100).round(2)
        d = d.rename(columns={"key_display_name": "country", "count": "core_count"})
        d[["country_code", "country", "core_count", "methods_count", "methods_share_pct"]
          ].head(40).to_csv(TAB / "T35_combined_country_ranking.csv", index=False)

    print(t33.to_string(index=False))
    print()
    print(t34.to_string(index=False))


if __name__ == "__main__":
    main()
