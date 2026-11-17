# IAM AI series: publish readiness (2026-11-17)

All five parts are drafted, each with its post, its LinkedIn post, a hero image (2400 × 1254, Inter, full alt text
in the post), and a date and excerpt in `series.json`. Nothing in `drafts/` reaches the site, because
`scripts/sync-series.mjs` reads only `posts/`.

| Part | Title | Proposed date | Status |
|---|---|---|---|
| 1 | Who Signed In, and Do We Still Trust Them? | 2026-12-03 (Thu) | Draft |
| 2 | Rules Decide, Models Advise | 2026-12-17 (Thu) | Draft |
| 3 | One Place Decides | 2027-01-07 (Thu) | Draft |
| 4 | The Build Was Green. The System Had Never Run. | 2027-01-21 (Thu) | Draft |
| 5 | Tenants, Evidence and What Is Still Open | 2027-02-04 (Thu) | Draft |

The dates are a proposal: every second Thursday, because Mondays belong to Agent Sentinel and AI-assisted SDLC
until 18 January. A third series also splits attention; starting after 18 January, or alternating Thursdays with
fewer parts in flight, are both reasonable. Change the dates in `series.json`.

## Blocker: the evidence is in a private repository

Every evidence link points at `anandnarayanan2017/iam-ai-tf` at commit `100c0d2`. That repository is private, so
readers would get a 404, and the series card has no “Source code on GitHub” link yet. Choose one:

- **Make `iam-ai-tf` public**, then add `"codeUrl"` to the card in `series.json`. Before you do:
  - [ ] Check `infra/terraform/environments/*/terraform.tfvars` hold placeholder IDs only (the changelog says dev
        was scrubbed; check staging and prod too).
  - [ ] Remove the local paths (`F:\learn\ai_ml\...`) from `docs/agent-sentinel-vs-iam-ai.md`.
  - [ ] Run secret scanning over the full history, not only the current tree. `.env.setup.example` once held
        live-looking values; the changelog says they were never committed, so confirm it.
  - [ ] The README describes the infrastructure only and still has a week-by-week plan; add a short overview of
        the platform first.
  - [ ] Fix the ONNX claims in `docs/architecture/c4-architecture.md` and `.claude/rules/scoring.md` (never built).
- **Or keep it private**, as AI-assisted SDLC does with its harness: describe the mechanisms in prose, remove the
  links, and copy only small excerpts into `iam-ai/examples/` where a post needs them.

## Decisions for you

- [ ] **Opinions stated as yours.** Part 2: the model-can’t-block trade-off is “the right trade”. Part 5: a
      decision that cannot be recorded should be flagged and probably not enforced silently. Confirm or reword.
- [ ] **Your own to-do items, stated publicly.** Part 2 (a precision gate for model promotion) and Part 3 (store the
      policy’s reason; write the explanation after responding) say these are on your list.
- [ ] **AI involvement.** The reviews that found many of these bugs were run by AI review agents (the commits say
      “8-agent code review” and “9-angle code review”), and one commit has an AI co-author line. The posts call them
      “code reviews” and do not say who or what ran them. Decide whether to say more; it would tie in well with
      AI-assisted SDLC Part 5.
- [ ] **Series vs design note.** This replaces the standalone design note. If you prefer one note after all, Part 4
      stands alone with small edits to its first paragraph.

## Aligned with the code (2026-11-17)

The series was checked claim by claim against `iam-ai-tf`, and the claims that can be run were run: the policy in OPA
1.22.4, the API and scorer against the compose Postgres, Redis and Neo4j, and the retraining job’s query.

- 133 unit tests passed at `100c0d2` (1 September), as Parts 1 and 4 say. At `cc0af56` there are 139 unit tests and
  15 end-to-end tests, all passing, plus the Airflow `DagBag` tests.
- Running it found three defects, now fixed in `iam-ai-tf` branch `claude/gracious-edison-9lx70j` (`cc0af56`) and
  told in Parts 2, 3 and 4: policy helpers that made OPA error on some inputs, a learning loop that could never
  train, and training/scoring encodings that disagreed. Also confirmed: OPA’s reason is always the default (Part 3).
- Corrected in the posts: the scoring endpoint *ignores* a tenant in the body (it did not stop accepting one), and
  the README’s cost estimate predates five of the eight container apps.
- Evidence links now point at `cc0af56`. **That commit is on a branch.** After it is merged to `iam-ai-tf` `main`,
  repin the links to the merge result so they cannot disappear with the branch:
  `sed -i 's#/blob/cc0af56acf368a2466bc60d8be5b301628e81ee0/#/blob/<merged-sha>/#g' iam-ai/docs/blog/drafts/posts/*.md`

## Facts to confirm (from the project's records, not re-run)

- [ ] The first full `docker compose up` was on 26 July 2026 (tech-debt log), five weeks after the first commit.
- [ ] Cost estimates of about $200 (dev) and $845 (prod) a month at 2025 prices come from the README’s own table.

## To publish part N on its date

1. `git mv drafts/posts/NN-<slug>.md posts/` and `git mv drafts/linkedin/NN-<slug>.md linkedin/`.
2. In the post, change the image path from `../../images/` to `../images/`.
3. Set the date in `series.json` if it moved.
4. Run `npm run build` and `typos`, then a pull request to `develop` and then `develop` → `main`.
5. Share the LinkedIn post. Its first comment links to the live article.

Parts link only backwards, in the `NN-<slug>.md` form, which the build turns into site links. The build does this
whether or not the target is published, so a forward link would point at a page that does not exist yet and fail
the internal link check. Later parts are named in plain text instead; the series box under each post links to the
next part once it is live. Publish in order, and do not add forward links.
