"""Separate variance-tree tuning from exact sorted interval search."""
import json
from pathlib import Path
import time
import pickle
import math
import numpy as np
from adaptive_tree import AdaptiveTree,summary,inside
from interval_reference import SortedIndex
from range_workloads import workloads,queries


def run(seed,data_seed,profile,output):
    output=Path(output);rows=[];metrics={}
    size=100 if profile=='smoke' else 10000
    for distribution in ['uniform','clustered','bursty-time']:
        points=workloads(seed+data_seed,size,distribution)
        development=queries(seed+data_seed+90000,10 if profile=='smoke' else 30)
        final=queries(seed+data_seed+100000,10 if profile=='smoke' else 100)
        candidates=[]
        for threshold in [0.,.05,.2,1.]:
            start=time.perf_counter();tree=AdaptiveTree(points,variance_threshold=threshold);build=time.perf_counter()-start
            start=time.perf_counter();[tree.query(q) for q in development];elapsed=time.perf_counter()-start
            candidates.append((elapsed,threshold,build,tree))
        _,threshold,build,tree=min(candidates,key=lambda x:(x[0],x[1]))
        start=time.perf_counter();answers=[tree.query(q) for q in final];elapsed=time.perf_counter()-start
        start=time.perf_counter();expected=[summary(p for p in points if inside(p[:4],q)) for q in final];scan=time.perf_counter()-start
        for a,b in zip(answers,expected):
            if (a.count,a.minimum,a.maximum)!=(b.count,b.minimum,b.maximum) or not math.isclose(a.total,b.total,abs_tol=1e-10):raise ValueError('adaptive tree query differs from scan')
        np.savez_compressed(output/(distribution+'.npz'),points=np.asarray(points),development_queries=np.asarray(development),final_queries=np.asarray(final))
        rows.append(dict(distribution=distribution,threshold=threshold,development=[dict(seconds=a,threshold=b,build_seconds=c) for a,b,c,_ in candidates],answers=[vars(a) for a in answers]))
        metrics.update({distribution+'.'+k:v for k,v in dict(tree_seconds=elapsed,scan_seconds=scan,build_seconds=build,serialized_bytes=len(pickle.dumps(tree)),selected_threshold=threshold).items()})
    rng=np.random.default_rng(seed+data_seed)
    for count in ([100] if profile=='smoke' else [100,10000,1000000]):
        for distribution in ['uniform','clustered','duplicates','skewed']:
            values=np.sort(rng.uniform(size=count) if distribution=='uniform' else rng.normal(.5,.02,count) if distribution=='clustered' else rng.integers(0,100,count).astype(float)/100 if distribution=='duplicates' else rng.exponential(.05,count))
            bounds=np.sort(rng.uniform(-.1,1.1,size=(100,2)),axis=1)
            start=time.perf_counter();index=SortedIndex(values.tolist());build=time.perf_counter()-start
            start=time.perf_counter();found=[index.bounds(float(a),float(b)) for a,b in bounds];indexed=time.perf_counter()-start
            start=time.perf_counter();expected=[np.flatnonzero((values>=a)&(values<b)) for a,b in bounds];scan=time.perf_counter()-start
            for (a,b),expected_indices in zip(found,expected):
                if not np.array_equal(np.arange(a,b),expected_indices):raise ValueError('interval differs from scan')
            prefix=f'interval_{distribution}_{count}'
            np.savez_compressed(output/(prefix+'.npz'),values=values,queries=bounds,indices=np.asarray(found))
            metrics.update({prefix+'.'+k:v for k,v in dict(build_seconds=build,indexed_seconds=indexed,scan_seconds=scan).items()})
    Path(output,'tree-comparisons.json').write_text(json.dumps(rows,indent=2)+'\n')
    return dict(scope='Development-selected variance threshold on synthetic 4D queries; separate exact binary-bounds comparison on sorted arrays. No learned estimator or real-workload latency claim.',metrics=metrics,seed=seed,data_seed=data_seed)
