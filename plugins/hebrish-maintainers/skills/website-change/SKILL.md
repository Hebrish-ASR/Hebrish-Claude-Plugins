---
name: website-change
description: Propose or make a change to hebrish.app (text, a number, a new page, nav or footer) following the site's page rules - claims match their source, no rounding or invented benchmark numbers, model names (Jachnun, Sabich, Shakshuka, Meorav, PoC-N), romanized Hebrew, first-person voice (I, never we), generated nav/footer, /he mirroring. Use when asked to fix, update, add or suggest something on the Hebrish website.
---

# Change hebrish.app

## Access

- **Anyone:** the website's repository is private, so you draft the change and open an issue on
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues) titled
  `Website: <short summary>` with the page URL, the current text, the proposed text (or a diff against
  the live HTML), and the source for every number or claim. Daniel applies it.
- **Maintainer access:** write access to the website's private repository. Edit, run the scripts below,
  commit and push to `main` (the host deploys on push; there is no build step and no CLI deploy). If you
  have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
  `docs/maintainer-agent-notes.md`, section *website-change*, for the maintainer setup.

Read [`references/page-rules.md`](references/page-rules.md) first. Every step below assumes it.

## 1. Pin down the change

1. Fetch the live page: `curl -s https://hebrish.app/<page>` (pages are served without `.html`; the
   home page is `/`, Hebrew home `/he`, model pages `/models/<slug>`).
2. Find the exact element to change. If the change touches the nav, the experimental strip, the Docs
   sub-bar or the footer, it is a change to `scripts/layout.py`, not to the page.
3. List every other place the same fact appears. Common pairs:
   - English page ↔ `/he` (`he.html`) for anything on the home page; numbers and downloads always.
   - A model fact ↔ `/models`, `/models/<slug>`, `/model`, `/faq`, `/docs`, `llms.txt`, `data/models.json`.
   - A result ↔ `data/results.json` ↔ the page tables ↔ `changelog.html`.
   Search the live site for the old wording: `curl -s https://hebrish.app/llms.txt` lists every page.

## 2. Check the content against the rules

For each sentence you add or change:

- **Number or result?** Find its source and copy it exactly (use the `check-page-claims` skill). Not
  measured → "not benchmarked yet". Different test-set revisions → no ranking.
- **Model name?** Jachnun v1.0, Sabich v1.0, Shakshuka PoC-N, Meorav PoC-N, PoC-1…PoC-5 with the POC
  badge; never a bare v1–v5; Sabich is recommended, Jachnun is not "main"; no Boxty.
- **Hebrew word?** The romanized spelling from the canonical `terms.csv`; Hebrew script only as a
  `<span class="he">` gloss.
- **Voice?** Daniel, not "we"; single-speaker training stated once and only where technical; no hype.
- **Download link?** `/get/<platform>`, never a versioned file.

## 3a. Anyone: open the issue

Write the issue body like this, then open it on the web or with
`gh issue create -R Hebrish-ASR/Hebrish-App --title "Website: ..." --body-file issue.md`:

```markdown
**Page:** https://hebrish.app/<page> (and /he if it mirrors)
**Current:** "<exact current text>"
**Proposed:** "<exact new text>"   (or a ```diff block against the live HTML)
**Source:** <URL of the model card / results file / benchmark JSON, with revision or date>
**Also affects:** <other pages from step 1.3, or "none found">
```

One issue per independent change. Don't send it as the project or claim Daniel approved it.

## 3b. Maintainer: make the edit

1. Edit the page HTML directly; mirror in `he.html` where step 1 says so.
2. Nav, strip, Docs bar or footer: edit the lists in `scripts/layout.py`, then `python3 scripts/layout.py`.
3. New page: copy the head and layout of a sibling page, give it its own title, description, canonical,
   Open Graph tags, JSON-LD breadcrumb and share-bar URL; add it to `sitemap.xml`, `sitemap.html` and
   `llms.txt`; run `python3 scripts/add_icons.py page.html` then `python3 scripts/layout.py page.html`.
   Blog post: also `blog/index.html` and `feed.xml`.
4. New model version or app release: `changelog.html`, `model.html` and `data/results.json` together.
5. Don't run a local build and don't hand-edit `data/stats.json` or `data/lexicon.json`.
6. Stage the named files and commit in one command (other sessions may share the working tree), push to
   `main`, then fetch the live page and confirm the new text is there.

## Done when

The live page (maintainer) or the issue (anyone) shows the exact new text, every number in it has a
named source, and every mirrored page is covered.
