# Face-based attention circuits: a controlled feature-mixing study

FBAC tests whether context-dependent mixing of fixed feature slices improves a small selection task beyond added dense capacity.

[Read the study](face-based-attention-circuits.md)

## Included implementation

FBAC now trains beside base, dense-adapter and static-mixture controls on frozen operand-pair splits. The implementation checks the exact 4,420-parameter mixer, gate gradients and checkpoint reloads. Final evaluation includes gate permutations within the same task mode and across modes.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

Run the tool or experiment after setup:

```bash
uv run --no-project --python .venv/bin/python python experiment.py --steps 40
```

All four task modes for an operand pair stay together. Noise is resampled after pair allocation. Gate swaps intervene on computed mixture weights while preserving the recipient features and projections.

## Earlier pilot result

In the saved 40-step, seed-1729 run, FBAC accuracy was 34.2%, compared with 34.4% for the dense adapter and 32.8% for the base model. Within-mode gate swaps gave 34.0%; cross-mode swaps gave 34.6%. These small, mixed differences do not support a gate-specific advantage. The useful next experiment is a sufficiently trained, multi-seed comparison with matched interventions.

## Files

- [experiment.py](experiment.py) — Runnable implementation.
- [face-based-attention-circuits.md](face-based-attention-circuits.md) — Article.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [smoke-results.json](smoke-results.json) — Recorded synthetic run; scope and provenance included.
- [test_experiment.py](test_experiment.py) — Local regression checks.

## Remaining work

The original saved pilot is one seed and forty steps. The separate CPU comparison adds five seeds and layout/swap evaluations, but still lacks a matched-magnitude gate intervention. Small accuracy differences do not establish a feature-mixing advantage.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the bounded CPU comparison

From the repository source root (the folder containing `blog`, `research` and `tools`):

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study face-based-attention-circuits --profile cpu --resume
```

See the [study execution guide](../../../tools/studies/README.md) for pinned asset acquisition, declared seeds, artifact locations and workload limits. The adapter writes raw evidence and a scope statement; a completed run does not establish claims outside that scope. `--profile smoke` checks integration only.

## Recorded findings

FBAC averaged 82.34% on the ordinary final split, below the base model at 89.06%. Under the layout shift it averaged 58.59%, close to the dense control at 58.83% and below the static gate at 59.80%. The swap comparisons do not supply the missing matched-magnitude causal control.

See the [article](face-based-attention-circuits.md) for methods and interpretation, and the [comparison record](comparison-results.json) for all conditions, seeds and measured values.
