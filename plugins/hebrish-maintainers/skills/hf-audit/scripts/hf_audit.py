#!/usr/bin/env python3
"""One-pass, read-only health audit of the Hebrish organisation on Hugging Face.

    uv run --no-project --with huggingface_hub python3 hf_audit.py              # markdown report
    ... --json                                    # machine-readable findings list instead
    ... --collections-config collections.json     # also diff the collections against a config
    ... --only collections,cards,gating,requests,naming   # some checks only

Never writes to the Hub: it calls only list/info/get/download endpoints, and runs the sibling
sync_collections.py as a dry run (never --apply). Reuses the sibling skills' scripts instead of
repeating their logic:

    ../../hf-collections/scripts/sync_collections.py   collections: orphans, config diff, site_check
    ../../model-cards/scripts/audit_cards.py           cards: every card rule, contact address, naming

Checks: collections, cards, gating, requests, naming. Each finding is
{check, repo, severity, detail, fix}; `fix` names the sibling skill and command that would fix it.
Severity: high (wrong for users now: a gate with no form, a wrong contact address, a dead
collection item, a site-listed repo that is not on the Hub), medium (should be fixed soon: repos in
no collection, inconsistent gating, naming), low (tidy-ups: card style findings), info (state, e.g.
pending requests, skipped checks).

Public data needs no token. Pending access requests need a token with write/admin role in the org
(HF_TOKEN or `hf auth login`); without one the check is reported as skipped. Requester names and
e-mail addresses are never read into the output: only counts per repo.
Needs huggingface_hub (tested with 2.2.0, 2026-10-22).
"""
import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent.parent
SYNC = SKILLS / "hf-collections" / "scripts" / "sync_collections.py"
EXAMPLE_CFG = SKILLS / "hf-collections" / "references" / "collections.example.json"
CARDS = SKILLS / "model-cards" / "scripts" / "audit_cards.py"
SITE_MODELS = "https://hebrish.app/data/models.json"
BUILD = re.compile(r"-(GGUF|ONNX|MLX|sherpa-onnx-int8)$")
SEV_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}
CHECKS = ("collections", "cards", "gating", "requests", "naming")

S_COLL = "${CLAUDE_PLUGIN_ROOT}/skills/hf-collections/scripts/sync_collections.py"
S_CARDS = "${CLAUDE_PLUGIN_ROOT}/skills/model-cards/scripts/audit_cards.py"
S_REQ = "${CLAUDE_PLUGIN_ROOT}/skills/access-requests/scripts/access_requests.py"
FIX_COLL = f"hf-collections: add it to the collections config, then `{S_COLL} --config <config> --apply`"
FIX_CARD = "model-cards: edit the card (step 3: show the diff, upload with a commit message)"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Report:
    def __init__(self):
        self.findings, self.notes = [], []

    def add(self, check, repo, severity, detail, fix):
        self.findings.append({"check": check, "repo": repo, "severity": severity, "detail": detail, "fix": fix})


