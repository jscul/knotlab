# WHAT-A-BIRTH-CARRIES-20261125-001A-E001: how to rerun

The question: under the recorded ordinary count (ORD), short knots retiring, RELEASE and the recorded taking rule MET with
take-the-oldest (take-the-newest as its swap), on the made starts made-3 and made-4 with the second pattern's start
knot fixed and a stated number a of its members left usable by a bar placed by hand, is the set of courses from X only,
over every numbering of the start, disjoint between two values of a; does the first difference involve a knot of the
second pattern's descent; and does one value the law uses at one birth already separate them (the law handing a count
over), or is the difference composed over several births?

Written from the frozen texts alone (`research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions.md` and `claim.md`,
`research/WHAT-A-BIRTH-CARRIES-20261125-001A/preregistration.md` and its data files, and the definitions of
`MADE-COPIER-20261125-001`, `PARTS-MEET-AGAIN-20261124-001` and `RING-IN-BALANCE-20261123-001`), without the drafter's
prototype. Readings are in `deviations.md`. `contract.json` and `identity.json` are frozen and were not touched.

Files:
- `wbc.py`: the round (FD 2, SD steps 1 to 8 with taking), the bars, descent, answers, the values used at X's births
  (RD 3.3), the meeting round and the linking knots, the course from X only in reduced form and its exact comparison
  (VF2 inside classes of an invariant), attribution. It imports the fold engine `pm.py` (the guard's numbers; the
  reference engine of run G) and `knots.py` (the knot test, FD 7) from
  `experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/`, unchanged.
- `common.py`: paths, the frozen hashes (checked at the start of every script), the memory cap, output, the class lists.
- `gate.py`: run G. `runs.py`: runs N, P, 1, 1b, 2 with the per-pair readings. `analyze.py`: the cells, the checks
  of S1 to S5, the predictions' inputs (`summary_raw.json`). `report.py`: `summary.json` and `summary.md`.

Outputs go to `artifacts/WHAT-A-BIRTH-CARRIES-20261125-001A/WHAT-A-BIRTH-CARRIES-20261125-001A-E001_which_under_ordinary_count/`.
Every process caps its address space at 6 GB.

From this folder, with `PY=/home/jscul/p-vs-np-contact-first/.venv/bin/python`:

| Step | Command | Wall time seen (24-core host, load 16 to 28 from other work) |
| --- | --- | --- |
| G, the 648 runs against the fold engine | `$PY -B gate.py engine --chunk i/4` for i = 0..3 | 196 s (4 processes) |
| G, listing, records, symmetric pairs | `$PY -B gate.py rest` | 10 s |
| P | `$PY -B runs.py P` | 1 s |
| N | `$PY -B runs.py N --procs 4` | 5 s |
| 1 | `$PY -B runs.py 1 --procs 4` | stopped at 60 min (deviations 28): 965 of 1,320 jobs |
| 1, second part (take-the-newest under parity only, deviations 32) | `$PY -B runs.py 1r --procs 4` | 135 s |
| 1b | `$PY -B runs.py 1b --procs 3` | 803 s |
| 2 | `$PY -B runs.py 2` | 48 s |
| verdicts | `$PY -B analyze.py && $PY -B report.py` | about 20 s |

What each output holds:
- `G_engine_i_of_4.jsonl`: one row per gate run, with every difference found (none).
- `G_rest.json`: the gate listing as reproduced, the four attribution records with the class returned, the 100
  symmetric pairs.
- `run<X>_runs.jsonl.gz` (X = 1, 1r (the second part of run 1), 1b, N): one record per run: the start as listed, the usable names, the law, rounds
  read, stop and guard, the course from X only through rounds 2, 3 and 4 in reduced form (node labels and edges, names
  forgotten) with its class in the job and over the whole run (`global_class`), the meeting round and how it was
  found, the linking knots with their FD 5.7 class, the S4 values of round 2 (J's candidates, take, D, f, places,
  groups, partners; the births of Y's usable members), every short member after round 1, the rounds with an implied
  birth, FD's trace in counts and the joint births per round, each round's births counted by (kind, parents, taken,
  D, f), the knot test's counts and failures, the values used at X's births in round 2, and a fingerprint of the
  whole run.
- `run<X>_pairs.jsonl.gz`: one record per pair (ν, A, B), a < b: both meeting rounds, the same meeting, course
  equality by prefix, and the first differing value used at X's births (round, step, entry, both values, its
  differing part with descents, its class).
- `run<X>_handed.jsonl.gz`: per underlying numbering and prefix, the partition P of a = 1 … h by courses and the
  entries that induce it.
- `run<X>_index.json.gz`, `run<X>_classes.json`: the run index used by `analyze.py`, and the number of course classes
  and VF2 calls per law and prefix. Run 1 has neither (it was stopped; `analyze.py` rebuilds its index from the
  per-run records).
- `runP.json.gz`, `run2.json.gz`: the records of the planted control and of run 2, and the comparison of made-5 with
  made-6.
- `summary_raw.json`, `summary.json`, `summary.md`: the verdicts.
