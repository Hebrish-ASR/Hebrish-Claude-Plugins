---
name: archive-screenshots
description: Keep replaced Hebrish screenshots: archive old app images to old-screenshots when the site or manual gets a new one, never delete.
---

# Archive old screenshots

When a new screenshot replaces an old one on hebrish.app or in the user manual, the old image is
kept, not deleted, in case it is needed later (Daniel, 2026-11-06). Use it on "archive the old
screenshot", "keep the old one", or as part of any change that replaces a screenshot, including
`website-change` and a manual update.

## Access

- **Maintainer access:** the website's private repository (`danielrosehill/Hebrish-Website`).
- **Fallback for everyone else:** attach the new image to an issue on
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) and say what it replaces.

## Where things go

`old-screenshots/<app>-<version>/<name>` at the website repo root, where `<version>` is the app
version the image shows. `old-screenshots/README.md` is the index. `.vercelignore` skips the folder,
so it never deploys, and nothing on the site may link to it.

## Steps

1. **Archive before you overwrite.** Run this before regenerating a file in place, such as
   `manual-src/docs/img/desktop/*.png`: once the file is overwritten, only git has the old one.

   ```bash
   mkdir -p old-screenshots/desktop-1.022
   cp manual-src/docs/img/desktop/voice-typing.png old-screenshots/desktop-1.022/
   ```

2. **Move or copy.** Images in a versioned folder, such as `img/screenshots/android-1.012/`: `git mv`
   once no page uses them, or copy while a page still does. Find the uses first:

   ```bash
   grep -rIl 'android-1.012/sound-microphone' --include=*.html --include=*.md . | grep -v '^./manual/'
   ```

   Take the `-480` thumbnail along with the full size.
3. **Add a row** to `old-screenshots/README.md`: image, what it shows, date taken
   (`git log -1 --format=%ad --date=short -- <path>`), what replaced it, today's date.
4. **Check for private content** if the source is a real capture. A "before" taken over an email or
   chat is cropped to the app's own UI first, and the full image stays out of the repo.
5. **Commit it with the change** that replaced the image, staging named paths.

New images go in `img/screenshots/<app>-<version>/` as `<name>.webp` and `<name>-480.webp`
(`cwebp -q 78 -m 6`, then `cwebp -q 72 -m 6 -resize 480 0`). A keyboard crop: find the top edge from
the pixel column, then `convert <shot> -crop <width>x<height>+0+<top> +repage`.
