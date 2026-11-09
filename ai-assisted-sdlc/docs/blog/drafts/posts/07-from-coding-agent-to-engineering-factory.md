# From Coding Agent to Engineering Factory

<!-- HERO (to draw): callback to Part 1's factory. The same monkey agents, now on a tidy line: a spec board at the start, a test rig that can light red, a locked cabinet labelled "tests & policies", a logbook, and at the end the architect awake at a desk with an "Approve" stamp and a folder labelled "Evidence". The anomalies panel now reads "Boardroom booked 1 time". Save as ../images/07-from-coding-agent-to-engineering-factory-1.png -->

*A factory is not more agents. It is the same agents, inside a process that can tell you what it built and why it is safe.*

Part 1 opened with a cartoon: an AI factory, every dashboard green, and an anomalies panel reading “Boardroom booked 10 times”.

Six parts later, the boardroom is booked once. Not because the model got smarter between posts. Because of what we put around it.

This last part puts those pieces into one flow and is honest about which parts I have built, which I haven’t, and what I would do first in a real team.

## One flow

Here is the delivery flow the series has been building, one control per part:

```text
Request ──► Specification ──► Contract ──► Agent writes code ──► Checks ──► Reviewer ──► Human gate ──► Release
            (Part 2)          (Part 2)     inside a harness      (Part 5)   (Part 5)     (Part 6)
                                           with enforced limits
                                           (Parts 3 and 4)
                          ◄───────────── failures fed back, limited retries ─────────────┘
```

Read it as a sequence of decisions, each made by whatever is best placed to make it:

1. **A person states the intent.** “Users book meeting rooms by the hour.”
2. **The invariants are written down, with their evidence.** “No two confirmed bookings overlap, enforced by the database. Twenty simultaneous requests: one 201, nineteen 409s.”
3. **A contract fixes what ‘done’ means for each feature,** including the tests, before any code is written.
4. **An agent writes code inside a harness** that gives it context, a small set of tools and fast feedback.
5. **Permissions are enforced by the system:** no shell, no writes outside the workspace, tests restored before every check.
6. **Deterministic checks decide:** tests, type checks, architecture rules, live probes.
7. **An AI reviewer looks for what the checks missed.** It may add a failure. It may never remove one.
8. **A person approves the release,** with the evidence attached, and the default is no.

Every step leaves something behind: a file, a test result, a commit, a transcript. That trail is the point.

## The orchestrator is not an agent

People who hear “agent factory” often picture a manager agent deciding which worker agent to call next.

I deliberately didn’t build that. The flow above is ordinary, deterministic code. It decides the order of the steps, the number of retries, when to stop and when to ask a person. Agents fill roles inside it: planner, contract writer, generator, prober, evaluator. Any role can be served by any model, and swapping the model doesn’t change the flow.

A language model choosing the control flow would be more flexible. It would also be harder to reproduce, harder to audit, and able to skip a check because it seemed unnecessary today. For the part of the system whose job is to make sure the checks happen, I want boring.

**Agents do the work. The process decides what counts as done.**

## Evidence is the product

A coding agent produces code. An engineering factory produces code *and the evidence that it is safe to ship*.

For every run, my harness keeps:

- the specification and the contract for each feature, with its tests;
- one git commit per attempt, failed ones included;
- the output of every check and every live probe;
- a transcript of every model call: what it was asked and what it replied;
- the evaluator’s scores, and every case where a check overruled it;
- a summary of attempts, tokens, cost and time.

None of this is extra paperwork written for an auditor. It falls out of running the flow. That is the test of a good control: the evidence is a by-product, not a chore.

## Measure the factory, not just the model

Part 3 described every harness component as a doubt about the model. Doubts should be tested.

The same flow makes that possible. Because the contracts and tests are fixed, I can run the same work through different models from different vendors and score them only on what executed: which features passed their tests, in how many attempts, at what cost. No AI judge decides the ranking. And because each harness component can be switched off, I can ask the more useful question: *does this component still earn its place with this model?*

Some won’t, in a year. That is fine. A harness that never removes anything becomes a museum of last year’s model weaknesses.

## What I have built, and what I haven’t

Honesty about scope, because a factory diagram is cheap:

| Stage | In my experiment today | Not yet |
|---|---|---|
| Requirements | A planner expands a short request into features | Structured requirements and user stories |
| Specification and tests | Contracts with tests, written before the code | Invariants reviewed by a person before the build |
| Code | Generator inside the harness | — |
| Verification | Tests, architecture rules, live probes, calibrated reviewer | — |
| Approval | Fail-closed gate, once per release | A signed record of who, when and which commit |
| Integration and deployment | A commit per attempt in a local workspace | Branches, pull requests, a real deployment |
| Operations | Build-time metrics and transcripts | Production signals feeding the next backlog |

The left column is enough to show the ideas work on a small, real problem. The right column is where a real organisation would spend most of its effort, and where agents will be most tempting and most dangerous: deployment, data and production access.

## If I were starting in a real team on Monday

Not a platform. Not eight new agents. Five small things:

1. **Pick one invariant that hurts when it breaks** and make it a test that runs on every change. Part 2.
2. **Write down what your agents may read, change and execute,** and move one rule from the prompt into the system. Part 4.
3. **Make one rule non-negotiable:** a failing deterministic check can’t be overruled by an AI review. Part 5.
4. **Protect what judges the work** — tests, policies, pipeline — so that agents can’t change it without a named person. Parts 4 and 6.
5. **Decide which changes need a person,** by reversibility and blast radius, not by size, and give that person the evidence. Part 6.

None of these needs a new tool. Each needs a decision.

## Back to the first question

I started by explaining myself to computers in C and ARM assembly. Then Java enterprise, then boxes and arrows, then infrastructure as code, now prompts. Every step raised the level of abstraction, and every step left the same question with the engineer: how do we know it works?

Agents don’t change that question. They change how much rides on the answer, because they produce more code, faster, than any team can read.

The answer can’t be “the agent was confident”. It can’t be “the reviewer gave it 9/10”. It has to be a specification someone wrote down, checks that can’t be talked out of their result, boundaries the system enforces, and a person who could have said no.

That isn’t the opposite of moving fast with AI. It is what makes moving fast safe enough to keep doing.

Thank you for reading the series. Which of the seven parts would you start with in your own team, and what is missing from the list? [Tell me on LinkedIn](https://linkedin.com/in/anandkn2012).

[Follow the series on GitHub](https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc)

## References and further reading

- **The whole series:** Part 1 to Part 6 on [anandnarayanan.net](https://anandnarayanan.net).
- **Harness design:** Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) and [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), on preferring simple, composable workflows to autonomous orchestration.
- **Harness engineering:** OpenAI, [Harness engineering](https://openai.com/index/harness-engineering/).
- **Measuring by execution:** Mark Chen et al., [Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374) (2021), which introduced HumanEval and pass@k.
- **Delivery performance:** Nicole Forsgren, Jez Humble and Gene Kim, *Accelerate* (IT Revolution, 2018).
