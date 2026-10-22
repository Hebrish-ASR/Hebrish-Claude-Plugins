# Hebrish Claude Plugins

The Claude Code marketplace for [Hebrish](https://hebrish.app): on-device English dictation
that writes Hebrew words correctly, in romanized form (makolet, arnona, teudat zehut). Hebrish
is a one-person, not-for-profit project by Daniel Rosehill. These plugins are for anyone who
wants to use it or help with it.

## Install

In Claude Code:

```
/plugin marketplace add Hebrish-ASR/Hebrish-Claude-Plugins
/plugin install hebrish-maintainers@hebrish
```


| Plugin | For | Skills |
| --- | --- | --- |
| `hebrish-setup` | People using the app: install and fix it on Linux | install, troubleshoot (from [Hebrish-Agent-Skills](https://github.com/Hebrish-ASR/Hebrish-Agent-Skills)) |
| [`hebrish-maintainers`](plugins/hebrish-maintainers/) | Anyone working on Hebrish, despite the name | app reviews per platform, feature parity, Android release, planning (requests, sprints, decision log); training data (vocabulary gaps, writing, checking and submitting sentences); website changes and brand assets; outreach; Hugging Face collections, model cards and access requests |

## What you need

Every skill starts with an **Access** section. The app development and training-data skills
work with nothing but a clone of a public repository; without push access they end in a pull
request or an issue. Releases, the website's own repository and the Hugging Face organisation
need the project's access. The outreach skills (email, community posts, newsletter) are only
for the maintainer and people Daniel has authorised to represent the project. They check
first, and stop for anyone else.

## Contributing

Code goes in pull requests to [Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App). Data,
site edits and ideas go in issues there. What is planned, and why, is in that repo's
[`planning/`](https://github.com/Hebrish-ASR/Hebrish-App/tree/main/planning) folder. To write
or change a skill, read [AUTHORING.md](AUTHORING.md).

MIT licence.
