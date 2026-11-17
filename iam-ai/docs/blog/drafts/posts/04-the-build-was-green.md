# The Build Was Green. The System Had Never Run.

![Three gates that sound like one question. Does it build? The Docker images built and the type checker was clean. Does it start? Every Python service failed on its first import, because the shared code was outside the build context. Does it work? Every BLOCK and STEP_UP decision lost its alert record to a swallowed foreign-key error, and the log line dropped the reason.](../../images/04-the-build-was-green-1.png)

*Every check passed. Each one answered a smaller question than it seemed to.*

Parts [2](02-rules-decide-models-advise.md) and [3](03-one-place-decides.md) described what IAM AI is designed to
do. This part is about the day I found out what it actually did.

By its own records the project looked healthy. The Docker images built. CI ran formatting, linting and a type
checker. Dependencies were pinned. Terraform had applied. Five weeks after the first commit, on 26 July, I ran
`docker compose up` for the whole stack, and the project’s tech-debt log gained this line:

> The single biggest lesson of this session is that nobody had ever actually run `docker compose up`
> successfully before, and several of these bugs would have blocked it immediately.

This part is about what that run found, why none of the green checks could have found it, and the design rules I
took from it.

## Three questions that sound like one

“Does it work?” is three questions, and every check answers only one of them.

| Check | What it proves | What it cannot see |
|---|---|---|
| `docker build` | The files copy and the dependencies install | Whether the code inside can import anything |
| Type checker | The types agree with the code it can see | Packages that are missing, if it is told to ignore them |
| Unit tests with fakes | Each function does what it says | Whether the services are wired to each other |
| Running the stack | The system does something end to end | Whether that something is correct |

The first three were green. The fourth had never been tried.

## Does it start? No service did

**The shared code was outside every image.** The four Python services share a package of models, configuration
and database helpers. In the first commit, each service’s image was built with its own folder as the Docker build
context, so the shared package was physically unreachable inside every image. `docker build` never noticed,
because building an image copies files and installs packages but never imports the code. The failure appeared
only when a container started: `ModuleNotFoundError`, in all four services, locally and in the CI image pipeline,
since the first commit.

**Dependencies went missing between two lists.** The ingestion worker lacked `httpx`, which a newer change used,
and `six`, an undeclared dependency of an Azure library it used. Two days later, after a folder rename, the risk
poller lacked `redis`. Each was in the root project file and missing from the service’s own requirements file,
which is what its image installs. Again: the build passed, the container died on start.

**The type checker approved an import that could not work.** One module used a relative import with the wrong
number of dots. The type checker resolved it more loosely than Python does at run time, so it passed. The first
thing that actually imported the module failed.

**The model registry could never start.** The MLflow container was configured to store its data in Postgres, but
its image had no Postgres driver, and the database it pointed at had never been created.

None of these are subtle. All of them sat behind green checks.

The design point is the one I missed: in a repository where several services share code, **the build context is
an architecture decision**. It decides which code a service can reach. I had treated it as a detail of each
Dockerfile. The fix makes the repository root the context for every service and mirrors the repository layout
inside each image.

The dependency drift got a structural fix rather than a careful one. Each service’s requirements file is now
[generated from its group in the root project file](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/scripts/sync-requirements.sh),
and a CI job fails if the two disagree. Two lists that must match will drift. A check that fails when they differ
does not.

## Does it work? The decision was made. The evidence was not kept.

Once every container started, synthetic sign-ins went through the API and the decisions came back as expected.
The alerts for them were not in the database.

The schema explained it. It chains three tables: an event, the risk score for that event, and an alert for that
score, each with a foreign key to the one before. The scoring endpoint wrote only the alert. Nothing ever wrote
the risk score, so every alert insert failed on its foreign key: every BLOCK and every STEP_UP, every time.

Nothing reported it. The insert sat inside a broad `except` that logged the error and carried on. And the logger
was hand-rolled with a format string that could not print the `extra` fields, which is where every error message
in the codebase was passed. So the log line said that something failed and dropped the reason. I found the bug by
querying the tables directly, not by reading the logs.

For a system meant to be audited, this is the worst kind of failure. The access decision was made and enforced.
The record of it, the thing an analyst reviews and an auditor asks for, was silently thrown away.

