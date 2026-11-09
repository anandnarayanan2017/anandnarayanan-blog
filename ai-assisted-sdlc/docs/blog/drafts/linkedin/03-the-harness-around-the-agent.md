My AI agent double-booked a meeting room ten times.
The second attempt fixed it.

Not because the model got smarter between attempts.
Because something ran twenty requests at once, saw ten bookings, and told it, precisely, that it was wrong.

That something is the harness: everything around the model.

Context: a short map of where knowledge lives, not a forty-page instruction file.
Tools: few and boring. My agent can only return files. The harness runs everything else.
Feedback: the failing test name and assertion, not "there seem to be some issues".
Recovery: every call starts fresh, every attempt is a commit, three strikes stops the run.

The most useful idea I found: every part of a harness encodes a doubt about the model.
A separate reviewer, because self-grading is lenient.
A deterministic check, because models can't verify their own work.
A human gate, because accountability stays with people.

As models improve, some doubts stop being true. Measure, then delete.

Part 3 of 7 on engineering with AI agents.

Which parts of the harness around your coding agent did you design on purpose?

First comment: Read the full article → -03-the-harness-around-the-agent/
Code and tests: 

#AIAgents #SoftwareArchitecture #AIAssistedDevelopment #SoftwareEngineering
