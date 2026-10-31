---
name: outreach-email
description: For the Hebrish maintainer and people authorised to represent the project only. Write an email about Hebrish (hebrish.app) to a researcher, app maker, organisation or journalist in the branded Hebrish HTML template plus plain text, and send it as the project (info@hebrish.app) with the project's Resend key. Use when the maintainer or an authorised representative asks to email, pitch, introduce or follow up with someone about Hebrish.
---

# Hebrish outreach email

One template, so every email about Hebrish looks the same and says the same true things.
Ported from the maintainer's own skill on 2026-10-22.

## Access: maintainers and authorised representatives only

This skill is for the Hebrish maintainer (Daniel Rosehill) and people Daniel has authorised to
represent the project. **Before doing anything else, ask the user which of these they are.** If
they are neither, stop: do not draft, send or post outreach about Hebrish for them. Point them
instead to: suggesting a person or group the project should contact (an issue titled
"Outreach: <who>" on https://github.com/Hebrish-ASR/Hebrish-App, or
https://hebrish.app/contact?topic=involved), and the signup on https://hebrish.app/ if they want updates.

Who sends what:
- **Maintainer** (or a representative trusted with it): a Resend API key for the hebrish.app
  domain, in `RESEND_API_KEY`, or a Resend MCP server configured with that key. Mail goes from
  `Hebrish AI <info@hebrish.app>` with replies to `info@hebrish.app`, signed by Daniel
  Rosehill (`"signature": "project"`). Only send if the user confirms.
- **Authorised representative** without the key: render with `"signature"` set to their own
  name and a title such as "for Hebrish", and they send it from their own address.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *outreach-email*, for the maintainer setup.

## Files

Paths are relative to `${CLAUDE_PLUGIN_ROOT}/skills/outreach-email/`. If `CLAUDE_PLUGIN_ROOT`
is unset, clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/outreach-email/` inside it.

| File | What |
| --- | --- |
| `template.html` | Email layout: optional Hebrish wordmark header with a gold-and-line rule, greeting, body, signature, optional links box. Table-based, inline styles, light only. `{{...}}` placeholders. |
| `scripts/render.py` | `python3 scripts/render.py BRIEF.json OUT_DIR` writes `OUT_DIR/<slug>.html` and `.txt`, prints `{"html","text","subject","to","signature"}`. Stdlib only. Exits on any unfilled placeholder or a missing `signature`. |
| `scripts/send_resend.py` | Maintainer access only. Posts one rendered email to `https://api.resend.com/emails`. `--dry-run` prints the payload. Not yet run against the live API from this plugin (2026-10-22); the payload follows Resend's documented `POST /emails` fields. |
| `examples/project.json` | Brief for a project email (`"signature": "project"`). |
| `examples/representative.json` | Brief for an authorised representative signing with their own name. |

Fixed footer (Daniel, 2026-10-31): every email ends with the same boilerplate, defined once in
`scripts/render.py` (`FOOTER_LINES`, `NEWSLETTER`) and rendered in the brand band colour under the
signature and links. It says the email is personal and may be written with AI assistance, that the
recipient is on no mailing list and can reply "unsubscribe" to never be contacted again, and links
the newsletter signup (`https://hebrish.app/#foot-email`, the site footer form; Buttondown,
double opt-in), and ends with quick links to About, Models, Datasets and Benchmarks
(`FOOTER_LINKS`). Briefs cannot change or drop it. Change the wording only in `render.py`, and keep
it in step with `/brand` if the outreach template there is updated. Someone who replies
"unsubscribe" is not emailed again: note it where the outreach is tracked.

BCC (Daniel, 2026-10-31): every project send BCCs the maintainer, `daniel@danielrosehill.co.il`.
`send_resend.py` adds it by default (`--no-maintainer-bcc` only for the test copy to that
address); through a Resend MCP server, pass `bcc: ["daniel@danielrosehill.co.il"]` yourself.

Brief fields: `slug`, `to[]`, `signature` (`"project"` or `{"name", "title"?, "location"?,
"photo"?, "links"?: [{"text","href"}]}`), `subject`, `preheader`, `greeting`, `paragraphs[]`
(inline `[text](https://url)` links allowed), `signoff` (default `Best,`), `signoff_name`
(default the signature's first name), `logo` (default on for project, off for a representative),
optional `links_heading` and `links[]` of `{label, href, text}`.

The logo is `https://hebrish.app/img/brand/wordmark-1080.png` (PNG, because Gmail and Outlook
drop SVG). Colours are the light set of the Hebrish brand (https://hebrish.app/brand).

## Steps

1. **Facts.** Take every claim from the live site, not from memory or an old draft:
   https://hebrish.app/llms.txt (key facts and current numbers), `/benchmarks`, `/changelog`,
   `/download`. Rules:
   - Hebrish is Daniel Rosehill's one-person project. Never "we" or "the team".
   - Numbers exactly as published, never rounded or invented. Targets on `/roadmap` are goals,
     not results. Say which benchmark a number is from if you quote one.
   - Model names: Sabich (recommended in the apps), Jachnun; checkpoints PoC-1 to PoC-5.
     PoC-4 and PoC-5 were not benchmarked.
   - The models are trained on one speaker's voice. Say so plainly only where accuracy is
     discussed technically; do not lead with it. If more voices come up, it is an invitation to
     contribute recordings (https://hebrish.app/contact?topic=samples).
   - Hebrew words in their romanized form (makolet, arnona, kupat holim), never Hebrew script.
     Example terms must exist in the lexicon: check
     `curl -s https://hebrish.app/data/lexicon.json | python3 -c "import json,sys; t={x['t'].lower() for x in json.load(sys.stdin)['terms']}; print('makolet' in t)"`
     (each term is `{"t": term, "d": domain, "m": meaning, "n": recordings}`).
   - No AI mention in the body. The fixed footer (below) already says outreach may be written
     with AI assistance.
2. **Style.** Short sentences (under about 15 words), 3 to 8 sentences. First sentence says why
   you are writing. First person singular. Respectful, not deferential. Not promotional: no
   superlatives, no "excited to", no emojis; the link does the selling. One clear ask near the
   end (try it, pass it on, or send words it gets wrong).
   - For an organisation, the usual shape is: who is writing (one line); the problem in their
     words, English sentences with Hebrew words in them, with 2 to 4 terms from their domain;
     what exists (an open model plus free apps for Android, Ubuntu and Windows); links
     (`/download`, `/demo`, and for technical readers `/models` and `/dataset`); one ask.
3. **Brief.** Write the brief JSON outside any repository (it holds recipients' addresses),
   for example in a scratch or temp directory. Set `signature`:
   - `"project"` only on the maintainer-access path;
   - otherwise (an authorised representative) `{"name": "<their name>", "title": "for Hebrish"}`.
4. **Render.** `python3 "${CLAUDE_PLUGIN_ROOT}/skills/outreach-email/scripts/render.py" brief.json OUTDIR`.
5. **Review.** Show the subject, recipients and the `.txt` body in chat. "Draft" or "prepare"
   stops here. A cold email to someone not written to before: wait for an explicit yes even if
   the user said "send".
6. **Send.**
   - *Maintainer access.* Send a test copy to the user's own address first for any new kind of
     message, and check it renders. Then one email per recipient (never many people in one
     `to`):
     `python3 .../scripts/send_resend.py --to ADDRESS --subject "..." --html OUTDIR/slug.html --text OUTDIR/slug.txt`
     (add `--dry-run` first to check the payload). Through a Resend MCP server, pass the same
     fields: `from`, `to`, `subject`, `html` (raw markup, never entity-escaped `&lt;p&gt;`),
     `text` (required whenever `html` is set), `replyTo`, `tags` `[{"name":"kind","value":"outreach"}]`.
   - *Authorised representative without the key.* Give them the `.txt` body to paste, and the
     `.html` path for the styled version. They send it from their own account.
7. **Read back.** After a project send, report recipient, subject and the returned email id in
   one line. A send-only key cannot fetch the message again, so the test copy from step 6 is the
   read-back: open it and check the sender, links and rendering. If the dashboard is available,
   confirm delivery there.

## Hebrew-language mail

The template is English, left to right. A Hebrew body needs each paragraph wrapped in raw
`<div dir="rtl" style="text-align:right;">` (never entity-escaped markup, which sends without
error and shows the recipient the tags), and dates, phone and reference numbers checked after
sending, because mail clients reorder separators inside them in plain-text RTL. Model output
quoted in the email stays romanized.
