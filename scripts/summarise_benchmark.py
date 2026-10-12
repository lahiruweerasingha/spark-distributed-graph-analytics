"""Summarise `make benchmark` runs into evidence/benchmark.json and BENCHMARK.md.

Each setting was run several times; the median is reported along with the
range, because single timings on a shared laptop are noisy.
"""

from __future__ import annotations

import json
import os
import re
import statistics
from collections import defaultdict
from pathlib import Path

EVIDENCE = Path(os.getenv("EVIDENCE_DIR", "/app/evidence"))
LABELS = {
    "baseline": "cache on, broadcast join on",
    "no-cache": "cache off",
    "no-broadcast": "broadcast join off (sort-merge join)",
}


def main() -> None:
    runs = defaultdict(list)
    for path in sorted((EVIDENCE / "runs").glob("bench-*.json")):
        match = re.fullmatch(r"bench-(.+)-\d+\.json", path.name)
        if not match:  # not a benchmark run file
            continue
        runs[match.group(1)].append(json.loads(path.read_text()))

    summary = {}
    for name, items in runs.items():
        totals = [r["total_action_seconds"] for r in items]
        steps = defaultdict(list)
        for r in items:
            for step, value in r["timings_seconds"].items():
                steps[step].append(value)
        summary[name] = {
            "description": LABELS.get(name, name),
            "runs": len(items),
            # e.g. "Inner: BroadcastHashJoin, LeftOuter: BroadcastHashJoin"
            "join_strategies": sorted(
                {
                    ", ".join(f"{t}: {j}" for t, j in sorted(r["join_strategy"].items()))
                    for r in items
                }
            ),
            "total_seconds_median": statistics.median(totals),
            "total_seconds_min": min(totals),
            "total_seconds_max": max(totals),
            "step_seconds_median": {s: statistics.median(v) for s, v in steps.items()},
        }
    (EVIDENCE / "benchmark.json").write_text(json.dumps(summary, indent=2) + "\n")

    base = summary.get("baseline", {}).get("total_seconds_median")
    order = [n for n in ("baseline", "no-cache", "no-broadcast") if n in summary]
    lines = [
        "# Benchmark: caching and the broadcast join",
        "",
        "Driver-side time spent in actions, median of repeated runs on the same cluster.",
        "",
        "| Setting | Runs | Joins used | Median total (s) | Range (s) | vs baseline |",
        "|---|---:|---|---:|---|---:|",
    ]
    for name in order:
        s = summary[name]
        is_base = name == "baseline"
        delta = f"{(s['total_seconds_median'] / base - 1):+.0%}" if base and not is_base else "-"
        lines.append(
            f"| {s['description']} | {s['runs']} | {'; '.join(s['join_strategies'])} | "
            f"{s['total_seconds_median']:.1f} | {s['total_seconds_min']:.1f}-"
            f"{s['total_seconds_max']:.1f} | {delta} |"
        )
    # Steps in the order the job runs them.
    steps = list(summary[order[0]]["step_seconds_median"]) if order else []
    lines += [
        "",
        "Median seconds per step:",
        "",
        "| Step | " + " | ".join(order) + " |",
        "|---|" + "---:|" * len(order),
    ]
    for step in steps:
        cells = [f"{summary[n]['step_seconds_median'].get(step, float('nan')):.2f}" for n in order]
        lines.append(f"| {step} | " + " | ".join(cells) + " |")
    (EVIDENCE / "BENCHMARK.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
