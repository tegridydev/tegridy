+++
title = "Four-dimensional summary trees and time-slice queries"
date = "2026"
description = "A saved synthetic pilot compares four-dimensional summary-tree queries with scanning and includes construction break-even costs."
draft = false
id = "research/four-dimensional-lattice"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/hyper-matrix-lattice-and-numerical-search"]
status = "pilot"
updated = "2026-09-08"
+++

# [td] tegridydev | Four-dimensional summary trees and time-slice queries

*design study and proposed evaluation*

This started as a 4D visualisation idea—three spatial axes plus time—but the useful research question is really about **when hierarchical summaries save enough repeated query work to justify building and storing the tree**. The animation can come later; first the numerical object needs to be exact.



<!-- cpu-comparison:start -->
## Results

For 10,000 clustered points, the tree answered the 100-query workload in about 8.2 ms, versus 24.2 ms for NumPy scanning and 18.9 ms for cKDTree. Counts and sums matched the reference queries. The tree was slower on several other distributions; these query timings exclude construction and do not establish a universal speed advantage.

Exact half-open 4D range summaries on five synthetic distributions; three timing repetitions per workload; no real-world latency claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| bursty-time 1000 · ckdtree seconds | 0.00407078 | 0.00036325 |
| bursty-time 1000 · numpy scan seconds | 0.00340557 | 0.00017014 |
| bursty-time 1000 · python scan seconds | 0.0309783 | 0.0015356 |
| bursty-time 1000 · tree seconds | 0.0146447 | 0.0016162 |
| bursty-time 10000 · ckdtree seconds | 0.0211595 | 0.0024464 |
| bursty-time 10000 · numpy scan seconds | 0.0277926 | 0.0010501 |
| bursty-time 10000 · python scan seconds | 0.326466 | 0.022976 |
| bursty-time 10000 · tree seconds | 0.0474208 | 0.0050091 |
| clustered 1000 · ckdtree seconds | 0.00362503 | 0.00045818 |
| clustered 1000 · numpy scan seconds | 0.0029919 | 0.00022558 |
| clustered 1000 · python scan seconds | 0.029868 | 0.0013156 |
| clustered 1000 · tree seconds | 0.00247446 | 0.0005811 |
| clustered 10000 · ckdtree seconds | 0.018893 | 0.0034471 |
| clustered 10000 · numpy scan seconds | 0.0242 | 0.0011959 |
| clustered 10000 · python scan seconds | 0.309552 | 0.020461 |
| clustered 10000 · tree seconds | 0.00819813 | 0.0019875 |
| identical 1000 · ckdtree seconds | 0.00550702 | 0.0011903 |
| identical 1000 · numpy scan seconds | 0.00363115 | 0.00054986 |
| identical 1000 · python scan seconds | 0.0310245 | 0.0016298 |
| identical 1000 · tree seconds | 0.030957 | 0.001147 |
| identical 10000 · ckdtree seconds | 0.0430606 | 0.011575 |
| identical 10000 · numpy scan seconds | 0.0304159 | 0.0054128 |
| identical 10000 · python scan seconds | 0.312664 | 0.018468 |
| identical 10000 · tree seconds | 0.310673 | 0.017007 |
| imbalanced 1000 · ckdtree seconds | 0.00245929 | 0.00048764 |
| imbalanced 1000 · numpy scan seconds | 0.00307403 | 0.00032789 |
| imbalanced 1000 · python scan seconds | 0.0296879 | 0.0018172 |
| imbalanced 1000 · tree seconds | 0.00963288 | 0.00064818 |
| imbalanced 10000 · ckdtree seconds | 0.00782288 | 0.00076623 |
| imbalanced 10000 · numpy scan seconds | 0.0249777 | 0.001086 |
| imbalanced 10000 · python scan seconds | 0.29991 | 0.017027 |
| imbalanced 10000 · tree seconds | 0.0288284 | 0.0024697 |
| uniform 1000 · ckdtree seconds | 0.00512165 | 0.00044862 |
| uniform 1000 · numpy scan seconds | 0.00361147 | 0.00020195 |
| uniform 1000 · python scan seconds | 0.0310376 | 0.0015462 |
| uniform 1000 · tree seconds | 0.0227979 | 0.00254 |
| uniform 10000 · ckdtree seconds | 0.0268896 | 0.003061 |
| uniform 10000 · numpy scan seconds | 0.0292009 | 0.0015359 |
| uniform 10000 · python scan seconds | 0.31264 | 0.018406 |
| uniform 10000 · tree seconds | 0.101076 | 0.014867 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.
<!-- cpu-comparison:end -->

## Earlier pilot results

Construction paid off for some query workloads and not others. In the saved uniform workload the tree was slower than scanning even before construction cost; clustered data had a much earlier break-even.

