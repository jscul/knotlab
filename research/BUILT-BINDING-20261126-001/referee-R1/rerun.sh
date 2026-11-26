#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
r=research/BUILT-BINDING-20261126-001/referee-R1
p=.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2621440

run() {
    local file=$1
    shift
    "$p" -B "$r/$file.py" --pilot
    "$p" -B "$r/$file.py" "$@"
}

run record
run replay_records --output "$r/replay_counts.json"
run ring_check --run
run ring_relations
run witness_check --output "$r/witness_counts.json"
run cut_check
run argument
run group_limit
for roster in census heldout sampled
do
    "$p" -B "$r/unrestricted.py" --group "$roster" --pilot
    "$p" -B "$r/unrestricted.py" --group "$roster"
done
run heldout_certificate
