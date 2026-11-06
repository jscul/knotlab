# Selection leaves a hub, and selected spaces glue into knot spaces

Status: Proved

Ticket `HUB-GLUE-20261102-001A`, 2026-11-02.

## Question

- **The observation** (TOP-LAYER closure). When a knot's space loses a line, the line's three points become tied. The knot's spaces are
  glued from pieces along such lines (THREEFOLD-GRAMMAR).
- **The question.** Is selection's leftover exactly the gluing interface, and does gluing selected spaces along it build the knot's
  spaces?

## Dependencies

- **`NATIVE-PATHS-20261101-001A`.** At a 3-edge cut of a knot space, the point side accepts an antipodal pair {v, v̄} and the line
  side its complement.
- **`THREEFOLD-SPACES-20261030-001`.**
  - The dictionary: not 2-colourable ⟺ minimally so ⟺ sign-nonsingular (SNS).
  - The block lemma: a Fano block forces its ports equal.
  - Splices.
- **`THREEFOLD-GRAMMAR-20261030-001`.** Fano atoms in planar Pfaffian glue: tight cuts, braces, decoration, 4-sums.
- **`MUTUAL-SELECTION-20261031-001C`.** The census.

## Setting

- **Knot spaces.** A knot space is a connected cubic triple system H (n points, n lines) with a signing s for which the signed knot,
  NAE(x_p ⊕ s_(L,p)) on every line L, has no solution.
- **Splices.** The splice of H1 at a line L into H2 at a point q is built in three steps.
  - Remove L and q.
  - Join the i-th point of L to the i-th line through q.
  - Keep the old signs, and choose the three new ones.
- **Cuts.** In the incidence graph a 3-edge cut has a point side (one more point than lines). All three cut edges meet its points
  (KNOT-COMPOSE A balance).
  - **Ports and slots.** The points they meet are the ports, and the lines across are the slots.
  - **Simple cuts.** The cut is simple when the ports are three distinct points and the slots three distinct lines.
  - **Contractions.** Close the point side with a new line through the ports, and the line side with a new point on the slots.

## Theorem

1. **The leftover is a hub.** In a knot space, removing a line L leaves solutions on which L's three points take exactly the two
   all-equal patterns under L's signs. They are tied, and H − L with ports L is the point side of a 3-edge cut.
2. **Splices of selected spaces are knot spaces.** For every knot space H1, line L, knot space H2 and point q, the splice is a knot
   space for exactly one switching class of the new signs: two of the eight choices, a choice and its complement.
3. **Simple cuts are splices.** Both contractions of a simple 3-edge cut of a knot space are knot spaces. So the cut is the splice of
   two selected spaces along a leftover hub.
4. **What this builds.** With THREEFOLD-GRAMMAR:
   - every knot space is assembled by splices from Fano atoms and planar glue;
   - its pieces may carry repeated incidences, as the doubled square does, which are the non-simple cuts;
   - non-planar glue also needs 4-sums.

## Proof

**Item 1.**
- **The removal is solvable.** A knot space fails minimally (the dictionary; with signs, THREEFOLD-GRAMMAR's twisted dictionary), so
  H − L has solutions.
- **L is violated in each.** A solution of H − L satisfying L would solve H, so in every solution L's signed values are all equal.
- **Both patterns occur.** The solutions are closed under complementing every value, since the knot is symmetric under it.
- **Tied.** Any two points of L take exactly two of their four value pairs.
- **The cut.** In a splice the incidences of L are the cut edges, and NATIVE-PATHS A names exactly {v, v̄} as the point side's patterns.
  ∎

**Item 2.**
- **SNS and Pfaffian.** The signed knot fails iff the signed incidence matrix is SNS, that is, iff the signing is a Pfaffian signing
  of the incidence graph (THREEFOLD-SPACES; NATIVE-PATHS C).
- **Tight cuts.** A 3-edge cut of a cubic bipartite graph is tight: every perfect matching uses exactly one cut edge, the surplus point
  of the point side.
- **Contractions.** A bipartite graph with a tight cut is Pfaffian iff both contractions are (Little; Vazirani and Yannakakis). Its
  Pfaffian signings are those of the contractions, with signs chosen on the cut edges.
- **The count.** Complementing all three cut signs is the switching of the whole point side: inside edges flip twice, cut edges once.
  So the working choices come in complementary pairs, and check 3 finds exactly one pair in every case. ∎

**Item 3.** As in item 2, the contractions of a tight cut of a Pfaffian graph are Pfaffian, with the cut signs moved onto the new
edges. They are simple triple systems exactly when the cut is simple. ∎

**Item 4.**
- **The decomposition.** THREEFOLD-GRAMMAR: tight-cut decomposition into braces, with leaves that are Fano pieces and glue that is
  planar.
- **Non-simple cuts.** Its decoration lemma covers the cuts whose contractions repeat a point.
- **Non-planar glue** needs RST's 4-sums. ∎

## Checks

`check.py` (`result.json`, about a minute):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | The census knot spaces. | 8 (4, 6, 7, 7, 8, 8, 8, 8 points), every failure global |
| 2 | Leftovers in the census spaces. | every one of 56 removals ties its line: exactly the two all-equal patterns |
| 3 | Splices of every ordered pair of census spaces up to 13 points, at every line and every point. | 1216 splices, each failing globally for exactly 2 of 8 sign choices; leftovers of 32 of them checked in full |
| 4 | Every nontrivial 3-edge cut of the census spaces and of their splices up to 10 points. | 14 cuts: 10 simple, all contracting to two knot spaces; 4 with a doubled port or slot (non-simple contractions) |

## What this does not establish

- **Whether emergence crosses the glue.** That is tickets B and C.
- **Non-simple cuts and 4-sums.** They are covered by THREEFOLD-GRAMMAR, not re-checked here.

## Novelty

- **Classical or ours already.** Item 1 is the block lemma and NATIVE-PATHS A, read from selection. Items 2–3 are tight-cut theory for
  Pfaffian graphs. Item 4 is THREEFOLD-GRAMMAR.
- **New here.** The reading: selection's leftover is exactly the gluing interface. Novelty is low; it is the setting for B and C.
