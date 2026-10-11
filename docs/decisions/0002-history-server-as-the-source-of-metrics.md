# 2. Take execution metrics from the history server's REST API

**Status:** accepted

## Context

The question is not only what the in-degrees are, but how Spark computed them:
which stages ran, how long each took, how much data was shuffled, and how the
work was spread across the two workers. The live driver UI (port 4040) has all
of this, but it disappears the moment the driver exits, and this job finishes
in about a minute.

## Decision

- Every run writes a Spark event log to a shared volume, and a history server
  replays it, so finished runs stay inspectable at
  [localhost:18080](http://localhost:18080).
- `scripts/capture_metrics.py` reads the history server's REST API and saves
  the raw responses plus a readable `SUMMARY.md` (stage durations, shuffle
  volumes, work per executor) under `evidence/metrics/<application-id>/`.
- The job itself records driver-side timings of each action. Spark is lazy, so
  timing a transformation would only measure building a query plan.

## Consequences

- Numbers in the README come from the API, not from screenshots, so they can be
  re-derived from the saved JSON.
- Driver-side action timings and history-server stage durations measure
  different things (a single action can span several stages). Both are reported
  and labelled.
