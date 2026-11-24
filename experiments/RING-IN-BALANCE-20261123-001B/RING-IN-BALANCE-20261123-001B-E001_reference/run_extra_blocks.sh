#!/bin/bash
# Complete the three census blocks that passed the runner's 1 GB case limit (deviations.md B14), one process at a
# time, each under ulimit -v 12000000 and timeout 1200.  Heavy starts (one ordinary-law run that explodes in the round
# that would pass the bound) get a process of their own with child limits 10 GB / 1,080 s; the others 10 GB / 240 s.
cd "$(dirname "$0")"
PY=../../../.venv/bin/python
LOG=../../../artifacts/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference/extra_blocks.log
run() {  # case range sec
  ( ulimit -v 12000000; timeout 1200 $PY -B -u extra_blocks.py --cases $1 --starts $2 --law-gb 10 --law-sec $3 ) >> $LOG 2>&1 \
    || echo "FAILED: $1 $2 (exit $?)" >> $LOG
}
run n6-b0032 0-37 240;   run n6-b0032 38-38 1080;  run n6-b0032 39-47 240;   run n6-b0032 48-48 1080;  run n6-b0032 49-199 240
run n6-b0065 0-31 240;   run n6-b0065 32-32 1080;  run n6-b0065 33-61 240;   run n6-b0065 62-62 1080;  run n6-b0065 63-199 240
run n6-b0152 0-111 240;  run n6-b0152 112-112 1080; run n6-b0152 113-113 1080; run n6-b0152 114-114 1080; run n6-b0152 115-199 240
echo "ALL DONE" >> $LOG
