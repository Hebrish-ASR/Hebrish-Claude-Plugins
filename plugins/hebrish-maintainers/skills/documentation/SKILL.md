---
name: documentation
description: Keep Hebrish's written record current after a model release or a new benchmark round - the white paper (English PDF and its Hebrew mirror), benchmark numbers on hebrish.app (data/results.json, /benchmarks, the home chart, model pages), a short results write-up for the changelog, blog, Hugging Face model cards and the public benchmark repo, the hand-off to the newsletter and community skills, and charts drawn from previously run benchmarks in the site's chart style. Claims match their source exactly; targets are not results; no ranking across test-set revisions. Use when asked to update the white paper, put new results on the site, write up or share benchmark results, or make a chart of Hebrish results.
---

# Hebrish documentation: white paper, results on the site, write-ups, charts

## Access

- **Anyone:** every number this skill uses is public: `https://hebrish.app/data/results.json`, the
  result files in [Hebrish-ASR/English-Hebrew-Codeswitching-ASR-Benchmark](https://github.com/Hebrish-ASR/English-Hebrew-Codeswitching-ASR-Benchmark)
  (`results/*.json`, `archive/*.json`) and the model cards on <https://huggingface.co/Hebrish>. You can
  draw charts (step 5) and draft any write-up (step 4). The website and the white paper sources are in
  a private repository, so a proposed edit goes to an issue on
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues) titled
  `Website: <summary>` (or `White paper: <summary>`), with the current text, the proposed text and the
  source of every number. Attach charts to the issue. Daniel applies it.
- **Maintainer access:** write access to the website's private repository (site pages, `data/`,
  `img/charts/`, `whitepaper/`), to the Hugging Face `Hebrish` org (model cards) and to the benchmark
  repo. Sending a newsletter or community message needs the project's own accounts (see the skills
  named in step 4). If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
  `docs/maintainer-agent-notes.md`, section *documentation*, for the maintainer setup.

Hebrish is Daniel Rosehill's one-person project: write "Daniel", never "we"/"our".

