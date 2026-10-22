---
name: write-sentences
description: Write new read-aloud English-Hebrew code-switching sentences for the Hebrish sentence bank — for a contribution's new terms, top-ups of thin terms, or variety (new registers, openings, short utterances) — with Claude subagents as writers and a different subagent as reviewer, in the exact row format the bank uses, then check and submit them. No API key needed. Use when the user says "write sentences for Hebrish", "generate training sentences", "sentences for these Hebrew words", "we need more variety", or after vocab-gaps or news-vocab produced terms.
---

# Write sentences

Defaults to Claude subagents in this session, so there is no API bill. For a large set (hundreds
of terms), `generate-synthetic` does the writing on the Anthropic Batches API with your own key.

## Access

- **Anyone**: writing, reviewing and checking need only this session and public data.
- **Maintainer access**: merging into the bank (after submission). If you have access to the
  private Hebrish-ASR/Hebrish-Mgmt repository, read `docs/maintainer-agent-notes.md`, section
  *write-sentences*, for the maintainer setup.

Paths: `${CLAUDE_PLUGIN_ROOT}/skills/...`; if `CLAUDE_PLUGIN_ROOT` is unset, clone
https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use the same paths under
`plugins/hebrish-maintainers/`.

## 1. Decide what to write

- **For new terms**: a contribution file with `terms` (from `vocab-gaps`, `news-vocab` or the
  user's own list). 3 sentences per term by default, 5 for terms the user cares most about.
- **Top-ups**: covered terms with fewer than 3 bank sentences (`bank_stats.py`,
  `thin_terms.rows`), as terms with `"topup": true`.
- **Variety batch**: no new terms; a slug like `variety-<theme>` (short utterances, a new register,
  new sentence shapes) for existing covered terms.

Then refresh the inputs:
`python3 ${CLAUDE_PLUGIN_ROOT}/skills/bank-coverage/scripts/bank_stats.py --avoid avoid.json --covered covered.txt`.

## 2. Writers

One writer subagent per about 40 terms (or per register for a variety batch), all launched in one
message. Each brief contains:

- the whole of `references/writing-rules.md` (pasted, not linked: subagents start cold);
- its terms with `term`, `meaning`, `proper_noun`, and whether the group is plain English
  (`companions: []`) or code-switching;
- the over-used words from `avoid.json`, and for code-switching groups a few suggested companion
  words from terms.csv categories in the group's `companions` (vary them per sentence; the
  maintainer found on 2026-10-19 that repetition came from companion words, not target terms);
- the output: a JSONL file `<slug>-w<N>.jsonl`, one row per sentence, in the row format of
  `${CLAUDE_PLUGIN_ROOT}/skills/submit-data/references/contribution-format.md` ("Sentences")
  without `review`, `source` set to `generated:<the writer's model id>`.

## 3. Reviewers

A **different** subagent reviews each writer file (a model judging its own output rubber-stamps
it; use a different model where you can, e.g. Sonnet writes, Opus reviews). Brief: the writing
rules and their reviewer checklist, the terms with meanings, and the file. It writes
`<slug>-w<N>.reviewed.jsonl`: every row plus `review: {keep, reason, model}`, fixing rows in place
where a small edit saves them (old text in `review.original_text`).

For news and politics terms, a reviewer whose knowledge predates the events may reject real people
and parties as "fictional" (2026-10-16: 27 correct rows were rejected that way). Read every
rejection of a current-events row before accepting it.

## 4. Assemble and check

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/submit-data/scripts/assemble.py add <slug>.json <slug>-w*.reviewed.jsonl
python3 ${CLAUDE_PLUGIN_ROOT}/skills/submit-data/scripts/check_contribution.py <slug>.json
```

Fix every ERROR by editing or rejecting rows (set `keep: false` with a reason), then re-check.
Past runs for scale: the maintainer's 187-term pack of 2026-10-18 (five writer subagents, a
different reviewer per file) kept 558 of 561 sentences; packs written before the no-digits rule was
in the brief lost up to a quarter of their rows to it.

## 5. Submit

Continue with `submit-data`. Report: terms covered, sentences kept and rejected (with the main
rejection reasons), and the issue URL.
