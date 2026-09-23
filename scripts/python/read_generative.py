#!/usr/bin/env python3
"""Deep-read the generative and large-language-model works, with two independent readers.

The screening found ten works in the materials subset that use generative methods. Ten is
few enough to read every one, and they are the frontier the thesis points at, so a count is
not enough: what matters is what each one actually generates, what it is conditioned on,
and whether anything is validated.

Two readers, deliberately. DeepSeek extracts a structured summary of each abstract, and
Claude reads the same abstracts independently. A single model reading its own shortlist
would repeat whatever bias put the works on the list.

Writes:
  outputs/tables/T31_generative_works.csv     DeepSeek's structured extraction
  data/processed/validation/generative_read.md  the abstracts, for the human-side read
"""
import csv
import glob
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import screen_abstracts as sa

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "data/raw/openalex/records"
PROC = ROOT / "data/processed"
TAB = ROOT / "outputs/tables"
VAL = PROC / "validation"

SYSTEM = """You are reading the abstract of a paper that uses a generative or large-language
model method on polymers or materials. Answer ONLY with a JSON object with these keys:

"generates": what the method actually produces, in at most 12 words. Examples: "candidate
  polymer repeat units", "full lignin molecular structures", "answers about polymer
  literature", "processing parameters". If the work only predicts a property rather than
  generating a structure, say "nothing; property prediction only".
"family": one of "generative_model" (GAN, VAE, diffusion, flow), "llm" (large language
  model, including retrieval-augmented generation and agents), "inverse_design" (an
  optimisation loop targeting properties, not necessarily a generative network),
  "structure_generator" (a rule-based or stochastic builder), "other".
"conditioned_on": what steers the generation, in at most 12 words, or "nothing stated".
"validated_how": one of "experiment" (something was synthesised or measured),
  "simulation" (checked against physics-based calculation), "held_out_data" (statistical
  validation only), "none_stated".
"biopolymer": the polymer family, or "generic_polymer" if it is not specific to a
  biopolymer.
"is_biopolymer_specific": true only if the work is genuinely about a biopolymer rather
  than about polymers in general with a biopolymer mentioned in passing.
"one_line": a single sentence, at most 25 words, stating what the paper does."""


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        sys.exit("DEEPSEEK_API_KEY is not set")

    wanted = {}
    for f in glob.glob(str(PROC / "screened_*.csv")):
        if f.endswith(".firstpass.csv"):
            continue
        d = pd.read_csv(f)
        d["materials"] = d["materials"].astype("string").str.lower().map(
            {"true": True, "false": False})
        for _, r in d[(d["materials"] == True) & (d["method"] == "generative")].iterrows():
            wanted[r["id"]] = r["title"]

    texts = {}
    for p in REC.glob("*.jsonl"):
        with p.open(encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if r.get("id") in wanted and r["id"] not in texts:
                    texts[r["id"]] = {
                        "title": r.get("display_name") or "",
                        "abstract": sa.abstract_of(r),
                        "year": r.get("publication_year"),
                        "doi": r.get("doi"),
                        "venue": ((r.get("primary_location") or {}).get("source") or {}
                                  ).get("display_name") or "",
                        "cited": r.get("cited_by_count") or 0,
                    }
    print(f"{len(wanted)} works, {sum(1 for v in texts.values() if v['abstract'])} with abstracts")

    saved, sa.SYSTEM = sa.SYSTEM, SYSTEM

    def work(item):
        wid, t = item
        if not t["abstract"]:
            return wid, {"_error": "no abstract"}
        res, _ = sa.ask(t["title"], t["abstract"], api_key)
        return wid, res

    with ThreadPoolExecutor(max_workers=6) as ex:
        reads = dict(ex.map(work, texts.items()))
    sa.SYSTEM = saved

    fields = ["generates", "family", "conditioned_on", "validated_how", "biopolymer",
              "is_biopolymer_specific", "one_line"]
    TAB.mkdir(parents=True, exist_ok=True)
    with (TAB / "T31_generative_works.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "year", "cited", "venue", "title"] + fields + ["error"])
        for wid, t in sorted(texts.items(), key=lambda x: -(x[1]["year"] or 0)):
            r = reads.get(wid, {})
            w.writerow([wid, t["year"], t["cited"], t["venue"], t["title"]]
                       + [r.get(f) for f in fields] + [r.get("_error", "")])

    VAL.mkdir(parents=True, exist_ok=True)
    with (VAL / "generative_read.md").open("w", encoding="utf-8") as fh:
        fh.write("# The generative works, for independent reading\n\n")
        fh.write("DeepSeek's extraction is in outputs/tables/T31_generative_works.csv and "
                 "is deliberately not shown here.\n\n")
        for n, (wid, t) in enumerate(
                sorted(texts.items(), key=lambda x: -(x[1]["year"] or 0)), 1):
            fh.write(f"## {n}. {t['title']}\n\n")
            fh.write(f"*{t['year']} · {t['venue']} · cited {t['cited']} · {t['doi']}*\n\n")
            fh.write((t["abstract"] or "_no abstract_") + "\n\n")

    print(f"wrote {TAB / 'T31_generative_works.csv'}")
    print(f"wrote {VAL / 'generative_read.md'}")
    df = pd.read_csv(TAB / "T31_generative_works.csv")
    with pd.option_context("display.max_colwidth", 42, "display.width", 200):
        print(df[["year", "family", "generates", "validated_how",
                  "is_biopolymer_specific"]].to_string(index=False))


if __name__ == "__main__":
    main()
