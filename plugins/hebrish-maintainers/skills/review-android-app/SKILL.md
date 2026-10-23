---
name: review-android-app
description: Review the Hebrish Android app (package app.hebrish.dictation, android/ in Hebrish-ASR/Hebrish-App), either the changes since the last android-v* release or the whole app. Builds it, checks identity, manifest, model and link rules, docs and release state, and smoke-tests on an Android device over adb if one is connected. Reports findings ranked by severity. Use when asked to "review the Android app", "audit the Hebrish APK", "is the Android build OK", "check the Android app before release" or "what's broken on Android".
---

# Review the Android app

## Access

- **Anyone.** Everything here works from a clone of the public
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) repository, public
  release data and, optionally, your own Android device. Findings go back as a GitHub issue or a
  pull request on that repo.

A review, not a fix and not a release. Report what is wrong, confirm what you can, and fix only
when the user asks. Releasing is the `android-release` skill; comparing Android with the desktop
builds is `check-feature-parity`.

| | |
|---|---|
| Repo | `Hebrish-ASR/Hebrish-App`, public, branch `main`, Android tags `android-vX.Y.Z` |
| Code | `android/app` (screens, IME `VoiceImeService`, floating mic `FloatingMicService`), `android/core` (`Transcriber`, `Recorder`, `TakeDecoder`, `ModelStore`, `Catalogue`) |
| Docs to read first | `android/README.md`, `android/docs/maintaining.md` (each section has a dated, measured reason; "Not yet verified" lists what has never run on a device) |

Paths below are relative to the repo root.

## Scope

Default: the changes since the last release:

```bash
git pull --ff-only
git log --oneline $(git tag -l 'android-v*' | sort -V | tail -1)..HEAD -- android shared
```

"Review the whole app" means every file under `android/app/src/main` and `android/core/src/main`.
For a whole-app review, split the reading across subagents by area (screens, IME + floating mic,
core engine, model store) and check what they report against the code before it goes in the report.

## Checks

1. **It builds.** Needs JDK 21; set `JAVA_HOME` explicitly per command (on Ubuntu:
   `/usr/lib/jvm/java-21-openjdk-amd64`), because a stale shell default pointing at a missing JDK 17
   was seen on 2026-10-20:
   `cd android && JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 ./gradlew -q assembleDebug lintDebug`.
   Read new lint errors from `android/app/build/reports/lint-results-debug.txt`. There are no unit
   tests in `android/` (as of 2026-10-22), so say that rather than reporting "tests pass".
2. **Shared catalogue and tests.** The Android build copies `shared/models.json` in
   (`android/app/build.gradle.kts`). Run the shared tests from `desktop/` (venv recipe in
   `desktop/CLAUDE.md`): `.venv/bin/python -m pytest tests/test_shared.py -q`.
   `test_hebrish_ships_only_code_switching_lines_and_stock` must pass: Hebrish ships the
   code-switching lines (Sabich, recommended and first; Jachnun; Shakshuka) and stock Parakeet,
   and no fine-tunes without Hebrew (test name and contents as of 2026-10-22).
3. **Identity.** The app id is `app.hebrish.dictation`. Parlance is a separate dictation app by
   the same author that can be installed alongside; its identifiers must not leak in:
   `grep -rn -i parlance android/app/src android/core/src`. The settings import from Parlance and
   the coexistence notes are the only legitimate hits. Return-to-keyboard prefers
   `app.hebrish.keyboard`, then HeliBoard.
4. **Manifest.** Every permission has a reason in `android/docs/maintaining.md`; activities other
   than the launcher stay `exported="false"`; the IME and accessibility services keep their
   `BIND_*` permissions. A new permission or exported component is a finding unless documented.
5. **Behaviour against the measured rules.** Trailing silence of at least 0.6 s before decode
   (`Transcriber`, `Recorder`), segment cuts at pauses, model reload deferred during a take, the
   update protocol in `shared/update-protocol.md`. A change that alters one of these without a new
   measurement in `maintaining.md` is a finding.
6. **Links and channels.** hebrish.app links come from one place (`Hebrish.kt`). No versioned CDN
   or GitHub asset URL in the app or README, except the versioned README badge and install link
   that the release process maintains. Distribution channels are the GitHub release, hebrish.app
   (`/get/android`) and the Hebrish F-Droid repo (`fdroid.hebrish.app`). A link to any channel
   not in that list is a finding: adding a channel is the maintainer's call.
7. **Strings and accessibility.** User-visible text in `strings.xml`, not hard-coded; content
   descriptions on icon buttons; Hebrew terms romanized as on hebrish.app (no Hebrew script as
   model output).
8. **Docs match the code.** `versionName`/`versionCode` in `android/app/build.gradle.kts`, the
   README badge, `.github/android-release-notes.md` and the latest tag agree, or the gap is the
   intended unreleased work. Features added since the last release have a `maintaining.md`
   section, and "Not yet verified" lists the new ones.
