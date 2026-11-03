A security tool that can break your payments run will be switched off by the first team it breaks. Then it records nothing.

In Part 1, Agent Sentinel caught a payments agent sending 250KB to a server nobody approved. That was simulated traffic: tidy, predictable, made to prove the rules work.

Real traffic is messier. Payloads the parser has never seen. A card number pasted into a prompt. A SIEM down for maintenance at 3am.

So moving to real model calls came down to one rule:

If the recorder fails, the agent must not.

In practice:
→ A payload it can't read is still recorded, not a crash.
→ It never stores the full prompt: only its size and a short preview, with credentials and card numbers removed first.
→ If alerting or the SIEM is down, the agent carries on, and every dropped alert is counted, not silently lost.

Fail-open has a cost: you can lose evidence. The design accepts that, but never silently.

Then I tested my own code against that rule. It failed in five places, invisible in the simulator. One was a detection bypass: a long enough prompt hid which model the agent called. All five are fixed, with a test each, and the article shows them.

This is Part 2 of a 5-part series on building it.
Next week: Part 3, Rules First, Statistics Second.

Which would worry you more: a recorder that occasionally misses an event, or one that occasionally blocks an agent?

First comment: Read the full article → https://anandnarayanan.net/blog/agent-sentinel-02-from-simulated-traffic-to-real-model-calls/
Code and tests: https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/agent-sentinel

#AIAgents #AIGovernance #CISO #AuditReadiness
