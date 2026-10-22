# Writing rules for Hebrish read-aloud sentences

Paste this whole file into every writer and reviewer brief. Sources: the project's dataset
conventions as of 2026-10-22. `check_contribution.py` enforces the mechanical ones.

## What the sentences are for

Hebrish fine-tunes NVIDIA Parakeet (an English speech recognition model) to write the Hebrew words
that English speakers in Israel drop into English, in one fixed romanized spelling: *"pick up some
bamba from the makolet"*, *"I have to go to Bituach Leumi tomorrow"*. Daniel Rosehill, the project's
maintainer, reads each sentence aloud into his phone; the recording and the sentence become one
training example. So every sentence must be something a person would really say, and its text must
be exactly what the model should write.

Code-switching is the objective. The target training mix is about 70% code-switching and 30% plain
English. Tech vocabulary is not a goal of this dataset.

## Romanization

- Latin letters only. Never Hebrew script in a sentence (the model cannot write it).
- Use the canonical spelling: the `term` column of
  [terms.csv](https://github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier/blob/main/data/terms.csv)
  or the spelling on [hebrish.app/lexicon](https://hebrish.app/lexicon). Never a listed variant.
- New terms: chet and chaf as `ch` (chag, cheshbon, mechonit), glottal stop as `'` (do'ach), a `ha-`
  prefix joined and lowercase inside a name (Park Hayarkon, Hashalom, not HaShalom). Brands,
  hospitals and institutions keep their own English spelling (Shaare Zedek, El Al).
- Proper nouns are capitalised as English writes them: Yerushalayim, Shabbat, Bituach Leumi, Clalit.
  Generic nouns stay lowercase: kupat holim, arnona, iriya, erev chag.
- Ashkenazi and Israeli forms (Shabbos / Shabbat, Sukkos / Sukkot, bris / brit) are both kept on
  purpose. Never "correct" one into the other; write the form the sentence is meant to be read in.
- A Hebrew word that is also an English dictionary word (tor, gush, yam, sal) cannot be tagged by
  the build. Avoid it as a target term.

## Transcript conventions (no contradictions)

The same spoken thing must always be written the same way, or the model learns two answers.
The project writes **digits** for versions, money (`$20`, `€18`, `50 NIS`), percentages (`4%`),
times, dates and any number of 10 or more, and **words** for one to nine in ordinary counts. But
the sentence build drops generated rows that contain digits (numbers go through a separate,
hand-written path). So in contributed sentences:

- **Leave numbers out.** No digits, no prices, no amounts, no percentages, no dates, no clock times.
- Counts from one to nine as words are fine ("two kilos", "three times").
- Never a number of 10 or more in words ("twenty minutes", "ten dollars"): that contradicts the
  digits convention. Rephrase ("a few minutes", "a bit late").
- Never "N shekels", "N dollars", "N percent", "o'clock", "a.m./p.m.": all contradict a convention.
- No `₪` (the model's tokenizer cannot write it; shekel amounts are `50 NIS` in the numeric path).
- Cased and punctuated like normal written English; one sentence per row, ending `.` `?` `!`.
- No quotation marks, brackets, asterisks, hashtags, emojis or markup.

## Content

- The term is used correctly for its `meaning`; a listener can tell what it means from context.
- Registers: email, WhatsApp message, note to self, reminder, voice note to a colleague or family
  member, request to an AI assistant.
- Length 6 to 30 words; about **20% short utterances** of 2 to 8 words ("Ask the va'ad bayit about
  it."). Rows under 5 words need `"min_words": 2`.
- Plain-English groups (`companions: []`, brands, public figures): English around the name, no other
  Hebrew. Other groups: the term, plus at most one companion Hebrew word that fits naturally.
- Names: varied Israeli first names. Not Yossi, Moshe, Noa, Avi, Yael, Michal or Dana (over-used),
  and not Daniel, Rosehill, Sarah, Dave or Smith (reserved for other datasets). No real private
  people.
- Public figures: neutral and factual, their role as of the source date. No political opinion.
- No medical advice beyond everyday talk. Nothing sexual, crude, demeaning or violent. Nothing a
  person would not want to read aloud and publish under their name.
- Original text only. Never copy or lightly edit sentences from articles, books, websites or other
  datasets (see the submit-data skill, "Third-party text").

## Variety (a hard requirement)

- No more than 2 sentences in a writer's file share their first two words.
- Rotate openings (imperative, question, time phrase, a name, "So", "Just", a subordinate clause),
  term position (start, middle, end), sentence type and person.
- **Banned openings** (over-used in the bank): Hi / Hello / Hey / Dear and any greeting, "Remind me
  to", "Don't forget to", "Note to self", "Reminder to self", "Can you check", "I need to".
  Also avoid the "<errand> before <deadline>" shape and the "tomorrow / this week / Thursday" pattern.
- Keep the over-used companion words out: `bank_stats.py --avoid` lists the 60 most frequent Hebrew
  words in the bank's code-switching sentences (on 2026-10-22: Yossi, Pesach, minyan, Noa, savta,
  Avi, Moshe, shiur, gan, Kiddush, …).

## Reviewer checklist

A reviewer reads every row and sets `review.keep` with a one-line `reason`:

1. Term used correctly for its meaning (the most common failure).
2. Natural English an English speaker in Israel would actually say; not contrived.
3. Every rule above: romanization and casing, no numbers, no banned opening, no reserved names,
   content screen.
4. Not a near-duplicate of another row or of a bank sentence.
5. For current events: facts match the cited source. A reviewer whose knowledge predates the
   events may call real people and parties "fictional"; check the source before rejecting.

The reviewer may fix a row in place (keep the old text in `review.original_text`) instead of
rejecting it.
