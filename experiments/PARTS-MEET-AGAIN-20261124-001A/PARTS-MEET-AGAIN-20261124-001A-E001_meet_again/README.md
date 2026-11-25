# PARTS-MEET-AGAIN-20261124-001A-E001: how to rerun

The engine and every script were written from the frozen texts (`research/RING-IN-BALANCE-20261123-001/definitions.md`,
`research/PARTS-MEET-AGAIN-20261124-001/definitions.md`, `research/PARTS-MEET-AGAIN-20261124-001A/preregistration.md`).
Readings are in `deviations.md`. `contract.json` and `identity.json` are frozen and were not touched.

Files: `pm.py` (the engine: structures with any number of holders, one complete round with taking, the laws, the guard
and bounds), `knots.py` (parity by ranks and by kernel, not-all-equal directly and by the birth method, brute force),
`paired.py` (the paired test: pairs, trace, B(i), B(ii), masked runs, way, verdict, all-pairs checks), `common.py`
(paths, memory cap, output), `test_engine.py` (unit tests on hand-built structures), `gate.py` (run G), `runs.py`
(runs 1, 3, 7 and the supplementary CARRY run), `enum_choices.py` (run 2), `special.py` (runs 4, 5, 6), `replays.py`
(birth-by-birth listings of the disagreements), `analyze.py` and `report.py` (verdicts, `summary.json`, `summary.md`).

Outputs go to `artifacts/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/`. Every script
caps its own address space (`resource.setrlimit`, default 6 to 8 GB per process).

From this folder, with `PY=/home/jscul/p-vs-np-contact-first/.venv/bin/python`:

| Step | Command | Time seen (24-core host, other work running) |
| --- | --- | --- |
| unit tests | `$PY -B test_engine.py` | < 1 s |
| G, ring engine | `$PY -B gate.py ring --chunk i/6` for i = 0..5 (and `--chunk 4/6 --registered-only`) | 4 to 400 s per chunk |
| G, rule R and rule Q | `$PY -B gate.py rq --chunk i/3` for i = 0..2 | about 15 s each |
| G, brute force | `$PY -B gate.py brute` | < 1 s |
| G, birth method | `$PY -B gate.py birth` | 5 s |
| run 1 | `$PY -B runs.py run1 --procs 7 --mem 6` | 488 s (one job 387 s) |
| run 3 | `$PY -B runs.py run3 --procs 5 --mem 6` | 250 s |
| run 7 | `$PY -B runs.py run7 --procs 1 --mem 6` | 14 s |
| CARRY, other reading | `$PY -B runs.py carry-alt --procs 1 --mem 6` | 3 s |
| run 2, first part (stopped after 161 enumerations, deviations 40) | `$PY -B enum_choices.py --procs 6 --mem 6` | 36 min |
| run 2, the rest | `$PY -B enum_choices.py --procs 8 --mem 6 --skip-done run2.jsonl --out run2b.jsonl` | long: see `summary.md` |
| run 4 | `$PY -B special.py run4 --mem 6` | 9 s |
| run 5 | `$PY -B special.py run5 --procs 2 --mem 6` | 2 min |
| run 6 | `$PY -B special.py run6 --mem 6` | < 1 s |
| replays | `$PY -B replays.py` | 2 s |
| verdicts | `$PY -B analyze.py && $PY -B report.py` | 10 s |

Run 5 reads `run1.jsonl.gz` and `run3.jsonl.gz`; `analyze.py` reads every output.
