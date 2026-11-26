#!/bin/bash
# drive_x.sh MODE: the extension's pre-count (MODE count) or tables (MODE run), nine processes, one per kind and thousand
cd "$(dirname "$0")"
for K in E1 E2 M1; do for P in 0 1000 2000; do
  /home/jscul/p-vs-np-contact-first/.venv/bin/python -B forbid.py "$1" "$K" "$P" "$((P + 1000))" --extension > "x$1_${K}_${P}.jsonl" &
done; done
wait
