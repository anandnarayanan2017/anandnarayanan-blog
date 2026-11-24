<!--
DRAFT, an Agent Sentinel series note for LinkedIn, tied to Part 4 (identity).
It has no number and no date in series.json because it has no article of its
own: the lasting content is the "Who owns the agent" section of
../technical-details/04-enterprise-foundation.md. Delete this comment block
before posting.

Check against Microsoft Learn ("What's new in Microsoft Entra Agent ID" and the
Agent ID lifecycle policy page) before posting. This was drafted from a web
search, not from the Microsoft pages themselves:

1. The inactivity numbers. The search found: owners notified after 60 days,
   identity disabled after 90, deleted after 455. If the page says otherwise,
   change the sentence marked [CHECK 1].
2. Preview or generally available. The search found preview. Change [CHECK 2]
   if that has moved, for example at Ignite.
3. Sponsor reconfirmation or attestation for agents. Not confirmed by the
   search, so the post does not claim it. Add one line if the page documents it.
4. Anything announced at the Ignite keynote that changes the above.
-->

Who is accountable for an AI agent six months after the project team has moved on?

Microsoft's recent Entra Agent ID updates start to answer that in the product, not in a policy document.

An agent identity gets a sponsor: a named person accountable for it. If the sponsor changes role or leaves, a workflow can pass the sponsorship on. And an agent that goes quiet is cleaned up: the owner is notified after 60 days of inactivity and the identity is disabled after 90. [CHECK 1]

It is still in preview, so not something to depend on in production yet. [CHECK 2] But the direction matters more than the dates.

For years, service accounts outlived the people who created them. Agents will do the same, faster, and with more access.

What identity governance does not tell you is what the agent did while it was active. A valid, sponsored, recently used identity can still send data somewhere it shouldn't.

So I think of it as three separate questions:

Should this agent still exist? Identity lifecycle.
What is it allowed to do? A policy per agent.
What did it actually do? A record, with evidence.

Entra is moving on the first. Most of my writing here is about the second and third. In Agent Sentinel, an agent with no policy entry is itself a finding, before it does anything wrong.

Each one is weaker without the other two.

This is a note alongside my Agent Sentinel series. Part 4 covers identity: who may call the recorder, and who owns the agent.

Who sponsors the agents in your organisation today? Is it a named person, or a team alias?

First comment: Agent Sentinel, Part 1: why agents need a record of what they did → https://anandnarayanan.net/blog/agent-sentinel-01-why-agents-need-a-flight-recorder/

#AgentSentinel #AIAgents #MicrosoftEntra #IdentityGovernance
