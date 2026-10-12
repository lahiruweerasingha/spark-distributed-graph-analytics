"""In-degree analysis of a directed edge list in SNAP format.

SNAP edge lists are plain text: a few `#` comment lines (including one that
states the published node and edge counts), then one `source<TAB>target` pair
per line. Every function here takes and returns Spark DataFrames so each step
can be tested on a small graph with a known answer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

_COUNTS = re.compile(r"Nodes:\s*(\d+)\s+Edges:\s*(\d+)")


class CountMismatch(ValueError):
    """The parsed graph does not match the counts the file says it contains."""


@dataclass(frozen=True)
class PublishedCounts:
    nodes: int
    edges: int


def published_counts(path: str | Path, max_header_lines: int = 20) -> PublishedCounts:
    """Read the `# Nodes: N Edges: E` line from the file's own header."""
    with open(path, encoding="utf-8") as handle:
        for _, line in zip(range(max_header_lines), handle, strict=False):
            if not line.startswith("#"):
                break
            match = _COUNTS.search(line)
            if match:
                return PublishedCounts(nodes=int(match.group(1)), edges=int(match.group(2)))
    raise ValueError(f"no 'Nodes: N Edges: E' line in the header of {path}")


def _classified_lines(spark: SparkSession, path: str) -> DataFrame:
    """Every line of the file, labelled comment / blank / edge / malformed.

    A line is an edge only if it has exactly two whitespace-separated tokens
    that both parse as integers. Anything else is malformed, and counted
    rather than silently dropped.
    """
    trimmed = F.trim(F.col("value"))
    parts = F.split(trimmed, r"\s+")
    src = parts.getItem(0).cast("long")
    dst = parts.getItem(1).cast("long")
    kind = (
        F.when(trimmed.startswith("#"), "comment")
        .when(trimmed == "", "blank")
        .when((F.size(parts) == 2) & src.isNotNull() & dst.isNotNull(), "edge")
        .otherwise("malformed")
    )
    return spark.read.text(path).select(kind.alias("kind"), src.alias("src"), dst.alias("dst"))


def line_report(spark: SparkSession, path: str) -> dict[str, int]:
    """How many lines of each kind the file has."""
    counts = {
        r["kind"]: r["count"]
        for r in _classified_lines(spark, path).groupBy("kind").count().collect()
    }
    return {k: counts.get(k, 0) for k in ("comment", "blank", "edge", "malformed")}


def load_edges(spark: SparkSession, path: str) -> DataFrame:
    """Edges as (src, dst) longs. Lazy: nothing is read until an action runs."""
    return _classified_lines(spark, path).filter(F.col("kind") == "edge").select("src", "dst")


def verify_counts(edges: int, nodes: int, published: PublishedCounts) -> None:
    """Fail loudly if the parsed graph is not the graph the file describes."""
    problems = []
    if edges != published.edges:
        problems.append(f"edges: parsed {edges:,}, published {published.edges:,}")
    if nodes != published.nodes:
        problems.append(f"nodes: parsed {nodes:,}, published {published.nodes:,}")
    if problems:
        raise CountMismatch("; ".join(problems))


def distinct_nodes(edges: DataFrame) -> DataFrame:
    return (
        edges.select(F.col("src").alias("node_id"))
        .union(edges.select(F.col("dst").alias("node_id")))
        .distinct()
    )


def in_degree(edges: DataFrame) -> DataFrame:
    """In-degree of every node with at least one incoming edge.

    A wide transformation: rows sharing a destination must meet on one
    executor, so Spark shuffles here: the job's main shuffle. (Reading and
    parsing the text file costs far more; see evidence/BENCHMARK.md.)
    """
    return edges.groupBy(F.col("dst").alias("node_id")).agg(F.count(F.lit(1)).alias("in_degree"))


def out_degree(edges: DataFrame) -> DataFrame:
    return edges.groupBy(F.col("src").alias("node_id")).agg(F.count(F.lit(1)).alias("out_degree"))


def top_n(degrees: DataFrame, n: int) -> DataFrame:
    """The n highest in-degrees; node id breaks ties so the ranking is deterministic."""
    return degrees.orderBy(F.col("in_degree").desc(), F.col("node_id").asc()).limit(n)


def enrich_with_out_degree(top: DataFrame, outs: DataFrame, broadcast: bool = True) -> DataFrame:
    """Add out-degree to the top nodes; a node with no outgoing edges gets 0.

    Two steps, because Spark cannot broadcast the preserved side of an outer
    join:
      1. Filter the large out-degree table down to the top nodes with an INNER
         join. With `broadcast=True` the n top ids are copied to every executor
         and each one filters its own partitions: no shuffle of the large side.
      2. Left-join that small result back onto `top`, so nodes that were not
         matched (no outgoing edges) are kept with out-degree 0. Both sides
         have at most n rows; with `broadcast=True` the matched side is
         broadcast too, so this step shuffles nothing either.
    """
    ids = top.select("node_id")
    matched = outs.join(F.broadcast(ids) if broadcast else ids, on="node_id", how="inner")
    return (
        top.join(F.broadcast(matched) if broadcast else matched, on="node_id", how="left")
        .select("node_id", "in_degree", F.coalesce("out_degree", F.lit(0)).alias("out_degree"))
        .orderBy(F.col("in_degree").desc(), F.col("node_id").asc())
    )


def distribution_stats(degrees: DataFrame) -> dict[str, float | int | None]:
    """Exact summary of the in-degree distribution (nodes with inbound edges)."""
    row = degrees.agg(
        F.count(F.lit(1)).alias("nodes_with_inbound"),
        F.sum("in_degree").alias("total_edges"),
        F.mean("in_degree").alias("mean"),
        F.stddev("in_degree").alias("stddev"),
        F.expr("percentile(in_degree, 0.5)").alias("median"),
        F.expr("percentile(in_degree, 0.99)").alias("p99"),
        F.max("in_degree").alias("max"),
    ).first()
    stats = row.asDict()
    stats["max_over_median"] = stats["max"] / stats["median"] if stats["median"] else None
    return stats


_JOIN = re.compile(
    r"(BroadcastHashJoin|SortMergeJoin|ShuffledHashJoin) \[[^\]]*\], \[[^\]]*\], (\w+)"
)


def _outermost_final_plan(plan: str) -> str:
    """The part of a plan's text that describes what actually executed.

    After an adaptive query has run, its plan text holds a final and an
    initial plan. Cached tables inside it carry their own nested pairs, so the
    outer pair is found by indentation, not by the first marker.
    """
    lines = plan.splitlines()
    start = next((i for i, line in enumerate(lines) if "== Final Plan ==" in line), None)
    if start is None:
        return plan
    column = lines[start].index("== Final Plan ==")
    for end in range(start + 1, len(lines)):
        if lines[end].find("== Initial Plan ==") == column:
            return "\n".join(lines[start:end])
    return "\n".join(lines[start:])


def join_strategy(df: DataFrame) -> dict[str, str]:
    """The physical join Spark used for each join type, e.g. {"Inner": "BroadcastHashJoin"}.

    Evidence that a setting took effect. Read it after the DataFrame has run,
    so adaptive execution has settled on its final plan.
    """
    plan = _outermost_final_plan(df._jdf.queryExecution().executedPlan().toString())
    return {join_type: strategy for strategy, join_type in _JOIN.findall(plan)}
