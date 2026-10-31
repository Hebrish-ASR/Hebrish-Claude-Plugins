---
name: community-fyi
description: For the Hebrish maintainer and people authorised to represent the project only. Draft a short, friendly FYI about Hebrish (hebrish.app) for an English-speaking AI, tech or olim community in Israel (WhatsApp or Slack groups, meetups, Facebook groups, newsletters, organisations), picking the right channel and wording; the user posts it. Use when the maintainer or an authorised representative asks to tell, ping, give a heads-up to or post in a community about Hebrish.
---

# Hebrish community FYI

A light-touch heads-up, not a pitch: "this exists, it's free, it might be useful to you or your
members". Ported from the maintainer's own skill on 2026-10-22. For a full email to one
organisation, use the `outreach-email` skill in this plugin; this skill decides the channel
and the words.

## Access: maintainers and authorised representatives only

This skill is for the Hebrish maintainer (Daniel Rosehill) and people Daniel has authorised to
represent the project. **Before doing anything else, ask the user which of these they are.** If
they are neither, stop: do not draft, send or post outreach about Hebrish for them. Point them
instead to: suggesting a person or group the project should contact (an issue titled
"Outreach: <who>" on https://github.com/Hebrish-ASR/Hebrish-App, or
https://hebrish.app/contact?topic=involved), and the signup on https://hebrish.app/ if they want updates.

With that settled, drafting is the job: the user posts the draft themselves, from their own
account, in groups they belong to. Never post, join, message or submit a form on the user's
behalf, and never post through a messaging bridge or bot. Emailing a community as the project
goes through `outreach-email`. The maintainer keeps a private list of communities and what was
sent to each, so groups are not contacted twice: check it first.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *community-fyi*, for the maintainer setup.

## Before drafting

1. Ask which group, what kind it is (WhatsApp, Slack, Facebook, Discord, meetup, mailing
   list, newsletter, organisation) and whether the user is a member.
2. Read the group's own rules on self-promotion if they are public, and follow them. Some groups
   only allow tools in a weekly thread or need admin approval.
3. Several Anglo olim organisations have already been contacted directly by Daniel. A post by a
   member in a group they belong to is still welcome; a second cold email to an organisation is
   not. If unsure, the user can ask Daniel at https://hebrish.app/contact?topic=involved.

## Message

3 to 5 short lines in plain text for a chat post; up to 8 sentences for an email or form.
Plain, no hype, no emojis, no superlatives. Facts from https://hebrish.app/llms.txt only, never
from memory; numbers exactly as published.

- **Who made it:** Daniel Rosehill built it as a personal project. (A
  representative writes in their own voice: "I'm helping Daniel Rosehill share Hebrish...")
- **The problem, in the group's words:** English sentences with Hebrew words in them. Give 2 or
  3 example terms that suit the group and exist in the lexicon
  (`https://hebrish.app/data/lexicon.json`, field `t`; browse by domain at
  https://hebrish.app/lexicon). Romanized, never Hebrew script.
- **What it is:** free, on-device dictation that writes those words correctly. Apps for Android,
  Ubuntu and Windows at https://hebrish.app/download; try it in the browser at
  https://hebrish.app/demo.
- **AI and developer groups only:** open models on Hugging Face (`Hebrish/Sabich` is the one the
  apps recommend, `Hebrish/Jachnun` the pure code-switching model), all models at
  https://hebrish.app/models, and agent install skills at
  https://github.com/Hebrish-ASR/Hebrish-Agent-Skills.
- **One ask:** try it, pass it on, or send words it gets wrong (https://hebrish.app/words).

The models are trained on one speaker's voice: mention it only if accuracy comes up, and then
as an invitation to contribute recordings (https://hebrish.app/contact?topic=samples).

## Channel

| Kind of group | What to produce |
| --- | --- |
| Chat group (WhatsApp, Slack, Discord, Facebook) | A 3 to 5 line post to paste. The user posts it. |
| Contact form or "submit a tip" (newsletters, blogs, podcasts) | The text to paste plus the form URL. The user submits it. |
| Meetup with demo slots | A short request to the organisers offering a live demo; the user sends it. Demos by Daniel: suggest the organisers contact him at https://hebrish.app/contact. |
| Organisation with an email address | `outreach-email`. One email per organisation. |

"Draft" or "prepare": show the drafts in chat and stop. "Send" or "post" still means: show the
final text, and the user posts it.

## After posting

Optional but useful: the user tells Daniel where it went (https://hebrish.app/contact?topic=involved,
one line: group, date, link if public), so the same group is not approached twice.
