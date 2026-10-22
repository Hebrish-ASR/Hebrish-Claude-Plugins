---
name: project-context
description: Read or update the Hebrish project context, the public context memory for agents at hebrish.app/project-context/ (what Hebrish is, model lines and data, product principles, work outside the apps, project decisions, open questions), and know where the rest lives (app sprints and decisions in planning/ of Hebrish-ASR/Hebrish-App, voice-note sources in planning/voice-notes/). Use before planning or designing any Hebrish work ("what's the context", "what did Daniel say about X", "is this decided"), and when a source (a voice note, a discussion, a settled question) should change the context ("update the project context", "add that to the context", "mark that task done").
---

# Read and update the project context

## Access

- **Reading: anyone.** The context is public at <https://hebrish.app/project-context/README.md>
  (plain Markdown files). The sources and app planning are public on GitHub in
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) `planning/`.
- **Updating: maintainer access**, meaning write access to the website's private repository,
  where `project-context/` lives. **Fallback for everyone else:** open an issue on
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App/issues) titled
  `Context: <short summary>` with the file, the current text, the proposed text and the source
  (a voice note with timestamp, an issue, a commit). Daniel applies it.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *project-context*, for the maintainer setup.

## Where things live (one home per fact)

| What | Where |
| --- | --- |
| What Hebrish is, why, principles | `project-context/project.md` |
| Model lines, naming, data composition, the TTS line | `project-context/models-and-data.md` (naming authority: the website's naming rules and <https://hebrish.app/models>) |
| How the apps should behave, and why | `project-context/product.md` (links backlog ids) |
| Work outside the apps: recording app, training, website | `project-context/tasks.md` |
| Project decisions (models, data, licensing) | `project-context/decisions.md` |
| Unsettled questions | `project-context/open-questions.md` |
| App requests, sprints, ideas | Hebrish-App `planning/requests.md`, `planning/backlog.md` (skill `queue-sprint`) |
| App decisions | Hebrish-App `planning/decisions.md` (skill `log-decision`) |
| Sources: voice notes, audio and transcript | Hebrish-App `planning/voice-notes/` |

## Reading

1. Start at `README.md`; read only the file for your question.
2. Follow the citation to the source when the wording matters: citations are
   `voice note YYYY-MM-DD mm:ss`, and the transcript has timestamps in brackets.
3. A task or decision you rely on may have moved on: check the app backlog or decision log it
   links before acting on it.

## Updating

1. **Find the source.** Every addition cites one (a voice note with timestamp, an issue, a commit,
   "Daniel, YYYY-MM-DD"). No source, no entry. Never infer a decision Daniel didn't make.
2. **Pick the one home** from the table. App work goes to `planning/` via `queue-sprint` or
   `log-decision`, not here; add a link here only if a file here explains the reasoning.
3. **Edit in place.** Tasks change status (`todo`, `doing`, `done YYYY-MM-DD`,
   `dropped YYYY-MM-DD: reason`). A reversed decision is marked with the date and what replaced
   it, never deleted. A settled question leaves `open-questions.md` and becomes a decision.
4. **Keep it public-safe.** No credentials, infrastructure identifiers (bucket names, account or
   file ids, internal hosts), personal contact details, or anything the site keeps off hebrish.app.
   Website rules apply: Hebrew words in the canonical romanization, model names Jachnun, Sabich,
   Shakshuka (ASR) and Meorav (TTS) with PoC-N checkpoints, "Daniel", never "we".
5. **Dates absolute**, YYYY-MM-DD.
6. Commit only the files you changed, in one command (other sessions may be working in the same
   tree): `git add project-context/<files> && git commit -m "project-context: <what>"`, then push.
   The site deploys on push. Check the live file:
   `curl -s https://hebrish.app/project-context/<file> | head`.

## A new source

A voice note goes into Hebrish-App `planning/voice-notes/inbox/` and is processed by
`queue-sprint` (step 0): transcript filed, app asks queued. Then mine what is not app work into this
folder: project facts, model and data reasoning, product principles, tasks outside the apps,
project decisions, open questions. Each with its timestamp.
