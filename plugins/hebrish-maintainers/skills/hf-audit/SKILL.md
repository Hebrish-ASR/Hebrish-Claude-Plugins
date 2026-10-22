---
name: hf-audit
description: One-shot, read-only health audit of the Hebrish organisation on Hugging Face - repos in no collection, dead collection items, hebrish.app's model list against the org and its collections, every model-card rule, the access-request address (access@hebrish.app), gated repos without a request form, gating inconsistent within a model line, pending access requests (counts only), and Jachnun/Sabich/Shakshuka/Meorav/PoC-N naming. Prints a report grouped by severity with a recommended fix per finding (which sibling skill and command), then offers to fix now or queue it. Use when asked to "audit Hugging Face", "check the HF org", "is everything in the right collections", "HF health check", or after publishing anything under huggingface.co/Hebrish.
---

# Hebrish Hugging Face health audit

## Access

- **Anyone:** every check except pending access requests reads public data only. Public repos, the
  cards of gated repos, collections and hebrish.app's `data/models.json` are readable without a token.
  Report what you find as an issue on
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues), titled for example
  `Hugging Face audit: 16 repos in no collection`, with the JSON findings that show it.
- **Maintainer access:** the pending-requests count (and anything about private repos) needs a Hugging
  Face token with the write or admin role in the [Hebrish organisation](https://huggingface.co/Hebrish),
  in `HF_TOKEN` (or saved by `hf auth login`). Without it the check is reported as skipped, not as
  "no requests". **Fixing** anything needs the same access, through the sibling skills named in each
  finding (`hf-collections`, `model-cards`, `access-requests`), or `website-change` for the site.

The audit itself never writes: it calls only list, info, get and download endpoints, and runs the
`hf-collections` script as a dry run.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *hf-audit*, for the maintainer setup.

Hebrish is Daniel Rosehill's one-person, not-for-profit project (<https://hebrish.app>). Written
2026-10-22; the script was run against the live org that day (results below).

## What it checks

| Check | What it looks for | Reuses |
| --- | --- | --- |
| `collections` | org repos in no collection (Boxty and `Hebrish/README` excluded, from the example config's `exclude`); repos hebrish.app's `models.json` lists for a model but missing from the collection the site names for it; items in any org collection that no longer resolve; repos on the site that the Hub does not answer for. With `--collections-config`, also the full config diff (`add`, `note`, `missing`, `unmanaged`, `create`, `description`) | `hf-collections/scripts/sync_collections.py` (subprocess, dry run) |
| `cards` | every rule of the model-cards audit (licence, front matter, single-speaker note, Hebrew script, voice, links, site listing), plus the access-request address: cards must name **access@hebrish.app** (standard since 2026-10-22); any other hebrish.app access address (e.g. `access-requests@hebrish.app`) is high. Also flags the terms page if it names anything else | `model-cards/scripts/audit_cards.py` (imported) |
| `gating` | gated repos with no `extra_gated_fields` form or no `extra_gated_prompt`; repos gated `auto` (policy is manual review); gating that differs within a model line (the repos hebrish.app lists under one model, or a repo and its `-GGUF/-ONNX/-MLX/-sherpa-onnx-int8` builds) | gate rules from `audit_cards.py` |
| `requests` | pending access requests, **count per repo only**; requester names, usernames and e-mails are never output | same API call as `access-requests` |
| `naming` | line names: the card of a site-listed main repo must name its line (Jachnun, Sabich, `Sabich-<Base>-<Size>`, Shakshuka, Meorav) and its current version; bare `v1`-`v5` instead of PoC-N; Shakshuka checkpoints without the prefix; Jachnun called main/recommended; Boxty mentions; "FUTO" in headings | naming rules from `audit_cards.py` |

Severity: **high** wrong for users now (no gate form, wrong address, dead item, site lists a repo the
Hub does not have); **medium** should be fixed soon (no collection, inconsistent gating, naming);
**low** card tidy-ups; **info** state (pending requests, skipped checks). A finding is a prompt to look,
not a verdict: the card rules have legitimate exceptions (see the `model-cards` skill), e.g. a bare `v2`
that is the base model, or a Boxty mention the maintainer wants.

## Steps

Script: `${CLAUDE_PLUGIN_ROOT}/skills/hf-audit/scripts/hf_audit.py`. If `CLAUDE_PLUGIN_ROOT` is unset,
clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/skills/hf-audit/scripts/hf_audit.py` inside it. It finds the sibling
scripts relative to itself, so keep the plugin directory intact.

```bash
A="uv run --no-project --with huggingface_hub python3 ${CLAUDE_PLUGIN_ROOT}/skills/hf-audit/scripts/hf_audit.py"
$A                                   # markdown report, every check (about 1 minute)
$A --json > /tmp/hf-audit.json       # findings list: [{check, repo, severity, detail, fix}]
$A --only collections,gating         # some checks
$A --collections-config <config>     # also diff against a collections config (hf-collections schema)
```

(Without `uv`: `pip install huggingface_hub` and run `python3` directly.) The output holds only repo
ids, counts and card text, never requester details, so it can go into an issue as it is.

1. **Run the audit** and show the markdown report: the per-check count table, then findings by
   severity. With many findings, summarise per check and list the high ones in full.
2. **Verify before reporting a finding as fact.** Open the flagged card lines or the collection page
   for anything surprising. A finding that rests on hebrish.app's `models.json` can be the site that is
   wrong, not the Hub. An empty result for a check you expected to fire: confirm the check actually ran
   (the `requests` check says "skipped" without a token; it never reports zero by default).
3. **Offer two routes per finding** (or per group of identical findings):
   - **Fix now** (maintainer access): use the skill and command in `fix`. Collections:
     `hf-collections` (edit the config, dry run, go-ahead, `--apply`). Cards, gate forms, naming:
     `model-cards` step 3 (show the diff, go-ahead, upload with a commit message). Pending requests:
     `access-requests` (the maintainer names who to accept or reject). Site data or terms page:
     `website-change`. Every change on the Hub is public: get the go-ahead first.
   - **Queue it:** add it to planning with the `queue-sprint` skill (`planning/backlog.md` in
     Hebrish-App), or open an issue on
     [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues) titled
     `Hugging Face: <finding>`. Never put requester details in either.
4. **After fixes, re-run** the affected checks (`--only ...`) and confirm the findings are gone.

## Live run, 2026-10-22

With an org token, every check: 54 models and datasets, 30 gated. Findings: collections 31 medium
(16 repos in no collection: every Sabich variant, `Sabich-ONNX`/`-MLX`, Shakshuka and its two builds,
`Hebrish/TTS-V1` (Meorav), `Hebrish-TTS-Voice-Recordings`, `Parakeet-TDT-0.6B-v2-Tech-And-Accent`,
Space `Hebrish-Models`; 15 site-listed repos missing from the collection the site names); gating 20 high
(6 gated build repos and 4 gated datasets with no form, each also without `extra_gated_prompt`) and 1
medium (`Parakeet-TDT-0.6B-v2-Tech-And-Accent` gated automatic); naming 27 medium (among them
`Hebrish/TTS-V1` never naming Meorav or "Meorav PoC-1", and Jachnun builds calling Jachnun the main
model); cards 2 medium, 52 low; requests 1 pending, on one dataset. No card named an access address
other than access@hebrish.app, and the terms page already named access@hebrish.app.

## Implementation notes

- `list_collections(owner=...)` returns only the first 4 items of each collection (seen 2026-10-20);
  the script reads items with `get_collection(slug).items`.
- `list_pending_access_requests` returns a generator in huggingface_hub 2.x; the script counts it
  without keeping the objects.
- Without `--collections-config`, the script hands `sync_collections.py` a temporary config with no
  collections, so it reports only org-wide orphans and the site cross-check.
