+++
title = "Reading LLM Model Maps: Activations and Causal Evidence"
date = "2026"
description = "Read a model map without confusing architecture, measured activations and causal evidence, using a local viewer and explicit capture provenance."
draft = false
id = "blog/what-a-model-map-can-show"
type = "article"
author = "tegridydev"
topic = "model-interpretation-evaluation"
related = ["research/neuron-mapping-and-token-trajectories", "research/arithmetic-across-notations"]
updated = "2026-09-09"
+++

# Reading LLM Model Maps: Activations and Causal Evidence

The model analysis interface I keep wanting is easy to picture.

Load a model, type a prompt, watch things activate, then run a slightly different prompt and overlay the two.

Click a neuron. Follow an edge. Open the numbers behind it. Patch something and run it again.

Basically Chrome DevTools except the weird bug is somewhere inside GPT 2.

Graphix and MechaMap are some of the projects I've used to explore that direction. The important part isn't just drawing the graph; it's making sure the graph tells me **what kind of evidence I'm actually looking at**.

## one useful route through the viewer

Open the [local viewer](viewer.html) and inspect its supplied fixture. First establish whether a displayed connection describes model structure or observed activity; then inspect its identity and provenance before giving it a semantic label.

For an observed activation, the next useful step is a [compatible capture](../../../research/transformers/neuron-mapping-and-token-trajectories/README.md): checkpoint, token occurrence and component location must agree. To ask whether it matters to an answer, use a bounded [intervention scorer](../../../research/transformers/arithmetic-across-notations/README.md).

The fixture demonstrates the viewer contract. It is not a capture from an unspecified production model, and a visually striking edge is not a causal finding.

## three maps that happen to look similar

I want structure, activity and intervention evidence to stay visibly separate.

| view | defensible statement |
|---|---|
| structure | this component exists here and has this shape |
| activity | this value was observed for this input |
| intervention | changing this component changed this measured behaviour |

Those distinctions sound obvious until all three become glowing nodes and lines.

Weights are parameters. Activations are values from a particular run. Attention weights, residual vectors and MLP outputs are different measurements. An edge might mean architecture, correlation or attribution.

I don't want the UI drawing all of them the same way and letting my brain fill in the exciting story.

## the arithmetic example I keep coming back to

Take:

```text
Answer using decimal digits. 42 + 41 =
```

and:

```text
Answer using decimal digits. forty-two plus forty-one =
```

Both ask for `83`.

The tempting thing is to overlay activations and hunt for shared components.

Useful, but the prompts may have different token lengths and boundaries. `token 5` in one isn't automatically comparable with `token 5` in the other.

For a controlled comparison I'd define the role, say the final prompt position before generation, and save:

```text
run ID
model + revision
prompt ID
token position
component
measurement type
value
```

Missing stays different from zero. An interrupted capture stays incomplete.

## controls should live in the interface

Say one neuron lights up across a pile of addition prompts.

Cool.

Now test:

```text
42 + 41
42 dogs 41
forty two plus forty one
forty two dogs forty one
13 + 70
blue + chair
```

Maybe it cares about arithmetic. Maybe digits. Maybe formatting.

All are interesting. Only one is the story I wanted, so clicking a candidate should also make matched controls easy.

Visual rules matter too. Use one colour scale for compatible measurements. Don't auto scale tiny and huge changes until both look dramatic. Don't subtract coordinates from separately fitted 2D projections and pretend that's motion in the original space.

If the basis changes, say so.

Maybe literally:

```text
Comparable across layers: NOPE
```

:)

## candidate circuit is a good name

If something looks circuit ish, show:

```text
supporting prompts
component coordinates
selection rule
controls tried
interventions tried
status
```

A generated explanation can sit beside that as commentary. It isn't privileged access to the model's reasoning.

For arithmetic I'd select candidates on one prompt set, then intervene on held out digit and word form examples. Compare against random same layer components and components with similar activation magnitude.

If suppressing the candidate damages every kind of text, broad model damage is still an explanation.

If it only breaks producing `83`, maybe I found number output machinery rather than addition.

Causal arithmetic work gives good reasons to look here. Nikankin and colleagues report heuristic like arithmetic components in the models they studied. That's motivation, not permission to call every bright node an arithmetic circuit. [Nikankin et al.](https://arxiv.org/abs/2410.21272v2).

## keep the measurement attached

A run should remember model/tokeniser revisions, precision, actual tokens, hook location, generation settings and code revision.

An intervention also needs its exact rule.

`zero ablation` is different from replacing with a corpus mean. Copying an activation from another prompt requires both prompts and a reason those positions correspond.

I don't want a screenshot becoming the only surviving evidence for a precise tensor capture.

## Implementation checks and recorded findings

The capture contains 8,448 activation values across 11 tokens from a pinned model. It provides an input for the viewer with recorded provenance; a visual pattern alone does not establish a semantic feature or causal circuit.

Real pinned model activation file for manual loading in the existing viewer. No browser was opened; no circuit interpretation follows from visualising this capture.

| Recorded metric | Value |
| --- | ---: |
| recorded values | 8448 |
| tokens | 11 |

The [comparison record](comparison-results.json) includes the 1 recorded run, measured values, source hashes and dependency versions. This is a single fixed evaluation; no across seed uncertainty is estimated.

## what I built from this

The local viewer now reads activation JSON, checks occurrence identities and representation manifests, and displays raw signed values on one shared colour scale.

`null` means missing. Numeric zero is an observation.

It refuses incompatible overlays and labels truncation after 2,000 displayed records.

See [viewer.html](viewer.html), load [fixture.json](fixture.json), and run:

```sh
node test_viewer.cjs
```

for the data contract checks.

The fixture is synthetic. The viewer does not load a model, infer circuits or perform semantic token alignment.

The full workflow I want eventually is:

```text
load model
→ capture
→ overlay
→ inspect candidate
→ generate controls
→ intervene
→ rerun
→ test held-out prompts
→ export evidence
```

with every interesting thing carrying a status like `observed`, `partial`, `not tested` or `hypothesis`.

I still want the giant circuit graph, clickable neurons and cursed neural subway map. Obviously.

I just want the tool to make it slightly harder to look at a pretty graph and accidentally convince myself I've already proved the story behind it.

## reference

Yaniv Nikankin, Anja Reusch, Aaron Mueller and Yonatan Belinkov. **Arithmetic Without Algorithms: Language Models Solve Math With a Bag of Heuristics.** First submitted 28 October 2024; arXiv v2, 20 May 2025. [Paper record](https://arxiv.org/abs/2410.21272v2). DOI: `10.48550/arXiv.2410.21272`.

[Blog index](../../README.md)
