+++
title = "Glow Worm: A Small Byte Level Language Model"
date = "2026"
description = "A small byte level language model tested on WikiText 2, with bits per byte, a unigram baseline and an explicit account of training exposure."
draft = false
id = "research/glow-worm-byte-model"
type = "research-note"
author = "tegridydev"
topic = "model-interpretation-evaluation"
related = []
status = "pilot"
updated = "2026-09-09"
+++

# Glow Worm: A Small Byte Level Language Model

glow worm is deliberately small: predict the next UTF 8 byte, measure held out probability quality and keep every part of the pipeline inspectable. A byte vocabulary avoids tokenizer mystery, but it also means one generated token is not necessarily one visible character. The first milestone is therefore a measured byte language model, not “I trained a chatbot”.

The [glow worm repository](https://github.com/tegridydev/glow-worm) is the project reference. This module contains the local byte baseline and experiment scaffolding; useful conversation would require additional data and evaluation later.

## Results

Across five initialisation seeds, held out loss averaged 3.360 bits per byte versus 4.570 for the unigram baseline. Each model used 2,097,152 training token exposures from approximately ten million available bytes. This is a bounded byte prediction result, not a full corpus training pass or a chatbot evaluation.

Pinned WikiText 2 article grouped byte study with up to roughly ten million available training bytes; fixed 512 step CPU budget, 256 byte windows, development checkpoint selection. Unigram sees the full selected corpus; Transformer training exposure is separately recorded. No chatbot quality claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| bits per byte | 3.36013 | 0.033341 |
| unigram bits per byte | 4.57022 | 0 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## Earlier pilot results

This smaller pilot used a different protocol, so its results are not directly comparable with the later experiment.

The saved byte model passed a tiny held out evaluation and checkpoint reload check. Its low training loss did not translate into similarly low held out uncertainty. This is a smoke result, not a language model quality benchmark.

| Measurement | Saved value |
| --- | --- |
| Held out bits per byte | 7.637374 |
| Evaluation bytes | 352 |
| Training/evaluation windows | 18 / 11 |
| Checkpoint reload equal | True |

Seed 1729; 40 training steps; one training document and one distinct evaluation document, identified by hashes in the record. Windows are 32 tokens, non overlapping and document local; incomplete tails are excluded. No multi corpus comparison was run.

Records: [smoke results.json](smoke-results.json). These values are transcribed from the saved records, not newly rerun experiments.

## Bytes make the contract simple, not effortless

Reserve IDs 0 to 255 for raw bytes and one separate end of document marker. Encode each document as UTF 8 and train shifted input/target pairs without crossing unrelated document boundaries.

Streaming output needs a real decoder because generation can stop halfway through a multibyte character. The UI can buffer incomplete sequences or replace invalid bytes for display, but those display choices must never silently change the raw bytes used for scoring.

The model design uses four causal Transformer blocks, width 128, four heads and a 256 byte context. Start with roughly ten million permitted bytes, deduplicate documents and split **by source document before making windows**. Close variants stay together so the final set is not just neighbouring text from training.

## Measure the representation we actually trained

The main metric is cross entropy in bits per byte, converting mean natural log loss with `ln(2)`. Compare against byte unigram and bigram baselines on the exact same scored bytes. Control tokens and document boundaries get their own accounting rather than disappearing inside the denominator.

Generation is a secondary diagnostic. Save the raw bytes, decoded view, prompt and sampling settings. Good byte loss does not establish factuality, instruction following or safety; those are different tasks.

I’d also record actual training bytes, wall time, peak memory, checkpoint bytes and throughput across several initialisation seeds. A smaller parameter count is not automatically a faster model.

## Fixtures before a larger run

Before spending compute, use ASCII, accented text, emoji, an empty document and an intentionally invalid byte sequence. Check valid round trips, causal masking, document boundaries and checkpoint reload. On a tiny fixed batch, verify that one optimisation step changes the intended parameters and can lower the objective.

The release should keep the model definition, data manifest, split IDs, configuration, curves and raw generations. That would make the project useful even if the model itself remains tiny.

**What would weaken the idea:** if byte modelling adds enough sequence length/compute overhead that a simple tokenizer baseline gives better held out quality per unit of compute, that trade off should be reported plainly. The point is inspectability, not proving bytes are universally superior.

The larger WikiText 2 comparison is now recorded above. It used about ten million available training bytes but only 2,097,152 training exposures per model. A full pass through that corpus and a broader generation evaluation remain future work. The earlier smoke fixture checks causality, byte accounting and reload behaviour.

## Implementation

The four block, width 128 causal byte Transformer now trains and reports held out bits per byte. Tests cover prefix invariance to future tokens, one batch learning and checkpoint reload. The runner accepts separate raw byte training/evaluation documents and rejects identical hashes across those partitions.

See [experiment.py](experiment.py); the [module README](README.md) describes usage and dependencies.

Optional `--training-documents train.txt --evaluation-documents heldout.txt` uses local files. Multiple filenames are accepted for each option. The report identifies document hashes and scored byte counts; byte only evaluation excludes the end of document control target.

[Research index](../../README.md)
