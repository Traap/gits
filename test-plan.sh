#!/usr/bin/env bash

LOGFILE="run-gits-test-plan.log"
> "$LOGFILE"

function run() {
  echo "▶ $@" | tee -a "$LOGFILE"
  eval "$@" >> "$LOGFILE" 2>&1
  echo "" >> "$LOGFILE"
}

# gits help
run "gits --help"

# gits list
run "gits list"
run "gits list -v"
run "gits list -r fzf"
run "gits list -r fzf -v"

# gits delete
run "gits delete -v"

# gits clone
run "gits clone -v"

# gits status
run "gits status"
run "gits status -v"
run "gits status -r fzf"
run "gits status -r fzf -v"

# gits delete
run "gits delete -r fzf --dry-run"
run "gits delete -r fzf --verbose"

# gits clone
run "gits clone -r fzf --dry-run"
run "gits clone -r fzf --verbose"
run "gits clone -r fzf"

# Make changes to ~/fzf/everything
cd
cd ~/fzf/everything
touch a b c d e f
cd

# gits status
run "gits status -r fzf -v"

# gits pull
run "gits pull -r fzf --dry-run"
run "gits pull -r fzf --verbose"
run "gits pull -r fzf"

# gits pop
run "gits pop -r fzf -n"
run "gits pop -r fzf -v"

# gits clean
run "gits clean -r fzf --dry-run"
run "gits clean -r fzf --verbose"
run "gits clean -r fzf"

# gits convert
run "gits convert -r fzf --dry-run"
run "gits convert -r fzf --verbose"

# gits delete
run "gits delete -r fzf"
run "gits delete -r fzf --dry-run"
run "gits delete -r fzf --verbose"

# command fallback tests
run "gits"
