#!/usr/bin/env bash
# From the repository root. Stop at the first failed check.
set -euo pipefail
d=research/FOLLOWS-THE-FORM-20261125-001/referee-R1
p=.venv/bin/python
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 3145728
compare_json() {
  "$p" -B -c 'import json, sys; from pathlib import Path
reference = Path(sys.argv[1])
if json.load(sys.stdin) != json.loads(reference.read_text()):
    raise SystemExit(f"Mismatch with {reference.name}")
print(f"Matched {reference.name}")' "$d/$1"
}
"$p" -B "$d/held_recount.py" --smoke
"$p" -B "$d/held_recount.py" | compare_json held_counts.json
"$p" -B "$d/growth_replay.py" --limit 3
"$p" -B "$d/growth_replay.py" --limit 60 --output "$d/growth_replay.json"
"$p" -B "$d/growth_law_spread.py" --limit 6
"$p" -B "$d/growth_law_spread.py" --limit 60 --output "$d/growth_law_spread_full.json"
for check in trace_read trace_controls; do
  "$p" -B "$d/$check.py" --time-first
  "$p" -B "$d/$check.py"
done
for check in crosscheck_traces simple_counts compare_readings; do
  "$p" -B "$d/$check.py" --pilot
  "$p" -B "$d/$check.py"
done
"$p" -B "$d/posthoc_recount.py" --studies-per-family 1
"$p" -B "$d/posthoc_recount.py" --output "$d/posthoc_counts.json"
"$p" -B "$d/later_regrow_check.py" all > /dev/null
"$p" -B "$d/later_regrow_witnesses.py" > /dev/null
"$p" -B "$d/replication_counts.py" --smoke
"$p" -B "$d/replication_counts.py" | compare_json replication_counts.json
"$p" -B "$d/replay_gate.py" --pilot
"$p" -B "$d/replay_gate.py"
for control in renumber unfinished omitted; do
  case "$control" in
    renumber) record=replication_renumber.json ;;
    unfinished) record=replication_unfinished_knot_test.json ;;
    omitted) record=replication_omitted_knot_tests.json ;;
  esac
  "$p" -B "$d/replication_control_replay.py" "$control" --smoke > /dev/null
  "$p" -B "$d/replication_control_replay.py" "$control" | compare_json "$record"
done
"$p" -B scripts/track.py objects-gate research/FOLLOWS-THE-FORM-20261125-001A/preregistration.md
"$p" -B scripts/track.py objects "fixed link second seed forms what first descent births partner steps" \
  --until 2026-11-25 --exclude FOLLOWS-THE-FORM-20261125-001 --limit 5
"$p" -B scripts/track.py objects --epic WHAT-A-BIRTH-CARRIES-20261125-001 --limit 5
