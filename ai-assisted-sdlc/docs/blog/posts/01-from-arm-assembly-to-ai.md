# From ARM Assembly to AI: Twenty Years of Explaining Myself to Computers

![AI-Native SDLC Factory: an architect relaxes with a "Still in control... right?" mug while monkey agents build, test and deploy. Every dashboard check is green; the anomalies panel reads "Boardroom booked 10 times".](../images/01-from-arm-assembly-to-ai-1.png)

*All checks green. Every anomaly red. Spot the problem.*

I started my career writing C and ARM assembly to optimise codecs. Back then, I would study a loop, examine memory access, and rearrange instructions to save a few CPU cycles. A small performance improvement could make my day.

Today, my browser uses more memory to display a meeting invitation than some of those systems had available.

I try not to take it personally.

Then I moved into Java enterprise development. Memory management became somebody else’s responsibility. In return, I met factories, interfaces, dependency injection, and stack traces with enough material for a weekend reading plan.

In assembly, I knew which register held my value. In Java enterprise development, I sometimes needed three people to explain which service owned it.

The abstraction had moved up a layer. My job hadn’t: know where things live, and what happens when they break.

Eventually, I became an architect. I drew boxes and connected them with arrows. The boxes had impressive names. The arrows looked simple.

Those arrows contained authentication, retries, timeouts, network failures, and the small question of what happened if the money left one system but never arrived in the other. Experience taught me to spend more time asking about the arrows.

Then came the cloud. Infrastructure became code. Environments could be created in minutes. Scaling became much easier.

So did accidentally leaving something expensive running.

I had progressed from asking, “Why does this take so many cycles?” to “Why does this subscription have seventeen databases?”

And now, AI. I can type:

“Build a booking API.”

An agent produces endpoints, database models, tests, and documentation. For a moment, I wonder whether twenty years of engineering was an elaborate training programme for typing one sentence.

Then I review the result.

Right. Still work to do.

**“Build a booking API” is a wish.**

Here is an illustrative specification:

> Twenty people try to book the same room for the same time slot simultaneously. Exactly one request succeeds with HTTP 201. The other nineteen receive HTTP 409. The database enforces the rule.

Now we have something we can design and test. Without that detail, you can end up with an implementation that passes every happy-path test and books the boardroom ten times.

The dashboard is green.

The meeting is a contact sport.

This is what interests me about AI-assisted development: how much engineering work goes into making a task clear enough to delegate and a result reliable enough to accept. We need to define behaviour, constraints, failure cases, and the evidence that will convince us it works.

We also need a harness: the context, tools, permissions, and checks surrounding the agent. Which files can it change? Which commands can it run? What requires review? What happens when a check fails?

“Please be careful” remains a charming security policy.

That thinking is behind my [**AI-assisted SDLC project**](https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc): exploring how intent, specifications, and a structured development workflow can guide AI-assisted implementation.

After twenty years, I find myself using old lessons in a new setting. Measure the result. Question assumptions. Check failure paths. Understand the arrows.

AI makes producing code faster. It doesn’t make deciding what “correct” means any faster.

I began by writing instructions for an ARM processor. Now I write instructions for an agent that writes instructions for a processor.

More layers. Same question:

**How do we know it works?**

## What’s next in this series

This first part was about the shift in abstraction: AI can produce code quickly, but engineering still starts with deciding what “correct” means.

The next six parts go deeper into the system around the agent, one question at a time:

2. **A Prompt Is Not a Specification.** Turning vague intent into explicit, testable invariants.
3. **The Harness Around the Agent.** Context, tools, feedback loops and recovery: what surrounds the model matters as much as the model.
4. **“Please Be Careful” Is Not a Permission Model.** What the agent may read, change and execute, enforced by the system rather than requested in a prompt.
5. **When the AI Reviewer Says 9/10 and the Test Still Fails.** Where probabilistic judgement helps, and where deterministic verification must win.
6. **Human Approval Is a Control, Not a Button.** Deciding which changes proceed automatically and which need a person, and making that review mean something.
7. **From Coding Agent to Engineering Factory.** Specifications, tools, verification, approvals and evidence brought together into one delivery flow.

Which of these is your team struggling with most right now? [Tell me on LinkedIn](https://linkedin.com/in/anandkn2012). It will shape what I go deeper on.

[Follow the series on GitHub](https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc)

## References and further reading

- **The booking specification, as code:** [examples/double-booking](https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc/examples/double-booking). The twenty-request concurrency test, the check-then-insert implementation the agent produced first, and the database constraint that fixes it. The example runs in CI on every change.
- **From intent to specification:** David Thomas and Andrew Hunt, *The Pragmatic Programmer*, 20th Anniversary Edition (Addison-Wesley, 2019). A useful reminder that requirements become clearer through feedback and refinement rather than arriving perfectly formed.
- **The arrows between the boxes:** the [fallacies of distributed computing](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing), associated with L. Peter Deutsch and colleagues at Sun Microsystems. The network is reliable, latency is zero: the assumptions that make an arrow look simple.
- **Concurrency and meeting-room bookings:** Martin Kleppmann, *Designing Data-Intensive Applications* (O’Reilly), chapter on transactions. The discussion of write skew and booking systems is a useful example of why some invariants belong in the data layer.
- **Letting the database enforce the invariant:** PostgreSQL documentation, [Exclusion constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION).
- **HTTP semantics:** [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110), including 201 Created and 409 Conflict.
- **Agents and harnesses:** Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) and [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).
- **Engineering discipline for agents:** Matt Pocock, [Skills for real engineers](https://github.com/mattpocock/skills), agent skills grounded in classic software engineering practice.

## Acknowledgements

Thanks to Claude by Anthropic, which I used as a reviewer and editor while writing this post. The architecture, examples, opinions and any mistakes are my own.
