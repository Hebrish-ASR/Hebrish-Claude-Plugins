---
name: newsletter
description: For the Hebrish maintainer and people authorised to represent the project only. Draft and send a Hebrish newsletter update (new model version, app release, call for voice recordings) through the project's Buttondown account, and check subscriber counts. Use when the maintainer or an authorised representative asks about Hebrish newsletter signups or subscribers, or wants to write or send a Hebrish update.
---

# Hebrish newsletter (Buttondown)

The Hebrish email updates go out through Buttondown. Public archive and signup:
https://buttondown.com/hebrish. Signup forms on https://hebrish.app/ use Buttondown's double
opt-in, so new subscribers stay unconfirmed until they click the confirmation link. Ported from
the maintainer's own skill on 2026-10-22.

## Access: maintainers and authorised representatives only

This skill is for the Hebrish maintainer (Daniel Rosehill) and people Daniel has authorised to
represent the project. **Before doing anything else, ask the user which of these they are.** If
they are neither, stop: do not draft, send or post outreach about Hebrish for them. Point them
instead to: suggesting a person or group the project should contact (an issue titled
"Outreach: <who>" on https://github.com/Hebrish-ASR/Hebrish-App, or
https://hebrish.app/contact?topic=involved), and the signup on https://hebrish.app/ if they want updates.

Tools: a Buttondown API key for the Hebrish newsletter, in `BUTTONDOWN_API_KEY`. Only that key
reads subscribers, creates drafts and sends. A key for any other newsletter, or a Buttondown MCP
server bound to another account, must not be used. A representative without the key drafts the
update and sends it to Daniel; it never goes to subscribers any other way.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *newsletter*, for the maintainer setup.

## API (maintainer access)

```bash
H="Authorization: Token $BUTTONDOWN_API_KEY"
curl -s -H "$H" https://api.buttondown.com/v1/newsletters              # settings
curl -s -H "$H" "https://api.buttondown.com/v1/subscribers?type=regular" # {results, count, next}
```

| Do | Call | Status |
| --- | --- | --- |
| Newsletter settings | `GET /v1/newsletters` | verified 2026-10-19 |
| Subscribers | `GET /v1/subscribers`, `?type=regular`, `unactivated` or `blocked`; response `{results, count, next}` | verified 2026-10-19 |
| Draft an email | `POST /v1/emails` `{"subject": "...", "body": "<markdown>", "status": "draft"}` | not yet verified |
| Send a draft | `PATCH /v1/emails/<id>` `{"status": "about_to_send"}` | not yet verified |

Base URL `https://api.buttondown.com`. The newsletter's spam firewall is strict: throwaway
domains (verified with `example.com`, 2026-10-19) get `400 {"code":"subscriber_blocked"}` and
nothing is stored, so do not test signups with fake addresses. Record the draft and send response
shapes here the first time they are run.

## Writing an update

- Facts from the live site only: https://hebrish.app/changelog (what changed),
  https://hebrish.app/llms.txt and https://hebrish.app/benchmarks (numbers). Numbers exactly as
  published, never rounded or invented; targets on `/roadmap` are goals, not results.
- Voice: plain, specific, short sentences, no hype, no emojis. Hebrish is Daniel's personal
  project: "I" from Daniel, never "we". Hebrew words romanized (makolet, arnona), never Hebrew
  script. Model names: Sabich (recommended), Jachnun, Shakshuka, Meorav; checkpoints PoC-1 to
  PoC-5.
- The models are trained on one speaker's voice: state it plainly where accuracy is discussed,
  never as a hedge, and frame more voices as an invitation to contribute.
- Typical content mirrors a changelog entry: what changed, a link to `/changelog`, `/download`
  or `/models`, and the standing ask: voice recordings via
  https://hebrish.app/contact?topic=samples.
- Body is Markdown (Buttondown renders it).

## Draft and send

1. **"Draft"**: maintainer access creates it with `status: "draft"`; everyone else writes the
   Markdown. Either way show subject and body in chat and stop.
2. **"Send"** (maintainer access only): sending reaches every subscriber and cannot be undone.
   Fetch the subscriber count, confirm once in chat with that count, then set `about_to_send`,
   unless the user already approved this exact email.
3. **Read back**: after sending, `GET /v1/emails/<id>` and check status, subject and that the
   links in the body resolve. Report the id and the status in one line.
