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

## 🧠 Usage
### 🧪 Help
```
gits --help
```
 Usage: gits [OPTIONS] COMMAND [ARGS]...

 Manage git repositories defined in YAML configuration.


╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --repo-group          -r      TEXT  [default: None]                          │
│ --verbose             -v                                                     │
│ --dry-run             -n                                                     │
│ --install-completion                Install completion for the current       │
│                                     shell.                                   │
│ --show-completion                   Show completion for the current shell,   │
│                                     to copy it or customize the              │
│                                     installation.                            │
│ --help                              Show this message and exit.              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ clean     Clean listed repositories by resetting and removing untracked      │
│           files, including subfolders.                                       │
│ clone     Clone repositories listed in the YAML file.                        │
│ convert   Convert UTF-16 files to UTF-8 in all repositories.                 │
│ doctor    Run environment and configuration checks for gits.                 │
│ delete    Delete repositories listed in YAML that are not protected by       │
│           do_not_delete.                                                     │
│ list      List repository groups and optionally their repositories.          │
│ pull      Pull changes for all repositories including unlisted ones.         │
│ status    Print git status for all repositories.                             │
╰──────────────────────────────────────────────────────────────────────────────╯

### 🧪 List
```
gits List
```
🗂️ editor
🗂️ fzf
🗂️ hyprland
🗂️ plugins
🗂️ traap


```
gits list -v
```
🗂️ editor
   🗃️ LazyVim
   🗃️ lazy.nvim
   🗃️ neovim
🗂️ fzf
   🗃️ fzf
   🗃️ everything
🗂️ hyprland
   🗃️ Dots
   🗃️ Arch
🗂️ plugins
   🗃️ neo-tree
   🗃️ telescope
   🗃️ fugitive
🗂️ traap
   🗃️ archlinux
   🗃️ gits
   🗃️ nvims
   🗃️ vimtex

```
gits list -v -r traap
```
🗂️ traap
   🗃️ archlinux
   🗃️ gits
   🗃️ nvims
   🗃️ vimtex


### 🧪 Clone
Clone runs 4 jobs concurrently so console output is interwoven.
```
gits clone
```
🗂️ editor
🗂️ fzf
🗂️ hyprland
🗂️ plugins
🗂️ traap
   📥 Cloned: fzf
   📥 Cloned: LazyVim
   📥 Cloned: lazy.nvim
   📥 Cloned: everything
   📥 Cloned: archlinux
   📥 Cloned: gits
   📥 Cloned: nvims
   📥 Cloned: vimtex
   📥 Cloned: Arch
   📥 Cloned: neovim
   📥 Cloned: Dots

```
gits clone -v -n
```
🗂️ editor
   📥 (dry-run) clone https://github.com/LazyVim/starter /home/traap/editor/LazyVim
   📥 (dry-run) clone https://github.com/folke/lazy.nvim /home/traap/editor/lazy.nvim
🗂️ fzf
   📥 (dry-run) clone https://github.com/junegunn/everything.fzf /home/traap/fzf/everything
   📥 (dry-run) clone https://github.com/junegunn/fzf-git.sh /home/traap/fzf/fzf
🗂️ hyprland
   📥 (dry-run) clone https://github.com/neovim/neovim /home/traap/editor/neovim
   📥 (dry-run) clone https://github.com/JaKooLit/Arch-Hyprland /home/traap/hyprland/Arch
   📥 (dry-run) clone https://github.com/JaKooLit/Hyprland-Dots /home/traap/hyprland/Dots
🗂️ plugins
   📥 (dry-run) clone https://github.com/nvim-telescope/telescope.nvim /home/traap/plugins/telescope
   📥 (dry-run) clone https://github.com/nvim-neo-tree/neo-tree.nvim /home/traap/plugins/neo-tree
   📥 (dry-run) clone https://github.com/tpope/vim-fugitive /home/traap/plugins/fugitive
🗂️ traap
   ⚠️ Exists: archlinux
   ⚠️ Exists: gits
   ⚠️ Exists: nvims
   ⚠️ Exists: vimtex

