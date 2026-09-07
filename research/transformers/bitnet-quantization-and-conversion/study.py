"""Measure packed matrix bytes and scalar execution versus floating simulation."""
from pathlib import Path
import time
import numpy as np
from packed import save,load,matvec


def run(seed,data_seed,profile,output):
    rng=np.random.default_rng(seed+data_seed);metrics={};output=Path(output)
    for size in ([16] if profile=='smoke' else [32,128,512]):
        weight=rng.normal(size=(size,size)).astype(np.float32)
        scale=float(np.abs(weight).mean())
        symbols=np.clip(np.rint(weight/scale),-1,1).astype(np.int8)
        inputs=rng.normal(size=(4 if profile=='smoke' else 32,size)).astype(np.float32)
        path=output/f'{size}.tern';save(path,symbols.ravel().tolist(),symbols.shape,scale)
        header,payload=load(path)
        start=time.perf_counter();dense=inputs@weight.T;dense_time=time.perf_counter()-start
        start=time.perf_counter();simulation=inputs@(symbols.astype(np.float32)*scale).T;simulation_time=time.perf_counter()-start
        start=time.perf_counter();packed=np.asarray([matvec(header,payload,row.tolist()) for row in inputs]);packed_time=time.perf_counter()-start
        if not np.allclose(packed,simulation,atol=1e-4,rtol=1e-4):raise ValueError('packed arithmetic differs from simulation')
        np.savez_compressed(output/f'{size}-evaluation.npz',weight=weight,inputs=inputs,dense=dense,simulation=simulation,packed=packed)
        for name,value in dict(packed_file_bytes=path.stat().st_size,dense_array_bytes=weight.nbytes,quantization_mse=float(np.mean((dense-simulation)**2)),packed_simulation_mse=float(np.mean((packed-simulation)**2)),dense_seconds=dense_time,simulation_seconds=simulation_time,packed_seconds=packed_time).items():metrics[f'{size}.{name}']=value
    return dict(scope='Synthetic single-matrix conversion and actual scalar two-bit CPU execution. Complete packed file bytes are measured; float array bytes exclude a container. No trained-model quality or optimised-kernel speed claim.',metrics=metrics,seed=seed,data_seed=data_seed)
