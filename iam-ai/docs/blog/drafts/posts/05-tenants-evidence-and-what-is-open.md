# Tenants, Evidence and What Is Still Open

![Where tenant identity has to reach. The tenant comes from the caller's API key, never from the request body. From there it has to be part of every Postgres row, every Redis baseline key, every Neo4j query and the nightly baseline job. Each was missed once: a new NOT NULL column would have made the ingestion worker fail every write, Redis baselines and Neo4j queries were keyed by user alone, and the nightly job kept the old key format after the scorer was fixed.](../../images/05-tenants-evidence-and-what-is-open-1.png)

*Every piece of data has an owner. The system has to know it at every hop, not just at the front door.*

The first four parts treated IAM AI as if it served one organisation. It was built that way: one Entra tenant per
deployment, an API with no authentication at all in the first commit, then a single shared key, and data that
belonged to whoever could call it.

That is fine for a prototype and wrong for anything an organisation would run on behalf of more than one team or
customer. This last part covers adding tenants to a system built without them, the leak that survived its own fix,
what is still open, and where this project meets Agent Sentinel.

## Who is calling, really

In late July the shared key, itself only a few days old, was replaced with a real caller identity. The
[authentication service](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/app/api/app/services/auth.py)
now resolves each API key to three things: a tenant, a user and a role.

- **Keys are stored as hashes.** The plaintext key is shown once and never kept.
- **Four roles, checked per endpoint.** Viewer, analyst, admin and owner. A viewer cannot submit a verdict; an
  analyst cannot change tenant settings. Each endpoint declares the lowest role it accepts.
- **The tenant comes from the key, never from the request.** A tenant field in a JSON body can be set to anything
  by anyone holding any valid key. The caller’s resolved identity cannot. So the scoring endpoint ignores any tenant
  in the body and stores the event under the caller’s own. I checked: a sign-in sent with the other tenant’s id was
  stored under the caller’s.
- **Identity comes from the key, too.** The verdict form used to accept an `analyst_id` typed by the client, so
  anyone could record a verdict in someone else’s name. It is now taken from the authenticated user, and every
  change to an alert, verdict or setting is written to an audit log with that user as the actor.
- **Ownership is checked, not assumed.** Before accepting a verdict, the API checks that the alert belongs to the
  caller’s tenant. Without it, a guessed alert ID could label another tenant’s data. An integration test against the
  running stack proves one tenant cannot see another’s alerts.

There is one deliberate trade-off. Looking a key up in Postgres on every request was expensive, so the result is
cached for 30 seconds. A revoked key keeps working for up to 30 seconds afterwards. That number should be a
conscious choice, and it is written next to the code.

## The column that dropped every event

Adding tenants meant adding a `tenant_id` column, required, to every table. The schema changed. The ingestion
worker’s write path did not.

From that change on, every event the worker tried to write would fail on the new required column. The failure fell
into a broad `except`, which retried row by row, failed again, and logged. The platform would have looked healthy
and ingested nothing.

The code review on 27 July found it. It is the same pattern as the lost alerts in
[Part 4](04-the-build-was-green.md): a broad `except` turned a total failure into a log line. Twice in one month is
not a coincidence. It is a habit, and the design rule from Part 4, to decide out loud what happens when a write
fails, came from both.

## The leak that survived its fix

Tenant identity has to reach every place data is stored, not only the tables. The August review found two places
it had not reached.

**Redis baselines were keyed by user alone.** Each user’s 30-day history of networks, countries and devices lived
under a key built from the user ID. Two tenants with the same user ID would share a baseline, and one tenant’s
sign-in habits would shape another tenant’s risk scores.

**Neo4j queries matched on user alone.** The blast-radius and consent-grant queries, two of the strongest signals in
[Part 2](02-rules-decide-models-advise.md), could run against the wrong tenant’s privilege graph.

Both were fixed on 20 August: every key and every query now includes the tenant.

Twelve days later, while adding tests for the Airflow jobs, the same leak turned up a third time. The nightly job
that rebuilds baselines wrote them with its own copy of the key format, and its copy still used the old, user-only
shape. Every night it would have rebuilt the baselines the scorer had just stopped sharing.

This is the duplicated-fact problem again. The key format lived in two places, the fix reached one, and nothing
failed when they disagreed. Both now build keys the same way, and the scorer’s documentation names the job as the
second place to change. A
[test](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/test/unit/airflow/test_baseline_logic.py)
now pins the job’s key format, but to a fixed string, not to the scorer’s own key function. If the scorer’s format
changed again, that test would still pass. A test that compares the two directly would close it for good.

The same review found one more silent loss. The worker writes events in batches with Postgres `COPY`, which is
all-or-nothing. One duplicate row failed the whole batch, the handler called that an idempotent duplicate, and the
other rows were never written while the worker reported success. It now falls back to writing row by row.

## What is still open

A series about knowing whether something works should end with what is not known yet. From the four earlier parts
and the project’s own records:

| Open item | Why it matters | Part |
|---|---|---|
| The end-to-end replay is not in CI | Starting the whole system is still a manual check | [4](04-the-build-was-green.md) |
| A decision stands even if its record cannot be written | Availability is favoured over evidence | [4](04-the-build-was-green.md) |
| The policy defaults to ALLOW when nothing matches | Safe while tuning, risky if forgotten | [3](03-one-place-decides.md) |
| The fallback mirrors the policy’s blocks but not its step-ups | An OPA outage lowers the bar | [3](03-one-place-decides.md) |
| The policy’s reason is always the default, and the API drops it anyway | The auditor sees the model’s summary, not the rule | [3](03-one-place-decides.md) |
| No trained model until 50 verdicts | Noisier STEP_UP rates on a fresh deployment | [2](02-rules-decide-models-advise.md) |
| Model promotion checks recall only | A noisier model can still be promoted | [2](02-rules-decide-models-advise.md) |
| The nightly job’s key test does not compare against the scorer | The tenant leak could come back | |
| The explainer and parts of the poller have no unit tests | Gaps on compliance-relevant code | |
| Tenants and users are created with SQL | No provisioning flow or admin API yet | |
| One Entra tenant per ingestion deployment | Serving several customers from one worker needs real design work | |
| Retraining learns only from sign-ins that raised an alert | The anomaly models never see ordinary traffic | [2](02-rules-decide-models-advise.md) |

For the record, the question I would ask first is the second row. For identity decisions in a regulated
environment, I think a decision that cannot be recorded should at least be flagged, and probably not enforced
silently. I have not built that yet.

## Where Agent Sentinel joins in

IAM AI and Agent Sentinel are separate projects with no shared code. They share a shape: typed events in, an
explained decision out, deterministic rules first, models second, one place for policy.

They also cover two halves of one question. IAM AI asks *who* signed in. Agent Sentinel asks *what* that person’s AI
agents then did. An agent usually acts with a person’s access, so the obvious join is this: feed IAM AI’s trust
score for the person behind an agent into Agent Sentinel’s policy. An agent acting for someone who has just been
stepped up, or whose sign-in looks risky, would be held to a stricter policy until that trust is restored.

The project keeps a
[vision note](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/docs/unified-trust-plane-vision.md)
for that. It is forward-looking, not a roadmap, and it is honest about the friction. One is event-driven, the other
intercepts calls inline. Making OPA the one policy point for both means rewriting Agent Sentinel’s rules as Rego.
And IAM AI blocks today, while Agent Sentinel only observes, so the two cannot yet enforce on equal terms.

## So, can we trust who signed in?

Not on its say-so. But for a given sign-in, IAM AI can now show which rules fired and why, what the models added and
how little that can be, which decision the policy made, who reviewed the alert, and the tests that would fail if any
of that logic changed. It cannot yet show which policy line decided; that is the second row above.

That is the difference between June and now. The first commit could produce a decision. It took ten weeks of
running it, reviewing it and testing it before it could show its working, and one more run in November to find
that two of its step-ups and its whole learning loop had never worked. The run is the evidence. Everything else is
a claim.

---

**The evidence:** the
[authentication service](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/app/api/app/services/auth.py),
the [schema](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/db/schema.sql),
the [integration tests](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/test/integration/test_replay.py),
the [changelog](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/CHANGELOG.md),
the [tech-debt log](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/docs/TECH_DEBT.md)
and the [vision note](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/docs/unified-trust-plane-vision.md).
