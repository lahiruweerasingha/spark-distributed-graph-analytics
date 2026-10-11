# 1. Fail fast if the parsed graph is not the graph the file describes

**Status:** accepted

## Context

A SNAP edge list starts with comment lines, one of which states the graph's
size (`# Nodes: 685230 Edges: 7600595`). Parsing goes wrong quietly: a header
filter that misses a comment line turns it into a malformed row, a split on
the wrong separator yields nulls that are then dropped, and every later number
is computed on the wrong graph without any error.

The first version of this analysis printed `match=False` and carried on.

## Decision

- The expected node and edge counts are read **from the file's own header**
  (`published_counts`), not hard-coded, so the same check works for any SNAP
  edge list.
- Every line is classified as comment, blank, edge or malformed. A line is an
  edge only if it has exactly two integer tokens. The counts of each kind are
  recorded (`line_report`), so nothing is dropped silently.
- `verify_counts` raises `CountMismatch` if the parsed edges or distinct nodes
  differ from the header. The job stops there, before any analysis runs.

## Consequences

- A wrong parse cannot produce a plausible-looking result.
- The check costs two extra Spark actions (a line classification and a distinct
  node count). Both are timed and reported with the rest of the run.
