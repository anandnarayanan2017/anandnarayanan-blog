# Rules Decide, Models Advise

![How a risk score is built. Fifteen signals feed two paths. Eleven deterministic rules add up to a rule total, capped at 100, which counts for 55% of the score. Three anomaly models, Isolation Forest at 40%, LOF at 35% and HBOS at 25%, give an anomaly score from 0 to 100, which counts for 45%. A hard floor forces the score to at least 71, which is BLOCK, whenever a single rule contributes 60 or more. With no rule fired, the score can never exceed 45, so the models can never block on their own.](../../images/02-rules-decide-models-advise-1.png)

*A rule can block a sign-in. A model can only raise its hand.*

In [Part 1](01-who-signed-in.md) the scorer was one box: an event goes in, a number from 0 to 100 comes out. This
part opens the box.

Two ideas compete for that box. One says: learn what normal looks like for each user, and flag what is unusual.
The other says: write down what must never happen, and flag it every time. The first catches what nobody thought
of. The second can be explained to an auditor, line by line.

IAM AI uses both, but not as equals. The rules decide. The models advise.

## Fifteen signals

Everything starts with a feature vector: fifteen facts about one sign-in, computed in one module and nowhere else.

| Group | Signals |
|---|---|
| Authentication | new network (ASN), new country, hour of sign-in, outside business hours, MFA method, failure rate in the past hour |
| Behaviour | days since this application was last used, new device, device compliance |
| Privilege | holds a privileged role, how often admin tools were used in the past week |
| Session | events in the past 15 minutes, refresh-token replays |
| Location | impossible travel, minutes between the two sign-ins |
| Relationships | blast radius, illicit consent grant |

“New” means new against a 30-day baseline of that user’s own sign-ins, kept in Redis: the networks, countries,
devices and applications they have used. A user with fewer than five sign-ins in the baseline has no meaningful
history yet, so the scorer falls back to global defaults instead of treating everything as new.

The last two signals come from a privilege graph in Neo4j. **Blast radius** measures how few steps separate the user
from a privileged resource: one step scores 100, six or more score 0. **Illicit consent grant** is true when the
user has granted an OAuth consent to an application flagged as high risk.

## Eleven rules

Each rule looks at the signals and either stays silent or adds a contribution to the rule total.

| Rule | Fires when | Adds |
|---|---|---|
| Illicit consent grant | consent to a high-risk application | 75 |
| No MFA on a privileged role | privileged and no second factor | 65 |
| Impossible travel | two distant sign-ins too close in time | 30 to 80, more for a shorter gap |
| Refresh-token replay | the same token reused | 20 per replay, up to 70 |
| High failure rate | 30% or more failed sign-ins in an hour | up to 40 |
| High API velocity | 30 or more events in 15 minutes | up to 35 |
| Privileged, outside business hours | admin sign-in outside 08:00–18:00 | 30 |
| SMS MFA on a privileged role | privileged and SMS as the second factor | 25 |
| New network and new country | both new against the baseline | 20 |
| Non-compliant device, privileged | admin on a device that fails compliance | 20 |
| High blast radius | blast radius of 60 or more | up to 15 |

Every rule carries a sentence that says why it fired, such as “Refresh token replayed 3 times”. That sentence is
what the analyst sees first, before any model output.

## How the score is built

The [aggregator](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/app/risk_scorer/scorer/aggregator.py)
combines the two halves in one line:

> score = rule total × 0.55 + anomaly score × 0.45

The rule total is capped at 100. The anomaly score is already on a 0 to 100 scale. Above 70 is BLOCK, 30 to 70 is
STEP_UP, below 30 is ALLOW.

Then one more line, which matters more than the weights:

> If any single rule contributes 60 or more, the score is at least 71.

That is the **hard floor**. Four rules can reach it: an illicit consent grant, no MFA on a privileged role,
impossible travel with a gap of an hour or less, and three or more token replays. When one of them fires, the
sign-in is blocked whatever the models say. A quiet model cannot talk a hard rule down.

