#!/usr/bin/env python3
"""Measure the public Hebrish sentence bank and lexicon: balance, variety, thin terms.

Stdlib only. Reads three public files (downloaded once a day into a cache directory):

  sentences.jsonl  every prompt in the sentence bank (id, text, categories, target_terms, split,
                   source), from github.com/Hebrish-ASR/English-Hebrew-Codeswitching-Parakeet-Finetune
  lexicon.json     every Hebrew term and Israeli name the dataset covers, with its domain, meaning
                   and number of recorded takes (`n`), from hebrish.app/data/lexicon.json
  terms.csv        the canonical romanization list with spelling variants, from
                   github.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier

Usage:
  python3 bank_stats.py                      # JSON report on stdout
  python3 bank_stats.py --covered OUT.txt    # also write every covered term, one per line
  python3 bank_stats.py --avoid OUT.json     # also write the over-used Hebrew words to avoid
  python3 bank_stats.py --candidates C.txt   # check candidate terms (one per line): new or covered
  python3 bank_stats.py --refresh            # re-download the sources first
"""
import argparse, csv, io, json, os, re, statistics, sys, time, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SOURCES = {
    "sentences.jsonl": "https://raw.githubusercontent.com/Hebrish-ASR/English-Hebrew-Codeswitching-Parakeet-Finetune/main/sentences/sentences.jsonl",
    "lexicon.json": "https://hebrish.app/data/lexicon.json",
    "terms.csv": "https://raw.githubusercontent.com/Hebrish-ASR/Hebrew-Latin-Token-Classifier/main/data/terms.csv",
}
CACHE = Path(os.environ.get("HEBRISH_DATA_CACHE", Path.home() / ".cache" / "hebrish-data"))
GREETING = re.compile(r"^(hi|hey|hello|dear|good morning|shalom)\b", re.I)


def fetch(name, refresh=False):
    path = CACHE / name
    if refresh or not path.exists() or time.time() - path.stat().st_mtime > 86400:
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(SOURCES[name], headers={"User-Agent": "hebrish-data-plugin"})
        data = urllib.request.urlopen(req, timeout=120).read()
        path.write_bytes(data)
    return path


def load(refresh=False):
    bank = [json.loads(l) for l in fetch("sentences.jsonl", refresh).read_text(encoding="utf-8").splitlines() if l.strip()]
    lex = json.loads(fetch("lexicon.json", refresh).read_text(encoding="utf-8"))
    terms = list(csv.DictReader(io.StringIO(fetch("terms.csv", refresh).read_text(encoding="utf-8"))))
    return bank, lex, terms


def skeleton(s):
    """Consonant skeleton, the same normalisation the maintainer's coverage check uses."""
    s = s.lower()
    for a, b in (("kh", "h"), ("ch", "h"), ("tz", "s"), ("ts", "s"), ("ck", "k"), ("c", "k"), ("q", "k"),
                 ("v", "b"), ("w", "b"), ("ph", "f"), ("p", "f")):
        s = s.replace(a, b)
    s = re.sub(r"[aeiouy'\-\s.’]", "", s)
    return re.sub(r"(.)\1+", r"\1", s)


def covered_terms(bank, lex, terms):
    """{lowercase form: (canonical, where)} for every covered term and spelling variant."""
    k = {}
    for t in lex["terms"]:
        k.setdefault(t["t"].lower(), (t["t"], "lexicon"))
    for r in terms:
        if r.get("status") not in (None, "", "active"):
            continue
        k.setdefault(r["term"].lower(), (r["term"], "terms.csv"))
        for v in (r.get("variants") or "").split("|"):
            if v:
                k.setdefault(v.lower(), (r["term"], "terms.csv variant"))
    for p in bank:
        for t in p.get("target_terms") or []:
            k.setdefault(t.lower(), (t, "bank target_terms"))
    return k


