#!/usr/bin/env bash
# Run in a clean SDK checkout. Stage only the reference tree and its provenance.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git fetch --quiet --no-tags https://github.com/commandoperator/cmdop-docker.git refs/heads/main
source_commit=$(git rev-parse FETCH_HEAD)
source_tree=$(git rev-parse "$source_commit:reference")
if [[ "$(git rev-parse --verify HEAD:docker/reference 2>/dev/null || true)" == "$source_tree" ]]; then
  exit 0
fi
git rm -qr --ignore-unmatch docker/reference
git read-tree -u --prefix=docker/reference/ "$source_tree"
printf '%s\n' "$source_commit" > docker/SOURCE
git add docker/SOURCE
