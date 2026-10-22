#!/usr/bin/env python3
"""Audit Hugging Face model and dataset cards against the Hebrish rules. Read-only: changes nothing.

    uv run --no-project --with huggingface_hub python3 audit_cards.py                 # every Hebrish repo
    ... --repos Hebrish/Sabich,dataset:Hebrish/Yiddish-Sentences                      # some repos
    ... --links                                                                        # also check outbound links
    ... --save-dir cards/                                                              # keep the README.md files

Prints JSON: per repo the findings (rule, detail, line) and the numbers found in the card, for a
human or agent to compare with the published results. Public sources it reads:
https://hebrish.app/data/models.json (current version, licence, repos per model) and
https://hebrish.app/terms (reported as `terms_contact`, to spot a terms page that still names an old
address). The access-request address on cards is STANDARD_CONTACT, access@hebrish.app: the project
standardised on it on 2026-10-22, and any other hebrish.app access address (for example the older
access-requests@hebrish.app) is flagged.

A finding is a prompt to look, not a verdict: some rules (Hebrew script, "we") have legitimate
exceptions explained in the skill. Needs huggingface_hub (tested with 2.2.0, 2026-10-22). Cards of
gated repos are readable without access; a token is only needed for private repos.
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

SITE = "https://hebrish.app"
STANDARD_CONTACT = "access@hebrish.app"  # the one access-request address, standardised 2026-10-22
HEBREW = re.compile(r"[֐-׿]")
BARE_V = re.compile(r"(?<![\w.])v[1-5](?![\w.])")  # "v3" but not "v1.0", "v2" inside "tdt-0.6b-v2"
PCT = re.compile(r"\d+(?:\.\d+)?\s?%")
LINK = re.compile(r"https?://[^\s)\"'>\]]+")
WE = re.compile(r"\b(?:[Ww]e|[Oo]ur|us|Us)\b")  # not "US" (US$)
QUOTED = re.compile(r"“[^”]*”|\"[^\"]*\"|`[^`]*`")
BASE_CTX = re.compile(r"(parakeet|0\.6b|stock|tdt|published as|test set|whisper)[^|]{0,25}$|poc-\d \($", re.I)
MAIN = re.compile(r"\b(main|recommended|default) (Hebrish )?model\b|\bis the Hebrish model\b", re.I)
SPEAKER = re.compile(r"\b(one|single)[- ]speaker\b|\bone speaker's\b|\bone voice\b", re.I)


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "hebrish-card-audit"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def site_index(models):
    """repo id -> (model entry, repo entry) from models.json."""
    idx = {}
    for m in models.get("models", []):
        for r in m.get("repos", []):
            if r.get("id"):
                idx[r["id"]] = (m, r)
    return idx


def split_front_matter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end], text[end + 4:]
    return "", text


def sections(body):
    """[(heading, start_line, end_line)] for ## headings."""
    lines = body.splitlines()
    heads = [(i, l.lstrip("#").strip()) for i, l in enumerate(lines) if l.startswith("## ")]
    out = []
    for n, (i, h) in enumerate(heads):
        out.append((h, i, heads[n + 1][0] if n + 1 < len(heads) else len(lines)))
    return out


def bare_versions(line):
    """Bare v1-v5 that may name a Hebrish checkpoint (not the base model 'Parakeet TDT 0.6B v2')."""
    clean = QUOTED.sub("", LINK.sub("", line))
    return [m.group() for m in BARE_V.finditer(clean) if not BASE_CTX.search(clean[:m.start()])]


def group(findings):
    """One entry per rule+detail, with the line numbers and up to 3 examples."""
    out = {}
    for f in findings:
        key = (f["rule"], f["detail"])
        g = out.setdefault(key, {"rule": f["rule"], "detail": f["detail"], "lines": [], "examples": []})
        if f.get("line"):
            g["lines"].append(f["line"])
        if f.get("text") and len(g["examples"]) < 3:
            g["examples"].append(f["text"])
    return [{k: v for k, v in g.items() if v} for g in out.values()]


