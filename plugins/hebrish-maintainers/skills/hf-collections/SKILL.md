---
name: hf-collections
description: Keep every Hebrish model, dataset and Space in the right Hugging Face collections (Jachnun, Sabich, sentence datasets, audio datasets, demos and Spaces, and the all-repos front door) from a collections config file. Finds repos that are in no collection, adds new ones, fixes item notes and collection descriptions. Use when asked to update, organise or check the Hebrish collections on Hugging Face, or after anything new is published under huggingface.co/Hebrish.
---

# Hebrish Hugging Face collections

## Access

- **Maintainer access:** people with the write or admin role in the
  [Hebrish organisation on Hugging Face](https://huggingface.co/Hebrish), using a Hugging Face token
  with that access in `HF_TOKEN` (or saved by `hf auth login`). Only they can create collections or
  change items. Collections are public pages, so show the plan and get the maintainer's go-ahead before
  `--apply` unless they asked for exactly this change.
- **Anyone else:** the dry run below works without a token (it reads public data only). Report what it
  finds as an issue on [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues),
  titled for example `Hugging Face: Hebrish/Sabich-MLX missing from collection Sabich`, with the JSON
  lines that show it.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *hf-collections*, for the maintainer setup.

Hebrish is Daniel Rosehill's one-person, not-for-profit project (<https://hebrish.app>). Written
2026-10-22; the script was run (dry run only) against the live org that day.

## The collections

As of 2026-10-22 the org has these collections (slugs in `references/collections.example.json`):

| Collection | What belongs in it |
| --- | --- |
| Jachnun | `Hebrish/Jachnun` and its builds (`-sherpa-onnx-int8`, `-ONNX`, `-GGUF`, `-MLX`), its demo Spaces |
| Sabich | `Hebrish/Sabich`, its builds, the training blend dataset; arguably the Sabich variants on other bases (`Sabich-Qwen3-ASR-1.7B`, `Sabich-Canary-Qwen-2.5B`, `Sabich-Parakeet-110M`, `Sabich-asr4all-S/-M`), since the site's `models.json` names this collection for them |
| Hebrish: sentence datasets | text-only datasets (the `*-Sentence-Bank` sentence banks) |
| Hebrish: audio datasets | datasets with recordings, one per phenomenon, plus the benchmark |
| Hebrish: demos and Spaces | every Hebrish Space except the org card (`Hebrish/README`) |
| Hebrish: English-Hebrew code-switching | the front door: every Hebrish model, dataset and Space, including repos still on Daniel's personal account |
| Accessory Models, Base Fine Tunes | exist on the Hub; not covered by the example config |
| Parakeet V2 Fine-Tune - Training Data | generated from the private training registries: leave it to the maintainer (see the notes) |

Rules that hold whatever the config says:

- **Boxty is not a Hebrish model.** `Hebrish/Boxty-sherpa-onnx-int8` and
  `Hebrish/Parakeet-V2-Blend-No-Hebrew` never go in any collection (top-level `exclude`).
- Model names follow the site: Jachnun, Sabich (the recommended model), Shakshuka, Meorav (TTS,
  repo `Hebrish/TTS-V1` as of 2026-10-22); checkpoints PoC-1 … PoC-5, Shakshuka PoC-N always prefixed.
- Collection descriptions are at most **150 characters**; the Hub answers 400 to longer ones (seen
  2026-10-20). The script checks before writing.

## The config

A JSON file, one entry per collection. Schema and the `auto` rules: `references/collections-schema.md`.
Start from `references/collections.example.json` (public repo ids only), or from the maintainer's own
config. The script takes the path, so the config can live anywhere.

## Steps

Script: `${CLAUDE_PLUGIN_ROOT}/skills/hf-collections/scripts/sync_collections.py`. If
`CLAUDE_PLUGIN_ROOT` is unset, clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/hf-collections/scripts/sync_collections.py` inside it.

```bash
S="${CLAUDE_PLUGIN_ROOT}/skills/hf-collections"
R="uv run --no-project --with huggingface_hub python3 $S/scripts/sync_collections.py"
$R --config $S/references/collections.example.json --site https://hebrish.app/data/models.json
```

(Without `uv`: `pip install huggingface_hub` and run `python3` directly.) Takes about 20 seconds.

1. **Dry run and read the plan.** Per collection: `create` (no such collection yet), `description`
   (differs), `add` (on the Hub, not in the collection), `note` (item note differs), `missing` (listed
   in the config but not visible on the Hub: typo, deleted, or private), `unmanaged` (in the collection,
   not in the config; kept unless `--prune`). Whole org: `orphans` (org repos in no collection at all),
   `hub_collections_not_in_config`, and with `--site`, `site_check` (repos that hebrish.app's
   `models.json` lists for a model but that are missing from the collection it names for that model).
   On 2026-10-22 the dry run found 16 orphans, among them every Sabich variant, Shakshuka and its
   builds, `Hebrish/TTS-V1` (Meorav) and `Hebrish/Hebrish-TTS-Voice-Recordings`.
2. **Edit the config**, not the Hub by hand: add the repo to every collection it belongs to (a new
   Jachnun build goes in Jachnun and the front door; a new recorded dataset is picked up by the
   `audio-datasets` rule if it holds audio files). An empty dataset is skipped by every rule until it has
   data files.
3. **Show the plan** (only `add`, `note`, `description`, `create`, and `unmanaged` if pruning) and get
   the go-ahead. Then:
   ```bash
   $R --config <config> --apply                 # or --only jachnun,sabich
   ```
   A new collection gets its slug from the printed `url`; write it into the config as `slug`, or a
   later title change creates a second collection.
4. **Verify the thing, not the exit code:** run the dry run again (`add` and `note` empty) and open
   each changed collection page, or read `HfApi().get_collection(slug).items`.
5. A new **model** also belongs on hebrish.app's `/models` (`data/models.json` in the website repo,
   which is private): without access, open an issue `Website: add <repo> to /models`.

Without maintainer access, stop after step 1 and file the issue described under Access.

## API facts (huggingface_hub 2.2.0)

| Call | Note | Verified |
| --- | --- | --- |
| `list_collections(owner=org)` | titles and slugs, but **only the first 4 items** of each: never diff against it | 2026-10-20 |
| `get_collection(slug).items` | full item list; each item has `item_id`, `item_type`, `item_object_id`, `note` | 2026-10-22 |
| `repo_info(id, repo_type=...).id` | the **current** id of a renamed or moved repo; the old id still answers through a redirect, so resolve before comparing or the same repo is added twice | 2026-10-20 |
| `add_collection_item(slug, item_id, item_type, note=..., exists_ok=True)` | | 2026-10-20 |
| `update_collection_item(slug, item_object_id, note=...)` | needs `item_object_id`, not the repo id | 2026-10-20 |
| `delete_collection_item(slug, item_object_id)` | used only with `--prune` | inferred from the docs |
| `update_collection_metadata(slug, description=...)` | 150-character limit | 2026-10-20 |
| `list_models(author=org, sort="lastModified")` | without `sort` the listing has omitted new repos | 2026-10-19 |
