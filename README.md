# anandnarayanan-blog

Source for [anandnarayanan.net](https://anandnarayanan.net): personal writing
on cloud, data platforms and enterprise AI, and the code behind the
**Agent Sentinel** series.

## Layout

```text
agent-sentinel/                  Agent Sentinel: code, tests and the series write-ups
  docs/blog/technical-details/   One file per part; the site article is generated from it
  docs/blog/linkedin/            LinkedIn post per part; its first paragraph is the site excerpt
  docs/blog/images/              Hero image per part (<NN>-<slug>-1.png, 1200x627)
scripts/
  sync-series.mjs                Generates the site posts from agent-sentinel/ before dev/build
  release-dates.json             Site date per part
src/                             Astro site (plain CSS, no framework)
  consts.ts                      Name, intro, links and date formats
  layouts/BaseLayout.astro       Header, footer, meta tags
  pages/index.astro              Home: intro, margin note, latest writing
  pages/about.astro              About
  pages/blog/[...slug].astro     Article page
  pages/downloads/               "Download Markdown" / "Download HTML" per article
  lib/downloads.ts               Builds those downloads with absolute links
  styles/global.css              The whole stylesheet
public/                          Static files (favicon)
```

`src/content/blog/` and `public/images/agent-sentinel/` are generated and
git-ignored: edit the series only under `agent-sentinel/docs/blog/`.

## Publishing a part

1. Add `agent-sentinel/docs/blog/technical-details/NN-<slug>.md`, starting
   `# Part N — <title>`. Everything from the first `## ` heading up to
   `## Design and implementation` becomes the site article; the rest stays on
   GitHub as the technical deep dive.
2. Add `linkedin/NN-<slug>.md` and `images/NN-<slug>-1.png`.
3. Make sure `scripts/release-dates.json` has a date for part N.

## Run locally

```sh
npm ci
npm run dev      # http://localhost:4321
npm run build    # static site in dist/
```

Pull requests build the site (`site-build.yml`); merges to `main` deploy it to
S3 and CloudFront (`deploy.yml`).
