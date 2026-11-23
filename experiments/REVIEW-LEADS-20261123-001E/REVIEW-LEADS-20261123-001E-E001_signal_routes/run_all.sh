#!/bin/bash
# Formal run order for REVIEW-LEADS-20261123-001E-E001 (run from anywhere).  Every command is limited to
# ten minutes of wall clock and 12 GB of address space; outputs go to the artifacts folder.
cd /home/jscul/p-vs-np-contact-first || exit 1
EXP=experiments/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes
OUT=artifacts/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes
LOG=$OUT/logs
mkdir -p $LOG
: > $LOG/status.txt
sha256sum $EXP/*.py > $LOG/code_sha256.txt
run() {  # name, then the script and its arguments
  name=$1; shift
  /usr/bin/time -v timeout 600 prlimit --as=12884901888 .venv/bin/python -u -B "$@" > $LOG/$name.log 2>&1
  code=$?
  echo "$name exit $code" >> $LOG/status.txt
  return $code
}
# 1. the gate comes first; nothing else runs unless it passes
run gate $EXP/gate.py || { echo "gate failed"; exit 1; }
# 2. R1 holdings
for g in source clock stall closing concealed; do run r1_$g $EXP/r1_holdings.py --group $g & done; wait
for h in explosive_00 explosive_04 explosive_13; do for law in parity nae; do run r1_${h}_$law $EXP/r1_holdings.py --history $h --law $law & done; done; wait
# 3. R2 values
for g in source clock stall closing concealed; do run r2_$g $EXP/r2_values.py --group $g & done; wait
for law in parity nae; do run r2_explosive_$law $EXP/r2_values.py --group explosive --law $law & done; wait
# 4. R3 allocations
run r3_seven_parity $EXP/r3_allocations.py --structure seven --law parity --sample-step2 200 &
run r3_seven_nae $EXP/r3_allocations.py --structure seven --law nae --sample-step2 200 &
run r3_clock_parity $EXP/r3_allocations.py --structure clock --law parity --sample-step2 200 &
run r3_clock_nae $EXP/r3_allocations.py --structure clock --law nae --sample-step2 200 &
wait
run r3_stall_parity $EXP/r3_allocations.py --structure stall --law parity &
run r3_stall_nae $EXP/r3_allocations.py --structure stall --law nae &
run r3_clock_parity_beyond_cap $EXP/r3_allocations.py --structure clock --law parity --beyond-cap &
run r3_clock_nae_beyond_cap $EXP/r3_allocations.py --structure clock --law nae --beyond-cap &
run r3_minimal $EXP/minimal_start.py &
wait
# 5. R4 groups, 6. R5 order
run r4_groups $EXP/r4_groups.py &
run r5_order $EXP/r5_order.py &
wait
# 6b. replays for the table of routes (in the recorded session this ran separately, after the five checks)
run routes_evidence $EXP/routes_evidence.py
# 7. tables
.venv/bin/python -B $EXP/summarize.py > $LOG/summary_tables.md 2>&1
cat $LOG/status.txt
