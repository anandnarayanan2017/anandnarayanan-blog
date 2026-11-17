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

## Facts to confirm (from the code and the project's records, not re-run here)

- [ ] The first full `docker compose up` was on 26 July 2026 (tech-debt log), five weeks after the first commit.
- [ ] 133 unit tests passing at 1 September (changelog); about 115 test functions, with parametrised cases.
- [ ] Cost estimates of about $200 (dev) and $845 (prod) a month at 2025 prices come from the README’s own table.
- [ ] **Not verified:** how OPA evaluates `reason` in `iam_risk.rego`. The rules assign `reason` inside each rule
      body, which in Rego may create a local variable rather than set the package-level `reason`. The posts make no
      claim about it. Part 3 states, from the API code, that the reason is discarded either way. Worth checking with
      `opa eval` before publishing Part 3; I could not download OPA in the drafting session.

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
