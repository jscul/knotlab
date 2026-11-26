#!/usr/bin/env bash
# Rerun from any directory. All writes go beside this file.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../.." && pwd)
cd "$root"
ulimit -Sv 2621440
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
py="$root/.venv/bin/python"
run() { "$py" -B "$here/$1.py" "${@:2}"; }

run provenance --pilot
run provenance
run alternatives --pilot
run alternatives
run start_places --pilot
run start_places
run map_check --pilot --output "$here/map_pilot.json"
run map_check --output "$here/map_counts.json"
run map_cancellation --limit 1 --output "$here/map_cancellation_pilot.json"
run map_cancellation --limit 223 --output "$here/map_cancellation.json"
run scores "$here/scores_pilot.json" --limit 12
run scores "$here/scores.json"
run scores_controls "$here/scores_controls_pilot.json" --limit 36 --confirm-all-rounds
run scores_controls "$here/scores_controls.json" --confirm-all-rounds
(
ulimit -Sv 2097152
run fittingaudit inventory --pilot 1 --output "$here/fittingaudit_inventory_pilot.json"
run fittingaudit inventory --output "$here/fittingaudit_inventory.json"
for mode in predictions small-replay cap-replay
do
    out=${mode//-/_}
    run fittingaudit_check "$mode" --pilot 1 --output "$here/fittingaudit_${out}_pilot.json"
    run fittingaudit_check "$mode" --output "$here/fittingaudit_${out}.json"
done
PYTHONPATH=tools run fittingaudit admission --pilot 1 --output "$here/fittingaudit_admission_pilot.json"
PYTHONPATH=tools run fittingaudit admission --output "$here/fittingaudit_admission.json"
)
run sampleaudit --pilot
run sampleaudit
run sampleaudit_omitted --pilot
run sampleaudit_omitted
mapfile -t pilot_args < <(run sampleaudit_knot uniform --args)
time PYTHONPATH=tools "$py" -B -m knotlab check "${pilot_args[@]}" > "$here/sampleaudit_knot_uniform_pilot.json"
for panel in uniform grow7
do
    run sampleaudit_knot "$panel"
    mapfile -t knot_args < <(run sampleaudit_knot "$panel" --args)
    PYTHONPATH=tools "$py" -B -m knotlab check "${knot_args[@]}" > "$here/sampleaudit_knot_${panel}.json"
done
run regrow_audit --pilot --output "$here/regrow_pilot.json"
run regrow_audit --output "$here/regrow.json"
