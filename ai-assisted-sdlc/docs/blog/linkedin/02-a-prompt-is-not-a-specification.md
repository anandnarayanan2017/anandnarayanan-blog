The AI reviewer scored the code 9/10.
The test failed.
Twenty people tried to book the same room at the same time. Ten of them got it.

The code looked careful: open a transaction, check the slot is free, insert, commit.

But under PostgreSQL's default isolation, every transaction that checks before the first one commits sees a free room. Ten of the twenty did.

My prompt never said "two people can't book the same room at the same time". Everyone knows that rule. That's why nobody writes it down.

So now, before an agent writes code, I ask three questions about each rule:

1. What must always be true?
2. Who enforces it: the application or the database?
3. What test would fail if it broke?

The second question fixed it. One database constraint, and the room can't be double-booked, whoever writes the next version of the API.

A prompt says what to build. A specification also says what must never happen.

Part 2 of 7 on engineering with AI agents.

What's one rule in your system that everyone knows and nobody has written down?

First comment: Read the full article → https://anandnarayanan.net/blog/ai-assisted-sdlc-02-a-prompt-is-not-a-specification/
Code and tests: https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc/examples/double-booking

#AIAgents #SoftwareArchitecture #AIAssistedDevelopment #SoftwareEngineering
