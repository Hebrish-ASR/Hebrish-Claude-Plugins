#!/usr/bin/env python3
"""Review Hugging Face access requests on every gated repo (models and datasets) of an organisation.
Dry run unless --apply. Prints JSON on stdout only; never writes a file.

    uv run --no-project --with huggingface_hub python3 access_requests.py            # pending requests
    ... --profiles                         # add each requester's public HF profile counts
    ... --accept alice,bob --apply         # accept on every repo they asked for
    ... --accept alice --repo Hebrish/Yiddish-Sentences --apply      # on one repo only
    ... --reject carol --reason "..." --apply
    ... --subscribe [--apply]              # accepted users who ticked the newsletter box -> Buttondown

Never prints e-mail addresses (they are used only inside --subscribe, never output). Do not redirect
the output into a file inside a repository: it holds requesters' usernames, names and form answers.

Needs huggingface_hub (tested with 2.2.0, 2026-10-22) and a token with write or admin role in the
organisation (HF_TOKEN or `hf auth login`); a read token gets HTTP 403. --subscribe also needs
`requests` and BUTTONDOWN_API_KEY for the Hebrish newsletter.
"""
import argparse
import json
import os
import sys

NEWSLETTER_FIELD = "I agree to receive Hebrish model updates by email (at most once a month; unsubscribe any time)"
BD = "https://api.buttondown.com/v1"


def gated_repos(api, org):
    """(repo_type, repo_id, gated mode) for every gated model and dataset of the org."""
    for m in api.list_models(author=org, sort="lastModified", limit=1000):
        g = api.model_info(m.id).gated
        if g:
            yield "model", m.id, g
    for d in api.list_datasets(author=org, limit=1000):
        g = api.dataset_info(d.id).gated
        if g:
            yield "dataset", d.id, g


def ticked(fields):
    v = (fields or {}).get(NEWSLETTER_FIELD)
    return v is True or str(v).lower() in ("true", "on", "yes", "1")


def profile(api, user, cache={}):
    if user not in cache:
        try:
            u = api.get_user_overview(user)
            cache[user] = {"models": u.num_models, "datasets": u.num_datasets, "spaces": u.num_spaces,
                           "papers": u.num_papers, "followers": u.num_followers,
                           "orgs": [o.name for o in (u.orgs or [])][:10], "pro": u.is_pro,
                           "url": f"https://huggingface.co/{user}"}
        except Exception as e:
            cache[user] = {"error": str(e)[:100]}
    return cache[user]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", default="Hebrish")
    ap.add_argument("--accept", default="", help="comma-separated usernames")
    ap.add_argument("--reject", default="", help="comma-separated usernames")
    ap.add_argument("--reason", default=None, help="rejection reason shown to the user (optional)")
    ap.add_argument("--repo", default="", help="limit to one repo id")
    ap.add_argument("--profiles", action="store_true", help="add public profile counts per requester")
    ap.add_argument("--subscribe", action="store_true", help="add accepted, consenting users to Buttondown")
    ap.add_argument("--apply", action="store_true", help="act (default: dry run)")
    a = ap.parse_args()
    from huggingface_hub import HfApi
    api = HfApi()
    accept = {u for u in a.accept.split(",") if u}
    reject = {u for u in a.reject.split(",") if u}
    if accept & reject:
        sys.exit(f"in both --accept and --reject: {sorted(accept & reject)}")

    plan = {"applied": a.apply, "repos": [], "pending": [], "accept": [], "reject": [],
            "not_pending": [], "subscribe": [], "skipped_no_consent": []}
    seen_users = set()
    subscribers = {}
    for typ, repo, mode in gated_repos(api, a.org):
        if a.repo and repo != a.repo:
            continue
        # huggingface_hub 2.x returns generators here, not lists (seen 2026-10-22): wrap in list().
        pending = list(api.list_pending_access_requests(repo, repo_type=typ))
        plan["repos"].append({"repo": repo, "type": typ, "gated": mode, "pending": len(pending)})
        for r in pending:
            seen_users.add(r.username)
            row = {"repo": repo, "type": typ, "user": r.username, "fullname": r.fullname,
                   "requested": str(r.timestamp)[:16], "fields": r.fields or {},
                   "form": bool(r.fields), "newsletter": ticked(r.fields)}
            if a.profiles:
                row["profile"] = profile(api, r.username)
            plan["pending"].append(row)
            if r.username in accept:
                plan["accept"].append({"repo": repo, "user": r.username})
                if a.apply:
                    api.accept_access_request(repo, r.username, repo_type=typ)
            elif r.username in reject:
                plan["reject"].append({"repo": repo, "user": r.username})
                if a.apply:
                    # rejection_reason is a required keyword in huggingface_hub 2.x (None is allowed)
                    api.reject_access_request(repo, r.username, repo_type=typ, rejection_reason=a.reason)
        if a.subscribe:
            for r in api.list_accepted_access_requests(repo, repo_type=typ):
                if not r.email:
                    continue
                if ticked(r.fields):
                    subscribers.setdefault(r.email, {"user": r.username, "repos": []})["repos"].append(repo)
                else:
                    plan["skipped_no_consent"].append({"repo": repo, "user": r.username})
    plan["not_pending"] = sorted((accept | reject) - seen_users)  # typo, or already decided

    if a.subscribe and subscribers:
        key = os.environ.get("BUTTONDOWN_API_KEY")
        if a.apply and not key:
            sys.exit("BUTTONDOWN_API_KEY is not set (the Hebrish newsletter's key)")
        import requests
        for email, s in subscribers.items():
            entry = {"user": s["user"], "repos": s["repos"]}
            if a.apply:
                # No `type`: Buttondown sends its own double opt-in mail, as the site's forms do.
                resp = requests.post(f"{BD}/subscribers", headers={"Authorization": f"Token {key}"}, json={
                    "email_address": email, "tags": ["gated-access"],
                    "metadata": {"hf_user": s["user"], "repos": ",".join(s["repos"]), "source": "hf-gated-access"}},
                    timeout=30)
                entry["status"] = resp.status_code
                if resp.status_code not in (200, 201):
                    entry["error"] = resp.text[:200].replace(email, "<email>")
            plan["subscribe"].append(entry)
    print(json.dumps(plan, indent=1, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
