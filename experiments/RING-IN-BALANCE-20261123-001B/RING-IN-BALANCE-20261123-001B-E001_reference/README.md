# RING-IN-BALANCE-20261123-001B-E001: what a reference is

Ticket B's runs B1 to B5 (`research/RING-IN-BALANCE-20261123-001B/preregistration.md`, shared definitions in
`research/RING-IN-BALANCE-20261123-001/definitions.md`), on ticket A's engine
(`experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/engine.py`), which is imported,
not copied or changed. Readings where the frozen text left a choice are in `deviations.md` (written before the
registered runs).

## Files

- `bref.py`: shared helpers (engine import, output folder, the census of starts and their canonical forms, the record
  of a run: kind, every return with which members waited, shapes of returning parts, the ordinary-law checks of G).
- `census_count.py`: enumerates the census and checks the registered counts (brute force for 3 and 4 knots, Burnside's
  lemma for every size).
- `b1.py` (B1 and B1's share of B3), `b3_a4.py` (ticket A's A4 rerun for B3), `b4.py` (B4, P6), `b5.py` (B5, P7).
- `job.py`: the census B2 as a job for the shared runner (`scripts/longrun.py`, `docs/tooling/shared-runner.md`).
- `extra_blocks.py`, `run_extra_blocks.sh`: the three census blocks that passed the runner's 1 GB case limit, completed
  outside the runner one process at a time, each run isolated in a child process (deviations.md B14); records in
  `census/extra_blocks.jsonl`. `extra_blocks.py --verify` recomputes finished blocks and compares them with the runner.
- `census_io.py`: loads the census (the runner's records and the extra blocks, merged by block).
- `p3_detail.py`: every census run with a return giving parts off, computed again with every such return listed
  (deviations.md B15); writes `p3_census_detail.json`.
- `summarize.py`: the verdict of G and P1 to P7, with the census tables once the census is complete.

Outputs: `artifacts/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference/` (one JSON and one log
per script; the runner's output directory `census/`).

## Commands (from the repository root)

```bash
cd experiments/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference
ART=../../../artifacts/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference
PY=../../../.venv/bin/python
mkdir -p $ART
ulimit -v 4000000
for s in census_count b1 b3_a4 b4 b5; do
  timeout 600 $PY -B -u $s.py > $ART/$s.log 2>&1 || echo "$s failed"
done
```

The census (from the repository root; prepare, smoke test, then the full run):

```bash
PY=.venv/bin/python
JOB=experiments/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference/job.py
OUTD=artifacts/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference/census
$PY -B scripts/longrun.py launch $JOB --out $OUTD --unit ring-balance-b-census --workers 8 \
  --case-timeout 3600 --case-mem 1G --mem-max 16G --retry timeout,memory,crashed --prepare-only
$PY -B scripts/longrun.py run --out $OUTD --foreground --limit 20     # smoke test (20 of 432 cases)
$PY -B scripts/longrun.py resume --out $OUTD                          # the remaining 412 cases (the thread runs it)
$PY -B scripts/longrun.py wait --out $OUTD
```

Three blocks (n6-b0032, n6-b0065, n6-b0152) passed the runner's 1 GB case limit; they are completed outside the runner
(deviations.md B14), then the census detail for P3 and the verdicts:

```bash
cd experiments/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference
ART=../../../artifacts/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference
PY=../../../.venv/bin/python
( ulimit -v 12000000; timeout 1200 $PY -B -u extra_blocks.py --verify n3-b0000,n5-b0005,n6-b0000,n6-b0200,n6-b0413 ) \
  > $ART/extra_blocks_verify.log 2>&1
./run_extra_blocks.sh                      # 15 processes, one at a time; log in $ART/extra_blocks.log
( ulimit -v 4000000; timeout 600 $PY -B -u p3_detail.py ) > $ART/p3_detail.log 2>&1
( ulimit -v 4000000; timeout 600 $PY -B -u summarize.py ) > $ART/summarize.log 2>&1
```

Run times on 2026-11-23 (one process each, `ulimit -v 4000000`): `census_count` 1.2 s (65 MB), `b1` 56 s (119 MB),
`b3_a4` 82 s (150 MB), `b4` 15 s (107 MB), `b5` 0.4 s (40 MB), `summarize` under 1 s before the census. The census's
smoke test: 20 cases (3,776 starts) in 15 s with 8 workers, 0.2 to 10.8 s per case of 200 starts, peak 32 MB per case.
