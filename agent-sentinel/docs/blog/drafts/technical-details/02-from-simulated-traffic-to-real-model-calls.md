# Part 2 — From Simulated Traffic to Real Model Calls

<!--
DRAFT, not published. Before moving this file to docs/blog/technical-details/:

1. DONE: SDK collectors and their tests copied from agent-sentinel-series
   (lint fixes only). Every claim below was checked against them.
2. DONE: the gaps found while testing are fixed in both repositories, with
   regression tests in app/tests/test_collector_contracts.py.
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

To record real calls, Agent Sentinel wraps the Anthropic and Azure OpenAI
Python SDKs that agents already use. The agent swaps `anthropic.Anthropic` for
`AnthropicSentinel`. The wrapper makes the real call, reports a redacted copy
of the request and response to Agent Sentinel, and hands the agent the
provider's response unchanged. Anything the wrapper doesn't record, such as
streaming, is passed straight through to the real SDK. When the model proposes a tool call, the
wrapper reports it as *requested*, not executed: from where it sits, it can't
know whether the agent actually ran it.

## Testing the rule against my own code

I wrote "if the recorder fails, the agent must not" before I tested the
wrappers against it. Testing them for this article found five places where
they fell short. Each one is now fixed and has a regression test:

| What I found | What changed |
|---|---|
| An agent calling `client.messages.stream`, `count_tokens` or batches **crashed**: only `messages.create` was wrapped, and everything else on that object raised an error. | Anything the wrapper doesn't record is passed straight through to the real SDK. Streaming calls work; they just aren't recorded yet. |
| A prompt over about 8KB was cut off mid-JSON before it was sent, so Agent Sentinel **lost the model name and the real size**. The unapproved-model rule and the oversize rule went silent: a long enough prompt slipped past both. | Long requests are sent as valid JSON that keeps the model name, with a short redacted preview of the messages and the real size alongside. Both rules fire again. |
| In async agents, reporting to a slow Agent Sentinel **froze the agent's event loop**, stalling everything else the agent was doing. | Reporting runs in a worker thread. The model call still waits for it, but nothing else does. |
| Calls the provider rejected (an outage, a rate limit) were **not recorded at all**. | They are recorded with the provider's status code, and the error reaches the agent unchanged. |
| Failed deliveries to Agent Sentinel were **logged but not counted**. | Each reporter counts them, so a gap in the record can be alerted on, not just found in a log. |

One limit remains, and it's a deliberate one. A synchronous agent still waits
for the report, up to a 2-second timeout, if Agent Sentinel is slow. Sending
reports in the background would remove that wait, but events could then be
lost when the agent exits. A bounded wait is the honest trade for now.

The pattern is the lesson. Every one of these gaps was invisible in the
simulator, because simulated traffic never streams, never sends a 165KB
prompt and never meets a provider outage. A rule only means something once
you test your own code against it.

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
  participant Wrap as AnthropicSentinel / SentinelReporter
  participant LLM as Model provider
  participant Pipe as POST /ingest → Pipeline.ingest_flow
  participant Store as Event and finding store
  participant Export as Alerting / SIEM

  Agent->>Wrap: messages.create(...)
  Wrap->>LLM: original request, unchanged
  LLM-->>Wrap: response
  Wrap->>Pipe: redacted flow + real size (2s timeout; failures counted, never raised)
  Wrap-->>Agent: response, unchanged
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
| SDK wrappers return the provider response unchanged; a delivery failure never raises into the agent | [`collector/sdk_base.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/collector/sdk_base.py), [`collector/anthropic_sdk.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/collector/anthropic_sdk.py), [`collector/azure_openai.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/collector/azure_openai.py) | `test_report_is_fail_open_when_sentinel_is_unreachable`, `test_report_is_fail_open_on_an_unparseable_response` in [`test_sdk_base.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/tests/test_sdk_base.py) |
| Redaction at the edge, before telemetry leaves the agent | `SentinelReporter.report` in [`sdk_base.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/collector/sdk_base.py) | `test_reporter_sends_bearer_token_and_redacts_before_transport` in [`test_collector_contracts.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/tests/test_collector_contracts.py) |
| Model-proposed tools are "requested", not "executed" | `report_tool_request` in [`sdk_base.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/collector/sdk_base.py) | `test_model_proposal_is_tool_requested_not_executed`, `test_tool_policy_does_not_treat_requested_tool_as_executed` in [`test_collector_contracts.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/tests/test_collector_contracts.py) |
| Unwrapped SDK methods pass through; long prompts keep model and real size; async reporting off the event loop; provider errors recorded; delivery failures counted | [`collector/sdk_base.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/collector/sdk_base.py) (`bound_request`, `delivery_failures`), [`collector/parsers.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/sentinel/collector/parsers.py) (`request_bytes`) | One test per gap, from `test_unwrapped_sdk_methods_pass_through_instead_of_breaking_the_agent` to `test_async_reporting_does_not_block_the_event_loop`, in [`test_collector_contracts.py`](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/app/tests/test_collector_contracts.py) |

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
