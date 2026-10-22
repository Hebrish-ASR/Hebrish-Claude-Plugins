---
name: log-decision
description: Record a decision about the Hebrish apps in the public decision log, planning/decisions.md in Hebrish-ASR/Hebrish-App, and keep planning/requests.md and planning/backlog.md consistent with it. Use when the maintainer or a contributor settles a default, a trade-off, a scope call or a "not this way", when asked to "log that decision", "note that we decided" or "put that in the decision log", or when implementing something on a choice someone made that a future reader would otherwise have to guess.
---

# Log a decision

## Access

- **Anyone** can write the entry in a clone of the public
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) repository.
- **Push access to Hebrish-App** is needed to commit straight to `main`. **Fallback for everyone
  else:** commit on a branch of your fork and open a pull request. A contributor logs only
  decisions that are theirs to make (an implementation choice in their own pull request) or that
  the maintainer stated in public (an issue or PR comment, linked from the entry). A product
  decision on the project's behalf is the maintainer's: propose it in an issue instead.

`planning/` is public (see the repo's `CLAUDE.md` and `planning/README.md`). Everything written
there is read by strangers and by agents opening the repo cold.

## 1. Is it a decision?

Log it if a future reader would ask "why is it like this?": a default value, a naming choice, a
feature scoped in or out, an approach chosen over another, a reversal. Don't log routine
implementation detail; that goes in `desktop/docs/maintaining.md` or `android/docs/maintaining.md`.

## 2. Write the entry

Insert it at the **top** of the entries in `planning/decisions.md` (newest first, below the
header and the `---`). Id: `D-<YYYY-MM-DD>-<nn>`, where `nn` continues that day's highest number
(two digits). Never renumber or delete an entry. A reversal is a new entry that says
`Supersedes D-…`, and the old entry gets one line added: `Superseded by D-…`.

```markdown
### D-2026-10-22-07: <the decision as a short statement>

- **Decision:** what was chosen, with the concrete identifiers (config keys, file paths, values).
- **Why:** the reason, including the constraint that settled it.
- **Alternatives:** what was considered and not chosen, and why. Omit if there were none.
- **By:** Daniel | <contributor handle, if they want credit> | agent (implementing D-…).
  Links: request R-…, backlog B-…/I-…, commit, tag, issue or PR.
```

Who decided matters. "Daniel" (the maintainer) only for what he actually chose. A detail you chose
while implementing someone's decision is `agent, implementing D-…`.

## 3. Keep the other files consistent

- The request that led to it (`planning/requests.md`): set its Outcome to the backlog item.
- The backlog item (`planning/backlog.md`): link the decision id. Move it between the sprints and
  *Ideas for future versions* if the decision changed its schedule, and update "Last updated".
- If the decision is about platform parity, check that `docs/feature-parity.json` still agrees.

## 4. Public-repo hygiene (every time)

- No private names, emails, phone numbers, machine or host names, account ids, internal URLs, or
  the contents of private repositories. A user is "user" unless they asked to be credited.
- No credentials, ever, and no paraphrases of private notes.
- Write plainly: absolute dates; no "we" or "our team" (Hebrish is a one-person project: "Daniel
  decided").

## 5. Commit

Commit the `planning/` change on its own, or alongside the code change it explains, with a message
like `planning: D-2026-10-22-07 <short>`. Stage only your files and commit in one command
(`git add planning/decisions.md … && git commit -m …`), because other sessions may be committing
in the same working tree. Push, or open a pull request (see Access).

If you have access to the private Hebrish-ASR/Hebrish-Mgmt repository, read
`docs/maintainer-agent-notes.md`, section *log-decision*, for the maintainer setup.
