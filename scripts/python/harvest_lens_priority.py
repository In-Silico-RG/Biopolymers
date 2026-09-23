#!/usr/bin/env python3
"""Harvest Lens in priority order, because the trial window is short.

Probed on 2026-09-23, the five blocks across three regions come to 597,516 records, about
1,213 scroll requests. The trial subscription expires 2026-09-25, so the whole thing is not
worth attempting blind. This driver pulls what the thesis actually needs first and keeps
going only while the quota lasts.

Priority reasoning:

  1. Regional corpora, every block. Small (about 25,000 records) and the most likely place
     for Lens to hold journals OpenAlex misses, which is the whole point of triangulating.
  2. The world methods layer, L3. Only 2,822 records and it is the corpus every headline
     number in docs/02 rests on.
  3. The world core field, L1. 120,691 records; the global comparison.
  4. The big world anchors, L4 and L6. 430,000 records between them. Their totals are
     already recorded for comparison, so full records are a luxury, taken last.

Each corpus is written as it completes, so an interrupted run loses nothing already on disk.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harvest_lens as h

PRIORITY = (
    [(c, g) for g in ("colombia", "latam") for c in ("L1", "L3", "L4", "L5", "L6")]
    + [("L3", "world"), ("L5", "world"), ("L1", "world"),
       ("L6", "world"), ("L4", "world")]
)

OUT = h.OUT
MANIFEST = OUT / "manifest.json"


def load_manifest():
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return []


def main():
    tok = h.token()
    OUT.mkdir(parents=True, exist_ok=True)
    blocks = h.load_blocks()
    runs = load_manifest()
    already = {(r["block"], r["geo"]) for r in runs}

    for code, geo in PRIORITY:
        if (code, geo) in already:
            print(f"{code}_{geo}: already on disk, skipping")
            continue
        if code not in blocks:
            print(f"{code}: not in the frozen query file")
            continue
        t0 = time.time()
        try:
            rec = h.harvest(code, blocks[code], geo, tok)
        except SystemExit as e:
            # h.post exits on an unrecoverable API status. Keep what is already saved.
            print(f"\nstopped at {code}_{geo}: {e}")
            break
        rec["seconds"] = round(time.time() - t0, 1)
        runs.append(rec)
        MANIFEST.write_text(json.dumps(runs, indent=2, ensure_ascii=False), encoding="utf-8")

    done = sum(r["records"] for r in runs)
    print(f"\n{len(runs)} corpora on disk, {done:,} records total")
    print(f"manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
