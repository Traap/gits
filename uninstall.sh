#!/usr/bin/env bash

set -euo pipefail

REPO_NAME=".gits"
INSTALL_DIR="$HOME/$REPO_NAME"
BIN_LINK="$HOME/.local/bin/gits"

echo "🧼 Uninstalling gits from $INSTALL_DIR"

# Remove symlink
if [[ -L "$BIN_LINK" ]]; then
  echo "🔗 Removing symlink: $BIN_LINK"
  rm -f "$BIN_LINK"
else
  echo "ℹ️  No symlink found at $BIN_LINK"
fi

# Remove install directory
if [[ -d "$INSTALL_DIR" ]]; then
  echo "🗑️  Removing installation directory: $INSTALL_DIR"
  rm -rf "$INSTALL_DIR"
else
  echo "ℹ️  No directory found at $INSTALL_DIR"
fi

echo "✅ gits uninstalled successfully."
