#!/usr/bin/env bash
# Run in a clean SDK checkout. Stage only the reference tree and its provenance.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
if [[ -n "$(git status --porcelain --untracked-files=all -- docker/reference docker/SOURCE)" ]]; then
  echo 'Commit or move local Docker reference and SOURCE changes before syncing.' >&2
  exit 1
fi
git fetch --quiet --no-tags https://github.com/commandoperator/cmdop-docker.git refs/heads/main
source_commit=$(git rev-parse FETCH_HEAD)
source_tree=$(git rev-parse "$source_commit:reference")
current_tree=$(git rev-parse --verify HEAD:docker/reference)
if [[ "$current_tree" == "$source_tree" ]]; then
  exit 0
fi
# Apply the complete update together so a path collision leaves the index intact.
git diff --binary --full-index --no-renames --no-ext-diff "$current_tree" "$source_tree" |
  git apply --index --directory=docker/reference
printf '%s\n' "$source_commit" > docker/SOURCE
git add docker/SOURCE
