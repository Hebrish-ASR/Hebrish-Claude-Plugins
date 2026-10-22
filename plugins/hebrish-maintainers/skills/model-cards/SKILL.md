---
name: model-cards
description: Audit and fix the Hugging Face model and dataset cards of the Hebrish org (Jachnun, Sabich and its variants, Shakshuka, Meorav, the datasets) so they are current and consistent - current version, Sabich as the recommended model, Jachnun/Sabich/Shakshuka/Meorav and PoC-N naming, numbers matching the published benchmarks, links, licence, gate form, the single-speaker limitation stated once, romanized Hebrew. Read-only audit by default; with org write access, edits a card with a commit message. Use when asked to check, review, update or fix a Hebrish model card or dataset card, or after a release.
---

# Hebrish model and dataset cards

## Access

- **Anyone:** the audit (step 1) and the manual review (step 2) read only public data: the cards
  on <https://huggingface.co/Hebrish> are readable even on gated repos, and the comparison sources are
  public. Report findings as an issue on
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues), titled for example
  `Hugging Face: card for Hebrish/Sabich-ONNX has no gate form`, with the proposed wording. On an
  **ungated** repo you can also open a pull request on the Hub (`create_pr=True` below, any Hugging Face
  account); on a gated repo the Community tab needs accepted access first.
- **Maintainer access:** people with the write or admin role in the Hebrish organisation on Hugging
  Face, with a token that has it in `HF_TOKEN` (or `hf auth login`). Only they edit cards directly
  (step 3), and only after showing the diff and getting the go-ahead.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *model-cards*, for the maintainer setup (where each card's
source lives, so a fix is not overwritten by the next release).

Hebrish is Daniel Rosehill's one-person project (<https://hebrish.app>). Written
2026-10-22; the audit script was run against every Hebrish model and dataset that day (54 repos).

## The rules a card is held to

