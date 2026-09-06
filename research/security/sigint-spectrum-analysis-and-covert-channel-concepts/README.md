# Signal detection under nuisance and session shift

This study asks whether a signal detector responds to the labelled change rather than to generator settings, plotting choices or shared recording sessions.

[Read the study](sigint-spectrum-analysis-and-covert-channel-concepts.md)

## Included implementation

The waveform generator now produces 3,000 balanced sequences in thirty sessions, matched nuisance pairs, unit clean energy and a separate shifted frequency range. A statistical classifier and a small sequence CNN train on twenty sessions; thresholds are selected on five development sessions and frozen for final/shift evaluation.

## Run locally

Use Python 3.11 or newer. Run these commands from this article folder; each module keeps its own imports and dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

Run the tool or experiment after setup:

```bash
python3 signal_experiment.py --seed 17 --steps 100
```

The report includes AUROC, Brier score, sequence false-alarm/detection rates, per-session outcomes and a session bootstrap interval. The development false-alarm target is not a promise that final false alarms stay below it.

## Local result

The statistical baseline achieved final AUROC 1.000, detection 100.0% and false alarms 4.8%. The CNN achieved AUROC 0.761, detection 56.4% and false alarms 22.0%. On the shifted set its false-alarm rate reached 100.0%. A threshold satisfying the development constraint did not transfer. This is a concrete reason to keep session-level reporting and the statistical baseline; it is not evidence about real radio traffic.

## Files

- [pilot-results.json](pilot-results.json) — Recorded synthetic run; scope and provenance included.
- [requirements.txt](requirements.txt) — Runtime and test dependencies.
- [sigint-spectrum-analysis-and-covert-channel-concepts.md](sigint-spectrum-analysis-and-covert-channel-concepts.md) — Article.
- [signal_experiment.py](signal_experiment.py) — Runnable implementation.
- [test_signal.py](test_signal.py) — Local regression checks.

## Remaining work

The saved result is one synthetic seed, not real RF performance. Five final sessions provide limited uncertainty; the intentionally label-correlated-SNR audit and multi-seed robustness study are still needed.

[Topic index](../README.md) · [Research index](../../README.md)
