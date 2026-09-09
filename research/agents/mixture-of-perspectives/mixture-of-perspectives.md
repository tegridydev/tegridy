+++
title = "Mixture of Perspectives: Decision Support with Disagreement"
date = "2026"
description = "Separate hard constraints from competing preferences and retain useful disagreement in a synthetic decision fixture with explicit utility assumptions."
draft = false
id = "research/mixture-of-perspectives"
type = "research-note"
author = "tegridydev"
topic = "agent-systems"
related = ["research/moa-framework", "research/recursive-self-correction-with-uncertainty"]
status = "implemented"
updated = "2026-09-09"
+++

# Mixture of Perspectives: Decision Support with Disagreement

Mixture of Perspectives is not an attempt to calculate the objectively correct morality number. I’m interested in a much more practical question: **does explicitly preserving different values and unresolved objections help a human reviewer notice important things that a single smooth answer misses?**

The useful output is therefore a decision support record, not a synthetic consensus. It should expose assumptions, factual disputes, value conflicts, minority objections and the person who still owns the decision.

## Recorded findings

The perspectives disagreed in 37.3% of the fictional utility cases while producing no infeasible winners. This demonstrates sensitivity to declared value weights while retaining hard constraints; it does not evaluate moral judgement or language model deliberation.

Varied fictional finite utilities and objective budget ceilings; this measures value weight sensitivity, not real world moral judgement or language model deliberation.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| cases | 200 | 0 |
| disagreement rate | 0.373 | 0.022528 |
| infeasible winners | 0 | 0 |

The [comparison record](comparison-results.json) includes the 5 recorded runs, measured values, source hashes and dependency versions. Variation is reported across the declared seeds; it does not establish generalisation beyond this workload.

## a disagreement that should survive aggregation

In the [40 case fixture](test_perspectives.py), the first speed first perspective selects `fast`, while cost first selects `cheap`. Both appear on the Pareto set. Changing the factual budget can remove `fast` and make `cheap` win even for speed first.

That separates disagreement about preferences from disagreement about feasibility. A large speed weight cannot make an over budget action eligible. Non finite constraint values and duplicate action IDs are rejected so they cannot quietly bypass that rule. These checks do not turn the weighting choices into objective facts.

## Make the modelling assumptions visible

One simple representation is a vector of dimensions such as harm prevention, fairness, autonomy, care, honesty, loyalty and justice. A perspective can weight those dimensions differently, but a weighted sum is only one modelling choice. Some positions are better represented as hard constraints: an action that violates a declared right or feasibility rule should not be able to buy its way back with unrelated benefits.

The numbers are not moral ground truth. Scenario authors decide which outcomes exist, how they are scaled and whose interests appear. Every score therefore needs a rationale, uncertainty range and enough provenance to challenge it. I also want a Pareto view beside each perspective’s preferred action, because disagreement can be a genuine trade off rather than a solver bug.

The response contract should keep **factual uncertainty** separate from **value disagreement**. Whether an option costs $100 can be checked. Whether fairness outweighs convenience cannot be resolved by generating more confident prose. A mediator can identify that difference without pretending every disagreement has to disappear.

## A test that does not reward theatrical debate

I’d begin with 40 fictional, low stakes allocation cases. Each case has facts, feasible options, affected groups and a checklist of considerations written before generation. Twenty cases are development material and twenty remain untouched, grouped by scenario template so paraphrases do not leak across the split.

Compare:

1. direct single agent advice;
2. one agent explicitly asked for multiple perspectives;
3. rule only vector scoring;
4. independent perspectives without debate;
5. the full deliberation loop.

Match generated tokens and maximum rounds where practical. Independent reviewers, blinded to the method, rate consideration coverage, factual error, unsupported certainty, contradiction, clarity and distracting but irrelevant objections. More words and more disagreement are not automatically better.

The hypotheses are straightforward. Structured perspectives should surface more relevant considerations than a direct answer at the same budget. Retaining dissent should help reviewers notice material omissions. Explicit assumption ranges should make recommendations stable under harmless paraphrase but sensitive to substantive factual changes.

I also want controls for correlated role play. Remove one perspective, permute order, swap role names and paraphrase keyword triggers. If a conclusion moves mainly because the word `rights` appeared, I have a lexical heuristic rather than robust deliberation. Same model versus different model panels are a later comparison because changing models also changes competence and style.

**What would weaken the idea:** if the multi perspective version adds cost without improving consideration coverage or omission detection, use the simpler direct prompt. A negative result here would be useful.

## Extensions that keep the disagreement inspectable

An **assumption sensitivity map** varies uncertain factual values and shows which recommendations flip. If two perspectives disagree only because they assumed different outcomes, the system should show that. If disagreement remains with identical facts, preserve it as a value conflict.

A second extension gives one challenger a narrow responsibility: name a potentially missing stakeholder, possible impact and evidence needed to assess it. Compare that with an unconstrained “critic” prompt. The goal is useful coverage, not a tiny theatre company arguing for its own sake.

Self Refine is relevant prior work for same model critique and revision. The narrower thing I’m testing here is whether **explicit value plurality plus retained dissent** improves a defined human review task. Fluent agreement is not the target.

## Implementation

The evaluator now applies hard constraints before utility ranking, preserves Pareto alternatives and separates value weight changes from a changed factual budget. Forty fictional cases expose both perspectives and all rejected actions.

See [perspectives.py](perspectives.py); the [module README](README.md) describes usage and dependencies.

All criteria use declared [0,1] scales and nonnegative weights. Ties remain multiple winners; an infeasible high scoring action cannot win.

## Related public work

[mixture of persona research](https://github.com/tegridydev/mixture-of-persona-research) is relevant to this topic. The local results in this article apply to the saved implementation and workload. Further proposals and linked upstream projects have separate scopes. A related project link does not establish that all features described here are implemented.

## References

- **Aman Madaan; Niket Tandon; Prakhar Gupta; Skyler Hallinan; Luyu Gao; Sarah Wiegreffe; Uri Alon; Nouha Dziri; Shrimai Prabhumoye; Yiming Yang; Shashank Gupta; Bodhisattwa Prasad Majumder; Katherine Hermann; Sean Welleck; Amir Yazdanbakhsh; Peter Clark. [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651v2).** 2023-05-25, arXiv v2; first submitted 2023-03-30.

[Research index](../../README.md)
