+++
title = "Swarm Sequence Generation: Neighbour Coupling Tests"
date = "2026"
description = "Test neighbour coupling in a small finite grammar, with baseline coverage and clear boundaries around untested communication and routing proposals."
draft = false
id = "research/swarm-and-collective-agent-concepts"
type = "research-note"
author = "tegridydev"
topic = "agent-systems"
related = ["research/moa-framework"]
status = "implemented"
updated = "2026-09-09"
+++

# Swarm Sequence Generation: Neighbour Coupling Tests

I’ve accumulated a few different “swarm” ideas over time, but they are not one algorithm just because they all involve neighbours. This note keeps four mechanisms separate: sequence generation, local model communication, trainable routing and ordinary boids motion. The first one is the most useful place to start because I can check it against a tiny grammar instead of relying on vibes.

## Recorded findings

Ring coupling covered 99.75% of the changed grammar versus 99.51% for independent generation, but the other grammars showed complete coverage for both. This small fixture specific difference does not establish a consistent benefit from coupling or useful downstream training data.

SW 01 finite layered grammars; exact uniform legal set evaluation; fixed coupling, four agents, equal token budgets; no downstream training claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| changed · complete · coverage | 0.992593 | 0.016563 |
| changed · complete · elapsed seconds | 0.0038198 | 5.9789e 05 |
| changed · complete · repetition | 0.8392 | 0.0026833 |
| changed · complete · uniform grammar logprob | -1.10698 | 0.0024848 |
| changed · independent · coverage | 0.995062 | 0.006762 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## start with SW 01

The implemented study is [the finite grammar](grammar.py): four legal sequences, four agents, fixed smoothing and neighbour reweighting. Its comparison uses five seeds and 2,000 generated tokens per condition, with zero coupling versus strength two.

Likelihood counts repeated occurrences; coverage counts distinct legal sequences. Those denominators answer different questions. Four legal sequences can saturate coverage quickly, so this is a mechanism fixture rather than evidence about language generation. SW 02, SW 03 and SW 04 remain separate proposals; they should not inherit SW 01's implementation status.

## SW 01, neighbour coupled sequence generation

The basic analogy maps separation to avoiding repetition, alignment to nearby vocabulary and cohesion to a shared topic. The important implementation detail is that generated sequences must remain **ordered**. A set throws away the frequency and transition information needed for a Markov model.

Each agent gets an ID, current topic, ordered token history, neighbours, legal vocabulary and random seed. Complete sequences are saved with the generation policy and occurrence counts. Neighbour information reweights the legal next token distribution; it does not get to invent transitions outside the grammar.

**Question:** does neighbour influence improve valid sequence coverage without damaging local coherence?

Start with a finite state grammar whose legal sequences can be enumerated exactly. Compare an ordinary Markov generator, independent constrained agents and neighbour coupled agents at the same 2,000 token budget. Measure legal sequence coverage, repetition, held out transition likelihood and computation. Tune on one grammar, then evaluate on a changed grammar with separately defined legal transitions.

If coupling mostly increases copying or compute, the swarm framing is not earning its complexity. That is the portfolio falsifier for SW 01.

## SW 02, local LLM communication

Here several small model agents receive selected neighbours’ recent text before generating their own continuation. Sharing one model with different contexts is fine, but it is not the same thing as independently trained agents.

Every generation should record its input context, neighbour IDs, model revision, parent examples and label rule. Compare independent sampling, all to all shared context and a sparse neighbour graph with roughly matched token budgets. For an initial benign task, measure annotation precision, contradiction rate, near duplicates and downstream performance on independently written examples. If the agents merely become more similar to each other, that is convergence, not better data.

A useful later ablation is to save exactly which neighbour messages each output saw and rerun selected cases with those messages removed or shuffled. That tests dependence on the communication channel without pretending an agent’s explanation reveals hidden model reasoning.

## SW 03, layered token routing

This is a separate neural idea: layers produce representations and routing scores, with extra processing only when needed. Before adding dynamic populations, shared memory or agent metaphors, I’d test a tiny differentiable version on parity or sequence classification.

Compare fixed depth processing, random layer skipping and learned routing at matched average compute. Report accuracy, active layers, routing entropy and latency. Parameter hashes before and after training are only a sanity check; useful learning still needs held out performance. If operations fall but wall time does not, dispatch overhead may be the interesting result.

## SW 04, ordinary boids, honestly labelled

SWARMNET is a Pygame boids sketch built from separation, alignment, cohesion and screen wrapping. That mechanism is established prior work from Craig Reynolds. A useful continuation is an educational experiment interface exposing neighbour radius, speed limits, steering weights and boundary rules while recording seeded trajectories.

Measure nearest neighbour distance, collisions, alignment and cluster count. It can be a good visual analogy for communication topology, but spatial proximity in boids is not semantic relevance in text.

## What I’d test next

SW 01 gets the first real comparison: four agents, several neighbour topologies, five seeds and a fixed generation budget. Sequence order and transition counts should have deterministic unit tests before any modelling result is interpreted.

Two extensions are worth keeping in the backlog. One chooses most neighbours for relevance and one for deliberate disagreement, testing exploration without all to all copying. The other keeps a communication ablation ledger so any claimed benefit can be traced to the messages that were actually available.

The main lesson is simple: **“swarm” is a topology, not a result**. Each version needs its own mechanism, baseline and failure condition instead of inheriting intelligence from the metaphor.

## Implementation

SW 01 now has a finite grammar, exact legal sequence enumeration, ordered transition counts, fixed smoothing and four agents with neighbour reweighting. Five seeds compare zero coupling with strength two at exactly 2,000 generated tokens per condition.

See [grammar.py](grammar.py); the [module README](README.md) describes usage and dependencies.

Likelihood uses occurrence counts, including duplicate sequences; coverage uses distinct legal sequences. The report evaluates a uniform distribution over the four legal sequences, not a natural language corpus.

## References

- **Craig Reynolds**. [Boids: Background and Update](https://www.red3d.com/cwr/boids/). Undated author page; describes 1986 model and SIGGRAPH 1987 paper; retrieved 2026-09-05.

[Research index](../../README.md)
