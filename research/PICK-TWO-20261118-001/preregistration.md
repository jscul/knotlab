# Who picks the number of orders: pre-registration

Epic `PICK-TWO-20261118-001`, 18 November 2026, by Claude. It takes `NEVER-NEST-20261118-001`'s first direction, chosen by the
coordinator. Goals G1 and G16; challenges A101. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

`NEVER-NEST-20261118-001` grew full two-way grids forever from a line with a rule told "at most two orders", and its referee found
that the two is wholly the cap's: the same rule uncapped makes every order. Does any rule told no number settle at two orders
from a line? Or is the number always handed over, and if so, by what: a cap, a price, the start, or the arity of one move?

## The rules

All read only the states. Their moves are fills (one to three betweenness knots on any old pairs, no state added) and
subdivisions (one knot on a pair one split apart, two states added), as in `NEVER-NEST-20261118-001`'s NNF. Ties are uniform over
distinct extensions.
- **Told a number.**
  - CAP(d): the fills after which λ ≤ d; else a subdivision. CAP(2) is NNF.
  - PRICE(f): the moves minimising (states added) + f(λ after), with f(λ) = wλ or wλ².
- **Told no number.** A rule counts as told no number when its conditions name no count of orders or of crossings, other than
  zero ("crosses nothing"). This choice is frozen here (the advisor's point that the answer rests on it).
  - KEEP: the fills that leave λ unchanged; else a subdivision.
  - CC: corners across two crossing splits; else a subdivision.
  - ODD: the fills after which the crossing graph has no odd cycle; else a subdivision.
  - FRESH: the fills whose new crossings all join splits that crossed nothing before; else a subdivision.
  - NEWCROSS: the fills that make no new crossing between two splits that both crossed something; else a subdivision.
  - SEED (seed and copy): while nothing crosses, any fill. After that, the fills that make no new crossing between two splits that
    crossed something, and under which a split that crossed nothing and gains crossings ends with exactly the crossers of a split
    that crossed something. Else a subdivision.

## Ticket A: the proof (written before this freeze)

`proofs/PICK-TWO-20261118-001A/PICK-TWO-20261118-001A-P001_sources/proof.md`.
- **S1.** λ never decreases.
- **S2.** CC keeps every relation of splits, so it keeps the start's number of orders.
- **S3.** CAP(d) refills from a full d-grid.
- **S4.** The corner knot set is always a fill. At a full grid along a chain it raises λ by exactly one, and Q_d has no fill.
- **S5.** A greedy price raises at a full non-cube grid iff its increment is below two states. A linear price either always
  raises or never leaves the line; the number is written into the price.
- **S6.** One fill on a line makes exactly two orders, and KEEP never fills a line.
- **S7.** After its first fill, SEED keeps a bipartite crossing graph.

## Ticket B: computations

`experiments/PICK-TWO-20261118-001B/PICK-TWO-20261118-001B-E001_pick/`: `picklib.py`, `run.py`, `checks.py`, building on
`NEVER-NEST-20261118-001B`'s `nnlib.py` and `MEET-ORDERS-20261118-001B`'s `melib.py` (pinned). The fill enumeration starts from the
middle knot that every fill needs (only middle knots pin the constant states) and equals NEVER-NEST's full enumeration on 120
bases. Runs stop at 62 states and say so. 9 checks pass before this freeze.
- **C1.** CAP(3) from lines of 5 to 8 (20 runs each) and Q₃ (10); CAP(4) from lines of 5 and 8 (10 each) and Q₄ (5); to n = 60.
- **C2.** PRICE(wλ), w = 1.0, 1.9, 2.0, 2.1, 3.0, from lines of 5 and 8, 20 runs each, to n = 40.
- **C3.** PRICE(wλ²), w = 0.25, 0.35, 0.5, 1.0 (none at a threshold), from lines of 5 and 8, 20 runs each, to n = 40.
- **C4.** KEEP, CC, ODD, FRESH, NEWCROSS and SEED from lines of 5, 6, 7, 8, 10 and 12 (20 runs each), and from Q₃ and the
  3 × 3 × 3 grid (10 each) as controls, to n = 60.

**Readings at every step.** k, λ, the states, a full d-grid and its chain sizes, the largest set of pairwise crossing splits, the
splits that cross nothing, the crossing graph's components, the step's kind and cost.

## Decision rules (frozen)

- **A rule told no number settles at two (weak)** if, from every line length, every run has k = λ = 2 at every step after its
  first fill to the end of the run.
- **Strong** if, in addition, at least 90% of runs from every line length pass through a full 2-grid at least three times, and
  every subdivision after the first full 2-grid comes at a full 2-grid.
- **Source.** From Q₃ and the 3 × 3 × 3 grid, a rule that keeps λ = 3 conserves the start; one whose λ rises does not.
- **CAP(d) picks d** if from lines λ reaches d and never exceeds it in every run, and full d-grids occur in at least 90% of runs
  (two or more by n = 60 for d = 3 from lines of 5 and 6).

## Predictions (frozen)

| # | Prediction | Source |
| --- | --- | --- |
| P1 | CAP(3) from lines of 5 to 8: λ reaches 3 and never exceeds it in every run; a full 3-grid before the first subdivision in every run; two or more full 3-grids by n = 60 in at least 90% from lines of 5 and 6 | advisor; S3 |
| P2 | CAP(4) from the line of 5 and from Q₄: λ reaches 4 and never exceeds it in every run | advisor |
| P3 | PRICE(wλ): w = 2.1 and 3.0 keep λ = 1 in every run (S5); w = 1.0 and 1.9 reach λ ≥ 4 by n = 40 from the line of 5 in every run; w = 2.0 grows past 2 in most runs | S5; advisor |
| P4 | PRICE(wλ²) settles where S5 says: the largest λ reached is 4, 3, 2 and 1 for w = 0.25, 0.35, 0.5 and 1.0, in every run | S5 |
| P5 | ODD behaves as NNF: two orders at every step after the first fill and a full 2-grid in every run, from every line | advisor (on these bases, no odd crossing cycle is equivalent to λ ≤ 2) |
| P6 | FRESH keeps k = λ = 2 at every step after the first fill in every run (weak tier), but is not strong at any line length | advisor |
| P7 | NEWCROSS does not settle at two: from the line of 8, fewer than half the runs end with λ = 2 | advisor (25 to 45%) |
| P8 | SEED is strong at every line length, and from Q₃ and the 3 × 3 × 3 grid keeps λ = 3 | advisor |
| P9 | KEEP and CC keep λ = 1 from every line and λ = 3 from both controls, in every run | S2, S6 |

So the predicted answer: of the rules told no number, only FRESH (weak) and SEED (strong) settle at two from a line, and both keep
three from the controls. Their two would then come from the start (one order) and the arity of one fill (one new distinction has two
sides, so one fill on a line makes exactly two orders, S6), not from the rule.

The advisor was consulted before this freeze: it checked S1 to S6, gave the rules FRESH and SEED, the controls, the decision tiers
and most predictions. S7 and P6 to P9 as worded are mine.

**Exploration disclosed.** Before this freeze, single runs were made for timing only: CAP(3), PRICE(λ), KEEP and CC to n = 30,
and FRESH, SEED, NEWCROSS, CAP(3) and PRICE(2λ) from the line of 9 and SEED from Q₃ to n = 40, each read for its time and whether
it stopped. A batch set to print each run's λ was stopped before it printed anything. The gate checks read λ on short runs of
CAP(3) and CC from Q₃ and of KEEP from the 2 × 2 pattern, Q₃ and the line of 5.
