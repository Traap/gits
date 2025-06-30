#!/usr/bin/env bash

set -euo pipefail

PRODUCT_LOCATION=".gits"
INSTALL_DIR="$HOME/$PRODUCT_LOCATION"
VENV_DIR="$INSTALL_DIR/.venv"
PRODUCT_NAME="gits"
BIN_LINK="$HOME/.local/bin/$PRODUCT_NAME"
CONFIG_FILE="$HOME/.config/$PRODUCT_NAME/repository_locations.yml"

echo "📦 Installing $PRODUCT_NAME to $INSTALL_DIR"

# Ensure ~/.local/bin exists and is on PATH
mkdir -p "$HOME/.local/bin"
if ! command -v "$PRODUCT_NAME" &>/dev/null && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo "⚠️  Please add \$HOME/.local/bin to your PATH."
fi

# Check for uv and install if missing
if ! command -v uv &>/dev/null; then
  echo "🚀 uv not found. Installing..."

  if [[ -f /etc/arch-release ]]; then
    sudo pacman -Sy --noconfirm uv
  elif command -v apt &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
  else
    echo "❌ Unsupported OS. Please install uv manually."
    exit 1
  fi
fi

# Clone the repo if not already cloned
if [[ ! -d "$INSTALL_DIR" ]]; then
  git clone https://github.com/Traap/gits.git "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Remove existing .venv
rm -rf "$VENV_DIR"

echo "🐍 Creating virtual environment..."
uv venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "🔧 Installing project..."
uv pip install -e .

# Symlink CLI
if [[ -f "$VENV_DIR/bin/$PRODUCT_NAME" ]]; then
  ln -sf "$VENV_DIR/bin/$PRODUCT_NAME" "$BIN_LINK"
  echo "🔗 Symlinked: $BIN_LINK → $VENV_DIR/bin/$PRODUCT_NAME"
fi

# Copy default config file if not already customized
if [[ ! -f "$CONFIG_FILE" ]]; then
  mkdir -pv "$(dirname "$CONFIG_FILE")"
  cp -v repository_locations.yml "$CONFIG_FILE"
  echo "📝 Installed default repository_locations.yml to $INSTALL_DIR"
fi

echo "✅ Done! You can now run: $PRODUCT_NAME"