Script: `${CLAUDE_PLUGIN_ROOT}/skills/documentation/scripts/results_report.py`. If `CLAUDE_PLUGIN_ROOT`
is unset, clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/documentation/scripts/results_report.py` inside it.

## Rules every step follows

These are the website's own rules; a write-up, card or chart that breaks one is wrong even if the
number is right.

| Rule | What it means in practice |
| --- | --- |
| Claims match the source | Copy the value from its source file. Don't invent, average or estimate. Where the source has two decimals the site writes one (5.30 → 5.3%, 5.42 → 5.4%); never coarser (5.42 → 5% is a finding). |
| Targets are not results | `results.json` `checkpoints` entries with `"status": "target"` (Jachnun v1.1, v1.2) are goals. Never chart them or quote them as scores. |
| Unbenchmarked stays unbenchmarked | PoC-4 and PoC-5 were published without a benchmark. Write "not benchmarked", never a number. Jachnun v1.0 and Sabich v1.0 have results (see below). |
| One revision per comparison | Scores compare only within one test-set revision. Never rank models scored on different revisions: e.g. Sabich-Qwen3-ASR-1.7B (revision `cf84f7e4`) against Sabich (round R7, `f956dbb1`), or R6 (`550bfcaa`) numbers against R7 numbers. |
| Names | Jachnun (the Parakeet fine-tune; current release Jachnun v1.0), Sabich (recommended in the apps since 2026-10-21; Sabich v1.0; variants `Sabich-<Base>-<Size>`), Shakshuka (streaming; Shakshuka PoC-1, PoC-2, v1.0), Meorav (speech synthesis; no benchmark, make no quality claims). Checkpoints PoC-1 … PoC-5, never a bare "v1"–"v5". Jachnun is never "the main model". Boxty is not a Hebrish model: leave it out. |
| Single speaker | The models are trained and tested on one speaker's voice. Say it once, plainly, where it matters technically (method, known limits, model-card Limitations, FAQ). Not in titles, hero text, chart footers or every paragraph. Where more voices come up, invite contributed recordings. |
| Hebrew | Hebrew words in their romanized form (makolet, arnona). Hebrew script only as a gloss, never as model output. |
| Mirrors | A number on the home page or in the white paper also changes on `/he` and in the Hebrew white paper. |

## Where the numbers live (public)

| Evaluation | Public source | What it is |
| --- | --- | --- |
| Public benchmark (leaderboard) | benchmark repo `results/*.json` (one file per model, every transcript included), `archive/<date>.json` (frozen rounds); `results.json` `leaderboard` | Frozen test set v1 (HF dataset `Hebrish/English-Hebrew-Codeswitching-ASR-Benchmark`, pinned revision in `ehcs_bench/data.py`), clean subset: 84 clips, 172 term occurrences, 139 distinct terms. Metrics: term recall, unseen-term recall, WER, English control WER |
| Held-out split, one revision | `results.json` `compare` (revision `550bfcaa0f84`, round R6, 2026-10-19) and `compare_r7` (revision `f956dbb184c2`, round R7, 2026-10-20) | The training dataset's own test split at one revision; grows each revision. Metrics: code-switching WER, held-out (unseen) and seen term recall, own English, LibriSpeech, long-form, tech (R7) |
| Version history | `results.json` `checkpoints` (revision `b47310621f79`) | Stock and PoC-1 to PoC-3 only; plus targets (not results) |
| Model facts | `https://hebrish.app/data/models.json`, model cards on <https://huggingface.co/Hebrish> | Base, size, formats, DOIs, versions |

`results.json` `_doc` keys (top level and per block) say where each block was copied from; read them.

Measured headline facts (for orientation only; always re-read the source):
- Public benchmark, round 4 (2026-10-20): Sabich v1.0 73.8% term recall, 68.4% unseen, 3.3% WER,
  2.0% English control; Jachnun v1.0 73.3 / 70.1 / 3.3 / 2.2; stock Parakeet TDT 0.6B v2 32.6 / 32.5 / 9.5 / 2.7.
  The Sabich–Jachnun gap is within noise (the benchmark's own limits: 2–3 points ≈ 4–5 hits).
- Round R7 (`compare_r7`): code-switching WER Sabich v1.0 5.30, Jachnun v1.0 5.42, stock 11.82.

## 1. After a release or benchmark round: find what changed

1. Read the new result: the benchmark repo's new `results/<model>.json` and its round in `archive/`,
   and/or the round's held-out numbers as published on the model card or in `results.json`.
2. Print the current published tables:
   ```bash
   python3 results_report.py                      # all blocks, Markdown, from the live site
   python3 results_report.py --block compare_r7   # one block
   ```
   It drops targets, prints "no score on this revision" for unscored checkpoints, and prints each
   block's revision so you don't mix them.
3. List every claim the new result touches (next step), then check each existing claim on the
   affected pages with the `check-page-claims` skill.

## 2. Benchmark numbers on hebrish.app

The site is static and hand-written; one result appears in many places. Places a new result goes
(website repo paths; maintainer edits them, everyone else lists them in the issue):

| Place | What |
| --- | --- |
| `data/results.json` | The source the charts read. Add the model to `leaderboard.models` (public benchmark: `name`, `short`, `ours`, `recall`, `unseen`, `wer`, `en`) or a same-revision block (`compare`, `compare_r7`, or a new `compare_rN` with its own `_doc`, `revision`, `metrics`). A target that is now measured becomes `"status": "measured"` with `scores`. Update `_doc` with the date and source file |
| `benchmarks.html` | Charts (`charts.js`: `data-viz="leaderboard"`, `data-block="compare"`, `scatter`, `gains`, `per100`) and their table views; the "Figures to reuse" thumbnails |
| Home page chart and cards | `index.html` per-100 cards (`data-viz="per100"`, `data-block="compare_r7" data-ours="sabich"`) and the same on `he.html`. The home side by side (`showdown.js`) uses verbatim benchmark transcripts: never edit or invent them |
| Model pages | `model.html` (the Jachnun card), `models/<slug>.html`, `/models` lede if a recommendation changes |
| Text copies of numbers | `explain.js` worked examples, `llms.txt`, `webmcp.js` (`get_model_results` summary), `.well-known/agent-skills/hebrish-model-facts/SKILL.md` (recompute its digest), `/faq`, `/docs` facts |
| `changelog.html` | A dated entry (step 4) |
| Static figures | `img/charts/*.{png,svg}` from `scripts/make_figures.py` (reads `results.json` only, never draws targets) |

Then grep the site for stale wording, e.g. `grep -rn "not benchmarked" --include=*.html .`, and fix
each line that is no longer true. Don't touch the nav, strip or footer by hand (`scripts/layout.py`).
After the edit, run `check-page-claims` on each changed page. Maintainer: commit and push (the host
deploys on push; no build step), then load the live page and read the number.

## 3. The white paper (English and Hebrew)

Current edition: **"Hebrish model release 1: Jachnun v1.0 and Sabich v1.0"** (2026-10-21, 13 pages),
<https://hebrish.app/whitepaper/hebrish-release-1-whitepaper.pdf> and the Hebrew translation
<https://hebrish.app/whitepaper/hebrish-release-1-whitepaper-he.pdf>. Each PDF is rendered from an
HTML file beside it in the website repo (`whitepaper/*.html`, `noindex`, not in the sitemap). The
HTML's head comment lists the sources of every number and the render command.

- **Correction or a new number for the same release** (e.g. a re-scored model): edit the HTML in both
  languages, re-render both PDFs. Figures stay English in the Hebrew edition; model output stays
  romanized there too.
- **A new release** (a new Jachnun or Sabich version, Shakshuka v1.0): a new edition, named for the
  release (`hebrish-release-2-whitepaper{,-he}.{html,pdf}`), not a rewrite under the old name. The
  old edition's URLs then redirect (`vercel.json`), and every link to the white paper (site pages,
  `llms.txt`, model cards) moves to the new one.
- Render with headless Chrome (from the website repo root):
  ```bash
  google-chrome --headless=new --no-pdf-header-footer \
    --print-to-pdf=whitepaper/<name>.pdf whitepaper/<name>.html
  pdffonts whitepaper/<name>.pdf   # must list Inter and Fraunces; the Hebrew PDF also Assistant and Frank Ruhl Libre
  ```
  A render before the web fonts load falls back to other fonts and reflows the pages; check the
  page count and `pdffonts` every time.
- Section by section, the paper follows the sources in "Where the numbers live". Shakshuka is
  described as work in progress until it has a benchmarked release.
- Without access: draft the changed paragraphs (English, and Hebrew if you can; otherwise say the
  Hebrew mirror needs translating) in the issue.

## 4. Share the results

Draft each piece from the same numbers; don't let wording drift between them.

1. **Changelog entry** (`changelog.html`): date, what was scored, on which test set/revision, the
   headline numbers against stock and against the current release on that revision, and the verdict.
   Two to four sentences. Dated entries are history: never rewrite an old one.
2. **Blog post** (optional, for a release): problem, what changed, results table, one chart, limits,
   how to try it. Link the white paper and `/benchmarks`.
3. **Hugging Face model cards**: the Results section of the model's card (and the build repos only
   point to it). Use the `model-cards` skill for the audit and the card rules. Images on cards use
   `https://hebrish.app/img/charts/...` URLs: the main model repos are gated, so their own `resolve/`
   image URLs return 401 to logged-out visitors.
4. **Public benchmark repo**: a new public-benchmark result is a file in `results/`, then
   `python3 scripts/results_table.py` (README table), `uv run --with matplotlib python scripts/make_figures.py`
   (its `docs/figures/`), and a dated round with `scripts/snapshot_run.py --title "Round N: ..." --notes "..."`.
   Outside contributors open a pull request with the result file (see the `evals` skill).
   Never edit a committed round.
5. **Newsletter, communities, people**: hand off with the written summary and links. `newsletter`
   (subscribers), `community-fyi` (Israeli AI and Anglo tech communities), `outreach-email` (one
   person or organisation). Those skills hold the access rules and templates; this skill only
   supplies the text.

## 5. Charts from previously run benchmarks

Draw from published results only; never re-run a model to make a chart.

```bash
S=${CLAUDE_PLUGIN_ROOT}/skills/documentation/scripts/results_report.py
uv run --with matplotlib python3 $S --block leaderboard --metric recall --chart term-recall.png
uv run --with matplotlib python3 $S --block compare_r7 --metric cs_wer --chart r7-cs-wer.svg \
  --title "Code-switching WER, round R7"
python3 $S --block leaderboard --json > leaderboard.json   # rows for another tool
```

Metric ids: `leaderboard`: `recall`, `unseen`, `wer`, `en`; `compare`/`compare_r7`: `cs_wer`,
`unseen`, `seen`, `own_en`, `libri`, `long` (and `tech`, `hefree` in R7); `checkpoints`: same as
`compare`. For per-clip or per-term charts, use the benchmark repo's `results/*.json`
(`utterances` hold every reference and transcript) and its `scripts/make_figures.py`.

Site chart conventions (matched by the script):
- Horizontal bars sorted best first, value labelled at the bar end, exact source value.
- Colours (brand tokens, light theme): Jachnun v1.0 `#0f6b5c`, Sabich v1.0 gold `#c8901c`, other
  Hebrish checkpoints `#7fb3a7`, everything else `#b8b2a5`; background `#fbf8f2`, ink `#1d2422`,
  muted `#5b6662`, grid `#e2dccf`. Fonts Inter (text) and Fraunces SemiBold (titles) where installed.
- A title, a subtitle naming the test set or revision and the scoring date, a source line naming the
  file. No single-speaker caveat in the footer (it is stated under the benchmark's known limits).
- One revision per chart. Targets never drawn. PNG at 1600 px wide plus SVG.
- The site's own figures are `img/charts/*` from the website repo's `scripts/make_figures.py`
  (fonts in the maintainer setup); `lineage.svg` is hand-drawn.

## Report

Say what changed where (file and line, or the issue URL), the source of each number, what is left for
someone with access (the Hebrew mirror, a re-render, a deploy), and the date checked (YYYY-MM-DD).
