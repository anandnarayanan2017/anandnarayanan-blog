# Part 2 — From Simulated Traffic to Real Model Calls

<!--
DRAFT, not published. Before moving this file to docs/blog/technical-details/:

1. RELEASE THE SDK COLLECTORS. app/sentinel/collector/__init__.py names
   collector.sdk_base, collector.anthropic_sdk and collector.azure_openai, but
   they are not in this companion repository yet. Copy them (and their tests)
   from the product repository, as Part 1 did for the Part 1 code.
2. VERIFY EVERY SENTENCE MARKED "VERIFY" against that code. They describe what
   the wrappers must do for this article to be true. If the code differs, change
   the sentence, not the code, unless the code is wrong.
3. Add a Part 2 row to ../../TRACEABILITY.md.
4. Add a hero image as ../../images/02-from-simulated-traffic-to-real-model-calls-1.png.
5. Check the "2" date in ../../series.json (currently 2026-10-13).
6. Convert the GitHub links below to relative links, as Part 1 uses.
-->

> **Reader path:** [LinkedIn post](../linkedin/02-from-simulated-traffic-to-real-model-calls.md) → this article → [design and implementation](#design-and-implementation) → code-and-test traceability

## Simulated traffic proves the rules. Real traffic tests the recorder.

Part 1 replayed a simulated night: a payments agent reads the ledger, asks an
approved model for a summary, then sends 250KB to a server nobody approved.
Agent Sentinel recorded all three steps and raised a finding for the third.

A simulator is the right place to start. You control every event, so you can
prove each rule fires when it should and stays quiet when it shouldn't.

It proves nothing about the recorder itself. Simulated events are tidy. Real
ones aren't. A real agent sends payloads the parser has never seen, pastes a
customer's card number into a prompt, and keeps running at 3am while the
security team's alerting webhook is down for maintenance.

So the move from simulated traffic to real model calls isn't mainly about
collecting more data. It's about one rule:

**If the recorder fails, the agent must not.**

A flight recorder that could stop the engines would never be allowed on the
plane. A monitoring tool that can break a payments run will be switched off
by the first team it breaks, and then it records nothing.

## Three ways a recorder breaks an agent, and what Agent Sentinel does instead

**1. It crashes on input it didn't expect.** A model provider changes its
response format, or a body arrives truncated. Agent Sentinel's parsers are
defensive: a payload they can't read is still recorded, classified by where it
went, instead of raising an error. A malformed request to `api.anthropic.com`
is still recorded as a model call, just without the model name.

**2. It turns the evidence into a new data leak.** A recorder that stores
prompts verbatim has quietly built a second copy of your customer data.
Agent Sentinel never stores the full prompt. It keeps the payload's size and a
short preview as evidence, and removes credentials and common identifiers from
that preview first: values under keys like `password` or `iban` are replaced whatever they
look like, and recognisable shapes, such as card numbers and bearer tokens,
are replaced wherever they appear. Redaction runs *before* the preview is cut
to length, so a secret can't hide just past the cut.

The limit is stated in the code, so it's stated here too: this handles
structured identifiers and sensitive keys. A customer's name written in plain
prose survives. It reduces exposure; it is not a guarantee.

**3. It waits on systems the agent doesn't need.** Findings go on to alerting
and to the SIEM. If either is down, Agent Sentinel still records the event and
the finding, and carries on. That is *fail-open*. It is not *fail-silent*:
every failed delivery is counted and logged with the finding and rule it
belonged to, so a dropped alert is something you can see, not something you
discover in an audit.

## Connecting real model calls

<!-- VERIFY this whole section against collector/sdk_base.py,
anthropic_sdk.py and azure_openai.py once they are released. -->

To record real calls, Agent Sentinel wraps the Anthropic and Azure OpenAI SDKs
that agents already use. The agent swaps one client class for another; its
code, prompts and responses are otherwise unchanged. The wrapper observes the
call and reports it. It never asks a model anything itself, and it never
changes what the agent receives.

The same rule applies here as everywhere else: **VERIFY** if Agent Sentinel is
slow or unreachable, the agent's model call still completes and returns
normally. The event is dropped and counted, not retried in the agent's path.

## The trade-off

Fail-open has a cost, and it's the one a CISO should ask about: when Agent
Sentinel or its exports are down, you can lose evidence. The design accepts
that cost deliberately, because the alternative, a recorder that can stop
payments, doesn't survive its first incident. What it doesn't accept is losing
evidence *silently*: failures are counted so they can be alerted on and
explained.

Recording also remains after the fact. Agent Sentinel sees the 250KB transfer
when it happens; it can't stop it. Blocking needs a different component that
sits *in* the agent's path, with a different failure rule, and it stays on the
roadmap until the evidence shows which actions are safe to block.

Next: Part 3 — Rules First, Statistics Second.

Which would worry you more in production: a recorder that occasionally misses
an event, or one that occasionally blocks an agent? [Tell me on
LinkedIn](https://linkedin.com/in/anandkn2012).

## Design and implementation

Every collector, simulated or real, enters the same pipeline through one
method, so the failure rules above are enforced in one place rather than once
per collector.

```mermaid
sequenceDiagram
  participant Agent as Agent code
  participant Wrap as SDK wrapper (VERIFY: Part 2 release)
  participant LLM as Model provider
  participant Pipe as Pipeline.ingest_flow
  participant Store as Event and finding store
  participant Export as Alerting / SIEM

  Agent->>Wrap: messages.create(...)
  Wrap->>LLM: original request, unchanged
  LLM-->>Wrap: response
  Wrap-->>Agent: response, unchanged
  Wrap->>Pipe: flow (host, path, bodies, agent_id)
  Pipe->>Pipe: parse_flow: redact, then truncate; malformed degrades, never raises
  Pipe->>Store: insert_event
  Pipe->>Pipe: Engine.evaluate (deterministic rules)
  Pipe->>Store: insert_finding
  Pipe-)Export: fail-open: failures counted and logged, never raised
```

### Where each guarantee lives

| Guarantee | Implementation | Regression proof |
|---|---|---|
| One ingest path for every collector | [`Pipeline.ingest_flow` and `Pipeline.ingest_event`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/pipeline.py) | [`test_pipeline_persists_events_and_findings`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/tests/test_pipeline.py) |
| Malformed input degrades instead of raising | [`collector/parsers.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/collector/parsers.py) | `test_parser_survives_malformed_body` in [`test_pipeline.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/tests/test_pipeline.py) |
| Redaction before storage, before truncation, never raises | [`collector/redaction.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/collector/redaction.py) | `test_redaction_runs_before_truncation`, `test_redaction_never_raises_on_hostile_input`, `test_prompt_evidence_from_a_real_flow_is_redacted` in [`test_redaction.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/tests/test_redaction.py) |
| Export is fail-open, not fail-silent | `_fire_alerter` and `_push_siem` in [`pipeline.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/pipeline.py) | `test_installed_module_that_raises_is_a_failure`, `test_successful_export_counts_nothing` in [`test_export.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/tests/test_export.py) |
| Missing optional packages don't crash the server, and aren't counted as failures | Lazy imports in [`pipeline.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/pipeline.py) | `test_missing_packages_are_not_failures_and_log_once` in [`test_export.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/tests/test_export.py) |
| SDK wrappers return the provider response unchanged and never raise into the agent | VERIFY: `collector/anthropic_sdk.py`, `collector/azure_openai.py` (not yet in this repository) | VERIFY: their tests |

### Why the guarantees sit in the pipeline, not in each collector

A proxy, an SDK wrapper and, later, a network collector see very different raw
data. If each one implemented its own redaction and its own failure handling,
the guarantees would be only as strong as the weakest collector, and every new
collector would be a new chance to get them wrong. Putting parsing, redaction,
storage and export behind `ingest_flow` means a new collector only has to
produce a flow. Everything the article promises happens after that point.

The cost is that the pipeline must be fast and safe to call from inside an
agent's process. That is why its locks are scoped to the store and the engine
rather than the whole ingest, and why export runs after the event and finding
are already stored.
