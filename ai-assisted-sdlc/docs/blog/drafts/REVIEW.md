# AI-assisted SDLC series: publish-readiness review (2026-11-09)

Nothing in `drafts/` reaches the site: `scripts/sync-series.mjs` reads only `posts/`. To publish a part, move
`drafts/posts/NN-*.md` to `posts/`, `drafts/linkedin/NN-*.md` to `linkedin/`, add its hero to `images/`, and add
`dates` and `excerpts` entries for it in `series.json`.

## Status

| Part | Title | Status | Blocking before publish |
|---|---|---|---|
| 1 | From ARM Assembly to AI | Live (2026-11-01) | — |
| 2 | A Prompt Is Not a Specification | **Ready.** On `develop`, site date 2026-11-11, hero done | Merge `develop` → `main` on or after 11 Nov (the build doesn't hold back future dates, so an earlier merge publishes it early). |
| 3 | The Harness Around the Agent | Draft for final review | Hero image; excerpt and date |
| 4 | “Please Be Careful” Is Not a Permission Model | Draft for final review | Hero image; excerpt and date; check the external links |
| 5 | When the AI Reviewer Says 9/10 and the Test Still Fails | Draft for final review | Hero image; excerpt and date; question B |
| 6 | Human Approval Is a Control, Not a Button | Draft for final review | Hero image (the existing “Who approved this?” cartoon may fit); excerpt and date; question C |
| 7 | From Coding Agent to Engineering Factory | Draft for final review | Hero image; excerpt and date; question B |

Each part has the post (`drafts/posts/`) and its LinkedIn post (`drafts/linkedin/`). The posts are 1,150–1,400
words, in line with Parts 1–2 (1,040 and 1,285 words). Each keeps the house structure: an italic subtitle, short
paragraphs, a “Where this stops working” section, a “Next:” line, one reader question and a references list.
They use only facts from the harness's design records and the recorded run.

## Questions for the author

**A. Recorded or live run? Resolved (2026-11-09):** a live model run, recorded for replay. Part 2, the README and
the Part 3 and 5 drafts now say so.

**B. Publish the harness code?** Parts 3–5 and 7 describe harness mechanisms: restoring tests, the path check, the
one-way verdict rule, calibration and the benchmark. The harness repository is private and must not be named or
linked. So the drafts link only to `examples/double-booking`, which is already public. Two options:
(1) keep it as it is, prose only, which is fine as written; or (2) copy a trimmed harness example into
`ai-assisted-sdlc/examples/`, as Part 1 did for the booking code, and link to it from Parts 3–5.

**C. Part 6 versus “Who Approved This?”** Part 6 reuses the strongest parts of the unpublished “Who Approved This?”
draft: the PR with no person on it, DORA, the fail-closed gate and the five Monday questions. It frames them around
the roadmap's promise (which changes need a person, and making the review mean something). If you still want
“Who Approved This?” as a separate post, Part 6 needs different examples. The Oct 2026 GitHub changelog links are
cited only once, in the references (workflow lockfiles GA). Please re-check that URL.

## Checks to run per part before publishing

- [ ] Every external link opens (Part 4: OWASP, Willison, Node.js permissions, GitHub token docs; Part 5: arXiv,
      Fowler; Part 6: EUR-Lex, GitHub changelog; Part 7: arXiv 2107.03374).
- [ ] No link to, or mention of, the private harness repository.
- [ ] The hero image has alt text that describes the image in full, as Parts 1–2 do. The suggested concepts are in an
      HTML comment at the top of each draft. Replace that comment with the image line.
- [ ] Add the `series.json` `dates` and `excerpts` entries. Suggested excerpts:
  - 3: “The same model behaves very differently depending on what surrounds it. Context, tools, feedback and recovery: what a harness has to do, and why every part of it encodes a doubt about the model.”
  - 4: “A rule in a prompt is a request. A rule in the system is a control. What an agent may read, change and execute, and what stops it when it tries anyway.”
  - 5: “The AI reviewer scored the code 9/10. The test proved it double-booked a room ten times. Both were honest. Where model judgement helps, and why a deterministic check must win.”
  - 6: “A human clicking Approve on fifty green pull requests is a ritual, not a control. Which changes need a person, and what that person needs to see.”
  - 7: “Specifications, a harness, enforced permissions, deterministic checks and a human gate, brought together into one delivery flow that produces code and the evidence it is safe to ship.”
- [ ] `npm run build` and `typos` pass. Both passed on these drafts on 2026-11-09.
- [ ] Update the series README table (`ai-assisted-sdlc/README.md`) if the part brings code.

## Suggested cadence

Parts 1 and 2 are ten days apart. At the same rhythm: Part 3 on about 21 Nov, Part 4 on 1 Dec, Part 5 on 11 Dec,
Part 6 in early January (after the holidays) and Part 7 about ten days later.
