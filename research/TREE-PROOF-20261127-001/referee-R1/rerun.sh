#!/usr/bin/env bash
# Run from the repository root. The only output files are the referee's JSON tables.
set -euo pipefail
ulimit -v 3145728
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
workspace_python=.venv/bin/python
referee=research/TREE-PROOF-20261127-001/referee-R1

time "$workspace_python" -B "$referee/record_audit.py" --limit 12 > /dev/null
time "$workspace_python" -B "$referee/record_audit.py" > "$referee/record_audit.json"
for study in diagnostics exceptions single_reads; do
    time "$workspace_python" -B "$referee/$study.py" --pilot
    time "$workspace_python" -B "$referee/$study.py"
done

# Each three-place projection saved in single_reads.json has these four even values.
time PYTHONPATH=tools "$workspace_python" -B -m knotlab check --cnf 'A B ~c; A ~B c; ~A B c; ~A ~B ~c' --loops A B --contact c --json

time "$workspace_python" -B "$referee/metric_witness.py" --pilot > /dev/null
time "$workspace_python" -B "$referee/metric_witness.py" > "$referee/metric_witness.json"
time "$workspace_python" -B "$referee/check_witness_growth.py" --pilot
time "$workspace_python" -B "$referee/check_witness_growth.py"

time "$workspace_python" -B "$referee/stress_wide.py" --pilot > /dev/null
time "$workspace_python" -B "$referee/stress_wide.py" --output "$referee/stress_wide.json"
time "$workspace_python" -B "$referee/replay.py" --pilot
time "$workspace_python" -B "$referee/replay.py" --output "$referee/replay_results.json" --raw "$referee/replay_pairs.json"
time "$workspace_python" -B "$referee/growth_compare.py" --pilot
time "$workspace_python" -B "$referee/growth_compare.py" --output "$referee/growth_comparison.json"

# Earlier records, searched using only the historical cutoff and public object descriptions.
"$workspace_python" -B scripts/track.py objects 'pair cost family facts least flip single linkage parity growth' --until 2026-11-27 --exclude TREE-PROOF-20261127-001 --limit 12
"$workspace_python" -B scripts/track.py objects 'recover knot holding presentation allowed states alone bond distance growth' --until 2026-11-26 --exclude TREE-PROOF-20261127-001 SELECTED-KNOTS-20261127-001 --limit 8
