+++
title = "Adaptive Range Summaries and Interval Search"
date = "2026"
description = "Separate multidimensional range summaries from sorted interval search, with exact overlap checks, scan baselines and construction costs."
draft = false
id = "research/hyper-matrix-lattice-and-numerical-search"
type = "research-note"
author = "tegridydev"
topic = "architecture-experiments"
related = ["research/four-dimensional-lattice"]
status = "implemented"
updated = "2026-09-09"
+++

# Adaptive Range Summaries and Interval Search

This note contains two related but separate data structure questions. The first is how to spend detail in a multidimensional summary tree. The second is how to locate an exact interval in a sorted numeric array. They share an interest in bounded search, but a speed claim in one does not transfer to the other.

## Results

Adaptive summaries answered the clustered query workload in about 7.3 ms versus 297.6 ms for Python scanning, with about 112 ms of construction. Separately, standard sorted lookup answered the million value uniform workload in about 0.34 ms versus 215 ms scanning after about 108 ms of sorting. These are distinct algorithms and baselines; sorting benefits are not evidence for a new lattice mechanism.

Development selected variance threshold on synthetic 4D queries; separate exact binary bounds comparison on sorted arrays. No learned estimator or real workload latency claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| bursty time · build seconds | 0.0764054 | 0.0029917 |
| bursty time · scan seconds | 0.304479 | 0.0082805 |
| bursty time · tree seconds | 0.0453314 | 0.006119 |
| clustered · build seconds | 0.111862 | 0.0087565 |
| clustered · scan seconds | 0.29763 | 0.0082026 |
| clustered · tree seconds | 0.00729367 | 0.0019867 |
| interval clustered 100 · build seconds | 2.22318e 05 | 2.8317e 06 |
| interval clustered 100 · indexed seconds | 9.30832e 05 | 1.1499e 05 |
| interval clustered 100 · scan seconds | 0.000269698 | 1.4226e 05 |
| interval clustered 10000 · build seconds | 0.000910059 | 5.0677e 05 |
| interval clustered 10000 · indexed seconds | 9.87758e 05 | 8.6954e 06 |
| interval clustered 10000 · scan seconds | 0.00207253 | 0.00036734 |
| interval clustered 1000000 · build seconds | 0.11255 | 0.0031225 |
| interval clustered 1000000 · indexed seconds | 0.000160379 | 1.2382e 05 |
| interval clustered 1000000 · scan seconds | 0.232819 | 0.025842 |
| interval duplicates 100 · build seconds | 1.93672e 05 | 6.2948e 06 |
| interval duplicates 100 · indexed seconds | 9.189e 05 | 1.3583e 05 |
| interval duplicates 100 · scan seconds | 0.000275896 | 3.1791e 05 |
| interval duplicates 10000 · build seconds | 0.000909055 | 3.516e 05 |
| interval duplicates 10000 · indexed seconds | 0.000117247 | 2.1141e 05 |
| interval duplicates 10000 · scan seconds | 0.000977512 | 7.7035e 05 |
| interval duplicates 1000000 · build seconds | 0.107768 | 0.00088215 |
| interval duplicates 1000000 · indexed seconds | 0.000266851 | 2.6744e 05 |
| interval duplicates 1000000 · scan seconds | 0.0879774 | 0.0033414 |
| interval skewed 100 · build seconds | 1.79356e 05 | 2.5797e 06 |
| interval skewed 100 · indexed seconds | 8.73316e 05 | 9.943e 06 |
| interval skewed 100 · scan seconds | 0.000259185 | 1.0807e 05 |
| interval skewed 10000 · build seconds | 0.000873291 | 2.9803e 05 |
| interval skewed 10000 · indexed seconds | 9.18882e 05 | 3.5109e 06 |
| interval skewed 10000 · scan seconds | 0.00070195 | 4.0228e 05 |
| interval skewed 1000000 · build seconds | 0.103923 | 0.0031255 |
| interval skewed 1000000 · indexed seconds | 0.000203101 | 1.186e 05 |
| interval skewed 1000000 · scan seconds | 0.0934 | 0.013823 |
| interval uniform 100 · build seconds | 2.64654e 05 | 5.0099e 06 |
| interval uniform 100 · indexed seconds | 0.00020638 | 2.6335e 05 |
| interval uniform 100 · scan seconds | 0.00079019 | 8.1951e 05 |
| interval uniform 10000 · build seconds | 0.000946864 | 9.7099e 05 |
| interval uniform 10000 · indexed seconds | 0.000106163 | 1.0732e 05 |
| interval uniform 10000 · scan seconds | 0.00105988 | 0.00011119 |
| interval uniform 1000000 · build seconds | 0.108451 | 0.0017413 |
| interval uniform 1000000 · indexed seconds | 0.000337843 | 4.7367e 05 |
| interval uniform 1000000 · scan seconds | 0.214945 | 0.0075885 |
| uniform · build seconds | 0.0767104 | 0.0020161 |
| uniform · scan seconds | 0.301659 | 0.0070093 |
| uniform · tree seconds | 0.0979578 | 0.014598 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## refinement is not an interval search result

