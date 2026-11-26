#!/usr/bin/env bash
# Run from any directory. All outputs stay beside this script.
set -euo pipefail
folder=$(cd "$(dirname "$0")" && pwd)
cd "$folder/../../.."
python_bin=.venv/bin/python
run_check() {
    local script=$1
    shift
    "$python_bin" -B "$folder/$script.py" "$@"
}
case "${1:-witnesses}" in
    all|witnesses) ;;
    *) echo 'Use witnesses or all.' >&2; exit 2 ;;
esac

run_check weighted_example --pilot
run_check weighted_example
run_check input_check --pilot
run_check input_check
run_check challenge --pilot --out "$folder/challenge_pilot.json"
run_check challenge --out "$folder/challenge.json"
run_check hand_audit --pilot --output "$folder/hand_audit_pilot.json"
run_check hand_audit --output "$folder/hand_audit.json"
if [[ ${1:-witnesses} == witnesses ]]; then
    exit 0
fi

run_check provenance --pilot
run_check provenance
run_check recount --limit 12 > "$folder/recount_pilot.json"
run_check recount > "$folder/recount.json"
run_check sampling --pilot 16
run_check sampling
run_check all_readers --pilot
run_check all_readers
run_check replay pilot
run_check replay sample
run_check replay_closure pilot
run_check replay_closure both
run_check omitted --pilot
run_check omitted
run_check engine_audit --pilot --output "$folder/engine_audit_pilot.json"
run_check engine_audit --logs-only --output "$folder/engine_audit_logs.json"
run_check engine_audit --output "$folder/engine_audit.json"
(
    ulimit -v 1572864
    run_check descent "$folder/descent_pilot.json" --select tree40:0 --select tree40:12 \
        --select treeplus25:0 --select treeplus25:2 --select census6:28907 --select census6:80874
    run_check descent "$folder/descent_archive.json" --archive
    run_check descent "$folder/descent_replay.json"
)
