---
name: anglo-usage
description: Mine real English-language writing by anglos in Israel and the Orthodox English-speaking world (Times of Israel blogs, Jerusalem Post Judaism, Yeshiva World News, Chabad.org parsha pages, frum and community sites) for how Hebrew words are actually used inside English — which words, which spelling (Ashkenazi or Israeli), in what kind of sentence — and turn the gaps into a contribution file of new terms and top-ups whose sentences are written fresh, never copied. Use when the user says "find real sources for sentences", "the religious words need more variety", "more parshas", "Ashkenazi pronunciation", "mine the anglo forums / blogs / frum news", or when bank-coverage shows a term family that is templated or thin.
---

# Anglo usage

Output: a contribution file (`terms`, plus `usage` hints for the writers) ready for
`write-sentences`. No paid API calls.

`news-vocab` covers **names** from the news. This skill is about **register and usage**. It looks
at how an anglo writes "we're having the aufruf Shabbos Parshas Noach" or "I davened at the
vasikin minyan", so that the written sentences sound like that and don't all follow one template.

**Never copy source text.** Blog posts, articles and forum posts are copyrighted by their authors,
and the bank feeds public datasets. What you take from a source is a term, its spelling, its
meaning and a one-line **paraphrased** usage pattern ("parsha name used as a date: 'the week of
Vayeira'"). Writers never see the source text. Take nothing about private individuals (names,
places, events from a forum or classified post).

## Access

- **Anyone**: public sites and the public sentence bank and lexicon.
- **Maintainer access**: none extra. The recording app's per-term take counts and recall
  (`v2_term_recall` in Voice-Training-Recorder `app/public/data/bank.json`) sharpen step 1 if you
  have the repo.

Paths: `${CLAUDE_PLUGIN_ROOT}/skills/...`; if `CLAUDE_PLUGIN_ROOT` is unset, clone
https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use the same paths under
`plugins/hebrish-maintainers/`.

## 1. Pick the gaps

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/bank-coverage/scripts/bank_stats.py --covered covered.txt > coverage.json`.

Aim at three things:

- **Thin terms** (`thin_terms.rows`, fewer than 3 sentences). These become `"topup": true` entries.
- **Templated families**: a family where every term has the same small count from one generated
  batch. Found on 2026-10-23 in the recorder bank (14,785 prompts): every parsha had exactly 3
  sentences, all `generated:claude-subagent`, built on "studying X", "the week of X",
  "presentation on X". The Ashkenazi forms (Bereishis, Toldos, Shemos, Yisro, Parshas) had 3 each,
  and Vayeitzei, kedushah, shlita, bochur, heimish, sheitel, tichel, aufruf and bentch had none.
- **Skip what is learned already**: a term with many takes and high recall in `v2_term_recall`
  (hits / tries of 0.9 or more over at least 3 tries). Recall is thin as of 2026-10-23: 609 terms,
  most with a single try. So treat "no recall data" as unknown, not as learned.

## 2. Choose sources by register

`references/sources.json` lists each source with its feed, the route that worked, its status on the
date it was checked, and its `registers`: `news`, `opinion`, `frum_news`, `torah`, `ashkenazi`,
`community`. Match the register to the gap:

| Gap | Sources |
|---|---|
| Parsha names, Torah vocabulary | `chabad-parsha` (Ashkenazi), `jpost-judaism`, `aish`, `inn` (Israeli forms) |
| Ashkenazi / yeshivish forms | `chabad-parsha`, `yeshiva-world`, `vinnews`, `matzav`, `collive`, `anash` |
| Everyday anglo life, aliyah, bureaucracy | `toi-blogs`, `toi-israel-inside`, `janglo` |
| Current Hebrew loan words in coverage | the `news` sources (or run `news-vocab`) |

Try the feed with `curl -sL -A "Mozilla/5.0" <feed>`. Fetch articles the way the source's
`articles` field says. If that route fails, use the `WebFetch` tool, then Claude in Chrome.
**Update `sources.json` with what you find**: a new status, a working article route, or a failure
moved into `failed`. Record it with the date. The next run depends on it.

The Chabad feed has only the current week's parsha. For the whole cycle, walk
`https://www.chabad.org/parshah/`, one parsha page each.

## 3. Extract usage, not text

Fan out with one subagent per source family, all launched in one message. Each one gets: the gap
list for its register, `covered.txt`, the "Romanization" section of
`${CLAUDE_PLUGIN_ROOT}/skills/write-sentences/references/writing-rules.md`, and the no-copy rule
above. It reads 10 to 20 items and returns JSON rows:

```json
{"term": "Vayeitzei", "form": "ashkenazi", "israeli_form": "Vayetze", "meaning": "weekly Torah portion (Genesis 28:10-32:3)",
 "usage": ["parsha name as a date: the Shabbos of X", "bar mitzvah boy's parsha"],
 "source": {"id": "chabad-parsha", "url": "https://...", "date": "2026-10-23"}}
```

- Keep Ashkenazi and Israeli forms as **separate terms**. The writing rules keep both on
  purpose, so never merge one into the other.
- `usage` is a short paraphrased pattern, at most 12 words. Never quote the source.
- Drop English dictionary words (they can't be tagged; this hits parshas like Bo, Lech, Emor and
  Tzav, so write those only as "Parshas Bo" / "Lech Lecha" with the full name as the term). Also
  drop one-off trivia and anything an anglo says in English anyway.

## 4. Coverage check and file

Run `python3 bank_stats.py --candidates candidates.txt` and read every `skeleton_matches` hit, as
in `vocab-gaps` step 3. Then:
`python3 ${CLAUDE_PLUGIN_ROOT}/skills/submit-data/scripts/assemble.py new <slug> --contributor <handle> > <slug>.json`.
Add the `terms` (with `"topup": true` for covered ones) and their `companions`. In `note`, put the
check date, every source as id + URL + date (no quoted text), and what was dropped and why.

Pass each term's `usage` lines to `write-sentences` as the writer's register hint: 3 sentences per
term, 5 for a templated family. Each sentence uses a different pattern. Run
`check_contribution.py` until it has no ERROR, then `submit-data`.

## Report

The sources read and their status changes, terms per register (new and top-up), what you dropped,
and the file path.
