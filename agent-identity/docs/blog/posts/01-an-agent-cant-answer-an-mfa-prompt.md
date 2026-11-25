# An Agent Can’t Answer an MFA Prompt

![Scoring a non-human identity: an agent acting for a user inherits that user’s risk. Four questions for every non-human identity: who is it, how does it prove it, who answers for it, and is it behaving like itself right now. STEP_UP becomes sponsor approval; BLOCK becomes revoke tokens and disable the service principal.](../images/01-an-agent-cant-answer-an-mfa-prompt-1.png)

*The rule that protects your administrators would block every automation you run.*

I have a small platform that scores identity risk in Microsoft Entra ID. It reads sign-in events, computes fifteen behavioural signals, runs eleven deterministic rules and an anomaly model, and asks a policy engine for one of three answers: allow, step up, or block.

One of the eleven rules is the kind every security team has:

> A privileged role, used without MFA, is blocked.

It is a good rule for people. Then I started feeding the platform sign-ins from service principals, managed identities and AI agents, and that rule became a problem.

A workload has no phone. An agent can’t tap “Approve”. Every privileged service principal in the tenant signs in without MFA, every time, by design. If those sign-ins had gone through the human rules, the policy would have blocked the backup job, the payroll sync and the deployment pipeline within minutes.

The platform had never seen a non-human identity before, so the bug had never fired. Running the human rules against workloads exposed it.

## The identities nobody signs in as

Non-human identities (NHIs) are the accounts that software uses: service principals, managed identities, API clients and, now, AI agents. In most tenants they already outnumber people. They hold standing privileges, they often authenticate with secrets that live for years, and nobody is paged when one of them signs in at 03:00, because that is when they always sign in.

Agents add something new. An agent often acts **on behalf of a person**. It reads your mailbox, files your expense report, or changes a ticket using your rights. If your session is compromised, the agent working for you is now working for the attacker, and controls built around human sessions never see it.

So I extended the platform. I didn’t start with code. I started with four questions that every non-human identity has to answer.

## Four questions for every non-human identity

**1. Who is it?** One identity per workload or agent, never shared, never a human account in disguise. In Entra an agent identity is a special service principal created from an *agent identity blueprint*. A service account that three teams share can’t be scored, because it has no single “normal”.

**2. How does it prove it?** Preferably without a secret. Managed identities and federated credentials (workload identity federation) replace stored secrets with short-lived tokens issued by the platform the workload runs on. When an agent acts for a person, the token has to carry both: the person as the subject, and the agent as the actor. That is what makes the delegation visible to the API, to the audit log and to a risk scorer.

**3. Who answers for it?** Every NHI needs a person who is accountable for it. That means an owner, a review date and access that expires. Entra separates *owners* (technical) from *sponsors* (business, at least one required). SailPoint distinguishes a machine account with a single owner from a machine identity with several. Recertification and time-bound access are what stop yesterday’s experiment from becoming tomorrow’s standing privilege.

**4. Is it behaving like itself right now?** Governance answers “should it have this access?” on a review cycle. Runtime risk answers “is this sign-in normal?” on every event. This fourth question is the one my platform answers, and it is the one this post is about.

None of these four questions is specific to one vendor. Here is how the first three land in the three products I see most often:

| Question | Microsoft Entra | SailPoint | Okta |
|---|---|---|---|
| Who is it? | Agent identity from a blueprint; service principals; managed identities | AI agents and machine identities, discovered and classified | AI agents in the directory, linked to an app |
| How does it prove it? | Managed identity, federated credential; agent on-behalf-of uses the **jwt-bearer** grant | Not an issuer; governs the resulting permissions | Cross App Access uses **RFC 8693** token exchange |
| Who answers for it? | Sponsor (required) and owners; access packages that expire | Owners; NHI certification campaigns | Owners; certifications for agents not described |

One detail surprised me. I expected Entra’s agent delegation to use the standard OAuth token-exchange grant (RFC 8693), as Okta’s Cross App Access does. It doesn’t: Entra uses the jwt-bearer grant. If your estate spans both, “the agent acts for the user” is two different protocols. A risk engine shouldn’t depend on either one, so it should reconstruct the chain of who acted for whom from the logs.

## What “behaving like itself” means for an NHI

People are noisy. They travel, change laptops and work late. Workloads are not. A payroll sync calls the same API, from the same network, with the same credential type, at roughly the same rate, every day. That regularity is the signal. Anything new means more for a workload than it does for a person.

I gave every non-human identity its own 30-day baseline and five signals:

- **New network.** A new ASN or IP for a workload that has only ever called from one place.
- **New resource.** A token for an API it has never asked for.
- **Credential drift.** A **client secret** used by an identity whose whole history is federated credentials, certificates or managed identity. This is a classic sign of a leaked secret: the legitimate workload never uses it, so the attacker is the one presenting it.
- **Token velocity.** Tokens in the last 15 minutes against *this identity’s own* average rate, not a global threshold. Twenty tokens is quiet for one workload and a five-fold burst for another.
- **The delegating person’s risk.** When an agent acts on behalf of a user, it inherits that user’s latest risk score.

The last one is the reason I built this. The platform already scores every human sign-in, so it knows when Alice’s account is looking compromised. Now, when an agent acts for Alice, that score comes with it. A compromised person can’t launder access through an agent, because the agent is only as trusted as the person it serves.

