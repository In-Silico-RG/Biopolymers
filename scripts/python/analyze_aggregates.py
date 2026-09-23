#!/usr/bin/env python3
"""Build the Phase 1 descriptive tables from the OpenAlex aggregates.

Every number the thesis reports comes from here, never from a hand count. Input is
data/raw/openalex/aggregates/, output is outputs/tables/.
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AGG = ROOT / "data/raw/openalex/aggregates"
TAB = ROOT / "outputs/tables"

Y0, Y1 = 1990, 2025          # 2026 is incomplete and is excluded from every curve
WIN0, WIN1 = 2015, 2025      # window for the comparative indicators


def facet(corpus, name):
    """Read one aggregate file.

    OpenAlex returns `key` as an entity URL (or 0/1 for booleans) and puts the readable
    value in `key_display_name`. A `code` column is added holding the short form, so
    downstream code never parses URLs.
    """
    p = AGG / f"{corpus}__{name}.csv"
    if not p.exists():
        return pd.DataFrame(columns=["key", "key_display_name", "count", "code"])
    df = pd.read_csv(p)
    df["code"] = (df["key"].astype(str).str.rsplit("/", n=1).str[-1]
                  .where(df["key"].astype(str).str.startswith("http"),
                         df["key_display_name"].astype(str)))
    return df


def years(corpus):
    df = facet(corpus, "publication_year")
    if df.empty:
        return pd.Series(dtype=int)
    df = df[pd.to_numeric(df["key"], errors="coerce").notna()].copy()
    df["key"] = df["key"].astype(int)
    s = df.set_index("key")["count"].sort_index()
    return s[(s.index >= Y0) & (s.index <= Y1)]


def cagr(s, a, b):
    """Compound annual growth rate between two years, in percent."""
    if a not in s.index or b not in s.index or s.get(a, 0) <= 0:
        return float("nan")
    return ((s[b] / s[a]) ** (1 / (b - a)) - 1) * 100


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    man = pd.read_csv(AGG / "manifest.csv")
    totals = man.set_index("corpus")["count"].to_dict()

    # --- T1: annual production, the four contexts plus the methods layer ---
    cols = ["core_world", "core_ibero", "core_latam", "core_colombia",
            "methods_world", "methods_ibero", "methods_latam", "methods_colombia"]
    t1 = pd.DataFrame({c: years(c) for c in cols}).fillna(0).astype(int)
    t1.index.name = "year"
    t1.to_csv(TAB / "T1_annual_production.csv")

    # --- T2: methods share of the field, by year and context ---
    t2 = pd.DataFrame(index=t1.index)
    for ctx in ["world", "ibero", "latam", "colombia"]:
        den = t1[f"core_{ctx}"].astype(float).replace(0.0, float("nan"))
        t2[f"{ctx}_pct"] = (t1[f"methods_{ctx}"] / den * 100).round(2)
    t2.to_csv(TAB / "T2_methods_share_by_year.csv")

    # --- T3: comparative indicator table across the four contexts ---
    rows = []
    for ctx, label in [("world", "World"), ("ibero", "Ibero-America"),
                       ("latam", "Latin America"), ("colombia", "Colombia")]:
        core_s, meth_s = years(f"core_{ctx}"), years(f"methods_{ctx}")
        core_w = int(core_s[(core_s.index >= WIN0)].sum())
        meth_w = int(meth_s[(meth_s.index >= WIN0)].sum())
        oa = facet(f"core_{ctx}", "open_access_is_oa")
        oa_true = oa.loc[oa["key_display_name"].astype(str).str.lower() == "true", "count"].sum()
        oa_all = oa["count"].sum()
        typ = facet(f"core_{ctx}", "type")
        art = typ.loc[typ["code"] == "article", "count"].sum()
        rows.append({
            "context": label,
            "total_all_years": totals.get(f"core_{ctx}"),
            f"core_{WIN0}_{WIN1}": core_w,
            "share_of_world_pct": None,
            f"cagr_{WIN0}_{WIN1}_pct": round(cagr(core_s, WIN0, WIN1), 2),
            f"methods_{WIN0}_{WIN1}": meth_w,
            "methods_share_pct": round(meth_w / core_w * 100, 2) if core_w else None,
            "open_access_pct": round(oa_true / oa_all * 100, 1) if oa_all else None,
            "article_share_pct": round(art / typ["count"].sum() * 100, 1) if len(typ) else None,
        })
    t3 = pd.DataFrame(rows)
    world_w = t3.loc[t3["context"] == "World", f"core_{WIN0}_{WIN1}"].iloc[0]
    t3["share_of_world_pct"] = (t3[f"core_{WIN0}_{WIN1}"] / world_w * 100).round(2)
    t3.to_csv(TAB / "T3_context_comparison.csv", index=False)

    # --- T4: country ranking of the field, and of the methods layer ---
    cw = facet("core_world", "institutions_country_code").head(40)
    mw = facet("methods_world", "institutions_country_code")
    mw_map = dict(zip(mw["code"], mw["count"]))
    cw["methods_count"] = cw["code"].map(mw_map).fillna(0).astype(int)
    cw["methods_share_pct"] = (cw["methods_count"] / cw["count"] * 100).round(2)
    cw = cw.rename(columns={"code": "country_code", "key_display_name": "country",
                            "count": "core_count"})[
        ["country_code", "country", "core_count", "methods_count", "methods_share_pct"]]
    cw.to_csv(TAB / "T4_country_ranking.csv", index=False)

    # --- T5: Latin American country ranking ---
    lw = facet("core_latam", "institutions_country_code")
    ml = facet("methods_latam", "institutions_country_code")
    ml_map = dict(zip(ml["code"], ml["count"]))
    lw["methods_count"] = lw["code"].map(ml_map).fillna(0).astype(int)
    lw["methods_share_pct"] = (lw["methods_count"] / lw["count"] * 100).round(2)
    lw = lw.rename(columns={"code": "country_code", "key_display_name": "country",
                            "count": "core_count"})[
        ["country_code", "country", "core_count", "methods_count", "methods_share_pct"]]
    lw.head(30).to_csv(TAB / "T5_latam_country_ranking.csv", index=False)

    # --- T6: the three anchored biopolymer lines ---
    rows = []
    for a in ["cellulose", "pha", "lignin"]:
        w, lat = totals.get(f"anchor_{a}_world"), totals.get(f"anchor_{a}_latam")
        col, mw_, ml_ = (totals.get(f"anchor_{a}_colombia"),
                         totals.get(f"anchor_{a}_methods_world"),
                         totals.get(f"anchor_{a}_methods_latam"))
        rows.append({
            "anchor": a, "world": w, "latam": lat, "colombia": col,
            "latam_share_of_world_pct": round(lat / w * 100, 2) if w else None,
            "colombia_share_of_world_pct": round(col / w * 100, 3) if w else None,
            "methods_world": mw_, "methods_latam": ml_,
            "methods_share_world_pct": round(mw_ / w * 100, 2) if w else None,
            "methods_share_latam_pct": round(ml_ / lat * 100, 2) if lat else None,
        })
    pd.DataFrame(rows).to_csv(TAB / "T6_anchor_lines.csv", index=False)

    # --- T7: top journals and top topics of the methods layer ---
    facet("methods_world", "primary_location_source_id").head(30).to_csv(
        TAB / "T7_methods_top_sources.csv", index=False)
    facet("methods_world", "primary_topic_id").head(30).to_csv(
        TAB / "T8_methods_top_topics.csv", index=False)
    facet("core_world", "primary_topic_id").head(30).to_csv(
        TAB / "T9_core_top_topics.csv", index=False)

    for p in sorted(TAB.glob("*.csv")):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
