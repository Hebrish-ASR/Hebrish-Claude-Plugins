---
name: generate-synthetic
description: Generate a large synthetic set of read-aloud English-Hebrew code-switching sentences for Hebrish with Claude Haiku 5.5 on the Anthropic Message Batches API, using the contributor's own Anthropic API key — labels made in code, raw output cached, a separate review, then the checker and submission. Use when the user says "generate a synthetic set for Hebrish", "use Haiku batch", "generate hundreds of sentences", or when write-sentences would need too many subagents.
---

# Generate a synthetic sentence set

## Access

- **Anyone with their own Anthropic API key** (or an `ant auth login` profile): the batch calls are
  billed to that account. Without a key, use `write-sentences`, which does the same job with Claude
  subagents in this session and costs nothing extra.
- **Maintainer access**: none needed to generate. If you have access to the private
  Hebrish-ASR/Hebrish-Mgmt repository, read `docs/maintainer-agent-notes.md`, section
  *generate-synthetic*, for the maintainer setup.

**Why Haiku batch.** The maintainer's verdict on 2026-10-21: batch jobs on Haiku are "very
affordable and quick, and that's the best one we've used so far". Haiku 5.5 is US$0.10 / $0.50 per
million input / output tokens (Anthropic price table as of 2026-10-06), and the Batches API bills
half that. Measured: a 222-sentence run cost US$0.008 (2026-10-21); a 10-request set cost well under
a cent. So anything under about 1,000 requests costs cents. Check the current price list, state the
estimate to the user, and get a yes before submitting: it is their money.

## Script

`${CLAUDE_PLUGIN_ROOT}/skills/generate-synthetic/scripts/generate_batch.py` (if
`CLAUDE_PLUGIN_ROOT` is unset, clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/generate-synthetic/scripts/generate_batch.py`). Needs the `anthropic`
Python package: run it with `uv run --with anthropic python ...` (or `pip install anthropic`).

## Rules

- **Labels are made in code, not by the model.** The script tells the model which term each
  sentence must use, keeps a sentence only if that term is in it with its exact casing (a lowercase
  term may be capitalised at the start), and writes `target_terms`, `hebrew_terms`, `categories`
  and `source` itself. Rows with digits, Hebrew script or no final punctuation are dropped and
  logged. Ask for about 1.5 times what you want to keep.
- **Structured outputs** (a JSON schema on every request), so every result parses. Results come
  back in any order and are keyed by request id.
- **Cache the raw output** (`<out>.haiku.json`, written automatically), so `--cached` rebuilds the
  rows with a new filter or seed without another API call. The batch id is printed first; if the
  run dies while polling, `--resume <batch id>`.
- The house rules (`${CLAUDE_PLUGIN_ROOT}/skills/write-sentences/references/writing-rules.md`) are
  in the script's system prompt. If you change the rules for a run, edit `SYSTEM` in the script.
- `source` is `generated:claude-haiku-5-5-batch` on every row. Haiku 5.5 thinks by default; the
  script sends effort `low` (thinking tokens bill as output).

## Steps

1. A contribution file with `terms` and `companions` (from `vocab-gaps`, `news-vocab` or the user's
   list); check it first with `check_contribution.py` so no covered term is paid for.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/bank-coverage/scripts/bank_stats.py --avoid avoid.json`
3. Estimate: `uv run --with anthropic python generate_batch.py <slug>.json --out <slug>-haiku.jsonl --avoid avoid.json --per-term 3`
   prints requests, sentences and an estimated cost, and stops. Tell the user; on their yes, re-run
   with `--yes`. Batches usually finish in minutes.
4. **Review** with a separate Claude subagent, never Haiku judging itself: brief it with the writing
   rules and reviewer checklist and the terms' meanings; it writes `<slug>-haiku.reviewed.jsonl` with
   `review: {keep, reason, model}` on every row. Recurring problems are better fixed in the script's
   `build()` filter and rebuilt with `--cached` than row by row.
5. `assemble.py add <slug>.json <slug>-haiku.reviewed.jsonl`, then `check_contribution.py <slug>.json`
   until no ERROR, then `submit-data`.

## Report

Batch id, requests, tokens and cost as printed, rows kept by the script and by the reviewer, the
main rejection reasons, and the issue URL.
