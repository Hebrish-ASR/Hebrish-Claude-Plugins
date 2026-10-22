# hebrish-maintainers

Every Claude Code skill for working on [Hebrish](https://hebrish.app), Daniel Rosehill's
one-person, not-for-profit English-Hebrew dictation project, in one plugin.

```
/plugin marketplace add Hebrish-ASR/Hebrish-Claude-Plugins
/plugin install hebrish-maintainers@hebrish
```

Despite the name, many skills are open to anyone: each one starts with an **Access** section
saying who can use it. The app development and training-data skills work from public
repositories. The Hugging Face, release, website-repo and outreach skills need the project's
own access (or Daniel's authorisation to represent the project), and say so before doing anything.

## App development
Claude Code skills for developing the Hebrish apps: the Android voice keyboard and the Ubuntu +
Windows desktop app, in the public repository
[Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App). Run them from a clone of
that repo. Each skill opens with an **Access** section; where a step needs the project's own
accounts, it gives the route for everyone else (usually a pull request or an issue).

| Skill | What it does | Access |
| --- | --- | --- |
| `review-android-app` | Review the Android app (since the last release, or whole): build, lint, rules, docs, release state, optional adb smoke test | Anyone |
| `review-ubuntu-app` | Review the desktop app on Ubuntu: tests, off-screen self-test, build and inspect the .deb, Linux code paths, release state | Anyone |
| `review-windows-app` | Review the desktop app on Windows without a Windows machine: CI job, freeze completeness, portability, the released zip | Anyone (dispatching CI on the main repo needs write access; use a fork otherwise) |
| `check-feature-parity` | Compare Android, Ubuntu and Windows feature by feature and released vs `main`; update `docs/feature-parity.json` | Anyone (commit via pull request without push access) |
| `android-release` | Take a feedback round to a published APK: implement, document, tag, CDN, F-Droid, changelog | Maintainer for the release steps; contributors stop at a pull request |
| `log-decision` | Add an entry to the public decision log, `planning/decisions.md` | Anyone (via pull request without push access) |
| `queue-sprint` | Queue a batch of requests into the per-platform sprints in `planning/backlog.md` | Anyone (issue or pull request without push access) |

Hebrish is Daniel Rosehill's one-person, not-for-profit project (<https://hebrish.app>).

## Training data
Claude Code skills for contributing training data to [Hebrish](https://hebrish.app): new Hebrew
vocabulary and read-aloud English-Hebrew code-switching sentences, in the format the project's
sentence bank uses. Hebrish is Daniel Rosehill's one-person, not-for-profit project; he records the
sentences, so a contribution becomes training data when he reads it aloud.

| Skill | What it does | Access |
|---|---|---|
| `bank-coverage` | Measures the public sentence bank and lexicon: balance, variety, thin terms | Anyone |
| `vocab-gaps` | Finds missing or thin Hebrew vocabulary and drafts the terms | Anyone |
| `news-vocab` | Mines recent Israeli English-language news for uncovered names and terms | Anyone |
| `write-sentences` | Writes and reviews sentences with Claude subagents (no API key) | Anyone |
| `generate-synthetic` | Writes a large set with Claude Haiku 5.5 on the Batches API | Anyone with their own Anthropic API key |
| `submit-data` | Checks the contribution file and files it as an issue | Anyone (merging: maintainer) |

### Contribution flow

1. `bank-coverage` shows what the bank needs; `vocab-gaps` or `news-vocab` drafts new terms.
2. `write-sentences` (or `generate-synthetic`) writes sentences; a separate reviewer marks each one.
3. Everything goes in one JSON file (`skills/submit-data/references/contribution-format.md`).
4. `submit-data` runs `check_contribution.py` against the public data and opens an issue on
   [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues) with the file.
5. Daniel merges accepted terms and sentences into the bank; they appear in the capture app and the
   [public sentence export](https://github.com/Hebrish-ASR/English-Hebrew-Codeswitching-Parakeet-Finetune/tree/main/sentences).

Public inputs the scripts read: the sentence export above, [hebrish.app/data/lexicon.json](https://hebrish.app/data/lexicon.json)
and [terms.csv](https://github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier/blob/main/data/terms.csv).
Scripts are stdlib Python 3, except `generate_batch.py`, which needs the `anthropic` package.

## Website and brand
Skills for working on <https://hebrish.app> and the Hebrish brand. The website's repository is
private; anyone can still draft changes and hand them in as an issue on
[Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues).

| Skill | What it does | Access |
| --- | --- | --- |
| `brand-assets` | Make on-brand model food marks, banners and illustrations (Hugging Face, GitHub, social) from the public palette, fonts and marks | Anyone; placing assets on the site, CDN or HF org: maintainer |
| `website-change` | Propose or make a change to hebrish.app following the page rules (sourced claims, model names, romanization, voice, generated nav/footer, `/he` mirror) | Anyone drafts an issue; editing and pushing: maintainer |
| `check-page-claims` | Check a page's numbers, names and links against the public data files, model cards and benchmark repo, and report mismatches | Anyone (a few sources are private: maintainer) |

## Outreach (maintainer and authorised representatives only)
Skills for telling other people about [Hebrish](https://hebrish.app), Daniel Rosehill's
one-person, not-for-profit English-Hebrew dictation project.


**For the maintainer and people Daniel has authorised to represent the project only.** Each
skill asks first and stops for anyone else. Want to suggest someone the project should contact?
Open an issue titled "Outreach: <who>" on [Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App).
Sending as the project needs its own accounts (Resend for info@hebrish.app, Buttondown).

| Skill | What it does | Access |
| --- | --- | --- |
| [`outreach-email`](skills/outreach-email/SKILL.md) | Writes an email about Hebrish in the branded HTML template plus plain text (`scripts/render.py`); sends from `info@hebrish.app` via Resend (`scripts/send_resend.py`). | Maintainer / authorised: Resend API key for the hebrish.app domain to send as the project. |
| [`community-fyi`](skills/community-fyi/SKILL.md) | Drafts a short FYI post for an Israeli AI, tech or olim community, matched to the group's channel and rules. | Maintainer / authorised: drafts; you post it yourself. |
| [`newsletter`](skills/newsletter/SKILL.md) | Drafts a newsletter update (release, new model, call for recordings); checks subscribers and sends via Buttondown. | Maintainer / authorised: Buttondown API key for the Hebrish newsletter. |

Scripts are Python 3, standard library only. Paths in the skills use `${CLAUDE_PLUGIN_ROOT}`;
if it is unset, clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use
`plugins/hebrish-maintainers/` inside it. Rules for writing skills here: [`AUTHORING.md`](../../AUTHORING.md).

## Hugging Face (maintainer access)
Skills for the [Hebrish organisation on Hugging Face](https://huggingface.co/Hebrish): its collections,
model and dataset cards, and access requests to the gated repos. Changing anything there needs the
write or admin role in the org (a Hugging Face token with that access in `HF_TOKEN`). Everyone else can
run the read-only checks and report what they find as an issue on
[Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues), titled e.g.
"Hugging Face: model X missing from collection Y".

| Skill | What it does | Access |
| --- | --- | --- |
| [`hf-audit`](skills/hf-audit/SKILL.md) | One read-only health check of the whole org (`scripts/hf_audit.py`): repos in no collection, dead collection items, site model list vs collections, card rules, the access@hebrish.app address, gated repos without a form, inconsistent gating, pending request counts, line naming. Markdown report by severity, or `--json`; each finding names the sibling skill and command that fixes it. | Anyone (public checks); pending requests need an HF org write/admin token; fixes: maintainer via the sibling skills. |
| [`hf-collections`](skills/hf-collections/SKILL.md) | Keeps every model, dataset and Space in the right collections from a config file (`scripts/sync_collections.py`, dry run by default); reports repos in no collection and gaps against hebrish.app's model list. | Maintainer: HF org write/admin token to apply; anyone can run the dry run and file an issue. |
| [`model-cards`](skills/model-cards/SKILL.md) | Audits model and dataset cards for current version, naming, numbers, licence, gate form, single-speaker note and romanized Hebrew (`scripts/audit_cards.py`, read-only); edits a card with a commit message. | Anyone audits; editing: maintainer (HF org write/admin token). |
| [`access-requests`](skills/access-requests/SKILL.md) | Lists pending access requests on the gated models and datasets with their form answers; accepts or rejects only the users the maintainer names (`scripts/access_requests.py`, dry run by default). | Maintainer only: HF org write/admin token. |

## Documentation and evaluation

| Skill | What it does | Access |
| --- | --- | --- |
| `documentation` | Keeps the written record current after a release or benchmark round: the white paper (English and Hebrew), benchmark numbers on hebrish.app (`data/results.json`, `/benchmarks`, home chart, model pages), changelog/blog/model-card/benchmark-repo write-ups and the hand-off to the newsletter and community skills, and charts in the site's style from published results (`scripts/results_report.py`). | Anyone: tables, charts and drafts from public data, proposed edits as an issue on Hebrish-App. Maintainer: edits the private website repo, the white paper and HF cards. |
| `evals` | Runs and judges evaluations: the public English-Hebrew code-switching benchmark on any model, metric definitions (term recall, unseen-term recall, WER, English control), the forgetting and publish gates with a suggested verdict (`scripts/verdict.py`, refuses cross-revision comparisons), recording results, and cost discipline. | Anyone: public benchmark on own compute after an approved access request to the gated test set; result by pull request. Maintainer: held-out split runs on the project's Modal account, pinned revisions and recorded verdicts. |
