#!/usr/bin/env python3
"""Keep a Hugging Face organisation's collections in step with a collections config file.

Dry run unless --apply. Prints a JSON plan on stdout.

    uv run --no-project --with huggingface_hub python3 sync_collections.py --config collections.json
    ... --only jachnun,sabich     limit to some collection keys
    ... --apply                   create collections, set descriptions, add items, rewrite notes
    ... --apply --prune           also remove items that are in a collection but not in the config
    ... --site https://hebrish.app/data/models.json
                                  also report repos that the site lists for a model but that are
                                  missing from the collection the site names for that model

Config schema: references/collections-schema.md next to this script's skill. Needs huggingface_hub
(tested with 2.2.0 on 2026-10-22). Reading works anonymously for public repos; --apply needs a token
with write access to the organisation (HF_TOKEN or `hf auth login`).
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

AUDIO = (".wav", ".mp3", ".flac", ".opus", ".ogg", ".m4a")
DATA = (".jsonl", ".json", ".csv", ".parquet", ".txt", ".tsv", ".arrow") + AUDIO
MAX_DESC = 150  # the Hub rejects longer collection descriptions with HTTP 400 (seen 2026-10-20)


def org_repos(api, org):
    """Org repos per auto rule, plus every org repo id (for the orphan report)."""
    out = {"audio-datasets": [], "text-datasets": [], "spaces": [], "models": []}
    every = []
    for d in api.list_datasets(author=org, limit=1000):
        every.append(("dataset", d.id))
        files = [s.rfilename.lower() for s in (api.dataset_info(d.id).siblings or [])]
        data = [f for f in files if f.endswith(DATA) and not f.startswith(".")]
        if not data:
            continue  # empty repo: skipped by every auto rule
        kind = "audio-datasets" if any(f.endswith(AUDIO) for f in data) else "text-datasets"
        out[kind].append(("dataset", d.id, None))
    # sort=lastModified: the unsorted listing has omitted new repos before (seen 2026-10-19)
    for m in api.list_models(author=org, sort="lastModified", limit=1000):
        every.append(("model", m.id))
        out["models"].append(("model", m.id, None))
    for s in api.list_spaces(author=org, limit=1000):
        every.append(("space", s.id))
        out["spaces"].append(("space", s.id, None))
    return out, every


def canonical(api, typ, rid, cache={}):
    """Current id of a repo (a renamed repo still answers under its old id), or None if not visible."""
    if (typ, rid) not in cache:
        try:
            cache[(typ, rid)] = api.repo_info(rid, repo_type=typ).id
        except Exception:
            cache[(typ, rid)] = None
    return cache[(typ, rid)]


def site_check(api, url, hub_items):
    """Repos listed per model in the site's models.json that are missing from that model's collection."""
    with urllib.request.urlopen(url, timeout=30) as r:
        site = json.load(r)
    out = []
    for m in site.get("models", []):
        coll = (m.get("collection") or "").rstrip("/")
        if "/collections/" not in coll:
            continue
        slug = coll.split("/collections/", 1)[1]
        if slug not in hub_items:
            try:
                hub_items[slug] = {i.item_id for i in api.get_collection(slug).items}
            except Exception as e:
                out.append({"model": m.get("slug"), "collection": slug, "error": str(e)[:120]})
                continue
        for repo in m.get("repos", []):
            rid = repo.get("id")
            typ = repo.get("type") or ("dataset" if repo.get("role") == "dataset" else "model")
            rid = rid and (canonical(api, typ, rid) or rid)  # the site may still list a pre-move id
            if rid and rid not in hub_items[slug]:
                out.append({"model": m.get("slug"), "collection": slug, "missing": rid})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, help="path to the collections config (JSON)")
    ap.add_argument("--only", default="", help="comma-separated collection keys")
    ap.add_argument("--apply", action="store_true", help="write to the Hub (default: dry run)")
    ap.add_argument("--prune", action="store_true", help="with --apply: remove unmanaged items")
    ap.add_argument("--site", default="", help="URL of a models.json to cross-check (optional)")
    a = ap.parse_args()
    if a.prune and not a.apply:
        print("note: --prune has no effect without --apply; unmanaged items are only reported", file=sys.stderr)

    from huggingface_hub import HfApi
    api = HfApi()
    cfg = json.loads(Path(a.config).read_text())
    org = cfg["org"]
    only = {k for k in a.only.split(",") if k}
    auto, every = org_repos(api, org)
    # list_collections returns only the first 4 items of each collection (seen 2026-10-20):
    # use it for titles and slugs only, and read items with get_collection.
    on_hub = {c.title: c.slug for c in api.list_collections(owner=org, limit=100)}
    hub_items = {}
    plan = []

    for c in cfg["collections"]:
        if only and c["key"] not in only:
            continue
        if len(c["description"]) > MAX_DESC:
            sys.exit(f"{c['key']}: description is {len(c['description'])} characters; the Hub allows {MAX_DESC}")
        want, seen = [], set()
        src = [tuple(i) + (None,) * (3 - len(i)) for i in c.get("items", [])]
        if c.get("auto"):
            src += auto.get(c["auto"], [])
        for typ, rid, note in src:
            rid = canonical(api, typ, rid) or rid  # resolve renames so old ids never duplicate
            if rid in seen or rid in c.get("exclude", []) or rid in cfg.get("exclude", []):
                continue
            seen.add(rid)
            want.append((typ, rid, note))

        slug = c.get("slug") or on_hub.get(c["title"])
        col = api.get_collection(slug) if slug else None
        have = {i.item_id: i for i in col.items} if col else {}
        if col:
            hub_items[col.slug] = set(have)
        p = {"key": c["key"], "title": c["title"],
             "url": f"https://huggingface.co/collections/{slug}" if slug else None,
             "create": col is None,
             "description": col is not None and (col.description or "") != c["description"],
             "add": [], "note": [], "missing": [],
             "unmanaged": [i for i in have if i not in seen]}
        for typ, rid, note in want:
            if rid in have:
                if note and (getattr(have[rid], "note", None) or "") != note:
                    p["note"].append(rid)
            elif canonical(api, typ, rid):
                p["add"].append(rid)
            else:
                p["missing"].append(rid)  # typo, deleted, or private and not visible to this token
        plan.append(p)

        if not a.apply:
            continue
        if col is None:
            col = api.create_collection(c["title"], namespace=org, description=c["description"], exists_ok=True)
        elif p["description"]:
            api.update_collection_metadata(col.slug, description=c["description"])
        for typ, rid, note in want:
            if rid in p["add"]:
                api.add_collection_item(col.slug, item_id=rid, item_type=typ, note=note, exists_ok=True)
            elif rid in p["note"]:
                api.update_collection_item(col.slug, have[rid].item_object_id, note=note)
        if a.prune:
            for rid in p["unmanaged"]:
                api.delete_collection_item(col.slug, have[rid].item_object_id)
        p["url"] = f"https://huggingface.co/collections/{col.slug}"

    # Org repos that are in no collection of the org at all (whole org, not just --only).
    in_any = set()
    for slug in on_hub.values():
        if slug not in hub_items:
            hub_items[slug] = {i.item_id for i in api.get_collection(slug).items}
        in_any |= hub_items[slug]
    excluded = set(cfg.get("exclude", []))
    orphans = [f"{t}:{r}" for t, r in every if r not in in_any and r not in excluded and r != f"{org}/README"]

    out = {"applied": a.apply, "org": org, "collections": plan, "orphans": orphans,
           "hub_collections_not_in_config": sorted(
               t for t in on_hub if t not in {c["title"] for c in cfg["collections"]})}
    if a.site:
        out["site_check"] = site_check(api, a.site, hub_items)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
