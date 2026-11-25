# Referee hand-off: DESCENT-HELD-20261125-001

The note's two arguments are the study's content and are not refereed; ticket A is their check and is referee pending.
The pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/DESCENT-HELD-20261125-001A/preregistration.md`. The study builds on
`LEAST-RECORD-20261124-001`, `PARENTS-FROM-HOLDERS-20261124-001`, `LOCAL-ROUND-20261123-001`,
`GUARD-CAP-AND-HOLD-20261124-001` and `RING-IN-BALANCE-20261123-001`, all referee pending, and it narrows the first
(where the three-valued stamp fails). Nothing waits on this hand-off.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| [The note](note.md), argument 1 (the restart lemma), with hypotheses R1 to R4 and the complete-round extension | That on a population holding a structure both as grown and as a start, no function of the structure names the parent places; that a structure after a complete round, handed in as a start, grows as the continuation does wherever the round uses only the present structure | An argument, not refereed; checked on 10 lone-knot cases, 515 census structures and 140 restarts | [the run's result](../DESCENT-HELD-20261125-001A/results.md), parts 2 and 3 |
| The note, argument 2 (H1 and its converse; the rule for retiring knots; H3) | That under a ration counting places in threes the place rule is right on a run exactly when the start's meeting knots agree, every birth's parents agree in parent steps counted in threes, no count changes after birth by a number not divisible by 3 and no closing birth would receive an added distinction; that with the added distinctions barred every birth is the base law's through the base law's closing round | Arguments, not refereed; no exception in 20,677, 1,800, 45,142, 3,372 and 616 runs | parts 1 and 4 |
| Ticket A, [result](../DESCENT-HELD-20261125-001A/results.md), the census counts | The table of starts with a birth whose parents are at different parent steps, under 14 laws, with the splits by greatest difference; 133 starts whose meeting knots agree; 515, 4, 511 and 1,234 census structures reached within round 1 | Exact counts by two programs written apart; seven of the laws counted a third time by the thread with an earlier study's round | `experiments/DESCENT-HELD-20261125-001A/…/part1.py`, `sum_part1.py`, `part2.py`; [the third count](checks/README.md) |
| The knot test (P10) | That every new knot passes under parity (argued in the note) and under not-all-equal (seen only) | Two methods under each knot law on 818 of 1,244 runs and 154 more; 272 not run | `part7.py` |

Points a referee should press:

- **Everything predicted had been seen.** Every prediction was written after the drafter's scratch runs. The run is a
  second program, not a test that could surprise; the arguments carry the claim.
- **The restart lemma's reach.** It is exact for one structure with two records. For structures within round 1 (511 of
  the 515) only that one-structure conclusion is claimed; the extension to every later structure needs a complete
  round.
- **"No function of the structure" is about a population.** Within one known start's history the lemma says nothing,
  and the note says so. Whether a class of starts that no reached structure belongs to gives one record is the open
  arm and is not tested.
- **The count forms are supplied rules.** The run's "right on every structure" is a property of a rule the thread
  wrote, checked against the conditions the thread stated. It is not evidence that growth holds an order.
- **Two sentences of the frozen text are too broad** (the planted error's "exactly"; "145 to 234 by law"), and two
  scratch figures for the count forms were 4 and 30 too high because the prototype left out a closing knot's places.
  The result lists each.
- **What was cut.** The six-knot sample stopped at 1,165 of 3,000; the knot test at 818 of 1,244 runs, with every run
  of the rings among the 272 not run; the registered renumberings of five larger starts were not run.
- **The earlier study's notes carry a dated correction.** The least-record study's result and decision now say where
  the stamp fails on the census; its registered verdicts are unchanged.
