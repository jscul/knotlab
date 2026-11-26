#!/bin/bash
# drive_xt.sh: the extension's tables (README.md, "The extension"): starts where forbidding answers a reader's setting,
# and the first 200 starts of each size as controls (table_starts.json), nine processes
cd "$(dirname "$0")"
for K in E1 E2 M1; do for P in 0 1000 2000; do
  /home/jscul/p-vs-np-contact-first/.venv/bin/python -B forbid.py run "$K" "$P" "$((P + 1000))" --extension --starts table_starts.json > "xrun_${K}_${P}.jsonl" &
done; done
wait
