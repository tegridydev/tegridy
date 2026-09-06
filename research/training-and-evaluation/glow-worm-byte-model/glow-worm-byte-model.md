# [td] tegridydev | glow-worm: an inspectable byte-language-model baseline

*research proposal*

glow-worm is deliberately small: predict the next UTF-8 byte, measure held-out probability quality and keep every part of the pipeline inspectable. A byte vocabulary avoids tokenizer mystery, but it also means one generated token is not necessarily one visible character. The first milestone is therefore a measured byte language model, not “I trained a chatbot”.

The [glow-worm repository](https://github.com/tegridydev/glow-worm) is the project reference. This module contains the local byte baseline and experiment scaffolding; useful conversation would require additional data and evaluation later.

## Bytes make the contract simple, not effortless

Reserve IDs 0–255 for raw bytes and one separate end-of-document marker. Encode each document as UTF-8 and train shifted input/target pairs without crossing unrelated document boundaries.

Streaming output needs a real decoder because generation can stop halfway through a multibyte character. The UI can buffer incomplete sequences or replace invalid bytes for display, but those display choices must never silently change the raw bytes used for scoring.

A proposed first model is four causal Transformer blocks, width 128, four heads and a 256-byte context. Start with roughly ten million permitted bytes, deduplicate documents and split **by source document before making windows**. Close variants stay together so the final set is not just neighbouring text from training.

## Measure the representation we actually trained

The main metric is cross-entropy in bits per byte, converting mean natural-log loss with `ln(2)`. Compare against byte unigram and bigram baselines on the exact same scored bytes. Control tokens and document boundaries get their own accounting rather than disappearing inside the denominator.

Generation is a secondary diagnostic. Save the raw bytes, decoded view, prompt and sampling settings. Good byte loss does not establish factuality, instruction following or safety; those are different tasks.

I’d also record actual training bytes, wall time, peak memory, checkpoint bytes and throughput across several initialisation seeds. A smaller parameter count is not automatically a faster model.

## Fixtures before a larger run

Before spending compute, use ASCII, accented text, emoji, an empty document and an intentionally invalid byte sequence. Check valid round trips, causal masking, document boundaries and checkpoint reload. On a tiny fixed batch, verify that one optimisation step changes the intended parameters and can lower the objective.

The release should keep the model definition, data manifest, split IDs, configuration, curves and raw generations. That would make the project useful even if the model itself remains tiny.

**What would weaken the idea:** if byte modelling adds enough sequence-length/compute overhead that a simple tokenizer baseline gives better held-out quality per unit of compute, that trade-off should be reported plainly. The point is inspectability, not proving bytes are universally superior.

The ten-million-byte study is still the real next step. The current smoke fixture is mainly there to prove that the causal model, byte accounting and reload path behave the way the article says they do.

## What exists locally

The four-block, width-128 causal byte Transformer now trains and reports held-out bits per byte. Tests cover prefix invariance to future tokens, one-batch learning and checkpoint reload. The runner accepts separate raw-byte training/evaluation documents and rejects identical hashes across those partitions.

Start with [experiment.py](experiment.py); the [module README](README.md) lists setup, commands and every supporting file.

Optional `--training-documents train.txt --evaluation-documents heldout.txt` uses local files. Multiple filenames are accepted for each option. The report identifies document hashes and scored byte counts; byte-only evaluation excludes the end-of-document control target.

## What I actually observed

The saved run scores 352 held-out byte targets at 7.637 bits per byte. Its final training loss is much lower than its held-out loss, which is unsurprising for repeated training on a tiny document. A uniform 256-byte baseline assigns eight bits per byte; this comparison alone is weak evidence because the learned model and unigram baselines must also be compared on the exact same scored bytes and document groups. See the [saved result](smoke-results.json) for the exact values and run scope.

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
