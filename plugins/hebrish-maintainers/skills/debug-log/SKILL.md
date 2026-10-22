---
name: debug-log
description: Record a diagnosed bug in the Hebrish debug log, docs/debug-log/ in Hebrish-ASR/Hebrish-App — one file per bug with symptom, cause, how it was found, what was ruled out, the fix and what is verified — and leave the lasting rule in the platform's maintaining.md. Use after diagnosing or fixing a bug in the apps, the website or the models (whether or not a fix shipped), when asked to "log this bug", "write up the debugging", "add it to the debug log", or when an investigation turned up something the next person would otherwise rediscover.
---

# Write a debug-log entry

The debug log keeps the expensive half of a fix: what was wrong, how it was found, and the
plausible causes that turned out not to be it. The diff only holds the cheap half. The format
and the index are defined in the repository's own
[`docs/debug-log/README.md`](https://github.com/Hebrish-ASR/Hebrish-App/blob/main/docs/debug-log/README.md).
Read it first; if it disagrees with this skill, the README wins.

## Access

- **Anyone** can write an entry in a clone of the public
  [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App) repository.
- **Push access** is needed to commit to `main`. **Without it:** commit on a branch of your fork
  and open a pull request, or paste the entry into an issue titled `Debug log: <symptom>`.

## 1. Is it worth an entry?

Write one if finding the cause took more than reading the obvious line: a protocol trace, a
measurement, a hypothesis ruled out, a value that looked authoritative and wasn't, an
environment-specific behaviour. An unresolved investigation is worth an entry too, with
`status: unfixed`, because it stops the next person from repeating the same steps. Skip typos
and one-line fixes whose cause is plain from the diff.

## 2. Gather before writing

While the session is still open, collect:

- the **symptom in the reporter's own words** (quote them) and the environment: OS and version,
  desktop or compositor and version, app version, model, the relevant package versions
  (`dpkg-query -W <pkg>`, `adb shell getprop ro.build.version.release`, …);
- the **commands that showed the cause**, with the lines of output that matter. Trim, don't
  paraphrase;
- every **hypothesis ruled out** and the evidence that ruled it out;
- the **fix** as commit hash, tag and file/function names;
- what you **verified** (V) and what you only **inferred** (I). Anything the reporter still has to
  confirm by eye or ear goes under (I) with "awaiting confirmation".

## 3. Write the entry

File `docs/debug-log/YYYY-MM-DD-<short-slug>.md`, dated the day the bug was diagnosed. Use the
front matter (`date`, `platform`, `environment`, `component`, `affected`, `fixed_in`, `status`)
and the sections in the README's format: Symptom, Cause, How it was found, Ruled out, Fix,
Verified / not verified, Related. Number the steps under "How it was found" in the order they
narrowed the cause; that order is what the next reader reuses.

Then add a row to the **Index** table in `docs/debug-log/README.md` (newest first).

## 4. Put the lasting rule where it belongs

- The rule the fix leaves behind ("use X only where Y, because Z") goes in
  `desktop/docs/maintaining.md` or `android/docs/maintaining.md`: a short section or table row
  that links the entry. Don't copy the story there.
- Fix any statement the bug proved wrong, including rows marked (V) that went stale.
- If fixing it meant choosing a behaviour, also log a decision (`log-decision` skill).
- Point the test module that covers the fix at the entry in its docstring.

## 5. Public-repo hygiene (every time)

The repository is public and read by strangers and agents opening it cold.

- No personal names except "Daniel" (the maintainer); a user is "a user" unless they asked to be
  credited. No host names, IPs, account ids, internal URLs, or contents of private repositories.
- No credentials or tokens, including in pasted command output. Redact `/home/<user>` paths to `~`.
- Absolute dates. No "we": Hebrish is a one-person project.

## 6. Commit

Stage only your files and commit in one command, because other sessions may be committing in the
same working tree:

```bash
git add docs/debug-log/<entry>.md docs/debug-log/README.md desktop/docs/maintaining.md \
  && git commit -m "docs/debug-log: <symptom> (<version>)" -- docs/debug-log desktop/docs/maintaining.md
```

Push, or open a pull request (see Access). Ship the entry with the fix commit, or straight after
it; don't leave it for later.

Worked example: [`2026-10-22-paste-flicker-kde.md`](https://github.com/Hebrish-ASR/Hebrish-App/blob/main/docs/debug-log/2026-10-22-paste-flicker-kde.md)
(a protocol trace with `WAYLAND_DEBUG=1`, one stale "(V)" row, and a fix that probes for a
capability instead of guessing it from the desktop's name).