def audit(api, typ, rid, info, site, contact, check_links, save_dir):
    from huggingface_hub import hf_hub_download
    f = []
    add = lambda rule, detail, line=None, text=None: f.append({"rule": rule, "detail": detail, "line": line, "text": text})
    try:
        path = hf_hub_download(rid, "README.md", repo_type=typ)
        text = Path(path).read_text(encoding="utf-8")
    except Exception as e:
        return {"repo": rid, "type": typ, "error": f"no README.md readable: {str(e)[:120]}"}
    if save_dir:
        out = Path(save_dir) / typ / rid.replace("/", "__") / "README.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    fm, body = split_front_matter(text)
    cd = info.card_data.to_dict() if info.card_data else {}
    lines = body.splitlines()
    lineno = lambda i: i + 1 + (fm.count("\n") + 2 if fm else 0)

    # Front matter
    if not cd.get("license"):
        add("licence", "no `license:` in the front matter")
    gated = getattr(info, "gated", False)
    if typ == "model" and cd.get("base_model") and cd.get("base_model_relation") != "finetune" \
            and not any(k in rid for k in ("GGUF", "ONNX", "MLX", "sherpa")):
        add("front-matter", "fine-tune without `base_model_relation: finetune` (the Hub may tag it 'quantized')")
    if gated and typ == "model" and not cd.get("extra_gated_fields"):
        add("gate", f"repo is gated ({gated}) but the card has no `extra_gated_fields` form")
    if gated and typ == "dataset" and not cd.get("extra_gated_fields"):
        add("gate", f"dataset is gated ({gated}) with no form: requests arrive with no answers to review")
    if gated and not cd.get("extra_gated_prompt"):
        add("gate", f"repo is gated ({gated}) but the card has no `extra_gated_prompt` (terms shown on the gate)")
    addrs = set(re.findall(r"[\w.+-]+@hebrish\.app", text))
    wrong = sorted(x for x in addrs if x.lower().startswith("access") and x.lower() != (contact or "").lower())
    if contact and wrong:
        add("contact", f"card names {wrong}; the access-request address is {contact}")

    # Site cross-check
    m, r = site.get(rid, (None, None))
    if m:
        card_lic, site_lic = str(cd.get("license") or "").lower(), (m.get("licence") or "").lower()
        if card_lic and site_lic and card_lic not in site_lic.replace(" ", "-"):
            add("licence-compare", f"card `{card_lic}` vs site `{m['licence']}`: check they say the same thing")
        name = m.get("name")
        if name and r and r.get("role") == "main" and name not in text:
            add("naming", f"card never names the model line '{name}' (hebrish.app/models calls it that)")
        cur = m.get("current")
        if cur and r and r.get("role") == "main" and cur not in text:
            add("version", f"site says the current version is '{cur}'; the card never says it")
    elif typ == "model":
        add("site", "repo not listed in hebrish.app/data/models.json (new, or should it be there?)")

    # Text rules
    secs = sections(body)
    lim = [s for s in secs if s[0].lower().startswith("limitation")]
    speaker_lines = [i for i, l in enumerate(lines) if SPEAKER.search(l)]
    if typ == "model" and not lim:
        add("single-speaker", "no Limitations section (the single-speaker limitation goes there)")
    elif typ == "model" and not any(s <= i < e for _, s, e in lim for i in speaker_lines):
        add("single-speaker", "Limitations section does not state that the model is trained on one speaker")
    if len(speaker_lines) > 2:
        add("single-speaker", f"mentioned on {len(speaker_lines)} lines; state it once, in Limitations")
    first = next((i for i, l in enumerate(lines) if l.startswith("# ")), 0)
    for i in speaker_lines if typ == "model" else []:
        if i <= first + 3:
            add("single-speaker", "stated in the title or opening lines; it belongs in Limitations, once", lineno(i))
    for i, l in enumerate(lines):
        t = l.strip()[:140]
        if HEBREW.search(l):
            add("hebrew-script", "Hebrew script: allowed only as a gloss next to the romanized word, never as output", lineno(i), t)
        if bare_versions(l) and "Shakshuka" not in rid:
            add("naming", "bare v1-v5: write PoC-N (or 'PoC-N, published as vN') or vX.Y", lineno(i), t)
        if re.search(r"(?<!Shakshuka )PoC-\d", QUOTED.sub("", LINK.sub("", l))) and ("Shakshuka" in rid or "Nemotron" in rid):
            add("naming", "Shakshuka checkpoint without the 'Shakshuka' prefix", lineno(i), t)
        if re.search(r"\bBoxty\b", l):
            add("naming", "mentions Boxty (not a Hebrish model): ask the maintainer whether it belongs here", lineno(i), t)
        if MAIN.search(l) and ("Jachnun" in l or "Jachnun" in rid):
            add("naming", "Jachnun presented as main/recommended/default (Sabich is the recommended model)", lineno(i), t)
        if l.startswith("#") and "FUTO" in l:
            add("naming", "'FUTO' in a heading", lineno(i), t)
        if WE.search(QUOTED.sub("", LINK.sub("", l))):
            add("voice", "'we/our/us' (one-person project: write 'Daniel' or rephrase)", lineno(i), t)
    if "hebrish.app" not in text:
        add("links", "no link to hebrish.app")

    numbers = [{"line": lineno(i), "values": PCT.findall(l), "text": l.strip()[:140]}
               for i, l in enumerate(lines) if PCT.search(l)]
    links = sorted(set(u.rstrip(".,;") for u in LINK.findall(text)))
    if check_links:
        for u in links:
            try:
                req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "hebrish-card-audit"})
                code = urllib.request.urlopen(req, timeout=20).status
            except urllib.error.HTTPError as e:
                code = e.code
            except Exception as e:
                code = type(e).__name__
            if code not in (200, 401, 403, 405):  # 401/403: gated file; 405: HEAD not allowed
                add("dead-link", f"{code} {u}")
    return {"repo": rid, "type": typ, "gated": gated, "license": cd.get("license"),
            "site_model": m.get("slug") if m else None, "findings": group(f), "numbers": numbers,
            "links": len(links)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", default="Hebrish")
    ap.add_argument("--repos", default="", help="comma-separated; prefix dataset: for datasets")
    ap.add_argument("--links", action="store_true", help="check every outbound link (slow)")
    ap.add_argument("--save-dir", default="", help="save each README.md here (outside any repo)")
    a = ap.parse_args()
    from huggingface_hub import HfApi
    api = HfApi()
    site = site_index(fetch_json(f"{SITE}/data/models.json"))
    terms = fetch_text(f"{SITE}/terms")
    found = re.findall(r"[\w.+-]+@hebrish\.app", terms)
    terms_contact = max(set(found), key=found.count) if found else None
    contact = STANDARD_CONTACT

    targets = []
    if a.repos:
        for r in a.repos.split(","):
            typ, _, rid = r.partition(":") if ":" in r else ("model", "", r)
            targets.append((typ, rid.strip()))
    else:
        targets += [("model", m.id) for m in api.list_models(author=a.org, sort="lastModified", limit=1000)]
        targets += [("dataset", d.id) for d in api.list_datasets(author=a.org, limit=1000)]
    out = []
    for typ, rid in targets:
        info = (api.model_info if typ == "model" else api.dataset_info)(rid)
        out.append(audit(api, typ, rid, info, site, contact, a.links, a.save_dir))
    print(json.dumps({"checked": len(out), "contact": contact, "terms_contact": terms_contact,
                      "terms_contact_is_standard": terms_contact == contact, "cards": out},
                     indent=1, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
