# An Agent Can’t Answer an MFA Prompt

![Scoring a non-human identity: an agent acting for a user inherits that user’s risk. Four questions for every non-human identity: who is it, how does it prove it, who answers for it, and is it behaving like itself right now. STEP_UP becomes sponsor approval; BLOCK becomes revoke tokens and disable the service principal.](../images/01-an-agent-cant-answer-an-mfa-prompt-1.png)

*The rule that protects your administrators would block every automation you run.*

I run a small platform that scores identity risk in Microsoft Entra ID: it reads sign-in events, computes behavioural signals, runs eleven deterministic rules plus an anomaly model, and asks a policy engine for one answer — allow, step up, or block.

One of the eleven rules is the kind every security team has:

> A privileged role, used without MFA, is blocked.

A good rule for people. Then I fed the platform sign-ins from service principals, managed identities and AI agents. A workload has no phone; an agent can’t tap “Approve”. Every privileged service principal signs in without MFA, by design. Run the human rules against them and the policy blocks the backup job, the payroll sync and the deployment pipeline within minutes. The platform had never scored a non-human identity before, so the bug had never fired.

## The identities nobody signs in as

Non-human identities (NHIs) — service principals, managed identities, API clients, and now AI agents — already outnumber people in most tenants. They hold standing privileges, often authenticate with secrets that live for years, and nobody is paged when one signs in at 03:00, because that is when they always do.

Agents add something new: an agent often acts **on behalf of a person**, using your rights to read your mailbox or file your expense report. If your session is compromised, the agent working for you is now working for the attacker — and controls built around human sessions never see it.

So I extended the platform, starting not with code but with four questions every NHI has to answer.

## Four questions for every non-human identity

1. **Who is it?** One identity per workload or agent — never shared, never a human account in disguise. A service account three teams share can’t be scored; it has no single “normal”.
2. **How does it prove it?** Preferably without a stored secret. When an agent acts for a person, the token must carry both — the person as subject, the agent as actor — which makes the delegation visible to the API, the audit log and a risk scorer.
3. **Who answers for it?** Every NHI needs an accountable owner, a review date, and access that expires.
4. **Is it behaving like itself right now?** Governance asks “should it have this access?” on a cycle; runtime risk asks “is this sign-in normal?” on every event. This is the question my platform answers.

None of this is vendor-specific. How the first three land in the products I see most often:

| Question | Microsoft Entra | SailPoint | Okta |
|---|---|---|---|
| Who is it? | Agent identity from a blueprint; service principals; managed identities | AI agents and machine identities, discovered and classified | AI agents in the directory, linked to an app |
| How does it prove it? | Managed identity / federated credential; on-behalf-of uses the **jwt-bearer** grant | Not an issuer; governs the resulting permissions | Cross App Access uses **RFC 8693** token exchange |
| Who answers for it? | Sponsor (required) and owners; access packages that expire | Owners; NHI certification campaigns | Owners; agent certifications not described |

One surprise: I expected Entra’s agent delegation to use RFC 8693 token exchange, as Okta’s Cross App Access does. It doesn’t — Entra uses **jwt-bearer**. If your estate spans both, “the agent acts for the user” is two different protocols, so a risk engine shouldn’t depend on either; it should reconstruct the actor chain from the logs.

## What “behaving like itself” means

People are noisy — they travel, change laptops, work late. Workloads are not: a payroll sync calls the same API, from the same network, with the same credential type, at the same rate, every day. That regularity is the signal, so anything new means more for a workload than for a person.

Each NHI gets a 30-day baseline. Five signals come from its behaviour, three from the identity graph:

| Signal | What it catches |
|---|---|
| New network | A new ASN or IP for a workload that only ever called from one place |
| New resource | A token for an API it has never asked for |
| Credential drift | A **client secret** from an identity whose history is all federation, certificates or managed identity — a classic leaked-secret sign |
| Token velocity | Tokens in the last 15 min vs *this identity’s own* average rate, not a global threshold |
| Delegating person’s risk | The agent inherits the latest risk score of the user it acts for |
| *Governance* | Owner/sponsor count, whether it holds a privileged role, and days since last recertification |

The behavioural signal that matters most is why I built this. The platform already scores every human sign-in, so when an agent acts for Alice, Alice’s risk score comes with it. A compromised person can’t launder access through an agent — the agent is only as trusted as the person it serves.

## Six rules, and the ones that must never run

