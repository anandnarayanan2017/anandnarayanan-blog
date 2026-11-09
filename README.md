# anandnarayanan.net

Source for [anandnarayanan.net](https://anandnarayanan.net), my personal blog, and the code behind its
article series.

## About

I work full time as a Solutions Architect based in Luxembourg. I have over 20 years of experience in
enterprise architecture across fintech, manufacturing, automotive and telecom. My fintech background has
shaped my interest in designing scalable, secure and audit-ready cloud, data and AI platforms, with a
particular focus on regulated environments and alignment with CSSF requirements, DORA and ISO 27001.

This blog and its projects are independent personal pursuits that I work on in my spare time, alongside my
full-time role. Find me on [LinkedIn](https://linkedin.com/in/anandkn2012).

## What this repository is trying to do

Most writing about AI agents stays at the level of opinion. Each series here pairs the articles with
something you can inspect: the specifications, design records, code and tests the articles describe. The
question running through all of it is the one from AI-assisted SDLC Part 1:

> How do we know it works?

So every claim in an article should point at a test, a design record or code that backs it up, and the
site is built and published from the same repository that holds that evidence.

## The series

| Folder | Series | What it covers |
|---|---|---|
(https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/agent-sentinel) | Agent Sentinel | An explainable runtime observability and policy-detection layer for AI agents in regulated environments: detect, explain, export. The code, tests, policies and a local Docker stack live in the folder. |
|(https://github.com/anandnarayanan2017/anandnarayanan-blog/tree/main/ai-assisted-sdlc) | AI-assisted SDLC | What it takes to delegate software work to AI agents and still know it works: specifications, harnesses, deterministic checks and human approval. The essays live here; the harness code lives in its own repository. |

Each series folder is the single source of truth for its posts. `docs/blog/series.json` holds its release
dates, excerpts and home-page card. Optionally, per part, it holds an `updated` date (shown as
"Last reviewed") and a list of `sources` (shown at the top of the post):

```json
"updated": { "1": "2027-03-01" },
"sources": { "1": [{ "title": "Claude prompting best practices", "url": "https://platform.claude.com/docs/" }] }
```

## How the site is built

- [Astro](https://astro.build) and plain CSS, built to last: no CSS framework, system fonts, and posts in
  standard Markdown. Pages and layout are in `src/`.
- Colours, fonts and widths are CSS custom properties at the top of `src/styles/global.css`. Restyling the
  site means changing those tokens, not the templates. Dark mode redefines the same tokens.
- The only JavaScript is the small inline dark-mode script and `public/js/site.js`
  (theme toggle, tag filter). Every page reads correctly without it; the table of contents is plain HTML.
- `/rss.xml` is the feed and `/sitemap-index.xml` the sitemap.


```bash
npm ci
npm run dev
```

## Acknowledgements

Thanks to Claude by Anthropic, which I use as a reviewer, editor and coding assistant on this blog and
its projects. The ideas, opinions and any mistakes are my own.

## Licence

- **Code** is licensed under the [Apache License 2.0](LICENSE).
- **Written content and images** in each series' `docs/blog/` folder are licensed under
  [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CONTENT). You may share and adapt
  them, including commercially, as long as you credit Anand Narayanan and link to the source. Code samples
  inside the write-ups are also available under Apache 2.0.

Copyright 2026 Anand Narayanan. See [NOTICE](NOTICE).
