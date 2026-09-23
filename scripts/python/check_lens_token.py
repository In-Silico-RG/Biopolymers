#!/usr/bin/env python3
"""Verify a Lens API token before running a harvest.

Sends the smallest possible scholarly query and reports what came back. Lens answers an
unauthenticated or malformed request with HTTP 401 and the body

    {"reference": "...", "message": "Missing/Incorrect Authorization Header", "code": 401}

which looks like a rejected token but is also exactly what you get with no token at all.
This script tells the two apart and says which.

Usage:
    check_lens_token.py                 # reads LENS_API_TOKEN, then ~/.lens_token
    check_lens_token.py <token>         # checks a token and offers to save it
"""
import json
import os
import sys
from pathlib import Path

import requests

API = "https://api.lens.org/scholarly/search"
STORE = Path.home() / ".lens_token"


def find_token(argv):
    if len(argv) > 1 and argv[1].strip():
        return argv[1].strip(), "command line"
    t = os.environ.get("LENS_API_TOKEN", "").strip()
    if t:
        return t, "LENS_API_TOKEN"
    if STORE.exists():
        t = STORE.read_text(encoding="utf-8").strip()
        if t:
            return t, str(STORE)
    return None, None


def main():
    token, where = find_token(sys.argv)
    if not token:
        print("No token found.\n")
        print("  Nothing is set in LENS_API_TOKEN and ~/.lens_token does not exist, so any")
        print("  request will return 401 'Missing/Incorrect Authorization Header'. That")
        print("  message means the request carried no credentials, not that a token was")
        print("  rejected.\n")
        print("  To get one: sign in at lens.org, open the API & Data tab, choose Trial or")
        print("  Custom Access, and complete the service request form. Approval arrives by")
        print("  email with instructions for generating the token.\n")
        print("  Then run:  check_lens_token.py <the-token>")
        sys.exit(1)

    print(f"Token found via {where} ({len(token)} characters). Testing.\n")
    body = {"query": {"query_string": {"query": "title:biopolymer"}}, "size": 1}
    try:
        r = requests.post(API, json=body, timeout=60,
                          headers={"Authorization": f"Bearer {token}",
                                   "Content-Type": "application/json"})
    except requests.RequestException as e:
        sys.exit(f"Network error reaching Lens: {e}")

    if r.status_code == 200:
        js = r.json()
        print(f"OK. HTTP 200, {js.get('total', '?')} records match a one-word test query.")
        if where == "command line" and not STORE.exists():
            STORE.write_text(token + "\n", encoding="utf-8")
            STORE.chmod(0o600)
            print(f"Saved to {STORE} with mode 600. It is gitignored and never committed.")
        print("\nReady. Run: scripts/python/harvest_lens.py")
        return

    try:
        msg = r.json()
    except ValueError:
        msg = r.text[:300]
    print(f"HTTP {r.status_code}: {json.dumps(msg, ensure_ascii=False)[:300]}\n")
    if r.status_code == 401:
        print("  401 means the header was missing or the token was not accepted. Check that")
        print("  the token was pasted whole with no surrounding quotes or trailing newline,")
        print("  and that the access request was approved rather than only submitted.")
    elif r.status_code == 403:
        print("  403 means the token is valid but the plan does not cover the scholarly API.")
        print("  Check which product the approval granted; patent and scholar are separate.")
    elif r.status_code == 429:
        print("  429 means the request rate or quota was exceeded. Wait and retry.")
    sys.exit(2)


if __name__ == "__main__":
    main()