| Workload | Build seconds | Tree query seconds | Scan query seconds | Break-even queries |
| --- | --- | --- | --- | --- |
| uniform | 0.005046 | 0.059331 | 0.041907 | No break-even |
| clustered | 0.009060 | 0.006487 | 0.041328 | 27 |
| identical | 0.000895 | 0.039652 | 0.040185 | 168 |

Each saved workload has 1,000 points and 100 queries. This is a construction/query timing pilot, with no training. The result record does not record a seed; do not infer one from current code. Timings are environment-specific.

Records: [pilot-results.json](pilot-results.json). These values are transcribed from the saved records, not newly rerun experiments.

## The tree I actually mean

Each observation is `(x, y, z, t, value, observation_id)` inside explicit finite domains. I use half-open intervals consistently so every boundary point belongs to exactly one child. Splitting all four axes in half produces up to sixteen children, but empty regions do not need to exist.

A node stores bounds, depth, count, sum, minimum, maximum, children and optional raw observation IDs. Mean is derived from `sum / count`; an empty cell has no mean rather than a pretend zero. Aggregates are computed **before** deciding whether to split, and recursion stops on maximum depth, low occupancy, identical coordinates or a midpoint that can no longer separate values.

The invariants are more important than the picture: every valid observation belongs to exactly one leaf, and parent count/sum must equal the totals of its disjoint children.

Range queries reuse a node aggregate only when that node is completely inside the query. Disjoint nodes are ignored. Partial nodes have to descend or inspect retained raw values. A leaf mean is not enough to answer an exact subregion query—if a leaf contains values 2 and 10 on opposite sides of the query boundary, returning 6 for the side containing only 2 is simply wrong.

For time views, I’d show an interval or containing time bin rather than imply that continuous-time data naturally has meaningful exact-timestamp slices. Observation count should be visible beside colour so one sample does not look as reliable as a thousand. Visual depth and numerical query depth stay separate settings.

## The cheap comparison

Hierarchical spatial indexing is established territory, so SQLite’s R-tree is a sensible prior baseline rather than pretending that “space plus time” is new. My narrower question is whether a sparse 4D summary tree gives a useful latency/memory trade-off for repeated local interval summaries.

Start with a hand-checkable sixteen-point fixture covering all child codes, duplicates, empty cells and boundaries. Every query must match a flat scan exactly before any timing is interesting.

Then use 1,000 and 10,000 synthetic points under uniform, clustered, identical-coordinate, bursty-time and imbalanced distributions. Pre-register 100 queries per distribution, half aligned to retained cells and half cutting across them. Compare:

- flat scan;
- the sparse summary tree;
- an established range-index adapter if available.

Measure build time, p50/p95 query latency, peak memory, retained nodes and visited observations. Also report **amortisation**: a faster query is not a win if construction only pays for itself after more queries than the workload ever makes.

The prediction is intentionally workload-dependent. Clustered data with repeated cell-aligned queries should benefit most. Uniform data or tiny datasets may be better as a scan.

**What would weaken the idea:** if the tree does not beat the strongest simple baseline after construction/storage are counted, keep it as a visualisation or educational structure rather than a performance claim.

## Two useful extensions

A variance-guided display could spend rendering detail on regions with high internal variation while leaving the exact numerical tree untouched. That would test visual anomaly detection at a fixed cube budget without confusing a prettier plot with a better data structure.

A boundary-audit overlay could highlight partially intersected leaves and expose where an approximate view lacks enough resolution. That is a usability experiment, not a new query algorithm.

The part I care about most is still very simple: **the tree should never get to be fast by quietly answering a different query than the scan.**

## Implementation

The sparse sixteen-child tree now retains raw leaf observations for exact partial queries and reuses aggregates only for covered nodes. Tests cover all child codes, boundaries, duplicates, empty results and randomized scan comparisons at depths zero, one and three. A 1,000-point pilot records build and query costs.

Start with [tree.py](tree.py); the [module README](README.md) lists setup, commands and every supporting file.

The API consumes `(x,y,z,t,value)` tuples in finite half-open bounds. Duplicate coordinates remain separate observations. `pilot-results.json` records local timings; benchmark break-even is conditional on that synthetic workload.

## Earlier observations

On this machine's repeated-query pilot, the clustered workload amortized construction after approximately 27 queries. The uniform workload had no measured break-even because traversal was slower than scanning. These timings depend on two reused query shapes and are too narrow for a general speed claim. Exact counts and sums matched the scan oracle in every timed case. See the [saved result](pilot-results.json) for the exact values and run scope.

## Status

The results apply to the stated datasets and controls. Further experiments described here are proposals unless accompanied by a recorded result.

[Research index](../../README.md)
