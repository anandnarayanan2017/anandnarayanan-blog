# AI-assisted SDLC (blog companion)

Write-ups for the AI-assisted SDLC series on [anandnarayanan.net](https://anandnarayanan.net), and the code each
part cites. Each part brings only the code it needs, so this folder grows with the series.

| Path | What it holds |
|---|---|
| `docs/blog/posts/NN-<slug>.md` | One post per part, published whole. The `# ` heading is the title. |
| `docs/blog/images/NN-<slug>-1.png` | The part's hero and social-preview image (more images: `-2.png`, ...). |
| `docs/blog/linkedin/NN-<slug>.md` | The LinkedIn post that shares the part; `NN-<slug>-article.md`, where present, is the LinkedIn Article version. |
| `docs/blog/series.json` | Site settings: release date and excerpt per part, tags, home-page card. |
| [`examples/double-booking/`](examples/double-booking/) | Part 1: the booking specification as code and tests. |

`npm run build` at the repository root generates the site's pages from this folder (`scripts/sync-series.mjs`).

## Part 1: "Build a booking API" is a wish

[From ARM Assembly to AI](docs/blog/posts/01-from-arm-assembly-to-ai.md) turns the wish into a specification:

> Twenty people try to book the same room for the same time slot simultaneously. Exactly one request succeeds
> with HTTP 201. The other nineteen receive HTTP 409. The database enforces the rule.

[`examples/double-booking/`](examples/double-booking/) is that specification, run against a real PostgreSQL:

| File | What it shows |
|---|---|
| [`tests/concurrency.test.ts`](examples/double-booking/tests/concurrency.test.ts) | The specification as tests: 20 simultaneous requests give exactly one 201 and nineteen 409s, and an overlapping row inserted directly with SQL is rejected (SQLSTATE 23P01). |
| [`src/routes/bookings-check-then-insert.ts`](examples/double-booking/src/routes/bookings-check-then-insert.ts) | The plausible first attempt: check for a clash, then insert. It passes every sequential test. |
| [`scripts/race.ts`](examples/double-booking/scripts/race.ts) | Fires the 20 requests at that first attempt. In local runs it booked the boardroom 19 or 20 times. |
| [`src/db/migrations/003_no_overlap.sql`](examples/double-booking/src/db/migrations/003_no_overlap.sql) | The fix: a PostgreSQL exclusion constraint, so the database enforces the rule. |
| [`src/routes/bookings.ts`](examples/double-booking/src/routes/bookings.ts) | The fixed route: it maps the constraint violation to 409. |

Run it with Docker only:

```bash
cd ai-assisted-sdlc/examples/double-booking
docker compose up --build --abort-on-container-exit --exit-code-from check
```

Or with Node 26 (the version in the repository's `.nvmrc`) and a PostgreSQL 16 at `DATABASE_URL` (default `postgres://postgres:postgres@localhost:5432/rooms`):

```bash
npm ci
npm run race     # the check-then-insert race; the count varies from run to run
npm run verify   # typecheck and tests for the fixed version
```

CI runs both on every pull request (`.github/workflows/ai-assisted-sdlc.yml`) and prints the race result on
the run's summary page.

### Where "ten times" comes from

The code is a trimmed copy of the room-booking example in the author's own unpublished delivery harness, where
an AI generator built the API sprint by sprint against these tests. The check-then-insert route was its first
attempt at the concurrency sprint. The AI evaluator approved it; the deterministic check did not. From the run log:

```text
CONTRACT [Concurrency-safe booking (no double-booking under load)]
  GENERATOR attempt 1: wrote 1 file(s)
  CHECK FAIL | EVALUATOR functionality=9 craft=8 => FAIL
    !! evaluator approved, but the deterministic check failed: the check wins
    FAIL  tests/s5-concurrency.test.ts > concurrency safety > exactly one of 20 simultaneous requests for the same slot wins
    AssertionError: expected [ 201, 201, 201, 201, 201, 201, …(4) ] to have a length of 1 but got 10
  -> failures fed back to the generator
  GENERATOR attempt 2: wrote 2 file(s)
  CHECK PASS | EVALUATOR functionality=9 craft=8 => PASS
```

The dashboard was green. The meeting was a contact sport.

Only the parts Part 1 cites are here: rooms, bookings and the concurrency tests. Users, availability search, the
harness itself and the model benchmark are not.

## Licence

Code is licensed under [Apache 2.0](../LICENSE). The write-ups and images in `docs/blog/` are licensed under
[CC BY 4.0](../LICENSE-CONTENT): reuse them with credit to Anand Narayanan. See [NOTICE](../NOTICE).
