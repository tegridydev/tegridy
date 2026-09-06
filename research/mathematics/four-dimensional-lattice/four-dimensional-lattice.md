# [td] tegridydev | Four-dimensional summary trees and time-slice queries

*design study and proposed evaluation*

This started as a 4D visualisation idea—three spatial axes plus time—but the useful research question is really about **when hierarchical summaries save enough repeated query work to justify building and storing the tree**. The animation can come later; first the numerical object needs to be exact.

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

## What exists locally

The sparse sixteen-child tree now retains raw leaf observations for exact partial queries and reuses aggregates only for covered nodes. Tests cover all child codes, boundaries, duplicates, empty results and randomized scan comparisons at depths zero, one and three. A 1,000-point pilot records build and query costs.

Start with [tree.py](tree.py); the [module README](README.md) lists setup, commands and every supporting file.

The API consumes `(x,y,z,t,value)` tuples in finite half-open bounds. Duplicate coordinates remain separate observations. `pilot-results.json` records local timings; benchmark break-even is conditional on that synthetic workload.

## What I actually observed

On this machine's repeated-query pilot, the clustered workload amortized construction after approximately 27 queries. The uniform workload had no measured break-even because traversal was slower than scanning. These timings depend on two reused query shapes and are too narrow for a general speed claim. Exact counts and sums matched the scan oracle in every timed case. See the [saved result](pilot-results.json) for the exact values and run scope.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
