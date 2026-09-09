# Reproducing the studies

The articles include supporting code and compact comparison records. Use uv with the committed dependency lock and Python 3.12. From the repository root:

```sh
uv run --locked --project tools/studies python -B tools/studies/runner.py run --list
uv run --locked --project tools/studies python -B tools/studies/runner.py check
uv run --locked --project tools/studies python -B tools/studies/runner.py run --study four-dimensional-lattice --profile cpu --resume
uv run --locked --project tools/studies python -B tools/studies/runner.py report
```

The environment uses CPU only PyTorch. Runs execute sequentially with two numerical threads. `--profile cpu` selects the workload described by each study; `--profile smoke` is an integration check and must not be treated as a research comparison. These commands do not start a website or publish results.

## Models and corpus

Studies that use pretrained models or WikiText require explicit acquisition:

```sh
uv run --locked --project tools/studies python -B tools/studies/assets.py all
uv run --locked --project tools/studies python -B tools/studies/corpus.py
```

The asset receipts pin model and dataset revisions and file hashes. Subsequent model loading uses the downloaded, verified files without remote code. WikiText preserves the official partitions and reconstructed article boundaries. Model weights and dataset text are not bundled with the repository; consult the recorded source licences.

## Seeds, evidence and interpretation

`register.json` declares the per study seeds and protocol. The default seed list is 17, 29, 43, 59 and 71, with data seed 1729 recorded separately. `--seed` selects one run. Some evaluations are deterministic; changing the seed label does not make them independent scientific samples.

Each article's `comparison-results.json` records measured values, source hashes, dependency versions, scope, seeds and execution measurements. Original pilot files use their own workloads and must not be pooled with later results. A successful execution establishes neither a missing causal control nor real world generalisation. The arithmetic feasibility failure, negative comparisons and catalogue proposals remain explicit.

Generated artifacts are written to `tools/_runs/<study>/<identity>/<attempt>/`, including raw predictions or event records where supplied by the adapter. Checkpoints and full run artifacts are not distributed. Linux/WSL peak process memory is reported in KiB.

The source fingerprint identifies the code used for a recorded run. Later source changes may produce a new identity; do not relabel historical results as measurements of changed code.

## Execution and recovery

`--timeout` limits each worker, defaulting to 3,600 seconds. `--resume` skips only completed runs with matching configuration and intact artifact hashes. It does not resume an optimiser halfway through training. Failures retain their logs and unsuccessful status.

Workers use temporary storage before archiving artifacts. The recorded comparisons used Linux RAM backed scratch storage via `TMPDIR=/dev/shm`. Select this only where sufficient shared memory is available. Storage choice is part of the run identity and affects timing; these runs do not establish power loss durability.

The `_runs/.runner-lock/owner.json` file identifies an active runner. Following a forced termination, confirm that the runner and worker have stopped before removing a stale lock. If artifact copying fails, recover the receipt's `working_directory` before deleting temporary files.

`run --all` also reports entries without automated comparisons: Minecraft is an interactive demonstration, two entries are catalogues, and PDF fidelity needs a labelled eighteen layout family corpus. The command returns a nonzero status while those entries remain pending; inspect individual receipts to distinguish this from a failed worker.


