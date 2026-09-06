# [td] tegridydev | pulling useful fields out of messy text

I'm interested in the bit where messy text becomes a useful table.

Someone mentions a company, quotes another person and drops an email address in the middle. A model can turn that into a convincing spreadsheet almost instantly.

Convincing and correct aren't the same thing.

I'd rather have a few honest blanks than a complete-looking table full of invented relationships.

## keep the sentence behind the cell

Take this fictional line:

> My friend Mira works at Cedar. Contact the event desk at events@example.invalid.

There are at least three subjects here: the author, Mira and the event desk.

The address belongs to the event desk because the sentence says so. It doesn't automatically belong to Mira, and Cedar doesn't automatically employ the author.

So I prefer storing fields as claims with evidence:

```json
{
  "field": "contact_email",
  "value": "events@example.invalid",
  "subject": "event desk",
  "source_id": "example-post-01",
  "source_span": "Contact the event desk at events@example.invalid.",
  "status": "observed"
}
```

The `.invalid` address is deliberately fictional.

The source span gives me somewhere concrete to check.

## “verified” is doing too much work

An email can have valid syntax. Its domain can resolve. A mailbox can appear deliverable.

None of that proves who owns it, where they work or whether they want to hear from me.

So I want named checks with timestamps and unknowns rather than one green `verified` badge. A timeout stays different from a negative result, and conflicting sources remain separate until someone resolves them.

## rules first, model where it earns the job

Predictable JSON fields don't need an LLM. Neither do obvious email candidates.

I'd start deterministic and use a local model only for ambiguous prose. Ollama's [structured outputs](https://docs.ollama.com/capabilities/structured-outputs) can constrain response shape, but a neat schema doesn't prove the fields are supported by the text.

After generation I still check values and spans independently. The model doesn't need tools for sending messages or editing files; source text is data even when it contains instructions.

## make review faster than rereading everything

Suggested value on one side. Exact excerpt on the other.

Accept, correct or suppress it.

If the same source is processed again, keep both the source revision and extractor revision. `already processed` isn't enough when either one changed.

JSON preserves the full structure. CSV can flatten accepted fields, with formula-like values escaped deliberately.

## what I built from this

The local SQLite pipeline finds email candidates, retains exact Unicode spans and keeps the full source text. Every candidate needs an explicit accepted/rejected review before export.

It deliberately does **not** guess the owner of an address from nearby prose. Suppression is reapplied during CSV export and formula-like cells are escaped.

Start with [extract_contacts.py](extract_contacts.py) or the [module README](README.md).

```text
list
review ID accepted REVIEWER --relation "reviewed relation"
suppress EMAIL REASON
export output.csv
```

Nothing sends a message.

The next test set I'd use includes quoted contacts, multiple people, no useful fields and conflicting roles. Then compare rules, model extraction and the combination on correct fields, missed fields, invented values and reviewer time.

If the model makes the table more complete by guessing, it hasn't improved the tool.

Acquisition, deliverability checks and model-assisted relationship extraction are still outside this build. The regex is deliberately a candidate finder rather than a full email-address parser.

The goal is basically a spreadsheet where every neat little cell can answer:

> yep, this is where I came from.

[Blog index](../../README.md)
