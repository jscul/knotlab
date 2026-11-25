# LEAST-RECORD-20261124-001A-E001: how little has to be written for a knot to find its parents?

Code for the frozen pre-registration `research/LEAST-RECORD-20261124-001A/preregistration.md`. The program is the earlier
study's search program (`PARENTS-FROM-HOLDERS-20261124-001A-E001`, commit `307b3bbe63`), copied into this folder and
extended here; the earlier folder is not changed. Readings are numbered in `deviations.md`. `contract.json` and
`identity.json` are frozen.

## Files

| File | What it is |
| --- | --- |
| `pfh_common.py` | Paths, the reference engine (through the one-birth-at-a-time study's checked loader), the laws (with the four laws with holding of P3), the frozen sums |
| `pfh_struct.py` | One read-only form for every structure; generations, children and the stamps of the table, written from the record |
| `pfh_pop.py` | P1 (serial states replayed and checked), P2 and P3 lineages; the condition of each start from its complete rounds |
| `pfh_look.py` | The look within d, which shows every stamp of the knots it shows; the explicit renaming and its place-by-place check (marks and stamps) |
| `pfh_iso.py` | Colour refinement on one look; the exhaustive search on two looks |
| `pfh_views.py` | The depth-d unfoldings, stamps included, structure-wide and on an extracted look |
| `pfh_auto.py` | Whole-structure renamings (from the record; by search), each checked to keep marks and stamps |
| `pfh_classes.py` | Classes of looks for one law and one stamp at a time; a coarser stamp may start from a finer one's classes |
| `pfh_report.py` | Tables split by the condition, the guard counts, the least distances, the smallest confusable pair |
| `pfh_checks.py` | The earlier study's three checks (check (a) here), with stamps kept by the trial of every renaming |
| `lrec_checks.py` | Run 1: the four checks |
| `lrec_generations.py` | Run 3: generations, and the condition of every start |
| `lrec_run.py` | Runs 2, 5, 6 and 7 for one law and one chain of stamps |
| `lrec_run_all.py` | Every process of runs 2, 5, 6 and 7, at most six at once |
| `lrec_rules.py` | Run 4 (and run 6's rule): rules stated and checked against every chosen place |
| `lrec_summarize.py` | `summary.json` and `summary.md` |

## Rerunning

From this folder, with `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`:

```bash
python -B lrec_checks.py            # run 1; every later run refuses to start if it failed
python -B lrec_generations.py       # run 3 (needed by run 6's modulus)
python -B lrec_run_all.py --jobs 6  # runs 2, 5, 6, 7: 24 processes, each capped at 8 GB
python -B lrec_rules.py             # run 4
python -B lrec_summarize.py
```

Outputs go to `artifacts/LEAST-RECORD-20261124-001A/LEAST-RECORD-20261124-001A-E001_least_record/`. The class tables used by
the summary for P4, P5 and P6 are written to the session scratchpad (`PFH_SCRATCH`); they are intermediates, not outputs.

## Times of the registered runs (this machine, 2026-11-25)

Run 1 (`lrec_checks.py`) 3 min 47 s; run 3 under a minute; runs 2, 5, 6 and 7 (`lrec_run_all.py --jobs 6`) 25 min of
wall clock, the longest single process 25 min 04 s (ORD, chain H), peak memory 3.7 GB; run 4 (`lrec_rules.py`) 35 s.
