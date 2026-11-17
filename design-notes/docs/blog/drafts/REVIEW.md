# Design notes: publish readiness (2026-11-17)

Nothing in `drafts/` reaches the site, because `scripts/sync-series.mjs` reads only `posts/`.

| Note | Title | Proposed date | Status |
|---|---|---|---|
| 1 | The Build Was Green. The System Had Never Run. | 2026-12-03 (Thursday) | Draft, blocked on the evidence links |

The date is a proposal. Mondays are taken by the two series until 18 January, so a design note goes out midweek.
Change it in `series.json`.

## Blocker: the evidence is in a private repository

Every evidence link in note 1 points at `anandnarayanan2017/iam-ai-tf` at commit `100c0d2`. That repository is
private, so readers would get a 404. Choose one before publishing:

- **Make `iam-ai-tf` public.** Before you do, check:
  - [ ] `infra/terraform/environments/*/terraform.tfvars` hold placeholder IDs only (the changelog says dev was
        scrubbed; check staging and prod too).
  - [ ] `docs/agent-sentinel-vs-iam-ai.md` names local paths (`F:\learn\ai_ml\...`); remove them.
  - [ ] Run secret scanning over the full history, not only the current tree.
  - [ ] The README describes the infrastructure only and still has a week-by-week plan; add a short overview of
        the platform first.
- **Or copy the evidence here.** Put the cited files, or excerpts of them, under `design-notes/evidence/iam-ai/`
  and change the links to relative ones. The note names eleven files; the tech-debt log and changelog carry most
  of the weight.

## Facts to confirm (from the project's records, not re-run here)

- [ ] The first full `docker compose up` was on 2026-07-26 and the four services failed on start, as the tech-debt
      log records.
- [ ] The STEP_UP-instead-of-ALLOW replay failure happened after the anomaly sign fix, as recorded.
- [ ] You are happy to state the open question in "What is still not proven": that a decision whose record cannot
      be written still stands today, and that you think the stricter design is the better default.

## To publish

1. `git mv drafts/posts/01-the-build-was-green.md posts/` and `git mv drafts/linkedin/01-the-build-was-green.md linkedin/`.
2. In the post, change the image path from `../../images/` to `../images/`.
3. Set the date in `series.json` if it moved.
4. Run `npm run build` and `typos`, then a pull request to `develop` and then `develop` → `main`.
5. Share the LinkedIn post. Its first comment links to the live note.
