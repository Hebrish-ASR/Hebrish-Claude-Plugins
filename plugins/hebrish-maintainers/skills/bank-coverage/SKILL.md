---
name: bank-coverage
description: Review the public Hebrish sentence bank and lexicon against the project's objectives — code-switching share, sentence length and short utterances, templated openings, over-used names and Hebrew words, and which covered terms are thin (few sentences, no recordings) — and say what contribution would help most. Use when the user asks "what does the Hebrish dataset need", "review the sentence bank", "is there enough variety", "which words are thin", or before vocab-gaps or write-sentences.
---

# Review the sentence bank

Read-only: this skill reports; it changes nothing.

## Access

- **Anyone**: everything here reads public data.
- **Maintainer access** adds the recorded-hours balance by category, which needs the gated audio
  dataset and the private training repository. If you have access to the private
  Hebrish-ASR/Hebrish-Mgmt repository, read `docs/maintainer-agent-notes.md`, section
  *bank-coverage*, for the maintainer setup.

## Script

`${CLAUDE_PLUGIN_ROOT}/skills/bank-coverage/scripts/bank_stats.py` (stdlib Python 3). If
`CLAUDE_PLUGIN_ROOT` is unset, clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/bank-coverage/scripts/bank_stats.py`. It downloads, once a day into
`~/.cache/hebrish-data/` (override with `HEBRISH_DATA_CACHE`):

| File | What | From |
|---|---|---|
| `sentences.jsonl` | Every prompt in the sentence bank: `id`, `text`, `categories`, `target_terms`, `split`, `source` | [tracker repo `sentences/`](https://github.com/Hebrish-ASR/English-Hebrew-Codeswitching-Parakeet-Finetune/tree/main/sentences) |
| `lexicon.json` | Every covered Hebrew term and Israeli name: `t` term, `d` domain, `m` meaning, `n` recorded takes | [hebrish.app/data/lexicon.json](https://hebrish.app/data/lexicon.json) (also browsable at [/lexicon](https://hebrish.app/lexicon)) |
| `terms.csv` | Canonical romanization with spelling `variants` and `category` | [Hebrew-Latin-Token-Classifier](https://github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier/blob/main/data/terms.csv) |

## Steps

1. `python3 bank_stats.py > coverage.json` (add `--refresh` to re-download). Also
   `--avoid avoid.json` (the 60 Hebrew words most used in code-switching prompts) and
   `--covered covered.txt` (every covered form, for duplicate checks) when sentence writing follows.
2. Read the JSON and answer with numbers:
   - **Balance.** `bank.code_switch_share` against the objective (code-switching first; the training
     mix targets about 70% code-switching to 30% English). The bank should keep plenty of
     code-switching prompts unread.
   - **Variety.** `openings_2_words_code_switch` (templated openings and their share),
     `greeting_opener_share_cs`, `cs_vocative_names_top10`, `length_buckets` and
     `code_switch_short_le8_words` (short utterances were a known gap). Quote 5 to 10 real bank
     sentences that show the repetition, not just counts.
   - **Term depth.** `lexicon.per_domain`: terms with fewer than 3 bank sentences and with 0 takes,
     per domain. `thin_terms.rows` lists the thinnest terms: candidates for top-up sentences
     (`"topup": true` in a contribution).
3. Measured on 2026-10-22 for comparison (export built 2026-10-19): 14,785 prompts, 54.5%
   code-switching, 698 code-switching prompts of 8 words or fewer, 3,642 lexicon terms of which
   1,839 have no recorded take and 758 have fewer than 3 bank sentences. Openings "can you", "don't
   forget", "hi dana" and "remind me" led the code-switching prompts; Dana alone opened 149
   greetings.

## Output

A short report: a verdict per objective, the three biggest problems, and which skill helps most:
`vocab-gaps` (missing or thin domains), `news-vocab` (current-events names), `write-sentences`
(variety, short utterances, top-ups of thin terms), `generate-synthetic` (a large set with your own
API key). Nothing is submitted from this skill.
