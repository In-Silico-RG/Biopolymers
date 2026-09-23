#!/usr/bin/env python3
"""Draw a blind sample for validating the DeepSeek screening.

Design note, which is the whole point. Asking DeepSeek to check its own labels is not
validation: the same model repeats the same mistakes, and the agreement it reports is
meaningless. The second coder has to be a different system. Here it is Claude, coding the
same abstracts without seeing the DeepSeek labels, after which agreement is computed as
Cohen's kappa rather than as bare percent agreement, because percent agreement flatters any
classification with one dominant class.

Two samples are drawn:

  random  a simple random sample of readable works, which gives an honest agreement figure
          for the mix the corpus actually has;
  rare    a targeted sample of thin categories (generative, qsar, solubility,
          statistical_doe), which the random draw would barely touch, reported separately
          and never pooled into the headline figure.

Writes the blind file (id, title, abstract, nothing else) and, separately, the key. The key
is not read until the coding is submitted.
"""
import argparse
import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import screen_abstracts as sa

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "data/raw/openalex/records"
PROC = ROOT / "data/processed"
VAL = PROC / "validation"

RARE = {"generative", "qsar", "solubility", "statistical_doe", "docking"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="methods_world")
    ap.add_argument("--random", type=int, default=100)
    ap.add_argument("--rare", type=int, default=25)
    ap.add_argument("--seed", type=int, default=20260923)
    args = ap.parse_args()

    labels = {}
    with (PROC / f"screened_{args.corpus}.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("id"):
                labels[row["id"]] = row

    texts = {}
    with (REC / f"{args.corpus}.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            a = sa.abstract_of(r)
            if r.get("id") and a and len(a.split()) >= 30:
                texts[r["id"]] = ((r.get("display_name") or r.get("title") or ""), a)

    readable = [i for i in texts if i in labels
                and str(labels[i].get("materials", "")).lower() in ("true", "false")]
    rng = random.Random(args.seed)
    rng.shuffle(readable)

    rand = readable[:args.random]
    chosen = set(rand)
    rare_pool = [i for i in readable
                 if i not in chosen and labels[i].get("method") in RARE]
    rng.shuffle(rare_pool)
    rare = rare_pool[:args.rare]

    VAL.mkdir(parents=True, exist_ok=True)
    items = [(i, "random") for i in rand] + [(i, "rare") for i in rare]
    rng.shuffle(items)          # so the coder cannot infer the stratum from position

    blind = VAL / f"blind_{args.corpus}.md"
    with blind.open("w", encoding="utf-8") as fh:
        fh.write(f"# Blind coding sheet: {len(items)} abstracts\n\n")
        fh.write("Code each item with: materials (yes/no), polymer family, method, "
                 "experimental (yes/no).\nDo not look at the key.\n\n")
        for n, (i, _) in enumerate(items, 1):
            t, a = texts[i]
            fh.write(f"## {n}\n\n**{t}**\n\n{a[:2200]}\n\n")
    key = VAL / f"key_{args.corpus}.csv"
    with key.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "id", "stratum", "ds_materials", "ds_polymer", "ds_method",
                    "ds_experimental", "title"])
        for n, (i, stratum) in enumerate(items, 1):
            L = labels[i]
            w.writerow([n, i, stratum, L.get("materials"), L.get("polymer"),
                        L.get("method"), L.get("experimental"), texts[i][0]])

    print(f"{len(rand)} random + {len(rare)} rare = {len(items)} items")
    print(f"blind sheet: {blind.relative_to(ROOT)}")
    print(f"key (do not open until coded): {key.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
