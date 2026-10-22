---
name: android-release
description: Take a round of feedback on the Hebrish Android app (android/ in Hebrish-ASR/Hebrish-App) through to a published APK: implement, compile, document, version and tag, verify the CI build, update the CDN copy and latest.json, publish to the Hebrish F-Droid repo, and note it on the hebrish.app changelog. Contributors without release access get the same flow up to a pull request. Use when asked to "push out a new APK", "make a new point release", "release the Android app", "ship these app changes" or to get a list of app feedback "into the latest version".
---

# Hebrish Android: feedback round → release

## Access

- **Anyone:** steps 0 to 2 (implement, compile, document) work from a clone of the public
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) repository.
- **Maintainer access:** steps 3 to 5 publish the release and need what only the project has:
  push access to `main` and tags on Hebrish-App, write access to the hebrish.app CDN bucket (an
  S3-compatible API key for `cdn.hebrish.app`), workflow-dispatch rights on
  `Hebrish-ASR/Hebrish-FDroid`, and the website's private repository for the changelog.
- **Fallback for everyone else:** stop after step 2 and open a pull request against `main` with
  the code and the docs, **without** the version bump and **without**
  `.github/android-release-notes.md` (the maintainer sets both when releasing). In the PR body,
  list the user-visible changes in plain words and say how it was tested ("compiled, not run on
  a device", or the Android version you ran it on).

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *android-release*, for the maintainer setup.

Written 2026-10-20 after a feedback list had to be repeated because an earlier session only
partly shipped it (0.6.0 was committed but never tagged). The rule that follows: **a round is not
done until the tag is pushed, the APK is on the CDN, `latest.json` points at it and the F-Droid
index lists it.** For a contributor, the round is done when the pull request is open.

Paths are relative to the Hebrish-App repo root.

## 0. Before writing code

- Check what is already built but unreleased: `git tag -l 'android-v*' | sort -V | tail -1` vs
  `versionName` in `android/app/build.gradle.kts`, and
  `curl -s "https://cdn.hebrish.app/downloads/latest.json?x=$RANDOM"` (`files.android.version`).
  If the version in gradle has no tag yet, fold the new work into it rather than bumping again.
- Read `android/docs/maintaining.md` (architecture, what is verified) and `planning/backlog.md`
  (the Android sprint). Record the round's items there with the `queue-sprint` skill if they are
  not already in it.
- `shared/models.json` is fetched live by every installed app (Android and desktop). Changes to
  `default`/`recommended`, ids or the schema affect old builds: see `android/docs/maintaining.md`,
  "Models by line, catalogue v2" (and the older "Catalogue: Jachnun recommended" bullet, since
  superseded: Sabich is the recommended model as of 2026-10-21). After editing it: `cp shared/models.json desktop/hebrish/data/` and
  `cd desktop && uv run --with pytest python -m pytest -q tests/test_shared.py`.

## 1. Build check

```bash
cd android && JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 ./gradlew -q assembleDebug
```

Needs JDK 21 (adjust the path to your install); set `JAVA_HOME` per command, because a shell
default pointing at a missing JDK 17 was seen on 2026-10-20. Add `--offline` once dependencies
are cached. The app has no androidx and no tests (as of 2026-10-22); screens are built in code
(`Page.kt`). Say "compiled, not run on a device" in the commit and docs unless someone has
actually run it on a device. If you have an Android device connected over adb, the
`review-android-app` skill's device section is the smoke test.

## 2. Document in the same commit

- `android/docs/maintaining.md`: a dated section per feature (what, where in the code, the
  decisions and who made them, (V)/(I) markers for verified/inferred), and extend "Not yet
  verified".
- `android/README.md` and the root `README.md` when user-visible behaviour or the model list
  changes.
- A decision made during the round (a default, a scope call): `log-decision` skill.

Contributors: open the pull request now (see Access). Maintainer: continue.

## 3. Release notes, version, tag, CI (maintainer)

- Overwrite `.github/android-release-notes.md`; CI uses it as the GitHub release body. Format: bold
  one-line headline `**X.Y.Z: …**`, then plain user-facing bullets, last bullet "Not yet tested on
  a device. arm64-v8a only. Android 9+. Downloads: [hebrish.app/download](https://hebrish.app/download)."
  (drop the first sentence once it has been tested). New features → minor bump, fixes only → patch.
- If `android/docs/maintaining.md` has a section titled "after X.Y.Z", rename it to the new version.
- Commit the code and docs, then let the script set the version and tag (it bumps `versionName`
  and `versionCode`, refuses a version that isn't newer or notes that don't start with `**X.Y.Z`,
  commits only the version file and notes, makes an annotated tag; `--push` pushes `main` and the
  tag). CI fails a tag that differs from the code.

```bash
scripts/release-tag.sh android X.Y.Z --push
gh run watch $(gh run list -R Hebrish-ASR/Hebrish-App --workflow android.yml -L1 --json databaseId -q '.[0].databaseId') \
  -R Hebrish-ASR/Hebrish-App --exit-status --interval 30
gh release view android-vX.Y.Z -R Hebrish-ASR/Hebrish-App --json assets -q '.assets[]|.name+" "+(.size|tostring)'
```

`.github/workflows/android.yml` signs the APK and creates the release with `Hebrish-vX.Y.Z.apk`
(about 4 minutes on 2026-10-20).

## 4. CDN, latest.json and F-Droid (maintainer)

Since 2026-10-21 the CDN holds **one stable APK, overwritten on every release**; old APKs stay on
the GitHub releases only.

| CDN object (overwrite) | GitHub release asset |
|---|---|
| `https://cdn.hebrish.app/apps/android/Hebrish-latest.apk` | `Hebrish-vX.Y.Z.apk` (tag `android-vX.Y.Z`) |

1. Download the release APK to a directory on disk (not a small tmpfs `/tmp`):
   `gh release download android-vX.Y.Z -R Hebrish-ASR/Hebrish-App -p 'Hebrish-vX.Y.Z.apk' -D <dir>`.
2. Overwrite the stable object with content type `application/vnd.android.package-archive`,
   `Cache-Control: public, max-age=300` (never `immutable`: the object changes) and
   `Content-Disposition: attachment; filename="Hebrish-vX.Y.Z.apk"`, so browsers still save the
   versioned name.
3. Rewrite `downloads/latest.json` from the live copy (fetch with a cache-busting `?x=`). Change
   only `files.android` = {`url` (the stable object), `name` (versioned asset name), `platform`,
   `size`, `sha256`, `version`} and the top-level `version`/`released`; leave the desktop entries
   alone. Upload with `max-age=300`. hebrish.app's `/get/<os>` route, its download pages and the
   apps all read this file.
4. Verify the thing itself:
   `curl -s "https://cdn.hebrish.app/apps/android/Hebrish-latest.apk?x=$RANDOM" | sha256sum` equals
   the release APK; `latest.json` names the new version;
   `curl -s -o /dev/null -w '%{http_code} %{redirect_url}' https://hebrish.app/get/android` gives
   302 to the stable object. **Use GET: HEAD on `/get/*` returns 405**, which looks broken and
   isn't. Edge caches can serve the previous file for up to 5 minutes after an overwrite.

**F-Droid is required for every Android release.** The Hebrish F-Droid repo
(`Hebrish-ASR/Hebrish-FDroid`, served at `fdroid.hebrish.app`) builds its index from the GitHub
releases, never from the CDN, so a CDN upload alone does not reach F-Droid users. It rebuilds
hourly on its own; publish now and confirm:

```bash
gh workflow run publish.yml -R Hebrish-ASR/Hebrish-FDroid
gh run watch $(gh run list -R Hebrish-ASR/Hebrish-FDroid -w publish.yml -L1 --json databaseId -q '.[0].databaseId') \
  -R Hebrish-ASR/Hebrish-FDroid --exit-status --interval 30
curl -s "https://fdroid.hebrish.app/repo/index-v1.json?x=$RANDOM" | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(sorted(p['versionName'] for p in d['packages']['app.hebrish.dictation']))"
```

The release is not done until the index lists the new `versionName`. F-Droid is the recommended
Android install on hebrish.app; the APK is second.

## 5. Elsewhere (maintainer)

- hebrish.app changelog (private website repo): an `<article class="log">` at the top of
  `changelog.html`, copying the existing ones, tag text `Android X.Y.Z`, plain user language, the
  same facts as the release notes. Download links follow `latest.json`; never put a versioned file
  URL on a page. If setup steps changed, keep `setup.html` and `SetupActivity` in step (same step
  ids).
- `planning/backlog.md`: set the round's items to `released X.Y.Z` (see `planning/README.md` for
  status words), and update "Last updated".

## Report

Tag and release URL, the CDN sha256 match, the `/get/android` target, the F-Droid index showing
the new version, the changelog commit. Say plainly if the release is untested on a device.
Contributor: the pull request URL and what the maintainer still has to do (version, notes,
release).
