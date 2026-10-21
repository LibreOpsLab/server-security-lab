#!/usr/bin/env bash
# Create your own PRIVATE copy of this repo that keeps its full history, and add this repo as `upstream`.
#
# Why not a GitHub fork? A fork of a public repo is always public, and your build will contain your lab
# details. A private copy with the same history behaves like a fork: `git fetch upstream` and
# `git merge upstream/main` work cleanly.
#
# Usage: scripts/create-private-copy.sh [name]      (default name: server-security-lab)
# Needs: git, and the GitHub CLI (gh) logged in with `gh auth login`.
set -euo pipefail

UPSTREAM_URL=${UPSTREAM_URL:-https://github.com/LibreOpsLab/server-security-lab.git}
GH_BASE=${GH_BASE:-https://github.com}
name=${1:-server-security-lab}

command -v gh >/dev/null 2>&1 || { echo "install the GitHub CLI (gh) and run 'gh auth login' first" >&2; exit 2; }
user=$(gh api user --jq .login)

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

git clone --bare "$UPSTREAM_URL" "$tmp/bare"
gh repo create "$name" --private
git -C "$tmp/bare" push --mirror "$GH_BASE/$user/$name.git"

git clone "$GH_BASE/$user/$name.git" "$name"
git -C "$name" remote add upstream "$UPSTREAM_URL"

echo "Done. Your private copy is in ./$name (origin: $user/$name, upstream: $UPSTREAM_URL)."
echo "Next: cd $name && read weeks/12-baseline-attack/README.md"
