<!--
LinkedIn Article version of Part 1 (the short post that shares it is
01-from-arm-assembly-to-ai.md). Too long for a LinkedIn post (3,000-character
limit): publish it with LinkedIn's Article editor. In the editor, make the
title and "What's next" headings, turn the two lists into bullets, and add the
links with the link tool. Use the hero image as the cover, with the caption
below the title as its caption.
-->

# From ARM Assembly to AI: Twenty Years of Explaining Myself to Computers

*Cover image caption: All checks green. Every anomaly red. Spot the problem.*

An AI agent built me a booking API. Every happy-path test passed.

It booked the boardroom ten times.

I started my career writing C and ARM assembly to optimise codecs. Back then, I would study a loop, examine memory access and rearrange instructions to save a few CPU cycles.

Today, my browser probably uses more memory to display a meeting invitation than some of those systems had available.

I try not to take it personally.

Then came Java enterprise development. Memory management became somebody else's problem. In return, I got factories, dependency injection and stack traces large enough to qualify as weekend reading.

Later, as an architect, I drew boxes and connected them with arrows. The boxes had impressive names. The arrows contained authentication, retries, timeouts, partial failures and awkward questions such as:

What happens if the money leaves one system but never reaches the other?

The abstraction kept moving upward. The engineering question stayed the same:

What happens when this breaks?

And now, AI.

Today I can type: "Build a booking API."

An agent produces endpoints, database models, tests and documentation. For a brief moment, twenty years of engineering appears to have been an elaborate training programme for typing one sentence.

Then I review the result.

Right. Still work to do.

**"Build a booking API" is a wish.**

This is closer to a specification:

> Twenty people try to book the same room for the same time slot simultaneously. Exactly one request succeeds with HTTP 201. The other nineteen receive HTTP 409. The database enforces the rule.

Now we have something we can design and test.

Without that detail, an implementation can pass every happy-path test and still book the boardroom ten times.

The dashboard is green.

The meeting is a contact sport.

The model writes the code. The specification and the checks decide what counts as correct.

That distinction is what interests me about AI-assisted development. Generating code is becoming cheaper. Deciding what behaviour must hold is not.

We still need to define:

- behaviour
- constraints
- failure cases
- invariants
- evidence

And once an agent can modify a codebase, we also need a harness around it:

- Which files may it read or change?
- Which commands may it run?
- Which checks must pass?
- What happens when a check fails?
- Which changes require human approval?

"Please be careful" remains a charming security policy.

None of this is a new form of software engineering. What is new is that we now delegate implementation to a system with context, tools, permissions and some autonomy.

That makes the boundaries more important, not less.

This is the thinking behind my AI-assisted SDLC project: explicit specifications, controlled tooling and deterministic verification around coding agents.

After twenty years, the lessons feel surprisingly familiar. Measure the result. Question assumptions. Test the failure path. Understand the arrows.

I began by writing instructions for an ARM processor. Now I write instructions for an agent that writes instructions for a processor.

More layers. Same question:

**How do we know it works?**

## What's next

Part 2: *A Prompt Is Not a Specification*, turning vague intent into explicit, testable invariants.

Originally published, with the full 7-part series roadmap, at https://anandnarayanan.net/blog/ai-assisted-sdlc-01-from-arm-assembly-to-ai/

Code, concurrency test and the run log behind "ten times": https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc#where-ten-times-comes-from

*Thanks to Claude by Anthropic, which I used as a reviewer and editor. The architecture, examples, opinions and any mistakes are my own.*
