#!/usr/bin/env python3
"""Measure how much regional output OpenAlex loses to unmatched affiliations.

Found the hard way. A 2025 paper by Wilson Castro carries two Peruvian affiliations,
Universidad Nacional de Frontera and Universidad Nacional de Cañete, and OpenAlex matched
neither to an institution entity. Only one of its six authorships matched at all, to
Universidad de Guadalajara, so the work counts as Mexican and Peru gets nothing.

This matters beyond one paper. Every regional corpus in this project was selected with
`institutions.country_code`, so a work whose Latin American affiliations all went unmatched
never entered the regional corpus in the first place. The regional counts are therefore a
lower bound, and this script estimates by how much.

Method: scan the world corpora, read the raw affiliation strings, and count works whose
raw text names a Latin American country or a known Latin American institution keyword but
whose matched institutions carry no Latin American country code.

Writes outputs/tables/T28_affiliation_misses.csv.
"""
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "data/raw/openalex/records"
TAB = ROOT / "outputs/tables"

LATAM = {"AR", "BO", "BR", "CL", "CO", "CR", "CU", "DO", "EC", "GT", "HN", "MX",
         "NI", "PA", "PE", "PR", "PY", "SV", "UY", "VE"}

# Country names as they appear in raw affiliation strings, accents stripped.
NAMES = {
    "argentina": "AR", "bolivia": "BO", "brasil": "BR", "brazil": "BR", "chile": "CL",
    "colombia": "CO", "costa rica": "CR", "cuba": "CU", "republica dominicana": "DO",
    "ecuador": "EC", "guatemala": "GT", "honduras": "HN", "mexico": "MX",
    "nicaragua": "NI", "panama": "PA", "peru": "PE", "puerto rico": "PR",
    "paraguay": "PY", "el salvador": "SV", "uruguay": "UY", "venezuela": "VE",
}
WORD = {n: re.compile(rf"\b{re.escape(n)}\b") for n in NAMES}


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


def scan(stem):
    p = REC / f"{stem}.jsonl"
    if not p.exists():
        return None
    total = matched_latam = raw_latam = missed = 0
    auth_total = auth_unmatched = auth_unmatched_with_text = 0
    missed_countries = {}
    per_country_missed, per_country_ok = {}, {}
    examples = []
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            total += 1
            codes, raw_hits = set(), set()
            for a in r.get("authorships") or []:
                auth_total += 1
                insts = a.get("institutions") or []
                if not insts:
                    auth_unmatched += 1
                for i in insts:
                    if i.get("country_code"):
                        codes.add(i["country_code"])
                raws = a.get("raw_affiliation_strings") or []
                txt = strip_accents(" ; ".join(raws))
                if not insts and len(txt.strip(" ;,")) > 3:
                    auth_unmatched_with_text += 1
                for name, code in NAMES.items():
                    if WORD[name].search(txt):
                        raw_hits.add(code)
            # Per-country loss, which is the case that matters and that a whole-work
            # test misses. The paper that exposed this counts for Mexico through a matched
            # Guadalajara affiliation while both of its Peruvian affiliations went
            # unmatched, so Peru loses a work that the work-level test calls fine.
            for c in raw_hits - codes:
                per_country_missed[c] = per_country_missed.get(c, 0) + 1
            for c in raw_hits & codes:
                per_country_ok[c] = per_country_ok.get(c, 0) + 1

            has_matched = bool(codes & LATAM)
            if has_matched:
                matched_latam += 1
            if raw_hits:
                raw_latam += 1
            if raw_hits and not has_matched:
                missed += 1
                for c in raw_hits:
                    missed_countries[c] = missed_countries.get(c, 0) + 1
                if len(examples) < 5:
                    examples.append((r.get("display_name") or "")[:70])
    return {
        "corpus": stem, "works": total,
        "matched_latam": matched_latam,
        "raw_text_names_latam": raw_latam,
        "missed_works": missed,
        "undercount_pct_of_matched": round(missed / matched_latam * 100, 1) if matched_latam else None,
        "authorships": auth_total,
        "authorships_unmatched_pct": round(auth_unmatched / auth_total * 100, 1) if auth_total else None,
        "authorships_unmatched_with_text_pct": round(
            auth_unmatched_with_text / auth_total * 100, 1) if auth_total else None,
        "missed_by_country": json.dumps(dict(sorted(missed_countries.items(),
                                                    key=lambda x: -x[1])), ensure_ascii=False),
        "example": examples[0] if examples else "",
        "_per_country": {c: {"credited": per_country_ok.get(c, 0),
                             "lost": per_country_missed.get(c, 0)}
                         for c in set(per_country_ok) | set(per_country_missed)},
    }


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    rows = [r for r in (scan(s) for s in ("methods_world", "core_latam", "core_colombia"))
            if r]
    per = []
    for r in rows:
        for c, v in r.pop("_per_country").items():
            tot = v["credited"] + v["lost"]
            per.append({"corpus": r["corpus"], "country": c,
                        "credited_by_openalex": v["credited"], "lost_to_no_match": v["lost"],
                        "loss_pct": round(v["lost"] / tot * 100, 1) if tot else None})
    pc = pd.DataFrame(per)
    if not pc.empty:
        pc = pc.sort_values(["corpus", "lost_to_no_match"], ascending=[True, False])
        pc.to_csv(TAB / "T29_country_attribution_loss.csv", index=False)
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "T28_affiliation_misses.csv", index=False)
    with pd.option_context("display.max_colwidth", 60):
        print(df.drop(columns=["missed_by_country", "example"]).to_string(index=False))
    print()
    for r in rows:
        print(f"{r['corpus']}: works losing ALL Latin American attribution -> {r['missed_by_country']}")
    if not pc.empty:
        print("\nPer-country attribution loss (a country named in the raw affiliation "
              "text with no matched institution in it):")
        for corpus in pc["corpus"].unique():
            sub = pc[(pc["corpus"] == corpus) & (pc["lost_to_no_match"] > 0)].head(10)
            if len(sub):
                print(f"\n  {corpus}")
                print(sub.drop(columns=["corpus"]).to_string(index=False))


if __name__ == "__main__":
    main()
