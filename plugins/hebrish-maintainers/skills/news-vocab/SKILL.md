---
name: news-vocab
description: Mine recent Israeli English-language news (Times of Israel, Jerusalem Post) for names and terms an American-English speech model would mangle — politicians and candidates, officers, rabbis, towns, parties, units, Hebrew loan words — that the Hebrish dataset does not cover yet, and turn them into a sourced, fact-checked contribution file of terms. Use when the user says "mine the news for Hebrish", "new names from Times of Israel", "news vocab", or wants current-events vocabulary added.
---

# News vocabulary

Output: a contribution file of **terms** (names and words), each with the article it came from.
Only names, roles and words are taken from the news, never sentences: the sentences are written
fresh afterwards (`write-sentences` or `generate-synthetic`).

## Access

- **Anyone**: public news sites and the public lexicon.
- **Maintainer access**: none needed for this skill. If you have access to the private
  Hebrish-ASR/Hebrish-Mgmt repository, read `docs/maintainer-agent-notes.md`, section *news-vocab*,
  for the maintainer setup.

Precedent: the maintainer's first run (2026-10-19) read 20 stories (8 Times of Israel, 12
Jerusalem Post) and produced 67 terms (40 people, 14 places, 10 institutions, 3 terms).

Names from the news go in as **plain English** rows (`companions: []`), counted on the English side
of the training mix. Hebrew loan words used in coverage (hasbara, mandatim) are code-switching
terms with companions.

## 1. Fetch 15 to 20 stories from the last week

Routes verified on 2026-10-19, in the order to try them:

| Target | Route that worked | What failed |
|---|---|---|
| ToI story list | `curl -sL -A "Mozilla/5.0" https://www.timesofisrael.com/feed/` (about 15 items; `<link>`, `<pubDate>`) | `https://www.timesofisrael.com/israel-news/feed/` returns an empty channel (HTTP 200, 1 KB) |
| ToI articles | the `WebFetch` tool | `curl` gets HTTP 403 (Cloudflare) on every article, even with a browser user agent |
| JPost story list | `curl` on `https://www.jpost.com/rss/rssfeedsfrontpage.aspx` and `.../rssfeedsisraelnews.aspx` | |
| JPost articles | `curl` with a browser user agent (HTTP 200, about 300 KB); the text is the JSON-LD `"articleBody"`, the date `"datePublished"` | |

If both fail, try a real browser (Claude in Chrome) before giving up.

- Save downloads in their own folder and extract with a script kept outside it (regex
  `"articleBody"\s*:\s*"(.*?)(?<!\\)"`, JSON-decode, strip tags). Reading the article body beats
  asking a summariser for names.
- ToI pages are 170 to 250 KB and `WebFetch` reads about the first 100,000 characters. Ask it to
  "list every proper name verbatim with role", then a second call quoting each name's sentence and
  role: the first answer can misattribute roles (2026-10-19: a summary gave a candidate the wrong
  party; the verbatim pass corrected it).
- News stories, not podcasts, liveblogs or opinion. Spread across politics, security, society,
  economy. Election explainers listing each slate's candidates are the richest single source.

## 2. Extract candidates

Keep, with the role **as stated in the article**: ministers, MKs and candidates (with slate
position), IDF and police officers, council heads, rabbis, journalists, academics, activists;
Israeli towns, kibbutzim, neighbourhoods, bases, crossings, and West Bank and Gaza place names
Israelis say often; parties, factions, NGOs, IDF units, yeshivot; Hebrew words the English coverage
uses as-is.

Skip: names English speech models already know (Netanyahu, Herzog, Lapid level) and English-named
organisations; non-Israelis unless the name is said the Hebrew way; anything with a digit (Lahav 433,
Shayetet 13); slurs; one-off fringe figures unless they recur; photo credits, bylines, sidebars;
private individuals (victims, suspects who are not public figures).

## 3. Check coverage

Scripts as in the `vocab-gaps` skill (`bank_stats.py`, `check_contribution.py`; under
`${CLAUDE_PLUGIN_ROOT}/skills/`, or clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins).

1. `python3 bank_stats.py --candidates candidates.txt`. Read every `skeleton_matches` hit: on
   2026-10-19 Sami Abou Shahadeh ~ Sami Abu Shehadeh and Merav Ben Ari ~ Merav Ben-Ari were real
   duplicates, Amir Avivi ~ maariv a false positive.
2. Per word for multi-word names: a covered surname alone does not cover the full name, but a
   covered full name under another title does.
3. Expect most of the political class to be covered already; the yield is mid-slate candidates,
   officials, rabbis and place names.

## 4. Write the file

Terms with `group` `news_people`, `news_places`, `news_institutions` or `news_terms`; `meaning`
factual and neutral, the role as of the article, nothing the article does not state unless you
checked it; `he` per the contribution format. `companions`: `[]` for people and institutions,
Hebrew categories for places and terms only where they fit. `instruction`: "Mention the person
neutrally and factually; no political opinion." `note`: the check date, every source article
(outlet, URL, date), what was left out and why.

Roles change fast around elections: if sentences are written more than a few days after the check
date, re-verify each person's `meaning` first. Run `check_contribution.py` until it has no ERROR.

## Report

Stories read and from where, terms per group, items you were unsure of. Then `write-sentences` or
`generate-synthetic`, and `submit-data`.
