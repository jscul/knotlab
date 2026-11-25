# TIME-AS-FOLD-20261125-001A-E001: how to rerun

The engine and every script were written from the frozen texts (SD `research/RING-IN-BALANCE-20261123-001/definitions.md`,
FD `research/PARTS-MEET-AGAIN-20261124-001/definitions.md`, TD `research/TIME-AS-FOLD-20261125-001/definitions.md`, the
claim, and the pre-registration `research/TIME-AS-FOLD-20261125-001A/preregistration.md` with its data files). The
engine of the study of parts that meet again and the ring study's code are imported only by the gates (`tf_gates.py`).
Readings where the texts leave a choice are numbered in `deviations.md`. `contract.json` and `identity.json` are frozen.

Files: `tf_engine.py` (structures with any number of holders, one complete round with taking, the laws, the guard, the
bounds and the limit of process time), `tf_knots.py` (the knot test: parity by ranks and by kernel, not-all-equal by the
birth method and directly, brute force), `tf_series.py` (sameness, series of returns, ticks, clocks, parts given off,
copies), `tf_tests.py` (the tests of a clock and a second part: B(r), B'(r), Ball(r), the masked runs, the test with X
barred, own and joint knots, the lag, the verdicts of TD 4.6), `tf_gates.py` (G1, G2, G3), `tf_runs.py` (runs 1, 2, 3),
`tf_census.py` (their tables and P2, P3, P7, P8, P9), `tf_run4.py` (run 4 and P10), `tf_analyse4.py` (run 4's verdicts,
P1, P5, P6, P12, P15, P16), `tf_run5.py` (runs 5, 5b, 6 and the near-case supplement), `tf_special.py` (P4's round 1),
`tf_run7.py` (the knot test of runs), `tf_unit_knots.py` (the knot tests against brute force), `tf_unit_series.py`
(unit checks of series and tests), `tf_summ5.py` (summaries of runs 5 and 6), `tf_replay.py` (birth-by-birth
listings), `tf_report.py`
(`summary.json`, `summary.md`), `tf_common.py` (paths, memory cap, output).

Outputs go to `artifacts/TIME-AS-FOLD-20261125-001A/TIME-AS-FOLD-20261125-001A-E001_count_of_returns/` (logs in `logs/`).
Every process caps its address space at 6 GB (`resource.setrlimit`); every run A and every test has the registered limit
of 600 seconds of process time.

From this folder, with `PY=/home/jscul/p-vs-np-contact-first/.venv/bin/python`:

| Step | Command | Wall time seen (6 processes, other work on the host) |
| --- | --- | --- |
| knot tests against brute force | `$PY -B tf_unit_knots.py` | 10 s |
| G1, knot for knot | `$PY -B tf_gates.py g1a --procs 6` | 70 s |
| G1, the census | `$PY -B tf_gates.py g1b --procs 6` | 90 s |
| G2 | `$PY -B tf_gates.py g2 --procs 6` | 5 s |
| G3 | `$PY -B tf_gates.py g3` | 2 s |
| run 1 | `$PY -B tf_runs.py run1 --procs 6` (writes `run1.jsonl.gz`, kept in eight parts, deviations 46) | 6 min |
| run 2 | `$PY -B tf_runs.py run2 --procs 6` | 10 s |
| run 3 | `$PY -B tf_runs.py run3 --procs 6` | 11 s |
| census tables (P2, P3, P7, P8, P9) | `$PY -B tf_census.py` | 12 s |
| P4's round 1 | `$PY -B tf_special.py p4` | 1 s |
| run 4, the prefix run (deviations 40) | `$PY -B tf_run4.py first --procs 6 --first 5000` | 51 min |
| run 4, the remainder (not run) | `$PY -B tf_run4.py first --procs 6 --skip 5000 --out run4_rest.jsonl.gz` | about 1 hour (estimate) |
| run 4, second pass | `$PY -B tf_run4.py second --procs 6` | nothing to run (deviations 41) |
| P10 | `$PY -B tf_run4.py p10` | 1 s |
| run 4 verdicts (P1, P5, P6, P15, P16) | `$PY -B tf_analyse4.py` | 3 s |
| cases | `$PY -B tf_run5.py cases` | 2 s |
| run 5 | `$PY -B tf_run5.py run5 --procs 6` | 57 min |
| run 5, every clock (deviations 42) | `$PY -B tf_run5.py run5-every-clock --procs 6` | 77 s |
| run 5b | not run (no case passes its 4n numberings) | |
| near-case supplement | `$PY -B tf_run5.py near --procs 6` | 7 s |
| run 6 | `$PY -B tf_run5.py run6 --procs 6`, and `run6-every-clock` (deviations 45) | 2 min each |
| summaries of runs 5, 6 | `$PY -B tf_summ5.py` | 1 s |
| run 7, runs A of runs 1 to 3 | `$PY -B tf_run7.py runA --procs 6` | 64 min |
| run 7, comparison runs (deviations 44) | `$PY -B tf_run7.py comparisons --procs 6 --time-sample 100 --prefix-pool 5000 --out run7_comparisons.jsonl.gz` | 16 min |
| replays of the census differences | `$PY -B tf_replay.py census` | 34 s |
| unit checks of series and tests | `$PY -B tf_unit_series.py` | 2 min |
| summary | `$PY -B tf_report.py` | 16 s |
