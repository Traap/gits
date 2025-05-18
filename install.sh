#!/bin/bash

set -e

# Clone to /tmp/gits and run from there.
git clone https://github.com/Traap/gits /tmp/traap/gits
cd /tmp/traap/gits

# Copy files to their production locations.
sudo cp -v gits /usr/local/bin/.
sudo chmod -v +x /usr/local/bin/gits

# Install default config if not present
mkdir -p "$HOME/.config/gits"
if [ ! -f "$HOME/.config/gits/repo_locations.yml" ]; then
  cp repo_locations "$HOME/.config/gits/repo_locations.yml"
fi

# Cleanup temporary directory.
rm -rf /tmp/traap/

echo "Installation complete."
echo "Add /usr/local/bin to your PATH if it's not already."