```
gits clone -v -r traap
```
🗂️ traap
Cloning into '/home/traap/traap/archlinux'...
Cloning into '/home/traap/traap/gits'...
Cloning into '/home/traap/traap/nvims'...
Cloning into '/home/traap/traap/vimtex'...
POST git-upload-pack (181 bytes)
POST git-upload-pack (gzip 1623 to 846 bytes)
   📥 Cloned: archlinux
   📥 Cloned: gits
   📥 Cloned: vimtex
   📥 Cloned: nvims

```

### 🧪 Status
```
gits status

```
**No output when there are not any errors.**

```
gits status -v
```
🗂️ editor
   🧹 Clean: LazyVim
   🧹 Clean: lazy.nvim
   🧹 Clean: neovim
🗂️ fzf
   🧹 Clean: fzf
   🧹 Clean: everything
🗂️ hyprland
   🧹 Clean: Dots
   🧹 Clean: Arch
🗂️ plugins
   🧹 Clean: neo-tree
   🧹 Clean: telescope
   🧹 Clean: fugitive
🗂️ traap
   🧹 Clean: archlinux
   🧹 Clean: gits
   🧹 Clean: nvims
   🧹 Clean: vimtex

```
gits status -v -r traap

```
🗂️ traap
   🧹 Clean: archlinux
   🧹 Clean: gits
   🧹 Clean: nvims
   🧠 Modified: vimtex
	 M README.md
	?? new-file
  stash@{0}: On master: gits status demo

### 🧪 Clean
```
gits clean -n
```
🧹 (dry-run) would clean LazyVim at /home/traap/editor/LazyVim
🧹 (dry-run) would clean lazy.nvim at /home/traap/editor/lazy.nvim
🧹 (dry-run) would clean neovim at /home/traap/editor/neovim
🧹 (dry-run) would clean everything at /home/traap/fzf/everything
🧹 (dry-run) would clean fzf at /home/traap/fzf/fzf
🧹 (dry-run) would clean Dots at /home/traap/hyprland/Dots
🧹 (dry-run) would clean Arch at /home/traap/hyprland/Arch
🧹 (dry-run) would clean telescope at /home/traap/plugins/telescope
🧹 (dry-run) would clean neo-tree at /home/traap/plugins/neo-tree
🧹 (dry-run) would clean fugitive at /home/traap/plugins/fugitive
🧹 (dry-run) would clean gits at /home/traap/traap/gits
🧹 (dry-run) would clean archlinux at /home/traap/traap/archlinux
🧹 (dry-run) would clean vimtex at /home/traap/traap/vimtex
🧹 (dry-run) would clean nvims at /home/traap/traap/nvims


```
gits clean -v
```
HEAD is now at 803bc18 docs: Explain more about how to add and remove autocmds (#105)
HEAD is now at 6c3bda4 chore(main): release 11.17.1 (#1927)
HEAD is now at 3ec3e97 Support opening GitHub URLs via WSL (#75)
🧹 LazyVim: cleaned successfully
🧹 fzf: cleaned successfully
🧹 lazy.nvim: cleaned successfully
HEAD is now at a13eb03 Add wiki.fzf
HEAD is now at 8813180 Merge pull request #289 from JaKooLit/development
🧹 everything: cleaned successfully
HEAD is now at ee8eb7a Update README.de.md
🧹 Arch: cleaned successfully
🧹 Dots: cleaned successfully
HEAD is now at c7f38e3bc8 fix(api): nvim_parse_cmd parses :map incorrectly #34068
HEAD is now at 3f1dd2d fix(renderer): fix cut & paste stack overflow on hidden root (#1792)
HEAD is now at 4a745ea Remove antiquated `a` map
HEAD is now at b4da76b fix(lsp): stop using deprecated `client.supports_method` function (#3468)
🧹 fugitive: cleaned successfully
🧹 neo-tree: cleaned successfully
🧹 telescope: cleaned successfully
HEAD is now at ef3e4db Add hyprland and bspwm.
HEAD is now at 806d8f6 Update repository locations.
HEAD is now at c6d4631 Add installation done message.
🧹 neovim: cleaned successfully
🧹 archlinux: cleaned successfully
🧹 nvims: cleaned successfully
🧹 gits: cleaned successfully
HEAD is now at 4b4f18b1 merge: fix test-tkz-euclide.vim
Removing new-file
🧹 vimtex: cleaned successfully
```

