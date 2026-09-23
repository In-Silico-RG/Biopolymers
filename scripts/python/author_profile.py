#!/usr/bin/env python3
"""Profile a researcher inside the harvested biopolymers corpus.

Answers the question the project keeps asking about collaborators: what is this person's
line, where do they sit, who do they work with, and is any of it computational. Reads the
OpenAlex records and, where the person has been screened, the DeepSeek classification, so
the computational answer comes from a reading of the abstract rather than a keyword.

Usage:
    author_profile.py "Marianny Combariza"
    author_profile.py "Cesar Sierra" --institution "Universidad Nacional"
    author_profile.py "Wilson Castro" --limit 15
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "data/raw/openalex/records"
PROC = ROOT / "data/processed"

COMPUTATIONAL = {"md", "qc", "qsar", "docking", "ml", "generative", "solubility",
                 "molecular_modelling", "informatics"}


def fold(s):
    """Lowercase and strip accents, so 'Cesar' matches 'César'."""
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()


def screened():
    """id -> (materials, polymer, method) from every screening file."""
    out = {}
    for p in PROC.glob("screened_*.csv"):
        if p.name.endswith(".firstpass.csv"):
            continue
        import csv
        with p.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("id"):
                    out[row["id"]] = (row.get("materials"), row.get("polymer"),
                                      row.get("method"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="all these words must appear in the author name")
    ap.add_argument("--institution", default=None,
                    help="also require this text in a matched or raw affiliation")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    parts = [fold(w) for w in args.name.split()]
    inst_q = fold(args.institution) if args.institution else None
    scr = screened()

    works, insts, coauth, topics, seen = {}, Counter(), Counter(), Counter(), set()
    for f in sorted(REC.glob("*.jsonl")):
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                wid = r.get("id")
                if not wid or wid in seen:
                    continue
                hits = []
                for a in r.get("authorships") or []:
                    n = (a.get("author") or {}).get("display_name") or ""
                    if all(p in fold(n) for p in parts):
                        aff = " ".join([i.get("display_name") or "" for i in
                                        (a.get("institutions") or [])]
                                       + (a.get("raw_affiliation_strings") or []))
                        if inst_q and inst_q not in fold(aff):
                            continue
                        hits.append((n, a))
                if not hits:
                    continue
                seen.add(wid)
                for n, a in hits:
                    for i in a.get("institutions") or []:
                        insts[i.get("display_name") or "?"] += 1
                    for raw in (a.get("raw_affiliation_strings") or [])[:1]:
                        insts["[unmatched] " + re.sub(r"\s+", " ", raw)[:70]] += 1
                for a in r.get("authorships") or []:
                    n = (a.get("author") or {}).get("display_name") or ""
                    if n and not all(p in fold(n) for p in parts):
                        coauth[n] += 1
                tp = (r.get("primary_topic") or {}).get("display_name")
                if tp:
                    topics[tp] += 1
                works[wid] = {
                    "year": r.get("publication_year"),
                    "cited": r.get("cited_by_count") or 0,
                    "title": r.get("display_name") or "",
                    "venue": ((r.get("primary_location") or {}).get("source") or {}).get(
                        "display_name") or "",
                    "screen": scr.get(wid),
                }

    if not works:
        sys.exit(f"No works found for {args.name!r}"
                 + (f" at {args.institution!r}" if args.institution else "")
                 + " in the harvested corpus.")

    ws = sorted(works.values(), key=lambda w: (-(w["year"] or 0), -w["cited"]))
    comp = [w for w in ws if w["screen"] and w["screen"][2] in COMPUTATIONAL]
    print(f"{len(ws)} works in the biopolymers corpus, "
          f"{sum(w['cited'] for w in ws)} citations, "
          f"{len(comp)} screened as computational\n")

    for w in ws[:args.limit]:
        mark = ""
        if w["screen"]:
            mats, poly, meth = w["screen"]
            bits = [b for b in (poly, meth) if b and b not in ("none", "nan")]
            if bits:
                mark = "  [" + ", ".join(bits) + "]"
        print(f"  {w['year']} | cited {w['cited']:>4} | {w['title'][:82]}{mark}")
    if len(ws) > args.limit:
        print(f"  ... and {len(ws) - args.limit} more")

    print("\naffiliations:")
    for k, v in insts.most_common(6):
        print(f"  {v:3d}  {k}")
    print("\nclosest collaborators:")
    for k, v in coauth.most_common(10):
        print(f"  {v:3d}  {k}")
    print("\ntopics:")
    for k, v in topics.most_common(8):
        print(f"  {v:3d}  {k}")


if __name__ == "__main__":
    main()
