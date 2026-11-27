# One layer up, made by growth?


> **Referee R1: refuted, one Block** ([report](referee-R1/report.md); notice in [decision.md](decision.md)). Ordinary
> growth makes the step one layer up on a built ten-knot start, both births needed. U_A's sums are modulo two.

`UPPER-GROWN-20261127-001`. It was opened after `RING-BOND-20261127-001`'s referee found the layer above. On a closed
start of twelve three-place knots, six agreements on disjoint carriers, A0, A1, B0, B1, C0 and C1, are bound by eight
clauses: no one A, one B and one C all agree. The agreements of agreements [A0 = A1], [B0 = B1] and [C0 = C1] then take
seven of eight words. The referee also found an example on the grown ring at round 3, but its agreements overlap. The
question: do grown stages hold such a step with disjoint carriers and a birth's law needed? And how common is it where
it does occur?

## Definitions (`boxes.py`)

A **box** is six agreement readings on pairwise disjoint carriers of two or three distinctions, with three conditions:
- each of its eight triples (Ai, Bj, Ck) is a bond in RING-BOND's sense;
- each of those bonds misses exactly one triple;
- the missing triple is (a_i, b_j, c_k), with one value fixed per reading.

The upper readings are U_A = [A0 + A1 = a_0 + a_1 + 1], and likewise U_B and U_C. They cannot all hold. A solver reads
the stage's own image of (U_A, U_B, U_C), and which laws its missing words need (each law removed in turn).

## Already known before the freeze

- **Proved (the earlier referee's argument).** Each ordinary birth has a fresh distinction of its own, at which it can
  satisfy its law. So every funded round keeps the projection of the allowed states onto the distinctions present before
  it. A relation among readings of earlier distinctions never changes afterwards. A box that needs a birth's law must
  therefore read a distinction born at or after that birth.
- **Explored** (not evidence for the predictions):
  - The grown ring has no box at rounds 1 to 4 (full search: 9, 411, 9,121 and 44,483 bonds).
  - The twelve-knot witness has 90 boxes, each upper image missing one word.
  - Removing one of the witness's knots, or opening knots with a loose distinction, removes its upper clause, and growth
    through round 3 does not bring it back.
  - A ten-start census pilot (seed 1, excluded below) has no box at rounds 0 to 2.
  - One of the nineteen ten-point closed systems has no box.
- **Advisor:** not consulted. The advisor model was over its usage limit at the freeze, and the referee stands in
  alone.

## Frozen predictions

**Closed systems** (`cubic.py`). A connected system of three-place knots in which every distinction is held twice is a
connected cubic graph: knots are its points, distinctions its links. Seeded draws reach every simple connected cubic
graph with 4 to 12 points: 1, 2, 5, 19 and 85, the known counts (OEIS A002851). Every such graph is read once.
- B1. No graph with 8 or fewer points has a box.
- B2. No graph with 10 points has a box.
- B3. With 12 points, the witness's graph and at least one other have boxes.
- B4. Every box on these graphs has an upper image missing exactly one word.

**Grown stages** (`census_boxes.py`). A held-out sample of 1,000 census starts (seed 20261128, the 10 pilot starts
excluded) at rounds 0 to 2. The full search runs where a stage has at most 19 distinctions; larger stages use the local
search with holders ≤ 4 and report it.
- G1. No stage of the sample has a box.
- G2. Consequently no box needs a birth.

The opportunity is reported with it: the stages with at least 12 distinctions and at least 8 bonds.

## Scaffolds (register entry added with the results)

- The box form (eight single-triple bonds with a product missing word), and the carrier cap and disjointness inherited
  from A308.
- The holder cap on large stages.
- For the closed systems, every isomorphism class counted once.

## Compute

About 1 minute per twelve-point graph, in 8 chunks. Census starts take about 5 seconds each through round 2, in 8
chunks. Each run has a memory cap of 6G and a 45-minute stop, and anything stopped is reported as not run.
