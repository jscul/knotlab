# MADE-COPIER-20261125-001B, experiment E001: two parts the same as the second pattern, each descended from both

The engine of the frozen ticket `MADE-COPIER-20261125-001B` (commit 733d0edaeb), written from its pre-registration
("PB"), its definitions ("DB") and claim, its data files (`starts_b.json`, `rosters_b.json`), ticket A's frozen texts
and `starts.json`, and the fold study's and the shared definitions. The growth is the fold study's engine and the
readings both tickets use are ticket A's engine (`experiments/MADE-COPIER-20261125-001A/.../mc.py`), both imported and
not changed; the fold engine's guard limits are multiplied by ten at import (DB 3.9). Every reading where the text left a
choice is in [deviations.md](deviations.md), written before the run it affects. `contract.json` and `identity.json` are
the study's own files and are not changed here.

## Files

| File | What it holds |
| --- | --- |
| `mcb.py` | ticket B's readings: starts (DB 2.3's builder), exact form classes, descents, how a set of knots ended |
| `cb.py` | result files, memory cap, log |
| `test_mcb.py` | unit tests: the builder against the 343 listed starts, forms against brute force, descents, the renaming check |
| `b4.py` | run B4, the renaming check (PB1) |
| `b5.py` | run B5: F1, the roster statement, the marked start roster, the knot laws until a closing, the made-knot statement (PB2 to PB5, PB8) |
| `bg.py` | run BG (PB16) and run B0 (PB17) |
| `b1.py` | runs B1 (`--set main`) and B2 (`--set other`, `--set hold`), arm 1 |
| `b3.py` | run B3, arm 2 (MET) |
| `replays_b.py` | the listings behind the differences from the disclosed numbers |
| `analyze_b.py`, `report_b.py` | `summary.json`, `summary.md` |

Results: `artifacts/MADE-COPIER-20261125-001B/MADE-COPIER-20261125-001B-E001_two_from_both/`.

## How to run

Interpreter: `/home/jscul/p-vs-np-contact-first/.venv/bin/python`, in this folder, with `-B`; each worker caps its address
space at 7 GB, and the runs were started under `ulimit -v 8000000`.

| Order | Command | Result file | Time here |
| --- | --- | --- | --- |
| 1 | `python -B test_mcb.py` | `test_mcb.json` | seconds |
| 2 | `python -B bg.py` | `bg.json` | seconds |
| 3 | `python -B b5.py --procs 3` | `b5.jsonl.gz` | 1 minute |
| 4 | `python -B b4.py --procs 4` | `b4.jsonl.gz` | 5 minutes |
| 5 | `python -B b1.py --procs 4 --set main` | `b1.jsonl.gz` | 6 minutes |
| 6 | `python -B b1.py --procs 3 --set other`, `--set hold` | `b2_other.jsonl.gz`, `b2_hold.jsonl.gz` | 2 minutes each |
| 7 | `python -B b3.py --procs 8` (the registered run; it did not fit the hour, deviations 30 to 33), run in four parts: | | |
| 7a | the first part, `python -B b3.py --procs 8`, stopped at 80 minutes | `b3.jsonl.gz` (8 jobs) | 80 minutes |
| 7b | `python -B b3.py --procs 1 --small --out b3_small.jsonl.gz`, stopped at 32 minutes | `b3_small.jsonl.gz` (12 jobs) | 32 minutes |
| 7c | `python -B b3.py --procs 8 --skip-done b3.jsonl.gz,b3_small.jsonl.gz --budget 420 --out b3_cut.jsonl.gz` (the cut, dev 32), stopped at 56 minutes | `b3_cut.jsonl.gz` (48 jobs) | 56 minutes |
| 7d | `python -B b3.py --procs 4 --skip-done b3.jsonl.gz,b3_small.jsonl.gz,b3_cut.jsonl.gz --budget 420 --iso-seconds 10 --hash-above 24 --out b3_cut2.jsonl.gz` (dev 33) | `b3_cut2.jsonl.gz` (4 jobs) | 10 minutes |
| 8 | `python -B replays_b.py` | `replays_b.json` | seconds |
| 9 | `python -B analyze_b.py` then `python -B report_b.py` | `summary.json`, `summary.md` | seconds |

The gate (PB1 to PB4, PB16) passed before B1, B2 and B3.

B3 is cut (deviations 32): in each job ticket A's twelve designs and the alone runs are read in full, and the 256
starts of DB 2 in their registered order for 7 minutes; the starts not reached are "not run", counted per job in
`summary.json` ("_b3 the cut"), and never read as negatives. In the four jobs of the fourth part, parts of more than 24
members are classed by invariants and hash alone and each other exact form test is limited to 10 processor seconds
(deviations 33); no verdict reads a form of more than 6 members.

## Post-freeze

Deviations 27, added after the freeze: wider numberings for every case of arm 2 (MET) that passes the renamings
registered for its design, reported in a file of its own. No run of arm 2 has two parts the same as Y each descended
from both (with X and Y of different kinds, or on ticket A's designs), so there is no case to number and nothing was
run; that is recorded in deviations 27 and in the post-freeze file `post_freeze_numberings.json` (written by
`analyze_b.py`). Arm 1 has no taking rule and
is covered by DB 7's renaming statement, checked in B4.
