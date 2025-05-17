### Gits

**Gits** is a simple tool to manage groups of git repositories.

### Features
- Clone multiple repositories into categorized folders
- Pull updates across repositories
- Define custom repo sets using an external config
- Compact CLI with short options (`-c`, `-r`, etc.)

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
Usage: gits [-h -l -R] [-r name -d -s -u -v -x] [-c | -p] [-n]

Options:
  -h  Show help.
  -l  List repository locations.
  -R  Apply modifiers to repository locations.

Repository Locations:
  -r  name
Modifiers:
  -d  Delete repository location.
  -s  List repositories with stash entries.
  -u  Convert UTF-16 files to UTF-8.
  -v  Verbose output.
  -x  Clean untracked files.

Mutually exclusive actions
  -c  Clone repositories in repository locations array.
  -p  Pull repositories in repository location array with safe stashing.

Dry-run
  -n  Dry-run (simulate actions)
```

### Example Respository Location File
```bash
repo_editor=(
  "https://github.com/folke/lazy.nvim.git lazy.nvim"
  "https://github.com/neovim/neovim.git neovim"
)

repo_fzf=(
  "https://github.com/junegunn/fzf-git.sh fzf1"
  "https://github.com/junegunn/everything.fzf fzf2"
)

repo_hyprland=(
  "git@github.com:JaKooLit/Hyprland-Dots.git Dots"
  "git@github.com:JaKooLit/Arch-Hyprland.git Arch"
)

repo_plugins=(
  "https://github.com/nvim-telescope/telescope.nvim telescope"
  "https://github.com/tpope/vim-fugitive fugitive"
)

repo_traap=(
  "https://github.com/Traap/gits gits"
  "https://github.com/Traap/nvims nvims"
)
```

