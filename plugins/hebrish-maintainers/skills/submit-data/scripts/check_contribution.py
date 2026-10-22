#!/usr/bin/env python3
"""Check a Hebrish training-data contribution file before it is submitted.

A contribution is one JSON file (format `hebrish-contribution/1`) holding new vocabulary terms,
read-aloud sentences, or both. The format is documented in the submit-data skill
(references/contribution-format.md). This script applies the rules the maintainer's own build
applies, so a file that passes here should merge without rows being dropped. Stdlib only.

It compares the file against the public data (downloaded once a day into a cache directory):
the sentence bank export, the hebrish.app lexicon and the canonical romanization list (terms.csv).

Exit 1 on any ERROR. Warnings are things to read, not necessarily to fix.

Usage:
  python3 check_contribution.py my-contribution.json
  python3 check_contribution.py my-contribution.json --refresh   # re-download the public data
  python3 check_contribution.py my-contribution.json --offline   # skip the coverage and duplicate checks
"""
import argparse, csv, io, json, os, re, sys, time, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SOURCES = {
    "sentences.jsonl": "https://raw.githubusercontent.com/Hebrish-ASR/English-Hebrew-Codeswitching-Parakeet-Finetune/main/sentences/sentences.jsonl",
    "lexicon.json": "https://hebrish.app/data/lexicon.json",
    "terms.csv": "https://raw.githubusercontent.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier/main/data/terms.csv",
}
CACHE = Path(os.environ.get("HEBRISH_DATA_CACHE", Path.home() / ".cache" / "hebrish-data"))

FORMAT = "hebrish-contribution/1"
REGISTERS = {"email", "message", "whatsapp", "note", "reminder", "voice_note", "assistant_prompt"}
CATEGORIES = {"code_switch", "email", "message", "names", "religious", "general", "yiddish"}
# The companion categories a group may draw on: the `category` column of terms.csv.
HEBREW_SCRIPT = re.compile(r"[֐-׿]")
BAD_CHARS = re.compile(r'[()\[\]{}"“”*_#<>₪¥°]')
DIGIT = re.compile(r"\d")
NUM10 = r"(?:ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion)"
NUMWORD = r"(?:one|two|three|four|five|six|seven|eight|nine|" + NUM10[3:]
CHECKS = [  # (regex, message): forms that contradict the transcript conventions
    (re.compile(rf"\b{NUM10}\b", re.I), "number word of 10 or more (the convention is digits, and generated rows with digits are dropped: leave the number out)"),
    (re.compile(rf"\b{NUMWORD}[\s-]+(?:dollars?|euros?|pounds?|shekels?|NIS|ILS|cents?|agorot|pence|percent|per cent)\b", re.I),
     "amount or percentage in words (the convention is $50, 50 NIS, 4%; leave amounts out of generated sentences)"),
    (re.compile(r"\bo'clock\b|\b(?:a\.m\.|p\.m\.)", re.I), "clock time in words (times are digits by convention; leave them out)"),
    (re.compile(rf"\bat\s+(?:one|two|three|four|five|six|seven|eight|nine)\s+(?:tonight|this evening|in the (?:morning|evening|afternoon))\b", re.I),
     "clock time in words (\"at 8 tonight\" by convention; leave it out)"),
    (re.compile(r"\bpercent\b|\bper cent\b", re.I), "percent written as a word (the convention is 4%)"),
]
BANNED_OPENINGS = [  # over-used in the bank (maintainer's coverage review, 2026-10-18)
    r"hi\b", r"hello\b", r"hey\b", r"dear\b", r"remind me to\b", r"don't forget to\b", r"note to self\b",
    r"reminder to self\b", r"reminder to myself\b", r"can you check\b", r"i need to\b",
]
BANNED_RX = re.compile(r"^(?:" + "|".join(BANNED_OPENINGS) + ")", re.I)
OVERUSED_NAMES = {"Yossi", "Moshe", "Noa", "Avi", "Yael", "Michal", "Dana"}
RESERVED_NAMES = {"Daniel", "Rosehill", "Sarah", "Dave", "Smith"}  # used by other datasets; keep out of new sentences


def fetch(name, refresh=False):
    path = CACHE / name
    if refresh or not path.exists() or time.time() - path.stat().st_mtime > 86400:
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(SOURCES[name], headers={"User-Agent": "hebrish-data-plugin"})
        path.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return path


