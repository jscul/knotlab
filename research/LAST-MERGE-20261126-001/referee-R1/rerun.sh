#!/usr/bin/env bash
# Repeat the checks serially, with a timed small run before each full comparison.
set -euo pipefail
folder=$(cd -- "$(dirname -- "$0")" && pwd)
cd -- "$folder/../../.."
py=.venv/bin/python
export PYTHONPATH=tools OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 3145728

run() {
    local script=$1
    shift
    time "$py" -B "$folder/$script.py" "$@"
}

for script in provenance sample_check admission overlap; do
    run "$script" --pilot
    run "$script"
done
run recount --pilot 100
run recount
run fitting --limit 50 --output "$folder/fitting_pilot.json"
run fitting --output "$folder/fitting.json"
run falsifiability --limit 100 --output "$folder/falsifiability_pilot.json"
run falsifiability --output "$folder/falsifiability.json"
run short_runs --pilot --output "$folder/short_prefix_pilot.json"
run short_runs --output "$folder/short_prefix.json"

run regrowth --selection pilot --output "$folder/regrowth_pilot.json"
run regrowth --selection stratified --output "$folder/regrowth.json"
run regrowth --extend --selection pilot --output "$folder/regrowth_extension_pilot.json"
run regrowth --extend --selection all --reuse-extension-pilot "$folder/regrowth_extension_pilot.json" \
    --output "$folder/regrowth_extension.json"
run short_runs --extension "$folder/regrowth_extension.json" --pilot --output "$folder/short_extension_pilot.json"
run short_runs --extension "$folder/regrowth_extension.json" --output "$folder/short_extension.json"
run coverage --pilot
run coverage
