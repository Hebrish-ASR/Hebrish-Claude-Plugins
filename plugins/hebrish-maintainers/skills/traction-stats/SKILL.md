---
name: traction-stats
description: Refresh Hebrish's usage numbers (Hugging Face download requests for every project model and dataset, minutes recorded) on the hebrish.app About page ("First weeks in numbers") and in data/traction.json, which keeps one dated snapshot per run so growth can be shown. Use when asked to update the stats, refresh the download numbers, get traction figures for a grant application, or before an outreach email or grant submission.
---

# Hebrish traction stats

## Access

- The website repo (`Hebrish-ASR/Hebrish-App`, local `~/repos/github/audio-dictation/Hebrish-App`) with push rights;
  pushing to `main` deploys hebrish.app.
- `HF_TOKEN` is optional: download counts of gated repos are public metadata. In Daniel's environment run through
  `with-secrets`.

## Steps

1. `cd` to the website repo and `git pull`. If `data/stats.json` is more than a day old, run
   `python3 scripts/build_data.py --stats-only` first (the minutes figure comes from it).
2. Run `with-secrets uv run --no-project --with huggingface_hub python3 scripts/build_traction.py`.
   It makes about 20 Hub requests (two org listings plus one per personal repo). Don't run it in a loop or
   alongside a training `prepare`, which shares the account's rate limit.
3. Check the printed snapshot against the last `history` entry in `data/traction.json`. Download counts
   rarely fall; a large drop usually means a repo was renamed or deleted (stderr prints `skip <repo>`), so fix
   `PERSONAL_MODELS` / `PERSONAL_DATASETS` in the script instead of publishing the drop.
4. Commit `data/traction.json` and `about.html` only, then push.
5. Report the new figures next to the previous snapshot's.

## What the numbers mean (say this when quoting them)

- Hugging Face counts **download requests, not people**, and includes bots and CI. Dataset subsets overlap.
- **App users are not counted:** the apps download models from `cdn.hebrish.app`, not from Hugging Face.
- Safe wording for a grant application: "Hugging Face recorded about N download requests across the project's
  model repositories by <date>. This counts requests, not unique users, and excludes app downloads, which are
  served from the project's own server." Quote the main dataset (`Read-Aloud-Voice-Sentences`) on its own
  rather than the sum of all the dataset repos.
- Don't lead with likes or gated access-request counts; both were 1-2 at launch and partly the maintainer's own.

## Layout

The block on `about.html` sits between `<!-- traction:begin -->` and `<!-- traction:end -->`; never edit it by
hand. To change the wording, edit `render()` in `scripts/build_traction.py`, then run it with `--render-only`.
While the project is under 21 days old the page gives its age in days, after that in weeks. Retitle the
block once "First weeks" stops being true.
