# WHAT-A-BIRTH-CARRIES-20261125-001B-E001: how to rerun

The question: under a listed family of 60 laws that use no names (takes of a sole candidate, MET-SOLE, STEPS1-SOLE
and STEPS2-SOLE, with the recorded rations and treatments, three owing rations and one new treatment, SHORT-BY, each
added by hand), on eight small starts, to 7 rounds: do two parts the growth made have a meeting only through made
knots; is one linking knot an ancestral common knot made by births; does the course from X only differ between Y
usable and Y barred, attributed through the meeting; and which listed laws are the least for each?

Written from the frozen texts alone (`research/WHAT-A-BIRTH-CARRIES-20261125-001/definitions_b.md`, `claim_b.md`,
`research/WHAT-A-BIRTH-CARRIES-20261125-001B/preregistration.md` and its four data files, ticket A's definitions, and
the definitions of `MADE-COPIER-20261125-001`, `PARTS-MEET-AGAIN-20261124-001` and `RING-IN-BALANCE-20261123-001`),
without the drafter's prototype. Readings are in `deviations.md`. `contract.json` and `identity.json` are frozen and
were not touched.

Files:
- `eng.py`: the round (FD 2 with RELEASE) with the rules of BD2 2 and the gate's MET(OLDEST) and MET(NEWEST); runs,
  bars, the guard with its multiplier and peak counts. Imports, unchanged and read-only, the fold engine `pm.py` and
  `knots.py` (FD 7) from `experiments/PARTS-MEET-AGAIN-20261124-001A/.../` and ticket A's `wbc.py` (the course's
  invariant and exact test, the alignment of values and attribution).
- `read.py`: descent, answers, meetings, the linking set and its readings, the course from X only, the values used
  at X's births, attribution, m, rosters the same, the symmetry check, the knot tests of barred runs.
- `item.py`: one item (a law, a start, a knot law) with every registered reading. `runs.py`: the registered runs as
  ordered lists of items. `gate.py`: run G. `test_rules.py`: unit tests of BD2 2 on structures built by hand.
- `verdicts.py`, `analyze.py`, `report.py`, `n2check.py`: verdicts, minimal laws, summary. `replay.py`,
  `expected_listing.py`: birth-by-birth listings.

From this folder, with `PY=/home/jscul/p-vs-np-contact-first/.venv/bin/python` (each process caps its address space
at 6 GB):

| Step | Command | Wall time seen (24-core host, load 6 to 10) |
| --- | --- | --- |
| unit tests | `$PY -B test_rules.py` | 1 s |
| G | `$PY -B gate.py engine --chunk i/5` (i = 0..4) and `$PY -B gate.py rest` | about 90 s, 6 processes |
| C0 | `$PY -B runs.py C0 --procs 6 --deadline T` | 67 s |
| 1a | `$PY -B runs.py 1a --procs 6 --deadline T` | 85 s |
| P1 | `$PY -B runs.py P1 --procs 6 --deadline T` | 72 s |
| N2 | `$PY -B runs.py N2 --laws L02,L10,L07 --procs 6 --deadline T`, then `$PY -B n2check.py` | 48 s + 18 s |
| 1b, 1c | `$PY -B runs.py 1b ...`, `$PY -B runs.py 1c ...` | 68 s, 70 s |
| P2 | `$PY -B runs.py P2 --from-runs 1a,P1,1b --mult 10` (and 100) | 0 items |
| U1, M2 | `$PY -B runs.py U1 --procs 4 ...`, `$PY -B runs.py M2 ...` | 144 s, 2 s |
| verdicts | `$PY -B analyze.py && $PY -B report.py` | 10 s |
| listings | `$PY -B replay.py <start> <law id> <knot law>`; `$PY -B expected_listing.py` | 1 s each; 340 s |

`--sample n` times every n-th item of a run into the scratch folder only (deviations 30). T is the end of the cap
(70 minutes from the start of run G).

Outputs, in `artifacts/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot/`:
- `G_engine_i_of_5.jsonl`, `G_rest.json`: run G.
- `run<R>.jsonl.gz` (R = C0, 1a, P1, N2, 1b, 1c, U1, M2; P2_x10 and P2_x100 are empty): one record per item: the
  law, the start, rounds read, stop, guard, peak counts, the knot test of run A; per s the parts after round s and the
  ordered pairs wholly apart with no meeting; per pair with a meeting: s, X's and Y's members, the meeting round and
  how it was found, the linking set (each knot's round, kind, parents, FD 5.7 class, ancestry, linking distinctions
  with their holders), strict or not, FD 5.7's weaker class, the ancestral reading in both forms, the barred run
  (A = ∅) with its meeting, the first round the courses differ, both courses (pairs meeting only through made
  knots; invariants for the others), the attribution (first differing round, step, entry, both values, differing
  part with descents, class, class in the other order), the Y-side knots of the first differing demand; for pairs
  meeting only through made knots also the subsets' runs (meeting, link verdict, course class), how many, which at
  equal number, m, lasting, the checks, and for the first 8 differing pairs of an item the knot tests of the barred
  run and the lasting reruns. N2's records keep, per pair, the verdicts and both courses.
- `run<R>_index.json`: per item, its wall time and counts; the run's items done, cut and not run.
- `runN2_comparison.json`: every renamed run against the registered numbering.
- `summary.json`, `summary.md`: the verdicts, the predictions, the minimal laws, the reported readings.
- `expected_case_listing.txt`: the expected case birth by birth; `check_c_fixing_start_knots.json`: check (c) with
  every start knot also fixed; `listing_*.txt`: the cases that differ from "Known before the runs".
