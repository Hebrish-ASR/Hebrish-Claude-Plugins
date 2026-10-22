# Writing skills for this marketplace

This repository is **public**. Anyone can install these plugins, and anyone can read every
line. Each skill has to work for a contributor who has a GitHub account, a clone of a public
Hebrish repository and Claude Code, and nothing else. Created 2026-10-22.

## Rules

1. **No private details.** No personal emails or phone numbers, home or machine names
   (hostnames, device models used for testing), IP addresses, account ids, internal URLs, MCP
   gateway or server names, 1Password item names, private bucket names, or paths in anyone's
   home directory (`~/repos/...`). No credentials, ever. Daniel Rosehill's public role
   (maintainer, hebrish.app) is fine.
2. **Access tiers, stated up front.** Each skill opens with a short **Access** section:
   - *Anyone*: works from public repositories and public data.
   - *Maintainer access*: needs something only the project has (the website's private repo,
     the training repo, the project's Resend or Buttondown account, the CDN, the Hugging Face
     org's write token, Modal). Say exactly what is needed in generic terms (for example "a
     Resend API key for the hebrish.app domain"). Then give the **fallback for everyone
     else**: draft the email for the user to send themselves, open an issue or pull request
     on a public repo with the change, or attach the file to an issue.
   Never assume the user is Daniel. Never send anything as the project unless the user has
   the project's own credentials and confirms.
3. **Maintainer specifics live in private.** Where the maintainer's own setup needs specifics
   (which MCP server, which account, which private path), the skill says: "If you have access
   to the private Hebrish-ASR/Hebrish-Mgmt repository, read `docs/maintainer-agent-notes.md`,
   section *<skill name>*, for the maintainer setup." Put those specifics in that file, not here.
4. **Public routes for contributions.** Code: pull requests to
   [Hebrish-ASR/Hebrish-App](https://github.com/Hebrish-ASR/Hebrish-App). Anything else
   (sentences, vocabulary, page edits, ideas): an issue on Hebrish-App unless a skill names a
   better public repository. Requests and ideas are also logged in that repo's `planning/`.
5. **Scripts.** A skill's scripts sit next to it (`skills/<name>/scripts/`) and are referenced
   as `${CLAUDE_PLUGIN_ROOT}/skills/<name>/scripts/...`. Also say what to do when the variable
   is unset: "clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use the path inside it".
6. **Project facts** (romanization, model names, "one person, no team") follow the Hebrish
   website's rules: Hebrish is Daniel Rosehill's one-person, not-for-profit project, so write
   "Daniel", never "we"/"our team". Model names: Jachnun, Sabich, Shakshuka (ASR), Meorav (TTS);
   checkpoints PoC-1… Hebrew words in their romanized form (makolet, arnona), never Hebrew
   script as model output.
7. **Write for an agent opening it cold:** concrete commands, file paths in the public repos,
   expected output, absolute dates for anything measured, what is confirmed and what is inferred.

## Layout

```
.claude-plugin/marketplace.json     the "hebrish" marketplace
plugins/<plugin>/.claude-plugin/plugin.json
plugins/<plugin>/skills/<skill>/SKILL.md (+ scripts/, references/)
```

Bump the plugin's `version` in both `plugin.json` and `marketplace.json` when a skill changes.
