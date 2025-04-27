#!/bin/bash

set -e

# Install gits script
mkdir -p "$HOME/.local/bin"
cp gits "$HOME/.local/bin/gits"
chmod +x "$HOME/.local/bin/gits"

# Install default config if not present
mkdir -p "$HOME/.config/gits"
if [ ! -f "$HOME/.config/gits/repo_locations" ]; then
  cp config/repo_locations "$HOME/.config/gits/repo_locations"
fi

echo "Installation complete."
echo "Add \$HOME/.local/bin to your PATH if it's not already."

echo "Done."