The [adaptive tree fixture](test_adaptive_tree.py) uses two points with values 2 and 10 in different halves of the first coordinate. A coarse node and a refined node both return mean 2 for the left query and mean 10 for the right query. Refinement changes storage, not the exact partial overlap answer.

Sorted interval search is a separate problem with a separate representation and cost model. A faster interval lookup would not validate variance driven refinement, just as equal tree answers do not establish a speed advantage. Keep construction cost and workload shape beside either timing claim.

## DATA 01, adaptive multidimensional summaries

The minimum object is a sparse tree whose node stores half open bounds, count, sum, children and a schema version. A binary split across `n` axes has `2^n` possible children, so the branching cost becomes part of the design very quickly.

Insertions choose exactly one child and update mergeable statistics. Means combine counts and sums, not averages of averages. Fully covered nodes can answer from their aggregate; partially covered leaves need raw observations or an explicit approximation contract. Empty cells mean missing observations, not zero valued measurements.

Adaptive subdivision can use occupancy or variance, but variance needs enough state to compute it honestly, such as `(count, mean, M2)`, and that storage belongs in the comparison. Quantisation is also allowed only as a declared lossy step with scale, offset and error bounds. It should not silently move points across query boundaries.

The useful question is whether sparse/adaptive allocation beats a flat scan or an established range index under a stated accuracy budget. Compare uniform depth, occupancy adaptive and variance adaptive trees on the same synthetic points. Measure exact count agreement, mean error where approximation is allowed, p50/p95 query latency, build/update time and complete serialised bytes.

Start with 10,000 four dimensional points under uniform, clustered and bursty distributions, five seeds and held out query sets. Thresholds are selected on development data and frozen before final queries. If no configuration improves the latency/storage trade off against the strongest simple baseline, the idea does not need rescuing with a more dramatic name.

## DATA 02, define the interval first

For a sorted finite array `a` and half open interval `[lo, hi)`, the exact result is every index satisfying `lo <= a[i] < hi`. Two lower bound insertion searches already give that slice. NumPy’s `searchsorted` is therefore the obvious baseline.

That sounds trivial, but it matters because “nearest”, “inside a tolerance”, “predecessor” and “in this interval” are different problems. Signed zero, duplicates, infinities and NaNs also need stated semantics. For the first pilot I would reject non finite inputs and keep the invariant small.

Any proposed estimator has to return exactly the same indices before speed is discussed. Test arrays of 100, 10,000 and 1,000,000 values with uniform spacing, clusters, duplicates and highly skewed gaps. Compare scan, standard binary bounds and any interpolation/learned position estimate with a verified fallback.

Measure setup cost, query latency, comparisons, fallback rate and memory for both scalar and batched queries. No method gets to ignore output enumeration when the requested interval itself is large.

The hypothesis is modest: a cheap position estimate may reduce comparisons on predictable arrays, while binary search remains the robust fallback. If wall time does not improve after setup and validation, fewer comparisons are not a practical win.

## Extensions I’d keep

A **query budgeted refinement** policy could learn where to spend tree detail from development query shapes, then be frozen and tested under both matched and shifted workloads. This tests application specific adaptation without claiming general superiority.

An **interval certificate** could return the two boundary positions plus neighbouring excluded values, giving downstream code a compact audit record. It still assumes the input was correctly sorted and does not replace provenance.

The naming is intentionally less important than the contract. The Hyper Matrix Lattice is an adaptive summary index, not an algebraic lattice result; interval search is a boundary problem, not a reason to reinvent binary search unless a measured workload gives me one.

## Implementation

A self contained variance refined 4D tree now complements the sorted interval reference. A fixed variance threshold controls subdivision; raw observations preserve exact answers even when a coarse leaf crosses a query boundary. Tests compare coarse/refined trees on original and shifted queries.

See [adaptive_tree.py](adaptive_tree.py); the [module README](README.md) describes usage and dependencies.

The same half open count/sum convention is implemented locally in this module. Changing refinement affects traversal/storage; it does not license approximate partial leaf answers.

[Research index](../../README.md)
