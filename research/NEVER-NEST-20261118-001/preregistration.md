# A rule that never nests its fills: pre-registration

Epic `NEVER-NEST-20261118-001`, 18 November 2026, by Claude. It takes B197, from `MEET-ORDERS-20261118-001` (direction 2), after
`LOCAL-ROOM-20261118-001`, agreed with the coordinator. Goals G1 and G16; tests A99. Frozen before any read-out of ticket B. The
canonical K1–K3 test is unchanged.

## The question

Under KF3 a fill makes the two halves of its knot cross, and a later fill of a triple keeps two orders exactly when its middle never
lies strictly between the ends of a fill with another middle (Lemma C, `MEET-ORDERS-20261118-001A`). A rule that takes only the
fills that keep two orders, and lengthens the line when none is left, keeps two orders by construction. Does it grow two-way grids
without end, as `LOCAL-ROOM-20261118-001`'s class law did with a remembered class per split, or does it run out of fills?

`LOCAL-ROOM-20261118-001`'s referee (R1, section 2) adds the sharper question: can a rule that reads the states, beyond a reach
limit, hold two orders and fill them with nothing handed over? It names a rule reading the crossing graph as the untested case.

## The rules

All add one distinction p with one to three betweenness knots, every old state kept, p constrained and no copy (A99). A **fill**
adds no state; a **subdivision** is one knot B(u, p, v) on an old pair differing on exactly one split.
- **KF3** (as in `MEET-ORDERS-20261118-001`): knots only on pairs that already share a knot; the fewest states; uniform over knot
  sets.
- **NN (never nest).** KF3's fills after which the base has two orders (k = λ = 2, read from the states), uniform over knot sets;
  if there is none, a subdivision on a pair that shares a knot, uniform over such pairs. On a line with fills of triples this is
  Lemma C's rule.
- **NN2.** The cheapest of KF3's options after which the base has two orders, at any cost, uniform over knot sets.
- **SUB.** Subdivisions only, the baseline: it keeps the number of orders and never fills.
- **NNF.** NN with any old pair allowed in a knot, uniform over distinct extensions.
- **CC (corner across crossing splits).** The fills {B(x, r, y), B(c, x, r), B(c, y, r)} on any old distinctions where c differs
  from x on exactly one split and from y on exactly one other, and those two splits cross; else a subdivision; uniform over
  distinct extensions. CC reads only two splits near c and whether they cross.
- **The class law** of `LOCAL-ROOM-20261118-001`, its frozen code, as the comparator.

**What each is given.** NN and NNF are given the number two: they take the fills after which there are at most two orders, read
from all the splits at once, and nothing marks which split belongs to which order. CC is given its first crossing (it never fills
a line). The class law is given a class for every split.

## Ticket A: the proof (written before this freeze)

`proofs/NEVER-NEST-20261118-001A/NEVER-NEST-20261118-001A-P001_refill/proof.md`.
- **N1.** A subdivision keeps k and λ.
- **N2.** On a line with fills of triples, the base is a full grid only with one or two middles and every fill they allow.
- **N3.** From a full grid, NNF refills every new row or column, forever.
- **N4.** From any line, NNF reaches a full grid before its first subdivision, then N3 applies.
- **N5.** CC keeps two orders, refills from a full grid, and never fills a line.

So NNF's and CC's courses are proved; the computations check them and read their shapes. The open question is NN, whose knots may
only join pairs that already share one, and NN2.

## Ticket B: computations

