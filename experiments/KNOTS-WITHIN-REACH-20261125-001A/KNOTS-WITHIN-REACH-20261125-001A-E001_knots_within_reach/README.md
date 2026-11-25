# KNOTS-WITHIN-REACH-20261125-001A-E001: how to rerun

How many knots lie within r holder steps of a knot in the whole history a law makes (H), the roster count at one round
(P), the gate of "the same power from every knot examined", the start-by-start table, the laws with a taking rule, and the
growing end's readings between loose distinctions. The code was written from the frozen texts (the shared definitions of
`RING-IN-BALANCE-20261123-001`, the definitions of `PARTS-MEET-AGAIN-20261124-001`, this epic's claim, definitions and
pre-registration with its data files) by a helper that had not seen the drafter's prototype. Readings taken where the
texts leave a choice, and the places where a frozen text was found short, are numbered in `deviations.md`.
`contract.json` and `identity.json` are frozen and were not touched.

The fold study's engine (`experiments/PARTS-MEET-AGAIN-20261124-001A/.../pm.py` and `knots.py`) is imported unchanged;
its SHA-256 is checked at every import. Its guard is multiplied by ten at import, as KD 7.4 says (deviations 1).

Files: `kwr.py` (paths, the laws, seeds, the growth driver with exact rollback of a guard-stopped round, the holder,
parent and witnessed graphs and the counts), `readings.py` (POWER and the m-phase form, LINREC, BOUND, RATIO, the
precedence, earlier segments, the doubling reading, the gate and its spread), `test_readings.py` (unit tests on
hand-written sequences), `ge.py` (exact counts of allowed states by contraction in integers, the pair readings, the
history weighting, the order comparisons, the member and pair shuffles), `ktest.py` (the graph forms of the parity knot
test for structures with at most two holders), `enum4b.py` (the enumeration of every choice and the numberings),
`run0.py` to `run5.py` and `run4c.py` (the runs), `check_known3.py` (a labelled replication of PR Known 3),
`report.py` (verdicts, `summary.json`, `summary.md`, listings).

Outputs go to `artifacts/KNOTS-WITHIN-REACH-20261125-001A/KNOTS-WITHIN-REACH-20261125-001A-E001_knots_within_reach/`.
Every process caps its own address space at 6 GB. From this folder, with `PY=/home/jscul/p-vs-np-contact-first/.venv/bin/python`:

| Step | Command | Wall time seen (24 cores, load 20 to 37 from other work, 4 processes) |
| --- | --- | --- |
| unit tests | `$PY -B run0.py tests` | < 1 s |
| run 0 controls | `$PY -B run0.py controls` | 12 s |
| run 0 checks E, F, R, I, N | `$PY -B run0.py checks` | 6 min |
| run 0 parity graph forms | `$PY -B run0.py ktest` | 11 s |
| run 0 probe for run 4b | `$PY -B run0.py probe` | 7 min (capped at 10) |
| run 2's small starts recomputed | `$PY -B run2.py recompute --procs 4` | 40 s |
| run 2 | `$PY -B run2.py run --procs 4` | 12 min |
| run 5 | `$PY -B run5.py run --procs 4`, then `$PY -B run5.py swap --procs 4` | 21 min, 4 min |
| run 1 (the registered prefix, deviations 29) | `$PY -B run1.py run --procs 4 --starts 469` | 36 min |
| run 4 | `$PY -B run4.py run --procs 4` and `$PY -B run4.py base --procs 4` | 11 min, 6 min |
| run 3 (the registered prefix, deviations 33, 34) | `$PY -B run3.py run --procs 6 --limit 1435` | 35 min |
| run 4c | `$PY -B run4c.py run --procs 2` | 2 min |
| check of PR Known 3 (outside the registered runs) | `$PY -B check_known3.py` | 1 min |
| verdicts | `$PY -B report.py` (run as the main script: the fold study's folder, first on the import path, has its own `report.py`) | about 2 min |

Every run script resumes: items already in its output file are skipped. Each output record holds the counts themselves
(H per knot examined, births per round, the pairs' integer counts), not only their readings, so that a verdict can be
checked from the raw file.
