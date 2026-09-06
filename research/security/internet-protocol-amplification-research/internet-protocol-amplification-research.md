# [td] tegridydev | Protocol resource budgets: bytes, work and retained state

*design study and proposed evaluation*

“Amplification” is one of those security words that can hide several completely different resource problems. I want to separate them before attaching the idea to any deployed protocol: response bytes, processing work, retained unfinished state and branching downstream work all need different measurements.

The first version therefore stays inside bounded discrete-event simulations. That lets me check the accounting and termination rules without constructing live traffic or turning a measurement note into an operational denial-of-service recipe.

## Four budgets, four claims

| Quantity | What I mean | What it does **not** prove |
| --- | --- | --- |
| Traffic ratio | Response bytes / attributable input bytes at a declared layer | CPU cost or successful reflection |
| Work ratio | Server work per accepted input unit against an ordinary-request baseline | Complexity from one timing point |
| Retained state | Live memory/queued work from unfinished jobs over time | An unbounded leak without cleanup tests |
| Branching work | Downstream jobs caused by one admitted job under an explicit graph | Self-sustaining network recursion |

Every result needs its byte layer, connection boundary, window and terminal condition. A zero denominator is undefined, not “infinite”. A large response to the actual requester is not automatically reflection.

## Protocol examples are constraints, not vulnerability claims

For HTTP/2, the useful question is whether different bounded parser/admission policies change retained state, rejection latency and legitimate completion under incomplete work. RFC 9113 already discusses field-block/resource limits, so the simulation should model started, accumulating, completed, rejected and cleaned-up states and track bytes separately from work. A parser can stop storing data yet still burn processing time.

For QUIC, RFC 9000 already defines pre-validation byte accounting around an unvalidated address. That means reflection and CPU-work questions should stay separate. A toy state machine can verify a declared byte invariant without spoofing anything; if the toy violates its own rule, I have found a model bug, not a protocol vulnerability.

The old CLDAP/referral idea is even more dependent on mechanism. A referral appearing in a response does not tell me who follows it or whether the action can repeat. Until a specific implementation establishes that behaviour, I only need an abstract job graph with chains, cycles, fan-out and explicit termination budgets.

## The cheap falsifiable study

Use 100 deterministic synthetic workloads containing ordinary jobs, incomplete jobs, bursts and slow clients. All policies receive the same offered work and every rejected job is retained in the ledger.

Three questions are enough:

1. Does a per-job deadline or global pending-work cap reduce peak retained state without destroying legitimate completion?
2. Does the QUIC-inspired accounting object always stay inside its declared pre-validation byte limit, including intentionally defective fixtures that prove the checker can fail?
3. Do cycle detection and a global work budget bound graph work more reliably than depth alone across chains, trees, cycles and dense graphs?

Measure peak state, admitted/emitted bytes, total work units, rejection delay, legitimate completion and tail latency. If wall-clock timing is later added, hardware/build/warm-up become part of the manifest.

Depth is a good example of why the ledger matters. Limiting path length does not limit total work when fan-out is high; a branching tree can contain `1 + b + … + b^d` jobs. Cycle detection controls repetition, while an admission budget controls total work. Retries and child jobs have to be charged **before** enqueueing or the limit is decorative.

**What would weaken the idea:** if a simpler cleanup/deadline policy gives the same bounded behaviour, there is no reason to invent a more elaborate resource contract. Likewise, any observation from the simulator stays an observation about the simulator until an authorised version-specific implementation study is designed separately.

## Where I’d extend it

A reusable **resource contract** could declare maximum retained bytes, pending jobs and work per lifecycle, then test those promises with state-machine fixtures. A second experiment could compose two individually bounded services and check whether retries/handoffs still multiply total work, comparing independent per-hop budgets with one shared end-to-end budget.

That is the direction I find useful: not “how big a bad request can I make?”, but **can a service state exactly what resources one admitted unit of work is allowed to consume, and can I falsify that statement safely?**

## What exists locally

The finite job-graph simulator now charges work before enqueueing, records every admitted/rejected job and measures peak queue occupancy. Chain, cycle and branching fixtures verify hand counts. A separate unvalidated-byte object enforces the three-to-one accounting invariant.

Start with [budgets.py](budgets.py); the [module README](README.md) lists setup, commands and every supporting file.

Depth, cycle detection and a global work budget are separate controls. The QUIC-inspired accounting fixture checks byte totals only; it makes no vulnerability or CPU-cost claim.

## References

- **RFC 9113: HTTP/2** — Martin Thomson, Cory Benfield. 2022-06. [Source](https://www.rfc-editor.org/rfc/rfc9113.html).
- **RFC 9000: QUIC: A UDP-Based Multiplexed and Secure Transport** — Jana Iyengar, Martin Thomson. 2021-05. [Source](https://www.rfc-editor.org/rfc/rfc9000.html).

## Status

The local implementation is tested where stated above. Anything beyond those bounded fixtures or saved results remains proposed rather than presented as a completed finding.

[Research index](../../README.md)
