#!/usr/bin/env bash

# 1. Activate the virtual environment
source .venv/bin/activate || {
  echo "❌ Failed to activate .venv"
  exit 1
}

# 2. Clear old log
: > gits.log

# 3. Define and run tests
run_test() {
  echo -e "\n=== Test: $* ===" >> gits.log
  "$@" >> gits.log 2>&1
}

run_test gits clone -n
run_test gits clean
run_test gits clean -r traap
run_test gits clean -r traap -v
run_test gits pull -v
run_test gits
run_test gits -r traap
run_test gits list
run_test gits list -r traap
run_test gits list -v
run_test gits list -r traap -v

# Optional: confirm success
echo -e "\n✅ All tests completed."
cat gits.log
