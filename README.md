### Gits is a simple tool to manage groups of git repositories.

### Features
- Clone multiple repositories into categorized folders
- Pull updates across repositories
- Define custom repo sets using an external config
- Compact CLI with short options (`-c`, `-r`, etc.)

### Dependences
- apt or pacman
- Python3
- pip3

#### Python packages
- argparse
- sys
- os
- yaml
- subprocess
- shutil
- concurrent.features
- ThreadPoolExecutor

### Installation
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Traap/gits/master/install.sh)"
```

### Removal
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Traap/gits/master/uninstall.sh)"
```

### Use
```console
Usage: gits [-h -l] [-r name -d -s -u -x] [-c | -p] [-n -v]

Options:
  -h  Show help.
  -l  List repository locations.

Repository Locations:
  -r  name
Modifiers:
  -d  Delete repository location.
  -s  List repositories with edits, delete, stasned and untracked files.
  -u  Convert UTF-16 files to UTF-8.
  -v  Verbose output.
  -x  Clean untracked files.

Mutually exclusive actions:
  -c  Clone repositories in repository locations array.
  -p  Pull repositories in repository location array with safe stashing.

Miscellaneous:
  -n  Dry-run (simulate actions).
  -v  Verbose output.
```

### Example Respository Location File
```console
$HOME/.config/gits/repository_locations.yml
```

```yaml
editor:
  - alias: LazyVim
    url: https://github.com/LazyVim/starter

  - alias: lazy.nvim
    url: https://github.com/folke/lazy.nvim

  - alias: neovim
    url: https://github.com/neovim/neovim

fzf:
  - alias: fzf
    url: https://github.com/junegunn/fzf-git.sh

  - alias: everything
    url: https://github.com/junegunn/everything.fzf

hyprland:
  - alias: Dots
    url: https://github.com/JaKooLit/Hyprland-Dots

  - alias: Arch
    url: https://github.com/JaKooLit/Arch-Hyprland

plugins:
  - alias: neo-tree
    url: https://github.com/nvim-neo-tree/neo-tree.nvim

  - alias: telescope
    url: https://github.com/nvim-telescope/telescope.nvim

  - alias: fugitive
    url: https://github.com/tpope/vim-fugitive

traap:
  - alias: gits
    url: https://github.com/Traap/gits
    do_not_delete: true

  - alias: nvims
    url: https://github.com/Traap/nvims
    do_not_delete: true
```
