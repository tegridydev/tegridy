+++
title = "botsim: letting the locals talk"
date = "2026"
description = "I like the idea of leaving a tiny local community of model personas running, then seeing what survives once scheduling, memory and interruptions get in the way."
draft = false
id = "blog/botsim-local-community"
type = "article"
author = "tegridydev"
topic = "agent-systems"
related = ["research/moa-framework", "research/local-assistants-and-memory"]
updated = "2026-09-08"
+++

# [td] tegridydev | botsim: letting the locals talk

I like the idea of leaving a little community of model personas running and seeing what they do with it.

Give them somewhere to talk, a few different interests and a problem to figure out together. Then try very hard not to end up with six bots endlessly telling each other *great point* lol.

That's basically BotSim. The chat interface is the easy part. The interesting bit is **who gets a turn, what they can see and whether useful information survives the conversation**.



<!-- cpu-comparison:start -->
## Recorded findings

The deterministic provider produced 200 messages across 180 tasks and 13 storage reopens. This demonstrates restartable scheduling for the supplied conversation fixture; live Ollama behaviour and the realism of the simulated community were not evaluated.

Headless deterministic fake-provider workflow with repeated process-level storage reopen; no live Ollama or social-simulation validity claim.

| Recorded metric | Mean | Seed standard deviation |
| --- | ---: | ---: |
| messages | 200 | — |
| restarts | 13 | — |
| tasks | 180 | — |

The [comparison record](comparison-results.json) includes the 1 recorded run, measured values, source hashes and dependency versions. This is a single fixed evaluation; no across-seed uncertainty is estimated.
<!-- cpu-comparison:end -->

## a restart I can actually check

The [restart test](test_app.py) posts one workshop message, steps once with `fake`, closes SQLite and reopens it. After recovery, it checks one completed task and two messages. Cancelling Ben's pending reply keeps it cancelled; a result arriving after cancellation does not become another message.

That is the useful replay boundary: completed work stays completed and cancelled work cannot sneak back in. `fake` supplies deterministic local replies. It does not test Ollama availability, model quality or a real inference request. Run `python -m pytest -q test_app.py` after [setup](README.md); the Flask test client does not start a server.

## the transcript can lie a little

Imagine three residents each know one fact needed to answer a question and a fourth resident asks it.

If the scheduler always prioritises the newest message, one chatty resident can keep jumping the queue while the person holding the missing fact never gets a turn. Reading the transcript later, that can look like a personality problem when it was really scheduling.

So I want each reply to retain its trigger, chosen speaker and actual visible context.

The Discord-ish layout is mostly because it's familiar. The experiment can stay completely local with Ollama or deterministic fake replies.

## start really small

Four personas and two channels are plenty.

Each persona gets an ID, role prompt and readable channels. Messages keep stable IDs, authors and parents. When a message creates work for another resident, that becomes a task with its own identity.

```text
message m12 -> task (m12, resident-b) -> queued
scheduler -> resident-b
context -> [m03, m08, m12]
reply m13 -> committed
restart -> task already complete
```

If the app dies halfway through a reply, recovery shouldn't create a second timeline. Streaming text is only a preview until the reply and completed task commit together.

I'd also keep simulation time separate from model latency. Otherwise the slowest model accidentally becomes the shyest resident :)

## relationships need receipts

`replied to three requests` is an observation.

`deeply trusts resident-b` is an interpretation.

I'd like both eventually, but the second shouldn't pretend to be the first. If the UI shows a relationship score, I should be able to open the messages behind it.

[Generative Agents](https://arxiv.org/abs/2304.03442v2) is useful related work around memory, reflection and simulated characters. My narrower interest here is how communication rules change what reaches the group.

## what I actually want to compare

First I'd replay one fixed script with fake replies: simultaneous requests, chatter, a cancellation and a restart. Check missing tasks, duplicates and context before involving a language model.

Then compare:

- latest-message-first
- round robin
- oldest-waiting-first
- independent residents with no neighbour messages

Everything else stays fixed.

I care less about which transcript feels smartest than whether the useful facts reach the answer and whether anyone gets starved of turns.

Replay also gives me a fun next step: remove one message and run the same situation again. Did the group lose a fact, avoid copying an error or barely change?

## what I built from this

The local Flask build now runs four personas across two channels. SQLite commits replies and completed tasks together, stores the exact visible context and rejects late replies to cancelled attempts.

Oldest-waiting scheduling, a 100-message ceiling and depth-three limit keep it bounded. The default provider uses deterministic fake replies; an explicit Ollama model enables local generation.

Start with [app.py](app.py) or the [module README](README.md).

```sh
python3 app.py
python3 app.py --ollama-model MODEL_NAME
```

Open `http://127.0.0.1:5050`. The adapter follows the [Ollama chat contract](https://docs.ollama.com/api/chat).

The live Ollama adapter hasn't been exercised against an installed model in this packaged version. Scheduler comparisons, token accounting, relationship metrics and multi-process workers are still outside the first build.

For now I mostly want the tiny town to survive a restart without inventing another one :)

[Blog index](../../README.md)
