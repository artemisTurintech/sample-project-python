#!/usr/bin/env bash

# Import variables
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "$DIR/variables.sh"

# Run benchmark, emit CSV, clean up raw JSON
echo "Running benchmark"
python -m poetry run pytest tests/ --benchmark-only --benchmark-json=artemis_raw.json && python -m poetry run python "$DIR/benchmark.py" > artemis_results.csv
rm -f artemis_raw.json
