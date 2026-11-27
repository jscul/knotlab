#!/usr/bin/env bash
# Replay the referee checks in dependency order from any working directory.
set -euo pipefail
ref_dir=$(cd "$(dirname "$0")" && pwd)
repo_dir=$(cd "$ref_dir/../../.." && pwd)
cd "$repo_dir"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export PYTHONPATH="$repo_dir/tools" PYTHONDONTWRITEBYTECODE=1
ulimit -v 2097152
ref_python="$repo_dir/.venv/bin/python"
run() { "$ref_python" -B "$ref_dir/$1.py" "${@:2}"; }
timed_pair() { run "$1" --pilot; run "$1"; }

timed_pair recount
run recount --verify-order --pilot
run recount --verify-order
timed_pair record_check
timed_pair starting_patterns
timed_pair stage_readings
for variant in base direct one-law; do
    options=()
    output=counts
    if [[ "$variant" != base ]]; then
        options=("--$variant")
        output=${variant//-/_}
    fi
    pilot_name="failure_rule_${output}_pilot.json"
    if [[ "$variant" == base ]]; then pilot_name=failure_rule_pilot.json; fi
    run failure_rule "${options[@]}" --pilot --out "$ref_dir/$pilot_name"
    run failure_rule "${options[@]}" --out "$ref_dir/failure_rule_${output}.json"
done
for check in other_bonds_paired other_bonds_paired_witness other_bonds_determination other_bonds_controls other_bonds_summary; do
    timed_pair "$check"
done
timed_pair reading_choices
timed_pair census_six
(
    ulimit -v 1572864
    run stage_readings_omitted --workers 5 --reset-every 12 --pilot --pilot-per-stage 24
    run stage_readings_omitted --workers 5 --reset-every 12 --reuse "$ref_dir/stage_readings_omitted_parallel_pilot.jsonl.gz"
)

# Each size-balanced partition below uses one process at a time.
(
    ulimit -v 976562
    run converse --pilot --output "$ref_dir/converse_pilot_1gb.json" --replace
    run converse --bare-lengths 6 --output "$ref_dir/converse_chain_replay_pilot.json" --replace
    run converse --bare-lengths 6 7 8 9 --output "$ref_dir/converse_chain_replay.json" --replace
    parts=()
    for part in 0 1 2; do
        result="$ref_dir/converse_${part}of3.json"
        run converse --part "$part/3" --output "$result" --replace
        parts+=("$result")
    done
    run converse --merge "${parts[@]}" --output "$ref_dir/converse.json" --replace
)
timed_pair report_counts
