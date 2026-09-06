"""Explicit low-rank factors with functional error and serialized-size measurements."""

import argparse
import io
import json
from pathlib import Path
import numpy as np


def factorize(weight, rank):
    weight = np.asarray(weight)
    if (
        weight.ndim != 2
        or not np.issubdtype(weight.dtype, np.floating)
        or not np.isfinite(weight).all()
    ):
        raise ValueError("finite floating matrix required")
    if type(rank) is not int or not 1 <= rank <= min(weight.shape):
        raise ValueError("invalid rank")
    u, s, vh = np.linalg.svd(weight, full_matrices=False)
    return (u[:, :rank] * s[:rank]).astype(weight.dtype), vh[:rank].astype(weight.dtype)


def report(weight, calibration, evaluation, rank):
    left, right = factorize(weight, rank)

    def error(inputs):
        exact = inputs @ weight.T
        approx = (inputs @ right.T) @ left.T
        denominator = np.linalg.norm(exact)
        return dict(
            mse=float(np.mean((exact - approx) ** 2)),
            relative_l2=float(np.linalg.norm(exact - approx) / denominator)
            if denominator
            else None,
        )

    dense = io.BytesIO()
    np.save(dense, weight, allow_pickle=False)
    packed = io.BytesIO()
    np.savez(packed, left=left, right=right)
    packed.seek(0)
    with np.load(packed, allow_pickle=False) as restored:
        reload_equal = np.array_equal(restored["left"], left) and np.array_equal(
            restored["right"], right
        )
    return dict(
        shape=list(weight.shape),
        rank=rank,
        calibration=error(calibration),
        held_out=error(evaluation),
        dense_parameters=weight.size,
        factor_parameters=left.size + right.size,
        dense_array_bytes=weight.nbytes,
        factor_array_bytes=left.nbytes + right.nbytes,
        dense_file_bytes=len(dense.getvalue()),
        factor_file_bytes=len(packed.getvalue()),
        reload_equal=bool(reload_equal),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("weight", type=Path)
    p.add_argument("calibration", type=Path)
    p.add_argument("evaluation", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--rank", required=True, type=int)
    a = p.parse_args()
    arrays = [
        np.load(path, allow_pickle=False)
        for path in [a.weight, a.calibration, a.evaluation]
    ]
    weight, calibration, evaluation = arrays
    if any(
        x.ndim != 2 or x.shape[1] != weight.shape[1] or not np.isfinite(x).all()
        for x in [calibration, evaluation]
    ):
        p.error("input matrices must match weight input width")
    left, right = factorize(weight, a.rank)
    with a.output.open("xb") as stream:
        np.savez(stream, left=left, right=right)
    print(json.dumps(report(*arrays, a.rank), indent=2, allow_nan=False))
