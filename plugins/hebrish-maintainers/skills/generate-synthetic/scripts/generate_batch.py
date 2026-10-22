#!/usr/bin/env python3
"""Write read-aloud code-switching sentences for a contribution's terms with Claude Haiku 5.5
on the Anthropic Message Batches API, using your own Anthropic API key.

Split of labour, so the labels are right by construction: the model writes only the prose; this
script assigns which term each sentence must use, checks the term is really in the sentence
(word boundary, exact casing), and writes `target_terms`, `categories` and `source` itself.
The output rows have no `review`; a separate reviewer adds it (see the generate-synthetic skill).

Raw model output is cached next to the output (`<out>.haiku.json`), so `--cached` rebuilds the
rows (new seed, new filter) without another API call. Results are keyed by request id, never by
position. The batch id is printed as soon as it exists; if the run dies while polling,
`--resume <batch id>` collects it.

  uv run --with anthropic python generate_batch.py contribution.json --out rows.jsonl            # estimate only
  uv run --with anthropic python generate_batch.py contribution.json --out rows.jsonl --yes      # submit
  python3 generate_batch.py contribution.json --out rows.jsonl --cached                         # rebuild from cache

Credentials: whatever the Anthropic SDK finds (ANTHROPIC_API_KEY, or a profile from `ant auth login`).
"""
import argparse, json, random, re, sys, time
from pathlib import Path

MODEL = "claude-haiku-5-5"
# US$ per million tokens, standard rate, input / output (Anthropic price table as of 2026-10-06,
# prompts up to 100K tokens). The Batches API bills half of this. Check the current price list.
PRICES = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.00, 10.00)}
BATCH_DISCOUNT = 0.5
SOURCE = "generated:claude-haiku-5-5-batch"
REGISTERS = ["email", "message", "whatsapp", "note", "reminder", "voice_note", "assistant_prompt"]
TERMS_PER_REQUEST = 10
DIGIT = re.compile(r"\d")
HEBREW_SCRIPT = re.compile(r"[֐-׿]")

SYSTEM = """You write sentences for an English speech-recognition dataset. One speaker, an English speaker living in Jerusalem, reads each sentence aloud into his phone. The model being trained must learn to write Hebrew words that English speakers in Israel drop into English, in a fixed romanized spelling.

Rules for every sentence:
- English, with the given Hebrew term spelled exactly as given (same letters, same casing). Never Hebrew script.
- Use the term correctly for its meaning; a listener should be able to tell what it means from context.
- Sound like something a real person dictates: an email, a WhatsApp message, a note to self, a reminder, a voice note to a colleague or family member, or a request to an AI assistant.
- Cased and punctuated like normal written English, ending with . ? or !. British or Irish spelling.
- No digits and no numbers of ten or more at all. Leave out prices, amounts, percentages, dates and clock times. Counts from one to nine are written as words.
- No quotation marks, brackets, emojis or hashtags.
- Do not open with: Hi, Hello, Hey, Dear, Remind me to, Don't forget to, Note to self, Reminder to self, Can you check, I need to. Vary the openings: imperative, question, time phrase, a name, So, Just, a subordinate clause. Put the term at the start, middle or end.
- Names: varied Israeli first names; never Yossi, Moshe, Noa, Avi, Yael, Michal, Dana, Daniel, Sarah or Dave. No real private people.
- You may add one other common Hebrew word an English speaker in Israel would use, if it fits naturally; list it in hebrew_words. Do not use these over-used words: {avoid}.
- No political opinions, no medical advice beyond everyday talk, nothing sexual, crude or violent."""

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["sentences"], "properties": {
    "sentences": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                             "required": ["term", "text", "register", "hebrew_words"],
                                             "properties": {"term": {"type": "string"}, "text": {"type": "string"},
                                                            "register": {"type": "string", "enum": REGISTERS},
                                                            "hebrew_words": {"type": "array", "items": {"type": "string"}}}}}}}


def term_re(term, case=True):
    return re.compile(rf"(?<![\w]){re.escape(term)}(?![\w])", 0 if case else re.I)


def present(term, text):
    """Exact casing, except that a lowercase term may open the sentence with a capital."""
    return bool(term_re(term).search(text)) or (term[:1].islower() and text.startswith(term[:1].upper() + term[1:]))


def requests(doc, per_term, avoid):
    terms = doc["terms"]
    system = SYSTEM.format(avoid=", ".join(avoid) or "none")
    reqs = []
    for i in range(0, len(terms), TERMS_PER_REQUEST):
        chunk = terms[i:i + TERMS_PER_REQUEST]
        lines = []
        for t in chunk:
            plain = doc.get("companions", {}).get(t["group"]) == []
            kind = ("a name; write plain English around it with no other Hebrew" if plain else
                    "a proper noun" if t.get("proper_noun") else "a Hebrew word")
            lines.append(f"- {t['term']} ({kind}): {t['meaning']}")
        reqs.append({"id": f"terms-{i // TERMS_PER_REQUEST:03d}", "system": system, "schema": SCHEMA, "user": (
            f"Write {per_term} different sentences for each of these terms, {per_term * len(chunk)} in total. "
            f"About one in five should be a short utterance of 2 to 8 words; the rest 9 to 30 words. "
            f"Spread the registers. For each sentence return the term it uses (exactly as listed), the text, "
            f"the register and any other Hebrew words in it.\n\n" + "\n".join(lines))})
    return reqs


