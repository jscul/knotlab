# Pre-registration: where groups of three take over

Epic `EXPLOSIVE-20261119-001`, ticket `EXPLOSIVE-20261119-001B`, 19 November 2026, by Claude, on the coordinator's go-ahead for
`DEAD-CAP-20261119-001#1`. Goal G17.

## The question

Outside the proved class, (S3) fails. A round-1 group of three is exactly a cycle of three blocks: three live knots pairwise in
three different blocks, none holding all three (DEAD-CAP Lemma 2). BREAK-EDDIES found an explosive kind there:
- counts leap (80, 32, 31, 465, 4,495, 31,465);
- the largest group jumps or falls back;
- its known shapes have knots of six or seven places.

**The framing (A110, the owner's direction of 19 November).** Blow-up is expected in an unlimited structure. It is not a defect to
avoid, and the program does not seek harmonies or any other restriction to escape it. So the study does not ask how to avoid the
explosive kind. It asks two things:
- what a sample of this kind typically shows;
- whether the kind has its own regularity, or is where finite description ends.

Concretely:
- What object replaces the unrolled map once a group of three exists?
- Is the growth then exponential, faster, or does it change kind with size?
- Can "grows without bound" be shown or refuted for the smallest case?

## The object: the filled map

The **filled map** is X⁺'s incidence graph with a 2-cell glued on every cycle of three blocks. It is read in two steps:
- **Betti numbers.** b1 and b2 over GF(2), per piece, with b2 the number of cells less the rank of their boundaries.
- **The filled reading.** If every piece has b1 = 0, the start is read as a tree start, with each live knot's rays taken from its
  true round-1 demand (a group of three counting once). The start's dimension is the most rays in a piece, a finished piece
  counting two when there are two or more pieces; "closes" if nothing remains. If some piece keeps a cycle (b1 ≥ 1), the reading is
  "cycle left".

The advisor's argument for round 1: a junction is a cone over its parents. Three pair junctions leave the cycle hollow, while one
three-parent junction cones it off, which is gluing the 2-cell. Beyond round 1 this is not proved.

## Exploration before the freeze (disclosed)

- **The touch census** (at most five knots and five places).
  - 389 starts do not stall, satisfy (S4), and hold exactly one cycle of three blocks. The filled reading gives every one's
    measured class: closes, or dimension 1, 2 or 3. Their largest group in rounds 1–20 is 3 to 6.
  - 82 more hold 3 or 6 such cycles. All fill to b1 = 0, and all close or grow polynomially; 8 reached the junction cap.
- **Smoke runs** of the samplers, with seeds marked "smoke".
- **The calibration** of the class rule on BREAK-EDDIES's reference shapes, to 12,000 junctions: `pilot/calibration.json`, run
  after the advisor and before the freeze.
  - Two triangles joined once read exponential-like, and all four starts of two triangles joined twice read explosive.
  - Of the three-regular six-knot starts, one reads explosive and two undecided (stopped by the child's limit).
  - Every reference shape keeps a cycle after filling.

## Populations (frozen, seeded by case id)

| Population | What | Size |
| --- | --- | --- |
| cap5 | random starts of 6–12 knots within five places, dead knots allowed, kept when they do not stall, satisfy (S4), and hold at least one cycle of three blocks | 300 per knot count |
| cycle5 | the same, kept only when some piece's filled map keeps a cycle (b1 ≥ 1): the stratum where filling could fail | up to 100 per knot count |
| cap7 | the same within seven places, 6–10 knots | 200 per knot count |
| census | every census start that does not stall, satisfies (S4) and holds a cycle of three blocks (explored, so not blind) | 471 |
| ref | BREAK-EDDIES's reference shapes, grown to 40,000 junctions | 9 |

Each start is grown by the engine to round 20, or to 6,000 junctions, recording its count and largest group every round. The
growth runs in its own child process, limited to 2.5 GB and 30 s (the calibration found single reference shapes above 8 GB). A
stopped child keeps its rounds, and its outcome is "resource".

## Classes (exclusive, in this order)

| Class | Rule |
| --- | --- |
| closes | the growth ends |
| dimension D (period q) | the D-th differences at lag q vanish on the last max(4, D + 3) counts (q = 1, 2, 3; D = 1 to 8) |
| explosive | some round-over-round ratio is at least 3 at round 4 or later, faster than any rate in the proved class within five places (DEAD-CAP's fastest is 2.383) |
| exponential-like | the last five ratios lie within 15% of their mean, and the mean is above 1.05 |
| undecided | cut by the junction cap, the child's limits or the horizon before any of these |

The largest group per round is reported separately, not used to class.

## Predictions

| # | Prediction | Falsified by |
| --- | --- | --- |
| X1 | On every start with filled b1 = 0 whose class is decided, the filled reading equals the measured class (dimension or closes) | one start |
| X1b | (risky) On every start with filled b1 ≥ 1 whose class is decided, the growth is neither polynomial nor closing: a kept cycle makes it exponential-like or explosive | one start |
| X2 | (risky) Within five places (cap5 and cycle5), no start is explosive | one explosive start |
| X3 | Within seven places (cap7, fresh starts only), at least one start is explosive | none |

**Readouts (no prediction):**
- **Each explosive start's features.** The advisor's three-way readout:
  - a filled map that keeps a cycle running along a block of a group;
  - b2 ≥ 1, an enclosed void;
  - two groups of three sharing a point or a block.
- **The smallest explosive start found** (fewest knots, then fewest places), with its largest group per round. Whether that group
  grows without bound can only be measured here, within reach.
- **The share of each population left undecided.**

## What would follow

- **X1 and X1b hold.** The filled map replaces the unrolled map: groups of three behave as filled cells, and growth is polynomial
  exactly when filling leaves no cycle.
- **X2 holds and X3 holds.** The explosive kind needs knots of six or more places, so it lies outside the five-place cap.
- **X2 fails.** The cap does not exclude it, and the smallest explosive start within five places is the entry point.

Either way, the result is a description of what samples of each kind show. Nothing here treats the explosive kind as an error.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze.
- **What it argued.**
  - It gave the round-1 cone argument for filling.
  - It predicted that explosion comes from a cycle that survives filling and runs along a group's block, not from b2 or from
    overlap at a point.
  - It counted two triangles joined twice as b1 = 1 after filling.
- **What it asked for, all adopted:**
  - D + 3 counts per degree, and lags;
  - explosion judged on counts, with groups reported apart;
  - exclusive classes;
  - calibration on the reference shapes;
  - the cycle5 stratum;
  - X3 on fresh starts only;
  - X1b, stating the filled prediction for b1 ≥ 1.
