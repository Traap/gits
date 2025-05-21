#!/bin/bash

set -e

# Ensure python3 and pip3 are installed.
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Installing python3..."
  if command -v apt >/dev/null 2>&1; then
    sudo apt update && sudo apt install -y python3
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm python
  else
    echo "Unsupported package manager. Please install python3 manually."
    exit 1
  fi
fi

if ! command -v pip3 >/dev/null 2>&1; then
  echo "pip3 not found. Installing python3-pip..."
  if command -v apt >/dev/null 2>&1; then
    sudo apt update && sudo apt install -y python3-pip
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm python-pip
  else
    echo "Unsupported package manager. Please install pip manually."
    exit 1
  fi
fi

# Install PyYAML using pip, unless installed via system package manager
if ! python3 -c "import yaml" 2>/dev/null; then
  echo "PyYAML not found, installing..."
  if command -v apt >/dev/null 2>&1; then
    sudo apt update && sudo apt install -y python3-yaml || pip3 install --user --upgrade PyYAML
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm python-yaml || pip3 install --user --upgrade PyYAML
  else
    pip3 install --user --upgrade PyYAML
  fi
fi

# Clone to /tmp/gits and run from there.
git clone https://github.com/Traap/gits /tmp/traap/gits
cd /tmp/traap/gits

# Copy files to their production locations.
sudo cp -v gits /usr/local/bin/.
sudo chmod -v +x /usr/local/bin/gits

# Install default config if not present
mkdir -p "$HOME/.config/gits"
if [ ! -f "$HOME/.config/gits/repository_locations.yml" ]; then
  cp -v repository_locations.yml "$HOME/.config/gits/repository_locations.yml"
fi

# Cleanup temporary directory.
rm -rf /tmp/traap/

echo "Installation complete."
echo "Add /usr/local/bin to your PATH if it's not already."
