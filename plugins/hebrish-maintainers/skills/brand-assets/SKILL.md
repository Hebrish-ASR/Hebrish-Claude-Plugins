---
name: brand-assets
description: Make on-brand Hebrish assets - model food marks (SVG), banners and cartoon illustrations for Hugging Face model cards, GitHub, social posts and blog headers, card images, or brand colours and fonts for a UI change. Use when asked for a Hebrish logo, mark, icon, banner, illustration, social image or "something for Hugging Face".
---

# Hebrish brand assets

## Access

- **Anyone:** everything here works from public material. The palette, fonts and marks are served by
  <https://hebrish.app> (`/style.css`, `/img/brand/`, `/img/<model>/`) and summarised in
  [`references/brand.md`](references/brand.md). Hand finished work in by opening an issue on
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues) titled
  `Brand: <what it is>`, attaching the PNG/SVG and the provenance (step 5).
- **Maintainer access:** placing an asset in the project's private brand repository, on the website,
  on the project CDN or on the Hugging Face organisation needs write access to those. If you have
  access to the private Hebrish-ASR/Hebrish-Mgmt repository, read `docs/maintainer-agent-notes.md`,
  section *brand-assets*, for the maintainer setup.

Read `references/brand.md` before making anything. It is the rules; this file is the procedure.

## 1. Decide what kind of asset it is

| Asset | Make it as |
| --- | --- |
| Org mark, wordmark, avatar | Don't redraw. Use the files at `https://hebrish.app/img/brand/`. |
| Model food mark (a new model line) | Hand-written 64×64 SVG (step 2) |
| Banner, cartoon, social or blog illustration | Generated with an image model, then cropped (step 3) |
| Web or app UI (cards, sections) | Token colours and the layout rules in `references/brand.md` |

Vector beats generated whenever the asset is small, repeated or must match exactly (marks, icons).
Generate only illustrations.

## 2. Model food marks (SVG)

1. Download an existing mark as a template, for example
   `curl -sO https://hebrish.app/img/sabich/sabich.svg`, and copy its structure: `<title>`, a comment
   with the date and each colour's token, round caps and joins, outline `#9a3412` at 2.2–2.4.
2. Draw the new food within the mark rules in `references/brand.md` (palette, tilt, no text).
3. Render: `inkscape <name>.svg -w 512 -h 512 -o <name>-512.png` (or `rsvg-convert -w 512 -h 512`).
4. Check it beside the existing marks on light **and** dark, for example with ImageMagick:
   ```bash
   magick -size 1100x420 xc:'#fbf8f2' \( jachnun-512.png -resize 160x160 \) -geometry +40+40 -composite \
     \( <name>-512.png -resize 160x160 \) -geometry +240+40 -composite \
     -fill '#111615' -draw 'rectangle 0,220 1100,420' \
     \( <name>-512.png -resize 160x160 \) -geometry +240+240 -composite sheet.png
   ```
   Then view `sheet.png`. The mark must read at 40 px and must not vanish on `#111615`.

## 3. Generated illustrations

Use an image model you have access to. These points held on 2026-10-21 for the models tried; treat them
as things to check, not guarantees:

- **Prompt pattern:** "flat vector cartoon, outlines in `#9a3412`, background `#fbf8f2`", list the
  palette hexes and say "palette only", then "no Hebrew letters, no other text", then name every word
  exactly: "exactly two words: Micollette in grey with a red line struck through it, an arrow, and
  makolet in bold dark green `#0f6b5c` with a gold underline". Models still add small labels on signs
  and machines, so check them.
- **Margins:** say "keep all content inside the middle 70% of the image height … no border lines, no
  frame, no panel". Asking for "empty bands" tends to produce drawn rules.
- **Size:** many tools take only a size preset (`landscape_16_9`, `square`), and a 16:9 preset can come
  back wider than 16:9. Crop or pad to the target yourself. Hugging Face and similar banners: 3:1,
  1500×500.
- **Background:** generated paper drifts a few levels off `#fbf8f2`, which shows as a faint box when the
  image sits on the site. Flatten near-paper pixels:
  `magick in.png -fuzz 2.5% -fill '#fbf8f2' -opaque '#fbf8f2' out.png`.
- **Seeds:** pass a `seed` explicitly and record it; some tools return only a URL, so without your own
  seed the image can't be reproduced.
- **Jokes:** real stock-model mishearings from the hebrish.app home page side-by-side (Micollette →
  *makolet*, TOFS → *tofes*, Mem Shalah → *memshala*), spellings from the canonical term list.
- **Check every image yourself** (open the PNG): spelling, no Hebrew-script gibberish, no extra limbs,
  palette close, nothing that misreads at icon size (steam drawn as a "?" reads as confusion; ask for
  "straight wavy steam lines").
- Keep cost small: a few images per round, rejects discarded.

For the web: WebP at 1500 and 750 wide (`cwebp -q 82 -m 6`) is what hebrish.app serves.

## 4. Images on Hugging Face model cards

The main Hebrish model repositories are gated, so a card image stored in the repo and referenced by a
relative path (`figures/banner.png`) returns 401 to logged-out visitors. Reference a public absolute URL
instead: the marks at `https://hebrish.app/img/<slug>/<slug>-512.png`, illustrations at their hosted
URL. Check a link with
`curl -s -o /dev/null -w '%{http_code}' <url>` (expect 200, logged out). Never rename or delete a hosted
image: model cards load them by URL.

## 5. Before it ships

Run the asset checklist at the end of `references/brand.md`. Record provenance next to the file or in
the issue: for a mark, the SVG and render command; for generated art, the model, exact prompt, seed,
raw and final size, post-processing and date.
