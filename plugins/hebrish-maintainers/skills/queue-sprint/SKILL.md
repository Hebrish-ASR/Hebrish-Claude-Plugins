---
name: queue-sprint
description: Queue a batch of Hebrish app feature requests, fixes and ideas into the per-platform sprints in planning/backlog.md of Hebrish-ASR/Hebrish-App (desktop = Ubuntu + Windows; Android), logging each in planning/requests.md and adding parity follow-ups. Use when several asks arrive at once ("queue this for the sprint", "add these to the Android sprint", "for the next Ubuntu version…", "the other thing I'd queue is…"), often in the middle of other work, and they should be recorded rather than built right now.
---

# Queue a batch into the sprints

## Access

- **Anyone** can make the edits in a clone of the public
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) repository.
- **Push access to Hebrish-App** is needed to commit straight to `main`. **Fallback for everyone
  else:** open a GitHub issue per ask on Hebrish-App (the public route for requests), or commit
  the `planning/` edits on a branch of your fork and open a pull request. Which sprint an item
  goes into and in what order is the maintainer's call; a contributor's pull request proposes it.

Requests often arrive in batches, mid-task, dictated, and spanning several platforms. The job is
to record every one faithfully and put it in the right place. It is **not** to build it, unless
the person says to. Keep working on the current task afterwards.

`planning/` is public: follow the hygiene rules in the `log-decision` skill (no private details;
users unnamed unless they ask for credit). `planning/README.md` explains the files and status words.

## 1. Split the batch

Break the message into separate asks. One ask is one thing that could ship on its own. For each,
note:
- **Platform(s):** desktop (Ubuntu + Windows, shared code in `desktop/`), Android, or all. "The
  Ubuntu app" means desktop; Windows comes with it.
- **Kind:** feature, fix, design, or idea (wanted but explicitly "for later").
- **The ask in one line**, in plain words. Keep the person's specifics: numbers, defaults, names,
  and "default should be…" details. Don't round them off or reinterpret them. If a dictated phrase
  is ambiguous, write the most likely reading and flag it in your reply.

## 2. Log the requests

`planning/requests.md`: one row per ask, newest at the top, id `R-<YYYY-MM-DD>-<n>` continuing
that day's numbers. "From" is `Daniel` (the maintainer), `user`, or an issue link.

## 3. Place each one

`planning/backlog.md`:
- Into **Sprint: desktop** or **Sprint: Android** with a new `B-<n>` id (continuing the highest
  number in the file), status `planned`. An "all platforms" ask gets an item in each sprint.
- Explicitly later, or too big or risky for now → **Ideas for future versions** (`I-<n>`).
- Already in the backlog → don't duplicate: add the new request id to the existing item, and any
  new detail.
- **Parity:** when an item lands on one platform, check whether the other sprint needs a matching
  item (`docs/feature-parity.json` is the matrix; parity is decision D-2026-10-22-05). Add it, and
  mark it "(parity with B-…)".
- Order inside a sprint: what was asked first or what blocks others, then the rest. The release
  item stays last.

Link each request's Outcome to its backlog anchor (for example
`[B-9](backlog.md#sprint-android)`). Update "Last updated".

## 4. Decisions

If the batch settles a choice (a default, a scope call, "for later"), log it with the
`log-decision` skill.

## 5. Commit and report

Stage only `planning/` and commit in one command (other sessions may be committing in the same
working tree): `planning: queue R-… into the sprints`. Push, or open a pull request (see Access).
In the reply, list what went where in a few lines, and anything you interpreted.

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *queue-sprint*, for the maintainer setup.
