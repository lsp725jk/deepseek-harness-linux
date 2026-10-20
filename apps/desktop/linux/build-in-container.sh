#!/usr/bin/env bash
# Build the unsigned Linux x64 AppImage and deb in an Ubuntu 22.04 container.
# Usage: bash apps/desktop/linux/build-in-container.sh [--dir]
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
MODE=${1:-}
docker build -t dsh-linux-build -f "$ROOT/apps/desktop/linux/Dockerfile" "$ROOT/apps/desktop/linux"
if [ "$MODE" = "--dir" ]; then
  TARGET="package:linux:x64:dir -- --unsigned"
else
  TARGET="package:linux:x64:unsigned"
fi
# shellcheck disable=SC2086
exec docker run --rm \
  -v "$ROOT:/src" -v dsh-pnpm-store:/pnpm-store -w /src \
  -e ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/ \
  -e npm_config_registry=https://registry.npmmirror.com \
  dsh-linux-build bash -lc "pnpm config set store-dir /pnpm-store && pnpm install --frozen-lockfile && pnpm --dir apps/desktop run $TARGET"
