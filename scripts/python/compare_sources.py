#!/usr/bin/env python3
"""Compare the OpenAlex and Lens corpora: counts, and how much they actually overlap.

This is the point of triangulating. Two numbers matter. How far the counts diverge for the
same concept, which says how much of any share reported so far is a property of the source
rather than of the literature. And how much the record sets overlap by DOI, which says
whether the divergence is different coverage or merely different indexing of the same works.

Writes outputs/tables/T26_source_counts.csv and T27_source_overlap.csv.
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OA_AGG = ROOT / "data/raw/openalex/aggregates"
OA_REC = ROOT / "data/raw/openalex/records"
LENS = ROOT / "data/raw/lens"
TAB = ROOT / "outputs/tables"

Y0, Y1 = 1990, 2026

# Lens block -> the OpenAlex corpus asking the same question.
PAIRS = {
    ("L1", "world"): "core_world", ("L1", "latam"): "core_latam",
    ("L1", "colombia"): "core_colombia",
    ("L3", "world"): "methods_world", ("L3", "latam"): "methods_latam",
    ("L3", "colombia"): "methods_colombia",
    ("L4", "latam"): "anchor_cellulose_latam", ("L4", "colombia"): "anchor_cellulose_colombia",
    ("L5", "world"): "anchor_pha_world", ("L5", "latam"): "anchor_pha_latam",
    ("L5", "colombia"): "anchor_pha_colombia",
    ("L6", "latam"): "anchor_lignin_latam", ("L6", "colombia"): "anchor_lignin_colombia",
}

DOI_RE = re.compile(r"10\.\d{4,9}/\S+", re.I)


def oa_count(corpus):
    """OpenAlex count for the same 1990-2026 window Lens was asked for."""
    p = OA_AGG / f"{corpus}__publication_year.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p)
    d = d[pd.to_numeric(d["key"], errors="coerce").notna()].copy()
    d["key"] = d["key"].astype(int)
    return int(d.loc[(d["key"] >= Y0) & (d["key"] <= Y1), "count"].sum())


def norm_doi(s):
    if not s:
        return None
    m = DOI_RE.search(str(s))
    return m.group(0).lower().rstrip(".").rstrip(")") if m else None


def oa_dois(corpus):
    p = OA_REC / f"{corpus}.jsonl"
    if not p.exists():
        return None
    out = set()
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            d = norm_doi(json.loads(line).get("doi"))
            if d:
                out.add(d)
    return out


def lens_dois(block, geo):
    p = LENS / f"{block}_{geo}.jsonl"
    if not p.exists():
        return None
    out = set()
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            ext = r.get("external_ids") or []
            for e in ext:
                if str(e.get("type", "")).lower() == "doi":
                    d = norm_doi(e.get("value"))
                    if d:
                        out.add(d)
    return out


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    manifest = {}
    mpath = LENS / "manifest.json"
    if mpath.exists():
        for r in json.loads(mpath.read_text(encoding="utf-8")):
            manifest[(r["block"], r["geo"])] = r

    counts, overlaps = [], []
    for (block, geo), corpus in PAIRS.items():
        m = manifest.get((block, geo))
        if not m:
            continue
        lens_n, oa_n = m["records"], oa_count(corpus)
        counts.append({
            "block": block, "geo": geo, "openalex_corpus": corpus,
            "openalex": oa_n, "lens": lens_n,
            "lens_vs_openalex_pct": round(lens_n / oa_n * 100, 1) if oa_n else None,
        })
        ld, od = lens_dois(block, geo), oa_dois(corpus)
        if ld is None or od is None:
            continue
        inter = ld & od
        union = ld | od
        overlaps.append({
            "block": block, "geo": geo,
            "lens_with_doi": len(ld), "openalex_with_doi": len(od),
            "in_both": len(inter), "lens_only": len(ld - od), "openalex_only": len(od - ld),
            "jaccard_pct": round(len(inter) / len(union) * 100, 1) if union else None,
            "pct_of_openalex_found_in_lens": round(len(inter) / len(od) * 100, 1) if od else None,
            "pct_of_lens_found_in_openalex": round(len(inter) / len(ld) * 100, 1) if ld else None,
        })

    c = pd.DataFrame(counts)
    c.to_csv(TAB / "T26_source_counts.csv", index=False)
    print(c.to_string(index=False))
    if overlaps:
        o = pd.DataFrame(overlaps)
        o.to_csv(TAB / "T27_source_overlap.csv", index=False)
        print()
        print(o.to_string(index=False))


if __name__ == "__main__":
    main()