| Rule | Fires when | Outcome on its own |
|---|---|---|
| Agent acting for a risky user | Delegating user scores 30+ (above 70) | Step up (block) |
| Privileged NHI with no owner | Privileged role, zero owners or sponsors | Step up |
| Secret where federation is the norm | Credential drift | Step up; block if privileged |
| New network or resource | Either is new (both are new) | Adds risk (step up) |
| Token burst | At least 5× its own rate | Up to step up |
| Stale recertification | Never reviewed, or 90+ days ago | Adds risk |

The more important change is what **doesn’t** run. The human rules — MFA, devices, business hours, impossible travel — are now guarded to fire only for people, in both the scorer and the policy. The administrator-without-MFA rule still blocks; it no longer blocks a backup job.

I also kept the anomaly model away from NHIs. Trained on human behaviour, it would call any workload that signs in at 03:00 with no MFA and no device an outlier. NHIs are scored by rules and policy only, until there is enough reviewed data to train a model on them.

## Step up, when nobody can be stepped up

For a person, “step up” means another MFA prompt. An agent can’t answer one, so the enforcement has to mean something else. The decision values stay ALLOW / STEP_UP / BLOCK and the policy engine is still the only place that decides — but it now knows the subject type (human, workload, managed identity or agent) and the actor chain.

| Value | For a person | For an NHI or agent |
|---|---|---|
| STEP_UP | Another MFA prompt | **Sponsor or owner approves**, or scopes narrow to the task; for credential drift, the owner confirms and rotates to a federated credential |
| BLOCK | Deny the sign-in | **Revoke tokens and sessions, disable the service principal** or drop its time-bound grant, page the owner; for a risky delegation, revoke that user’s grant |

A blocked agent should also trigger an off-cycle recertification: a runtime alert is evidence a governance review should have caught something.

## The poller that was itself an NHI

Some irony: the component that reads risk data from Microsoft Graph is itself an NHI, and it authenticated with a client secret. Not any more — it now uses its own managed identity, presented as a federated credential to read another tenant, with Terraform creating the trust. (The secret still works for local dev, with a warning.) Writing about secretless workloads from a service that held a secret would have been hard to defend.

## Where this stops working

| Limit | What it means |
|---|---|
| Field names unconfirmed | Microsoft documents the agent-type marker and a dedicated agent sign-in event, but I couldn’t confirm the exact property path on exported records. The mapping is isolated and flagged — check it against a real tenant first. |
| Governance data must exist | Owners, sponsors and recertification dates come from your governance tool via the identity graph. Without it, those rules stay silent by design — an unknown is a data gap, not a missed review. |
| No NHI model yet | Rules catch what I thought of; the rest needs an anomaly model trained on non-human data and analyst verdicts. That’s the next piece of work. |
| Tested, not deployed | 188 unit tests and 18 policy tests pass, and infra validates. Writing the policy tests found two older bugs — overlapping rules returned an error instead of a decision, and reason text never reached the output. End-to-end proof still needs a real tenant. |

Treat an agent as an identity: give it an owner, a review date and expiring access, and score it against its own baseline and the trust of the person it acts for. The vendors cover who the agent is and what it may hold; the gap I wanted to close is whether it is still behaving like itself.

Which non-human identities in your tenant would you not be able to name an owner for today? [Tell me on LinkedIn](https://linkedin.com/in/anandkn2012).

## References and further reading

- **Entra agent identities:** Microsoft, [Agent identity blueprints](https://learn.microsoft.com/en-us/entra/agent-id/agent-blueprint), [Owners, sponsors and managers](https://learn.microsoft.com/en-us/entra/agent-id/agent-owners-sponsors-managers) and [Agent ID governance](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview).
- **Delegation:** Microsoft, [Agent on-behalf-of flow](https://learn.microsoft.com/en-us/entra/agent-id/agent-on-behalf-of-oauth-flow); Okta, [Cross App Access](https://developer.okta.com/docs/concepts/xaa).
- **Governance of machine identities:** SailPoint, [Machine Identity Security](https://documentation.sailpoint.com/saas/help/machine/index.html) and [Access reviews for non-human identities](https://www.sailpoint.com/blog/bringing-access-reviews-to-your-non-human-identities).
- **Agent sign-in logs:** Microsoft, [Sign-in and audit logs for agents](https://learn.microsoft.com/en-us/entra/agent-id/sign-in-audit-logs-agents).
