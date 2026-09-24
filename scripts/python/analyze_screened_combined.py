#!/usr/bin/env python3
"""Recompute the screened shares on the combined corpus, beside the English-only ones.

The screened shares in docs 02 and 05 rest on the English-only denominator, which the
language rebuild showed to be too small. This reports both, because the difference is the
point: if the works recovered by Spanish and Portuguese are as non-computational on a
reading of their abstracts as they were on a keyword match, that is a second, independent
confirmation of the finding rather than a repetition of it.

Writes outputs/tables/T36_screened_combined.csv.
"""
import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data/processed"
TAB = ROOT / "outputs/tables"

COMPUTATIONAL = {"md", "qc", "qsar", "docking", "ml", "generative", "solubility",
                 "molecular_modelling", "informatics"}

PAIRS = [
    ("methods_world", "comb_methods_world", "Method layer, world"),
    ("methods_ibero", "comb_methods_ibero", "Method layer, Ibero-America"),
    ("methods_latam", "comb_methods_latam", "Method layer, Latin America"),
    ("methods_colombia", "comb_methods_colombia", "Method layer, Colombia"),
    ("core_colombia", "comb_core_colombia", "Whole field, Colombia"),
    ("core_latam", "comb_core_latam", "Whole field, Latin America"),
]


def load(stem):
    p = PROC / f"screened_{stem}.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p)
    d["materials"] = d["materials"].astype("string").str.lower().map(
        {"true": True, "false": False})
    return d


def summarise(d):
    if d is None:
        return None
    cls = d[d["materials"].notna()]
    mat = d[d["materials"] == True]
    comp = mat[mat["method"].isin(COMPUTATIONAL)]
    doe = mat[mat["method"] == "statistical_doe"]
    return {
        "screened": len(d), "readable": len(cls),
        "readable_pct": round(len(cls) / len(d) * 100, 1) if len(d) else None,
        "materials": len(mat),
        "materials_pct_of_readable": round(len(mat) / len(cls) * 100, 1) if len(cls) else None,
        "computational": len(comp),
        "computational_pct_of_materials": round(len(comp) / len(mat) * 100, 2) if len(mat) else None,
        "statistical_doe_only": len(doe),
    }


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    rows = []
    for en, cb, label in PAIRS:
        e, c = summarise(load(en)), summarise(load(cb))
        if e is None and c is None:
            continue
        row = {"corpus": label}
        for k, v in (e or {}).items():
            row[f"en_{k}"] = v
        for k, v in (c or {}).items():
            row[f"comb_{k}"] = v
        if e and c:
            row["added_screened"] = c["screened"] - e["screened"]
            row["added_materials"] = c["materials"] - e["materials"]
            row["added_computational"] = c["computational"] - e["computational"]
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(TAB / "T36_screened_combined.csv", index=False)

    show = ["corpus", "en_screened", "comb_screened", "added_screened",
            "added_materials", "added_computational",
            "en_computational_pct_of_materials", "comb_computational_pct_of_materials"]
    show = [c for c in show if c in df.columns]
    with pd.option_context("display.width", 220, "display.max_colwidth", 30):
        print(df[show].to_string(index=False))

    # Only the whole-field corpora are comparable here. The method-layer corpora were
    # selected on a computational keyword, so ~87% of them are computational by
    # construction and averaging the two kinds together would be meaningless.
    whole = df[df["corpus"].str.startswith("Whole field")]
    if len(whole) and "added_materials" in whole.columns:
        am = whole["added_materials"].fillna(0).sum()
        ac = whole["added_computational"].fillna(0).sum()
        print(f"\nOn the whole-field corpora, the combined vocabulary adds {int(am)} "
              f"materials works of which {int(ac)} are computational.")
        if am:
            base = whole["en_computational_pct_of_materials"].mean()
            print(f"The recovered literature is {ac / am * 100:.1f}% computational, against "
                  f"{base:.1f}% in the English-only corpora it was added to: "
                  f"about {(ac / am * 100) / base:.1f} times as computational.")
        for _, r in whole.iterrows():
            print(f"  {r['corpus']:<28} screened share "
                  f"{r['en_computational_pct_of_materials']}% -> "
                  f"{r['comb_computational_pct_of_materials']}%")


if __name__ == "__main__":
    main()
