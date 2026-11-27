#!/usr/bin/env bash
# Replay the finite recount and its controls sequentially from any directory.
set -euo pipefail
ref=$(cd "$(dirname "$0")" && pwd)
cd "$ref/../../.."
py="$PWD/.venv/bin/python"
export TMPDIR="$ref" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
ulimit -v 3000000
run() { "$py" -B "$ref/$1.py" "${@:2}"; }
g++ -pipe -std=c++17 -O3 -march=native -Wall -Wextra "$ref/read_engine.cpp" -o "$ref/read_engine"
run record_audit --pilot
run record_audit
run witness_checks --pilot
run witness_checks --out "$ref/witness_checks.json"
run read_recount --pilot 206/0,15/1,5260/2,2485/2,420/2 --out read_pilot.json
run read_recount --chunk 0/100 --signed-spool --timing
run read_recount --chunk 0/1 --signed-spool
run read_recount --summarize 1
run read_bond_controls --small
run read_bond_controls
run read_pattern_checks --smoke --benchmark 2000 > /dev/null
run read_pattern_checks --benchmark 2000 10000 41256 > "$ref/read_pattern_controls.json"
run locality_check --pilot
run locality_check
run locality_check --all-bonds --pilot
run locality_check --all-bonds
run role_controls --pilot
run role_controls
run alternative_read --controls --limit 1 "$ref/read_all_bonds_5260_2.json.gz" --output "$ref/alternative_pilot.json"
run alternative_read "$ref/read_all_bonds_420_2.json.gz" --output "$ref/alternative_prior_control.json"
run alternative_read "$ref/read_signed_0.jsonl.gz" --output "$ref/alternative_full.json"
run alternative_signed "$ref/read_signed_0.jsonl.gz" --limit 10 --output "$ref/alternative_signed_pilot.json"
run alternative_signed "$ref/read_signed_0.jsonl.gz" --output "$ref/alternative_signed_full.json"
run omitted_search --structural-only --stage 5260 2 --stage 15 2 --stage 1283 2 --output "$ref/omitted_structural_pilot.jsonl"
run omitted_search --structural-only --output "$ref/omitted_screen.jsonl"
run omitted_search --all-patterns --stage 5260 2 --stage 2439 2 --stage 1283 2 --output "$ref/omitted_exact_pilot.jsonl"
run omitted_search --all-patterns --output "$ref/omitted_stages.jsonl"
run omitted_semantics_replay --pilot > /dev/null
run omitted_semantics_replay > "$ref/omitted_semantics_replay.json"
run omitted_global --pilot
run omitted_global
run omitted_controls --pilot
run omitted_controls
run omitted_summary
run direct_crosscheck --pilot
run direct_crosscheck
run common_source --pilot
run common_source
run read_recount --pilot 426/2 --export-pilot-bonds --out read_positive_426.json
run alternative_witness "$ref/read_all_bonds_426_2.json.gz" --limit 256 --covers 1 --output "$ref/alternative_witness_pilot.json"
run alternative_witness "$ref/read_all_bonds_426_2.json.gz" --output "$ref/alternative_witnesses.json"
run summarize_audit > "$ref/audit_counts.json"
