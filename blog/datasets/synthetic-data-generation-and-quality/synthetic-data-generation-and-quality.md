# [td] tegridydev | making synthetic data I can actually check

Generating another thousand examples is the easy part.

Working out whether they're actually useful is where I want to spend more time.

I've played with DataWRT, SynData and [data-m8](https://github.com/tegridydev/data-m8), but the common question is simpler:

**can I independently explain why each accepted example is right?**

## start somewhere with a boring correct answer

For the first experiment I like tiny synthetic worlds where the answer doesn't depend on another model's opinion.

An inventory item starts with 12 units, receives 5 and ships 4.

The answer is 13.

```python
def remaining_stock(start, received, shipped):
    if any(type(v) is not int or v < 0 for v in (start, received, shipped)):
        raise ValueError("stock movements must be non-negative integers")
    if shipped > start + received:
        raise ValueError("shipment exceeds available stock")
    return start + received - shipped
```

Now a generator can rewrite the question, but it doesn't get to decide the answer.

That gives me one independent check. A correct `13` attached to a misleading question is still bad data.

## keep the ugly raw response

For every candidate I want the source-state ID, generator/template revision, settings, raw response, parsed fields, verifier result and final disposition.

Failed generations count too.

Otherwise I can generate 1,000 attempts, quietly throw away 700 broken ones and tell myself I made a wonderfully clean 300-row dataset :)

Rewrites keep parent IDs, and cache keys include model, prompt, settings and source state. A cache saves a call; it doesn't prove correctness.

## polished reasoning can still be wrong

I also don't want one magic quality score.

Longer reasoning isn't automatically better. Fancy wording isn't automatically better. A model judge can prefer the same confident mistake the generator likes.

A useful calibration pair is:

```text
short + correct
long + wrong
```

then reverse the writing style.

If the filter follows style instead of correctness, that's important to know before training anything on it.

[Self-Instruct](https://arxiv.org/abs/2212.10560) is useful prior work. My narrower interest is making source state → generated wording → accepted row easy to inspect.

## split the world before rewriting it

Every paraphrase of the same source state belongs in the same split.

Otherwise the model can train on:

> 12 units arrived, 4 shipped...

and get evaluated on:

> after receiving twelve and shipping four...

which isn't quite the heroic generalisation story I was hoping for.

Counterfactual pairs are useful too. Change one shipment value, recompute the answer and generate a minimally different question. If the rewrite keeps the old answer or drops the changed condition, it fails a concrete test.

## what I built from this

The local generator creates deterministic inventory states, two wording templates and minimally changed shipment counterfactuals.

A separate parser reconstructs the arithmetic and rejects mismatched answers, altered states or unsupported wording. Parent families are assigned to splits before variants are generated, and overlapping counterfactual states are merged into one split group.

Start with [generate.py](generate.py) or the [module README](README.md).

`--count` refers to source states, not final rows. Most states produce four rows, and every output keeps parent identity, split, template revision, seed, source state and verifier outcome.

Free-form model rewrites, broader rule families, judge comparisons and actual fine-tuning are still separate experiments. The current verifier only understands its explicit grammar.

That's fine for now.

I'd rather have a small synthetic dataset I can genuinely inspect than a million-row one where the main quality check is another model saying *looks good to me*.

[Blog index](../../README.md)
