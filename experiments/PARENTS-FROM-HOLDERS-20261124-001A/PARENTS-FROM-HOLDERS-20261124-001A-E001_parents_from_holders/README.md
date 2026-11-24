# PARENTS-FROM-HOLDERS-20261124-001A-E001: can a knot tell its parents from its children by what is built near it?

Code for the frozen pre-registration `research/PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md`, written from it, the
shared definitions of `RING-IN-BALANCE-20261123-001` and sections 1.1 and 4 of `LOCAL-ROUND-20261123-001`'s definitions.
The reference engine is imported unchanged through the one-birth-at-a-time study's `lr_reference.py` (which checks its
SHA-256 sum); that study's `lr_core`, `lr_laws`, `lr_search` and `lr_configs` are imported read-only to rebuild its serial
states. Readings are numbered in `deviations.md`. `contract.json` and `identity.json` are frozen.

## Files

| File | What it is |
| --- | --- |
| `pfh_common.py` | Paths, the reference engine, the twenty pairs of `gate.json`, the frozen sums |
| `pfh_struct.py` | One read-only form for reference rounds and serial states; the record of parents gives each chosen place its kind |
| `pfh_pop.py` | P2 lineages (rounds to 2,000 knots or 12) and the 27 runs of R3 with seeds 0 to 19 replayed and checked |
| `pfh_look.py` | The look within d (full, C1, C2), its compressed form, the explicit renaming and its place-by-place check |
| `pfh_iso.py` | Colour refinement on one look; the exhaustive individualization-refinement search on two looks |
| `pfh_views.py` | The depth-d unfolding of every place (structure-wide) and the same computed on an extracted look |
| `pfh_auto.py` | Whole-structure renamings: from the record (P2) and by the search (serial states), each checked |
| `pfh_classes.py` | Classes of looks for one law, every kind of look and distance, exact both ways |
| `pfh_report.py` | Population tables, written-out pairs, the followed pair, whole-structure renamings |
| `pfh_checks.py` | Run 1: checks (a), (b), (c) |
| `pfh_checks_extra.py` | An extra check (not registered): the code against networkx's VF2 on larger looks |
| `pfh_run.py` | Runs 2 to 5 for one law |
| `pfh_rules.py` | Run 6: the stated rule checked against every place; guard counts of the serial runs |
| `pfh_knot_test.py` | P2's knot test (parity by both methods; not-all-equal up to 600 knots) |
| `pfh_whole_extra.py` | Addition to run 5 (deviations item 37): the last round of each lineage under 2,000 knots |
| `pfh_whole_pairs.py` | Addition to run 4 (item 39): confusable pairs at d = 6 exchanged by a renaming of a whole structure |
| `pfh_followed_extra.py` | Addition to run 4 (item 40): ORD's pair at d = 5 followed from round to round |
| `pfh_summarize.py` | `summary.json` and `summary.md` |

## Rerunning

From this folder, with `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`:

```bash
python -B pfh_checks.py                  # run 1 (writes checks.json; every later run refuses to start if it failed)
python -B pfh_checks_extra.py            # extra check against VF2
python -B pfh_run.py --law F1R           # runs 2-5, one law per process (F1R, F1O, R3W, ORD), 8 GB address-space cap
python -B pfh_run.py --law F1O
python -B pfh_run.py --law R3W
python -B pfh_run.py --law ORD
python -B pfh_knot_test.py
python -B pfh_rules.py                   # run 6
python -B pfh_whole_extra.py             # additions (not registered)
python -B pfh_whole_pairs.py             # needs the class tables pfh_run.py leaves in the scratchpad
python -B pfh_followed_extra.py
python -B pfh_summarize.py
```

Outputs go to `artifacts/PARENTS-FROM-HOLDERS-20261124-001A/PARENTS-FROM-HOLDERS-20261124-001A-E001_parents_from_holders/`.
Setting `PFH_OUT` sends them elsewhere (development only). `pfh_run.py` also writes the class of every place to the
session scratchpad (`PFH_SCRATCH`), an intermediate that is not an output.

## Times of the registered runs (this machine, 2026-11-24)

| Run | Wall clock | Peak memory |
| --- | --- | --- |
| `pfh_checks.py` | under 1 s | small |
| `pfh_run.py --law F1R` | 52 s | 0.7 GB |
| `pfh_run.py --law F1O` | 4 min 28 s | 2.1 GB |
| `pfh_run.py --law R3W` | 10 min 05 s | 4.7 GB |
| `pfh_run.py --law ORD` | 15 min 19 s | 5.5 GB |
| `pfh_knot_test.py` | 3 s | small |
