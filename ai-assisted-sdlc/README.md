# AI-assisted SDLC

Write-ups for the AI-assisted SDLC series on [anandnarayanan.net](https://anandnarayanan.net). The code they describe
(a TypeScript harness that runs delivery as a planner, contract, generator, check, evaluator and human-gate loop,
plus a multi-vendor model benchmark) lives in its own repository:
[anandnarayanan2017/ai-assisted-sdlc](https://github.com/anandnarayanan2017/ai-assisted-sdlc).

| Path | What it holds |
|---|---|
| `docs/blog/posts/NN-<slug>.md` | One post per part, published whole. The `# ` heading is the title. |
| `docs/blog/images/NN-<slug>-1.png` | The part's hero and social-preview image (more images: `-2.png`, ...). |
| `docs/blog/series.json` | Site settings: release date and excerpt per part, tags, home-page card. |

`npm run build` at the repository root generates the site's pages from this folder (`scripts/sync-series.mjs`).

## Licence

Code is licensed under [Apache 2.0](../LICENSE). The write-ups and images in `docs/blog/` are licensed under
[CC BY 4.0](../LICENSE-CONTENT): reuse them with credit to Anand Narayanan. See [NOTICE](../NOTICE).
