"Privileged role, no MFA: block."

Every security team has that rule. It is a good rule.

Then I started scoring service principals, managed identities and AI agents with the same platform, and realised it would have blocked every automation in the tenant.

An agent can't answer an MFA prompt.

Non-human identities already outnumber people in most tenants. They hold standing privileges, often authenticate with secrets that live for years, and nobody is paged when one signs in at 03:00, because that is when it always signs in.

Four questions every non-human identity has to answer:
1. Who is it? One identity per workload, never shared.
2. How does it prove it? Federated credentials and managed identities, not secrets.
3. Who answers for it? An owner, a sponsor, a review date, access that expires.
4. Is it behaving like itself right now?

The fourth one is where I spent the effort.

Workloads are regular, so "new" means more: a new network, a new API, or a client secret used by an identity that has only ever used federation (a classic leaked-secret pattern).

And an agent acting on behalf of a person inherits that person's current risk score. A compromised user can't launder access through an agent.

For an agent, step-up isn't another MFA prompt. It means sponsor approval or narrower scopes. Block means revoke tokens and disable the service principal.

One surprise: Entra's agent on-behalf-of flow uses the jwt-bearer grant, while Okta's Cross App Access uses RFC 8693 token exchange. Same idea, two protocols.

Part 1 of a new series on identity for AI agents, mapped to Entra, SailPoint and Okta.

Which non-human identities in your tenant could you not name an owner for today?

First comment: Read the full article → https://anandnarayanan.net/blog/agent-identity-01-an-agent-cant-answer-an-mfa-prompt/

#IdentitySecurity #AIAgents #IAM #ZeroTrust #MicrosoftEntra
