#!/usr/bin/env python3
"""Compare scored checkpoints and suggest a verdict by the Hebrish selection and publish gates.
Read-only: it reads result files and prints; it never runs a model or writes anything.

    # Public benchmark result files (ehcs-bench format, results/*.json in the benchmark repo)
    python3 verdict.py --stock results/parakeet-tdt-0-6b-v2.json \
        --release results/parakeet-v2-en-he-sabich-v1-0.json --candidate my-result.json

    # Held-out split eval summaries (the training harness's <tag>-summary.json format)
    python3 verdict.py --stock r7-baseline-summary.json --release r7-r6-en30-summary.json \
        --candidate r7-all-summary.json r7-en30-summary.json

Both formats are detected per file. All files in one call must be scored on the same test-set
revision; the script refuses to compare across revisions (scores are comparable only within one).

Rules (Hebrish training docs, "Evaluation" and the benchmark checklist, 2026-10-18 onwards):
 1. Forgetting gate: fail if own-English WER or LibriSpeech WER (normalised) is worse than stock
    on this revision. "Stock" is the candidate's own base model, scored on the same revision.
    On the public benchmark the English-control subset stands in for both.
    The check is strict; the margin is printed so a maintainer can judge a near-zero miss.
 2. Code-switching WER (normalised) and held-out-term recall decide; gaps under ~1 WER point
    or a few term hits are noise (--wer-noise, --hits-noise).
 3. Numbers recall breaks ties (summaries only).
 4. Publish gate: beats stock and the current release on this revision and passes 1.
Suggested verdicts: publishable, fails forgetting, no better than <release>, noise-level difference.
They are suggestions: a maintainer records the final verdict (and can override, which has
happened: Sabich v1.0 was published on 2026-10-20 despite a 0.07-point LibriSpeech miss).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(path: str) -> dict:
    """Normalise one result file to {name, revision, fmt, cs_wer, heldout, seen, own_en, libri, numbers}.
    WER values in percent; recall as (recall %, occurrences)."""
    j = json.loads(Path(path).read_text())
    if "benchmark" in j:  # public benchmark result (ehcs-bench)
        c = j["metrics"]["subsets"]["clean"]
        en = j["metrics"]["subsets"].get("english_control", {})
        t = c["terms"]
        return {
            "file": path, "fmt": "benchmark", "name": j["model"].get("name") or path,
            "revision": j["benchmark"]["revision"],
            "cs_wer": c["wer"] * 100,
            "heldout": (t["unseen"]["recall"] * 100, t["unseen"]["occurrences"]),
            "seen": (t["seen"]["recall"] * 100, t["seen"]["occurrences"]),
            "all_terms": (t["all"]["recall"] * 100, t["all"]["occurrences"]),
            "own_en": en.get("wer", 0) * 100 if en else None, "libri": None, "numbers": None,
            "contamination": j["model"].get("contamination"),
            "missing": len(j["metrics"].get("missing") or []),
        }
    if "test_cs" in j:  # training-harness eval summary
        def rec(k):
            v = j.get(k)
            return (v["recall"] * 100, v["occurrences"]) if v else None
        return {
            "file": path, "fmt": "summary", "name": j.get("tag") or path,
            "revision": j.get("rav_sha", "")[:12],
            "cs_wer": j["test_cs"]["wer_norm"] * 100,
            "heldout": rec("held_terms"), "seen": rec("other_terms_in_test"), "all_terms": None,
            "own_en": j["test_own_en"]["wer_norm"] * 100 if j.get("test_own_en") else None,
            "libri": j["test_libri"]["wer_norm"] * 100 if j.get("test_libri") else None,
            "long": j["test_long"]["wer_norm"] * 100 if j.get("test_long") else None,
            "numbers": (j["numbers"]["recall"] * 100, j["numbers"]["tokens"]) if j.get("numbers") else None,
            "contamination": None, "missing": 0,
        }
    sys.exit(f"{path}: not a benchmark result or eval summary")


def hits(r):
    return None if r is None else r[0] * r[1] / 100


def compare(cand, ref, wer_noise, hits_noise):
    """Per-signal outcome of cand against ref: +1 better beyond noise, 0 noise, -1 worse beyond noise."""
    out = {}
    d = ref["cs_wer"] - cand["cs_wer"]  # positive = candidate better
    out["cs_wer"] = (d, 1 if d >= wer_noise else -1 if d <= -wer_noise else 0)
    for k in ("heldout", "seen"):
        if cand.get(k) and ref.get(k):
            dh = hits(cand[k]) - hits(ref[k])
            out[k] = (dh, 1 if dh >= hits_noise else -1 if dh <= -hits_noise else 0)
    return out


def forgetting(cand, stock):
    fails, margins = [], {}
    for k in ("own_en", "libri"):
        if cand.get(k) is None or stock.get(k) is None:
            continue
        m = cand[k] - stock[k]
        margins[k] = m
        if m > 1e-9:
            fails.append(k)
    return fails, margins


def fmt_rec(r):
    return "-" if r is None else f"{r[0]:.2f}% ({hits(r):.0f}/{r[1]})"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stock", required=True, help="stock base model's result on this revision")
    ap.add_argument("--release", help="current release's result on this revision")
    ap.add_argument("--candidate", nargs="+", required=True)
    ap.add_argument("--wer-noise", type=float, default=1.0, help="WER points treated as noise (default 1.0)")
    ap.add_argument("--hits-noise", type=float, default=8,
                    help="term hits treated as noise (default 8: a 6-hit gain was judged noise on 2026-10-19)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    stock = load(a.stock)
    release = load(a.release) if a.release else None
    cands = [load(p) for p in a.candidate]
    everyone = [stock] + ([release] if release else []) + cands
    revs = {e["revision"] for e in everyone}
    if len(revs) > 1:
        sys.exit("refusing to compare across test-set revisions: "
                 + ", ".join(f"{e['name']}={e['revision']}" for e in everyone))

    report = {"revision": revs.pop(), "noise": {"wer_points": a.wer_noise, "term_hits": a.hits_noise}, "rows": []}
    for c in cands:
        fails, margins = forgetting(c, stock)
        vs_stock = compare(c, stock, a.wer_noise, a.hits_noise)
        vs_rel = compare(c, release, a.wer_noise, a.hits_noise) if release else None
        if fails:
            verdict = "fails forgetting"
        elif vs_rel is None:
            verdict = ("publishable" if any(v[1] > 0 for v in vs_stock.values())
                       and not any(v[1] < 0 for v in vs_stock.values()) else "no better than stock")
        else:
            signals = [v[1] for v in vs_rel.values()]
            beats_stock = any(v[1] > 0 for v in vs_stock.values()) and not any(v[1] < 0 for v in vs_stock.values())
            if any(s < 0 for s in signals) and not any(s > 0 for s in signals):
                verdict = f"no better than {release['name']}"
            elif any(s > 0 for s in signals) and not any(s < 0 for s in signals) and beats_stock:
                verdict = "publishable"
            elif all(s == 0 for s in signals):
                raw = vs_rel["cs_wer"][0]
                verdict = ("noise-level difference" if raw > 0 or any(v[0] > 0 for v in vs_rel.values())
                           else f"no better than {release['name']}")
            else:
                verdict = "mixed: better on some signals, worse on others (maintainer call)"
        notes = []
        if c.get("contamination"):
            notes.append(f"declared contamination: {c['contamination']}")
        if c.get("missing"):
            notes.append(f"{c['missing']} clips without a prediction (scored as empty)")
        if c["fmt"] == "benchmark":
            notes.append("public benchmark: English control stands in for the forgetting gate (no LibriSpeech)")
        report["rows"].append({
            "candidate": c["name"], "file": c["file"], "verdict": verdict,
            "forgetting": {"fails": fails, "margin_points": {k: round(v, 3) for k, v in margins.items()}},
            "vs_stock": {k: round(v[0], 3) for k, v in vs_stock.items()},
            "vs_release": {k: round(v[0], 3) for k, v in vs_rel.items()} if vs_rel else None,
            "notes": notes,
        })

    if a.json:
        print(json.dumps(report, indent=1))
        return
    print(f"Revision {report['revision']}. Noise: {a.wer_noise} WER points, {a.hits_noise:g} term hits.\n")
    print("| Model | CS WER | Held-out / unseen terms | Seen terms | Own EN / EN control | LibriSpeech | Numbers |")
    print("|---|---|---|---|---|---|---|")
    for e in everyone:
        f = lambda v: "-" if v is None else f"{v:.2f}%"
        print(f"| {e['name']} | {f(e['cs_wer'])} | {fmt_rec(e['heldout'])} | {fmt_rec(e['seen'])} | "
              f"{f(e['own_en'])} | {f(e['libri'])} | {fmt_rec(e['numbers'])} |")
    print()
    for r in report["rows"]:
        print(f"- **{r['candidate']}**: {r['verdict']}")
        fm = r["forgetting"]["margin_points"]
        if fm:
            print("  - forgetting margins vs stock (positive = worse): "
                  + ", ".join(f"{k} {v:+.2f}" for k, v in fm.items()))
        if r["vs_release"]:
            print("  - vs release (positive = candidate better; WER points, term hits): "
                  + ", ".join(f"{k} {v:+.2f}" for k, v in r["vs_release"].items()))
        for n in r["notes"]:
            print(f"  - {n}")


if __name__ == "__main__":
    main()
