---
name: submit-data
description: Check and submit a Hebrish training-data contribution (new vocabulary terms and/or read-aloud English-Hebrew code-switching sentences) as one JSON file, validated against the public sentence bank and lexicon, then filed as an issue on Hebrish-ASR/Hebrish-App. Use when the user says "submit my sentences", "send these words to Hebrish", "contribute this pack", "is my contribution file valid", or at the end of vocab-gaps, news-vocab, write-sentences or generate-synthetic.
---

# Submit a data contribution

## Access

- **Anyone**: checking the file and opening an issue need only Python 3, network access and a
  GitHub account (the `gh` CLI or the GitHub website).
- **Maintainer access** (merging the contribution into the sentence bank): the project's private
  training repository. Contributors do not need it; the maintainer does that step (below). If you
  have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
  `docs/maintainer-agent-notes.md`, section *submit-data*, for the maintainer setup.

## Scripts

`${CLAUDE_PLUGIN_ROOT}/skills/submit-data/scripts/`: `check_contribution.py` (validator) and
`assemble.py` (start a file, add reviewed rows). If `CLAUDE_PLUGIN_ROOT` is unset, clone
https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/submit-data/scripts/` inside it. Both are stdlib-only Python 3.

The validator downloads three public files once a day into `~/.cache/hebrish-data/` (override with
`HEBRISH_DATA_CACHE`): the sentence bank export
([sentences.jsonl](https://github.com/Hebrish-ASR/English-Hebrew-Codeswitching-Parakeet-Finetune/tree/main/sentences)),
the [hebrish.app lexicon](https://hebrish.app/data/lexicon.json) and
[terms.csv](https://github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier/blob/main/data/terms.csv).

## Steps

1. **The file.** One JSON file in the format in `references/contribution-format.md`. To start one:
   `python3 assemble.py new <name> --contributor <github-handle> > <name>.json`; to add reviewed rows:
   `python3 assemble.py add <name>.json rows.reviewed.jsonl`. Fill `note` (what, why, how written,
   how reviewed, sources with dates) and confirm with the user that the text is original and may be
   published under CC-BY-4.0.
2. **Check it.** `python3 check_contribution.py <name>.json`. Fix every `ERROR` and run it again
   until it exits 0. Read every `warn`: a skeleton match ("same consonant skeleton as covered
   [...]") is a likely respelling of a term the dataset already has (on 2026-10-18 doch, kenas and
   bricha turned out to be do'ach, knas and breicha), and should usually be dropped.
3. **Read a sample yourself.** Pick 10 kept rows at random and read them aloud in your head. If any
   sounds unnatural or uses a term wrongly, the review was too lenient: re-review the file.
4. **Open the issue** on [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues),
   the project's public repository for contributions. Show the user the title and body before
   creating it; creating an issue is public and is done in their name.
   - Title: `Data contribution: <name> (<N> terms, <M> sentences)`.
   - Body: one paragraph from `note`, the checker's final summary line, and the file.
   - The file: in the browser, drag `<name>.json` into the issue box (GitHub accepts `.json`
     attachments; zip it if it is refused). With the CLI, an issue body holds at most 65,536
     characters: a file under about 60 KB can go in the body as a fenced `json` block
     (`gh issue create --repo Hebrish-ASR/Hebrish-App --title "..." --body-file body.md`); for a larger
     one, `gh gist create --public <name>.json` and put the gist link in the body.
5. **Report** the issue URL to the user.

## Third-party text

Only original sentences are accepted. Do not submit sentences copied or lightly edited from news
articles, books, websites, subtitles or other datasets, even if the source is public. If you think a
public text corpus would help, open a separate issue proposing it with: the corpus id or URL, the
licence and a link to the licence text itself (not a tag on a listing; a listing can say MIT for a
dataset whose card says research-only), the date you checked it, the slice you mean, and why. Bank
text ends up in a public dataset, so only licences that allow redistribution qualify (CC0, CC-BY,
MIT, ODC-BY; not NC, ND or "research only"). Adding third-party text is opt-in and Daniel's
decision: past experience (2026-10-21) was that an unscreened public corpus added bland sentences
and one explicit one, and it was removed.

## What happens next (maintainer)

Daniel (the maintainer) re-runs the checks against the full private term lists, which can catch a
few duplicates the public files cannot (the public export can lag the live bank by a few days).
Accepted terms become a vocabulary pack, accepted sentences are merged into the sentence bank
without changing any existing prompt, and the public sentence export is refreshed. The sentences
then appear in the capture app and become training data as Daniel records them. The contributor is
credited in the pack note. He may edit or drop rows, and will say why on the issue.
