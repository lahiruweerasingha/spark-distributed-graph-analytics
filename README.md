# Distributed in-degree analysis of a web graph with Spark

Spark job that parses the 7.6-million-edge Berkeley–Stanford web graph on a
two-worker standalone cluster, verifies it against the counts the file
publishes, ranks the most-linked pages, and measures (rather than assumes)
what caching and a broadcast join actually buy.

Originally developed as part of my MSc Data Science at Coventry University, then extended into a standalone project.

## Results

From a run on the full graph ([`evidence/runs/default.json`](evidence/runs/default.json)):

| | |
|---|---|
| Edges / distinct nodes parsed | 7,600,595 / 685,230, identical to the counts in the file's header |
| Lines in the file | 7,600,599: 7,600,595 edges, 4 comments, 0 blank, 0 malformed |
| Nodes with at least one incoming link | 617,094 (90%) |
| In-degree: median / mean / 99th percentile / max | 2 / 12.32 / 111 / 84,208 |
| Max ÷ median | 42,104× |
| Most-linked page | node 438238: 84,208 incoming links, 82 outgoing |
| Run time on the cluster | 36 s for the whole application ([metrics](evidence/metrics/app-20261011222017-0003/SUMMARY.md)) |

**The distribution is extremely skewed, but the shuffle is not.** Half the
pages that are linked to at all have 2 incoming links or fewer and 99%
have at most 111, while one page has 84,208. That might be expected to
overload whichever task receives the hub. It doesn't, because `groupBy().count()`
is pre-aggregated on each executor before the shuffle, so the hub arrives as
one partial count per input partition. The in-degree shuffle moved
4.7 MB for 7.6 million edges, and its slowest task took 0.41 s
against a median of 0.15 s ([stage metrics](evidence/metrics/app-20261011222017-0003/SUMMARY.md)). Skew
would matter for an operation that cannot be pre-aggregated, such as joining
edges to page data on the destination.

**What the optimisations bought** ([`evidence/BENCHMARK.md`](evidence/BENCHMARK.md)):

Driver-side time in actions, median of 3 runs per setting:

| Setting | Median (s) | Range (s) | vs baseline | Joins Spark used |
|---|---:|---|---:|---|
| cache on, broadcast join on | 37.2 | 35.3–38.3 | - | Inner: BroadcastHashJoin, LeftOuter: BroadcastHashJoin |
| cache off | 77.9 | 74.8–83.2 | +109% | Inner: BroadcastHashJoin, LeftOuter: BroadcastHashJoin |
| broadcast join off (sort-merge join) | 36.0 | 34.6–39.8 | -3% | Inner: SortMergeJoin, LeftOuter: SortMergeJoin |

- **Caching is what matters.** Without it every action re-reads and re-parses the 110 MB text file, and the job takes 2.1 times as long. The node count goes from 3.5 s to 17.9 s.
- **The broadcast join makes no measurable difference to the total.** On its own step it saves about 1.1 s (2.63 s vs 3.68 s), which is inside the run-to-run noise of the whole job. Without it Spark plans 54 stages instead of 35 (counting skipped ones). It writes the same 16.3 MB of shuffle data but reads 21.2 MB instead of 16.3 MB ([baseline](evidence/metrics/app-20261011222100-0004/SUMMARY.md), [no broadcast](evidence/metrics/app-20261011222726-0010/SUMMARY.md); first run of each setting). The out-degree table is already partitioned by node id from its own aggregation, so the sort-merge join does not repartition it, but it reads that table's 4.9 MB of shuffle output a second time.

## Architecture

```mermaid
flowchart LR
    F[(web-BerkStan.txt<br/>7.6M edges)] --> C[classify lines<br/>comment / blank / edge / malformed]
    C --> V{counts match<br/>the file header?}
    V -->|no| X[fail the job]
    V -->|yes| I[in-degree<br/>groupBy dst: shuffle]
    I --> T[top N]
    T --> J[broadcast join<br/>out-degree]
    I --> S[distribution statistics]
    J --> E[evidence/runs/*.json]
    S --> E
    subgraph Spark standalone: 1 master, 2 workers x 2 cores / 2 GB
        C
        I
        T
        J
        S
    end
    H[history server] --> M[capture_metrics.py<br/>evidence/metrics/]
```

