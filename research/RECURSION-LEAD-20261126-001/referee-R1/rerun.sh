#!/usr/bin/env bash
set -euo pipefail
R=research/RECURSION-LEAD-20261126-001/referee-R1
P=.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 2097152
time "$P" -B "$R/growth_check.py" --limit 12 >/dev/null
"$P" -B "$R/growth_check.py" --output "$R/growth.json"
time "$P" -B "$R/exchange_audit.py" all --literal --limit 100 >/dev/null
"$P" -B "$R/exchange_audit.py" all --literal --output "$R/exchange.json" >/dev/null
time "$P" -B "$R/exchange_controls.py" --pilot >/dev/null
"$P" -B "$R/exchange_controls.py" --output "$R/exchange_controls.json" >/dev/null
time "$P" -B "$R/projections.py" --pilot
"$P" -B "$R/projections.py" --output "$R/projections.json"
time "$P" -B "$R/rival_exchange.py" --limit 64
"$P" -B "$R/rival_exchange.py" --output "$R/rival_exchange.json"
time "$P" -B "$R/tower_extension.py" --pilot >/dev/null
"$P" -B "$R/tower_extension.py" --output "$R/tower_extension.json" >/dev/null
time "$P" -B "$R/tower_recount.py" --pilot >/dev/null
"$P" -B "$R/tower_recount.py" --output "$R/tower.json" >/dev/null
time "$P" -B "$R/counterexample.py" --pilot --output "$R/counterexample_pilot.json"
"$P" -B "$R/counterexample.py" --output "$R/counterexample.json"
for family in small parts; do
    time "$P" -B "$R/counterexample_${family}.py" --pilot --output "$R/counterexample_${family}_pilot.json"
    "$P" -B "$R/counterexample_${family}.py" --output "$R/counterexample_${family}.json"
done
(ulimit -v 1048576
 time "$P" -B "$R/counterexample_free.py" atlas 5 6 7 --limit 10 --output "$R/counterexample_free_atlas_pilot.json"
 "$P" -B "$R/counterexample_free.py" atlas 5 6 7 --output "$R/counterexample_free_atlas.json"
 time "$P" -B "$R/counterexample_free.py" witness 6 7 8 --limit 5 --output "$R/counterexample_free_witness_pilot.json"
 "$P" -B "$R/counterexample_free.py" witness 6 7 8 --output "$R/counterexample_free_witness.json"
)
time "$P" -B "$R/record.py" --pilot
"$P" -B "$R/record.py" --output "$R/record.json"