# ---------------------------------------------------------------- collections
def check_collections(api, org, cfg_path, site, rep):
    """Run sync_collections.py as a dry run (never --apply), then check the live items exist."""
    with tempfile.TemporaryDirectory() as tmp:
        if cfg_path:
            cfg = cfg_path
        else:
            # No config: an empty collection list makes sync_collections report only the org-wide
            # orphans and site_check from the live collections. Excludes come from the example config.
            ex = json.loads(EXAMPLE_CFG.read_text()) if EXAMPLE_CFG.exists() else {}
            cfg = str(Path(tmp) / "empty.json")
            Path(cfg).write_text(json.dumps({"org": org, "exclude": ex.get("exclude", []), "collections": []}))
        cmd = [sys.executable, str(SYNC), "--config", cfg, "--site", SITE_MODELS]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if p.returncode:
        rep.add("collections", None, "info", f"sync_collections.py dry run failed: {p.stderr.strip()[-300:]}",
                f"hf-collections: run `{S_COLL} --config <config>` by hand and read the error")
        return
    plan = json.loads(p.stdout)
    for o in plan.get("orphans", []):
        typ, _, rid = o.partition(":")
        rep.add("collections", rid, "medium", f"{typ} is in no collection of the org", FIX_COLL)
    for s in plan.get("site_check", []):
        if "error" in s:
            rep.add("collections", None, "medium", f"collection {s['collection']} named by hebrish.app for "
                    f"'{s['model']}' could not be read: {s['error']}",
                    "website-change: fix `collection` in data/models.json, or hf-collections: create the collection")
        else:
            rep.add("collections", s["missing"], "medium", f"hebrish.app lists it under '{s['model']}', but it is "
                    f"not in the collection the site names for that model ({s['collection']})", FIX_COLL)
    for c in plan.get("collections", []):  # only with --collections-config
        for kind, sev, what in (("add", "medium", "on the Hub but not in the collection"),
                                ("note", "low", "item note differs from the config"),
                                ("missing", "high", "listed in the config but not visible on the Hub (typo, deleted or private)"),
                                ("unmanaged", "low", "in the collection but not in the config")):
            for rid in c.get(kind, []):
                rep.add("collections", rid, sev, f"collection '{c['title']}': {what}",
                        FIX_COLL if kind != "missing" else "hf-collections: fix or remove the id in the config")
        if c.get("create"):
            rep.add("collections", None, "medium", f"collection '{c['title']}' does not exist yet", FIX_COLL)
        if c.get("description"):
            rep.add("collections", None, "low", f"collection '{c['title']}': description differs from the config", FIX_COLL)
    if cfg_path:
        for t in plan.get("hub_collections_not_in_config", []):
            rep.add("collections", None, "info", f"Hub collection '{t}' is not in the config", "hf-collections: add it to the config if it should be managed")

    # Collection items that no longer exist. get_collection gives the full item list
    # (list_collections returns only 4 items per collection, seen 2026-10-20).
    for col in api.list_collections(owner=org, limit=100):
        for it in api.get_collection(col.slug).items:
            if it.item_type not in ("model", "dataset", "space"):
                continue
            try:
                api.repo_info(it.item_id, repo_type=it.item_type)
            except Exception as e:
                code = getattr(getattr(e, "response", None), "status_code", type(e).__name__)
                rep.add("collections", it.item_id, "high", f"item of collection '{col.title}' is not readable "
                        f"({code}): deleted, renamed without redirect, or private",
                        f"hf-collections: `{S_COLL} --config <config> --apply --prune` after removing it from the config")

    # Repos hebrish.app lists that are not on the Hub at all.
    for m in site.get("models", []):
        if m.get("status") == "coming-soon":
            continue
        for r in m.get("repos", []):
            if not r.get("id") or r.get("coming_soon"):
                continue
            typ = r.get("type") or ("dataset" if r.get("role") == "dataset" else "model")
            try:
                api.repo_info(r["id"], repo_type=typ)
            except Exception as e:
                code = getattr(getattr(e, "response", None), "status_code", type(e).__name__)
                rep.add("collections", r["id"], "high", f"hebrish.app lists it under '{m.get('slug')}' but the Hub "
                        f"answers {code}", "website-change: fix the repo id in data/models.json (or publish the repo)")


# ---------------------------------------------------------------- cards, gating, naming
CARD_RULE_CHECK = {"gate": "gating", "naming": "naming", "version": "naming"}
CARD_RULE_SEV = {"gate": "high", "contact": "high", "naming": "medium", "version": "medium",
                 "site": "medium", "licence": "medium"}


def check_cards(api, org, site_raw, repos, infos, want, rep):
    ac = load(CARDS, "audit_cards")
    site = ac.site_index(site_raw)
    try:
        terms = ac.fetch_text(f"{ac.SITE}/terms")
        found = re.findall(r"[\w.+-]+@hebrish\.app", terms)
        terms_contact = max(set(found), key=found.count) if found else None
    except Exception as e:
        terms_contact = None
        rep.notes.append(f"terms page not readable: {e}")
    if "cards" in want and terms_contact and terms_contact != ac.STANDARD_CONTACT:
        rep.add("cards", "hebrish.app/terms", "high", f"the terms page names {terms_contact}; the standard "
                f"access-request address is {ac.STANDARD_CONTACT}",
                "website-change: replace the address in terms.html (and its PDF), then push")
    for typ, rid in repos:
        if typ == "space":
            continue
        res = ac.audit(api, typ, rid, infos[(typ, rid)], site, ac.STANDARD_CONTACT, False, "")
        if res.get("error"):
            if "cards" in want:
                rep.add("cards", rid, "high", res["error"], FIX_CARD + " (add a README.md)")
            continue
        for f in res.get("findings", []):
            check = CARD_RULE_CHECK.get(f["rule"], "cards")
            if check not in want:
                continue
            lines = f" (lines {', '.join(map(str, f['lines'][:6]))})" if f.get("lines") else ""
            fix = FIX_CARD
            if f["rule"] == "gate":
                fix = ("model-cards: add `extra_gated_prompt` and `extra_gated_fields` (Name, Organisation, "
                       "Intended use, terms checkbox) to the card front matter, copying the main model's card")
            elif f["rule"] == "site":
                fix = "website-change: add the repo to data/models.json (or confirm it is deliberately absent)"
            rep.add(check, rid, CARD_RULE_SEV.get(f["rule"], "low"), f"[{f['rule']}] {f['detail']}{lines}", fix)


def line_of(rid, site_by_repo):
    if rid in site_by_repo:
        return site_by_repo[rid]
    return BUILD.sub("", rid)