```
gits clean -v -r traap -n
🧹 (dry-run) would clean archlinux at /home/traap/traap/archlinux
🧹 (dry-run) would clean gits at /home/traap/traap/gits
🧹 (dry-run) would clean vimtex at /home/traap/traap/vimtex
🧹 (dry-run) would clean nvims at /home/traap/traap/nvims

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
### 🧪 Delete
Delete will remove all repos within a group and the group itself unless 1) a
repo is marked do_not_delete or repo untracked.  Untracked repos are not listed
in repository_locations.yml.
```
gits delete
```
🗂️ editor
   ⚠️ Not Empty: editor -> /home/traap/editor
🗂️ fzf
   🗑️ Deleted: fzf
   🗑️ Deleted: everything
   🗑️ Deleted: fzf
🗂️ hyprland
   🗑️ Deleted: Dots
   🗑️ Deleted: Arch
   🗑️ Deleted: hyprland
🗂️ plugins
   🗑️ Deleted: neo-tree
   🗑️ Deleted: telescope
   🗑️ Deleted: fugitive
   🗑️ Deleted: plugins
🗂️ traap
   ⚠️ Not Empty: traap -> /home/traap/traap

```
gits delete -v -n
```
🗂️ editor
   🗑️ (dry-run) would remove: LazyVim -> /home/traap/editor/LazyVim
   🗑️ (dry-run) would remove: lazy.nvim -> /home/traap/editor/lazy.nvim
   🗑️ (dry-run) would remove: neovim -> /home/traap/editor/neovim
   ⚠️ Not Empty: editor -> /home/traap/editor
🗂️ fzf
   🗑️ (dry-run) would remove: fzf -> /home/traap/fzf/fzf
   🗑️ (dry-run) would remove: everything -> /home/traap/fzf/everything
   ⚠️ Not Empty: fzf -> /home/traap/fzf
🗂️ hyprland
   🗑️ (dry-run) would remove: Dots -> /home/traap/hyprland/Dots
   🗑️ (dry-run) would remove: Arch -> /home/traap/hyprland/Arch
   ⚠️ Not Empty: hyprland -> /home/traap/hyprland
🗂️ plugins
   🗑️ (dry-run) would remove: neo-tree -> /home/traap/plugins/neo-tree
   🗑️ (dry-run) would remove: telescope -> /home/traap/plugins/telescope
   🗑️ (dry-run) would remove: fugitive -> /home/traap/plugins/fugitive
   ⚠️ Not Empty: plugins -> /home/traap/plugins
🗂️ traap
   🗑️ (dry-run) would remove: archlinux -> /home/traap/traap/archlinux
   🧠 Skipped gits (do_not_delete = true)
   🧠 Skipped nvims (do_not_delete = true)
   🗑️ (dry-run) would remove: vimtex -> /home/traap/traap/vimtex
   ⚠️ Not Empty: traap -> /home/traap/traap
   🧠 No repositories deleted.

```
gits delete -v -r traap
```
🗂️ traap
   🗑️ Deleted: archlinux -> /home/traap/traap/archlinux
   🧠 Skipped gits (do_not_delete = true)
   🧠 Skipped nvims (do_not_delete = true)
   🗑️ Deleted: vimtex -> /home/traap/traap/vimtex
   ⚠️ Not Empty: traap -> /home/traap/traap

```
gits delete -v -r editor
🗂️ editor
   🗑️ Deleted: LazyVim -> /home/traap/editor/LazyVim
   🗑️ Deleted: lazy.nvim -> /home/traap/editor/lazy.nvim
   🗑️ Deleted: neovim -> /home/traap/editor/neovim
   🗑️ Deleted: editor -> /home/traap/editor


## 🛠️ Development
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
