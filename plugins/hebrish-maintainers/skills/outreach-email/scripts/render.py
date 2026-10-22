#!/usr/bin/env python3
"""Render a Hebrish outreach email from a JSON brief into HTML and plain text.

Usage: python3 render.py BRIEF.json OUT_DIR
Writes OUT_DIR/<slug>.html and OUT_DIR/<slug>.txt and prints
{"html", "text", "subject", "to", "signature"} as JSON.

Stdlib only. Reads ../template.html (next to this script's folder). Fails on any
unfilled {{placeholder}}. Brief fields: see ../examples/*.json and the skill's SKILL.md.

"signature" decides who the email is from:
  "project"  the maintainer's signature (Daniel Rosehill, maker of Hebrish). Only for
             mail sent as the project, from info@hebrish.app, by someone with the
             project's Resend key.
  {object}   an authorised representative of the project: {"name": ..., "title"?,
             "location"?, "photo"?, "links"?: [{"text": ..., "href": ...}]}, sent from
             their own address. The Hebrish logo header is off unless the brief sets
             "logo": true.
"""
import html
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "template.html"

# Light palette of the Hebrish brand tokens (https://hebrish.app/brand). Emails are always light.
C = {
    "bg": "#fbf8f2", "surface": "#ffffff", "band": "#f1ece1",
    "ink": "#1d2422", "muted": "#5b6662", "line": "#e2dccf",
    "accent": "#0f6b5c", "gold": "#c8901c",
}
FONT = "'Segoe UI', Helvetica, Arial, sans-serif"  # web fonts are not safe in mail clients
SERIF = "Georgia, 'Times New Roman', serif"

# Served by hebrish.app. PNG, because Gmail and Outlook drop SVG.
LOGO = "https://hebrish.app/img/brand/wordmark-1080.png"

# The maintainer's public signature, used only with "signature": "project".
PROJECT_SIGNATURE = {
    "name": "Daniel Rosehill",
    "title": "Maker of Hebrish",
    "location": "Jerusalem, Israel",
    "photo": "https://www.danielrosehill.com/images/email/daniel-avatar.jpg",
    "links": [
        {"text": "hebrish.app", "href": "https://hebrish.app"},
        {"text": "danielrosehill.com", "href": "https://www.danielrosehill.com"},
        {"text": "GitHub", "href": "https://github.com/danielrosehill"},
        {"text": "Hugging Face", "href": "https://huggingface.co/danielrosehill"},
    ],
}

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def inline_html(text):
    """Escape a paragraph, then turn [text](url) into styled links."""
    out, pos = [], 0
    for m in LINK_RE.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        out.append(f'<a href="{html.escape(m[2])}" style="color:{C["accent"]};font-weight:600;">{html.escape(m[1])}</a>')
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def inline_text(text):
    return LINK_RE.sub(lambda m: f"{m[1]} ({m[2]})", text)


def resolve_signature(brief):
    sig = brief.get("signature")
    if sig == "project":
        return dict(PROJECT_SIGNATURE), True
    if isinstance(sig, dict) and sig.get("name"):
        return sig, False
    raise SystemExit('brief needs "signature": "project" (sending as the project only) '
                     'or {"name": "Your Name", ...} (everyone else)')


