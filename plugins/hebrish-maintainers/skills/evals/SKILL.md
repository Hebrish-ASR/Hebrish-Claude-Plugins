---
name: evals
description: Run and judge evaluations of Hebrish speech-recognition checkpoints (Jachnun, Sabich and its variants, Shakshuka) or any other model on English speech with Hebrew words - the public English-Hebrew code-switching benchmark (anyone, own compute, gated test set) and the project's held-out split on a pinned dataset revision (maintainer). Covers metric definitions (term recall, unseen-term recall, WER, English control, forgetting checks), the selection and publish gates, suggested verdicts, recording them, and cost discipline (the cheapest set that answers the question). Use when asked to benchmark, evaluate or score a model or checkpoint, compare checkpoints, decide whether one is publishable, or submit a result to the leaderboard.
---

# Hebrish evaluations

## Access

- **Anyone:** the public benchmark's code is
  [Hebrish-ASR/English-Hebrew-Codeswitching-ASR-Benchmark](https://github.com/Hebrish-ASR/English-Hebrew-Codeswitching-ASR-Benchmark)
  (MIT). Its test set, the Hugging Face dataset
  [`Hebrish/English-Hebrew-Codeswitching-ASR-Benchmark`](https://huggingface.co/datasets/Hebrish/English-Hebrew-Codeswitching-ASR-Benchmark),
  is **gated with manual approval** (checked 2026-10-22): request access on that page, wait for
  approval, then log in with a Hugging Face token (`hf auth login`). With that you can score any model
  on your own compute (a local GPU, or your own Modal account) and submit the result by pull request.
  Comparing result files and suggesting a verdict (`verdict.py`) needs no access at all: every
  published result, transcripts included, is in the repo's `results/`.
- **Maintainer access:** the project's held-out split evaluations run from the private training
  repository on the project's Modal account, on dataset revisions pinned there; recording a verdict
  for a Hebrish checkpoint and publishing a leaderboard round need write access to that repository
  and to the benchmark repo and its leaderboard Space. If you have access to the private
  Hebrish-ASR/Hebrish-Mgmt repository, read `docs/maintainer-agent-notes.md`, section *evals*, for
  the maintainer setup.
- **Fallback for everyone else:** open a pull request on the benchmark repo with your result file, or
  an issue on [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues) with the
  scores and the files, if you think a Hebrish checkpoint's verdict or a published number is wrong.

Script: `${CLAUDE_PLUGIN_ROOT}/skills/evals/scripts/verdict.py`. If `CLAUDE_PLUGIN_ROOT` is unset,
clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/evals/scripts/verdict.py` inside it.

## Two evaluations, never mixed

| | Public benchmark | Held-out split |
| --- | --- | --- |
| Test set | Frozen: test set v1, dataset revision `3cb0b2b3b3e46c951962ababeb7c56fc4248cb94` (pinned in `ehcs_bench/data.py`; a new test set is a new `VERSION` + `REVISION` together) | The training dataset's test split at one pinned revision; it grows with every new revision |
| Size | 145 clips. Headline `clean` subset: 84 clips (11.8 min), 172 Hebrew term occurrences, 139 distinct terms, 117 occurrences unseen. `english_control`: 24 clips (3.3 min) | e.g. round R7 (revision `f956dbb184c2`, 2026-10-20): 422 code-switched clips, 324 held-out term occurrences (134 terms), 293 seen-term occurrences, 84 own-English clips, 200 LibriSpeech test-clean, 17 long-form files |
| Who runs it | Anyone with dataset access | Maintainer |
| Comparable | Across all models on the leaderboard | Only within one revision |
| Published at | Leaderboard Space and `results/` in the benchmark repo; `leaderboard` in hebrish.app `data/results.json` | Model cards; `compare` (R6), `compare_r7` (R7) in hebrish.app `data/results.json` |

Never put a held-out number next to a public-benchmark number as if they measured the same thing, and
never rank two models scored on different held-out revisions.

## Metrics (definitions)

Both evaluations share the normaliser and term matcher (`ehcs_bench/score.py`):

| Metric | Definition | Better |
| --- | --- | --- |
| **Term recall** | Hebrew term occurrences whose canonical romanized spelling appears in the transcript as a whole word, case-insensitive, hyphen and space interchangeable, ÷ occurrences. Never substring (*chool* is not in *school*). Hebrew script is never a hit | Higher |
| **Unseen-term recall** (held-out recall) | The same over terms absent from the training split. The generalisation number | Higher |
| Seen-term recall | Over terms that also appear in training (memorisation plus spelling) | Higher |
| Lenient recall | Also accepts the lexicon's variant spellings (*tsaharon* for *tzaharon*); fairer to stock models | Higher |
| Exact-case recall | Canonical hit whose casing matches the reference (*Bituach Leumi*) | Higher |
| **WER** (normalised) | Lowercase, hyphens to spaces, punctuation removed except in-word apostrophes, `jiwer` 3.1.0. `wer_raw` keeps case and punctuation | Lower |
| **English control WER** | Public benchmark: WER on the same speaker's English-only clips. A fine-tune that damages English shows here | Lower |
| Own English WER, LibriSpeech WER | Held-out split: same-speaker English, and 200 LibriSpeech-PC test-clean utterances (other speakers). The forgetting check | Lower |
| Long-form WER | Held-out split: test clips joined into ~3-minute files (0.4 s gaps) | Lower |
| Numbers recall | Held-out split: number tokens (8 on R6/R7, too few to mean much yet); a tie-breaker only | Higher |

Held-out recall is scored against the bank's held-out term list, not every term on a test row: a row
goes to test if any of its terms is held out, so its other terms may be in training.

**Oracle check:** scoring the references as transcripts must give 0% WER and 100% on every term metric.
Run it after any change to the scorer or the test set (it caught 4 non-canonical references and 7 case
mismatches on 2026-10-15).

**Known issue (open since 2026-10-15):** 22 of the 139 clean-subset terms (26 of 172 occurrences) are
English tech words or product names (*JSON*, *grep*, *Proxmox*, ...). Ranks are unaffected; absolute
term recall is 2–6 points high. Test set v1.1 will relabel them and rescore every model from its
stored transcripts.

**Noise:** one speaker, read speech, small sets. On the public benchmark 2–3 points of term recall is
about 4–5 hits: noise. On the held-out split, gaps under ~1 WER point or a handful of term hits are
noise (2026-10-19: a 2.1-point held-out gain, about 6 of 293 hits, was judged noise-level).

## 1. Decide what to score (cost first)

Hebrish is a personal passion project: spend the fewest GPU minutes that answer the question.

- Score the checkpoint(s) asked about, **stock** (the candidate's own base model) and the **current
  release** on the same revision, so there is one comparable point. Not every published version.
- The public benchmark is frozen: a new model needs only its own run. Never re-run existing
  leaderboard rows.
- No streaming evals unless the question is streaming accuracy (each is a full extra run).
- Measured costs: Modal L40S about US$1.95/h (2026-10-18). One public-benchmark run of a 0.6B
  Parakeet model: about 35 s of inference on an L40S (2026-10-20). One held-out eval: about 2.5 min
  wall, US$0.10–0.20. The R6 round (six parallel jobs, 2026-10-19) was under 15 GPU-minutes,
  about US$0.50 at most. Say the estimate before launching a paid job and record the actual minutes.
- While the first proof-of-concept models on new bases are being trained (rule set 2026-10-21), the
  project runs no cross-model or post-hoc comparison evals; only an eval that picks a checkpoint or
  shows a run works, or one Daniel asks for. This binds the project's own compute, not yours.

## 2. Run the public benchmark (anyone)

```bash
git clone https://github.com/Hebrish-ASR/English-Hebrew-Codeswitching-ASR-Benchmark && cd English-Hebrew-Codeswitching-ASR-Benchmark
uv venv && source .venv/bin/activate
uv pip install -e '.[nemo]'        # Parakeet, Canary, Nemotron (NeMo 2.7.3); '.[whisper]' for Whisper
hf auth login                      # an account whose access request was approved
ehcs-bench run --model nemo:Hebrish/Sabich@<full sha> --name "<display name>" \
  --fine-tuned --base-model nvidia/parakeet-tdt-0.6b-v2 --out my-result.json
```

- A model spec is `<adapter>:<hf repo>[@revision]`; pin the full commit sha so the result is
  reproducible. The `nemo` adapter loads the one `.nemo` file in the repo. Hebrish main model repos
  (`Hebrish/Sabich`, `Hebrish/Jachnun`, `Hebrish/Shakshuka`) are gated too: request access on each
  model page first. Adapters: `nemo`, `whisper` (`ehcs_bench/adapters.py`; add a family there).
- `--limit N` is a smoke test only, never a valid result.
- **GPU on Modal (your own account):** `modal run modal_app.py --model ... --name ... --args "--fine-tuned --base-model ..." --out my-result.json`.
  It uses the NeMo build pinned in `modal_app.py` (unpinned installs broke the TDT kernel twice) and
  reads `HF_TOKEN` from the Modal secret named in that file: create a secret with that name in your
  workspace, or edit the name. No volume; weights download each run.
- **Models that don't run here** (APIs, phone apps, GGUF or sherpa-onnx runtimes): transcribe the 145
  WAVs yourself, write one `{"id": ..., "hyp": ...}` per line, then
  `ehcs-bench score --preds preds.jsonl --name "My model" --model-id org/model`. Missing ids score as
  empty (a warning says how many).
- Declare any overlap between the model's training data and the test set with `--contamination "..."`.
  Training on the source datasets' *train* split is fine; that is what unseen recall is for.
- `ehcs-bench rescore results/*.json` recomputes every metric from the stored transcripts and prints
  `OK` per file (it refuses files scored on another revision).

Output: one JSON with `benchmark` (repo, version, revision), `model` (id, pinned revision, name,
adapter, base, settings, notes, contamination), `metrics.subsets` (`clean`, `all_code_switch`,
`english_control`), and `utterances` (every reference and transcript). Headline:
`metrics.subsets.clean.terms.all.recall`, `.terms.unseen.recall`, `.wer`, and
`metrics.subsets.english_control.wer`.

**Submitting:** a pull request adding the file to `results/`. `ehcs-bench rescore results/<file>.json`
must print `OK`. The maintainer then refreshes the README table, figures and leaderboard Space and
freezes a dated round (`documentation` skill, step 4).

Quantized builds: if the model will ship as int8 (sherpa-onnx, ONNX) or GGUF, score that build too
(via `score`); quantization can take back part of a fine-tune's gain.

## 3. Held-out split (maintainer)

Done in the private training repository; the maintainer notes give the commands. In outline:
1. Use the revision the last data preparation pinned; never re-prepare just to benchmark.
2. Evaluate stock (base model, same harness), the current release re-scored on this revision, and
   the candidate(s), in parallel. Pull each eval's summary JSON.
3. A Hebrish checkpoint going onto the public leaderboard also needs a **contamination check**: none
   of the 145 benchmark clip ids or normalised texts may be in the run's training or validation
   manifests. Write the check into the result's `notes`.

## 4. Apply the gates

In order (Hebrish training docs, "Evaluation", rules in force since 2026-10-18):

1. **Forgetting gate:** fails if own-English or LibriSpeech WER (normalised) is worse than stock on
   this revision. Public benchmark: English control WER stands in.
2. **Code-switching WER and held-out-term recall** decide. In a sweep a setting wins only if it wins
   on both seeds. Gaps at noise level are called noise.
3. **Numbers recall** breaks ties.
4. **Publish gate:** beats stock and the current release on this revision, and passes 1.

Verdicts: `publishable`, `fails forgetting`, `no better than <release>`, `noise-level difference`.

```bash
V=${CLAUDE_PLUGIN_ROOT}/skills/evals/scripts/verdict.py
python3 $V --stock results/parakeet-tdt-0-6b-v2.json \
  --release results/parakeet-v2-en-he-sabich-v1-0.json --candidate my-result.json
python3 $V --stock <stock>-summary.json --release <release>-summary.json --candidate <run>-summary.json --json
```

It reads public benchmark result files or held-out eval summaries (format detected per file),
**refuses to compare across revisions**, prints a table (recall with hits/occurrences) and a
suggested verdict per candidate with the forgetting margins and the deltas against the release.
Noise defaults: 1.0 WER point, 8 term hits (`--wer-noise`, `--hits-noise`). A candidate counts as
better when at least one of code-switching WER, held-out hits or seen hits improves beyond noise and
none gets worse beyond noise. The suggestion is not the verdict: the maintainer records it and can
override (below).

Checked against past rounds on 2026-10-22 (read-only): R6 (revision `550bfcaa0f84`) gives Jachnun
v1.0 `publishable` (CS WER 5.07 vs PoC-3 6.00; seen terms +26 hits), matching the recorded
verdict. The Nemotron run comes out `fails forgetting`, but only against Parakeet stock: its own base
was not re-scored on that revision, so the recorded verdict gave no forgetting call. Pass the
candidate's own base as `--stock`. R7 (`f956dbb184c2`) gives the kitchen-sink run `fails forgetting` (LibriSpeech
1.30 vs stock 1.23, +0.07 points, about 3 words); Daniel accepted that as noise and published it as
Sabich v1.0 on 2026-10-20. That is the kind of call the script leaves to a person.

## 5. Record

- **Public benchmark:** the result file in `results/` (via pull request for outside contributors).
  Never edit a committed round in `archive/`.
- **Hebrish checkpoints (maintainer):** the verdict, revision and summary go into the training repo's
  checkpoint registry; a checkpoint is marked discarded only on Daniel's say-so. Then the
  `documentation` skill puts the numbers on hebrish.app, the white paper and the model cards. A
  `publishable` verdict is the input to a release; none publishable means say so and publish nothing.
- Record dates absolutely (YYYY-MM-DD), the revision, the GPU minutes, and which numbers you measured
  versus copied.

## Report

A table (stock, current release, each candidate) on one revision, the suggested and recorded verdicts,
cost (GPU minutes, estimate vs actual), contamination status, and what is left for a maintainer.
