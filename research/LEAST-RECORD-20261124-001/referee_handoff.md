# Referee hand-off: LEAST-RECORD-20261124-001

Ticket A is referee pending. Its pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/LEAST-RECORD-20261124-001A/preregistration.md`. It builds on
`PARENTS-FROM-HOLDERS-20261124-001` and `LOCAL-ROUND-20261123-001`, both referee pending. Nothing in the next step waits
for the verdict.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| Ticket A, [result](../LEAST-RECORD-20261124-001A/results.md) | That with the generation modulo 3 shown, the rule "the other holder is a parent exactly when its stamp is one less" gives every chosen place of both populations under four laws, wherever no start knot waits in a round in which a start knot it meets acts; that it fails on the start-clause counterexample and the generation modulo 5 works there; the table of costs of ten stamps; the smallest confusable pairs for the stamps that fail | Exact computation; confusable pairs with explicit renamings, "no pair" by a quantity every renaming keeps | `experiments/LEAST-RECORD-20261124-001A/LEAST-RECORD-20261124-001A-E001_least_record/` (`README.md`, `deviations.md`), outputs in `artifacts/LEAST-RECORD-20261124-001A/LEAST-RECORD-20261124-001A-E001_least_record/` (`summary.md`, `checks.json`, `generations.json`, `rules.json`, `pairs_*.json`) |
| [Pre-registration](../LEAST-RECORD-20261124-001A/preregistration.md), "Settled by construction" | That under the release rule every birth's parents have equal generations wherever that condition holds | A proof sketch by the advisor | The pre-registration |
| The thread's [check](checks/thread_checks.txt) | The rule on ten structures grown by complete rounds with the ring study's engine, and its failure on the counterexample (one birth with parents of generations 0, 1, 1, 1; two places wrong) | Exact computation by the designer, on complete rounds only | `checks/thread_checks.py` |

Things a referee should know.

- **One program**, the earlier search's, extended by its author. The thread's own check covers the main rule on complete
  rounds, not the half-built structures and not the table of other stamps.
- **The second guard count is redundant** by a slip in the design; it always equals the first.
- **Holding.** The prediction that parents would have unequal generations under holding failed on the sixteen runs tried.
  One law under holding could not be counted at all, because every look there reaches a start knot or a member.
- **Two values.** Only five two-valued stamps were tried. The advisor sketched, without making it sound, a two-valued
  stamp read over a longer distance; it was not run.
- **What the stamp is.** It is written by hand and is the order of descent reduced modulo 3. The result is about the size
  of the record, and the note says so.
