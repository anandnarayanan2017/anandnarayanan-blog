# The Harness Around the Agent

<!-- HERO (to draw): the same monkey agent at two desks. Left: alone with a laptop and a sticky note "Build a booking API". Right: the same monkey inside a workshop with a spec on the wall, a test rig blinking red, a logbook, and a "restart from here" bookmark. Caption idea: "Same model. Different workshop." Save as ../images/03-the-harness-around-the-agent-1.png -->

*Same model, different workshop. Most of what makes an agent reliable is not in the model.*

In Part 2, the twenty-request test caught the double booking. The failure went back to the agent, and the second attempt passed.

That sentence hides most of the engineering.

Who ran the test? Who decided the agent should see the failure? What did the agent see on its second attempt: the whole conversation, or just the error? And if the machine had crashed between attempt one and attempt two, where would the work have resumed?

None of that is the model. All of it is the harness.

## What a harness is

A harness is everything around the model that turns one clever reply into a delivery process:

- **Context:** what the agent knows when it starts.
- **Tools:** what it can actually do.
- **Feedback:** how it finds out it was wrong.
- **Recovery:** what happens when it, or anything else, fails.

Most debates about AI coding are about the model. Which one writes better code, which one is cheaper, which one came out last week. Those matter. But in my own experiment the same model behaved very differently depending on what surrounded it, and the surrounding parts were the ones I could control.

I built a small harness to find out what that surrounding has to do. It runs delivery as a loop: a planner expands the request into features, a contract step agrees what “done” means for each feature and writes the tests, a generator writes the code, a check runs the tests, an evaluator reviews, and a person approves the release. It is an experiment, not a product. Here is what each of the four parts turned out to need.

## Context: a map, not a manual

My first instinct was to give the agent everything. Every requirement, every convention, every decision, in one long instruction file.

It works badly. Context is scarce. A long instruction file crowds out the task, and the agent can’t tell which of the forty rules matters for the change it is making.

What works better is a short map that says where knowledge lives, and the knowledge itself in the repository, loaded when the task needs it. The specification from Part 2 is a file. The architecture rules are a file. The decisions are files. If a decision was made in a chat and never written down, the agent can’t see it. Neither can the next person.

The rule I ended up with: **if it isn’t in the repository, it doesn’t exist.**

## Tools: few, and boring

The generator in my harness has exactly one ability: it returns file contents, and the harness writes them into the workspace.

It can’t run a shell. It can’t install a package. It can’t push. The harness runs the checks, starts the app, and talks to git. The agent proposes; the harness acts.

That sounds restrictive, and it is. It is also why the next part of this series is short to explain: an agent that can only return files has a small, visible blast radius. (What the agent may touch, and how that is enforced, is Part 4.)

## Feedback: let the system say “no”

This is the part that did the work in Part 2.

After every attempt the harness runs the contract’s tests and passes the agent the failing test names and the assertion output. Not a summary. Not “there seem to be some issues”. The actual failure:

```text
FAIL  tests/s5-concurrency.test.ts > concurrency safety >
      exactly one of 20 simultaneous requests for the same slot wins
AssertionError: expected [ 201, 201, 201, 201, 201, 201, …(4) ] to have a length of 1 but got 10
```

The second attempt fixed it. The agent didn’t need to be cleverer. It needed to be told, precisely, that it was wrong.

The next sprint showed the same pattern on a much duller bug. The availability search returned HTTP 400 for every request. The tests said so: `expected 400 to be 200`. The cause was route order: the route for `/rooms/:id` was registered before `/rooms/available`, so “available” was being read as a room id. One line of feedback, one reordered route, done.

A good feedback loop is not a smarter reviewer. It is a fast, specific, honest “no”.

## Recovery: assume everything fails

Agents fail. So do networks, rate limits, laptops and the person running the experiment. The harness has to assume all of them will.

Three choices made recovery boring, which is what you want:

1. **Every agent call starts fresh.** The agents don’t share a long conversation. Each one reads its inputs from files and writes its outputs to files. Nothing important lives only in a context window, so nothing important is lost when one ends.
2. **Progress is a file, and every attempt is a commit.** The harness records which features are done and how many attempts each took. If the process dies, it resumes from that file. If an attempt makes things worse, the previous attempt is one `git checkout` away.
3. **Retries are limited, and running out stops everything.** Each feature gets three attempts. A feature that still fails blocks the run. Nothing is built on top of a broken base.

The third one feels harsh until you see the alternative: an agent that has failed three times at concurrency, now building availability search on top of a booking table that double-books.

## Every part encodes a doubt

The most useful way I found to think about a harness: **every component is an assumption about what the model gets wrong.**

| Component | The doubt it encodes |
|---|---|
| Planner expands the request | Models under-scope from a short prompt |
| Contract agrees “done” and the tests first | Models drift from the specification mid-build |
| Deterministic check | Models can’t reliably verify their own work |
| Architecture rules | Models erode layering unless it is enforced |
| Live probe of the running app | Reading code misses runtime bugs |
| Separate evaluator | Self-grading is lenient |
| Human gate | Accountability stays with people |

That table is also a to-do list. As models improve, some of these doubts stop being true, and the component should be removed, not kept out of habit. The only honest way to know is to measure: run the same work with and without the component and compare. (The measurement is part of Part 7.)

## Where this stops working

- **It costs more.** Fresh contexts mean every call re-reads the workspace. My harness sends the whole project snapshot to every role, and that cost grows with the project. Role-specific context is on its to-do list.
- **The feedback is only as good as the tests.** The loop converges on whatever the tests check. Part 2’s warning applies: a test that encodes the wrong rule produces confidently wrong code, faster.
- **One run is an anecdote.** The run log in this post is a live model run, recorded so it can be replayed exactly against a real PostgreSQL. It shows the mechanism, not a failure rate. Other runs, and other models, fail in messier ways and need more than three attempts more often than I would like.

A harness tells the agent what “correct” means and lets the system say no. It doesn’t yet say what the agent is allowed to touch. That is the next part.

**Next: Part 4, “Please Be Careful” Is Not a Permission Model.**

What is in the harness around your coding agent today, and which of those parts did you design on purpose? [Tell me on LinkedIn](https://linkedin.com/in/anandkn2012).

## References and further reading

- **The run log and tests:** [examples/double-booking](https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc/examples/double-booking): the concurrency tests and the run log behind “ten times”.
- **Harness design:** Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) and [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps).
- **A map, not a manual:** OpenAI, [Harness engineering](https://openai.com/index/harness-engineering/), on keeping agent instructions short and the knowledge in the repository.
- **Agents and workflows:** Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