`experiments/NEVER-NEST-20261118-001B/NEVER-NEST-20261118-001B-E001_nest/`: `nnlib.py`, `run.py`, `checks.py`, building on
`MEET-ORDERS-20261118-001B`'s `melib.py`, `STATE-RULES-20261117-001B`'s `rules.py` and `LOCAL-ROOM-20261118-001B`'s `locallib.py`
(all pinned). `melib.py` holds masks over the states in 64-bit integers, so beyond 62 states `nnlib.py` runs the same enumeration
on 64-bit words (equal to `melib.moves` on 40 bases: check 2b). 19 checks pass before this freeze.
- **E1.** Exact distributions of NN from every bracketing of 5 to 8 distinctions (5, 14, 42 and 132) to n = 12.
- **E2.** Exact distributions of NN2 from every bracketing of 5 and 6 to n = 10 (beyond that the classes number millions).
- **R1.** Labelled runs of NN (with the line tracked and odd sets read), NN2, KF3 and SUB to n = 40, from every bracketing of 5 to 8:
  two seeds for 5 to 7, one for 8 (254 runs per rule).
- **R2.** NNF from the line of 5 to 8 and the 2 × 2 pattern; CC from the 2 × 2 pattern, from the line of 5 to 8 after one fill of a
  uniform triple, and from the bare line of 5 (10 runs); 50 runs each to n = 40. The class law from the 2 × 2 pattern, 50 runs to 40.

**Readings at every step.** The number of orders (k, λ), the states N, the crossing graph (bipartition, complete or not), a full
grid ((a + 1)(b + 1) = n with a complete bipartite crossing graph), the two chains' sizes and the empty cells of their grid when
the crossing graph is connected, the splits that cross nothing, the step's kind (fill, subdivision, other) and cost, and for NN
the fills that keep two orders among the options (the advisor's diagnostic), the line's middles and the new fill's odd set while
the line can be tracked.

**Derived per run, on steps 21 to 40.** The fill fraction (fills per step), whether the base is a full grid at some n from 30 to
40, whether both chains grow after n = 20, the fills in steps 31 to 40, the share of subdivisions after n = 20 on the larger chain
(the advisor's strip test), empty cells (holes) and splits crossing nothing (tails).

## Decision rule (frozen; the advisor's)

For NN and NN2, at each start size, on steps 21 to 40:
- **Grows two-way grids:** median fill fraction at least 0.7, a full grid at some n in 30 to 40 in at least 80% of runs, and both
  chains growing after n = 20 in at least 80% of runs.
- **Starved:** median fill fraction at most 0.15, or no fill in steps 31 to 40 in at least 50% of runs.
- **Intermediate:** anything else.

## Predictions (frozen)

| # | Prediction | Source |
| --- | --- | --- |
| P1 | NN is **intermediate** at every start size: neither starved nor growing full grids | advisor (second consultation); my first expectation was starvation |
| P2 | NN passes through a full grid at some n ≤ 40 in at least half the runs at each start size, and in fewer runs from 8 than from 5 | advisor (95%, 85%, 70%, 60% for 5 to 8) |
| P3 | NN's median fill fraction on steps 21 to 40 lies between 0.25 and 0.65 at each start size | advisor (0.45) |
| P4 | NN has no fill in steps 31 to 40 in at most 15% of runs at each start size | advisor (5 to 10%) |
| P5 | NN2's median fill fraction on steps 21 to 40 is below NN's at each start size | advisor (0.2 to 0.35) |
| P6 | KF3 leaves two orders: at n = 40 at most 10% of KF3 runs have two orders, at each start size | mine, from `MEET-ORDERS-20261118-001` |
| P7 | NNF and CC from the 2 × 2 pattern, and NNF from every line: two orders at every step after the first and a full grid after every completed row or column, in every run (N3 to N5; a check, not a test) | proved |
| P8 | CC after one fill of a line reaches a full grid in fewer than half the runs at each start size | mine, not reviewed by the advisor |

The advisor was consulted twice before this freeze (its answers are summarised in the decision note). The CC rule, P8 and N5 were
added after its second answer, prompted by `LOCAL-ROOM-20261118-001`'s referee, and were not reviewed by it.

**Exploration disclosed.** Before this freeze, timing runs of single seeds of each rule (to n = 26 and n = 40, read only for their
times), one exact NN distribution from one bracketing of 5 to n = 11 (its class counts read), one of NN2 to n = 10 (class counts),
and the gate checks, which showed NN taking fills of five distinctions that keep two orders (9 of 183 bases in check 8).
