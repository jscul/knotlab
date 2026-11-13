#!/bin/bash
# part 6, which the first launcher skipped (its list had no final newline), split into four instances
cd /home/jscul/p-vs-np-contact-first
C=experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex
set -- 53 102 152 208 248 276 309 348 387 428 441 481 540 579 649 692 743 785 822 863 900 914 938 981 1051 1118 1156 1194 1242 1286 1308 1335
a=(); b=(); c=(); d=(); k=0
for x in "$@"; do case $((k % 4)) in 0) a+=($x);; 1) b+=($x);; 2) c+=($x);; 3) d+=($x);; esac; k=$((k+1)); done
.venv/bin/python -B $C/run_true.py --workers 3 --smax 12 --seconds-limit 1100 --memory-mb 2500 --output true_rates_part6a.jsonl --only ${a[@]} > $C/run_part6a.log 2>&1 &
.venv/bin/python -B $C/run_true.py --workers 3 --smax 12 --seconds-limit 1100 --memory-mb 2500 --output true_rates_part6b.jsonl --only ${b[@]} > $C/run_part6b.log 2>&1 &
.venv/bin/python -B $C/run_true.py --workers 3 --smax 12 --seconds-limit 1100 --memory-mb 2500 --output true_rates_part6c.jsonl --only ${c[@]} > $C/run_part6c.log 2>&1 &
.venv/bin/python -B $C/run_true.py --workers 3 --smax 12 --seconds-limit 1100 --memory-mb 2500 --output true_rates_part6d.jsonl --only ${d[@]} > $C/run_part6d.log 2>&1 &
wait
