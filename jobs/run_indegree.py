"""In-degree analysis of the web-BerkStan graph on the Spark cluster.

    make run                        default: cache on, broadcast join on
    make benchmark                  repeats the run with each optimisation off

Settings (environment variables):
    EDGE_FILE   path to the SNAP edge list           default /data/web-BerkStan.txt
    TOP_N       how many top nodes to report         default 50
    CACHE       1/0: cache the reused DataFrames     default 1
    BROADCAST   1/0: broadcast the top-node join     default 1
    RUN_TAG     name for this run's evidence file    default "default"
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from pyspark.sql import SparkSession

from graph_analytics import indegree as g

EDGE_FILE = os.getenv("EDGE_FILE", "/data/web-BerkStan.txt")
TOP_N = int(os.getenv("TOP_N", "50"))
CACHE = os.getenv("CACHE", "1") == "1"
BROADCAST = os.getenv("BROADCAST", "1") == "1"
RUN_TAG = os.getenv("RUN_TAG", "default")
EVIDENCE = Path(os.getenv("EVIDENCE_DIR", "/app/evidence"))


def main() -> int:
    builder = SparkSession.builder.appName(f"indegree-{RUN_TAG}")
    if not BROADCAST:
        # Also stop Spark from choosing a broadcast join on its own, so the
        # comparison really is broadcast vs shuffle.
        builder = builder.config("spark.sql.autoBroadcastJoinThreshold", "-1")
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    timings: dict[str, float] = {}

    def timed(label, action):
        # Spark is lazy: only actions do work, so only actions are timed.
        start = time.perf_counter()
        result = action()
        timings[label] = round(time.perf_counter() - start, 2)
        print(f"  {label:<40} {timings[label]:>8.2f}s", flush=True)
        return result

    published = g.published_counts(EDGE_FILE)
    lines = timed("classify every line", lambda: g.line_report(spark, EDGE_FILE))

    edges = g.load_edges(spark, EDGE_FILE)
    if CACHE:
        edges = edges.cache()  # reused by four actions below
    edge_count = timed("count edges", edges.count)
    node_count = timed("count distinct nodes", lambda: g.distinct_nodes(edges).count())
    g.verify_counts(edge_count, node_count, published)  # stops the job on any mismatch

    degrees = g.in_degree(edges)
    if CACHE:
        degrees = degrees.cache()  # reused by the ranking and the statistics
    timed("in-degree (shuffle)", degrees.count)

    top = g.top_n(degrees, TOP_N)
    enriched = g.enrich_with_out_degree(top, g.out_degree(edges), broadcast=BROADCAST)
    rows = timed("rank top N + join out-degree", enriched.collect)
    # Read after running: with adaptive execution the final plan can differ
    # from the one planned up front.
    strategy = g.join_strategy(enriched)
    stats = timed("distribution statistics", lambda: g.distribution_stats(degrees))

    summary = {
        "run_tag": RUN_TAG,
        "application_id": spark.sparkContext.applicationId,
        "settings": {"cache": CACHE, "broadcast": BROADCAST, "top_n": TOP_N},
        "join_strategy": strategy,
        "published": {"nodes": published.nodes, "edges": published.edges},
        "parsed": {"nodes": node_count, "edges": edge_count},
        "lines": lines,
        "distribution": stats,
        "top": [r.asDict() for r in rows],
        "timings_seconds": timings,
        "total_action_seconds": round(sum(timings.values()), 2),
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    out = EVIDENCE / "runs" / f"{RUN_TAG}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(f"\nedges {edge_count:,} / nodes {node_count:,}: match the published counts")
    print(f"join strategy: {strategy}")
    print(
        f"median in-degree {stats['median']:,.0f}, mean {stats['mean']:.2f}, max {stats['max']:,}"
    )
    print(f"evidence -> {out}")
    spark.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
