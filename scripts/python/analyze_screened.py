#!/usr/bin/env python3
"""Turn the DeepSeek screening into the corrected Phase 2 numbers.

The point of the screening is the contamination measured in
docs/01_bibliometric_mapping.md section 6: the framing terms "biomacromolecule" and
"natural polymer" pull protein and nucleic-acid biophysics into the corpus. This script
reports how large that fraction is and restates the method share on the materials-only
subset.
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROC, TAB = ROOT / "data/processed", ROOT / "outputs/tables"


def load(stem):
    p = PROC / f"screened_{stem}.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["materials"] = df["materials"].astype("string").str.lower().map(
        {"true": True, "false": False})
    return df


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    df = load("methods_world")
    if df is None:
        sys.exit("methods_world not screened yet")

    n = len(df)
    err = int(df["error"].notna().sum() - (df["error"].astype(str) == "nan").sum())
    mat = df[df["materials"] == True]
    bio = df[df["materials"] == False]
    unk = df[df["materials"].isna()]

    summary = pd.DataFrame([
        {"class": "biopolymer materials research", "works": len(mat),
         "pct": round(len(mat) / n * 100, 1)},
        {"class": "biological-function research", "works": len(bio),
         "pct": round(len(bio) / n * 100, 1)},
        {"class": "unclassifiable (no usable abstract)", "works": len(unk),
         "pct": round(len(unk) / n * 100, 1)},
    ])
    summary.to_csv(TAB / "T10_screening_summary.csv", index=False)

    # Corrected method share: the Phase 1 denominator is unchanged, the numerator drops to
    # the materials-only works.
    t3 = pd.read_csv(TAB / "T3_context_comparison.csv")
    core_w = int(t3.loc[t3["context"] == "World", "core_2015_2025"].iloc[0])
    meth_w = int(t3.loc[t3["context"] == "World", "methods_2015_2025"].iloc[0])
    frac = len(mat) / (len(mat) + len(bio)) if (len(mat) + len(bio)) else float("nan")
    corrected = pd.DataFrame([{
        "measure": "method share of the field, 2015-2025",
        "uncorrected_pct": round(meth_w / core_w * 100, 2),
        "materials_fraction_of_methods_layer": round(frac * 100, 1),
        "corrected_pct": round(meth_w * frac / core_w * 100, 2),
    }])
    corrected.to_csv(TAB / "T11_corrected_method_share.csv", index=False)

    for col, fname in [("method", "T12_method_mix.csv"), ("polymer", "T13_polymer_mix.csv")]:
        a = df[col].value_counts().rename("all_works")
        b = mat[col].value_counts().rename("materials_only")
        m = pd.concat([a, b], axis=1).fillna(0).astype(int)
        m["materials_pct"] = (m["materials_only"] / m["materials_only"].sum() * 100).round(1)
        m.index.name = col
        m.sort_values("materials_only", ascending=False).to_csv(TAB / fname)

    ct = pd.crosstab(mat["polymer"], mat["method"])
    ct.to_csv(TAB / "T14_polymer_by_method.csv")

    exp = mat["experimental"].astype("string").str.lower().value_counts()
    print(f"screened: {n}  errors: {err}")
    print(summary.to_string(index=False))
    print()
    print(corrected.to_string(index=False))
    print()
    print("method mix, materials-only:")
    print(pd.read_csv(TAB / "T12_method_mix.csv").head(10).to_string(index=False))
    print()
    print("polymer mix, materials-only:")
    print(pd.read_csv(TAB / "T13_polymer_mix.csv").head(10).to_string(index=False))
    print()
    print("purely computational vs coupled to experiments (materials-only):")
    print(exp.to_string())


if __name__ == "__main__":
    main()
