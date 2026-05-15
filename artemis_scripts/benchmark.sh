#!/usr/bin/env bash

# Import variables
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "$DIR/variables.sh"

# Run benchmark via Python orchestrator (cross-platform RSS/CPU sampling).
# Forwards all args to benchmark.py (e.g. --runs N, --output PATH).
echo "Running benchmark"
python -m poetry run python "$DIR/benchmark.py" "$@"