def skeleton(s):
    s = s.lower()
    for a, b in (("kh", "h"), ("ch", "h"), ("tz", "s"), ("ts", "s"), ("ck", "k"), ("c", "k"), ("q", "k"),
                 ("v", "b"), ("w", "b"), ("ph", "f"), ("p", "f")):
        s = s.replace(a, b)
    s = re.sub(r"[aeiouy'\-\s.’]", "", s)
    return re.sub(r"(.)\1+", r"\1", s)


def term_re(term, case=False):
    return re.compile(rf"(?<![\w]){re.escape(term)}(?![\w])", 0 if case else re.I)


def norm(text):
    return re.sub(r"[^\w\s]", "", text.lower()).split()


def public_data(refresh):
    bank = [json.loads(l) for l in fetch("sentences.jsonl", refresh).read_text(encoding="utf-8").splitlines() if l.strip()]
    lex = json.loads(fetch("lexicon.json", refresh).read_text(encoding="utf-8"))
    rows = list(csv.DictReader(io.StringIO(fetch("terms.csv", refresh).read_text(encoding="utf-8"))))
    covered = {}
    for t in lex["terms"]:
        covered.setdefault(t["t"].lower(), (t["t"], "hebrish.app lexicon"))
    for r in rows:
        if r.get("status") not in (None, "", "active"):
            continue
        covered.setdefault(r["term"].lower(), (r["term"], "terms.csv"))
        for v in (r.get("variants") or "").split("|"):
            if v:
                covered.setdefault(v.lower(), (r["term"], "terms.csv variant"))
    for p in bank:
        for t in p.get("target_terms") or []:
            covered.setdefault(t.lower(), (t, "bank target_terms"))
    categories = {r["category"] for r in rows if r.get("category")}
    return bank, covered, categories


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    doc = json.loads(Path(a.file).read_text(encoding="utf-8"))
    errors, warnings = [], []
    E, W = errors.append, warnings.append

    # --- header -------------------------------------------------------------------------------
    if doc.get("format") != FORMAT: E(f"format must be {FORMAT!r}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", doc.get("name", "")): E("name must be a kebab-case slug")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", doc.get("created", "")): E("created must be YYYY-MM-DD")
    if not doc.get("contributor"): E("contributor (your GitHub handle) is missing")
    if doc.get("licence") != "CC-BY-4.0":
        E("licence must be \"CC-BY-4.0\": the sentences are published with the dataset under it")
    if len(doc.get("note", "")) < 40: E("note is missing or too short: say what, why, how it was written and reviewed, sources and dates")
    terms, sents = doc.get("terms", []), doc.get("sentences", [])
    if not terms and not sents: E("nothing to submit: no terms and no sentences")

    bank, covered, categories = ([], {}, set()) if a.offline else public_data(a.refresh)
    skel = defaultdict(set)
    for low, (canon, _) in covered.items():
        skel[skeleton(low)].add(canon)

    # --- terms --------------------------------------------------------------------------------
    companions = doc.get("companions", {})
    pack = {}
    for t in terms:
        term = t.get("term", "")
        for f in ("term", "group", "proper_noun", "meaning"):
            if f not in t: E(f"term {term or t}: missing {f}")
        if t.get("group") not in companions: E(f"term {term}: group {t.get('group')!r} has no entry in companions")
        if term.lower() in pack: E(f"term {term}: duplicate in file")
        pack[term.lower()] = t
        if DIGIT.search(term): E(f"term {term}: digits (no spoken-form convention for these)")
        if HEBREW_SCRIPT.search(term): E(f"term {term}: Hebrew script in `term` (romanize it; Hebrew goes in `he`)")
        if t.get("proper_noun") and term[:1].islower(): E(f"term {term}: proper noun not capitalised")
        if not t.get("he"): W(f"term {term}: no `he` (Hebrew-script spelling)")
        elif "'" in t["he"] or '"' in t["he"]: E(f"term {term}: `he` uses an ASCII quote; use geresh ׳ (U+05F3) or gershayim ״ (U+05F4)")
        elif not HEBREW_SCRIPT.search(t["he"]): W(f"term {term}: `he` has no Hebrew letters")
        if covered:
            hit = covered.get(term.lower())
            if hit and not t.get("topup"): E(f"term {term}: already covered as {hit[0]!r} ({hit[1]}); drop it, or mark it \"topup\": true to add sentences for it")
            if t.get("topup") and not hit: W(f"term {term}: topup, but not covered anywhere")
            near = sorted(skel.get(skeleton(term), set()) - {term})
            if near and not hit: W(f"term {term}: same consonant skeleton as covered {near}: read them; a respelling of a covered term is a duplicate")
    for g, cats in companions.items():
        if not isinstance(cats, list): E(f"companions[{g}] must be a list (use [] for plain-English groups)")
        elif categories:
            for c in cats:
                if c not in categories: W(f"companions[{g}]: {c!r} is not a terms.csv category")

    # --- sentences ----------------------------------------------------------------------------
    bank_text = {" ".join(norm(p["text"])) for p in bank}
    seen, opens, kept = set(), Counter(), 0
    short = 0
    for i, s in enumerate(sents, 1):
        text = s.get("text", "")
        tag = f"sentence {i} ({text[:50]!r})"
        review = s.get("review")
        if not isinstance(review, dict) or not isinstance(review.get("keep"), bool) or not review.get("model"):
            E(f"{tag}: review {{keep, reason, model}} missing: every sentence needs a second-model review")
            continue
        if review.get("model") == s.get("source", "").removeprefix("generated:"):
            W(f"{tag}: reviewed by the same model id that wrote it; the reviewer must be a separate run")
        if not review["keep"]:
            continue
        kept += 1
        for f in ("text", "categories", "target_terms", "hebrew_terms", "register", "source"):
            if f not in s: E(f"{tag}: missing {f}")
        n = len(text.split())
        floor = s.get("min_words", 5)
        if n < floor or n > 45: E(f"{tag}: {n} words (5 to 45; set \"min_words\": 2 on a deliberate short utterance)")
        if n <= 8: short += 1
        if HEBREW_SCRIPT.search(text): E(f"{tag}: Hebrew script (romanized Hebrew only)")
        if BAD_CHARS.search(text): E(f"{tag}: brackets, quotes, markup or a symbol the model cannot write (₪, °)")
        if not re.search(r"[.?!]$", text): E(f"{tag}: must end with . ? or !")
        if DIGIT.search(text): E(f"{tag}: digits (the bank drops generated rows with digits; leave numbers out or use one to nine as words)")
        for rx, msg in CHECKS:
            if rx.search(text): E(f"{tag}: {msg}")
        if BANNED_RX.match(text): E(f"{tag}: over-used opening")
        words = re.findall(r"[\w']+", text)
        opens[" ".join(words[:2]).lower()] += 1
        for name in OVERUSED_NAMES & set(words): W(f"{tag}: {name} is already over-used in the bank; pick another name")
        for name in RESERVED_NAMES & set(words): E(f"{tag}: {name} is reserved for another dataset")
        if s.get("register") not in REGISTERS: E(f"{tag}: register must be one of {sorted(REGISTERS)}")
        cats = set(s.get("categories", []))
        if cats - CATEGORIES: E(f"{tag}: unknown categories {sorted(cats - CATEGORIES)}")
        if not cats & {"email", "message", "general"}: E(f"{tag}: categories need email or message")
        if s.get("hebrew_terms") and "code_switch" not in cats: E(f"{tag}: has hebrew_terms but no code_switch category")
        if "code_switch" in cats and not s.get("hebrew_terms"): E(f"{tag}: code_switch but hebrew_terms is empty")
        src = s.get("source", "")
        if not (src.startswith("generated:") or src == "self-written"): E(f"{tag}: source must be generated:<model> or self-written")
        for t in s.get("target_terms", []) + s.get("hebrew_terms", []):
            if not term_re(t).search(text): E(f"{tag}: term {t!r} not in the text (word-boundary match)")
            elif t[:1].isupper() and not term_re(t, case=True).search(text): W(f"{tag}: {t!r} cased differently in the text")
        for t in s.get("target_terms", []):
            if t.lower() not in pack and covered and t.lower() not in covered:
                W(f"{tag}: target term {t!r} is neither in this file's terms nor covered: add it to terms")
        key = " ".join(norm(text))
        if key in seen: E(f"{tag}: duplicate in file")
        if key in bank_text: E(f"{tag}: already in the sentence bank")
        seen.add(key)
    limit = max(2, kept // 50)
    for o, k in opens.items():
        if k > limit: E(f"{k} sentences open with {o!r} (at most {limit}): vary the openings")
    if kept >= 20 and short / kept < 0.1:
        W(f"only {short} of {kept} kept sentences are 8 words or fewer; aim for about 20% short utterances")

    for w in warnings: print("warn ", w)
    for e in errors: print("ERROR", e)
    print(json.dumps({"file": a.file, "terms": len(terms), "sentences": len(sents), "kept": kept,
                      "errors": len(errors), "warnings": len(warnings), "checked_against_public_data": not a.offline}))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
