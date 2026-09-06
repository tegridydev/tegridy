# [td] tegridydev | botsim: letting the locals talk

I like the idea of leaving a little community of model personas running and seeing what they do with it.

Give them somewhere to talk, a few different interests and a problem to figure out together. Then try very hard not to end up with six bots endlessly telling each other *great point* lol.

That's basically BotSim. The chat interface is the easy part. The interesting bit is **who gets a turn, what they can see and whether useful information survives the conversation**.

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