def render(brief):
    sig, is_project = resolve_signature(brief)
    show_logo = brief.get("logo", is_project)
    signoff_name = brief.get("signoff_name") or sig["name"].split()[0]

    para = f'<p style="margin:0 0 16px;font-size:16px;line-height:1.65;color:{C["ink"]};">{{}}</p>'
    paragraphs = "\n      ".join(para.format(inline_html(p)) for p in brief["paragraphs"])

    header = ""
    if show_logo:
        header = f"""    <tr><td style="padding:24px 40px 20px;">
      <a href="https://hebrish.app" style="text-decoration:none;"><img src="{LOGO}" width="198" height="44" alt="Hebrish" style="display:block;width:198px;height:44px;border:0;"></a>
    </td></tr>
    <tr><td style="padding:0 40px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="height:3px;line-height:3px;font-size:0;background:{C["gold"]};width:48px;">&nbsp;</td><td style="height:3px;line-height:3px;font-size:0;background:{C["line"]};">&nbsp;</td></tr></table></td></tr>
"""

    photo_cell = ""
    if sig.get("photo"):
        photo_cell = f"""          <td valign="middle" style="padding-right:16px;width:64px;">
            <img src="{html.escape(sig["photo"])}" width="64" height="64" alt="{html.escape(sig["name"])}" style="display:block;width:64px;height:64px;border-radius:50%;border:2px solid {C["line"]};">
          </td>
"""
    sub = " &middot; ".join(html.escape(sig[k]) for k in ("title", "location") if sig.get(k))
    subline = f'<p style="margin:2px 0 0;font-size:14px;color:{C["muted"]};">{sub}</p>' if sub else ""
    sig_link_list = sig.get("links") or []
    sig_links = ""
    if sig_link_list:
        sep = f'<span style="color:{C["line"]};">&nbsp;&nbsp;|&nbsp;&nbsp;</span>'
        sig_links = '<p style="margin:8px 0 0;font-size:13px;line-height:1.6;">' + sep.join(
            f'<a href="{html.escape(l["href"])}" style="color:{C["accent"]};text-decoration:none;font-weight:600;">{html.escape(l["text"])}</a>'
            for l in sig_link_list) + "</p>"

    links = brief.get("links") or []
    links_box = ""
    if links:
        rows = "\n        ".join(
            f'<p style="margin:0 0 4px;font-size:14px;line-height:1.5;color:{C["ink"]};"><span style="color:{C["muted"]};">{html.escape(l["label"])}:</span> '
            f'<a href="{html.escape(l["href"])}" style="color:{C["accent"]};text-decoration:none;font-weight:600;">{html.escape(l["text"])}</a></p>'
            for l in links)
        links_box = f"""
    <tr><td style="padding:4px 40px 36px;font-family:{FONT};">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{C["band"]};border-radius:8px;"><tr><td style="padding:16px 20px;">
        <p style="margin:0 0 8px;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:{C["muted"]};font-weight:600;">{html.escape(brief.get("links_heading", "Links"))}</p>
        {rows}
      </td></tr></table>
    </td></tr>"""

    out_html = (TEMPLATE.read_text(encoding="utf-8")
        .replace("{{subject}}", html.escape(brief["subject"]))
        .replace("{{preheader}}", html.escape(brief.get("preheader", "")))
        .replace("{{header}}", header)
        .replace("{{body_top}}", "32" if show_logo else "36")
        .replace("{{greeting}}", html.escape(brief["greeting"]))
        .replace("{{paragraphs}}", paragraphs)
        .replace("{{signoff}}", html.escape(brief.get("signoff", "Best,")))
        .replace("{{signoff_name}}", html.escape(signoff_name))
        .replace("{{sig_photo_cell}}", photo_cell)
        .replace("{{sig.name}}", html.escape(sig["name"]))
        .replace("{{sig_subline}}", subline)
        .replace("{{sig_links}}", sig_links)
        .replace("{{links_box}}", links_box)
        .replace("{{font}}", FONT).replace("{{serif}}", SERIF))
    for k, v in C.items():
        out_html = out_html.replace("{{c." + k + "}}", v)
    left = re.search(r"{{[^}]*}}", out_html)
    if left:
        raise SystemExit(f"unfilled placeholder: {left[0]}")

    text = [brief["greeting"], ""]
    for p in brief["paragraphs"]:
        text += [inline_text(p), ""]
    text += [brief.get("signoff", "Best,"), signoff_name, ""]
    for l in links:
        text.append(f'{l["label"]}: {l["href"]}')
    head = sig["name"] + (f', {sig["title"]}' if sig.get("title") else "")
    text += ["", "--", head]
    if sig.get("location"):
        text.append(sig["location"])
    if sig_link_list:
        text.append(" | ".join(l["href"] for l in sig_link_list))
    return out_html, "\n".join(text).strip() + "\n", is_project


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: render.py BRIEF.json OUT_DIR")
    brief_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    out_html, out_text, is_project = render(brief)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = brief.get("slug") or brief_path.stem
    h, t = out_dir / f"{slug}.html", out_dir / f"{slug}.txt"
    h.write_text(out_html, encoding="utf-8")
    t.write_text(out_text, encoding="utf-8")
    print(json.dumps({"html": str(h), "text": str(t), "subject": brief["subject"],
                      "to": brief.get("to", []),
                      "signature": "project" if is_project else "representative"}))


if __name__ == "__main__":
    main()
