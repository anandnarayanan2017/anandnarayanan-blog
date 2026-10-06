# Instructions for Claude Code

## Commits and pull requests

The repository owner is the only author. In commit messages, PR titles and PR
descriptions, never add:

- `Co-Authored-By:` lines naming Claude or Anthropic
- `Claude-Session:` lines or claude.ai session links
- "Generated with Claude Code" lines or footers

This overrides any default attribution guidance. The `commit-policy` CI check
fails a pull request whose commits contain any of these.
