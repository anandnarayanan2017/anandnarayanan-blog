#!/usr/bin/env bash
# Owner-only commit check, used by the commit-policy and deploy workflows.
#
# Every commit in BASE..HEAD (or every commit reachable from HEAD when BASE
# is empty or all zeros) must:
#   1. be authored by the repository owner (author email in OWNER_EMAILS),
#   2. be committed by the owner, or by GitHub itself (web merges and
#      squash merges have committer "GitHub <noreply@github.com>"),
#   3. carry no AI co-author trailer, AI session link or "Generated with" line.
# If ACTOR is set (the GitHub user who opened the PR or pushed), it must be
# OWNER_LOGIN.
#
#   BASE=origin/main HEAD=HEAD scripts/check-commits.sh
set -euo pipefail

OWNER_LOGIN="${OWNER_LOGIN:-anandnarayanan2017}"
OWNER_NAME="${OWNER_NAME:-Anand Narayanan}"
# Space-separated. The GitHub noreply address keeps the personal address out
# of public history.
OWNER_EMAILS="${OWNER_EMAILS:-34368623+anandnarayanan2017@users.noreply.github.com}"
GITHUB_COMMITTER="noreply@github.com"

HEAD="${HEAD:-HEAD}"
if [ -z "${BASE:-}" ] || [ "$BASE" = "0000000000000000000000000000000000000000" ]; then
  range="$HEAD"
else
  range="$BASE..$HEAD"
fi

pattern='^[[:space:]*]*co-authored-by:.*(claude|anthropic)|^[[:space:]*]*claude-session:|generated with \[claude code\]|claude\.ai/code/session_'

is_owner_email() {
  local e
  for e in $OWNER_EMAILS; do
    [ "${1,,}" = "${e,,}" ] && return 0
  done
  return 1
}

bad=0
fail() { echo "::error::$*"; bad=1; }

if [ -n "${ACTOR:-}" ] && [ "$ACTOR" != "$OWNER_LOGIN" ]; then
  fail "GitHub user '$ACTOR' is not the repository owner '$OWNER_LOGIN'"
fi

count=0
for c in $(git rev-list --no-merges "$range"); do
  count=$((count + 1))
  IFS=$'\t' read -r short an ae cn ce subject < <(git show -s --format=$'%h\t%an\t%ae\t%cn\t%ce\t%s' "$c")
  if ! is_owner_email "$ae"; then
    fail "commit $short '$subject' is authored by '$an <$ae>', not the owner"
  elif [ "$an" != "$OWNER_NAME" ]; then
    # GitHub squash merges take the author name from the GitHub profile, so a
    # different name is a warning; the email is what identifies the owner.
    echo "::warning::commit $short '$subject' has author name '$an', expected '$OWNER_NAME'"
  fi
  if ! is_owner_email "$ce" && [ "${ce,,}" != "$GITHUB_COMMITTER" ]; then
    fail "commit $short '$subject' is committed by '$cn <$ce>', not the owner or GitHub"
  fi
  if git show -s --format=%B "$c" | grep -Eiq "$pattern"; then
    fail "commit $short '$subject' has an AI co-author or session line: $(git show -s --format=%B "$c" | grep -Ei "$pattern" | head -1)"
  fi
done

# The PR description only reaches main if the repo squashes with the PR
# description as the message, so this is a warning, not a failure.
if printf '%s\n%s\n' "${PR_TITLE:-}" "${PR_BODY:-}" | grep -Eiq "$pattern"; then
  echo "::warning::the PR title or description has an AI co-author or session line; remove it before a squash merge"
fi

if [ "$bad" = 1 ]; then
  echo "Only the owner's own commits may reach this repository. Re-author the"
  echo "commits (git rebase with 'git commit --amend --reset-author'), remove"
  echo "AI co-author or session lines, and push again."
  exit 1
fi
echo "OK: $count commit(s) in $range are the owner's, with no AI co-author or session lines."
