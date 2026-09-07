#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
python_bin="${GITS_TEST_PYTHON:-.venv/bin/python}"
if [[ ! -x "$python_bin" ]]; then
  python_bin=python3
fi
exec "$python_bin" -m unittest discover -s tests -v
