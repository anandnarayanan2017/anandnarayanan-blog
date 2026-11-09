"Do not modify the tests."
"Never touch production."
"Be careful with destructive commands."

Every agent instruction file I read has lines like these.
Every one is a good rule. None of them is a permission.

A prompt is a request. The model usually follows it. "Usually" is fine for writing style. It isn't fine for "never delete the customer table".

For any agent, I now ask three questions:
1. What may it read?
2. What may it change?
3. What may it execute?

And one more for each: what stops it if it tries anyway?

In my harness:
→ The tests are restored from the contract before every check. An edited test is overwritten. A deleted one comes back.
→ Writes outside the workspace are refused.
→ The agent never gets a shell. Only fixed, pre-agreed commands run.
→ Untrusted code runs in a separate process: no network, no child processes, ten-second timeout.

The rule I'd put on the wall: the thing that judges the work must not be writable by the thing being judged.

Part 4 of 7 on engineering with AI agents.

Which rule in your agent's prompt would cause real damage if it were ignored? And what actually enforces it?

First comment: Read the full article → -04-please-be-careful-is-not-a-permission-model/

#AIAgents #AISecurity #SoftwareArchitecture #SoftwareEngineering
