# What the knots read when nothing crosses yet: pre-registration

Epic `KNOT-SWITCH-20261118-001`, 18 November 2026, by Claude. It takes `PICK-TWO-20261118-001`'s first direction, chosen by the
coordinator. Goals G1 and G16; challenges A101. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

`PICK-TWO-20261118-001` found one rule, told no number, that settles at two orders from every line. SEED takes any fill while no
two splits cross, and afterwards only copies or conserves. The two enters at that switch. What state of the knots does "no two
splits cross" read?

## Ticket A: the proof (written before this freeze)

`proofs/KNOT-SWITCH-20261118-001A/KNOT-SWITCH-20261118-001A-P001_switch/proof.md`.
- **W1.** A knot-local move attaches a cone over the graph of the old pairs its knots use. b₂ never falls, and b₁ grows when those
  pairs do not touch.
- **W2.** A filled knot (four distinctions carrying four knots, each the middle of one) forces a crossing in any presentation.
- **W3.** Along KF3, NN, NN2 and SEEDK from a bracketing, four things are equivalent at every step: no two splits cross, there is no
  filled knot, b₂ = 0, and no fill has been made yet.
- **W4.** b₂ depends on the presentation (a saturated line has b₂ = C(n − 1, 3) and nothing crosses); the filled-knot reading does
  not, in its forcing direction.

## Ticket B: computations

`experiments/KNOT-SWITCH-20261118-001B/KNOT-SWITCH-20261118-001B-E001_switch/`: `knotlib.py`, `run.py`, `checks.py`, building on
`PICK-TWO-20261118-001B`'s `picklib.py`, `NEVER-NEST-20261118-001B`'s `nnlib.py` and `MEET-ORDERS-20261118-001B`'s `melib.py`
(all pinned). 7 checks pass before this freeze.
- **S1.** KF3, NN, NN2 and SEEDK, one seed each, from every bracketing of 5, 6 and 7 (61) and every third of 8 (44). SEEDK runs
  to n = 40, the others to 30. Every knot is recorded.

**Readings at every step.** b₀, b₁, b₂, the number of filled knots, the most knots on one pair, whether some four distinctions have
all four triples knotted, whether nothing crosses, k, λ, a full grid, and for each move the pair graph's cycles and components.

## Decision rules (frozen)

- **W3 holds** if at every step of every run the four readings agree.
- **SEEDK is strong** if, from every start size, every run has k = λ = 2 at every step after the first fill, and at least 90% pass
  through a full two-way grid at least three times with every later subdivision at a full grid (`PICK-TWO-20261118-001`'s tiers).

## Predictions (frozen)

| # | Prediction | Source |
| --- | --- | --- |
| Q1 | W3 holds at every step of every run | proved |
| Q2 | "Some four distinctions have all four triples knotted" (without middles) also agrees with "a crossing" on every step of these runs | mine: the grown presentations are irredundant, so line-type fours do not arise (advisor: it fails only on saturated presentations) |
| Q3 | SEEDK is strong at every start size | advisor (about 65%) |
| Q4 | b₁ > 0 by the run's end in at least half the KF3 runs | the gate checks showed b₁ growing under KF3 (disclosed) |

**Exploration disclosed.** The gate checks ran short KF3, NN and SEEDK runs (up to seven steps from 12 bracketings) and showed b₁
rising above zero under KF3 and SEEDK. That is how W1's first version was found wrong before this freeze.

The advisor was consulted before this freeze: it corrected W1, separated the presentation-dependent from the
presentation-independent readings, proposed the filled knot and the word "even knot set", and gave Q3's estimate.
