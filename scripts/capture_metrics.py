"""Capture a finished run's metrics from the Spark history server.

    make metrics

Writes the raw REST responses to evidence/metrics/<application-id>/ and a
readable summary (stage durations, task-time spread, shuffle volumes,
per-executor work) to evidence/metrics/<application-id>/SUMMARY.md. Taking
numbers from the REST API rather than screenshots keeps them exact and
reproducible.

The application is the one recorded in evidence/runs/$RUN_TAG.json (or
$APP_ID). The history server picks up new event logs every few seconds, so
asking it for "the latest application" straight after a run can return the
previous one; this waits for the right one instead.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HISTORY = os.getenv("HISTORY_URL", "http://spark-history:18080")
API = f"{HISTORY}/api/v1"
EVIDENCE = Path(os.getenv("EVIDENCE_DIR", "/app/evidence"))
RUN_TAG = os.getenv("RUN_TAG", "default")
WAIT_SECONDS = 120


def get(path: str):
    with urllib.request.urlopen(f"{API}{path}", timeout=60) as response:
        return json.loads(response.read())


def seconds(stage: dict) -> float | None:
    try:
        fmt = "%Y-%m-%dT%H:%M:%S.%f%Z"
        start = datetime.strptime(stage["firstTaskLaunchedTime"], fmt)
        end = datetime.strptime(stage["completionTime"], fmt)
        return round((end - start).total_seconds(), 2)
    except (KeyError, ValueError):
        return None


def wait_for(app_id: str) -> dict:
    """The application's record, once the history server has it as completed."""
    deadline = time.monotonic() + WAIT_SECONDS
    while True:
        try:
            app = get(f"/applications/{app_id}")
            if app["attempts"][0].get("completed"):
                return app
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise
        if time.monotonic() > deadline:
            raise SystemExit(f"{app_id} not in the history server after {WAIT_SECONDS} s")
        time.sleep(3)


def task_spread(app_id: str, stage: dict) -> tuple[float, float] | None:
    """Median and maximum task run time (s) of a completed stage: shows skew."""
    if stage["status"] != "COMPLETE":
        return None
    summary = get(
        f"/applications/{app_id}/stages/{stage['stageId']}/{stage['attemptId']}"
        "/taskSummary?quantiles=0.5,1.0"
    )
    median, maximum = summary["executorRunTime"]
    return median / 1000, maximum / 1000


def main() -> int:
    app_id = os.getenv("APP_ID")
    if not app_id:
        run = json.loads((EVIDENCE / "runs" / f"{RUN_TAG}.json").read_text())
        app_id = run["application_id"]
    application = wait_for(app_id)

    out = EVIDENCE / "metrics" / app_id
    out.mkdir(parents=True, exist_ok=True)
    raw = {
        "application": application,
        "jobs": get(f"/applications/{app_id}/jobs"),
        "stages": get(f"/applications/{app_id}/stages"),
        "executors": get(f"/applications/{app_id}/allexecutors"),
    }
    for name, data in raw.items():
        (out / f"{name}.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    app = raw["application"]
    duration = app["attempts"][0]["duration"] / 1000
    stages = sorted(raw["stages"], key=lambda s: s["stageId"])
    lines = [
        f"# Spark metrics: {app['name']} ({app_id})",
        "",
        f"Wall-clock duration: **{duration:.1f} s**. Source: Spark history server REST API.",
        "",
        "## Stages",
        "",
        "Skipped stages reused cached or already-shuffled data. Task time is the",
        "median and maximum run time of the stage's tasks; a maximum far above",
        "the median means one partition did most of the work.",
        "",
        "| Stage | Name | Status | Tasks | Duration (s) | Task time median / max (s) "
        "| Input (MB) | Shuffle read (MB) | Shuffle write (MB) |",
        "|---:|---|---|---:|---:|---|---:|---:|---:|",
    ]
    spreads = {}
    for s in stages:
        spread = task_spread(app_id, s)
        spreads[s["stageId"]] = spread
        duration_text = seconds(s) if seconds(s) is not None else "-"
        spread_text = f"{spread[0]:.2f} / {spread[1]:.2f}" if spread else "-"
        lines.append(
            f"| {s['stageId']} | {s['name'][:40]} | {s['status']} | {s['numTasks']} | "
            f"{duration_text} | {spread_text} | "
            f"{s.get('inputBytes', 0) / 1e6:.1f} | {s.get('shuffleReadBytes', 0) / 1e6:.1f} | "
            f"{s.get('shuffleWriteBytes', 0) / 1e6:.1f} |"
        )
    lines += [
        "",
        f"Total shuffle written: {sum(s.get('shuffleWriteBytes', 0) for s in stages) / 1e6:.1f} MB "
        f"across {sum(1 for s in stages if s.get('shuffleWriteBytes'))} stages.",
        "",
        "## Work per executor",
        "",
        "| Executor | Tasks | Task time (s) | Input (MB) | Shuffle read (MB) |",
        "|---|---:|---:|---:|---:|",
    ]
    workers = [e for e in raw["executors"] if e["id"] != "driver"]
    for e in workers:
        lines.append(
            f"| {e['id']} ({e['hostPort'].split(':')[0]}) | {e['totalTasks']} | "
            f"{e['totalDuration'] / 1000:.1f} | {e['totalInputBytes'] / 1e6:.1f} | "
            f"{e['totalShuffleRead'] / 1e6:.1f} |"
        )
    (out / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "task_spread.json").write_text(
        json.dumps({str(k): v for k, v in spreads.items()}, indent=2) + "\n", encoding="utf-8"
    )
    print("\n".join(lines))
    print(f"\nwritten to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
