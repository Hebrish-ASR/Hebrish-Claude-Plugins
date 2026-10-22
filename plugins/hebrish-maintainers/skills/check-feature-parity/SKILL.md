---
name: check-feature-parity
description: Check feature parity for the Hebrish apps across platforms and builds. Compares Android, Ubuntu (.deb) and Windows (zip) feature by feature, the released build on each platform against main, and the shared engine and model rules between the Kotlin and Python code, then records the result in the living matrix docs/feature-parity.json in Hebrish-ASR/Hebrish-App. Use when asked to "check feature parity", "what does Android have that desktop doesn't", "are the platforms level", "parity between builds", "is Windows behind" or for the "feature matrix".
---

# Check feature parity

## Access

- **Anyone.** The inventory, the comparison and the release checks work from a clone of the public
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) repository and public
  release data.
- **Push access to Hebrish-App** is needed to commit the updated matrix straight to `main`.
  **Fallback for everyone else:** commit it on a branch of your fork and open a pull request
  titled `Feature parity: <date>`.

Answers: which features exist on which platform, which gaps are on purpose, and which builds
people actually download are behind the code. Finding a gap is the output; closing it is a
separate task (queue it with `queue-sprint`). Per-platform bugs are the review skills
(`review-android-app`, `review-ubuntu-app`, `review-windows-app`). Platform parity is the
project's standing aim (decision D-2026-10-22-05 in `planning/decisions.md`).

| | |
|---|---|
| Android | `android/app`, `android/core` (Kotlin); tags `android-vX.Y.Z` |
| Ubuntu + Windows | `desktop/` (one Python codebase; per-OS only `hotkey_*`, `inserter_*`, `autostart.py`); tags `desktop-vX.Y.Z` |
| Shared | `shared/models.json`, `shared/update-protocol.md` |
| Matrix | `docs/feature-parity.json` (living file, update in place) |

Android and desktop are numbered separately (Android 0.6.0 and desktop 0.2.2 on 2026-10-20), so
version numbers say nothing about parity between them. Paths are relative to the repo root.

## 1. Inventory the features

`git pull --ff-only`. Build the feature list from the code and the docs, not from memory: the `##`
sections of `android/docs/maintaining.md` and `desktop/docs/maintaining.md`, each README's feature
list, the release notes, and the screens and settings themselves (Android `Prefs.kt` and the
activities; desktop `config.py` defaults and the `ui/window.py` tabs). Fan out: one subagent
inventories Android, one the desktop, each returning feature → evidence (file:line, version
introduced). Check a sample of what they return against the code.

Group features as: capture and triggers, transcription engine, insertion, model catalogue and
updates, feedback (beeps, levels, retake), history and files, setup and onboarding, settings
import and coexistence, links/About/contact, platform integration.

## 2. Classify each feature per platform

`present` · `partial` (say what is missing) · `missing` · `n/a` (deliberately absent; give the
reason). Typical `n/a`: the IME, floating mic and accessibility service are Android-only; the
global hotkey, tray and autostart are desktop-only; the `.deb` predecessor migration is
Linux-only. A feature that *could* exist on a platform and doesn't is `missing`, not `n/a`, unless
a doc or `planning/decisions.md` records the decision; cite it.

Ubuntu and Windows share code, so they differ only where per-OS code, the freeze or the packaging
differ. Check those spots: hotkey keys and modes, paste chord and terminal paste, autostart,
data-dir paths, anything PyInstaller doesn't collect.

## 3. Engine and model rules (the parity that changes transcripts)

Compare the numbers and steps, Kotlin against Python, and record each with both locations:

- trailing silence before decode (desktop `engine.TAIL_PAD_S`; Android `Transcriber` trim plus
  tail pad, `Recorder` segment pause);
- inner-pause handling (desktop `engine.stretch_pauses`; whether Android has an equivalent);
- long-take chunking (desktop at most 30 s, cut at the quietest window; Android segment cuts);
- sample rate, normalisation, model files and quantisation loaded;
- update protocol steps (`shared/update-protocol.md`), catalogue fetch URL and fallback;
- catalogue copies: `android/app/build.gradle.kts` copies `shared/models.json` at build time; the
  desktop bundles `desktop/hebrish/data/models.json` (must be byte-identical).

A rule that differs without a measurement explaining it is the most important kind of finding
here: the same audio gives different text on different platforms.

## 4. Builds: released vs main

Per platform, what users download against what the code has:

- Released version: `curl -s "https://cdn.hebrish.app/downloads/latest.json?x=$RANDOM"` →
  `files.android.version`, `files.ubuntu.version`, `files.windows.version`. Confirm each equals
  the newest tag and that the GitHub release carries the asset
  (`gh release view <tag> -R Hebrish-ASR/Hebrish-App --json assets`; the `.deb` is uploaded by
  hand and is the one that goes missing).
- Unreleased work: `git log --oneline <latest tag>..HEAD -- android shared` and
  `-- desktop shared`. List user-visible changes waiting for a release.
- Ubuntu vs Windows from the same `desktop-v` tag: both assets present, same version in
  `latest.json`. If they differ, one platform's users are on older code.
- F-Droid: `curl -s "https://fdroid.hebrish.app/repo/index-v1.json?x=$RANDOM"` lists the current
  Android `versionName` for `app.hebrish.dictation`.

## 5. Record

Update `docs/feature-parity.json` in place (it is the living matrix, not a dated log):

```json
{
  "checked": "YYYY-MM-DD",
  "commit": "<app repo short sha>",
  "released": {"android": "0.6.0", "ubuntu": "0.2.2", "windows": "0.2.2"},
  "features": [
    {
      "id": "beeps",
      "group": "feedback",
      "name": "Start/stop beeps",
      "android": {"status": "present", "since": "0.6.0", "evidence": "android/core/.../Recorder.kt:NN"},
      "ubuntu":  {"status": "present", "since": "0.2.0", "evidence": "desktop/hebrish/audio.py:NN"},
      "windows": {"status": "present", "since": "0.2.0", "evidence": "shared desktop code", "verified": false},
      "notes": ""
    }
  ],
  "engine_rules": [
    {"rule": "trailing silence before decode", "android": "…", "desktop": "1.0 s (engine.TAIL_PAD_S)", "same": false, "explained_by": ""}
  ],
  "unreleased": {"android": ["…"], "desktop": ["…"]}
}
```

`verified: false` marks a Windows status inferred from shared code or CI. Keep `id`s stable
between runs so the diff shows what changed. The file also has a `twin_lag` block, filled by the
maintainer from a private ledger: leave it unchanged. Link the file from the root `README.md`
docs list if it isn't already.

The repo is public and the matrix must contain nothing private: no names, machines or internal
notes. Commit `Feature parity: <date>`, staging only `docs/feature-parity.json` (and the README if
you linked it) in one command, because other sessions commit in this repo too. Push, or open a
pull request (see Access).

## Report

In chat: the gaps that are not `n/a`, worst first (engine-rule differences, then missing
user-facing features, then builds behind main), each with the sprint it would go into
(`planning/backlog.md`); then the counts per platform and what changed since the last run
(`git diff` of the matrix).

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *check-feature-parity*, for the maintainer setup.