Two design changes came out of it:

- **The evidence trail is written in one transaction or not at all.** The endpoint now
  [writes the event, the score and the alert](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/app/api/app/routers/scoring.py)
  together, so a failure can no longer leave half a trail.
- **Catch, log and continue is a decision, not a habit.** It means the system keeps going without the thing that
  failed. The endpoint still does this when the trail cannot be written: the decision is returned and enforced,
  and the failure is logged. The difference is that it is now a stated choice, in a comment next to the code,
  that the decision matters more than completing its record. And the logs now go through
  [a JSON formatter that keeps the `extra` fields](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/common/logging_config.py),
  so the failure carries its reason.

Whether that choice is right is a question for Part 5.

## A test that passed because of a bug

Reading the code still found things running it did not. [Part 2](02-rules-decide-models-advise.md) told how a
review found the anomaly score’s sign inverted, so that the most unusual sign-ins scored lowest. The fix was one
character.

Then the end-to-end replay failed. A benign sign-in, with no rules fired, came back STEP_UP instead of ALLOW.

The fix was right. The test was wrong, and had been passing only because of the bug. Until analysts have recorded
50 verdicts, there is no trained model, and the scorer falls back to a placeholder fitted on random noise. Its
output for any real sign-in is arbitrary. The old inverted sign happened to push this one input low enough to
ALLOW.

What the design does guarantee is narrower. With no rule fired, the final score is the anomaly score times 0.45,
so it can never exceed 45 and can never reach BLOCK, which starts above 70.
[The test now asserts exactly that](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/test/integration/test_replay.py):
not BLOCK, and a score of at most 45.

It is the same lesson as
[A Prompt Is Not a Specification](/blog/ai-assisted-sdlc-02-a-prompt-is-not-a-specification/): assert the
invariant the design guarantees, not an outcome you happened to observe.

## Green can mean nothing was checked

Two more checks turned out to be vacuous.

From the first commit until the end of July, the CI step ran `pytest` against a test folder that did not exist.
The project’s own audit recorded that the gate was “either failing or vacuously green”.

Later, the type checker reported the Airflow jobs clean. Airflow was not installed anywhere in the project, and the
type checker was set to ignore missing imports, so it treated every Airflow name as “could be anything” and had
nothing to object to. When Airflow was finally installed in its own environment on 1 September, a
[smoke test that loads the jobs the way Airflow does](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/airflow/test/test_dags_import.py)
caught a real problem straight away. The jobs had just been split so their logic could be unit-tested, and the
split worked under `pytest`. Under Airflow it did not, because Airflow imports each job file by its path without
putting the file’s own folder on the import path.

A check that cannot fail is not a check. It is a decoration that happens to be green.

## Design rules I took from it

1. **Start the whole system before believing any green check.** A build proves the files are there. Only a run
   proves they work together.
2. **Treat the build context and dependency lists as architecture.** They decide what each service can reach and
   what it ships with.
3. **Give every duplicated fact a test that fails when the copies disagree.** Here that is the requirements files
   against the project file, and, from [Part 3](03-one-place-decides.md), the policy thresholds in Rego against the
   Python fallback.
4. **Write the evidence of a decision all at once, and decide out loud what happens when you can’t.** For a
   regulated system the record of a decision is part of the decision.
5. **Prove a gate can fail.** Break it once, on purpose, and watch it go red.
6. **Assert invariants, not outcomes.** Test what the design guarantees, not what one run happened to return.

The first rule is still only half done. The end-to-end replay is opt-in: CI runs the unit tests and the Airflow
smoke test, but not the replay against a running stack, so starting the whole system is still something I do by
hand. It is the next gate to automate.

So, how do we know it works? Not because it built, and not because a checker approved it. Because it ran, and
something looked at what it actually did.

---

**The evidence:** the project’s
[tech-debt log](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/docs/TECH_DEBT.md)
and [changelog](https://github.com/anandnarayanan2017/iam-ai-tf/blob/100c0d2f8a9fc57be2b824940d40a7917e36589a/CHANGELOG.md)
record each finding with its date and fix. The links above point at the commit this series describes.
