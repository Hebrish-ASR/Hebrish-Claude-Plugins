---
name: android-screenshot-iteration
description: Improve the Hebrish Android app from the latest phone screenshot: read it, fix the UI, test the build on the phone before release.
---

# Android iteration from screenshots

One round: a screenshot of the installed app plus what the user wants changed, turned into a
change that has been seen working on a phone. Written 2026-11-06 from the voice keyboard round
(B-96 in `planning/backlog.md`). Releasing is `android-release`; a review with no change is
`review-android-app`.

Use it on "look at the latest Android screenshot", "check the Android album", "here's the latest
install, change this", or a pasted screenshot of the app with requests.

## Access

- **Anyone:** steps 1 to 6 from a clone of
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) and your own screenshot.
  Without push access, the change goes back as a pull request and the build check stops at step 5.
- **Maintainer access:** the signed test build (step 7) needs write access to the repo, and the
  shared album needs its owner's login. If you have access to the private Hebrish-ASR/Hebrish-Mgmt
  repository, read `docs/maintainer-agent-notes.md`, section *android-screenshot-iteration*, for the
  album and the maintainer setup.

## Steps

1. **Get the screenshot.** A pasted image is enough. For a Google Photos album there is no usable
   API, so use a signed-in browser, read only. The grid runs **oldest first** and loads as it
   scrolls, so scroll the page's scroller to the end while collecting every
   `a[href*="/photo/"]`, then pick the newest by the date in its `aria-label`
   ("Photo – Portrait – 6 Nov 2026, 14:50:59"). Never go by grid position. Compare that time with
   the phone's clock in a pasted shot: if they match, it is the same image.
2. **Read it.** Note the app version the phone runs (`adb shell dumpsys package
   app.hebrish.dictation | grep versionName`, or ask), and the navigation mode: the shot shows
   three buttons or a gesture bar. If the install is older than `main`, some of it may be fixed.
3. **Tie it to the code.** Voice keyboard: `android/app/src/main/res/layout/ime_view.xml` and
   `VoiceImeService.kt`. Floating mic: `FloatingMicService.kt`. Screens are built in code
   (`Page.kt`). Search `android/docs/maintaining.md` for the control: most of the layout exists
   because of an earlier request. Today's request overrides it; say so in the doc.
4. **Measure, don't estimate.** With a phone on adb, read real sizes instead of working from the
   screenshot's pixels:

   ```bash
   adb shell wm size; adb shell wm density        # dp = px / (density / 160)
   adb shell dumpsys window | grep 'type=navigationBars' | head -1
   adb shell cmd overlay list | grep navbar       # [x] marks the navigation mode
   ```

   Write a height budget for the layout, before and after, into the `maintaining.md` section.
5. **Change it, and compile.**

   ```bash
   cd android
   JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 ./gradlew --offline -q \
     :app:testFdroidDebugUnitTest --tests '*YourTest'
   ```

   That compiles and links resources without the native build. Don't run `assembleDebug` or a
   release build on a small machine: sherpa-onnx builds from source. Put logic in a plain function
   with a unit test in `android/app/src/test`. Colours come from the brand tokens, not new ones.
6. **Record it, push.** In one commit: a dated section in `android/docs/maintaining.md` with the
   user's words, cause, sizes and what is verified; a row in `planning/requests.md` and
   `planning/backlog.md`. Don't commit a screenshot from a real app to this public repo unless it
   shows nothing personal: a shot taken over an email or chat holds someone's message.
7. **Try it on the phone before releasing.** `workflow_dispatch` on `android.yml` builds a signed
   APK and publishes nothing: no GitHub release, no CDN, no F-Droid.

   ```bash
   gh workflow run android -R Hebrish-ASR/Hebrish-App --ref main
   gh run watch <id> -R Hebrish-ASR/Hebrish-App --interval 60
   gh run download <id> -R Hebrish-ASR/Hebrish-App -n apk -D <empty folder off tmpfs>
   adb install -r <folder>/Hebrish-main.apk
   ```

   It takes the signature of a release, so `-r` keeps the app's data and the selected keyboard. Ask
   before installing on someone's phone: it restarts the keyboard. Never uninstall to get past
   a signature error, because that deletes the models and history. Versions stay the same until a
   real bump, so say which build the phone now runs.
8. **Verify on the device.** Open a blank text field, never one in a message or a form with
   someone's content. For a keyboard change, `adb exec-out screencap -p > shot.png` and
   `adb shell uiautomator dump /sdcard/ui.xml` give the real picture and bounds. Check each state
   the change touches: for the keyboard, idle and recording, three-button and gesture navigation
   if you can. Move the item in "Not yet verified" or mark what you saw, with the Android version.
9. **Report** what changed, what was seen on the device and what was not. A release has an
   audience, so offer it and wait for a yes, then use `android-release`. Name any larger idea from
   the shot in one line and leave it unbuilt.

## Gotchas

- Wireless debugging drops and changes port. If `adb devices` is empty, pair with a QR code: render
  `WIFI:T:ADB;S:<name>;P:<6 digits>;;` with `qrencode`, have the phone scan it under Wireless
  debugging, then find the ports with `nmap -Pn -p 30000-49999 --open <phone>`: `adb pair` on the
  new port, `adb connect` on the one that answers. mDNS may find nothing.
- Never send `adb shell input` taps without a fresh screenshot and a check of `mCurrentFocus`. The
  user may be using the phone, and a tap meant for a key lands on whatever is open. A locked phone
  captures as a black image: `isKeyguardShowing` tells you.
- `gh run download -D .` fails with "would result in path traversal": give it a full path.

- `targetSdk` 35+ makes every window edge to edge, the IME included, so anything at the bottom of a
  view needs the `navigationBars` inset. Keys under the bar are this, not a height problem.
- Keep the keyboard one height in every state, and no taller than it was unless the user agrees.
