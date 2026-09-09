# Synthetic Signal Detection Under Distribution Shift

This study asks whether a signal detector responds to the labelled change rather than to generator settings, plotting choices or shared recording sessions.

[Read the study](sigint-spectrum-analysis-and-covert-channel-concepts.md)

## Implementation

The waveform generator now produces 3,000 balanced sequences in thirty sessions, matched nuisance pairs, unit clean energy and a separate shifted frequency range. A statistical classifier and a small sequence CNN train on twenty sessions; thresholds are selected on five development sessions and frozen for final/shift evaluation.

## Run locally

Run from this directory with Python 3.12.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip sync --python .venv/bin/python requirements.txt
uv run --no-project --python .venv/bin/python python -m pytest -q
```

Run:

```bash
uv run --no-project --python .venv/bin/python python signal_experiment.py --seed 17 --steps 100
```

The report includes AUROC, Brier score, sequence false alarm/detection rates, per session outcomes and a session bootstrap interval. The development false alarm target is not a promise that final false alarms stay below it.

## Earlier pilot result

The statistical baseline achieved final AUROC 1.000, detection 100.0% and false alarms 4.8%. The CNN achieved AUROC 0.761, detection 56.4% and false alarms 22.0%. On the shifted set its false alarm rate reached 100.0%. A threshold satisfying the development constraint did not transfer. This is a concrete reason to keep session level reporting and the statistical baseline; it is not evidence about real radio traffic.

## Scope and limitations

The saved result is one synthetic seed, not real RF performance. Five final sessions provide limited uncertainty; the intentionally label correlated SNR audit and multi seed robustness study are still needed.

[Topic index](../README.md) · [Research index](../../README.md)

## Reproduce the comparison

From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study sigint-spectrum-analysis-and-covert-channel-concepts --profile cpu --resume
```

See [reproducing the studies](../../../tools/studies/README.md) for dependencies, data and run profiles.