| Topic | Rule |
| --- | --- |
| Names | **Jachnun** is the code-switching Parakeet fine-tune (current: Jachnun v1.0; retrains v1.1, v1.2 …). **Sabich** is code-switching plus tech, and the **recommended model** in the apps since 2026-10-21: never call Jachnun "main", "default" or "recommended". **Shakshuka** is the Nemotron streaming line (Shakshuka PoC-1, PoC-2, Shakshuka v1.0), always prefixed so it never reads as Jachnun's PoC-N. **Meorav** is the text-to-speech line (repo `Hebrish/TTS-V1`, Meorav PoC-1 as of 2026-10-22). The first five Jachnun checkpoints are **PoC-1 … PoC-5**: never a bare "v1"-"v5" (history may say "PoC-3, published as v3"). Sabich variants on other bases: `Sabich-Qwen3-ASR-1.7B`, `Sabich-Canary-Qwen-2.5B`, `Sabich-Parakeet-110M`, `Sabich-asr4all-S/-M`; no "FUTO" in their headings or marketing text (the base id and licence name are fine). |
| Boxty | Not a Hebrish model. A card may name it as a sibling only if the maintainer wants that; ask. |
| Current version | The card's title and "latest version" lines name the version in `current` of hebrish.app's `data/models.json`. |
| Numbers | Every result is copied from a published source, never typed from memory, never invented: `https://hebrish.app/data/results.json` (`leaderboard`, `compare`, `compare_r7`), the result files in <https://github.com/Hebrish-ASR/English-Hebrew-Codeswitching-ASR-Benchmark> (`results/*.json`), or the [public leaderboard](https://huggingface.co/spaces/danielrosehill/English-Hebrew-Codeswitching-ASR-Leaderboard). Do not round a figure differently from its source. PoC-4 and PoC-5 are unbenchmarked; Jachnun v1.0 and Sabich v1.0 have round-7 results. Targets are goals, never shown as results. Do not rank Sabich-Qwen3 against Sabich: their results are on different test-set revisions. |
| Licence | `license:` in the front matter matches the repo's licence on hebrish.app/models and the [terms](https://hebrish.app/terms): PoC-1 … PoC-5 and v1.0 CC-BY-4.0; Parakeet fine-tunes from v1.1 CC-BY-NC-4.0; other bases keep their base licence (Shakshuka: NVIDIA Open Model License, card `other`; asr4all variants: the base's weights licence, `other`; Qwen3 variants: Apache-2.0). Plus the Hebrish terms of use. |
| Access | Every gated card has the "Access and terms of use" paragraph right after the Website line, an `extra_gated_prompt`, and `extra_gated_fields` (Name, Organisation, Intended use, the terms checkbox). The access-request address on cards is **access@hebrish.app** (standardised 2026-10-22; replace any older address such as access-requests@hebrish.app). The audit flags any other hebrish.app access address, and reports the terms page's address as `terms_contact` so an out-of-date terms page shows up too. |
| Single speaker | The models are trained on one speaker's voice. Say it **once**, plainly, under **Limitations**; not in the title, the opening lines or every section. Where more voices come up, invite people to contribute recordings. |
| Hebrew | Hebrew words in their romanized form (makolet, arnona; canonical spellings: `term` column of `data/terms.csv` in <https://github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier>). Hebrew script only as a gloss next to the romanized word, never as model output. |
| Voice | One person, no organisation: "Daniel", not "we/our/us" (quoted example sentences are fine). |
| Links | A link to <https://hebrish.app>; no dead links (401/403 on a gated `huggingface.co/Hebrish/...` file is the gate, not a dead link). |

A main model card has these parts, in order: front matter (`license`, `language`, `base_model`,
`base_model_relation: finetune` (without it the Hub tags the repo "quantized" because of the GGUF
files), `pipeline_tag`, `library_name`, `tags`, `datasets`, gate fields); title with name and version;
summary; Website line; Access and terms paragraph; Results; Version history; what this version changed;
Training data; Training; Usage; formats; Limitations; Licence. Build repos (`-GGUF`, `-ONNX`, `-MLX`,
`-sherpa-onnx-int8`) have a short card that points to the main one and carries the same gate.

## Steps

Script: `${CLAUDE_PLUGIN_ROOT}/skills/model-cards/scripts/audit_cards.py`. If `CLAUDE_PLUGIN_ROOT` is
unset, clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/model-cards/scripts/audit_cards.py` inside it.

### 1. Audit (read-only)

```bash
A="uv run --no-project --with huggingface_hub python3 ${CLAUDE_PLUGIN_ROOT}/skills/model-cards/scripts/audit_cards.py"
$A > /tmp/hebrish-cards.json                                  # every Hebrish model and dataset, ~1 min
$A --repos Hebrish/Sabich,dataset:Hebrish/Yiddish-Sentences   # some repos
$A --repos Hebrish/Jachnun --links --save-dir /tmp/cards      # check links, keep the README.md files
```

Output: per card `findings` (rule, detail, line numbers, examples) and `numbers` (every line with a
percentage, for step 2). It reads hebrish.app's `data/models.json` (line name, current version, licence,
repos per model) and `/terms` (`terms_contact`; `terms_contact_is_standard` is false while the terms
page names anything other than access@hebrish.app). For a whole-org health check that also covers
collections, gating and pending requests, use the `hf-audit` skill, which runs this audit inside it. A finding means "look here", not "wrong": a bare `v2` is often
the base model ("Parakeet TDT 0.6B v2"), Hebrew script may be a legitimate gloss, and format repos
legitimately skip Limitations if they point to the main card.

On 2026-10-22 it reported, among others: four gated datasets with no gate form (requests arrive with
nothing to review), gated build repos without `extra_gated_fields` (`Sabich-sherpa-onnx-int8`,
`Sabich-Parakeet-110M-GGUF`/`-sherpa-onnx-int8`, `Shakshuka-GGUF`/`-sherpa-onnx-int8`,
`Whisper-Hebrish-Small-ACFT`), `Hebrish/TTS-V1` (Meorav) not naming "Meorav PoC-1" and missing a
Limitations section and a hebrish.app link, and the Jachnun card opening with "Jachnun is the Hebrish
model".

### 2. Review numbers and wording by hand

For each card with findings, open it and read the flagged lines in context. For every number in
`numbers`, find its source (table above) and mark: matches, mismatch (card value, source value, source
location), rounded differently, or no public source. Write a short report: repo, finding, proposed text.
Without maintainer access, this report is the deliverable: file it as described under Access.

### 3. Edit a card (maintainer access, after a go-ahead on the diff)

Edit a local copy, show the diff, then upload with a commit message that says what and why:

```python
from huggingface_hub import HfApi, hf_hub_download, ModelCard, DatasetCard
import shutil
api, repo, typ = HfApi(), "Hebrish/Sabich", "model"           # typ "dataset" for a dataset card
info = api.repo_info(repo, repo_type=typ)
shutil.copy(hf_hub_download(repo, "README.md", repo_type=typ, revision=info.sha), "README.md")
# ... edit README.md, then check the front matter still parses:
(ModelCard if typ == "model" else DatasetCard).load("README.md").data.to_dict()
api.upload_file(path_or_fileobj="README.md", path_in_repo="README.md", repo_id=repo, repo_type=typ,
                commit_message="Card: Sabich is the recommended model; single-speaker note moved to Limitations",
                parent_commit=info.sha)    # fails instead of overwriting if someone committed meanwhile
                # create_pr=True opens a Hub pull request instead of committing
```

Work in a scratch directory outside any repository. One commit per card; batch only identical fixes
(for example the gate form on every build repo). Gate settings themselves (manual or automatic) are
repo settings, not card text: change them only when the maintainer asks
(`api.update_repo_settings(repo, gated="manual", repo_type=typ)`).

### 4. Verify

Re-run the audit for the edited repos (the finding is gone), open the card page and read it rendered
(front matter errors show as a banner on the page), and check `api.repo_info(repo).card_data` shows the
new values.

If a card is generated by the training pipeline, the next release regenerates it: the fix must also go
into that source (maintainer notes). Without access, say so in the issue.
