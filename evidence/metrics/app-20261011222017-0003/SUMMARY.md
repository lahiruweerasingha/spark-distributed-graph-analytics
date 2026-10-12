# Spark metrics: indegree-default (app-20261011222017-0003)

Wall-clock duration: **36.0 s**. Source: Spark history server REST API.

## Stages

Skipped stages reused cached or already-shuffled data. Task time is the
median and maximum run time of the stage's tasks; a maximum far above
the median means one partition did most of the work.

| Stage | Name | Status | Tasks | Duration (s) | Task time median / max (s) | Input (MB) | Shuffle read (MB) | Shuffle write (MB) |
|---:|---|---|---:|---:|---|---:|---:|---:|
| 0 | collect at /app/src/graph_analytics/indegree.py:67 | COMPLETE | 4 | 9.11 | 8.04 / 8.31 | 110.5 | 0.0 | 0.0 |
| 1 | collect at /app/src/graph_analytics/indegree.py:67 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 2 | collect at /app/src/graph_analytics/indegree.py:67 | COMPLETE | 1 | 0.35 | 0.21 / 0.21 | 0.0 | 0.0 | 0.0 |
| 3 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 9.44 | 8.89 / 9.37 | 110.5 | 0.0 | 0.0 |
| 4 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 0.23 | 0.16 / 0.16 | 25.0 | 0.0 | 0.0 |
| 5 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 6 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 1 | 0.07 | 0.03 / 0.03 | 0.0 | 0.0 | 0.0 |
| 7 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 8 | 2.01 | 0.86 / 1.16 | 50.0 | 0.0 | 6.7 |
| 8 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 8 | - | - | 0.0 | 0.0 | 0.0 |
| 9 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 0.88 | 0.69 / 0.76 | 0.0 | 6.7 | 0.0 |
| 10 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 8 | - | - | 0.0 | 0.0 | 0.0 |
| 11 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 12 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 1 | 0.07 | 0.04 / 0.04 | 0.0 | 0.0 | 0.0 |
| 13 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 4 | 1.09 | 0.99 / 1.03 | 25.0 | 0.0 | 4.7 |
| 14 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 15 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 16 | 0.8 | 0.15 / 0.41 | 0.0 | 4.7 | 0.0 |
| 16 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 17 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 16 | 0.26 | 0.01 / 0.02 | 3.1 | 0.0 | 0.0 |
| 18 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 19 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 20 | count at NativeMethodAccessorImpl.java:0 | COMPLETE | 1 | 0.08 | 0.03 / 0.03 | 0.0 | 0.0 | 0.0 |
| 21 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 4 | 0.66 | 0.52 / 0.53 | 25.0 | 0.0 | 4.9 |
| 22 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 23 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 16 | 0.46 | 0.03 / 0.09 | 3.1 | 0.0 | 0.0 |
| 24 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 1 | 0.09 | 0.04 / 0.04 | 0.0 | 0.0 | 0.0 |
| 25 | collect at /app/jobs/run_indegree.py:48 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 26 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 4 | 0.37 | 0.29 / 0.30 | 0.0 | 4.9 | 0.0 |
| 27 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 28 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 16 | 0.27 | 0.02 / 0.04 | 3.1 | 0.0 | 0.0 |
| 29 | collect at /app/jobs/run_indegree.py:48 | COMPLETE | 1 | 0.21 | 0.15 / 0.15 | 0.0 | 0.0 | 0.0 |
| 30 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 31 | first at /app/src/graph_analytics/indegree.py:146 | COMPLETE | 16 | 1.64 | 0.15 / 1.09 | 3.1 | 0.0 | 0.1 |
| 32 | count at NativeMethodAccessorImpl.java:0 | SKIPPED | 4 | - | - | 0.0 | 0.0 | 0.0 |
| 33 | first at /app/src/graph_analytics/indegree.py:146 | SKIPPED | 16 | - | - | 0.0 | 0.0 | 0.0 |
| 34 | first at /app/src/graph_analytics/indegree.py:146 | COMPLETE | 1 | 0.14 | 0.12 / 0.12 | 0.0 | 0.1 | 0.0 |

Total shuffle written: 16.3 MB across 10 stages.

## Work per executor

| Executor | Tasks | Task time (s) | Input (MB) | Shuffle read (MB) |
|---|---:|---:|---:|---:|
| 0 (172.27.0.4) | 68 | 52.2 | 181.1 | 7.6 |
| 1 (172.27.0.3) | 55 | 51.0 | 177.2 | 8.7 |
