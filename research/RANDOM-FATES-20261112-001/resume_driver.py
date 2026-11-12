"""Resume RANDOM-FATES-20261112-001A-E001 after its 4-hour runtime cap, with the frozen task code unchanged.

The registered run (systemd unit rf-a-1794454099) stopped at its cap with 969 of 2,990 runs written. Five runs never finished:
U300 runs 0 to 4, the only ones that compute a minimal contradiction at 300 distinctions (still running after 4 hours). This
driver runs the frozen census.task on the remaining runs:
  --part rest      every unwritten run except U300 runs 0 to 4, appended to runs.jsonl (as census.run would);
  --part u300core  only U300 runs 0 to 4, written to runs_u300core.jsonl, in a separate long-running unit (LONG_RUNNING
                   RANDOM-FATES-A2), folded in when it finishes.
Run from the repository root with the workspace's .venv python.
"""

import json
import os
import sys
import time
from multiprocessing import Pool

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "experiments", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census"))
sys.argv = [sys.argv[0]] + sys.argv[1:]
import census as C  # noqa: E402

CORE300 = {("U300", r) for r in range(C.U_CORES[300])}


def lab_of(kind, p):
    return "U" + str(p) if kind == "U" else ("T" if kind == "T" else C.label(kind, p))


def main():
    part = sys.argv[sys.argv.index("--part") + 1]
    workers = int(sys.argv[sys.argv.index("--workers") + 1])
    done = set()
    for name in ("runs.jsonl", "runs_u300core.jsonl"):
        path = os.path.join(C.OUT, name)
        if os.path.exists(path):
            for line in open(path):
                r = json.loads(line)
                done.add((r["label"], r["run"]))
    specs = [s for s in C.all_specs() if (lab_of(s[0], s[1]), s[2]) not in done]
    if part == "rest":
        specs = [s for s in specs if (lab_of(s[0], s[1]), s[2]) not in CORE300]
        out = os.path.join(C.OUT, "runs.jsonl")
    else:
        specs = [s for s in specs if (lab_of(s[0], s[1]), s[2]) in CORE300]
        out = os.path.join(C.OUT, "runs_u300core.jsonl")
    specs.sort(key=lambda s: (s[2] >= C.READ_RUNS, -(s[1] if s[0] == "U" else 0)))
    C.log(f"resume {part} {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC: {len(specs)} runs")
    t0 = time.time()
    with Pool(workers) as pool, open(out, "a") as f:
        for i, rec in enumerate(pool.imap_unordered(C.task, specs, chunksize=1)):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if (i + 1) % 100 == 0:
                C.log(f"resume {part}: {i + 1}/{len(specs)} runs, {time.time() - t0:.0f} s")
    C.log(f"resume {part} done {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC, {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
