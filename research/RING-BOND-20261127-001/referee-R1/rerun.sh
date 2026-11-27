#!/usr/bin/env bash
# From the repository root. Give --pilots-only for the short checks.
set -euo pipefail
ulimit -v 2621440
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
r=research/RING-BOND-20261127-001/referee-R1
mode=${1:-all}
case "$mode" in all|--pilots-only) ;; *) exit 2 ;; esac

run() { .venv/bin/python -B "$r/$1.py" "${@:2}"; }
pilot() { time run "$@" >/dev/null; }
full() { if [[ "$mode" == all ]]; then time run "$@" >/dev/null; fi; }

pilot sources_audit --pilot
full sources_audit --out "$r/sources_audit.json"
pilot sample_scope 1
full sample_scope 1000 --out "$r/sample_scope.json"

for part in growth swaps checks local full; do
    pilot ring_verify --part "$part" --pilot
    full ring_verify --part "$part" --out "$r/ring_$part.json"
done
for part in growth ternary orbits; do
    pilot sym_ring --part "$part" --pilot
    full sym_ring --part "$part" --out "$r/sym_$part.json"
done
for part in survey universe selection controls; do
    case "$part" in universe) f=all_rigid ;; selection) f=selected ;; *) f="$part" ;; esac
    pilot sym_selection --part "$part" --pilot
    full sym_selection --part "$part" --out "$r/sym_$f.json"
done

for cap in 4 5; do
    pilot census_replay --cap "$cap" --ranks 1 1695 3572 5273
    full census_replay --cap "$cap" --out "$r/census_heldout$cap.json"
done
for part in targeted alternatives population; do
    case "$part" in
        targeted) pilot census_controls "$part" --limit 1 ;;
        population) pilot census_controls "$part" --ranks 1 477 1695 3572 5273 7000 ;;
        alternatives) pilot census_controls "$part" --ranks 1 1695 3572 5273 ;;
    esac
    full census_controls "$part" --out "census_$part.json"
done
pilot census_strict --ranks 1 477 1695 3572 5273 7000 --out census_strict_pilot.json
full census_strict --out census_strict.json
pilot census_birth --ranks 1 1695 3572 5273 --out census_birth_pilot.json
full census_birth --out census_birth.json

pilot parity_replay --indices 1 --out "$r/parity_replay_pilot.json"
full parity_replay --selection completed --out "$r/parity_replay_results.json"
pilot parity_replay --selection unrun --indices 3145 4239 5584 6398 7050 --out "$r/parity_extension_pilot.json"
full parity_replay --selection unrun --out "$r/parity_extension.json"
pilot parity_checks --pilot --out "$r/parity_checks_pilot.json"
full parity_checks --out "$r/parity_checks_results.json"
if [[ "$mode" == all ]]; then
    export PYTHONPATH=tools
    .venv/bin/python -B -m knotlab check --cnf 'a b c; a ~b ~c; ~a b ~c; ~a ~b c' \
        --loops a b --contact c --json > "$r/parity_knot_pilot.json"
    formula=$(jq -r '.["a grown parity relation needs a born law"]["holder CNF"]' "$r/parity_checks_results.json")
    .venv/bin/python -B -m knotlab check --cnf "$formula" --loops a b --contact c \
        --witnesses x0 x1 x2 x3 x6 x7 x12 x13 --json > "$r/parity_knot.json"
fi

pilot collapse_check controls 5
full collapse_check controls 210 --out "$r/control_counts.json"
pilot collapse_check nae 2
full collapse_check nae 200 --out "$r/collapse_nae.json"
pilot collapse_check parity 1
full collapse_check parity 6 --out "$r/collapse_parity.json"
full collapse_check parity 200 --out "$r/collapse_parity_extended.json"

pilot layer_recount --pilot
full layer_recount
pilot layer_witness --pilot
full layer_witness
pilot layer_ring_search --pilot
full layer_ring_search --through 4
pilot carrier_shrink 64
full carrier_shrink 4096 --out "$r/carrier_shrink.json"
pilot source_deletions 8192
full source_deletions 262144 --out "$r/source_deletions.json"
pilot ring_upper_deletions 256
full ring_upper_deletions 8192 --out "$r/ring_upper_deletions.json"

# Look up the historical index as in sources_notes.md. The current index can grow.
if [[ "$mode" == all ]]; then
    jq -r '.[].query' "$r/sources_prior.json" | while IFS= read -r query; do
        .venv/bin/python -B scripts/track.py objects "$query" --until 2026-11-27 \
            --exclude RING-BOND-20261127-001 --limit 3 --deep --json >/dev/null
    done
fi
