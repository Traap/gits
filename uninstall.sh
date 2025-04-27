#!/bin/bash

set -e

# Remove all files nvims installed or created.
sudo rm -f /usr/local/bin/gits
rm -rf /tmp/traap
rm -rf "$HOME"/.config/gits

echo "Uninstall complete."