def estimate(reqs, per_term):
    # Rough: ~900 input tokens per request; ~45 output tokens per sentence plus low-effort thinking.
    tin = 900 * len(reqs)
    tout = sum(len(r["user"].splitlines()) - 2 for r in reqs) * per_term * 45 * 2
    pin, pout = PRICES[MODEL]
    return tin, tout, round((tin * pin + tout * pout) / 1e6 * BATCH_DISCOUNT, 4)


def run_batch(reqs, model, effort, resume=None):
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request
    client = anthropic.Anthropic(max_retries=6)
    if resume:
        batch_id = resume
    else:
        batch = client.messages.batches.create(requests=[Request(custom_id=r["id"], params=MessageCreateParamsNonStreaming(
            model=model, max_tokens=8000, system=r["system"], messages=[{"role": "user", "content": r["user"]}],
            # Haiku 5.5 thinks by default (effort medium); low keeps it cheap. Thinking bills as output.
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": r["schema"]}})) for r in reqs])
        batch_id = batch.id
        print(f"batch {batch_id}: {len(reqs)} requests to {model}", file=sys.stderr)
    while (b := client.messages.batches.retrieve(batch_id)).processing_status != "ended":
        print(f"{batch_id}: {b.processing_status}, {b.request_counts.succeeded} done", file=sys.stderr)
        time.sleep(20)
    out, tin, tout = {}, 0, 0
    for res in client.messages.batches.results(batch_id):
        if res.result.type != "succeeded":
            print(f"{res.custom_id}: {res.result.type}", file=sys.stderr)
            continue
        msg = res.result.message
        tin += msg.usage.input_tokens
        tout += msg.usage.output_tokens
        if msg.stop_reason != "end_turn":
            print(f"{res.custom_id}: {msg.stop_reason}", file=sys.stderr)
            continue
        out[res.custom_id] = json.loads(next(b.text for b in msg.content if b.type == "text"))
    pin, pout = PRICES.get(model, (0, 0))
    print(f"batch {batch_id}: {len(out)} ok, {tin} in / {tout} out tokens, about US${(tin * pin + tout * pout) / 1e6 * BATCH_DISCOUNT:.4f}",
          file=sys.stderr)
    return out


def build(doc, raw, rnd):
    by_term = {t["term"]: t for t in doc["terms"]}
    rows, dropped = [], 0
    for rid in sorted(raw):
        for s in raw[rid]["sentences"]:
            t, text = by_term.get(s["term"]), s["text"].strip()
            why = ("unknown term" if not t else "term not in text with its exact casing" if not present(t["term"], text)
                   else "digits" if DIGIT.search(text) else "Hebrew script" if HEBREW_SCRIPT.search(text)
                   else "no final punctuation" if not re.search(r"[.?!]$", text) else None)
            if why:
                dropped += 1
                print(f"dropped ({why}): {text}", file=sys.stderr)
                continue
            plain = doc.get("companions", {}).get(t["group"]) == []
            extra = [w for w in s["hebrew_words"] if w != t["term"] and term_re(w, case=False).search(text)]
            hebrew = ([] if plain else [t["term"]]) + extra
            cats = ["email" if s["register"] == "email" else "message"]
            if hebrew: cats.append("code_switch")
            if t.get("proper_noun"): cats.append("names")
            row = {"text": text, "categories": cats, "target_terms": [t["term"]], "hebrew_terms": hebrew,
                   "tech_terms": [], "register": s["register"], "source": SOURCE}
            if len(text.split()) < 5:
                row["min_words"] = 2
            rows.append(row)
    rnd.shuffle(rows)
    print(f"{len(rows)} rows kept, {dropped} dropped", file=sys.stderr)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("contribution", help="contribution JSON with `terms` (and `companions`)")
    ap.add_argument("--out", required=True, help="JSONL of unreviewed rows")
    ap.add_argument("--per-term", type=int, default=3)
    ap.add_argument("--avoid", help="JSON from bank_stats.py --avoid: over-used Hebrew words to keep out")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--effort", default="low")
    ap.add_argument("--yes", action="store_true", help="submit the batch (without it, print the estimate and stop)")
    ap.add_argument("--cached", action="store_true")
    ap.add_argument("--resume")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    doc = json.loads(Path(a.contribution).read_text(encoding="utf-8"))
    out = Path(a.out)
    cache = out.with_suffix(".haiku.json")
    if a.cached:
        raw = json.loads(cache.read_text(encoding="utf-8"))
    else:
        avoid = [w["word"] for w in json.loads(Path(a.avoid).read_text())] if a.avoid else []
        reqs = requests(doc, a.per_term, avoid)
        tin, tout, cost = estimate(reqs, a.per_term)
        print(f"{len(reqs)} requests, {len(doc['terms']) * a.per_term} sentences asked for; estimate ~{tin} in / "
              f"~{tout} out tokens, about US${cost} at {a.model} batch prices", file=sys.stderr)
        if not (a.yes or a.resume):
            print("Not submitted. Re-run with --yes to submit.", file=sys.stderr)
            return
        raw = run_batch(reqs, a.model, a.effort, a.resume)
        cache.write_text(json.dumps(raw, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    rows = build(doc, raw, random.Random(a.seed))
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"{len(rows)} rows -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
