# [td] tegridydev | knowledge bases should help me choose the next check

I keep technical knowledge bases because remembering a term and knowing what to do next are very different things.

The useful page gets me from:

> something here looks wrong

to:

> okay, this is the next thing I should inspect

without pretending one check proves more than it does.

Two of my public projects approach that from different directions: [Mechanistic-Interpretability](https://github.com/tegridydev/Mechanistic-Interpretability) and [physical-security-dev](https://github.com/tegridydev/physical-security-dev). The subjects stay separate; the useful design habit is the same.

## start with the actual question

In interpretability:

> which component activates here?

and:

> which component causes this behaviour?

need different evidence.

An activation view gives me a candidate. An intervention tests what happens when I change it.

Physical-security integrations have the same trap. `did this event arrive?` is different from `does this field mean what my application thinks it means?`

Perfectly valid JSON can still confuse device time with receipt time or a persistent alarm state with a one-off event. A useful knowledge base should make those distinctions hard to miss.

## keep the raw thing beside the interpretation

In [physical-security-dev's data-model guidance](https://github.com/tegridydev/physical-security-dev/blob/main/01-foundations/data-models-and-semantics.md), raw source records stay separate from parsed fields and the application's canonical model.

That lets me improve a mapping later without pretending the device originally sent something different. For a door event I'd want:

```text
raw message
device_time
received_at
device_id
mapping revision
canonical event
```

together.

The interpretability equivalent is keeping the checkpoint, prompt tokens, component location and intervention rule beside any later label. `number neuron` is shorthand, not the measurement.

## organise around routes, not encyclopaedias

The structure I tend to want is:

```text
question
↓
short orientation
↓
which method fits?
↓
worked example
↓
limitations
↓
deeper references
```

If I'm debugging a late alarm, I want the route from raw message to diagnostic decision. A giant contents tree is useful only if it gets me there faster.

## test the navigation too

Take realistic questions and ask someone to choose the next check, find the supporting passage and explain what the result would **not** establish.

Then compare a flat contents page with task-oriented routes.

If the fancy route just adds more clicking, delete it.

I especially want limitations easy to find. A confident answer that hides when it doesn't apply is actively unhelpful.

There is now a [local lexical/vector search tool](../embeddings-need-a-contract/README.md) and a [Cedar evidence fixture](../../../research/knowledge/graph-memory-with-a-paper-trail/README.md) for smaller versions of the same idea.

The external knowledge bases remain their own projects.

I don't need one giant unified system. I just want each one to do this well:

> **help me choose the next defensible check, then show me what that check actually means.**

[Blog index](../../README.md)
