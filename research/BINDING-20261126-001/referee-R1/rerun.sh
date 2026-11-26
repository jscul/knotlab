#!/usr/bin/env bash
# Run from the repository root. Each full comparison follows a timed subset.
set -euo pipefail
ulimit -v 2097152
p=.venv/bin/python
r=research/BINDING-20261126-001/referee-R1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

simple() {
  "$p" -B "$r/$1.py" --pilot
  "$p" -B "$r/$1.py"
}

alternate() {
  "$p" -B "$r/alternate_moves.py" "$1" --pilot --output "$r/alternate_${2}_pilot.json"
  "$p" -B "$r/alternate_moves.py" "$1" --output "$r/alternate_${2}.json"
}

cut_rounds() {
  local suite=$1
  shift
  "$p" -B "$r/cuts_rounds.py" "$suite" "$@" --pilot --output "cuts_${suite}_pilot.json"
  "$p" -B "$r/cuts_rounds.py" "$suite" "$@" --output "cuts_${suite}.json"
}

simple record_check
"$p" -B "$r/replay_archive.py" --pilot --output "$r/replay_pilot.json"
"$p" -B "$r/replay_archive.py" --output "$r/replay_results.json"
"$p" -B "$r/split_audit.py" --limit-per-set 32 --output "$r/split_audit_pilot.json"
"$p" -B "$r/split_audit.py" --output "$r/split_audit.json"
simple construct_witness
simple construct_born
simple cycle_certificate
simple carrier_check
simple path_carriers
"$p" -B "$r/path_carriers.py" --archive --pilot
"$p" -B "$r/path_carriers.py" --archive
simple path_certificate
alternate witnesses witnesses
alternate positive-control control
alternate recorded-certificate recorded
alternate archive archive
alternate challenge challenge
alternate larger-draws larger
cut_rounds archive --rounds 4 --cap 512
cut_rounds larger --count 256 --rounds 5 --cap 512
cut_rounds witnesses --rounds 6 --cap 1024
simple cuts_construction
simple cuts_changes
simple cuts_three
simple three_parent_certificate
