# One Place Decides

![Who decides what. The scorer produces a number from 0 to 100 and a list of fired rules. The OPA policy is the only place that turns them into ALLOW, STEP_UP or BLOCK, using the score and the raw signals. If OPA cannot be reached, a Python fallback mirrors the policy's blocking conditions, and a unit test fails if the two drift apart. The language model runs only after the decision, only for STEP_UP and BLOCK, and only writes the explanation.](../../images/03-one-place-decides-1.png)

*The scorer produces a number. A policy decides what happens. A language model only explains.*

[Part 2](02-rules-decide-models-advise.md) ended with a number. A score of 64 is not a decision. Someone has to say
what 64 means: let the user in, ask for stronger proof, or stop them.

In IAM AI, exactly one thing says that: an Open Policy Agent (OPA) policy, written in Rego. No application code
hard-codes ALLOW, STEP_UP or BLOCK anywhere else. This part is about why, what happens when that one place is
unavailable, and why the language model in the system is kept well away from the decision.

## Why the decision lives outside the code

The scorer is Python, written and changed by engineers. The policy is a single
[Rego file](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/infra/terraform/policies/iam_risk.rego)
of about 160 lines, deployed with the infrastructure.

Separating the two gives three things the scorer cannot:

- **One file to read.** A security owner or an auditor who wants to know when a user is blocked reads the policy,
  not four services.
- **Its own change control.** A change to who gets blocked is a change to one file, reviewed as a policy change.
  The project’s rules route any edit to it through a dedicated policy review.
- **Context beyond the score.** The policy receives the score *and* the raw signals, so it can block on a
  combination that the score alone would let through.

## What the policy says

The policy blocks in six situations:

1. The score is above 70.
2. Impossible travel, with the two sign-ins less than 30 minutes apart.
3. An illicit consent grant.
4. A refresh token replayed more than twice.
5. A privileged user, outside business hours, with a score above 50.
6. A privileged user with no second factor at all.

It asks for step-up in five more, whenever the user is not already blocked: a score from 30 to 70; a new device
with a score of 20 or more; a new location with a score of 20 or more; a privileged user with SMS or no second
factor; and a user with a blast radius above 70 and a score of 15 or more. Below 30, with nothing else matched, it
allows.

That is what the file says. For two of those five, it is not what the file did, until November. The section
“What running the policy found” below explains why.

Look again at the second example from Part 2: an administrator from a new network and a new country, outside
business hours, with SMS. On the score alone that sign-in is STEP_UP until the anomaly models push it past 70. The
policy blocks it as soon as the score passes 50, because a privileged account outside business hours deserves a
lower bar. That threshold is a policy choice, visible in one line, not a weight buried in the scorer.

The same file also states its default: if no rule matches, allow. Its comment says why: “prefer availability over
lockout during tuning”. That is a defensible choice while the rules are being tuned, and a risky one to forget about
afterwards. It belongs on the list of things to revisit before production, and it is on mine.

## When the one place is down

A single policy point is also a single point of failure. If the API cannot reach OPA, it still has to answer.

The [OPA client](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/app/api/app/services/opa_client.py)
falls back to a decision of its own: block above 70, block on the policy’s unconditional conditions, step up from 30
to 70, allow below 30. Rego cannot be imported into Python, so those conditions are a hand-written copy of the
policy’s.

A hand-written copy drifts. Two code reviews found exactly that.

**July: the copy ignored the unconditional blocks.** The first fallback decided on the score alone. During an OPA
outage, an illicit consent grant or a privileged sign-in with no MFA, both blocked by the policy whatever the score,
could have been allowed. The fix added a mirror of the policy’s blocking conditions.

**August: the mirror was incomplete, and one check misread zero.** It had four of the five unconditional
conditions; the privileged, after-hours, score-above-50 rule was missing. And the impossible-travel check filled in
a missing travel time with `value or 999`. In Python, zero is false, so a gap of zero minutes, the strongest
possible signal of a stolen session, became 999 minutes and passed the under-30 check. Both were fixed.

Then the project stopped relying on care. A
[threshold-sync test](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/test/unit/api/test_rego_threshold_sync.py)
reads the Rego file and checks its thresholds and its five blocking conditions against the Python constants and the
fallback. Edit one side alone and a unit test fails.

The fallback still differs from the policy in one way, and that should be written down. It mirrors the blocks but
not the step-ups: during an OPA outage, a sign-in from a new device with a score from 20 to 29, or a privileged user
with SMS and a score under 30, is allowed rather than asked for stronger proof. That keeps the fallback small, and it means an outage lowers the
bar for exactly the cases the policy marks as worth a second look.

## The language model only explains

For STEP_UP and BLOCK, the API asks a language model, GPT-4o-mini on Azure OpenAI, for a short explanation for the
analyst. Its role is fenced in four ways:

- **It runs after the decision.** The order in the
  [scoring endpoint](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/app/api/app/routers/scoring.py)
  is score, then policy, then explanation. Nothing the model writes can change the outcome.
- **Its prompt forbids judgement.** It is told to name the signals that contributed, quote their values, and “not
  recommend blocking or allowing — that decision is made by the policy engine”, and not to mention signals that are
  not in the data.
- **It is kept steady.** Temperature 0.1 and at most 200 tokens.
- **It is optional.** If the call fails, a
  [fixed template](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/app/api/app/services/explainer.py)
  lists the score, the decision and the rules that fired. The analyst always gets an explanation; it is just less
  fluent.

## What running the policy found

Everything above comes from reading the Rego file. In November, checking this post, I loaded the file into the
same OPA server the local stack runs and sent it inputs.

**Two of the step-ups had never worked.** For a privileged user with SMS and a score of 10, OPA did not answer
STEP_UP. It answered with an error: the decision “produced conflicting values”.

Rego evaluates every rule, so the policy guards each one. The ALLOW rule only fires if a helper called
`_needs_step_up` is false, and the STEP_UP rules only fire if `_is_blocked` is false. Each helper is a hand-written
copy of the rules it guards, and the copies had drifted. `_needs_step_up` had no entry for weak MFA on a privileged
account, or for a new location. So for those inputs both STEP_UP and ALLOW matched, and OPA refused to pick.

The API treats an OPA error like an outage, so the Python fallback decided. The fallback steps up only on the score.
The result: privileged users with SMS, and sign-ins from new places, were allowed whenever their score was below 30.
That is exactly the case those two rules exist for.

A third gap had the opposite luck. `_is_blocked` had no entry for the privileged, after-hours, score-above-50 rule,
so that case errored too. But the fallback had been fixed in August to include that very rule, so the sign-in was
blocked anyway, through the error path.

The fix is three short helper entries. What matters more is the two tests that came with it:

- A [unit test](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/test/unit/api/test_rego_threshold_sync.py)
  compares every BLOCK and STEP_UP rule with its helper entry, condition for condition, and fails if any rule has no
  mirror. An older test in the same file had counted five helper entries and passed. It passed by coincidence: the
  file had five entries, but not the right five.
- An [end-to-end test](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/test/integration/test_policy.py)
  sends 6,144 combinations of signals and scores to the running OPA and fails on any error. Against the old policy it
  failed; against the fix it passes.

**And the reason is always wrong.** Every response, BLOCK included, carried the reason “No policy rule matched;
defaulting to ALLOW.” Each rule sets its reason as a local variable that never reaches the output, so only the
default ever comes back. Nobody noticed, because of the next section.

## Two things I would change

Reading the endpoint for this post showed two things worth fixing.

**The policy’s own reason is thrown away, and it is wrong anyway.** The OPA client returns a decision and a reason,
and the endpoint keeps only the decision. So the explanation an analyst reads is the language model’s summary, never
the policy’s own statement of which rule decided. For an auditor, the second is the one that matters. The policy
should return the rule that decided, and the API should store it with the decision.

**The explanation sits inside the request.** The API waits for the model before it responds, for every STEP_UP and
BLOCK. A slow model makes every block slow. The decision does not depend on the explanation, so the explanation can
be written afterwards and attached to the alert.

## What “one place” really means

A single policy point is not one file. It is one file, a fallback that copies it, tests that keep the copies
honest, inside the file as well as outside it, and a clear rule that nothing else decides. The file was there from
the first commit. The rest took two code reviews, two months, and finally sending the policy real inputs.

---

**The evidence:** the
[policy](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/infra/terraform/policies/iam_risk.rego),
the [OPA client and fallback](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/app/api/app/services/opa_client.py),
the [threshold-sync test](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/test/unit/api/test_rego_threshold_sync.py),
the [explainer](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/app/api/app/services/explainer.py)
and the [changelog](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/CHANGELOG.md)
entries for both fallback fixes.
