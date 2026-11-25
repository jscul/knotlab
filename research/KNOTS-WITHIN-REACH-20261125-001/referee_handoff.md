# Referee hand-off: KNOTS-WITHIN-REACH-20261125-001

Ticket A is referee pending. Its pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/KNOTS-WITHIN-REACH-20261125-001A/preregistration.md`. It builds on
`RING-IN-BALANCE-20261123-001`, `PARTS-MEET-AGAIN-20261124-001`, `COPYING-PARTS-20261123-001` and the studies of 17 to
19 November 2026 that it cites, several of them referee pending. Nothing waits on this hand-off.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| [Definitions](definitions.md), Lemmas E, F, R, N and P (sections 1.6, 2.6, 2.8, 5.3, 5.4) | That counted from a start knot the history count is the count of knots made by a round, within a stated shift; the bound on how strongly two loose distinctions are related under not-all-equal; that under parity two loose distinctions are tied or unrelated | Arguments, not refereed; checked on 136, 87, 1,930 and 29,599 cases with no exception | [result](../KNOTS-WITHIN-REACH-20261125-001A/results.md), run 0 and the checks of runs 2, 4 and 5 |
| Ticket A, the test for one power from every knot examined (run 2) | That 21 runs pass with the scaling condition, all at power 1 with constant births; that none passes at 2 or more; that 54 runs of the capped laws hold the test at power 2 at the longer length only; that 111 pass at power 2 under the swapped thresholds | Computed by one engine written from the frozen texts, with eight built controls; the answers recounted by the thread from the raw records | `experiments/KNOTS-WITHIN-REACH-20261125-001A/…/run2.py`, `readings.py`; `artifacts/…/run2.jsonl.gz` |
| Ticket A, births per round by law and the start-by-start table (run 1) | The readings of births under twelve laws on 219 small starts and 250 five-knot starts; that retiring without a cap turns 112 of 145 ending starts into growths of degree 1; that a cap of three leaves 9 starts at degree 2 | The same engine; the readings by law recounted by the thread | `run1.py`; `run1.jsonl.gz` |
| Ticket A, the growing end (runs 4 and 5) | The counts of concordant, discordant and tied comparisons under five laws; the smallest stages at each level (7 knots with loose counts equal; 9 and 10 with shared-place counts equal too); the 1,602 parity stages with a rule among fewer loose distinctions than all | Exact integer arithmetic by the same engine, within a registered cap on stages | `run4.py`, `run5.py`, `ge.py`; `run4.jsonl.gz`, `run5_*.jsonl.gz` |

Points a referee should press:

- **One program.** No second implementation. The controls are structures built by hand whose counts are known (a ring,
  a tree, a six-regular pattern, a comb, one law from one knot), and the two tables the thread recounted use the
  engine's own records.
- **The negative at power 2 is the thresholds'.** Under a range of a factor 4 and a factor of 3 between a knot's
  bounds, 111 runs pass at power 2. The registered thresholds were fixed before the run; they are a scaffold.
- **The history count mixes the roster with the rounds.** The study says so and reads the roster apart; it does not
  separate the two inside the history count.
- **A frozen formula was short.** The count from a made knot of a bare ring lacks its upper end in the definitions;
  the engine found it, a control was rewritten before the gate run, and one disclosed sentence fails with it.
- **Four predictions failed** (two about caps, one clause about bare rings, one about the power read at the shorter
  length), and one is undecided because a clause is tested on no stage.
- **What was cut.** The first table ran on 250 of 1,000 sampled five-knot starts; the knot test on 1,435 of 2,863
  runs; the exact check of the statement about uniform takes was not run.
