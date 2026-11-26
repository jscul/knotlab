#!/usr/bin/env bash
# Rebuild the independent referee tables, one process at a time.
set -euo pipefail
cd -- "$(dirname -- "$0")"
P="$PWD/../../../.venv/bin/python"
export PYTHONPATH="$PWD/../../../tools"
ulimit -v 2400000
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
"$P" -B witness.py --pilot
"$P" -B witness.py
"$P" -B joint_check.py --pilot
"$P" -B joint_check.py
"$P" -B record.py --pilot
"$P" -B record.py
"$P" -B frozen_recount.py --limit-per-size 12 --out frozen_recount_pilot.json
"$P" -B frozen_recount.py --out frozen_recount_results.json
for part in funded sign long; do
    "$P" -B built_baselines.py --part "$part" --pilot > /dev/null
    "$P" -B built_baselines.py --part "$part" > "built_baselines_${part}.json"
done
"$P" -B built_witness.py --compare-growth --rounds 1 > /dev/null
"$P" -B built_witness.py --compare-growth --rounds 8 --output built_witness.json
"$P" -B built_search.py --compare-growth --limit 1 > /dev/null
"$P" -B built_search.py --compare-growth --output built_search.json
"$P" -B periodic.py --pilot
"$P" -B periodic.py
"$P" -B extended_rounds.py --pilot-limit 8 > extended_pilot.json
"$P" -B extended_rounds.py > extended_results.json
"$P" -B extended_witness.py --pilot > extended_witness_pilot.json
"$P" -B extended_witness.py > extended_witness.json
for group in archive rings; do
    "$P" -B moves.py "$group" --pilot --output "moves_${group}_pilot.json"
    "$P" -B moves.py "$group" --output "moves_${group}.json"
done
"$P" -B moves.py original-rings --pilot --output moves_original_rings_pilot.json
"$P" -B moves.py original-rings --output moves_original_rings.json
cases=(5_5_joins2_inside1_copies2_rings 5_5_joins1_inside0_copies1_except_joins
       4_4_joins1_inside1_copies2_rings 5_7_joins1_inside0_copies1_except_joins)
"$P" -B moves.py rings --rounds 3 --verbose --case "${cases[0]}" --output moves_deep_pilot.json
"$P" -B moves.py rings --rounds 3 --verbose --case "${cases[@]}" --output moves_deep.json
"$P" -B moves_certificates.py --pilot --output moves_certificates_pilot.json
"$P" -B moves_certificates.py --output moves_certificates.json
"$P" -B moves.py candidate --verbose --rounds 4 --pilot --output moves_sample_pilot.json
"$P" -B moves.py candidate --verbose --rounds 4 --output moves_sample.json
