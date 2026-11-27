My coding agent has no tools.
It returns files. The harness decides what happens to them.

That is a big part of why the controls in this series work. An agent that can only return text can't do much with a bad idea.

The next step for any "agentic SDLC" is tools: open a pull request, read CI logs, look at the ticket. In 2026 those arrive through MCP servers.

So before building the gateway that hands them out, I threat-modelled the whole factory.
STRIDE per element. Each abuse case mapped to MITRE ATLAS and the OWASP LLM and Agentic Top 10s.

Nine trust boundaries. Fifteen abuse cases. 31 controls:
→ 16 built and tested
→ 2 partly built
→ 11 planned, nearly all at the gateway
→ 2 open gaps, written down

Five decisions it forced before any gateway code:
1. Rules decide what is blocked, not a model score.
2. Fail closed: if the gateway can't decide, the run pauses.
3. Irreversible actions (merge, deploy, change a secret) are not agent tools at all.
4. Every allow and every refusal is evidence, kept outside the harness.
5. Start narrow and widen with evidence.

The uncomfortable one: a poisoned ticket can still smuggle a harmful change through if no test describes the harm. That is a specification problem, not a prompt problem.

Which boundary in your agent setup has the most arrows and the fewest controls?

#AIAgents #ThreatModeling #MCP #OWASP #AISecurity #SoftwareArchitecture