9. **Release state** (public, read-only):
   - `gh release view <latest android tag> -R Hebrish-ASR/Hebrish-App --json assets` has
     `Hebrish-vX.Y.Z.apk`.
   - `curl -s "https://cdn.hebrish.app/downloads/latest.json?x=$RANDOM"`: `files.android.version`
     equals it.
   - `curl -s -o /dev/null -w '%{http_code} %{redirect_url}' https://hebrish.app/get/android` gives
     302 to the CDN file. Use GET as shown: a HEAD (`curl -I`) on `/get/*` returns 405, which looks
     broken and isn't.

## On a device or an emulator

Use an Android device connected over adb, if you have one. `unauthorized` means the device owner
must accept the prompt on the device. With no device, use an emulator (next section) for anything
visual: layout, theme, dark mode, crashes on opening a screen. Recording and dictation still need a
real device; say so in the report.

Never uninstall, and never install a debug APK over a release install: the signatures differ, and
uninstalling deletes the downloaded models and settings. If the installed version is behind the
release, ask before installing the release APK.

- `adb shell dumpsys package app.hebrish.dictation | grep -E 'versionName|versionCode'`
- `adb shell ime list -s` lists `app.hebrish.dictation/.VoiceImeService`;
  `adb shell settings get secure enabled_accessibility_services` includes the floating mic if it
  is in use.
- Start each screen and watch for crashes: `adb logcat -c`, then
  `adb shell am start -n app.hebrish.dictation/.<Activity>` (only `MainActivity` is exported; the
  others refuse with "Permission Denial ... not exported" unless adb runs as root, which an
  emulator allows: `adb root`) for `MainActivity`, `SetupActivity`,
  `ModelsActivity`, `KeyboardActivity`, `FloatingMicActivity`, `ControlsActivity`, `AboutActivity`,
  then `adb logcat -d -b crash` and `adb logcat -d | grep -E 'AndroidRuntime|hebrish'`.
  Screenshot with `adb exec-out screencap -p > <scratch dir>/<screen>.png` and look at it.
- Don't record or dictate on someone's device unasked. If you confirmed an item from "Not yet
  verified" on the device, moving it out of that list in `maintaining.md` with the date and the
  Android version (not a personal device name) is the review's one doc edit:
  `Android docs: verified on Android <version>, <date>`.

### Emulator (no device needed; verified 2026-10-23 on Ubuntu x86-64 with KVM)

Google's official `android-skills` plugin (skill `android-cli`; github.com/android/skills, which
is its own Claude Code marketplace) covers the generic emulator loop with Google's
`android` CLI. Plain SDK tools do the same; what is specific to this app:

1. **Image:** an x86-64 `google_apis` image of API 30+ (`system-images;android-34;google_apis;x86_64`
   was used). The APK ships arm64-v8a only; those images translate arm64 and install it. Older or
   AOSP images refuse it (`INSTALL_FAILED_NO_MATCHING_ABIS`) (I for the refusal; the install on
   API 34 is V).
   `sdkmanager --install emulator "system-images;android-34;google_apis;x86_64"`, then
   `avdmanager create avd -n hebrish34 -k "system-images;android-34;google_apis;x86_64" -d pixel_6`.
2. **Boot headless:** `emulator -avd hebrish34 -no-window -no-audio -no-snapshot -gpu swiftshader_indirect &`,
   then wait for `adb shell getprop sys.boot_completed` = 1 (about 30 s with KVM).
3. **Install the flavour APK:** the app has product flavours, so `assembleDebug` writes
   `android/app/build/outputs/apk/fdroid/debug/app-fdroid-debug.apk` (and `play/`).
   `outputs/apk/debug/app-debug.apk` may be a stale leftover from before the flavours and is never
   refreshed: installing it shows an old build with no error. Check the APK's time first.
4. **Screens:** `adb root` (emulator only), then `am start` each activity as above and
   `adb exec-out screencap -p > <scratch>/<screen>.png`. Dark mode: `adb shell cmd uimode night yes`.
   `adb shell settings put global window_animation_scale 0` keeps screenshots from catching a
   transition.
5. Crash lines from other apps (the Google search app crashes with SIGILL on this image) are
   not ours: filter `adb logcat -d -b crash` by `app.hebrish`.

## Report

In chat, ranked most severe first: crash or data loss, wrong behaviour, rule breach (identity,
models, links, channels), doc drift, polish. Each finding: file:line, what is wrong, how you know
(built, ran on a device, read the code), and the fix in one sentence. Then what you could not
check (no device, no tests) and the release-state line.

Offer to fix or to open issues on `Hebrish-ASR/Hebrish-App`. The repo is public, so don't open
issues unasked. Contributors send fixes as pull requests against `main`.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *review-android-app*, for the maintainer setup.
