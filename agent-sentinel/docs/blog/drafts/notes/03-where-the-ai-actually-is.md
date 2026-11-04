<!--
DRAFT NOTE for Part 3 (Rules First, Statistics Second), not published.
Moved from Part 1's "Where the AI actually is" section on 2026-11-03, unchanged
except for the ADR link path. Part 1 now carries a short teaser instead.
Recount the line numbers before reusing them: they were counted in the full
product repository when Part 1 was written.
-->

### Where the AI actually is

The question a reader of an AI-security product asks first, answered with
counted numbers rather than positioning.

**Agent Sentinel performs no LLM inference anywhere in its own runtime.** It
wraps the Anthropic and Azure OpenAI SDKs, but only to observe the calls an
*agent* makes — Sentinel never asks a model anything itself. One optional seam
exists, `Explainer(narrator=...)`, where a model could rewrite an explanation's
prose. It defaults to `None` and nothing in the product sets it.

Non-blank lines of product code, tests excluded, counted in the full product
repository when this part was written. This companion repository carries a
trimmed copy, so a recount here gives smaller numbers; the proportions are what
matter:

| Layer | Lines | Share | What it is |
|---|---:|---:|---|
| Platform (API, storage, auth, collectors, export) | 4,069 | 61% | Plumbing |
| Sequence model (`app/sentinel_sequence/` + adapter, released with Part 3) | 1,792 | 27% | The only machine learning |
| Deterministic detection, schema, explainability | 667 | 10% | `if` statements and string templates |
| Descriptive statistics (`detection/baseline.py`) | 115 | 2% | Means, standard deviations, set membership |

Roughly **70% of this product contains no AI or ML at all**, and the part that
does is one Markov chain — first or second order over a ~28-token action
vocabulary, trained by counting transitions, Laplace-smoothed so novel
behaviour scores as *surprising* rather than *impossible*, and persisted as a
JSON file of integers. `numpy` appears in four files, computing medians and
array arithmetic, never a learned parameter. There is no `sklearn`, no
`torch`, and no gradient anywhere in the repository.

That model also ships switched off (`SeqLayerConfig.enabled = False`), cannot
cite a policy clause — `Explainer.build_sequence()` hardcodes
`policy_clause=None`, so it is structurally incapable of denying anything —
and fails open at both construction and evaluation.

#### Why the boring answer is the design

A payments bot is flagged mid-run and the compliance officer asks why. (Today
Agent Sentinel flags and does not stop the bot; the question is the same either
way.) Two possible answers:

> **A.** "The model scored this session at 0.87 anomalous, above our 0.85 threshold."
>
> **B.** "It called `initiate_wire_transfer`. Its policy permits `check_balance`,
> `get_exchange_rate`, `initiate_sepa_transfer`, `initiate_swift_transfer` and
> `confirm_payment`. Clause `allowed_tools`, agent `payment-processor`, session
> `s-4417`, 09:42:03 UTC."

Answer A cannot be argued with, which reads as strength until you are the one
defending it to a regulator — or overturning it at 2am because it was wrong.
Answer B can be checked, challenged, and changed by a human in a pull request.

The layer ordering makes that structural rather than cultural ([ADR-0001](../../../adr/0001-rules-first-detection.md)): the
deterministic layer runs first, is the only layer whose findings cite a policy
clause, and is the only layer that will be allowed to deny once enforcement
exists. The ML
earns its place in the one spot rules cannot reach — **order**. An allow-list
can confirm `verify_id`, `check_sanctions` and `initiate_wire_transfer` are
each permitted. It cannot notice the transfer happened *before* the sanctions
check.

The cost is maintaining a policy for each agent, and missing behavior those
rules do not describe. Recording before enforcing is the other deliberate
boundary: a finding helps investigate a transfer after it happens; it cannot
recover the data or stop it. Pre-action blocking remains a separate
engineering step.

One caveat, stated because the repo states it: every published figure for that
model comes from synthetic data the author wrote — both the normal workflows
and the attacks. `docs/EVAL_PAYMENTS_BOT.md` (released with Part 3) calls this the "author-designed
validity ceiling" and declines to present the numbers as real-world
performance.
