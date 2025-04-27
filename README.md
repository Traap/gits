# Gits

**Gits** is a simple tool to manage groups of git repositories.

## Features
- Clone multiple repositories to categorized folders
- Pull updates across many repositories
- Define custom sets of repos using an external config

## Installation
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Traap/gits/master/install.sh)"
```
Make sure `~/.local/bin` is in your `PATH`.

## Configuration
Edit your repository locations:
```bash
~/.config/gits/repo_locations
```
Define arrays like:
```bash
repo_bb=(
  "git@github.com:Traap/amber.git amber"
  "git@github.com:Traap/nvim.git nvim"
)
```

## Usage
```bash
gits -r bb git
```
Options:
- `-h` Show help
- `-l` List available repo locations
- `-r` Specify repo location(s)
- `-p` Pull latest changes (default)
- `-v` Verbose mode
- `-d` Dry-run (simulate)

## Example
Clone all bb and git repos:
```bash
gits -r bb git
```
Pull latest changes:
```bash
gits -r bb git -p
```
Dry-run clone:
```bash
gits -r bb git -d
```
