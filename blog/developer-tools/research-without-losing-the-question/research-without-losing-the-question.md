# [td] tegridydev | doing research without losing the question

I like questions that start slightly sideways.

Could a different representation make this easier to inspect? Is the complicated system doing anything the little baseline isn't? What happens if I change one weird part?

The problem is that one question can quickly become a reading list, dashboard and three architectures before I've decided what would count as an answer.

At that point I'm also giving myself several creative ways to avoid the original question lol.

## turn curiosity into something that can lose

`understand how models do maths` is an interest.

This is a question:

> Do components selected using digit-form addition also matter when the same problem is written using number words?

Now I have something I can vary and something I can measure.

Before building much, I like a tiny question card:

| thing | example |
|---|---|
| question | do digit-selected components contribute to word-form addition? |
| prediction | removing them hurts more than matched random components |
| comparison | same model and operands, different notation |
| alternative | they support number output generally |
| evidence | held-out answers before/after intervention |
| stop | the untouched model can't reliably do the task |

The stop condition is underrated.

If the model can't answer the baseline questions, I don't want to spend three days explaining the mechanism behind behaviour it wasn't reliably producing.

## search for mechanisms, not the name I gave mine

The name I give an idea usually tells me very little about prior art.

Something I call `reflective memory` could overlap with retrieval, recurrent state, cache replacement or online adaptation. Those are the terms I actually need to search.

For close methods I want to know what changes, what the baseline is, what evidence is reported and how the question differs from mine.

If I can't explain the difference, I don't know enough to call my thing novel. If a simpler method already handles the problem, finding that early saves a lot of lovingly over-engineered work.

## attach evidence to claims

A bibliography tells me which sources I used.

It doesn't tell me which source supports which sentence.

So I keep a small claim ledger:

| claim | evidence | status | limit |
|---|---|---|---|
| tool saves a conversation | save-path + round-trip fixture | implementation claim | saving isn't retrieval |
| retrieved history changes an answer | paired requests | proposed test | change can still be wrong |
| memory improves accuracy | held-out comparison | hypothesis | extra context may explain it |

For papers I keep title, authors, version, URL and relevant section. For runs I keep code revision, inputs, settings and output.

W3C PROV gives useful language around entities, activities and derivation. [Groth and Moreau, 2013](https://www.w3.org/TR/prov-overview/). A recoverable table is enough to start.

## build the cheapest test that separates explanations

A pilot should help me choose between explanations, not just make my favourite one look plausible.

For arithmetic I'd first fix the answer scorer, then confirm the model solves both notation forms. Only then do activations and interventions become worth collecting.

I also like separating:

```text
development → fix the method
discovery   → choose candidates
evaluation  → test choices already made
```

Related examples stay together. A paraphrase isn't magically unseen because the wording changed.

Before final evaluation, freeze the main metric and comparison. If I change them after seeing the result, cool—that run just became development data.

A fixed seed doesn't rescue a bad metric. It only helps me reproduce it perfectly :)

## use AI where I can inspect the contribution

Models are useful for search terms, explanations, fixtures, code review and draft criticism.

A review prompt I like is:

> Which claim here is stronger than the evidence I've shown?

That's much more useful than asking whether the work seems impressive.

Generated explanations and novelty scores are still generated outputs. They don't become independent validation because they sound confident.

## finish with an answer sized to the evidence

A useful result can be positive, negative or a good reason to abandon the idea.

The write-up should say what I asked, what I compared, what happened and what else could still explain it.

I try to keep these distinctions visible:

```text
helped on this evaluation ≠ generally works
inconclusive test ≠ hypothesis is false
candidate feature ≠ mechanism found
```

They look obvious written down and get less obvious after several hours staring at an experiment.

At the end of a session I want one recoverable state and one next action.

> The scorer accepts the right digits inside a wrong explanation. Fix canonical matching before collecting activations.

That's dramatically more useful tomorrow than `continue research`.

The [arithmetic module](../../../research/transformers/arithmetic-across-notations/README.md) now has a token-boundary checker and intervention scorer, so the next hand-off there is concrete: choose the local model, record the exact hook and pass the feasibility check before ranking anything.

Still not enough to write `arithmetic circuit found` in the notes :)

## reference

Paul Groth and Luc Moreau, editors. **PROV-Overview: An Overview of the PROV Family of Documents.** W3C Working Group Note, 30 April 2013. [Full document](https://www.w3.org/TR/prov-overview/).

[Blog index](../../README.md)
