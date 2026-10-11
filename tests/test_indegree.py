"""Tests on a hand-built graph whose answers are worked out by hand.

tests/fixtures/tiny_graph.txt has 9 valid edges between 6 nodes:

    1->2  1->3  2->3  4->3  5->3  3->1  4->1  6->2  2->5

plus 4 comment lines, 1 blank line and 3 malformed lines
("abc def", "7", "8 9 10").

    node   in-degree   out-degree
      1        2           2        (from 3, 4)
      2        2           2        (from 1, 6)
      3        4           1        (from 1, 2, 4, 5)
      4        0           2
      5        1           1        (from 2)
      6        0           1
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from graph_analytics import indegree as g

FIXTURE = str(Path(__file__).parent / "fixtures" / "tiny_graph.txt")


@pytest.fixture(scope="module")
def edges(spark):
    return g.load_edges(spark, FIXTURE).cache()


def test_published_counts_come_from_the_header():
    assert g.published_counts(FIXTURE) == g.PublishedCounts(nodes=6, edges=9)


def test_header_without_counts_is_an_error(tmp_path):
    f = tmp_path / "no_counts.txt"
    f.write_text("# just a comment\n1\t2\n")
    with pytest.raises(ValueError):
        g.published_counts(f)


def test_every_line_is_accounted_for(spark):
    assert g.line_report(spark, FIXTURE) == {"comment": 4, "blank": 1, "edge": 9, "malformed": 3}


def test_parsed_graph_matches_the_header(edges):
    g.verify_counts(
        edges=edges.count(),
        nodes=g.distinct_nodes(edges).count(),
        published=g.published_counts(FIXTURE),
    )


def test_count_mismatch_fails_loudly():
    with pytest.raises(g.CountMismatch, match="edges: parsed 8"):
        g.verify_counts(edges=8, nodes=6, published=g.PublishedCounts(nodes=6, edges=9))
    with pytest.raises(g.CountMismatch, match="nodes"):
        g.verify_counts(edges=9, nodes=7, published=g.PublishedCounts(nodes=6, edges=9))


def test_in_degree(edges):
    got = {r["node_id"]: r["in_degree"] for r in g.in_degree(edges).collect()}
    assert got == {1: 2, 2: 2, 3: 4, 5: 1}  # 4 and 6 have no incoming edges


def test_out_degree(edges):
    got = {r["node_id"]: r["out_degree"] for r in g.out_degree(edges).collect()}
    assert got == {1: 2, 2: 2, 3: 1, 4: 2, 5: 1, 6: 1}


def test_top_n_breaks_ties_by_node_id(edges):
    top = [(r["node_id"], r["in_degree"]) for r in g.top_n(g.in_degree(edges), 3).collect()]
    assert top == [(3, 4), (1, 2), (2, 2)]  # 1 and 2 tie on 2; lower id first


@pytest.mark.parametrize("broadcast", [True, False])
def test_enrichment_is_the_same_with_and_without_broadcast(edges, broadcast):
    top = g.top_n(g.in_degree(edges), 4)
    rows = g.enrich_with_out_degree(top, g.out_degree(edges), broadcast=broadcast).collect()
    assert [(r["node_id"], r["in_degree"], r["out_degree"]) for r in rows] == [
        (3, 4, 1),
        (1, 2, 2),
        (2, 2, 2),
        (5, 1, 1),
    ]


def test_top_node_without_outgoing_edges_keeps_out_degree_zero(spark):
    edges = spark.createDataFrame([(1, 9), (2, 9), (3, 9), (9, 1)], ["src", "dst"])
    edges = edges.selectExpr("cast(src as long) src", "cast(dst as long) dst")
    top = g.top_n(g.in_degree(edges.filter("src != 9")), 1)  # node 9: in 3, out 0 here
    row = g.enrich_with_out_degree(top, g.out_degree(edges.filter("src != 9"))).first()
    assert (row["node_id"], row["in_degree"], row["out_degree"]) == (9, 3, 0)


def test_join_strategy_follows_the_setting(spark, edges):
    top = g.top_n(g.in_degree(edges), 3)
    outs = g.out_degree(edges)
    previous = spark.conf.get("spark.sql.autoBroadcastJoinThreshold")
    try:
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
        forced = g.enrich_with_out_degree(top, outs, broadcast=True)
        none = g.enrich_with_out_degree(top, outs, broadcast=False)
        forced.collect(), none.collect()
    finally:
        spark.conf.set("spark.sql.autoBroadcastJoinThreshold", previous)
    # The explicit hints win even with auto-broadcast off.
    assert g.join_strategy(forced) == {
        "Inner": "BroadcastHashJoin",
        "LeftOuter": "BroadcastHashJoin",
    }
    assert g.join_strategy(none) == {"Inner": "SortMergeJoin", "LeftOuter": "SortMergeJoin"}


def test_join_strategy_reads_the_outer_final_plan_of_an_adaptive_query():
    # Shape of a real plan: a cached table nested inside carries its own
    # final/initial pair, which must not cut the outer final plan short.
    plan = "\n".join(
        [
            "AdaptiveSparkPlan isFinalPlan=true",
            "+- == Final Plan ==",
            "   SortMergeJoin [a#1], [b#2], LeftOuter",
            "   :- InMemoryRelation [a#1]",
            "   :     +- AdaptiveSparkPlan isFinalPlan=true",
            "   :        +- == Final Plan ==",
            "   :           Scan",
            "   :        +- == Initial Plan ==",
            "   :           Scan",
            "   +- BroadcastHashJoin [b#2], [c#3], Inner, BuildRight, false",
            "+- == Initial Plan ==",
            "   SortMergeJoin [a#1], [b#2], LeftOuter",
            "   +- SortMergeJoin [b#2], [c#3], Inner",
        ]
    )
    final = g._outermost_final_plan(plan)
    assert {t: s for s, t in g._JOIN.findall(final)} == {
        "LeftOuter": "SortMergeJoin",
        "Inner": "BroadcastHashJoin",
    }


def test_distribution_stats_by_hand(edges):
    s = g.distribution_stats(g.in_degree(edges))
    # in-degrees of nodes with inbound edges: 4, 2, 2, 1
    assert s["nodes_with_inbound"] == 4
    assert s["total_edges"] == 9
    assert s["mean"] == pytest.approx(2.25)
    # sample variance: (1.75^2 + 0.25^2 + 0.25^2 + 1.25^2) / 3 = 4.75 / 3
    assert s["stddev"] == pytest.approx(math.sqrt(4.75 / 3))
    assert s["median"] == pytest.approx(2.0)
    assert s["max"] == 4
    assert s["max_over_median"] == pytest.approx(2.0)
