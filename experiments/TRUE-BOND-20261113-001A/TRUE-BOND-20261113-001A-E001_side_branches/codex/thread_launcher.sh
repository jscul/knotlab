#!/bin/bash
# the thread's launcher for TRUE-BOND-A1: seven instances of Codex's runner, three workers each, disjoint families
cd /home/jscul/p-vs-np-contact-first
C=experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex
i=0
while read -r line; do
  .venv/bin/python -B $C/run_true.py --workers 3 --smax 12 --seconds-limit 1100 --memory-mb 2500 --output true_rates_part$i.jsonl --only $line > $C/run_part$i.log 2>&1 &
  i=$((i+1))
done < /tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/dw/tb_parts.txt
wait
