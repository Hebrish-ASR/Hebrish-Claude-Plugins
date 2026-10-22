---
name: review-ubuntu-app
description: Review the Hebrish desktop app as shipped on Ubuntu (the hebrish .deb built from desktop/ in Hebrish-ASR/Hebrish-App), either the changes since the last desktop-v* release or the whole app. Runs the tests and the off-screen self-test, builds and inspects the .deb, checks the Linux-only code (evdev hotkey, uinput paste, XDG autostart), identity and coexistence, docs and release state, and a local install if there is one. Use when asked to "review the Ubuntu app", "review the Linux app", "audit the .deb", "is the desktop app OK on Linux" or "check the Linux build before release".
---

# Review the Ubuntu app

## Access

- **Anyone.** Works from a clone of the public
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) repository on an Ubuntu (or
  Debian-family) machine, plus public release data. Findings go back as a GitHub issue or a pull
  request on that repo.

A review, not a fix and not a release. Report findings; fix only when asked. The Windows side of
the same code is `review-windows-app`; comparing platforms is `check-feature-parity`.

| | |
|---|---|
| Repo | `Hebrish-ASR/Hebrish-App`, code in `desktop/`; tags `desktop-vX.Y.Z` (one tag ships both the .deb and the Windows zip) |
| Linux-only code | `desktop/hebrish/hotkey_evdev.py`, `desktop/hebrish/inserter_linux.py`, the Linux half of `desktop/hebrish/autostart.py`, `desktop/packaging/debian/`, `desktop/build-deb.sh`, `desktop/install.sh` |
| Docs to read first | `desktop/CLAUDE.md`, `desktop/docs/maintaining.md` (measured findings with V/I marks, and the section on Hebrish and Parlance) |

Target platform (as of 2026-10-22): Ubuntu 26.04, KDE Plasma on Wayland, Python 3.14, PySide6
from apt. Paths below are relative to the repo root.

## Scope

Default: `git pull --ff-only`, then
`git log --oneline $(git tag -l 'desktop-v*' | sort -V | tail -1)..HEAD -- desktop shared`.
Whole-app: every module in `desktop/hebrish/`.

## Checks

1. **Tests.** Venv per `desktop/CLAUDE.md`:
   `cd desktop && uv venv --python /usr/bin/python3 --system-site-packages .venv && uv pip install -e . pytest`
   (a uv-managed Python can't import apt's `evdev` and PySide6, so the system Python is required).
   Then `.venv/bin/python -m pytest tests -q`. If `/tmp` is a small tmpfs, point `TMPDIR` at a
   directory on disk (for example `~/.cache/deb-build-tmp`) for anything that writes large temp files.
2. **Self-test, off-screen.** `QT_QPA_PLATFORM=offscreen .venv/bin/python -m hebrish --selftest`.
   Never run live record-and-paste tests on the user's desktop session: if behaviour needs
   exercising, drive the controller from a script with the UI off-screen.
3. **The .deb.** `cd desktop && mkdir -p ~/.cache/deb-build-tmp && TMPDIR=~/.cache/deb-build-tmp ./build-deb.sh`,
   then `dpkg-deb -I dist/hebrish_<ver>-1_amd64.deb` and `dpkg-deb -c dist/hebrish_<ver>-1_amd64.deb`:
   - `Depends` includes apt's PySide6 and is pinned to python3 3.14; sherpa-onnx is bundled.
   - `Conflicts`/`Replaces` name the predecessor packages (`voice-to-hebrish`,
     `codeswitch-dictation`, `parakeet-dictation`) and **not** `parlance` (a separate app by the
     same author that must be installable alongside).
   - Every installed path, the desktop file, the udev rule `70-hebrish-uinput.rules`, the uinput
     device name and the socket are named `hebrish`.
   - `lintian dist/*.deb` if lintian is installed; report errors, not style warnings.
4. **Linux code paths.** evdev reading stays non-exclusive and ignores the `hebrish-keyboard` and
   `parlance-keyboard` virtual devices (`IGNORED_DEVICES` in `hotkey_evdev.py`); paste is clipboard
   plus a uinput chord, never typed keycodes (typed keycodes follow the keyboard layout); a modifier
   hotkey cancels the take when another key is pressed; default hotkey F14 (Parlance uses F13).
   Nothing writes to `~/.config/parlance` or Parlance's data dir; the first-start import copies
   settings and **hardlinks** models, never moves them.
5. **Engine rules.** `TAIL_PAD_S` at least 0.6 (1.0 as of 2026-10-22), the `stretch_pauses`
   parameters, chunks of at most 30 s cut at the quietest window: each has a measurement in
   `desktop/docs/maintaining.md`. A change without a new measurement is a finding.
6. **Models.** `desktop/hebrish/data/models.json` is byte-identical to `shared/models.json`
   (`desktop/tests/test_shared.py` checks); the code-switching lines (Sabich, Jachnun, Shakshuka)
   and stock Parakeet only; update protocol per
   `shared/update-protocol.md` (manifest written last, reload deferred while a take runs).
7. **Links.** hebrish.app URLs only in `desktop/hebrish/ui/about.py` (`HEBRISH_LINKS`); no
   versioned download URLs; no distribution channel beyond those the README lists.
8. **A local install, if this machine has one.** `dpkg -l hebrish`, `hebrish-model status`,
   `hebrish-model check codeswitch` (must print a latest version; a 401 means it read a gated
   Hugging Face repo instead of the CDN manifest). Is it running:
   `pgrep -af "bin/hebrish( |$)|-m hebrish( |$)"` (never `pkill -f`, which can hit unrelated
   processes). Read its log for tracebacks. Don't install, upgrade or restart it as part of a review.
9. **Docs and release state.** `__version__` in `desktop/hebrish/__init__.py`,
   `desktop/pyproject.toml`, `.github/desktop-release-notes.md` and the latest tag agree, or the gap
   is unreleased work. `gh release view <tag> -R Hebrish-ASR/Hebrish-App --json assets` includes the
   `.deb` (CI can't build it; it is uploaded by hand and is the asset most often missing).
   `curl -s "https://cdn.hebrish.app/downloads/latest.json?x=$RANDOM"`: `files.ubuntu.version`
   matches; `curl -s -o /dev/null -w '%{http_code} %{redirect_url}' https://hebrish.app/get/ubuntu`
   gives 302 to it (GET as shown: HEAD returns 405).

## Report

In chat, ranked most severe first: crash or data loss (including touching Parlance's data), wrong
behaviour, packaging error, rule breach, doc drift, polish. Each finding: file:line, what is
wrong, how you know (test, self-test, built package, read the code), and the fix in one sentence.
Then what wasn't checked and the release state. A finding in shared desktop code also affects
Windows: say so.

Offer to fix or open issues on the public repo; don't open them unasked. Contributors send fixes
as pull requests against `main`.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *review-ubuntu-app*, for the maintainer setup.
