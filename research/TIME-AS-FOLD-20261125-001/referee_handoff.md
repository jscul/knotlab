# Referee hand-off: TIME-AS-FOLD-20261125-001

**Refereed, 26 November 2026: confirmed with fixes** ([report R1](referee-R1/report.md)); its fixes are folded into the records it names. In its knot-test row, "P11, which fails as predicted by hand" is wrong: the hand prediction of two failures missed 23 more.

Ticket A is referee pending. Its pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/TIME-AS-FOLD-20261125-001A/preregistration.md`. It builds on
`PARTS-MEET-AGAIN-20261124-001`, `RING-IN-BALANCE-20261123-001` and `COPYING-PARTS-20261123-001`, all referee pending.
Nothing waits on this hand-off.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| [Claim](claim.md) and [definitions](definitions.md): C (a made count of returns) and C-iii (a second part whose course differs at each of three returns), with the rule for verdicts | That the tests are decidable as registered, and that "undecided" is never folded into "none" | Definitions; reviewed twice by the advisor before the freeze | the frozen texts |
| The count argument (pre-registration, "Settled by construction", item 2) | That under the first primary law, with a birth's fresh distinctions counted by its distinct inputs, no series has more ticks that give parts off than start knots acting, on every start | An argument, not refereed; no exception in 288 runs of each of two groups | [result](../TIME-AS-FOLD-20261125-001A/results.md), P2 |
| Ticket A, [result](../TIME-AS-FOLD-20261125-001A/results.md), the verdicts | That C fails in all 88,299 tests; that C-iii holds in 78 (8, 20 and 50 by rule) with 148 undecided; the numberings under which each case holds (80 and 112 of 240, and the registered shifts) | Computed by one engine written from the frozen texts, gated against two earlier engines; verdict counts recounted by the thread from the raw records | `experiments/TIME-AS-FOLD-20261125-001A/…/tf_run4.py`, `tf_analyse4.py`, `tf_run5.py`; `artifacts/…/run4.jsonl.gz`, `run5*.jsonl.gz` |
| The knot test (P11, which fails as predicted by hand) | That 25 knots fail, all joins under parity with 4 to 38 parents, in 20 runs, none the run of a C-iii case; that the two methods never disagree | 28,352,211 verdicts on every run of the census runs; a seeded sample of comparison runs | `tf_run7.py`, `tf_knots.py` |

Points a referee should press:

- **One program.** There is no second implementation. The gates compare the engine's round with two earlier engines
  knot for knot, but the readings this study adds (series of returns, ticks, own and joint knots, the bars, the
  masked run) are checked only by unit tests and by agreement with the prototype's disclosed numbers.
- **The cut.** The main run stopped at its first 5,000 of 10,116 runs in the registered order. The primary laws and
  the first group are whole; three of the swap groups are partial. "No count under any law run" is about the part
  run.
- **One clock of each form.** The main run tests one clock of each form, as registered; testing every clock changes
  110 of 3,488 numbering verdicts and no conclusion. The frozen texts are in conflict on this point, and both
  readings are in the outputs.
- **The form of the count.** C asks for a fixed number of own knots for each tick. A count held otherwise is outside
  the test, and the result says so.
- **A census column not reproduced.** "Runs with a series giving parts off at two or more ticks" is higher than the
  prototype's in 8 of 82 cells, all for rules the prototype implemented itself; unresolved, and no prediction uses
  it.
- **Rounds.** Every period is in rounds. A result about ticks "per period" is a result about a supplied clock's
  units.
