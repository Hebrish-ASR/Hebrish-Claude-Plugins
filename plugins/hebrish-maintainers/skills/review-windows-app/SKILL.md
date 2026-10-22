---
name: review-windows-app
description: Review the Hebrish desktop app as shipped on Windows (the portable PyInstaller zip that CI builds from desktop/ in Hebrish-ASR/Hebrish-App). Needs no Windows machine: reads the Windows-only code, runs the tests, uses the CI Windows job (tests, freeze, frozen-exe self-test) as the test bed, and inspects the released zip. Use when asked to "review the Windows app", "audit the Windows build", "is the Windows zip OK", "check Windows before release" or "does Hebrish work on Windows".
---

# Review the Windows app

## Access

- **Anyone.** Code reading, the tests, the artifact listing and the release checks work from a
  clone of the public [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App)
  repository with the `gh` CLI.
- **Write access to Hebrish-App** is needed to dispatch the CI workflow on the main repo
  (step 1). **Fallback for everyone else:** fork the repo and run the `desktop.yml` workflow on
  your fork (Actions must be enabled there), or open a pull request, which runs CI on it.

A review, not a fix and not a release. The desktop code is shared with Ubuntu; only the hotkey,
paste and autostart differ, plus the PyInstaller freeze. Shared-code findings also belong to
`review-ubuntu-app`; comparing platforms is `check-feature-parity`.

| | |
|---|---|
| Repo | `Hebrish-ASR/Hebrish-App`, tags `desktop-vX.Y.Z`; CI `.github/workflows/desktop.yml` (job `windows`) |
| Windows-only code | `desktop/hebrish/hotkey_win.py` (pynput low-level hook), `desktop/hebrish/inserter_win.py` (SendInput), the HKCU `Run` half of `desktop/hebrish/autostart.py`, `desktop/packaging/windows/launcher.py`, `make_icon.py`, the PyInstaller command in `desktop.yml` |
| Docs | `desktop/CLAUDE.md`, `desktop/docs/maintaining.md`, `desktop/README.md` (Windows install) |

**No Windows host is assumed.** Everything here is CI, static reading and the built artifact. Say
that in the report, and mark every behavioural claim about Windows as inferred unless CI
exercised it. (If you do have a Windows machine, a manual run of the released zip is a bonus;
report it as such.)

## Scope

Default: `git pull --ff-only`, then
`git log --oneline $(git tag -l 'desktop-v*' | sort -V | tail -1)..HEAD -- desktop shared .github/workflows/desktop.yml`.

## Checks

1. **CI is the Windows test bed.** Latest runs:
   `gh run list -R Hebrish-ASR/Hebrish-App --workflow desktop.yml -L 5`. If `main` has desktop
   changes newer than the last green Windows run, trigger one (the workflow has
   `workflow_dispatch`; a dispatch on `main` tests, freezes and self-tests but does not release):
   `gh workflow run desktop.yml -R Hebrish-ASR/Hebrish-App --ref main`, then
   `gh run watch <id> -R Hebrish-ASR/Hebrish-App --exit-status --interval 30` (the default 3 s
   polling burns GitHub API quota). Read the output of the `Self-test the frozen exe` step
   (`selftest.txt`), not just the job colour: a green job with an empty self-test is a finding.
2. **Freeze completeness.** Every new module, data file or dependency since the last release is
   reachable by PyInstaller. Per-OS modules are imported dynamically, so each needs a
   `--hidden-import` (as of 2026-10-22: `hebrish.hotkey_win`, `hebrish.inserter_win`,
   `pynput.keyboard._win32`, `pynput.mouse._win32`); package data needs `--collect-data hebrish`;
   native libraries need `--collect-all`. A new import of a per-OS module or a new runtime data file
   without a matching flag is a finding. Check that the `[windows]` extra in `desktop/pyproject.toml`
   matches what the code imports.
3. **Windows code paths.** The hotkey hook releases cleanly on quit and doesn't swallow other apps'
   keys; paste is clipboard plus SendInput Ctrl+V (not typed characters, which follow the keyboard
   layout); the clipboard is restored after paste if the Linux side does so; autostart writes
   `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` value `Hebrish` with the exe path quoted.
4. **Portability of shared code.** Read the shared modules for Windows breakers: hard-coded `/`
   paths or `~/.config` instead of the platform dirs; `os.fork`, signals or `fcntl`; file handles
   kept open while renaming or deleting (Windows locks them: the model-store version-folder swap and
   pruning are the risk); `open()` without `encoding="utf-8"` on files that can hold Hebrew; paths
   that can exceed 260 characters under the models dir; `QLocalServer` names that could collide
   with Parlance (a separate app by the same author that can run alongside).
5. **Identity and coexistence.** Data dir, Run value, local-server name and window titles say
   Hebrish, never Parlance. The Parlance settings import copies and never moves; on Windows a
   hardlink across volumes fails, so check the fallback is a copy, not a move.
6. **The artifact.**
   `gh release download <tag> -R Hebrish-ASR/Hebrish-App -p '*windows*.zip' -D <scratch dir>/win`
   (not a small tmpfs `/tmp`: the zip is around 70 MB), then `python3 -m zipfile -l` it. Expect
   `Hebrish/Hebrish.exe`, the sherpa-onnx and PortAudio DLLs, `hebrish/data/models.json`
   (byte-identical to `shared/models.json`) and the icon. Compare the size with the previous
   release (68.6 MB at desktop 0.2.2); a large jump means something extra got collected.
7. **Docs and release state.** `__version__`, the release notes and the tag agree;
   `curl -s "https://cdn.hebrish.app/downloads/latest.json?x=$RANDOM"`: `files.windows.version`
   matches; `curl -s -o /dev/null -w '%{http_code} %{redirect_url}' https://hebrish.app/get/windows`
   gives 302 to the zip (GET as shown: HEAD returns 405); `desktop/README.md` Windows steps still
   match the zip layout.

## Report

In chat, ranked most severe first: won't start or crashes (frozen self-test), data loss, missing
from the freeze, wrong behaviour, rule breach, doc drift. Each finding: file:line, what is wrong,
how you know (CI log, artifact listing, code reading = inferred), and the fix in one sentence.
State plainly whether anything ran on a real Windows desktop.

Offer to fix or open issues on the public repo; don't open them unasked. Contributors send fixes
as pull requests against `main`.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *review-windows-app*, for the maintainer setup.
