# AI-assisted SDLC series: publish readiness (updated 2026-11-24)

Parts 4–7 are ready to publish. Each has its post, its LinkedIn post, a hero image and an excerpt in
`series.json`. Nothing in `drafts/` reaches the site, because `scripts/sync-series.mjs` reads only `posts/`.

A part's date in `series.json` is the day it went live, added on that day. Planned dates are not stored there:
the build fails on a date after today, so a part can never show a release that hasn't happened.

## Status

| Part | Title | Went live | Status |
|---|---|---|---|
| 1 | From ARM Assembly to AI | 2026-11-01 | Live |
| 2 | A Prompt Is Not a Specification | 2026-11-09 | Live |
| 3 | The Harness Around the Agent | 2026-11-24 | Live |
| 4 | “Please Be Careful” Is Not a Permission Model | | Ready |
| 5 | When the AI Reviewer Says 9/10 and the Test Still Fails | | Ready |
| 6 | Human Approval Is a Control, Not a Button | | Ready |
| 7 | From Coding Agent to Engineering Factory | | Ready |
| 8 | Threat-Modelling the Factory Before It Gets Tools | | Draft: needs the ID checks below |

Parts 4–8 go out one at a time, in order, about every two weeks. Part 8 is backed by
[`docs/threat-model.md`](../../threat-model.md), which is already public and is the link to use elsewhere (CV, talks)
until Part 8 has a site URL.

## To publish part N on its date

The site shows a post as soon as it is deployed, and the build does not hold back future dates, so do this on the
day itself, not before.

1. `git mv drafts/posts/NN-<slug>.md posts/` and `git mv drafts/linkedin/NN-<slug>.md linkedin/`.
2. In the post, change the image path from `../../images/` to `../images/`.
3. Add today's date for the part to `dates` in `series.json`. The build refuses a date after today.
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
- [ ] **Part 8 only:** check every MITRE ATLAS technique ID and name in `docs/threat-model.md` section 6 against
      atlas.mitre.org (names change, e.g. "ML" to "AI"), and re-map AC-04, AC-05, AC-13 and AC-14 if newer
      agent-specific techniques fit better.
- [ ] **Part 8 only:** check the OWASP Agentic IDs (ASI01–ASI10) and LLM 2025 IDs against genai.owasp.org.
- [ ] **Part 8 only:** when publishing, change the "Companion post" link at the top of `docs/threat-model.md` from
      `blog/drafts/posts/` to `blog/posts/`, and set its **Last reviewed** date.
