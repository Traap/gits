# 🧠 gits

`gits` is a Git repository group manager. It helps you efficiently clone, pull,
clean, convert, delete, and track the status of many repositories—organized by
group—using a single YAML configuration file.

---

## 📦 Features

- Define repositories in logical groups
- Use `alias`, `target_path`, and `do_not_delete` for fine-grained control
- CLI powered by [Typer](https://typer.tiangolo.com/)
- Fast installs and dependency management via [`uv`](https://astral.sh/uv/)
- Supports dry-run and verbose modes
- Works seamlessly on **Arch Linux** and **Ubuntu**

---

## 🚀 Installation

> Installs `gits` to `~/.gits` and links the CLI to `~/.local/bin/gits`.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Traap/gits/master/install.sh)"
```

This will:

Install uv if missing

Clone this repo into ~/.gits

Create a .venv and install dependencies

Symlink the CLI to ~/.local/bin/gits

Copy a default repository_locations.yml if one doesn't already exist

Ensure ~/.local/bin is in your PATH:``


## 🧹 Uninstall
To remove everything installed by gits:

> Removes `gits` from `~/.gits` and removes links the CLI to `~/.local/bin/gits`.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Traap/gits/master/install.sh)"
```

This will:

Remove the ~/.gits directory

Remove the CLI symlink from ~/.local/bin/gits

## 🧾 Default repository_locations.yml

```yaml

editor:
  - root_dir: ~/editor
  - repositories:
    - alias: LazyVim
      url: https://github.com/LazyVim/starter
    - alias: lazy.nvim
      url: https://github.com/folke/lazy.nvim
    - alias: neovim
      url: https://github.com/neovim/neovim

fzf:
  - root_dir: ~/fzf
  - repositories:
    - alias: fzf
      url: https://github.com/junegunn/fzf-git.sh
    - alias: everything
      url: https://github.com/junegunn/everything.fzf

hyprland:
  - root_dir: ~/hyprland
  - repositories:
    - alias: Dots
      url: https://github.com/JaKooLit/Hyprland-Dots
    - alias: Arch
      url: https://github.com/JaKooLit/Arch-Hyprland

plugins:
  - root_dir: ~/plugins
  - repositories:
    - alias: neo-tree
      url: https://github.com/nvim-neo-tree/neo-tree.nvim
    - alias: telescope
      url: https://github.com/nvim-telescope/telescope.nvim
    - alias: fugitive
      url: https://github.com/tpope/vim-fugitive

traap:
  - root_dir: ~/traap
  - repositories:
    - alias: archlinux
      url: git@github.com:Traap/bootstrap-archlinux
    - alias: gits
      url: git@github.com:Traap/gits
      do_not_delete: true
    - alias: nvims
      url: git@github.com:Traap/nvims
      do_not_delete: true
    - alias: vimtex
      url: https://github.com/lervag/vimtex
      do_not_delete: false
```

## 🧪 Usage
```
gits                      # Same as `gits status`
gits status               # Show git status across all repositories
gits clone -r traap       # Clone only repos in the 'traap' group
gits pull -r fzf          # Pull updates for the 'fzf' group
gits clean -r plugins     # Clean repos in the 'plugins' group
gits convert -r traap     # Convert .sql files from UTF-16 to UTF-8
gits delete -r fzf        # Delete repos not protected by do_not_delete
gits list                 # List all repository groups
gits list -r traap -v     # List repos in 'traap' with URLs
```

🛠️ Development
Clone and test locally:

```bash
git clone https://github.com/Traap/gits ~/.gits
cd ~/.gits
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

```bash
gits --help
```