def report(bank, lex, terms, top=25):
    cs = [p for p in bank if "code_switch" in p["categories"]]
    words = [len(p["text"].split()) for p in bank]
    buckets = Counter("<=8" if n <= 8 else "9-15" if n <= 15 else "16-20" if n <= 20 else "21-30" if n <= 30 else ">30" for n in words)

    def openings(ps, n):
        c = Counter(" ".join(re.findall(r"[\w']+", p["text"])[:n]).lower() for p in ps)
        return [{"opening": o, "prompts": k, "share": round(k / max(1, len(ps)), 4)} for o, k in c.most_common(top)]

    voc = Counter()
    for p in cs:
        m = re.match(r"^(?i:hi|hey|hello|dear)\s+([A-Z][\w']+)", p["text"])
        if m:
            voc[m.group(1)] += 1
    # Bank sentences per covered lexicon term (target_terms, case-insensitive).
    per_term = Counter(t.lower() for p in bank for t in p.get("target_terms") or [])
    dom = defaultdict(list)
    for t in lex["terms"]:
        dom[t["d"]].append(t)
    per_domain = {}
    for d, ts in sorted(dom.items()):
        takes = [t.get("n", 0) for t in ts]
        sent = [per_term.get(t["t"].lower(), 0) for t in ts]
        per_domain[d] = {"name": lex["domains"].get(d, d), "terms": len(ts), "terms_0_takes": sum(1 for x in takes if x == 0),
                         "median_takes": statistics.median(takes), "terms_lt3_bank_sentences": sum(1 for x in sent if x < 3),
                         "median_bank_sentences": statistics.median(sent)}
    thin = [{"term": t["t"], "domain": t["d"], "meaning": t.get("m"), "bank_sentences": per_term.get(t["t"].lower(), 0),
             "takes": t.get("n", 0)} for t in lex["terms"]
            if per_term.get(t["t"].lower(), 0) < 3]
    thin.sort(key=lambda r: (r["bank_sentences"], r["takes"]))
    return {
        "sources": {k: v for k, v in SOURCES.items()},
        "lexicon_built": lex.get("built"),
        "bank": {
            "prompts": len(bank), "code_switch": len(cs), "code_switch_share": round(len(cs) / max(1, len(bank)), 3),
            "by_category": dict(Counter(c for p in bank for c in p["categories"]).most_common()),
            "by_source_family": dict(Counter(p["source"].split(":")[0] for p in bank).most_common()),
            "by_split": dict(Counter(p["split"] for p in bank)),
            "words_per_prompt_median": statistics.median(words), "length_buckets": dict(buckets),
            "code_switch_short_le8_words": sum(1 for p in cs if len(p["text"].split()) <= 8),
            "greeting_opener_share_cs": round(sum(1 for p in cs if GREETING.match(p["text"])) / max(1, len(cs)), 3),
            "cs_vocative_names_top10": voc.most_common(10),
            "openings_2_words_all": openings(bank, 2), "openings_2_words_code_switch": openings(cs, 2),
        },
        "lexicon": {"terms": len(lex["terms"]), "terms_0_takes": sum(1 for t in lex["terms"] if not t.get("n")),
                    "per_domain": per_domain},
        "thin_terms": {"count": len(thin), "rows": thin[:200]},
    }


def overused(bank, lex, n=60):
    """The Hebrew words that appear most often in code-switching prompts: writers should not reach for these."""
    # Case-sensitive, so the brand "Bit" does not count the English word "bit"; a lowercase
    # term also matches with a capital first letter (sentence start).
    forms = {t["t"] for t in lex["terms"]}
    forms |= {f[0].upper() + f[1:] for f in forms if f[:1].islower()}
    rx = re.compile(r"(?<![\w'])(" + "|".join(map(re.escape, sorted(forms, key=len, reverse=True))) + r")(?![\w])")
    c = Counter()
    for p in bank:
        if "code_switch" in p["categories"]:
            c.update({m.lower() for m in rx.findall(p["text"])})
    return [{"word": w, "code_switch_prompts": k} for w, k in c.most_common(n)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--covered", help="write every covered term (canonical spellings and variants) to this file")
    ap.add_argument("--avoid", help="write the 60 most frequent Hebrew words in code-switching prompts to this JSON file")
    ap.add_argument("--candidates", help="file with one candidate term per line: report new / covered / skeleton collisions")
    ap.add_argument("--top", type=int, default=25)
    a = ap.parse_args()
    bank, lex, terms = load(a.refresh)
    cov = covered_terms(bank, lex, terms)
    if a.covered:
        Path(a.covered).write_text("\n".join(sorted(cov, key=str.lower)) + "\n", encoding="utf-8")
        print(f"{len(cov)} covered forms -> {a.covered}", file=sys.stderr)
    if a.avoid:
        Path(a.avoid).write_text(json.dumps(overused(bank, lex), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"over-used words -> {a.avoid}", file=sys.stderr)
    if a.candidates:
        skel = defaultdict(set)
        for low, (canon, _) in cov.items():
            skel[skeleton(low)].add(canon)
        texts = [p["text"] for p in bank]
        out = []
        for line in Path(a.candidates).read_text(encoding="utf-8").splitlines():
            term = line.strip()
            if not term:
                continue
            rx = re.compile(rf"(?<![\w]){re.escape(term)}(?![\w])", re.I)
            hit = cov.get(term.lower())
            out.append({"term": term, "status": "covered" if hit else "new", "covered_as": hit[0] if hit else None,
                        "where": hit[1] if hit else None,
                        "skeleton_matches": sorted(skel.get(skeleton(term), set()) - {term}),
                        "bank_text_hits": sum(1 for t in texts if rx.search(t))})
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    print(json.dumps(report(bank, lex, terms, a.top), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
