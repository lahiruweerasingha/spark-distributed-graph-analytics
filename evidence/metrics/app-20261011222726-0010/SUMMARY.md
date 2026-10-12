# Spark metrics: indegree-bench-no-broadcast-1 (app-20261011222726-0010)

Wall-clock duration: **38.9 s**. Source: Spark history server REST API.

## Stages

Skipped stages reused cached or already-shuffled data. Task time is the
median and maximum run time of the stage's tasks; a maximum far above
the median means one partition did most of the work.

| Stage | Name | Status | Tasks | Duration (s) | Task time median / max (s) | Input (MB) | Shuffle read (MB) | Shuffle write (MB) |
|---:|---|---|---:|---:|---|---:|---:|---:|
| 0 | collect at /app/src/graph_analytics/indegree.py:67 | COMPLETE | 4 | 8.93 | 7.89 / 8.07 | 110.5 | 0.0 | 0.0 |
| 1 | collect at /app/src/graph_analytics/indegree.py:67 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 2 | collect at /app/src/graph_analytics/indegree.py:67 | COMPLETE | 1 | 0.32 | 0.18 / 0.18 | 0.0 | 0.0 | 0.0 |
| 3 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 9.85 | 9.24 / 9.71 | 110.5 | 0.0 | 0.0 |
| 4 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 0.23 | 0.15 / 0.15 | 25.0 | 0.0 | 0.0 |
| 5 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 6 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 1 | 0.05 | 0.02 / 0.02 | 0.0 | 0.0 | 0.0 |
| 7 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 8 | 1.58 | 0.90 / 1.08 | 50.0 | 0.0 | 6.7 |
| 8 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 8 | - | - | 0.0 | 0.0 | 0.0 |
| 9 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 0.84 | 0.66 / 0.73 | 0.0 | 6.7 | 0.0 |
| 10 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 8 | - | - | 0.0 | 0.0 | 0.0 |
| 11 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 12 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 1 | 0.11 | 0.04 / 0.04 | 0.0 | 0.0 | 0.0 |
| 13 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 0.87 | 0.79 / 0.82 | 25.0 | 0.0 | 4.7 |
| 14 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 15 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 16 | 0.86 | 0.13 / 0.34 | 0.0 | 4.7 | 0.0 |
| 16 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 17 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 16 | 0.26 | 0.01 / 0.02 | 3.1 | 0.0 | 0.0 |
| 18 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 19 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 20 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 1 | 0.15 | 0.08 / 0.08 | 0.0 | 0.0 | 0.0 |
| 21 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 22 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 16 | 0.45 | 0.03 / 0.08 | 3.1 | 0.0 | 0.0 |
| 23 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 1 | 0.17 | 0.09 / 0.09 | 0.0 | 0.0 | 0.0 |
| 24 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 4 | 0.86 | 0.68 / 0.75 | 25.0 | 0.0 | 4.9 |
| 25 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 16 | 0.4 | 0.02 / 0.04 | 3.1 | 0.0 | 0.0 |
| 26 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 1 | 0.09 | 0.05 / 0.05 | 0.0 | 0.0 | 0.0 |
| 27 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 28 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 29 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 30 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 1 | - | - | 0.0 | 0.0 | 0.0 |
| 31 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 32 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 1 | - | - | 0.0 | 0.0 | 0.0 |
| 33 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 4 | 0.91 | 0.55 / 0.56 | 0.0 | 4.9 | 0.0 |
| 34 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 35 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 36 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 37 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 1 | - | - | 0.0 | 0.0 | 0.0 |
| 38 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 1 | - | - | 0.0 | 0.0 | 0.0 |
| 39 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 40 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 4 | 0.38 | 0.17 / 0.18 | 0.0 | 4.9 | 0.0 |
| 41 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 42 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 43 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 44 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 1 | - | - | 0.0 | 0.0 | 0.0 |
| 45 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 1 | - | - | 0.0 | 0.0 | 0.0 |
| 46 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 47 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 48 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 1 | 0.11 | 0.07 / 0.07 | 0.0 | 0.0 | 0.0 |
| 49 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 50 | first at /app/src/graph_analytics/indegree.py:146 | COMPLETE | 16 | 1.9 | 0.16 / 1.15 | 3.1 | 0.0 | 0.1 |
| 51 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 52 | first at /app/src/graph_analytics/indegree.py:146 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 53 | first at /app/src/graph_analytics/indegree.py:146 | COMPLETE | 1 | 0.14 | 0.12 / 0.12 | 0.0 | 0.1 | 0.0 |

Total shuffle written: 16.3 MB across 13 stages.

## Work per executor

| Executor | Tasks | Task time (s) | Input (MB) | Shuffle read (MB) |
|---|---:|---:|---:|---:|
| 0 (172.27.0.4) | 64 | 49.2 | 178.8 | 5.1 |
| 1 (172.27.0.3) | 64 | 53.7 | 179.6 | 16.0 |