Governance data from the identity graph adds three more: how many owners and sponsors the identity has, whether it holds a privileged role, and how many days since anyone last recertified it.

## Six rules, and the ones that must never run

From those signals come six rules, deliberately few:

| Rule | Fires when | Outcome on its own |
|---|---|---|
| Agent acting for a risky user | Delegating user scores 30 or more (above 70) | Step up (block) |
| Privileged NHI with no owner | Privileged role, zero owners or sponsors | Step up |
| Secret where federation is the norm | Credential drift | Step up; block if privileged |
| New network or resource | Either is new (both are new) | Adds risk (step up) |
| Token burst | At least five times its own rate | Up to step up |
| Stale recertification | Never reviewed, or more than 90 days ago | Adds risk |

The more important change is what **doesn’t** run. The human rules about MFA, devices, business hours and impossible travel are now guarded so they only run for people, both in the scorer and in the policy. The rule from the start of this post still blocks an administrator without MFA. It no longer blocks a backup job.

I also kept the anomaly model away from non-human identities for now. It was trained on human behaviour. Asked about a workload that signs in at 03:00 with no MFA and no device, it would call every service principal an outlier. So non-human identities are scored by rules and policy only, until there is enough reviewed data to train a model on them. A model trained on the wrong population shouldn’t be in the loop.

## Step up, when nobody can be stepped up

For a person, “step up” means another MFA prompt. An agent can’t answer one, so the policy has to mean something else.

- **STEP_UP** puts a person in the loop instead: the agent’s **sponsor or owner approves**, or the delegated scopes are narrowed to what this task needs. For credential drift, the owner confirms the secret use and rotates the identity to a federated credential.
- **BLOCK** acts on the identity: **revoke its refresh tokens and sessions, disable the service principal** or drop its time-bound grant, and page the owner. For an agent acting for a high-risk user, revoke the delegated grant for that user.

The decision values are still ALLOW, STEP_UP and BLOCK, and the policy engine is still the only place that decides. What changes is the enforcement attached to each value, and that the policy now knows the subject type: human, workload, managed identity or agent. It also knows the actor chain, meaning whose behalf the agent is acting on.

A blocked agent should also trigger an off-cycle recertification. A runtime alert is evidence that a governance review should have caught something, and a reviewer deciding whether an agent keeps its access should see its runtime risk history.

## The poller that was itself a non-human identity

There was some irony in this. The component that reads risk data from Microsoft Graph is itself a non-human identity, and it authenticated with a client secret.

It doesn’t any more. It now authenticates with its own managed identity. To read another tenant, it presents its managed identity’s token as a federated credential on an app registration, and Terraform creates the trust. The client secret is still accepted for local development, with a warning in the log.

Writing about secretless workloads from a service that held a secret would have been hard to defend.

## Where this stops working

- **Field names I couldn’t confirm.** Microsoft documents the agent-type marker on audit records, and says agent sign-ins carry a dedicated event type, but I couldn’t find the exact property path on exported sign-in records. The mapping is isolated in one function and flagged, but it has to be checked against real tenant data before anyone relies on it.
- **Governance data has to exist.** Owners, sponsors and recertification dates come from whichever governance tool you use, synced into the identity graph. Without that data, the ownership and recertification rules stay silent by design: an unknown is a data gap, not evidence of a missed review.
- **No model for non-human identities yet.** Rules catch what I thought of. Behaviour I didn’t think of needs the anomaly model, trained on non-human data and analyst verdicts. That is the next piece of work.
- **The tests prove the logic, not the deployment.** 188 unit tests cover the normaliser, the signals, the rules and the policy fallback, all against fakes. The policy and the infrastructure were reviewed but not executed by their own tools in that environment. Proof that it works end to end needs a real tenant.

Treat an agent as an identity: give it an owner, a review date and access that expires, and score it against its own baseline and against the trust of the person it acts for. The vendors cover who the agent is and what it may hold. The gap I wanted to close is whether it is still behaving like itself.

Which non-human identities in your tenant would you not be able to name an owner for today? [Tell me on LinkedIn](https://linkedin.com/in/anandkn2012).

## References and further reading

- **Entra agent identities:** Microsoft, [Agent identity blueprints](https://learn.microsoft.com/en-us/entra/agent-id/agent-blueprint), [Owners, sponsors and managers](https://learn.microsoft.com/en-us/entra/agent-id/agent-owners-sponsors-managers) and [Agent ID governance](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview).
- **Delegation:** Microsoft, [Agent on-behalf-of flow](https://learn.microsoft.com/en-us/entra/agent-id/agent-on-behalf-of-oauth-flow); Okta, [Cross App Access](https://developer.okta.com/docs/concepts/xaa).
- **Governance of machine identities:** SailPoint, [Machine Identity Security](https://documentation.sailpoint.com/saas/help/machine/index.html) and [Access reviews for non-human identities](https://www.sailpoint.com/blog/bringing-access-reviews-to-your-non-human-identities).
- **Agent sign-in logs:** Microsoft, [Sign-in and audit logs for agents](https://learn.microsoft.com/en-us/entra/agent-id/sign-in-audit-logs-agents).
