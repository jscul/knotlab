#!/usr/bin/env bash
# Run the jobs listed in a file (one "script.py args..." per line, relative to this folder) from the repository root,
# at most six at once, each as: timeout 600 prlimit --as=12884901888 .venv/bin/python -B <script> <args>, with
# OMP/OPENBLAS/MKL threads set to 1.  Each job's output goes to <artifacts>/logs/<jobs file stem>_<line number>.log, and
# one line per finished job (exit status, seconds, command) is appended to <artifacts>/logs/<jobs file stem>_runs.log.
# usage (repository root): bash experiments/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/run_jobs.sh <jobs file>
set -u
HERE="experiments/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread"
ART="artifacts/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread"
JOBS="$1"
STEM="$(basename "$JOBS" .txt)"
mkdir -p "$ART/logs"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
grep -n -v '^\s*$' "$JOBS" | grep -v '^[0-9]*:#' | while IFS= read -r line; do echo "$line"; done | \
  xargs -P 6 -I{} bash -c '
    n="${1%%:*}"; cmd="${1#*:}"
    t0=$(date +%s)
    timeout 600 prlimit --as=12884901888 .venv/bin/python -B '"$HERE"'/$cmd > '"$ART"'/logs/'"$STEM"'_$n.log 2>&1
    st=$?
    echo "status=$st seconds=$(( $(date +%s) - t0 )) line=$n cmd=$cmd" >> '"$ART"'/logs/'"$STEM"'_runs.log
  ' _ {}
