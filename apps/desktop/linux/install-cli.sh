#!/bin/sh
# Link the dsh CLI from an installed deb (or an extracted AppImage) into ~/.local/bin.
set -eu
APP_DIR=${DSH_DESKTOP_APP_DIR:-/opt/DeepSeek Harness}
CLI="$APP_DIR/resources/runtime/cli/bin/dsh"
if [ ! -x "$CLI" ]; then
  echo "install-cli: expected an executable CLI at $CLI" >&2
  echo "install-cli: set DSH_DESKTOP_APP_DIR to the unpacked application directory" >&2
  exit 1
fi
mkdir -p "$HOME/.local/bin"
ln -sf "$CLI" "$HOME/.local/bin/dsh"
echo "installed $HOME/.local/bin/dsh -> $CLI"
