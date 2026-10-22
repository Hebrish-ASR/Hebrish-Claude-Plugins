#!/usr/bin/env python3
"""Tables and charts from hebrish.app's published results (data/results.json). Read-only.

    python3 results_report.py                         # every block, Markdown, from the live site
    python3 results_report.py --block compare_r7      # one block
    python3 results_report.py --source ./results.json --json
    uv run --with matplotlib python3 results_report.py --block leaderboard --metric recall --chart out.png

Blocks: leaderboard (public benchmark, test set v1 clean subset), compare (held-out split at one
dataset revision), compare_r7 (held-out split, round R7), checkpoints (Jachnun version history).
Rules this script enforces, from the website's own rules:
  - targets (checkpoints with status "target") are goals, never results: they are left out;
  - checkpoints without measured scores in a block print as "no score on this revision", never
    as a number (in the history block: PoC-4 and PoC-5 are unbenchmarked; Jachnun v1.0 was
    benchmarked on a later revision, so its numbers are in compare, compare_r7 and leaderboard);
  - each block prints its own revision and source note, because blocks on different test-set
    revisions must never be ranked against each other;
  - values are printed exactly as stored: no rounding.
Chart colours follow the site's figures (scripts/make_figures.py in the website repo):
Jachnun v1.0 accent green, Sabich v1.0 gold, other Hebrish checkpoints light green, the rest grey.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

DEFAULT_SOURCE = "https://hebrish.app/data/results.json"
BLOCKS = ("leaderboard", "compare", "compare_r7", "checkpoints")

# Brand tokens (light theme), as used by the site's static figures.
BG, INK, MUTED, LINE = "#fbf8f2", "#1d2422", "#5b6662", "#e2dccf"
ACCENT, GOLD, ACCENT_2, OTHER = "#0f6b5c", "#c8901c", "#7fb3a7", "#b8b2a5"


def load(source: str) -> dict:
    if source.startswith("http"):
        req = urllib.request.Request(source, headers={"User-Agent": "hebrish-results-report"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    return json.loads(Path(source).read_text())


def fmt(v) -> str:
    if v is None:
        return "no score on this revision"
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


def block_rows(data: dict, name: str) -> tuple[list[dict], list[dict], dict]:
    """(metrics, rows, info). Rows are dicts with 'name' plus metric values; targets dropped."""
    if name == "checkpoints":
        metrics = data["metrics"]
        rows = []
        for c in data["checkpoints"]:
            if c.get("status") == "target":
                continue
            row = {"name": c.get("label", c["id"]) + (f" ({c['name']})" if c.get("name") else ""),
                   "id": c["id"], "cs_min": c.get("cs_min"), "status": c.get("status")}
            for m in metrics:
                row[m["id"]] = (c.get("scores") or {}).get(m["id"]) if c.get("status") == "measured" else None
            rows.append(row)
        info = {"revision": data.get("test_revision"), "doc": data.get("_doc", "")}
        return metrics, rows, info
    b = data[name]
    info = {"revision": b.get("revision"), "doc": b.get("_doc", ""), "url": b.get("url")}
    return b["metrics"], [dict(m) for m in b["models"]], info


def markdown(data: dict, name: str) -> str:
    metrics, rows, info = block_rows(data, name)
    out = [f"### {name}", ""]
    if info.get("revision"):
        out.append(f"Dataset revision: `{info['revision']}`. Compare rows only within this block.")
    if info.get("doc"):
        out.append(f"Source note: {info['doc']}")
    out.append("")
    head = ["Model"] + [f"{m['label']} ({m['better']} is better)" for m in metrics]
    if name == "checkpoints":
        head.insert(1, "CS minutes")
    out.append("| " + " | ".join(head) + " |")
    out.append("|" + "---|" * len(head))
    for r in rows:
        cells = [r["name"]] + [fmt(r.get(m["id"])) for m in metrics]
        if name == "checkpoints":
            cells.insert(1, fmt(r.get("cs_min")))
        out.append("| " + " | ".join(cells) + " |")
    if name == "checkpoints":
        out.append("")
        out.append("Targets in this block are goals and are deliberately not shown.")
    return "\n".join(out) + "\n"


def colour(row: dict) -> str:
    n = row.get("name", "")
    if "Sabich" in n:
        return GOLD
    if "Jachnun" in n or row.get("id") in ("v1.0", "jachnun"):
        return ACCENT
    if row.get("ours"):
        return ACCENT_2
    return OTHER


def chart(data: dict, name: str, metric: str, out: str, title: str | None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics, rows, info = block_rows(data, name)
    meta = next((m for m in metrics if m["id"] == metric), None)
    if meta is None:
        sys.exit(f"metric {metric!r} not in block {name}: {[m['id'] for m in metrics]}")
    rows = [r for r in rows if r.get(metric) is not None]
    rows.sort(key=lambda r: r[metric], reverse=meta["better"] == "higher")
    plt.rcParams.update({"font.family": ["Inter", "DejaVu Sans"], "figure.facecolor": BG,
                         "axes.facecolor": BG, "savefig.facecolor": BG, "svg.fonttype": "none"})
    fig = plt.figure(figsize=(8, 1.9 + 0.42 * len(rows)))
    ax = fig.add_subplot(111)
    y = list(range(len(rows)))[::-1]
    vals = [r[metric] for r in rows]
    cols = [colour(r) for r in rows]
    ax.barh(y, vals, height=0.62, color=cols, edgecolor="none")
    xmax = 100 if meta["better"] == "higher" else max(vals) * 1.18
    for yi, v in zip(y, vals):
        ax.text(v + xmax * 0.012, yi, f"{v:g}%", va="center", fontsize=9, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([r.get("short") or r["name"] for r in rows], fontsize=9.5, color=INK)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(length=0, labelsize=8.5, colors=MUTED)
    ax.set_xlim(0, xmax)
    ax.xaxis.grid(True, color=LINE, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.34, right=0.95, top=1 - 1.0 / fig.get_figheight(),
                        bottom=0.75 / fig.get_figheight())
    fig.text(0.04, 1 - 0.3 / fig.get_figheight(), title or meta["label"], fontsize=15,
             weight="bold", color=INK, va="top")
    sub = f"{meta['better'].capitalize()} is better."
    if info.get("revision"):
        sub += f" Dataset revision {str(info['revision'])[:12]}."
    fig.text(0.04, 1 - 0.65 / fig.get_figheight(), sub, fontsize=9.5, color=MUTED, va="top")
    fig.text(0.04, 0.25 / fig.get_figheight(), f"Source: hebrish.app/data/results.json, block '{name}'.",
             fontsize=8, color=MUTED, va="bottom")
    fig.savefig(out, dpi=200)
    print(f"wrote {out}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=DEFAULT_SOURCE, help="URL or path of results.json")
    ap.add_argument("--block", choices=BLOCKS, help="one block (default: all)")
    ap.add_argument("--json", action="store_true", help="print rows as JSON instead of Markdown")
    ap.add_argument("--metric", help="metric id to chart (with --chart)")
    ap.add_argument("--chart", help="write a horizontal bar chart (.png or .svg); needs matplotlib")
    ap.add_argument("--title", help="chart title (default: the metric label)")
    a = ap.parse_args()
    data = load(a.source)
    if a.chart:
        if not (a.block and a.metric):
            sys.exit("--chart needs --block and --metric")
        chart(data, a.block, a.metric, a.chart, a.title)
        return
    names = [a.block] if a.block else [b for b in BLOCKS if b in data]
    if a.json:
        res = {}
        for n in names:
            metrics, rows, info = block_rows(data, n)
            res[n] = {"revision": info.get("revision"), "metrics": metrics, "rows": rows}
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print("\n".join(markdown(data, n) for n in names))


if __name__ == "__main__":
    main()
