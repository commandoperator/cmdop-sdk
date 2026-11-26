#!/usr/bin/env bash
set -euo pipefail
sync="$(cd "$(dirname "$0")/.." && pwd)/sync-docker.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export GIT_AUTHOR_NAME=Fixture GIT_COMMITTER_NAME=Fixture
export GIT_AUTHOR_EMAIL=fixture@example.invalid GIT_COMMITTER_EMAIL=fixture@example.invalid
git init -q -b main "$tmp/upstream"
cd "$tmp/upstream"
mkdir reference
printf 'original\n' > reference/connect
touch reference/obsolete
git add .
git commit -qm initial

git init -q -b main "$tmp/sdk"
cd "$tmp/sdk"
mkdir docker
cp -R "$tmp/upstream/reference" docker/reference
git -C "$tmp/upstream" rev-parse HEAD > docker/SOURCE
git config url."$tmp/upstream".insteadOf https://github.com/commandoperator/cmdop-docker.git
git add .
git commit -qm baseline

cd "$tmp/upstream"
chmod +x reference/connect
git rm -q reference/obsolete
printf 'new file\n' > reference/new
git add reference
git commit -qm update

cd "$tmp/sdk"
printf 'local edit\n' > docker/SOURCE
if "$sync"; then exit 1; fi
test "$(cat docker/SOURCE)" = 'local edit'
git diff --cached --exit-code
git restore docker/SOURCE
"$sync"
test -x docker/reference/connect
test ! -e docker/reference/obsolete
test "$(cat docker/SOURCE)" = "$(git -C "$tmp/upstream" rev-parse HEAD)"
git commit -qm synced
test "$(git rev-parse HEAD:docker/reference)" = "$(git -C "$tmp/upstream" rev-parse HEAD:reference)"
git -C "$tmp/upstream" commit -q --allow-empty -m unrelated
"$sync"
test -z "$(git status --porcelain)"
