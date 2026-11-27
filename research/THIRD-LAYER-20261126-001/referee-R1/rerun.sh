#!/usr/bin/env bash
# Run from the repository root. Each check times a subset before its full roster.
set -euo pipefail
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
r=research/THIRD-LAYER-20261126-001/referee-R1
for check in record growth solver_gate minima scale_audit splits grouping readers ring_overlap overlap; do
    args=()
    case "$check" in
        growth) args=(--output "$r/growth_counts.json") ;;
        minima) args=(--out "$r/minima_counts.json") ;;
        scale_audit) args=(--output "$r/scale_counts.json") ;;
    esac
    .venv/bin/python -B "$r/$check.py" --pilot >/dev/null
    .venv/bin/python -B "$r/$check.py" "${args[@]}" >/dev/null
    echo "Passed $check"
done
