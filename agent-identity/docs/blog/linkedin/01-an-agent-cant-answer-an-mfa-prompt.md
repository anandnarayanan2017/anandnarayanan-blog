In July, AI agents broke into Hugging Face. Not one of them typed a password.

They didn't need to. Fourteen Hugging Face access tokens, with write rights, were sitting in a public dataset. The agents found them and used them.

A token is a key that software uses instead of a password. It never gets an MFA prompt. Whoever holds it is trusted.

That is the gap. Your strongest rule, "privileged access needs MFA", protects people. It does nothing for a key that a machine presents, and an AI agent can't answer an MFA prompt anyway.

So for every non-human identity, ask four plain questions:
1. Who is it? One identity per workload or agent, never shared.
2. How does it prove it? Short-lived tokens from the platform, not secrets that live for years in a file.
3. Who answers for it? A named owner, a review date, access that expires.
4. Is it behaving like itself right now? A key used from a new place, or for a new API, is a red flag.

And when an agent acts for a person, it should only be as trusted as that person is right now.

Part 1 of my new series, Identity for AI Agents, mapped to Entra, SailPoint and Okta.

Which keys in your estate would still work if someone found them in a public file today?

![Meme: the architect relaxes in the "Agent Identity Control Room" while monkey agents with "No owner", "No MFA" and "Old secret" shirts ship boxes of "14 tokens" and "keys". Every identity check is green, the anomalies panel lists "14 tokens in a public dataset" and "Agent asked for MFA: no phone", and the kill switch reads "Revoke tokens".](01-an-agent-cant-answer-an-mfa-prompt-meme.jpg)

First comment: Read the full article → https://anandnarayanan.net/blog/agent-identity-01-an-agent-cant-answer-an-mfa-prompt/
Sources on the Hugging Face incident: OpenAI's technical report and Hugging Face's statement (July 2026).

#IdentitySecurity #AIAgents #IAM #ZeroTrust #NonHumanIdentity
