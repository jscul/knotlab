# Referee hand-off: PARENTS-FROM-HOLDERS-20261124-001

Ticket A is referee pending. Its pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md`. It builds on
`LOCAL-ROUND-20261123-001` and `RING-IN-BALANCE-20261123-001`, both referee pending. Nothing in the next step waits for
the verdict.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| Ticket A, [result](../PARENTS-FROM-HOLDERS-20261124-001A/results.md) | That half-built states hold pairs of places, one to a parent and one not, exchanged by a renaming of the whole structure, under each of four laws; that under (FLOOR1, CANCEL-RETIRE) a stated rule of distance 2 gives every place of the structures built by complete rounds; that under (FLOOR1, CANCEL-OFFSHOOT) the advisor's pair is alike exactly for d ≤ R − 2 at round R; the least distances by round under the other two laws; the finished structure of 16 knots with its renaming | Exact computation; each confusable pair is reported with an explicit renaming checked place by place, and "no pair" only where a quantity every renaming keeps separates the looks | `experiments/PARENTS-FROM-HOLDERS-20261124-001A/PARENTS-FROM-HOLDERS-20261124-001A-E001_parents_from_holders/` (`README.md`, `deviations.md`), outputs in `artifacts/PARENTS-FROM-HOLDERS-20261124-001A/PARENTS-FROM-HOLDERS-20261124-001A-E001_parents_from_holders/` (`summary.md`, `checks.json`, `pairs_*.json`, `rules.json`, `whole_pairs.json`) |
| The advisor's proof by hand (in the pre-registration, "Known before the freeze") | That on the two-knot start under (FLOOR1, CANCEL-OFFSHOOT) an offshoot's place to its parent and its place to its join are alike until the look reaches the live roster | A proof by hand, confirmed by computation at rounds 2 to 12 | The pre-registration |
| The thread's [checks](checks/thread_checks.txt) | The threshold d ≤ R − 2 at rounds 3 to 6, by a separate program using a general graph matcher; the finished structure of 16 knots as the literature's four-dimensional hypercube graph, with a renaming that swaps the start knot and its offshoot | Exact computation by the designer | `checks/thread_checks.py` |

Things a referee should know.

- **One program for the search**, written from the frozen text by a helper that saw no earlier code. Its comparison of looks
  was checked against trying every renaming on small looks, against a separate matcher on 4,000 larger ones, and by the
  advisor's pair with its exact threshold.
- **The first population's half-built states decide the headline.** They are the states of the earlier study's widest
  guard in twenty sampled orders. The pairs there are small and exact; they do not depend on the growth going further.
- **The second population is the thread's addition.** The owner asked for the structures already built; on those a look of
  a few steps reaches the start or a member. Every "rule exists" statement is given with the number of places whose look
  reaches neither.
- **Two predictions failed**, and two parts of the frozen text could not be run as written (a bound that excluded most
  final structures; a condition no law met). The result note says how each was handled.
- **What is not shown:** that the distance needed is unbounded under a fixed three with waiting or under ordinary growth;
  and anything about a record smaller than the full one.
