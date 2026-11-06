#!/usr/bin/env bash
# Use the repository's hooks (scripts/git-hooks/) for this clone.
set -euo pipefail
cd "$(dirname "$0")/.."
git config core.hooksPath scripts/git-hooks
echo "Git hooks installed (core.hooksPath=scripts/git-hooks)."
