#!/bin/bash
# Launch 8 chunks of one command in parallel and wait; prints the wall time.  Usage:
#   ff_launch.sh <label> <script.py> <args...>       (each process gets --chunk i/8)
cd "$(dirname "$0")"
PY=/home/jscul/p-vs-np-contact-first/.venv/bin/python
OUT=/home/jscul/p-vs-np-contact-first/artifacts/FOLLOWS-THE-FORM-20261125-001A/FOLLOWS-THE-FORM-20261125-001A-E001_place_fixed_form_changed
mkdir -p "$OUT/logs"
label=$1; shift
t0=$(date +%s.%N)
echo "$label start $(date -u +%FT%TZ)" >> "$OUT/logs/walltime.log"
pids=()
for i in 0 1 2 3 4 5 6 7; do
  "$PY" -B "$@" --chunk $i/8 > "$OUT/logs/${label}_$i.log" 2>&1 &
  pids+=($!)
done
echo "$label pids ${pids[*]}" >> "$OUT/logs/walltime.log"
rc=0
for p in "${pids[@]}"; do wait $p || rc=1; done
t1=$(date +%s.%N)
echo "$label end $(date -u +%FT%TZ) wall $(echo "$t1 - $t0" | bc) s rc $rc" >> "$OUT/logs/walltime.log"
echo "$label wall $(echo "$t1 - $t0" | bc) s rc $rc"
