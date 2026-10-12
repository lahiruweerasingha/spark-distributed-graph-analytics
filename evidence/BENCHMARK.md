# Benchmark: caching and the broadcast join

Driver-side time spent in actions, median of repeated runs on the same cluster.

| Setting | Runs | Joins used | Median total (s) | Range (s) | vs baseline |
|---|---:|---|---:|---|---:|
| cache on, broadcast join on | 3 | Inner: BroadcastHashJoin, LeftOuter: BroadcastHashJoin | 37.2 | 35.3-38.3 | - |
| cache off | 3 | Inner: BroadcastHashJoin, LeftOuter: BroadcastHashJoin | 77.9 | 74.8-83.2 | +109% |
| broadcast join off (sort-merge join) | 3 | Inner: SortMergeJoin, LeftOuter: SortMergeJoin | 36.0 | 34.6-39.8 | -3% |

Median seconds per step:

| Step | baseline | no-cache | no-broadcast |
|---|---:|---:|---:|
| classify every line | 14.83 | 14.56 | 14.27 |
| count edges | 10.89 | 7.43 | 10.40 |
| count distinct nodes | 3.54 | 17.90 | 3.02 |
| in-degree (shuffle) | 2.28 | 8.76 | 2.35 |
| rank top N + join out-degree | 2.63 | 19.36 | 3.68 |
| distribution statistics | 2.16 | 9.69 | 2.28 |
