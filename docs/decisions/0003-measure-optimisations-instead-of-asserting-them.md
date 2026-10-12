# 3. Measure the optimisations instead of asserting them

**Status:** accepted

## Context

The job uses two standard optimisations:

- **Caching.** The edge list and the in-degree table are each reused by
  several actions; without a cache Spark recomputes them from the file every time.
- **A broadcast join.** The top-N nodes (a few dozen rows) are copied to every
  executor to filter the out-degree table, instead of shuffling both sides.

The original version of this analysis described the broadcast join as "the
single highest-leverage optimisation", without measuring it. There is a reason
to doubt that: Spark broadcasts small tables automatically (below
`spark.sql.autoBroadcastJoinThreshold`, 10 MB by default), so an explicit hint
on a 50-row table may change nothing. (The benchmark compares the hint with
all broadcasting switched off; it does not separate the hint from Spark's
automatic broadcast, so that narrower question stays open.)

## Decision

- Both optimisations are switches (`CACHE`, `BROADCAST`).
- With `BROADCAST=0`, automatic broadcasting is also turned off, so the
  comparison really is broadcast vs sort-merge join. The physical plan's join
  strategy is recorded with every run as proof the setting took effect.
- `make benchmark` runs each setting several times on the same cluster and
  reports the **median and range**, because single timings on a laptop are
  noisy. Results are in `evidence/BENCHMARK.md`.

## Result

Driver-side time in actions, median of 3 runs per setting:

| Setting | Median (s) | Range (s) | vs baseline | Joins Spark used |
|---|---:|---|---:|---|
| cache on, broadcast join on | 37.2 | 35.3–38.3 | - | Inner: BroadcastHashJoin, LeftOuter: BroadcastHashJoin |
| cache off | 77.9 | 74.8–83.2 | +109% | Inner: BroadcastHashJoin, LeftOuter: BroadcastHashJoin |
| broadcast join off (sort-merge join) | 36.0 | 34.6–39.8 | -3% | Inner: SortMergeJoin, LeftOuter: SortMergeJoin |

- **Caching is what matters.** Without it every action re-reads and re-parses the 110 MB text file, and the job takes 2.1 times as long. The node count goes from 3.5 s to 17.9 s.
- **The broadcast join makes no measurable difference to the total.** On its own step it saves about 1.1 s (2.63 s vs 3.68 s), which is inside the run-to-run noise of the whole job. Without it Spark plans 54 stages instead of 35 (counting skipped ones). It writes the same 16.3 MB of shuffle data but reads 21.2 MB instead of 16.3 MB ([baseline](../../evidence/metrics/app-20261011222100-0004/SUMMARY.md), [no broadcast](../../evidence/metrics/app-20261011222726-0010/SUMMARY.md); first run of each setting). The out-degree table is already partitioned by node id from its own aggregation, so the sort-merge join does not repartition it, but it reads that table's 4.9 MB of shuffle output a second time.

## Consequences

- The README states what was measured, including where an optimisation made
  little difference.
- `tests/test_indegree.py` checks that the join strategy follows the setting
  and that the result is identical either way.
