#!/usr/bin/env python3
"""Send one rendered Hebrish email through the Resend REST API, as the project.

Only for someone who holds the project's Resend API key for the hebrish.app domain.
Only the maintainer, or a representative Daniel has authorised and given the key, runs this.

Usage:
  RESEND_API_KEY=... python3 send_resend.py --to someone@example.org \
      --subject "..." --html out/slug.html --text out/slug.txt [--dry-run]

Defaults: from "Hebrish AI <info@hebrish.app>", reply-to info@hebrish.app,
tag kind=outreach. One recipient per call: send several people one email each.
Prints the API response (on success {"id": "..."}) or, with --dry-run, the payload
without the key. Stdlib only.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.resend.com/emails"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True, help="one recipient address")
    ap.add_argument("--subject", required=True)
    ap.add_argument("--html", required=True, type=Path)
    ap.add_argument("--text", required=True, type=Path)
    ap.add_argument("--from", dest="sender", default="Hebrish AI <info@hebrish.app>")
    ap.add_argument("--reply-to", default="info@hebrish.app")
    ap.add_argument("--cc", action="append", default=[])
    ap.add_argument("--bcc", action="append", default=[])
    ap.add_argument("--tag", default="kind=outreach", help="name=value")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if "," in a.to:
        raise SystemExit("one recipient per email; run once per person")
    name, _, value = a.tag.partition("=")
    payload = {
        "from": a.sender,
        "to": [a.to],
        "subject": a.subject,
        "html": a.html.read_text(encoding="utf-8"),
        "text": a.text.read_text(encoding="utf-8"),
        "reply_to": a.reply_to,
        "tags": [{"name": name, "value": value}],
    }
    if a.cc:
        payload["cc"] = a.cc
    if a.bcc:
        payload["bcc"] = a.bcc
    if "&lt;" in payload["html"][:200]:
        raise SystemExit("html looks entity-escaped; pass the raw rendered file")

    if a.dry_run:
        shown = dict(payload, html=f"<{len(payload['html'])} chars>", text=payload["text"])
        print(json.dumps(shown, indent=2, ensure_ascii=False))
        return

    key = os.environ.get("RESEND_API_KEY")
    if not key:
        raise SystemExit("RESEND_API_KEY is not set. Without the project's key, send the "
                         "rendered email from your own account instead.")
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "hebrish-outreach/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(r.read().decode())
    except urllib.error.HTTPError as e:
        print(e.read().decode(), file=sys.stderr)
        raise SystemExit(f"Resend returned HTTP {e.code}")


if __name__ == "__main__":
    main()
