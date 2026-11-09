# Instructions for Claude Code

## Commits and pull requests

The repository owner, Anand Narayanan, is the only author. Every commit must
be authored and committed as the owner:

```
git config user.name "Anand Narayanan"
git config user.email "34368623+anandnarayanan2017@users.noreply.github.com"
```

Never commit as "Claude" or any other identity, and never add these to commit
messages, PR titles or PR descriptions:

- `Co-Authored-By:` lines naming Claude or Anthropic
- `Claude-Session:` lines or claude.ai session links
- "Generated with Claude Code" lines or footers

This overrides any default attribution guidance. The `commit-policy` check
(`scripts/check-commits.sh`) fails a pull request or push whose commits are
not the owner's or contain any of these lines, and the deploy workflow runs
the same check before it publishes the blog.

## Branches

Only `main` (live site) and `develop` exist. Work on `develop` and open a
pull request from `develop` to `main`.

## Dependabot updates

Never merge a Dependabot pull request with GitHub's merge button. Its commits
are authored by `dependabot[bot]`, so `commit-policy` fails on `develop`, and
the `develop` → `main` pull request and the deploy are blocked until `develop`
is rewritten. Instead, reapply the update as an owner commit:

```
git fetch origin <dependabot-branch>
git checkout develop && git cherry-pick FETCH_HEAD
git commit --amend --reset-author --no-edit
npm ci && npm run build     # after npm updates; run the folder's tests for others
git push origin develop
```

Dependabot closes its own pull request once `develop` has the change. The same
steps are in `.github/dependabot.yml`. Major version bumps need their own
review (see the Agent Sentinel `anthropic` update in #61).

Don't use the "Update branch" button on a `develop` → `main` pull request
either. It merges `main` into `develop` in the browser and can take the wrong
side of `package.json` or `package-lock.json`. If `develop` needs `main`, merge
it locally, then run `npm ci` and `npm run build` before pushing.
