#!/usr/bin/env bash

LOGFILE="run-gits-test-plan.log"
> "$LOGFILE"

function run() {
  echo "▶ $@" | tee -a "$LOGFILE"
  eval "$@" >> "$LOGFILE" 2>&1
  echo "" >> "$LOGFILE"
}

# gits list
run "gits list"
run "gits list -r traap"
run "gits list -v"
run "gits list -v -r traap"

# gits status
run "gits status"
run "gits status -r traap"

# gits pull
run "gits pull -r traap"
run "gits pull -r traap --dry-run"
run "gits pull -r traap --verbose"

# gits clean
run "gits clean -r traap"
run "gits clean -r traap --dry-run"
run "gits clean -r traap --verbose"

# gits convert
run "gits convert -r traap"
run "gits convert -r traap --dry-run"

# gits delete
run "gits delete -r traap"
run "gits delete -r traap --dry-run"
run "gits delete -r traap --verbose"

# command fallback tests
run "gits"
run "gits unknown"
