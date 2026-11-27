#!/usr/bin/env bash
# Run from the repository root. Each pilot and full run use the same process limits.
set -eu
r=research/ONE-STATEMENT-20261127-001/referee-R1
export PYTHONPATH=tools
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 3145728
for check in record unmarked pair_sizes layer_audit growth_audit parity_argument family_witness nae_audit nae_compositions; do
    .venv/bin/python -B "$r/$check.py" --pilot
    .venv/bin/python -B "$r/$check.py"
done
.venv/bin/python -B "$r/parity_census.py" --pilot 128
.venv/bin/python -B "$r/parity_census.py" --output "$r/parity_counts.json"