| Component | Version |
|---|---|
| Apache Spark | 3.5.9, standalone cluster, history server |
| Python | 3.10 (in the Spark image) |
| Docker Compose | the whole cluster; nothing installed on the host |

## Quickstart

Requirements: Docker, GNU make, and `sh`, `curl` and `gzip` on the host for
`make data` (all present in Git Bash, macOS and Linux).

On Linux, the job writes `evidence/` as the image's `spark` user (uid 185).
Docker Desktop on Windows and macOS maps this automatically; on a native
Linux host, make the folder writable first (`chmod -R a+w evidence`).

```bash
make data        # download web-BerkStan from SNAP (20 MB compressed)
make up          # build the image, start master, 2 workers, history server
make run         # run the analysis, then capture metrics from the history server
make benchmark   # each optimisation switched off in turn, repeated 3 times
make test        # 15 tests on a hand-built graph, in the Spark image
make down
```

| UI | URL |
|---|---|
| Spark master (workers, running applications) | http://localhost:8080 |
| History server (DAGs, stages, executors of finished runs) | http://localhost:18080 |

## Key design decisions

Short decision records are in [`docs/decisions/`](docs/decisions).

1. **Fail fast against the published counts**
   ([ADR 1](docs/decisions/0001-fail-fast-against-the-published-counts.md)).
   Every line is classified, and the job stops if the parsed edge or node count
   differs from the file's own header, instead of analysing the wrong graph.
2. **Metrics from the history server's REST API**
   ([ADR 2](docs/decisions/0002-history-server-as-the-source-of-metrics.md)).
   The driver UI disappears when a one-minute job ends; event logs and the
   history server keep every run inspectable, and the numbers are saved as JSON.
3. **Measure the optimisations instead of asserting them**
   ([ADR 3](docs/decisions/0003-measure-optimisations-instead-of-asserting-them.md)).
   Caching and the broadcast join are switches. With broadcasting off, Spark's
   automatic broadcast is disabled too, and each run records the join strategy
   Spark actually used, read from the final plan after the query has run.

## What checking the evidence caught

- **A silently dropped node.** In the original version, enriching the top nodes
  with their out-degree used an inner join, so a top node with **no** outgoing
  links would have disappeared. It is now a broadcast filter followed by a left
  join with the small matched side broadcast (Spark cannot broadcast the
  preserved side of an outer join), with a test for exactly that case.
- **A wrong join-strategy report.** The first benchmark recorded
  `SortMergeJoin` for every setting. The plan text of an adaptive query holds
  a final and an initial plan, and the cached tables inside it carry their own
  nested pairs; the parser stopped at a nested marker and missed the broadcast
  join. It now finds the outer final plan by indentation, reports every join by
  type, and has a test built from that plan shape.
- **Metrics from the previous run.** `make metrics` asked the history server for
  its latest application straight after a run, before it had picked up the
  new event log, and saved the previous run's metrics. It now reads the
  application id from the run's own evidence file and waits for it.

## Project layout

```
src/graph_analytics/indegree.py   parsing, verification, degrees, top N, join, statistics
jobs/run_indegree.py              the cluster job: timings, verification, evidence
scripts/capture_metrics.py        history server REST API -> evidence/metrics/
scripts/summarise_benchmark.py    benchmark runs -> evidence/BENCHMARK.md
tests/                            hand-built graph with answers worked out by hand
evidence/                         measured outputs
docs/decisions/                   architecture decision records
```

## Known limitations

- **A laptop cluster.** Two workers with 2 cores and 2 GB each, on one machine,
  demonstrate distribution but not network cost between machines. Timings are
  noisy, which is why the benchmark reports medians of repeated runs.
- **One dataset.** The parsing is written for SNAP edge lists; other formats
  would need their own line classification.
- **Driver-side timings** measure each action end to end and are not the same
  as the history server's per-stage durations; both are reported and labelled.

## What I would do next

1. **PageRank** with GraphFrames, which weights a link by the importance of the
   page it comes from, compared with plain in-degree.
2. **Skew mitigation**: salt the hub keys before the shuffle and measure the
   effect on the slowest task.
3. **A larger graph** (for example the full SNAP web-Google or a Common Crawl
   host graph) on a real multi-machine cluster.
