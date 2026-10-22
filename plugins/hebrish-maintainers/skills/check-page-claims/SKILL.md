---
name: check-page-claims
description: Check the numbers, model names and links on a hebrish.app page against their sources (the site's public data files, Hugging Face model cards, the public benchmark repository, the canonical term list) and report each mismatch. Use when asked to verify, fact-check or audit a Hebrish web page, or before proposing a website change that quotes a result.
---

# Check a hebrish.app page against its sources

## Access

- **Anyone:** all checks below use public sources. Report what you find as an issue on
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues) titled
  `Website: claims on /<page>` (or hand it to the `website-change` skill).
- **Maintainer access:** some figures (held-out split results, training minutes per version) come from
  the private training repository. Without it, mark those claims "source not public" rather than wrong.
  If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
  `docs/maintainer-agent-notes.md`, section *check-page-claims*, for the maintainer setup.

This skill reads and reports; it changes nothing.

## 1. Get the page and its data

```bash
mkdir -p claims && cd claims
curl -s https://hebrish.app/<page> -o page.html
for f in results models variants lexicon stats; do curl -s https://hebrish.app/data/$f.json -o $f.json; done
```

Pull every number, percentage, model name and outbound link from `page.html` into a list (one row per
claim, with the sentence it sits in).

## 2. Match each claim to its source

| Claim | Public source |
| --- | --- |
| WER, term recall, per-100 figures, leaderboard | `data/results.json`: `leaderboard` (public benchmark), `compare` and `compare_r7` (same-revision held-out comparisons), `checkpoints`. Its `_doc` key explains the blocks. Upstream: `results/*.json` in <https://github.com/Hebrish-ASR/English-Hebrew-Codeswitching-ASR-Benchmark> |
| Model facts (base, params, formats, DOIs, HF repos) | `data/models.json`, then the model card on <https://huggingface.co/Hebrish> (`Hebrish/Jachnun`, `Hebrish/Sabich`, `Hebrish/Shakshuka` …) |
| Which model to use, speed/accuracy positions | `data/variants.json` (positions are estimates and must be labelled so) |
| Lexicon and dataset counts | `data/lexicon.json`, `data/stats.json` (generated daily from the dataset; small drift against a dated statement is expected, so check the date in the sentence) |
| Hebrew word spellings | `term` column of `data/terms.csv` in <https://github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier> |
| App versions and sizes | not written on pages; they are filled at runtime from the release manifest. A hard-coded version is itself a finding |

For each claim decide: **matches**, **mismatch** (give page value, source value, source location),
**rounded** (the page rounds a source value: a finding, e.g. 5.42 must be written 5.4%, not 5%),
**no public source**, or **unsourced** (nothing backs it).

## 3. Check the rules that aren't numbers

- Model names: bare "v1"–"v5" for the PoC checkpoints; Jachnun called "main"; Shakshuka PoC-N without
  its prefix; any mention of Boxty; "FUTO" in an asr4all heading.
- Ranking across test-set revisions (e.g. Sabich-Qwen3 vs Sabich); targets shown as results.
- Hebrew script used as model output; a non-canonical romanization.
- "We"/"our" outside the terms of use and dated changelog entries.
- Single-speaker wording in the hero, strip, home cards or chart footers.
- Versioned download URLs instead of `/get/<platform>`.
- On a home-page fact: does `/he` say the same number?

## 4. Check the links

```bash
grep -o 'href="https\?://[^"]*"' page.html | cut -d'"' -f2 | sort -u | while read u; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' -L "$u") $u"; done
```

A 401 or 403 on a `huggingface.co/Hebrish/...` file URL usually means a gated repo, not a dead link;
note it and check whether the page needed a public URL there.

## 5. Report

A table: claim (quoted), verdict, source (URL plus key or line), suggested fix. Say which checks you
could not do and why. Dates: write the date you checked (absolute, YYYY-MM-DD).
