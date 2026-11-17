# Who Signed In, and Do We Still Trust Them?

![IAM AI in one picture. Microsoft Entra ID sign-in and audit events, and risky users from the Graph API, flow through Event Hub to an ingestion worker that turns them into typed events. A scorer computes 15 signals from a 30-day baseline in Redis and a privilege graph in Neo4j, runs 11 rules and three anomaly models, and returns a score from 0 to 100. An OPA policy turns the score into ALLOW, STEP_UP or BLOCK. A language model explains STEP_UP and BLOCK for the analyst, and analyst verdicts feed a weekly retraining job.](../../images/01-who-signed-in-1.png)

*A sign-in is checked once. Trust should be checked every time something changes.*

[Agent Sentinel](/blog/agent-sentinel-01-why-agents-need-a-flight-recorder/) asks whether we can trust what an
AI agent did. But before any agent acts, a person signs in, and the agent usually acts with that person’s access.
So there is an earlier question:

Can we trust who signed in?

IAM AI is my attempt at an answer for Microsoft Entra ID. It is a personal project that I built in my spare time
between June and September 2026. This series walks through how it is designed, what I got wrong, and what
checking it actually found.

## Trust checked once, at the door

Most sign-in decisions are made once. The password is right, the second factor passes, the device is compliant,
and the user is in. From then on the session is trusted until it expires.

Attackers know this. A stolen refresh token replays a session without ever touching the password. A consent grant
to a malicious application keeps working after the password is reset. And some risks are only visible in
combination: an administrator signing in from a new country, at 03:00, with SMS as the only second factor. Each
fact alone is ordinary. Together they are worth a second look.

Entra has its own risk detections, and IAM AI reads them. What I wanted on top was a decision whose rules belong to
the organisation: written down, versioned, tested, and explained in terms that an analyst and an auditor can both
check.

## What it does, in one pass

The platform is a set of small services on Azure. An event goes through six steps:

1. **Collect.** Entra sign-in and audit logs stream into Azure Event Hub. A poller asks the Graph API every five
   minutes for risky users and risk events, and publishes them to the same hub.
2. **Normalise.** An ingestion worker turns raw Entra JSON into one of three typed event models and writes them to
   Postgres. Raw JSON never crosses a service boundary.
3. **Score.** A scorer computes 15 signals from the event, a 30-day baseline of each user’s habits in Redis, and a
   privilege graph in Neo4j. Eleven rules and an ensemble of three anomaly models turn them into a score from 0 to
   100.
4. **Decide.** An Open Policy Agent (OPA) policy turns the score and the signals into one of three decisions:
   ALLOW, STEP_UP (ask for stronger proof) or BLOCK.
5. **Explain.** For STEP_UP and BLOCK, a language model writes a two-to-four-sentence explanation for the analyst
   who reviews the alert.
6. **Learn.** Analysts mark each alert as a true positive, a false positive or benign. Once 50 new verdicts exist,
   an Airflow job retrains the anomaly models, and MLflow keeps their versions.

Around it sits the infrastructure, all in Terraform for three environments: Container Apps, Postgres, Redis, Neo4j,
Key Vault in role-based access mode, private endpoints in staging and production, managed identities instead of
registry passwords, Microsoft Sentinel with two alert rules, and Grafana. The project’s own estimate, at 2025
prices, is about $200 a month for development and $845 for production, with the graph database the largest single
cost in development. That estimate was written when the platform had three container apps; it now has eight, so
read it as a lower bound.

## Four rules the design rests on

Everything in the series comes back to four decisions.

**1. Typed events at every boundary.** Each service receives and returns validated models, never loose
dictionaries. A field that is missing or misspelled fails at the boundary, not three services later.

**2. Rules decide, models advise.** The deterministic rules can block on their own. The anomaly models cannot:
their share of the score is capped below the block threshold. Part 2 shows the
arithmetic.

**3. One place decides.** The scorer produces a number. The OPA policy has the final say on what happens, and no
application code hard-codes ALLOW or BLOCK anywhere else. Part 3 covers why, and what
happens when OPA is down.

**4. The language model explains. It never decides.** Its prompt tells it not to recommend blocking or allowing,
and it only runs after the decision is made.

These are the same instincts behind Agent Sentinel, where policy comes first and statistics second. IAM AI looks at
the person; Agent Sentinel looks at what that person’s agents do. Part 5
comes back to how the two could meet.

## Finished on day one, proven ten weeks later

The first commit, on 22 June 2026, added 134 files and about 8,300 lines: every service, the models, the rules,
the anomaly ensemble, the OPA policy, eleven Terraform modules and the CI workflows.

It looked finished. It had no tests. The CI step that was meant to run them pointed at a folder that did not
exist.

The next ten weeks were spent finding out what the first commit actually did:

| Date | What happened | Part |
|---|---|---|
| 23 June | A security review of the Terraform and deployment scripts | |
| 26 July | The first time anyone started the whole stack | 4 |
| 27–28 July | Tenants, roles and an audit log; a multi-agent code review and its fixes | 5 |
| 20–21 August | Cross-tenant leaks, gaps in the OPA fallback, and a test that keeps the policy and the code in step | 3, 5 |
| 1 September | The last items in the tech-debt log closed | 5 |
| 17 November | Checking this series against the running system: three more defects that every test had passed | 2, 3, 4 |

By September there were 133 passing unit tests, an end-to-end replay against the running stack, and a written record
of every bug and how it was found. That record is the most useful thing the project produced, and this series is
built on it.

Writing the series added one more round. To check each claim, I ran the policy, the services and the retraining
query again, against the code as it stood. Three defects turned up that had passed every unit test and two code
reviews. Each is told in the part it belongs to, with its fix and the test that now guards it.

## The series

1. **Who signed in, and do we still trust them?** What the platform does and the rules it rests on. You are here.
2. **Rules decide, models advise.** Fifteen signals, eleven rules, three
   models, one hard floor, and an inverted sign.
3. **One place decides.** OPA as the single policy point, the fallback when it is down,
   and the model that only explains.
4. **The build was green. The system had never run.** What starting the whole stack
   found that no check had.
5. **Tenants, evidence and what is still open.** Adding tenants to a
   system built without them, the leak that survived its fix, and where Agent Sentinel joins in.

---

**The evidence:** the
[architecture diagrams](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/docs/architecture/c4-architecture.md),
the [infrastructure README with the cost estimates](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/README.md)
and the [changelog](https://github.com/anandnarayanan2017/iam-ai-tf/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/CHANGELOG.md).
Links point at the commit this series describes.
