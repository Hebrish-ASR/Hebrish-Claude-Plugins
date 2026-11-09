# CLAUDE.md

The `hebrish` Claude Code marketplace (Hebrish-ASR/Hebrish-Claude-Plugins). **Public.** Read
[AUTHORING.md](AUTHORING.md) before adding a skill.

- It lists one plugin, `hebrish-setup`, which is not in this repo: the marketplace points at
  Hebrish-ASR/Hebrish-Agent-Skills (`strict: false`, skills listed in `marketplace.json`). Edit
  those skills there, then bump its `version` in `.claude-plugin/marketplace.json` and run
  `claude plugin validate .`.
- **`hebrish-maintainers` was deleted on 2026-11-09** (Daniel: two plugins in parallel was too
  risky). Every one of its skills moved to the private plugin `hebrish-private`
  (`danielrosehill/Hebrish-Private-Plugin`). Do not re-create a maintainer plugin here; new
  maintainer skills go in the private plugin.
