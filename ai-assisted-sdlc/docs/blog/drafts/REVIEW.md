# AI-assisted SDLC series: publish readiness (updated 2026-11-09)

Parts 3–7 are ready to publish. Each has its post, its LinkedIn post, a hero image, and a date and excerpt in
`series.json`. Nothing in `drafts/` reaches the site, because `scripts/sync-series.mjs` reads only `posts/`. The
dates for parts 3–7 have no effect until the part's post is in `posts/`.

## Status

| Part | Title | Site date | Status |
|---|---|---|---|
| 1 | From ARM Assembly to AI | 2026-11-01 | Live |
| 2 | A Prompt Is Not a Specification | 2026-11-09 | Live |
| 3 | The Harness Around the Agent | 2026-11-23 | Ready |
| 4 | “Please Be Careful” Is Not a Permission Model | 2026-12-07 | Ready |
| 5 | When the AI Reviewer Says 9/10 and the Test Still Fails | 2026-12-21 | Ready |
| 6 | Human Approval Is a Control, Not a Button | 2027-01-04 | Ready |
| 7 | From Coding Agent to Engineering Factory | 2027-01-18 | Ready |

Parts 3–7 go out every second Monday. They alternate weekly with Agent Sentinel (16 Nov, 30 Nov, 14 Dec, 28 Dec).

## To publish part N on its date

The site shows a post as soon as it is deployed, and the build does not hold back future dates, so do this on the
day itself, not before.

1. `git mv drafts/posts/NN-<slug>.md posts/` and `git mv drafts/linkedin/NN-<slug>.md linkedin/`.
2. In the post, change the image path from `../../images/` to `../images/`.
3. If the date has slipped, update `dates` in `series.json`.
4. Run `npm run build` and `typos`, then use a pull request to `develop` and then `develop` → `main`.
5. Share the LinkedIn post. Its first comment links to the live article.

## Decisions (open questions resolved)

- **The run behind “ten bookings”** was a live model run, recorded for replay. Part 2, the series README and
  Parts 3 and 5 say so.
- **The harness code stays private.** Parts 3–7 describe its mechanisms in prose and link only to the public
  `examples/double-booking` folder. Publishing a trimmed harness example would mean deciding what to open-source
  from a private repository, and none of the posts depends on it. To revisit it later, add a folder under
  `ai-assisted-sdlc/examples/` and link it from Parts 3–5.
- **Part 6 replaces the “Who Approved This?” draft.** Part 6 already uses its strongest material: the pull request
  with no person on it, DORA, the fail-closed gate and the five questions. The master copy of that draft in the
  private repository should be marked as superseded by Part 6, not published separately.
- **The hero images** are diagrams in the same style as Part 2: 2400 × 1254, Inter, with full alt text in each post.

## Before each part goes out, check

- [ ] Every external link still opens. These were not checked from the drafting environment: OWASP, Willison,
      Node.js, GitHub docs, arXiv, Fowler, EUR-Lex, and the 2026-10-28 GitHub changelog entry in Part 6.
- [ ] Nothing links to or names the private harness repository.
