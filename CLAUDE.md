# CLAUDE.md

The `hebrish` Claude Code marketplace (Hebrish-ASR/Hebrish-Claude-Plugins). **Public.** Read
[AUTHORING.md](AUTHORING.md) before adding or editing a skill. It has the no-private-details
rule, the Access tiers and where maintainer-only specifics go: the private Hebrish-ASR/Hebrish-Mgmt
repository, `docs/maintainer-agent-notes.md`.

- After a change, bump `version` in the plugin's `plugin.json` and in
  `.claude-plugin/marketplace.json`, then run `claude plugin validate .`.
- `hebrish-setup` is not in this repo: the marketplace points at Hebrish-ASR/Hebrish-Agent-Skills
  (`strict: false`, skills listed in `marketplace.json`). Edit those skills there.
- The skills started as Daniel's private skills (2026-10-22) and are the only copies now. Don't
  fork a skill back into a private plugin; put maintainer specifics in the notes file instead.
