# Hebrish Claude Plugins

The Claude Code marketplace for [Hebrish](https://hebrish.app): on-device English dictation
that writes Hebrew words correctly, in romanized form (makolet, arnona, teudat zehut). Hebrish
is a one-person project by Daniel Rosehill.

## Install

In Claude Code:

```
/plugin marketplace add Hebrish-ASR/Hebrish-Claude-Plugins
/plugin install hebrish-setup@hebrish
```

| Plugin | For | Skills |
| --- | --- | --- |
| `hebrish-setup` | People using the app: install and fix it on Linux | install, troubleshoot, transcribe with the local API (from [Hebrish-Agent-Skills](https://github.com/Hebrish-ASR/Hebrish-Agent-Skills)) |

## The maintainer plugin is gone (2026-11-09)

This marketplace used to carry `hebrish-maintainers`, skills for app reviews and releases,
training-data contributions, the website and the Hugging Face organisation. It was removed on
2026-11-09: project maintenance now runs from one private plugin, so there are not two copies of
each skill drifting apart. Its last public version is in this repository's history (commit
before the removal).

## Contributing

Code goes in pull requests to [Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App). Data,
site edits and ideas go in issues there, and so do suggestions of people or groups the project
should contact (title "Outreach: <who>", or https://hebrish.app/contact?topic=involved).

MIT licence.
