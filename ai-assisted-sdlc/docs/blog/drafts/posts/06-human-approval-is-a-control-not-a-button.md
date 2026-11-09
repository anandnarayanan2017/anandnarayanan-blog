# Human Approval Is a Control, Not a Button

![Human approval is a control, not a button: an “Approve all (50)” button with fifty green ticks changes nothing. A control means the person could realistically say no, has the evidence attached, and the decision is recorded: who, when, which version. The default answer is no. A person is needed when a change can’t be undone, touches tests, policies, permissions or the pipeline, or a check was skipped or overridden.](../../images/06-human-approval-is-a-control-not-a-button-1.png)

*An approval only means something if the person could have said no, and knew why they might.*

In Part 1, I asked how we know the code works. Parts 2 to 5 answered with specifications, a harness, enforced permissions and deterministic checks.

This part is about the question that comes straight after it:

**Who decided it could go to production?**

For most of my career, the answer was a person. Sometimes a tired person at 6 p.m. on a Friday, but a person. A developer wrote the change, another reviewed it, a pipeline ran the tests, someone with the right permissions pressed merge. If an auditor asked, we could point at names.

Now picture a pull request from this autumn. An agent opened it. An AI scanner flagged a finding. An autofix agent patched it and re-ran the scanner to prove the fix. The pipeline went green.

Everyone on that pull request was very productive. Nobody on it was a person.

## A button is not a control

The obvious answer is “a human approves before merge”. Most teams already have that. It is a button.

A button becomes a control only when three things are true:

1. **The person could realistically say no.** Not after the release train left, not on the forty-third pull request of the day.
2. **The person has the evidence to decide.** Not just a diff and a green tick.
3. **The decision is recorded.** Who, when, which version, and on what evidence.

Remove any one and the approval is a ritual. It feels like oversight. It produces a name in a log. It doesn’t change what ships.

Lisanne Bainbridge called this one of the *ironies of automation*, back in 1983: the more reliable the automation, the less practice the human gets at catching its failures, and the more we rely on that human exactly when the automation fails. An approver who has clicked “Approve” on two hundred green changes is not well placed to catch the two-hundred-and-first.

## Which changes need a person?

If every change needs a person, people stop reading. If none do, nobody is accountable. So the real design question is which changes go through automatically and which stop.

Size is the wrong test. A one-line change to a database constraint can be riskier than a thousand lines of new screens. I decide on three questions instead:

| Question | Proceeds automatically when… | Needs a person when… |
|---|---|---|
| **Can it be undone?** | A revert fully restores the previous state | It migrates data, deletes, sends, pays or publishes |
| **What does it touch?** | Application code inside known boundaries | Tests, policies, permissions, the pipeline, secrets, infrastructure |
| **Did every deterministic check pass?** | Yes, and the AI reviewer raised nothing | A check was skipped, changed, or overridden |

The middle row matters most with agents. A change that edits the tests, the policy or the pipeline is a change to *what passing means*. Part 4 made those files unwritable for the agent inside the harness. Outside it, in a normal repository, they need a named person every time.

## Making the review mean something

In my harness, a person approves once per release, not once per change. That sounds like less oversight. In practice it is more, because the person reviews one decision with the evidence attached instead of fifty green ticks.

The evidence is what the harness already produced on the way:

- **The specification:** the contract for each feature, and the tests that define “done”.
- **The checks:** which tests ran and passed, which architecture rules held, which live probes ran against the running app.
- **The disagreements:** every time the AI reviewer and a deterministic check disagreed, and which one won. The 9/10 on double-booking code belongs in front of the approver, not buried in a log.
- **The attempts:** each attempt is a commit, so the approver can see what failed and how it was fixed.
- **The exceptions:** anything that touched tests, policies or the pipeline, listed separately.

An approver who reads that for ten minutes knows more than one who has skimmed fifty diffs.

## The default answer is no

The harness’s human gate fails closed. A run ends at *awaiting approval*. Nothing is released unless a person explicitly approves. A feature that runs out of retries blocks the run and asks for a person, rather than letting the next feature build on a broken base.

The difference between “release unless someone objects” and “hold unless someone approves” sounds small. It is the whole difference between a button and a control.

## Regulators already wrote the requirement

If you work in EU financial services, this has a name: **DORA**, the Digital Operational Resilience Act. (Not the DevOps metrics. Same acronym, different meeting.)

DORA expects ICT changes to be recorded, tested, assessed, approved, implemented and verified in a controlled way. The technical standards behind it ask for the function that approves a change to be separate from the function that requests it.

None of that says “by a human”. All of it assumes someone can explain, afterwards, why the change was safe. When the author, the reviewer and the fixer are the same model, the separation exists on the organisation chart and nowhere else. “The agent was confident” is not an explanation an auditor will accept.

## Where this stops working

- **My gate is a command-line flag.** It proves the shape: fail closed, approve once with evidence. It doesn’t yet record who approved, when and which commit. A real gate needs that record, and an identity behind it that an agent can’t borrow.
- **Risk tiers drift.** Whatever rules decide “automatic” versus “needs a person” will be gamed, usually innocently, by splitting a risky change into harmless-looking pieces. Review the tiers themselves, regularly.
- **People still get tired.** Better evidence reduces fatigue. It doesn’t remove it. If approvals pile up, the answer is fewer, better-prepared decisions, not faster clicking.

Five questions worth an hour if your teams are turning on AI review and autofix:

1. Can the same model write, review and fix the same change?
2. Can an agent edit the tests, the policy or the pipeline that judges its own work?
3. Has anyone measured your AI reviewer against human reviewers?
4. Does a failing deterministic check ever get overruled by an AI “looks fine”?
5. If an auditor picks one agent-authored change, can you show who approved it, and on what evidence?

Specifications, harness, permissions, checks and approval: each part of this series has been one control. The last part puts them into one delivery flow.

**Next: Part 7, From Coding Agent to Engineering Factory.**

In your team, what does a person actually look at before they approve an agent’s change? [Tell me on LinkedIn](https://linkedin.com/in/anandkn2012).

## References and further reading

- **DORA:** Regulation (EU) 2022/2554 on digital operational resilience for the financial sector, [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2022/2554/oj).
- **ICT change management:** Commission Delegated Regulation (EU) 2024/1774, Article 17, [EUR-Lex](https://eur-lex.europa.eu/eli/reg_del/2024/1774/oj).
- **Ironies of automation:** Lisanne Bainbridge, “Ironies of Automation”, *Automatica* 19(6), 1983.
- **Pipeline integrity:** GitHub Changelog, [GitHub Actions workflow lockfiles are generally available](https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/) (2026-10-28).
- **Humans steer, agents execute:** OpenAI, [Harness engineering](https://openai.com/index/harness-engineering/).
