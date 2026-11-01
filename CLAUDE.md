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
