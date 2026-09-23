#!/usr/bin/env python3
"""Probe OpenAlex record counts for candidate query blocks.

No corpus is downloaded here. The point is to see how each block behaves, and how
much each one adds, before a search string is frozen into queries/.
"""
import sys, time, json, urllib.parse
import requests

MAILTO = "aldo.combariza@unisucre.edu.co"
BASE = "https://api.openalex.org/works"

def count(search, extra=None, field="title_and_abstract.search"):
    filt = f"{field}:{search}"
    if extra:
        filt += "," + extra
    params = {"filter": filt, "per-page": 1, "mailto": MAILTO}
    for attempt in range(4):
        r = requests.get(BASE, params=params, timeout=60)
        if r.status_code == 200:
            return r.json()["meta"]["count"]
        time.sleep(2 * (attempt + 1))
    return f"ERR {r.status_code} {r.text[:120]}"

if __name__ == "__main__":
    blocks = json.load(open(sys.argv[1]))
    extra = sys.argv[2] if len(sys.argv) > 2 else None
    for name, s in blocks.items():
        c = count(s, extra)
        print(f"{c:>12}  {name}")
        sys.stdout.flush()
        time.sleep(0.3)