The floor also works the other way. With no rule fired, the score is the anomaly score times 0.45, so it can never
go above 45. **The models can never block on their own.** At most they can push a sign-in into STEP_UP, which asks
the user for stronger proof. Nobody is locked out because a model found them unusual.

Two examples:

- **A privileged user signs in with no second factor.** One rule, 65. The floor applies: the score is at least
  71, so BLOCK. Nothing the models say can change that.
- **An administrator signs in from a new network in a new country, outside business hours, with SMS.** Three
  rules: 20 + 30 + 25 = 75. Times 0.55 is 41.25, already STEP_UP. To reach BLOCK on the score alone the anomaly
  score would need to be above 64. (Part 3 shows why the policy blocks this one much
  earlier.)

This is the same choice Agent Sentinel made in its
[first decision record](https://github.com/anandnarayanan2017/anandnarayanan-blog/blob/main/agent-sentinel/docs/adr/0001-rules-first-detection.md):
deterministic policy first, statistics second, because an alert has to be defensible to someone who was not in
the room when it fired.

## Three models, and why three

The anomaly half is an ensemble of three models from the PyOD library, each looking at the same feature vector in
a different way:

- **Isolation Forest** (40%) isolates a point with random splits; outliers isolate quickly.
- **LOF** (35%) compares a point’s local density with its neighbours’.
- **HBOS** (25%) scores each feature against a histogram, which is fast and easy to reason about.

No single anomaly model is right about every kind of unusual, so the ensemble averages their opinions. The
project’s rules fix the weights: they cannot change without a matching change to the retraining job and a written
decision record.

## The loop that teaches the models

Analysts review STEP_UP and BLOCK alerts and record a verdict: true positive, false positive or benign. Those
verdicts are the labels. An Airflow job checks every Sunday at 03:00 and retrains once at least 50 new verdicts
exist. It holds back 20% of the labelled data for evaluation, and a new model is promoted to production only if
its recall on that held-out data is at least 0.5.

Two honest consequences follow.

**Before 50 verdicts, there is no trained model.** A fresh deployment scores with a placeholder fitted on random
noise. Its output is arbitrary, so the anomaly half adds noise until analysts have done enough work to replace it.
The hard floor and the 45-point cap keep that noise away from BLOCK, but STEP_UP rates will be noisier at first.

**The promotion gate checks recall only.** Precision is measured and logged, but nothing acts on it. A model that
catches more true positives but raises many more false alarms would still pass. A gate on precision, or on the STEP_UP rate it would cause, is on my list.

## The sign that was upside down

The most consequential bug in the scorer was one character long.

The models return raw anomaly scores, and the scorer squashes each into 0 to 100 with a sigmoid. The original code
assumed the convention of scikit-learn’s Isolation Forest, where lower means more anomalous. PyOD uses the
opposite convention: in its own words, “outliers are assigned with larger anomaly scores”. So the most unusual
sign-ins got the *lowest* anomaly scores. For 45% of every score, the scale was upside down.

Nothing failed. The hard floor still blocked the obvious attacks, which is exactly why the bug could hide. It was
found in July by reading the code against the library’s documentation, fixed by flipping one sign, and pinned with
[a test that higher raw scores give higher normalised scores](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/test/unit/risk_scorer/test_anomaly.py),
so the direction can never silently flip back.

The fix then broke an end-to-end test that had been passing only because of the bug.
Part 4 tells that story.

## What this design buys, and what it costs

It buys a system whose blocks can always be traced to a rule with a sentence attached, and whose models can make it
smarter without ever making it arbitrary.

It costs coverage. A truly new attack pattern that no rule describes can reach STEP_UP through the models, but never
BLOCK. For identity decisions in a regulated environment I think that is the right trade: a new pattern should get a
person’s attention and a new rule, not an automatic lockout from a model nobody can question.

---

**The evidence:** the
[rules](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/app/risk_scorer/scorer/rules.py),
the [signals](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/common/models/scoring.py),
the [aggregator](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/app/risk_scorer/scorer/aggregator.py),
the [retraining rules](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/airflow/dags/retrain_logic.py)
and the [tech-debt log](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/docs/TECH_DEBT.md)
entry for the inverted sign.
