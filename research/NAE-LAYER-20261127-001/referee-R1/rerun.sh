#!/usr/bin/env bash
# From the repository root. Run a short timed case before each full family.
set -euo pipefail
r=research/NAE-LAYER-20261127-001/referee-R1
ulimit -v 2097152
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1

run() {
    /usr/bin/time -f '%e s, %M KiB' .venv/bin/python -B "$@"
}

run "$r/source_census.py" --pilot
run "$r/source_census.py"
run "$r/growth_audit.py" --pilot > "$r/growth_pilot.json"
run "$r/growth_audit.py" > "$r/growth_results.json"
run "$r/seven_check.py" --pilot
run "$r/seven_check.py"
run "$r/carrier_search.py" --limit-partitions 3 > /dev/null
run "$r/carrier_search.py" --out "$r/carrier_search.json" > /dev/null
run "$r/carrier_witness.py" birth --rounds 1
run "$r/carrier_witness.py" birth --rounds 4 --out "$r/carrier_birth.json"
run "$r/carrier_witness.py" nine --rounds 1
run "$r/carrier_witness.py" nine --rounds 2 --out "$r/carrier_nine.json"
run "$r/carrier_witness.py" seven --limit-partitions 3
run "$r/carrier_witness.py" seven --out "$r/carrier_seven.json"
run "$r/weight_counts.py" --pilot --output "$r/weight_pilot.json"
run "$r/weight_counts.py" --output "$r/weight_tables.json"
run "$r/lemma_checks.py" --pilot > /dev/null
run "$r/lemma_checks.py" --output "$r/lemma_counts.json"

export PYTHONPATH=tools
run -m knotlab check --loops x y --contact p --cnf 'x y p; ~x ~y ~p' --json > /dev/null
run -m knotlab check --loops x y z --contact q --witnesses p r \
    --cnf 'q p x; ~q ~p ~x; p r y; ~p ~r ~y; r q z; ~r ~q ~z' \
    --json > "$r/lemma_ring_check.json"

source_law='d0 d1 d2; ~d0 ~d1 ~d2'
round_one='d0 d3 d4; ~d0 ~d3 ~d4; d1 d5 d6; ~d1 ~d5 ~d6; d2 d7 d8; ~d2 ~d7 ~d8'
round_two='d3 d5 d9; ~d3 ~d5 ~d9; d4 d7 d10; ~d4 ~d7 ~d10; d6 d8 d11; ~d6 ~d8 ~d11'
readouts='~a ~d3; ~a ~d4; a d3 d4; ~b ~d5; ~b ~d6; b d5 d6; ~c ~d7; ~c ~d8; c d7 d8'
run -m knotlab check --loops a b --contact c --witnesses d{0..8} \
    --cnf "$source_law; $round_one; $readouts" --json > "$r/growth_relation_pilot.json"
run -m knotlab check --loops a b --contact c --witnesses d{0..11} \
    --cnf "$source_law; $round_one; $round_two; $readouts" --json > "$r/growth_relation_round2.json"
run -m knotlab check --loops a b --contact c --witnesses d{0..11} \
    --cnf "$round_one; $round_two; $readouts" --json > "$r/growth_relation_delete.json"
unset PYTHONPATH
run "$r/record_audit.py" --pilot > /dev/null
run "$r/record_audit.py" > "$r/record_audit.json"
