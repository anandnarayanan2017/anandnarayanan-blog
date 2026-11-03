I asked an AI agent to build a booking API.
Every happy-path test passed.
It booked the boardroom ten times.

"Build a booking API" is a wish, not a specification.

A specification says: twenty people try to book the same room for the same slot at the same moment. Exactly one gets HTTP 201. The other nineteen get 409. The database enforces the rule.

Now there is something to design and test.

Twenty years ago I wrote ARM assembly to save CPU cycles. Today I write instructions for an agent that writes instructions for a processor. More layers. Same question: how do we know it works?

AI makes producing code faster. It doesn't make deciding what "correct" means any faster.

This is Part 1 of a 7-part series on engineering with AI agents.
Next: Part 2, A Prompt Is Not a Specification.

Is your team giving its agents specifications, or wishes?

![All checks green. Every anomaly red: an architect relaxes while agents build, test and deploy, and the anomalies panel reads "Boardroom booked 10 times".](../images/01-from-arm-assembly-to-ai-1.png)

First comment: Read the full article → https://anandnarayanan.net/blog/ai-assisted-sdlc-01-from-arm-assembly-to-ai/
Code, tests and the run log behind "ten times": https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc#where-ten-times-comes-from

#AIAgents #SoftwareArchitecture #AIAssistedDevelopment #SoftwareEngineering
