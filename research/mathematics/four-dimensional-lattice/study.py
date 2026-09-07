"""Distinct-query exactness and cost comparison; all inputs and answers are saved."""
import json
import math
import pickle
import random
import statistics
import time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from tree import Tree, summary, inside


from range_workloads import workloads, queries


def timed(call, repeats=3):
    times = []
    value = None
    for _ in range(repeats):
        start = time.perf_counter()
        value = call()
        times.append(time.perf_counter() - start)
    return value, times


def run(seed, data_seed, profile, output):
    output = Path(output)
    rows, metrics = [], {}
    for size in ([100] if profile == 'smoke' else [1000, 10000]):
        for distribution in ['uniform', 'clustered', 'identical', 'bursty-time', 'imbalanced']:
            points = workloads(data_seed + seed, size, distribution)
            bounds = queries(data_seed + seed + 100000, 10 if profile == 'smoke' else 100)
            array = np.asarray(points)
            tree, build = timed(lambda: Tree(points))
            kd, kd_build = timed(lambda: cKDTree(array[:, :4]))
            def scan(q):
                return summary(p for p in points if inside(p[:4], q))
            def vector_scan(q):
                q = np.asarray(q)
                return summary(array[((array[:, :4] >= q[:, 0]) & (array[:, :4] < q[:, 1])).all(1)])
            def indexed(q):
                q = np.asarray(q)
                center = q.mean(1)
                radius = np.nextafter(((q[:, 1] - q[:, 0]) / 2).max(), np.inf)
                candidates = array[kd.query_ball_point(center, radius, p=np.inf)]
                return summary(candidates[((candidates[:, :4] >= q[:, 0]) & (candidates[:, :4] < q[:, 1])).all(1)])
            answers, timings = {}, {}
            for name, function in [('python_scan', scan), ('numpy_scan', vector_scan), ('tree', tree.query), ('ckdtree', indexed)]:
                answers[name], timings[name] = timed(lambda: [function(q) for q in bounds])
            for name, values in answers.items():
                for expected, actual in zip(answers['python_scan'], values):
                    if expected.count != actual.count or not math.isclose(expected.total, actual.total, rel_tol=1e-10, abs_tol=1e-10) or (expected.minimum, expected.maximum) != (actual.minimum, actual.maximum):
                        raise ValueError('incorrect answer from ' + name)
            prefix = f'{distribution}_{size}'
            np.savez_compressed(output / (prefix + '.npz'), points=array, queries=np.asarray(bounds))
            savings = (statistics.median(timings['numpy_scan']) - statistics.median(timings['tree'])) / len(bounds)
            row = dict(distribution=distribution, count=size, queries=len(bounds), aligned_queries=len(bounds)//2,
                       build_seconds=build, ckdtree_build_seconds=kd_build, query_seconds=timings,
                       serialized_tree_bytes=len(pickle.dumps(tree)), serialized_ckdtree_bytes=len(pickle.dumps(kd)),
                       break_even_against_numpy=math.ceil(statistics.median(build)/savings) if savings>0 else None,
                       answers={k:[vars(a) for a in v] for k,v in answers.items()})
            rows.append(row)
            for name, values in timings.items():
                metrics[f'{prefix}.{name}_seconds'] = statistics.median(values)
            metrics[prefix+'.correct_queries'] = len(bounds)
    (output / 'comparisons.json').write_text(json.dumps(rows, indent=2, allow_nan=False)+'\n')
    return dict(scope='Exact half-open 4D range summaries on five synthetic distributions; three timing repetitions per workload; no real-world latency claim.', metrics=metrics,
                seed=seed, data_seed=data_seed, profile=profile, workloads=len(rows),
                timing='Warm process, two-thread environment; repeated timing trials are not independent datasets. Serialized size is not peak resident memory.')
