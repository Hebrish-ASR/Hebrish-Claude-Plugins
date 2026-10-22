# hebrish.app page rules

The rules every change to <https://hebrish.app> follows. They come from the website repository's own
agent instructions and README (as of 2026-10-22). The site is plain static HTML and CSS, deployed on
push to `main`; there is no build step and no framework. Pages are served without `.html`
(`model.html` is `/model`).

## 1. Every claim matches its source

- Every number and link on a page is copied from a source. Do not round results, do not invent
  benchmark numbers, and quote the comparison with the number ("5.3% vs 10.9% stock", not "half the
  errors").
- A result that has not been measured is written "not benchmarked yet". PoC-4 and PoC-5 are
  unbenchmarked.
- Targets (the goals in `data/results.json`) are goals: never show them as results.
- Results measured on different test-set revisions are not ranked against each other. In particular,
  do not rank Sabich-Qwen3 against Sabich.
- Speed and accuracy positions on `/models/choose` and the Sabich variants gradient are estimates; say so.
- Generated data files are never hand-edited: `data/stats.json` and `data/lexicon.json` (and
  `lexicon.csv`) come from `scripts/build_data.py`.
- The home page's side-by-side ("Same recording. Two models.") shows **verbatim** benchmark transcripts.
  Never edit or invent them.

Where to find sources: see the `check-page-claims` skill in this plugin.

## 2. Model names

| Line | What it is | Write |
| --- | --- | --- |
| **Jachnun** | The Parakeet code-switching fine-tune | "Jachnun v1.0"; later retrains v1.1, v1.2 … |
| **Sabich** | Code-switching plus tech and other recordings; the **recommended** model in the apps | "Sabich v1.0" |
| **Shakshuka** | Nemotron streaming fine-tune | "Shakshuka PoC-1", "Shakshuka PoC-2" (always prefixed), "Shakshuka v1.0" |
| **Meorav** | Text-to-speech (Qwen3-TTS fine-tune) | "Meorav PoC-1" … until "Meorav v1.0" |
| Sabich variants | Sabich recipe on other bases | `<Line>-<Base>-<Size>`: Sabich-Qwen3-ASR-1.7B, Sabich-Canary-Qwen-2.5B, Sabich-Parakeet-110M, Sabich-asr4all-S / -M |

- The first five Parakeet checkpoints are **PoC-1 … PoC-5**, with a POC badge
  (`<span class="tag poc">POC</span>`) and no food name. Never write a bare "v1"–"v5" for them; where it
  helps, add "published as v1" (`<span class="pub-as">`).
- Jachnun is the name of the model, not of a version. Never call Jachnun "main"; Sabich is recommended,
  Jachnun stays offered.
- On the home page and `/he`, write "Hebrish Jachnun v1.0" (visitors there don't know the names yet); on
  technical pages, "Jachnun v1.0".
- Sabich-asr4all: no "FUTO" in headings or marketing copy; the base model id and licence name are fine.
- Boxty is not a Hebrish model and stays off hebrish.app entirely.
- A new model version gets the next v1.x number; update `changelog.html`, `model.html` and
  `data/results.json` together (and `demo.js` `REVISION` for the browser demo).

## 3. Hebrew words

- Hebrew words are written in the canonical romanization: the `term` column of `data/terms.csv` in
  <https://github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier> (makolet, arnona, kupat holim).
- Hebrew script appears only as a reference gloss in a `<span class="he">` (set in Frank Ruhl Libre):
  the gloss line under the home side-by-side and the Hebrew spelling above a highlighted term in dataset
  sentences, plus ordinary Hebrew prose on `/he`. Never as model output.

## 4. Voice

- **One person, no organisation.** Hebrish is Daniel Rosehill's one-person project.
  Never "we", "our", "us" or a team ("Mission", not "Our mission"; "tell Daniel", not "tell us"). The
  legal "we" in the terms of use is the exception. Dated changelog entries are history: leave their
  wording.
- **Single speaker.** The models are trained on one speaker's voice. State it once, as a plain fact,
  where it matters technically (benchmark method and known limits, dataset docs, model-card limitations,
  terms, the FAQ on accents, `llms.txt`). Not in the hero, the experimental strip, home cards, every
  changelog entry or chart footers. Where more voices come up, invite recordings ("Want it to learn your
  voice? Contribute recordings") rather than warn.
- Plain, specific, measured. No hype words, no emojis. "One-person project"; never "non-profit",
  "not-for-profit" or "charity", and no statements of motive (Daniel, 2026-10-22). Full voice guide and templates: <https://hebrish.app/brand>.

## 5. Structure

- **Shared chrome is generated.** The top nav, the experimental strip, the Docs sub-bar and the footer
  are written into every page by `python3 scripts/layout.py` (lists `NAV`, `DOCS`, `FOOTER_GROUPS`,
  `EXP`, and Hebrew twins `NAV_HE`, `FOOTER_GROUPS_HE`). Edit those lists and run the script; never
  hand-edit those blocks in a page. `python3 scripts/layout.py page.html` does one page.
- Each page keeps its own SEO head (title, description, canonical, Open Graph, Twitter, JSON-LD
  `BreadcrumbList`) and its own share bar.
- **A new page** goes into `sitemap.xml`, `sitemap.html` and `llms.txt`, then:
  ```bash
  python3 scripts/add_icons.py page.html
  python3 scripts/layout.py page.html
  ```
  A new blog post also needs a card on `blog/index.html` and an item in `feed.xml`.
- **Navigation:** the top nav serves people using the app (Download, Try it, Models, Use cases, FAQ,
  Docs, Blog, About, Contact, עברית). Developer pages (model card, benchmarks, datasets, lexicon,
  integrate, stack …) live under Docs (`/docs`) and carry the Docs sub-bar. Keep heavy technical
  content off the home page and `/he`.
- **`/he` mirrors English.** `he.html` (and the Hebrew white paper) mirror their English sources: a
  number or download change goes in both. Model output stays romanized there too.
- **Downloads:** links are `/get/<platform>` (android, ubuntu, windows), which follow the release
  manifest, so an app release needs no link edit. Never put a versioned file URL on a page. Android:
  F-Droid is the recommended install, the APK second.
- **Model chooser:** `/models/choose` and the variants gradient on `/models/sabich` are driven by
  `data/variants.json` via `chooser.js`. Change models or rules in the JSON, not the JS.
- **Brand:** palette, fonts and logo come from the brand standard; `style.css` and `img/brand/` copy it.
  Don't introduce new colours in a page. See the `brand-assets` skill.