def check_gating(repos, infos, site_raw, rep):
    site_by_repo = {r["id"]: m["slug"] for m in site_raw.get("models", []) for r in m.get("repos", []) if r.get("id")}
    lines = defaultdict(list)
    for typ, rid in repos:
        if typ == "space":
            continue
        g = getattr(infos[(typ, rid)], "gated", False)
        lines[line_of(rid, site_by_repo)].append((rid, g))
        if g == "auto":
            rep.add("gating", rid, "medium", "gated **automatic**: requests are accepted without review "
                    "(policy: every gated Hebrish repo uses manual review)",
                    "model-cards: maintainer runs `api.update_repo_settings(repo, gated=\"manual\")` if that is intended")
    for line, members in lines.items():
        modes = {str(g) for _, g in members}
        if len(members) > 1 and len(modes) > 1:
            desc = ", ".join(f"{r}={g}" for r, g in members)
            rep.add("gating", line, "medium", f"gating differs within the line: {desc}",
                    "model-cards: maintainer aligns the gate setting (`update_repo_settings`) and the card's gate form")


# ---------------------------------------------------------------- access requests
def check_requests(api, repos, infos, rep):
    from huggingface_hub import get_token
    if not (os.environ.get("HF_TOKEN") or get_token()):
        rep.add("requests", None, "info", "skipped: no Hugging Face token (pending requests need a token with "
                "write/admin role in the org)", "access-requests: run with HF_TOKEN set (maintainer only)")
        return
    total, denied = 0, []
    for typ, rid in repos:
        if typ == "space" or not getattr(infos[(typ, rid)], "gated", False):
            continue
        try:
            # Count only: the objects carry usernames and e-mails, which never leave this function.
            n = sum(1 for _ in api.list_pending_access_requests(rid, repo_type=typ))
        except Exception as e:
            denied.append(f"{rid} ({getattr(getattr(e, 'response', None), 'status_code', type(e).__name__)})")
            continue
        total += n
        if n:
            rep.add("requests", rid, "info", f"{n} pending access request(s)",
                    f"access-requests: `{S_REQ} --profiles`, show the list, then --accept/--reject only the users the maintainer names")
    if denied:
        rep.add("requests", None, "info", f"could not list requests on {len(denied)} repo(s) (token lacks org "
                f"write/admin?): {', '.join(denied[:5])}", "access-requests: use a token with write/admin role in the org")
    rep.notes.append(f"pending access requests in total: {total}")


# ---------------------------------------------------------------- output
def markdown(rep, org, ran):
    f = sorted(rep.findings, key=lambda x: (SEV_ORDER[x["severity"]], x["check"], x["repo"] or ""))
    counts = defaultdict(lambda: defaultdict(int))
    for x in f:
        counts[x["check"]][x["severity"]] += 1
    out = [f"# Hugging Face audit: {org}", "", f"Checks run: {', '.join(ran)}. Findings: {len(f)}.", "",
           "| Check | high | medium | low | info |", "| --- | --- | --- | --- | --- |"]
    for c in ran:
        out.append(f"| {c} | " + " | ".join(str(counts[c][s]) for s in SEV_ORDER) + " |")
    for sev in SEV_ORDER:
        items = [x for x in f if x["severity"] == sev]
        if not items:
            continue
        out += ["", f"## {sev} ({len(items)})", ""]
        for x in items:
            out.append(f"- **{x['check']}** `{x['repo'] or '-'}`: {x['detail']}  \n  Fix: {x['fix']}")
    if rep.notes:
        out += ["", "## Notes", ""] + [f"- {n}" for n in rep.notes]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", default="Hebrish")
    ap.add_argument("--collections-config", default="", help="collections config for a full diff (optional)")
    ap.add_argument("--only", default="", help=f"comma-separated subset of: {','.join(CHECKS)}")
    ap.add_argument("--json", action="store_true", help="print the findings list as JSON")
    a = ap.parse_args()
    want = [c for c in CHECKS if not a.only or c in a.only.split(",")]

    from huggingface_hub import HfApi
    ac = load(CARDS, "audit_cards")
    api = HfApi()
    site_raw = ac.fetch_json(SITE_MODELS)
    rep = Report()

    repos = [("model", m.id) for m in api.list_models(author=a.org, sort="lastModified", limit=1000)]
    repos += [("dataset", d.id) for d in api.list_datasets(author=a.org, limit=1000)]
    infos = {}
    if set(want) & {"cards", "gating", "requests", "naming"}:
        for typ, rid in repos:
            infos[(typ, rid)] = (api.model_info if typ == "model" else api.dataset_info)(rid)
    rep.notes.append(f"{len(repos)} models and datasets in {a.org}; "
                     f"{sum(1 for k in infos if getattr(infos[k], 'gated', False))} gated")

    if "collections" in want:
        check_collections(api, a.org, a.collections_config, site_raw, rep)
    if set(want) & {"cards", "gating", "naming"}:
        check_cards(api, a.org, site_raw, repos, infos, want, rep)
    if "gating" in want:
        check_gating(repos, infos, site_raw, rep)
    if "requests" in want:
        check_requests(api, repos, infos, rep)

    if a.json:
        print(json.dumps({"org": a.org, "checks": want, "notes": rep.notes,
                          "findings": sorted(rep.findings, key=lambda x: (SEV_ORDER[x["severity"]], x["check"]))},
                         indent=1, ensure_ascii=False))
    else:
        print(markdown(rep, a.org, want))


if __name__ == "__main__":
    main()
