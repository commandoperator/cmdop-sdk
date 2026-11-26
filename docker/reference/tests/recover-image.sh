#!/bin/sh
# Exercise the offline recovery procedure on an isolated Compose project.
set -eu
cd "$(dirname "$0")/.."
scratch=$(mktemp -d)
project="cmdop-recovery-$(basename "$scratch" | tr '[:upper:].' '[:lower:]-')"
tag="$project:local"
compose() {
  docker compose -p "$project" -f compose.yaml -f "$scratch/test.yaml" "$@"
}
cleanup() {
  compose down --timeout 0 --volumes >/dev/null
  docker image rm "$tag" >/dev/null
  rm -rf "$scratch"
}
cat > "$scratch/test.yaml" <<YAML
services:
  report-app:
    image: $tag
    entrypoint: ["sh", "-ec"]
    command:
      - |
        cmdop --version
        if test -f /home/cmdop/proof; then
          cat /home/cmdop/proof
        else
          echo retained > /home/cmdop/proof
        fi
    restart: "no"
    network_mode: none
YAML
docker tag cmdop-report-app:local "$tag"
trap cleanup EXIT
compose up -d --pull never --no-build --no-deps report-app
container=$(compose ps -aq report-app)
test "$(docker wait "$container")" = 0
image=$(docker inspect --format '{{.Image}}' "$container")

# Simulate a later build changing the local tag to a different image.
docker tag cmdop-report-report-fixture "$tag"
test "$(docker image inspect --format '{{.Id}}' "$tag")" != "$image"
printf 'services:\n  report-app:\n    image: %s\n' "$image" |
  compose -f - up -d --pull never --no-build --force-recreate --no-deps report-app
replacement=$(compose ps -aq report-app)
test "$replacement" != "$container"
test "$(docker wait "$replacement")" = 0
test "$(docker inspect --format '{{.Image}}' "$replacement")" = "$image"
docker logs "$replacement" | grep -Fx retained
