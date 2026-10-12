# Spark metrics: indegree-bench-baseline-1 (app-20261011222100-0004)

Wall-clock duration: **41.0 s**. Source: Spark history server REST API.

## Stages

Skipped stages reused cached or already-shuffled data. Task time is the
median and maximum run time of the stage's tasks; a maximum far above
the median means one partition did most of the work.

| Stage | Name | Status | Tasks | Duration (s) | Task time median / max (s) | Input (MB) | Shuffle read (MB) | Shuffle write (MB) |
|---:|---|---|---:|---:|---|---:|---:|---:|
| 0 | collect at /app/src/graph_analytics/indegree.py:67 | COMPLETE | 4 | 10.07 | 8.54 / 8.91 | 110.5 | 0.0 | 0.0 |
| 1 | collect at /app/src/graph_analytics/indegree.py:67 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 2 | collect at /app/src/graph_analytics/indegree.py:67 | COMPLETE | 1 | 0.26 | 0.15 / 0.15 | 0.0 | 0.0 | 0.0 |
| 3 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 10.09 | 9.51 / 9.90 | 110.5 | 0.0 | 0.0 |
| 4 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 0.17 | 0.10 / 0.10 | 25.0 | 0.0 | 0.0 |
| 5 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 6 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 1 | 0.14 | 0.09 / 0.09 | 0.0 | 0.0 | 0.0 |
| 7 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 8 | 2.2 | 1.29 / 1.57 | 50.0 | 0.0 | 6.7 |
| 8 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 8 | - | - | 0.0 | 0.0 | 0.0 |
| 9 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 0.82 | 0.69 / 0.75 | 0.0 | 6.7 | 0.0 |
| 10 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 8 | - | - | 0.0 | 0.0 | 0.0 |
| 11 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 12 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 1 | 0.09 | 0.04 / 0.04 | 0.0 | 0.0 | 0.0 |
| 13 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 0.77 | 0.66 / 0.70 | 25.0 | 0.0 | 4.7 |
| 14 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 15 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 16 | 0.86 | 0.15 / 0.32 | 0.0 | 4.7 | 0.0 |
| 16 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 17 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 16 | 0.23 | 0.01 / 0.03 | 3.1 | 0.0 | 0.0 |
| 18 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 19 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 20 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 1 | 0.08 | 0.03 / 0.03 | 0.0 | 0.0 | 0.0 |
| 21 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 4 | 0.95 | 0.81 / 0.83 | 25.0 | 0.0 | 4.9 |
| 22 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 23 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 16 | 0.47 | 0.03 / 0.08 | 3.1 | 0.0 | 0.0 |
| 24 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 1 | 0.09 | 0.03 / 0.03 | 0.0 | 0.0 | 0.0 |
| 25 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 26 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 4 | 0.39 | 0.33 / 0.34 | 0.0 | 4.9 | 0.0 |
| 27 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 28 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 16 | 0.26 | 0.02 / 0.03 | 3.1 | 0.0 | 0.0 |
| 29 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 1 | 0.12 | 0.08 / 0.08 | 0.0 | 0.0 | 0.0 |
| 30 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 31 | first at /app/src/graph_analytics/indegree.py:146 | COMPLETE | 16 | 1.7 | 0.13 / 1.11 | 3.1 | 0.0 | 0.1 |
| 32 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 33 | first at /app/src/graph_analytics/indegree.py:146 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 34 | first at /app/src/graph_analytics/indegree.py:146 | COMPLETE | 1 | 0.21 | 0.19 / 0.19 | 0.0 | 0.1 | 0.0 |

Total shuffle written: 16.3 MB across 10 stages.

## Work per executor

| Executor | Tasks | Task time (s) | Input (MB) | Shuffle read (MB) |
|---|---:|---:|---:|---:|
| 0 (172.27.0.4) | 62 | 56.2 | 184.7 | 7.3 |
| 1 (172.27.0.3) | 61 | 54.2 | 173.7 | 9.0 |
