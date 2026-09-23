#!/usr/bin/env python3
"""Score the DeepSeek screening against an independent second coder.

Agreement is reported as Cohen's kappa, not as bare percent agreement. Percent agreement
flatters any classification with one dominant class: if 80% of a corpus is one label, a
coder who always guessed that label would score 80% and know nothing. Kappa subtracts the
agreement expected by chance.

Conventional reading of kappa: below 0.20 poor, 0.21-0.40 fair, 0.41-0.60 moderate,
0.61-0.80 substantial, above 0.80 almost perfect.

The random stratum is the headline figure, because it reflects the mix the corpus actually
has. The rare stratum is reported separately and never pooled into it, since it was drawn
deliberately to over-represent thin categories.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VAL = ROOT / "data/processed/validation"
TAB = ROOT / "outputs/tables"

# Method labels grouped as the report uses them: what matters most is whether a work is
# counted as computational at all, then which broad family.
COMPUTATIONAL = {"md", "qc", "qsar", "docking", "ml", "generative", "solubility",
                 "molecular_modelling", "informatics"}
FAMILY = {
    "md": "simulation", "qc": "simulation", "molecular_modelling": "simulation",
    "ml": "data_driven", "qsar": "data_driven", "informatics": "data_driven",
    "generative": "data_driven",
    "docking": "docking", "solubility": "solubility",
    "none": "none", "statistical_doe": "none", "": "none",
}


def kappa(a, b):
    """Cohen's kappa for two equal-length label sequences."""
    n = len(a)
    if n == 0:
        return float("nan"), float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] / n * cb.get(k, 0) / n for k in ca)
    if pe == 1:
        return po, float("nan")
    return po, (po - pe) / (1 - pe)


def norm(v):
    return str(v).strip().lower() if v is not None else ""


def tri(v):
    """materials as yes/no/unknown, from either coder's spelling."""
    v = norm(v)
    if v in ("yes", "true"):
        return "yes"
    if v in ("no", "false"):
        return "no"
    return "unknown"


def main():
    key = {r["n"]: r for r in csv.DictReader((VAL / "key_methods_world.csv").open(encoding="utf-8"))}
    mine = {r["n"]: r for r in csv.DictReader(
        (VAL / "claude_codes_methods_world.csv").open(encoding="utf-8"))}
    ns = [n for n in key if n in mine]
    if not ns:
        sys.exit("no overlapping items; was the coding sheet filled in?")

    out_rows, disagreements = [], []
    for stratum in ("random", "rare", "all"):
        sel = [n for n in ns if stratum == "all" or key[n]["stratum"] == stratum]
        if not sel:
            continue
        ds_mat = [tri(key[n]["ds_materials"]) for n in sel]
        cl_mat = [tri(mine[n]["materials"]) for n in sel]
        ds_comp = ["yes" if norm(key[n]["ds_method"]) in COMPUTATIONAL else "no" for n in sel]
        cl_comp = ["yes" if norm(mine[n]["method"]) in COMPUTATIONAL else "no" for n in sel]
        ds_fam = [FAMILY.get(norm(key[n]["ds_method"]), "other") for n in sel]
        cl_fam = [FAMILY.get(norm(mine[n]["method"]), "other") for n in sel]
        ds_pol = [norm(key[n]["ds_polymer"]) for n in sel]
        cl_pol = [norm(mine[n]["polymer"]) for n in sel]

        for label, a, b in (("materials vs biological", ds_mat, cl_mat),
                            ("computational at all", ds_comp, cl_comp),
                            ("method family", ds_fam, cl_fam),
                            ("polymer family", ds_pol, cl_pol)):
            po, k = kappa(a, b)
            out_rows.append({"stratum": stratum, "n": len(sel), "dimension": label,
                             "percent_agreement": round(po * 100, 1),
                             "cohens_kappa": round(k, 3) if k == k else None})

        if stratum == "random":
            for n, dm, cm, df, cf in zip(sel, ds_mat, cl_mat, ds_fam, cl_fam):
                if dm != cm or df != cf:
                    disagreements.append({
                        "n": n, "deepseek_materials": dm, "claude_materials": cm,
                        "deepseek_method": key[n]["ds_method"], "claude_method": mine[n]["method"],
                        "title": key[n]["title"][:95]})

    TAB.mkdir(parents=True, exist_ok=True)
    with (TAB / "T32_screening_validation.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    if disagreements:
        with (VAL / "disagreements.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(disagreements[0]))
            w.writeheader()
            w.writerows(disagreements)

    width = max(len(r["dimension"]) for r in out_rows)
    cur = None
    for r in out_rows:
        if r["stratum"] != cur:
            cur = r["stratum"]
            print(f"\n--- {cur} sample, n={r['n']} ---")
        k = r["cohens_kappa"]
        print(f"  {r['dimension']:<{width}}  agreement {r['percent_agreement']:>5.1f}%   "
              f"kappa {k if k is not None else 'n/a'}")
    print(f"\n{len(disagreements)} disagreements in the random sample "
          f"-> {VAL / 'disagreements.csv'}")


if __name__ == "__main__":
    main()
