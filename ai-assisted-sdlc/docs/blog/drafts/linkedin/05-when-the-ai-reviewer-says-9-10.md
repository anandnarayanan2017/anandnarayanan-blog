The AI reviewer gave the code 9/10.
The test proved it booked one meeting room ten times.

Both were honest.

The reviewer read careful-looking code: a transaction, a clash check, a 409.
The test ran twenty requests at once and counted the bookings.

A reviewer judges plausibility. A test measures behaviour.

So my harness has one rule: a deterministic check outranks any model's judgement. The model can add a failure. It can never remove one.

I still keep the AI reviewer. It's good at what tests miss: craft, missing checks, the next test nobody wrote yet.

But I measure it first. I graded its real inputs by hand and run it against my grades. The number that matters is false approvals: work I failed that it passed. One is enough to fail the run.

If you haven't measured your AI reviewer against people, you have a second opinion of unknown quality.

Part 5 of 7 on engineering with AI agents.

Has an AI reviewer ever approved something your tests or your users later proved wrong?

First comment: Read the full article → -05-when-the-ai-reviewer-says-9-10/
Code and tests: /examples/double-booking

#AIAgents #SoftwareTesting #AIAssistedDevelopment #SoftwareEngineering
