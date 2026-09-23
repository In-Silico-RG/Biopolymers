#!/usr/bin/env python3
"""Compare the screened corpora: does the region use different methods from the world?

Phase 1 showed Latin America and the world adopt computational methods at almost the same
rate. That says nothing about WHICH methods. This answers that, on the materials-only
subset of each corpus, which is the only comparison that is like for like.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROC, TAB = ROOT / "data/processed", ROOT / "outputs/tables"

CORPORA = [("methods_world", "World"), ("methods_ibero", "Ibero-America"),
           ("methods_latam", "Latin America"), ("methods_colombia", "Colombia")]

# What counts as computational, after the strict second pass. statistical_doe is
# deliberately excluded: factorial designs, response-surface methodology and curve fitting
# to one's own measurements are not computational chemistry, and counting them inflated the
# Colombian share from about 3 to 12.5 percent. See refine_other_computational.py.
COMPUTATIONAL = {"md", "qc", "qsar", "docking", "ml", "generative", "solubility",
                 "molecular_modelling", "informatics"}


def load(stem):
    p = PROC / f"screened_{stem}.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df["materials"] = df["materials"].astype("string").str.lower().map(
        {"true": True, "false": False})
    df["experimental"] = df["experimental"].astype("string").str.lower().map(
        {"true": True, "false": False})
    return df


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    rows, mix, pmix = [], {}, {}
    for stem, label in CORPORA:
        df = load(stem)
        if df is None:
            continue
        mat = df[df["materials"] == True]
        cls = df[df["materials"].notna()]
        rows.append({
            "context": label, "screened": len(df),
            "with_abstract": len(cls),
            "abstract_coverage_pct": round(len(cls) / len(df) * 100, 1),
            "materials_pct_of_classified": round(len(mat) / len(cls) * 100, 1) if len(cls) else None,
            "materials_works": len(mat),
            "coupled_to_experiments_pct": round(
                (mat["experimental"] == True).sum() / len(mat) * 100, 1) if len(mat) else None,
        })
        if len(mat):
            mix[label] = (mat["method"].value_counts(normalize=True) * 100).round(1)
            pmix[label] = (mat["polymer"].value_counts(normalize=True) * 100).round(1)

    pd.DataFrame(rows).to_csv(TAB / "T21_screening_by_context.csv", index=False)
    pd.DataFrame(mix).fillna(0).to_csv(TAB / "T22_method_mix_by_context.csv")
    pd.DataFrame(pmix).fillna(0).to_csv(TAB / "T23_polymer_mix_by_context.csv")

    # The whole regional field, not just its computational layer
    extra = []
    for stem, label in [("core_colombia", "Colombia, whole field"),
                        ("core_latam", "Latin America, whole field")]:
        df = load(stem)
        if df is None:
            continue
        cls = df[df["materials"].notna()]
        mat = df[df["materials"] == True]
        has_method = mat[mat["method"].isin(COMPUTATIONAL)]
        extra.append({
            "corpus": label, "screened": len(df),
            "with_abstract": len(cls),
            "materials_pct_of_classified": round(len(mat) / len(cls) * 100, 1) if len(cls) else None,
            "materials_works": len(mat),
            "with_computational_method": len(has_method),
            "computational_pct_of_materials": round(
                len(has_method) / len(mat) * 100, 2) if len(mat) else None,
            "statistical_doe_only": int((mat["method"] == "statistical_doe").sum()),
        })
    if extra:
        pd.DataFrame(extra).to_csv(TAB / "T24_whole_field_screened.csv", index=False)

    print(pd.DataFrame(rows).to_string(index=False))
    print("\nmethod mix, materials-only, % of each context:")
    print(pd.DataFrame(mix).fillna(0).to_string())
    print("\npolymer mix, materials-only, % of each context:")
    print(pd.DataFrame(pmix).fillna(0).head(12).to_string())
    if extra:
        print("\nwhole regional field:")
        print(pd.DataFrame(extra).to_string(index=False))


if __name__ == "__main__":
    main()
