# Contribution file format (`hebrish-contribution/1`)

One JSON file per contribution, named `<name>.json`. It carries new vocabulary (`terms`), read-aloud
sentences (`sentences`), or both. The maintainer splits it into the project's own pack and sentence
files; the field names below are the ones those files use, so nothing is renamed on the way in.
Defined 2026-10-22.

```json
{
  "format": "hebrish-contribution/1",
  "name": "kitchen-and-cooking",
  "created": "2026-10-22",
  "contributor": "your-github-handle",
  "licence": "CC-BY-4.0",
  "note": "What this adds and why; domains swept; how sentences were written (which model) and reviewed (which model); sources and the dates they were checked; anything left out and why.",
  "instruction": "Optional. One line for every sentence of this pack, e.g. Mention people neutrally and factually.",
  "companions": {"kitchen": ["food", "food_shopping", "home"], "brands": []},
  "terms": [
    {"term": "sir lachatz", "group": "kitchen", "proper_noun": false,
     "meaning": "pressure cooker", "he": "סיר לחץ"}
  ],
  "sentences": [
    {"text": "Can we borrow your sir lachatz for the cholent this week?",
     "categories": ["message", "code_switch"],
     "target_terms": ["sir lachatz"], "hebrew_terms": ["sir lachatz", "cholent"], "tech_terms": [],
     "register": "whatsapp", "source": "generated:claude-sonnet-5-5",
     "review": {"keep": true, "reason": "natural, term used correctly", "model": "claude-opus-5-5"}}
  ]
}
```

## Header

| Field | Rule |
|---|---|
| `format` | Always `hebrish-contribution/1`. |
| `name` | Kebab-case slug. Becomes the pack name, so make it specific (`kitchen-and-cooking`, not `vocab`). |
| `created` | `YYYY-MM-DD`. |
| `contributor` | Your GitHub handle, for credit in the pack note. |
| `licence` | Always `CC-BY-4.0`. The sentences are published with the dataset under it, so they must be text you may license: written by you or by a model for you, never copied from a book, site, article or another dataset. |
| `note` | Who, what, why, how written, how reviewed, sources with dates. Required. |
| `companions` | One entry per `group` used in `terms`: a list of 2 to 6 `category` values from [terms.csv](https://github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier/blob/main/data/terms.csv) (food, food_shopping, home, family, religious, religious_calendar, transport_geography, bureaucracy, health, …) whose words fit in the same sentence. **An empty list `[]` means plain English** that only mentions the name: use it for brands, politicians, celebrities and institutions with English names. Those sentences count toward the English side of the training mix, not the code-switching side. |

## Terms

| Field | Rule |
|---|---|
| `term` | The canonical romanized spelling, cased as it should appear in transcripts. See "Romanization" in `skills/write-sentences/references/writing-rules.md`. No digits, no Hebrew script. |
| `group` | Your own label for a set of related terms (`kitchen`, `jerusalem_street`, `news_people`). Must have a `companions` entry. |
| `proper_noun` | `true` for names of people, places, brands, institutions (must start with a capital). |
| `meaning` | A short, factual gloss with enough context for a writer to use the term correctly. A wrong meaning produces wrong sentences; it was the main reason sentences were dropped in past packs. |
| `he` | The Hebrew-script spelling: modern ktiv male, no niqqud, geresh `׳` (U+05F3) and gershayim `״` (U+05F4), never an ASCII apostrophe or quote. The literal spoken form, not an official name. |
| `topup` | Optional `true`: the term is already covered and you are adding more sentences for it on purpose (for thin terms). Without it, a covered term is an error. |

## Sentences

| Field | Rule |
|---|---|
| `text` | One English sentence, 5 to 45 words (aim for 6 to 30), ending `.`, `?` or `!`. Rules: `skills/write-sentences/references/writing-rules.md`. |
| `categories` | `email` or `message` by register (`email` only for the email register), plus `code_switch` when `hebrew_terms` is non-empty, plus `names` when a target term is a proper noun. `religious` or `yiddish` when the sentence is about religious practice or uses Yiddish words. |
| `target_terms` | The term(s) this sentence exists for: pack terms, or covered terms when topping up. Each must appear in `text` by whole-word match. |
| `hebrew_terms` | Every Hebrew word in the sentence (target and companion words), spelled as in `text`. Empty for plain-English rows. |
| `tech_terms` | Always `[]` here (tech vocabulary is not part of this dataset). |
| `register` | `email`, `message`, `whatsapp`, `note`, `reminder`, `voice_note` or `assistant_prompt`. |
| `source` | `generated:<model id>` for model-written rows (`generated:claude-haiku-5-5-batch`, `generated:claude-sonnet-5-5`), `self-written` for rows you wrote yourself. |
| `review` | `{"keep": true/false, "reason": "...", "model": "<reviewer>"}` from a **separate** reviewer. Rows with `keep: false` may stay in the file (they are ignored) and help the maintainer see what was rejected. If the reviewer edited a row, put the old text in `review.original_text`. |
| `min_words` | Optional `2` on a deliberate short utterance under 5 words ("I sent it shilshom."). Without it, rows under 5 words are dropped. |

Check the file with `skills/submit-data/scripts/check_contribution.py` before submitting.
