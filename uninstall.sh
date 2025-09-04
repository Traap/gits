#!/usr/bin/env bash
# {{{ Config
set -euo pipefail

PRODUCT_NAME="gits"
REPO_NAME=".gits"
INSTALL_DIR="$HOME/$REPO_NAME"
BIN_DIR="$HOME/.local/bin"
BIN_LINK="$BIN_DIR/$PRODUCT_NAME"

# -------------------------------------------------------------------------- }}}
# {{{ Remove CLI hook (symlink or launcher)

echo "🧼 Uninstalling $PRODUCT_NAME from $INSTALL_DIR"

if [[ -L "$BIN_LINK" ]]; then
  echo "🔗 Removing symlink: $BIN_LINK"
  rm -f "$BIN_LINK"
elif [[ -f "$BIN_LINK" ]]; then
  # Git Bash launcher (not a symlink)
  echo "🔗 Removing launcher script: $BIN_LINK"
  rm -f "$BIN_LINK"
else
  echo "ℹ️  No symlink or launcher found at $BIN_LINK"
fi

# -------------------------------------------------------------------------- }}}
# {{{ Remove installation directory

if [[ -d "$INSTALL_DIR" ]]; then
  echo "🗑️  Removing installation directory: $INSTALL_DIR"
  rm -rf "$INSTALL_DIR"
else
  echo "ℹ️  No directory found at $INSTALL_DIR"
fi

# -------------------------------------------------------------------------- }}}
# {{{ Remove default config file (optional

CONFIG_FILE="$HOME/.config/$PRODUCT_NAME/repository_locations.yml"
if [[ -f "$CONFIG_FILE" ]]; then
  echo "🗑️  Removing config file: $CONFIG_FILE"
  rm -f "$CONFIG_FILE"
else
  echo "ℹ️  No config file found at $CONFIG_FILE"
fi

echo "✅ $PRODUCT_NAME uninstalled successfully."

# -------------------------------------------------------------------------- }}}
