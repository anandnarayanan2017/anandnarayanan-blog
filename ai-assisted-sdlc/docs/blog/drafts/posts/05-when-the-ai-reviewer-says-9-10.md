# When the AI Reviewer Says 9/10 and the Test Still Fails

![The AI reviewer said 9/10 for careful-looking code with a transaction, a clash check and HTTP 409. The deterministic test ran 20 simultaneous requests for one room and got 10 bookings instead of 1. Verdict: FAIL, the check wins. A model’s judgement can add a failure but never remove one.](../../images/05-when-the-ai-reviewer-says-9-10-1.png)

*The reviewer judged what it could read. The test measured what actually happened.*

In Part 2 I promised to explain how an AI reviewer could score code 9 out of 10 while a test proved it double-booked a meeting room ten times.

The short answer: both were honest. They were answering different questions.

## What the reviewer saw

Here is the first attempt at concurrency-safe booking, in words: open a transaction, check whether the slot is taken, insert if it is free, commit.

That is what careful code looks like. It handles the clash. It returns 409. It uses a transaction, which is exactly what a reviewer hopes to see near the words “concurrency” and “booking”. A good human reviewer skimming a pull request at 6 p.m. would likely approve it too.

The bug isn’t in any line. It is in the gap between twenty transactions that each check before any of them commits. You can’t see that gap by reading the code. You see it by running twenty requests at once.

So the reviewer scored what it was shown: plausible, well-structured code. The test measured what happened: ten bookings for one room.

**A reviewer judges plausibility. A test measures behaviour.** When they disagree, behaviour wins.

## The one-way rule

The rule in my harness is short:

> A deterministic check outranks any model’s judgement. The model can add a failure. It can never remove one.

A feature passes only if the tests pass, the architecture rules pass, and the evaluator’s scores meet the threshold. All three. The evaluator can turn green into red. It can’t turn red into green.

In the recorded live run, that rule printed itself:

```text
CHECK FAIL | EVALUATOR functionality=9 craft=8 => FAIL
  !! evaluator approved, but the deterministic check failed: the check wins
```

It looks obvious written down. It isn’t how many teams use AI review today. An AI comment that says “looks good” sits next to a flaky test that someone reruns until it passes, and the human merging reads the friendlier signal.

## So why keep the reviewer at all?

Because tests only check what someone thought to test. Part 2 ended on that: four invariants protect four things.

The reviewer is useful in exactly the places the tests aren’t:

- **Craft.** Naming, duplication, a function doing three jobs, an error swallowed in a `catch`. No test fails for these. They still cost you later.
- **Things nobody wrote a test for yet.** A missing input check, an endpoint without authentication, a query that will be slow at ten thousand rows.
- **Writing the next test.** In my harness, once the contract’s tests pass, a separate prober writes extra browser tests against the running app: an empty time window, a negative capacity, a request with no user. It looks for what the contract missed, and its findings are real test failures, not opinions.

That is the healthy division of labour. The model widens the search. The deterministic check decides.

## Measure the reviewer before you trust it

An AI reviewer whose accuracy you haven’t measured is a second opinion of unknown quality.

So I measure mine. I graded a set of the evaluator’s real inputs by hand: the feature, the changed files, the check output, my verdict and one sentence on why. For example:

| Case | My grade | Why |
|---|---|---|
| Concurrency, attempt 1 | FAIL | Ten of twenty requests won. A transaction without a lock or constraint doesn’t prevent double booking. |
| Concurrency, attempt 2 | PASS | An exclusion constraint enforces the rule in the database, and the API maps the violation to 409. |
| Availability, attempt 1 | FAIL | `/rooms/:id` is registered before `/rooms/available`, so the search never runs. |

Those grades do two jobs. They go into the evaluator’s prompt as examples of how to grade. And a calibration run asks the evaluator to grade each case without seeing my answer for that case, then reports how often it agreed with me.

One number in that report matters more than the rest: **false approvals**, work I failed that the model passed. A false rejection costs a retry. A false approval costs a production incident. The calibration run fails if there is even one.

## Why AI reviewers lean towards “yes”

None of this is unique to my harness. Research on using language models as judges keeps finding the same tendencies:

- **Leniency.** A model reviewing a confident, well-formatted answer tends to find reasons to approve it, even after listing real problems.
- **Self-preference.** A judge tends to favour output that looks like its own. Generator and reviewer on the same model share blind spots, not just style.
- **Position and length bias.** Order and verbosity move scores in ways that have nothing to do with correctness.

You can reduce these with prompts (“be sceptical”, “don’t trust the author’s claims”) and with examples. You can’t prompt them away entirely. Which is why the model’s judgement only ever adds failures.

## Where this stops working

- **My calibration set is tiny.** A handful of human-graded cases proves the mechanism, not the reviewer. A real team needs hundreds, refreshed as the code base and the models change.
- **Deterministic doesn’t mean correct.** A test that encodes the wrong rule fails reliably and wrongly. The one-way rule trusts the tests. Part 2’s warning still applies: specifications need review too.
- **Flaky tests break the rule.** If a team learns that red sometimes means nothing, it will start overriding red. Then the reviewer’s 9/10 becomes the tie-breaker again. Fix flaky tests first.
- **Some quality has no test.** Readability, design fit, whether this is the right feature at all. For these, the reviewer’s opinion and a person’s judgement are all you have.

That last point is the bridge to the next part. If neither the test nor the model can decide some things, a person has to. But a person clicking “Approve” on fifty green pull requests is not a control either.

**Next: Part 6, Human Approval Is a Control, Not a Button.**

Has an AI reviewer ever approved something your tests or your users later proved wrong? [Tell me on LinkedIn](https://linkedin.com/in/anandkn2012).

## References and further reading

- **The run log:** [examples/double-booking](https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc/examples/double-booking): the evaluator’s 9/10 and the failing test, side by side.
- **LLM-as-a-judge and its biases:** Lianmin Zheng et al., [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685), NeurIPS 2023.
- **Separate builder and judge:** Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps), on separating the generator from a sceptical evaluator.
- **Flaky tests:** Martin Fowler, [Eradicating Non-Determinism in Tests](https://martinfowler.com/articles/nonDeterminism.html).
