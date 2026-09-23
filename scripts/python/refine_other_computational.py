#!/usr/bin/env python3
"""Second, stricter pass over the works the first screening put in "other_computational".

Why this exists. Inspecting the Colombian corpus showed that bucket was catching factorial
designs, response-surface methodology and ordinary statistical modelling. Those are not
computational chemistry, and counting them inflated the Colombian computational share from
about 3 percent to 12.5 percent. The first pass is otherwise sound, so rather than
re-screening every abstract under a new prompt, only this one ambiguous bucket is asked
again, with a question that names the distinction explicitly.

Rewrites the method column in place: "other_computational" becomes one of
molecular_modelling, statistical_doe, informatics or none. Original files are kept as
*.firstpass.csv so the correction is auditable.
"""
import json, os, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import screen_abstracts as sa

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data/processed"
REC = ROOT / "data/raw/openalex/records"

SYSTEM = """You decide whether a scientific abstract uses COMPUTATIONAL CHEMISTRY or
MOLECULAR MODELLING, as opposed to ordinary statistics.

Answer ONLY with a JSON object with one key, "kind", whose value is exactly one of:

"molecular_modelling": the work computes something about molecules or materials from
  physical theory. Molecular dynamics, Monte Carlo, DFT or other quantum chemistry,
  force-field or coarse-grained simulation, docking, finite-element or mesoscale
  simulation of a material, solubility-parameter or thermodynamic prediction from
  molecular structure.
"informatics": the work builds a predictive or data-driven model of chemical or material
  behaviour. Machine learning, neural networks, QSAR/QSPR, molecular descriptors,
  cheminformatics, database screening of structures.
"statistical_doe": the work only uses experimental design or ordinary statistics.
  Factorial design, response surface methodology, ANOVA, regression fitting of measured
  data, optimisation of process variables, kinetic or isotherm curve fitting, chemometrics
  on spectra. This is NOT computational chemistry, however quantitative it is.
"none": no computational or statistical modelling is described.

When the work is mainly experimental and the modelling is a curve fit to its own
measurements, answer "statistical_doe"."""


def titles_and_abstracts():
    """Map OpenAlex id -> (title, abstract) across every harvested record file."""
    out = {}
    for p in REC.glob("*.jsonl"):
        with p.open(encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if r.get("id") and r["id"] not in out:
                    out[r["id"]] = (r.get("display_name") or r.get("title") or "",
                                    sa.deabbrev(r.get("abstract_inverted_index")))
    return out


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        sys.exit("DEEPSEEK_API_KEY is not set")
    texts = titles_and_abstracts()
    print(f"{len(texts)} records indexed")

    files = sorted(PROC.glob("screened_*.csv"))
    files = [f for f in files if not f.name.endswith(".firstpass.csv")]
    targets = {}
    for f in files:
        d = pd.read_csv(f)
        for wid in d.loc[d["method"] == "other_computational", "id"].dropna():
            targets[wid] = texts.get(wid, ("", ""))
    print(f"{len(targets)} distinct works to re-ask")

    saved_system = sa.SYSTEM
    sa.SYSTEM = SYSTEM   # the cache key includes the system prompt, so this is a new ask

    def work(item):
        wid, (t, a) = item
        res, _ = sa.ask(t, a, api_key)
        return wid, res.get("kind")

    with ThreadPoolExecutor(max_workers=12) as ex:
        verdicts = dict(ex.map(work, targets.items()))
    sa.SYSTEM = saved_system

    counts = pd.Series(list(verdicts.values())).value_counts()
    print("\nverdicts:\n" + counts.to_string())

    for f in files:
        d = pd.read_csv(f)
        keep = f.with_suffix(".firstpass.csv")
        if not keep.exists():
            d.to_csv(keep, index=False)
        mask = d["method"] == "other_computational"
        d.loc[mask, "method"] = d.loc[mask, "id"].map(verdicts).fillna("none")
        d.to_csv(f, index=False)
        print(f"  rewrote {f.name}: {int(mask.sum())} rows")


if __name__ == "__main__":
    main()
