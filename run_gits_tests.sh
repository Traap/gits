#!/usr/bin/env bash

LOGFILE="gits.log"
VENV=".venv/bin/gits"

set -e
echo "" > $LOGFILE

function run_test() {
  echo "$ $@" | tee -a $LOGFILE
  eval "$@" >> $LOGFILE 2>&1
  echo "" >> $LOGFILE
}

# Define repo group
GROUP="fzf"

# Commands to test
run_test "$VENV"
run_test "$VENV -r $GROUP"
run_test "$VENV status -r $GROUP"
run_test "$VENV pull -r $GROUP -n"
run_test "$VENV clean -r $GROUP -n"
run_test "$VENV delete -r $GROUP -n"
run_test "$VENV clone -r $GROUP -n"
run_test "$VENV convert -r $GROUP -n"
run_test "$VENV list"
run_test "$VENV list -r $GROUP"
run_test "$VENV list -r $GROUP -v"
