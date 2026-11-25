# MADE-COPIER-20261125-001A, experiment E001: the engine and its runs

The engine of the frozen study `MADE-COPIER-20261125-001A` (frozen in commit 5ccb89fd87), written from the
pre-registration ("P"), the definitions ("D"), the claim, the owner's arm and the three data files of
`research/MADE-COPIER-20261125-001A/`, and the fold study's and the shared definitions. The growth is the fold
study's engine (`experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/`:
`pm.py`, `knots.py`, `paired.py`), imported and not edited. Every reading where the text left a choice is in
[deviations.md](deviations.md), with the place in the text, written before the run it affects; items 20 and 47 were
written after a first pass of the run they affect and before it was redone. The gate was run before the engine's
last changes; the independent check reran it on the final code and got identical files.

`contract.json` and `identity.json` are the study's own files and are not changed here.

## Files

| File | What it holds |
| --- | --- |
| `mc.py` | the readings: starts and renamings, descents, tie classes, form, built structure, values, the owner's arm |
| `common.py` | result files, memory cap, log |
| `test_mc.py` | unit tests of the new readings against brute force and hand-built structures |
| `gate.py` | run G and run R: P0, P14, P4, the third-pattern starts |
| `run1.py` ... `run6.py`, `runO.py` | the registered runs 1 to 6 and O |
| `run2_exchanged_alone.py` | X alone and Y alone for made-2-exchanged (deviations 44) |
| `check_p5.py`, `check_p20.py` | P5's first clause; P20's two clauses |
| `replay.py` | the birth-by-birth replays of the disagreements with the disclosed numbers |
| `run4_fails.py` | run 4's drawn histories with two, drawn again, with every failing knot listed (P10; dev 50) |
| `run7_numberings.py` | **post-freeze** (dev 51): every case passing the registered renamings, under 4n numberings |
| `analyze.py` | every prediction's verdict from the result files: `summary.json` |
| `report.py` | `summary.md` from `summary.json` |

Results are written to `artifacts/MADE-COPIER-20261125-001A/MADE-COPIER-20261125-001A-E001_made_copier/`.

## How to run

The interpreter is the workspace's `.venv` (`/home/jscul/p-vs-np-contact-first/.venv/bin/python`); every command is run
in this folder with `-B`. Each worker caps its own address space at 6 GB (`resource.setrlimit`); the longer runs were
started under `ulimit -v 8388608`. `--procs` sets the number of worker processes.

| Order | Command | Result files | Time here |
| --- | --- | --- | --- |
| 1 | `python -B test_mc.py` | `test_mc.json` | seconds |
| 2 | `python -B gate.py fold`, then `ties`, `same`, `controls`, `third`, `record` | `gate_*.json` | under a minute each |
| 3 | `python -B run1.py --procs 3` (`--append` resumes) | `run1.jsonl.gz` | about 15 minutes |
| 4 | `python -B run4.py replay` | `run4_replay.json` | seconds |
| 5 | `python -B run2.py --procs 4` (`--append` resumes) | `run2.jsonl.gz` | about 15 minutes |
| 6 | `python -B run2_exchanged_alone.py` | `run2_exchanged_alone.jsonl` | 20 seconds |
| 7 | `python -B run3.py --procs 2` | `run3.jsonl.gz` | 2 minutes |
| 8 | `python -B run4.py every --procs 2` | `run4.jsonl` | hours (see below) |
| 9 | `python -B run5.py cases`, `cases3`, `lists`, `iv`, `form` (each `--procs 2`) | `run5_*.jsonl`, `run5_form.jsonl.gz` | seconds to about an hour |
| 10 | `python -B run6.py --procs 2` | `run6.jsonl.gz` | 4 minutes |
| 11 | `python -B runO.py --procs 2` | `runO.jsonl.gz` | under a minute |
| 12 | `python -B check_p5.py`, `python -B check_p20.py`, `python -B replay.py` | `check_p5.json`, `check_p20.json`, `replays.json` | a minute |
| 13 | `python -B run4_fails.py --procs 4` | `run4_fails.json` | a minute |
| 14 | **post-freeze**: `python -B run7_numberings.py` (after run 5's cases) | `run7_numberings.json` | seconds |
| 15 | `python -B analyze.py` then `python -B report.py` | `summary.json`, `summary.md` | seconds |

The gate (P0, P14) passed before any other run; the take lists were replayed (P8a) before run 4's draws. Run 5's
`cases`, `lists` and `iv` read run 2's result file; `cases3` and run 6 read run 3's.

Run 4 is the long one: under CAP-3(CANCEL-OFFSHOOT) every design has more than 60,000 histories, so each enumeration
first establishes that (a lower bound, dev 49) and then draws 20,000; the longest took about an hour on one process.
It was resumed three times (`--append`, devs 46, 48, 49); each row is one complete enumeration.

`run7_numberings.py` and its file are **post-freeze** (dev 51): outside the registered runs, on the coordinator's
instruction; nothing registered depends on them.
