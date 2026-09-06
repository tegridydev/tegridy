# [td] tegridydev | Hyper Matrix Lattice: adaptive summaries and interval search

*design study and proposed evaluation*

This note contains two related but separate data-structure questions. The first is how to spend detail in a multidimensional summary tree. The second is how to locate an exact interval in a sorted numeric array. They share an interest in bounded search, but a speed claim in one does not transfer to the other.

## DATA-01 — adaptive multidimensional summaries

The minimum object is a sparse tree whose node stores half-open bounds, count, sum, children and a schema version. A binary split across `n` axes has `2^n` possible children, so the branching cost becomes part of the design very quickly.

Insertions choose exactly one child and update mergeable statistics. Means combine counts and sums, not averages of averages. Fully covered nodes can answer from their aggregate; partially covered leaves need raw observations or an explicit approximation contract. Empty cells mean missing observations, not zero-valued measurements.

Adaptive subdivision can use occupancy or variance, but variance needs enough state to compute it honestly—such as `(count, mean, M2)`—and that storage belongs in the comparison. Quantisation is also allowed only as a declared lossy step with scale, offset and error bounds. It should not silently move points across query boundaries.

The useful question is whether sparse/adaptive allocation beats a flat scan or an established range index under a stated accuracy budget. Compare uniform-depth, occupancy-adaptive and variance-adaptive trees on the same synthetic points. Measure exact-count agreement, mean error where approximation is allowed, p50/p95 query latency, build/update time and complete serialised bytes.

Start with 10,000 four-dimensional points under uniform, clustered and bursty distributions, five seeds and held-out query sets. Thresholds are selected on development data and frozen before final queries. If no configuration improves the latency/storage trade-off against the strongest simple baseline, the idea does not need rescuing with a more dramatic name.

## DATA-02 — define the interval first

For a sorted finite array `a` and half-open interval `[lo, hi)`, the exact result is every index satisfying `lo <= a[i] < hi`. Two lower-bound insertion searches already give that slice. NumPy’s `searchsorted` is therefore the obvious baseline.

That sounds trivial, but it matters because “nearest”, “inside a tolerance”, “predecessor” and “in this interval” are different problems. Signed zero, duplicates, infinities and NaNs also need stated semantics. For the first pilot I would reject non-finite inputs and keep the invariant small.

Any proposed estimator has to return exactly the same indices before speed is discussed. Test arrays of 100, 10,000 and 1,000,000 values with uniform spacing, clusters, duplicates and highly skewed gaps. Compare scan, standard binary bounds and any interpolation/learned position estimate with a verified fallback.

Measure setup cost, query latency, comparisons, fallback rate and memory for both scalar and batched queries. No method gets to ignore output enumeration when the requested interval itself is large.

The hypothesis is modest: a cheap position estimate may reduce comparisons on predictable arrays, while binary search remains the robust fallback. If wall time does not improve after setup and validation, fewer comparisons are not a practical win.

## Extensions I’d keep

A **query-budgeted refinement** policy could learn where to spend tree detail from development query shapes, then be frozen and tested under both matched and shifted workloads. This tests application-specific adaptation without claiming general superiority.

An **interval certificate** could return the two boundary positions plus neighbouring excluded values, giving downstream code a compact audit record. It still assumes the input was correctly sorted and does not replace provenance.

The naming is intentionally less important than the contract. The Hyper Matrix Lattice is an adaptive summary index, not an algebraic-lattice result; interval search is a boundary problem, not a reason to reinvent binary search unless a measured workload gives me one.

## What exists locally

A self-contained variance-refined 4D tree now complements the sorted interval reference. A fixed variance threshold controls subdivision; raw observations preserve exact answers even when a coarse leaf crosses a query boundary. Tests compare coarse/refined trees on original and shifted queries.

Start with [adaptive_tree.py](adaptive_tree.py); the [module README](README.md) lists setup, commands and every supporting file.

The same half-open count/sum convention is implemented locally in this module. Changing refinement affects traversal/storage; it does not license approximate partial-leaf answers.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
