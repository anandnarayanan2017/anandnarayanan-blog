"Does it detect prompt injection?"

No. And I think that's the honest answer for most tools that say yes.

Agent Sentinel doesn't read a prompt and decide it's an attack. It checks what the agent did afterwards, against the policy written for that agent.

So I tested it. One invoice with an injected instruction, and ten things that could happen next.

It caught every outcome that left the policy: a tool the agent may not use, six bytes to an unknown server, a lookalike hostname, an oversized prompt, a runaway loop.

It caught none that stayed inside it. An allowed report tool, with the attacker as recipient, looks like an ordinary report. And redaction had removed the recipient's address from the evidence.

Three lessons for a design review:

The policy is the control. A loose policy catches less.
Check arguments inside the tool, where the action happens.
Recording is not prevention. Every finding comes after the action.

All ten are tests in the repository, including the ones that get through.

Which of the ten would your monitoring have caught?

First comment: Read the full article → https://anandnarayanan.net/blog/agent-sentinel-06-prompt-injection-what-the-recorder-catches/
Code and tests: https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/agent-sentinel

#AIAgents #PromptInjection #AISecurity #OWASP
