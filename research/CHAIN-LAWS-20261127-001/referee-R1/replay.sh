#!/usr/bin/env bash
# Run from any directory; artifacts are written beside this script.
set -eu
ref=$(cd -- "$(dirname -- "$0")" && pwd)
cd -- "$ref/../../.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
run() {
    local script=$1
    shift
    .venv/bin/python -B "$ref/$script" "$@"
}
both() { run "$1" --pilot; run "$1"; }

# Each workload uses the same resource configuration for its pilot and full run.
# The address limits below are in KiB. This replay runs workloads sequentially.
ulimit -v 1572864
(ulimit -v 921600; both record_audit.py)
both growth.py
both step_inventory.py
both step_readings.py
both step_controls.py
both step_exceptions.py
(ulimit -v 921600; both local_witness.py; both source_projections.py)
run step_paired.py --pilot
run step_paired.py --widest 8
run step_paired.py --controls --pilot
run step_paired.py --controls
run step_paired.py
(
    ulimit -v 1310720
    both step_nonpaired_controls.py
    run step_nonpaired.py --pilot
    run step_nonpaired.py --ids 17,39 --output-prefix step_nonpaired_sizing
    run step_nonpaired.py
)
run step_summary.py --frozen-only --pilot
run step_summary.py --frozen-only
both step_summary.py
both selection.py
run selection.py --pilot --join-complete
run selection.py --join-complete
# Optional independent solver comparison. Both engines must support assumptions.
if [[ -n "${STAGE_COMPARISON_BACKEND:-}" ]]; then
    run step_compare_backends.py --backend "$STAGE_COMPARISON_BACKEND" --pilot
    run step_compare_backends.py --backend "$STAGE_COMPARISON_BACKEND"
fi
