#!/bin/bash

set -e

# Remove all files nvims installed or created.
sudo rm -fv /usr/local/bin/gits
rm -rfv /tmp/traap
rm -rfv "$HOME"/.config/gits
