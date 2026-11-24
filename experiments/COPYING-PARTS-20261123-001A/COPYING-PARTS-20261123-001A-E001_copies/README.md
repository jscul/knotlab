# COPYING-PARTS-20261123-001A-E001: parts that copy themselves

Runs 1 to 6 and the gate of the frozen pre-registration `research/COPYING-PARTS-20261123-001A/preregistration.md`, on
the shared definitions `research/RING-IN-BALANCE-20261123-001/definitions.md`. Every computation uses ticket A's
engine, `experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/engine.py` (SHA-256
2c6eac56...). It is imported, not copied or changed: `cpcommon.py` appends ticket A's folder to `sys.path`, imports only
`engine`, and refuses to run if the engine's SHA-256 differs. Readings: `deviations.md`. Sections C0 to C15 were written
before any run. C16 to C19 were added after the runs and change no computation.

## Files

- `cpcommon.py`: output folder (`COPYING_OUT` overrides it), the starts, the nine laws, two-knot parts and N(t), parts
  that copy themselves.
- `cpcensus.py`: the census of starts of 3 to 5 knots, written again from ticket B's B1, and the reader of the earlier
  census's identities and set-aside flags.
- `gate.py`: the gate. It writes `gate.json` and `trace_two_knot_part.txt`.
- `run1.py` to `run6.py`: runs 1 to 6. They write `run<k>.json`; run 5 also writes `run5_census_check.json` and
  `run5_starts.json.gz` (gzipped, 12.5 MB raw), and run 6 also writes `run6_trace.txt`.
- `summarize.py`: a verdict line for the gate, for P1 to P10 and for the Reported items. It writes `summary.json`.
- `determinism.py`: compares the outputs with a rerun in another folder. It writes `determinism.json`.

Outputs go to `artifacts/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies/`, with one log per
script.

## Commands (from the repository root)

```bash
cd experiments/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies
ART=../../../artifacts/COPYING-PARTS-20261123-001A/COPYING-PARTS-20261123-001A-E001_copies
PY=../../../.venv/bin/python
mkdir -p $ART
ulimit -v 4000000
for s in gate run1 run2 run3 run4 run5 run6 summarize; do
  /usr/bin/time -f "%e s %M KB" timeout 600 $PY -B -u $s.py > $ART/$s.log 2>&1 || echo "$s failed"
done
cat $ART/summarize.log

# optional: run 5's enumeration check alone, and the rate measurement made before run 5
$PY -B -u run5.py --check
$PY -B -u run5.py --measure 60

# determinism: rerun everything into another folder with another hash seed, then compare
RERUN=$ART/rerun_hashseed12345; mkdir -p $RERUN
for s in gate run1 run2 run3 run4 run5 run6 summarize; do
  env COPYING_OUT=$RERUN PYTHONHASHSEED=12345 timeout 600 $PY -B -u $s.py > $RERUN/$s.log 2>&1 || echo "$s failed"
done
RERUN_HASHSEED=12345 $PY -B determinism.py $RERUN && rm -r $RERUN
```

`run5.py` uses 8 processes. Each process is held under the same `ulimit -v`. On 2026-11-23 the scripts took 0.2 s
(gate), 122 s (run 1), 3 s (run 2), 3 s (run 3), 25 s (run 4), 141 s wall (run 5: 1,109 s of computation on 8
processes) and 7 s (run 6). Peak resident memory was at most 206 MB per process. The rerun with PYTHONHASHSEED=12345
gave identical outputs once the timing fields were removed (`determinism.json`).
