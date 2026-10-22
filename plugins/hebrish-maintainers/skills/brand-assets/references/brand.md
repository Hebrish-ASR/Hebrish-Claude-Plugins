# Hebrish brand reference

Public facts about the Hebrish look, as served on <https://hebrish.app> (`/style.css`, `/img/brand/`,
`/img/<model>/`) and described on <https://hebrish.app/brand>. Values checked against the live
`style.css` on 2026-10-22. If the live site and this file disagree, the live site wins: re-read
`https://hebrish.app/style.css` (the `:root` block and its `prefers-color-scheme: dark` twin).

## Colour tokens

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `bg` | `#fbf8f2` | `#111615` | Page background (warm paper) |
| `surface` | `#ffffff` | `#18201e` | Cards |
| `band` | `#f1ece1` | `#151c1a` | Alternate sections |
| `ink` | `#1d2422` | `#e8ece9` | Text |
| `muted` | `#5b6662` | `#9aa7a2` | Secondary text |
| `line` | `#e2dccf` | `#2a3532` | Borders |
| `accent` | `#0f6b5c` | `#3fbf9f` | Primary green: links, primary buttons, the brand |
| `accent-ink` | `#ffffff` | `#0c1412` | Text on an accent fill |
| `accent-soft` | `#d8efe7` | `#163a31` | Tag and highlight backgrounds |
| `warn-soft` | `#fbe3d9` | `#3a2018` | POC / experimental tag background, error highlights |
| `warn-ink` | `#9a3412` | `#f4a582` | POC tag text; also the outline colour of the model marks |
| `gold` | `#c8901c` | `#e0b14a` | Highlight, sparingly |

The accent green on paper is the brand. Gold is an accent of the accent: **one** gold mark,
underline or badge per surface, never a fill (model food marks are the exception: they are golden
food). Warn colours only for errors and POC labels.

## Fonts (all OFL, Google Fonts)

| Role | Family | Weights |
| --- | --- | --- |
| Display, headings, logo | Fraunces | 600, 700 |
| Body | Inter | 400, 500, 600 |
| Hebrew in running text (glosses) | Frank Ruhl Libre | 500, 700 |
| Hebrew in the logo lockup (עבריש) | Noto Sans Hebrew | 500 |

Google Fonts URL used by the site:
`https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600&family=Frank+Ruhl+Libre:wght@500;700&display=swap`

## Name and lines

- **Hebrish**, capital H, in prose. Hebrew name עבריש (only in the logo lockup).
- Tagline (short form): "Dictation that gets the Hebrew words right."
- GitHub organisation `Hebrish-ASR`; Hugging Face organisation `Hebrish`.

## Marks

| Mark | Public file |
| --- | --- |
| Org mark: a serif **H** in paper colour on a rounded green square (radius 14/64) | `https://hebrish.app/img/brand/mark.svg`, `mark-dark.svg`, `mark-256.png` |
| Wordmark (mark + "Hebrish" + עבריש; light backgrounds only) | `https://hebrish.app/img/brand/wordmark.svg`, `wordmark-1080.png` |
| Org avatar (square, unrounded; platforms crop it) | `https://hebrish.app/img/brand/avatar-500.png` |
| Jachnun (rolled golden pastry with a spiral end) | `https://hebrish.app/img/jachnun/jachnun.svg`, `jachnun-512.png` |
| Sabich (pita with eggplant, egg, parsley, tahini) | `https://hebrish.app/img/sabich/sabich.svg`, `sabich-512.png` |
| Shakshuka (copper pan, two eggs, steam = streaming) | `https://hebrish.app/img/shakshuka/shakshuka.svg`, `shakshuka-512.png` |
| Meorav (plate of Jerusalem mixed grill, onion, pita wedge) | `https://hebrish.app/img/meorav/meorav.svg`, `meorav-512.png` |

Don't recolour the org mark outside the two token sets, stretch it, outline it or add effects. Leave
clear space of at least a quarter of its width. The H (the project) and a food mark (one model line)
never merge.

### Rules for a model food mark

Every model line is named after an Israeli food and gets a mark that sits in the set:

- `viewBox="0 0 64 64"`, transparent background, the food filling about 52 of the 64 px.
- Outline `#9a3412` at 2.2–2.4; inner detail 1.2–1.6; `stroke-linecap` and `stroke-linejoin` round.
  No gradients, filters, shadows or text.
- Colours only from the mark palette: gold `#c8901c` / `#e0b14a`, crust `#9a3412`, soft `#f4a582`,
  paper `#fbf8f2`, one green `#0f6b5c` garnish. No pure black or white: the mark must work on both
  `#fbf8f2` and `#111615`.
- A slight tilt or diagonal element (Jachnun −24°, Sabich −22°, Shakshuka's handle about 40°,
  Meorav −14°), so the set looks hand-placed rather than clip art.
- A `<title>` and an XML comment naming the date and each colour's token.

## Illustration style

- Flat vector cartoon, outlines in crust brown `#9a3412` or ink, warm paper `#fbf8f2` ground, the food
  mascots as friendly characters. Playful, never slapstick about Israel or Hebrew.
- The joke: a stock model's mishearing against the right romanized word. Use real ones from the home
  page's side-by-side (Micollette → *makolet*, TOFS → *tofes*, Mem Shalah → *memshala*) rather than
  invented ones.
- Text in images: 1–4 words, romanized spellings from the canonical term list
  (`data/terms.csv` in <https://github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier>). No Hebrew
  script (generators garble it), no benchmark numbers, no slogans, no emojis.
- Words that work on banners: makolet, arnona, teudat zehut, Bituach Leumi, kupat holim,
  Motzei Shabbat, sabich, balagan, miluim.

## Web layout (for UI work)

`.wrap` max 1040 px with a 16 px gutter; sections 64 px vertical padding. Cards: `surface` on `bg`,
1 px `line` border, radius 14 px (feature cards 18 px). Pills (999 px) for buttons, tags and chips.
Headings Fraunces 700; body Inter 17 px / 1.6. Primary button: `accent` fill, `accent-ink` text. Tags:
`accent-soft` on `accent`; POC = `warn-soft` on `warn-ink`. Model marks 40 px inline, 64–72 px on hero
cards, never cropped or circled. Motion small and behind `prefers-reduced-motion`.

## Asset checklist

1. Colours are token values; the piece works on its background (check dark too).
2. Fonts are the four above, or text is converted to paths.
3. Names are right: Hebrish, Jachnun, Sabich, Shakshuka, Meorav; checkpoints written PoC-N with the
   line prefix where needed (Shakshuka PoC-2); never a bare "v1"–"v5".
4. Hebrew words romanized; Hebrew script only as a gloss (and עבריש in the lockup).
5. No numbers on promotional art; no single-speaker caveat on promotional art.
6. One gold mark per surface (model marks excepted).
7. Source file and how it was made are recorded (for generated art: model, prompt, seed, date).
