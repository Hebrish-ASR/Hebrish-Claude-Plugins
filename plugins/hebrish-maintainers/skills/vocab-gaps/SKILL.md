---
name: vocab-gaps
description: Find the Hebrew and Israeli vocabulary the Hebrish code-switching dataset is missing or thin on — everyday domains with no terms, covered terms with too few sentences — and turn the result into a draft contribution file (terms with meaning, Hebrew spelling and companions) that passes the checker. Use when the user asks "what Hebrew words is Hebrish missing", "find vocabulary gaps", "what's underrepresented", "suggest niche vocabulary for Hebrish", or after bank-coverage flags thin domains.
---

# Vocabulary gaps

Output: a contribution file with `terms` (and no sentences yet), ready for `write-sentences` or
`generate-synthetic`. No paid API calls.

## Access

- **Anyone**: works from the public lexicon, romanization list and sentence bank.
- **Maintainer access**: the private term lists behind the lexicon (the maintainer's coverage check
  runs on them after submission). If you have access to the private Hebrish-ASR/Hebrish-Mgmt
  repository, read `docs/maintainer-agent-notes.md`, section *vocab-gaps*, for the maintainer setup.

## Scope

The target is **code-switching**: Hebrew words an English-speaking Israeli drops into English
speech (the reference speaker is an English-speaking immigrant in Jerusalem: everyday, religious,
bureaucratic and workplace Hebrew all come up). Ask of every candidate: would an English speaker in Jerusalem say *this* word in Hebrew in
the middle of an English sentence? Tech English is not a gap for this dataset. Brands, public
figures and institutions are allowed but count as English (`companions: []`).

## Steps

Scripts: `bank_stats.py` is at `${CLAUDE_PLUGIN_ROOT}/skills/bank-coverage/scripts/`, the checker
and `assemble.py` at `${CLAUDE_PLUGIN_ROOT}/skills/submit-data/scripts/`. If `CLAUDE_PLUGIN_ROOT`
is unset, clone https://github.com/Hebrish-ASR/Hebrish-Claude-Plugins and use the same paths under
`plugins/hebrish-maintainers/`.

0. **Read the lexicon's saturation** (maintainer access; notes section *vocab-gaps*). The lexicon
   saturation report counts the recorded takes per term and returns `avoid` (terms with enough
   recordings: never propose them, not even as companions) and `next_targets` (thin or unrecorded
   terms still short of sentences, with how many to `write`). Its `next_targets` are the top-ups,
   ahead of `thin_terms.rows` below; aim new domains at the categories it shows as thin, so the
   code-switching lexicon gets wider rather than deeper.
1. **Measure depth.** `python3 bank_stats.py --covered covered.txt > coverage.json`.
   `thin_terms.rows` are covered terms with fewer than 3 bank sentences: these are **top-ups**
   (`"topup": true`), not new terms. Prefer everyday words over junk entries (the lexicon still has
   some phrases nobody says; skip them).
2. **Sweep domains for missing terms.** Domains already swept by the maintainer (2026-10-16 to
   2026-10-20): Jerusalem and Tel Aviv places and streets, second-tier towns, hospitals and health,
   kupat holim admin and drug brands, brands and acronyms, politics and media, Jewish observance,
   halakha, rabbis and Torah portions, Ashkenazi forms, conversational reactions, home repairs,
   parenting and gan, work, renting, produce, army and reserves, the Hebrew calendar, driving,
   weather, banking, tax, family law, insurance, simchas, mourning, elder care, pregnancy and baby,
   sport, travel, pets, academia, greetings, everyday errands. **Not swept as of 2026-10-18:**
   cooking and kitchen, clothing and shoe shopping, hobbies and crafts, neighbourhood and building
   life beyond va'ad bayit, Shabbat-table small talk, the Hebrew of Israeli tech workplaces. Start
   with those. Fan out: one subagent per 2 or 3 domains, launched together, each given
   `covered.txt`, this scope section and the term fields from
   `${CLAUDE_PLUGIN_ROOT}/skills/submit-data/references/contribution-format.md`, returning candidates
   with `term`, `group`, `proper_noun`, `meaning`, `he`.
3. **Filter.**
   - Drop anything an anglo would say in English, pure Hebrew-only register, one-off trivia, and
     English dictionary words (they can never be tagged: tor, gush, yam).
   - Spelling per "Romanization" in
     `${CLAUDE_PLUGIN_ROOT}/skills/write-sentences/references/writing-rules.md`; take the canonical
     form from terms.csv where the term is there. Match by whole word, never substring.
   - Write the candidates one per line and run `python3 bank_stats.py --candidates candidates.txt`:
     `status` new or covered, `skeleton_matches` (consonant skeleton equal to a covered term), and
     `bank_text_hits`. A skeleton match is a collision to read, not an automatic drop: on 2026-10-18
     doch, kenas and bricha were real duplicates of do'ach, knas and breicha, while on 2026-10-19
     Omri Ronen ~ Meron was a false positive.
4. **Write the file.** `python3 assemble.py new <slug> --contributor <handle> > <slug>.json`, then
   add `terms` and one `companions` entry per group (2 to 6 terms.csv categories whose words fit the
   same sentence, or `[]` for plain-English groups). `note`: who asked, the date, domains swept,
   what was dropped and why. For factual or current-events terms, check on the web and cite the
   source and date in `note`.
5. `python3 check_contribution.py <slug>.json` until it has no ERROR (a file with terms but no
   sentences is valid).

## Output

The ranked gap list (domain, why it matters for code-switching, term count), the file path and the
checker's summary. Then continue with `write-sentences` (or `generate-synthetic`) if the user wants
sentences too, and `submit-data` to send it. A terms-only file can also be submitted: the maintainer
can write sentences for it.
