# Reproduce the one-added-meeting census

From the repository root with its installed Python environment, run these commands. Each process uses one CPU thread and a six-GiB address-space cap.

~~~sh
ulimit -v 6291456
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
case_dir=experiments/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B-E001_meetings
.venv/bin/python -B "$case_dir/physical_population.py"
.venv/bin/python -B "$case_dir/cycle_counts.py"
.venv/bin/python -B "$case_dir/classify_sources.py"
~~~

The first program generates every source by adding a missing meeting to an unlabelled tree, exhausts the flags under the exact symmetry action and grows under both laws. It writes the named physical holdings, demands, shortages and funded rosters. The second independently builds decorated rings from rooted trees and checks every labelled six-knot tree edit and flag assignment. The final program checks each class, funding decision and physical trajectory, computes both exact weightings, ranks the empty sets of ordinary and operator-admitting closures, and executes the matched source-deletion and fresh-name sign controls. [Results](../../../research/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/results.md) · [Referee handoff](../../../research/KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001B/referee_handoff.md)
