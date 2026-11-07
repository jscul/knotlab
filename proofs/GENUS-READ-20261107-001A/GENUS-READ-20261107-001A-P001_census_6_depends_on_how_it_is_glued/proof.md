# Census 6 depends on how it is glued

Status: Proved (exhaustive symmetry computation; the dependence measured on a fixed sample)

Ticket `GENUS-READ-20261107-001A`, 2026-11-07.

## Question

- **How it was found.** While proving that FAR-READ B's rule reads every Fano tree, a composition model of creation inside an atom
  disagreed with an exact creation map. The two differed only in the order in which a gluing line's points were written.
- **The question.** Does the creation map depend on how a line's points happen to be listed? If so, which far sides depend on it, and
  why?

## Dependencies

- **`FAR-READ-20261106-001A`.** The saved maps (`far_lib.py`).
- **`GLUE-READ-20261106-001A`.** The engine (`port_lib.py`, which loads `transfer_lib.py`). It uses PENDANT-LINE A's local engine and
  HANDLE-LOCALITY B's `far_side`, both bound by hash.

## How a far side is glued

- **The far gadget.** The creation test at a gluing line b splits a census far side at its point 0 (`far_side`, `pt=0`).
- **The order.** It joins the i-th line through that point to the i-th listed point of b, choosing the first sign twist that leaves b's
  six patterns.
- **The question it raises.** The order of b's points is not part of the space. It is how the line was written down.

## Theorem

Write F for a census far side and Stab for the signed symmetries of F (point permutations preserving lines, up to flipping points and
lines) that fix its split point.

1. **The three order-free far sides.** For K4^(3), the Fano plane and census 58, Stab permutes the three lines through the split point in
   all six ways. So their verdicts do not depend on the order of the gluing line's points.
2. **Census 6.** Stab permutes those lines in only two ways, so census 6 has three inequivalent gluings at every line.
3. **Census 58's split point.** Census 58 is not point-transitive: its points fall into orbits of sizes 2 and 6. Its far side is
   split at a point of the two-point orbit, a fixed intrinsic choice.

*Proof.*

- **The symmetry counts.** These are exhaustive computations over all point permutations (check 1).
- **Why a full stabilizer gives order-freedom.** Let σ be a symmetry of F that fixes the split point and induces a permutation π of its
  lines.
  - **σ moves the glued space.** It carries the space glued in one order onto the space glued in the order permuted by π.
  - **It preserves what creation looks at.** That is solutions, knots, and the elimination closure, since σ is a signed isomorphism.
  - **So the verdicts agree.** When every π is realized, every order gives the same verdict.
- **Census 6.** It is point-transitive, so the split point does not matter, but its order does. ∎

## Measured (check 2)

The sample is every third saved space and every fourth removal: 64 spaces and 12,626 (removal, gluing line) pairs.
- **The stored order reproduces the stored maps** at all 12,626.
- **The order-free far sides never change.** At all 11,552 non-degenerate pairs, K4^(3), the Fano plane and census 58 are the same at
  every order.
- **Creation never changes.** Whether creation occurs is the same at every order in all 11,552.
- **Census 6 does change**, in 8,046 of the 11,552 pairs.
  - **How often it creates.** It creates at 0 of the six orders in 1,967 pairs, 2 of six in 8,046, and 6 of six in 1,539.
  - **In gluings.** That is none, exactly one, or all three of its three gluings. Exactly two never occurs in this sample.

## The Fano plane alone (check 3)

- **In the stored orders.** Census 6 creates at 14 of the 42 ordered pairs. That is BRACE-TREE A's count.
- **Natively.** By 2-transitivity every ordered pair is the same. Indeed census 6 creates at exactly two of the six orders, one gluing of
  three, at every pair.
- **So BRACE-TREE's count was a pattern of the listing order**, not of the plane.

## The native repair

- **Census 6's entry.** Record the number of its gluings that create, 0 to 3. Equivalently, record the number of orders out of six.
- **The native far-side vector.** It is (K4^(3), the number of census-6 gluings that create, the Fano plane, census 58).
- **The other three are unchanged.**

## What earlier records rest on census 6's listing order

- **BRACE-TREE A.** "Census 6 at 14 of 42" in the Fano plane. Natively it is one gluing of three at every pair.
- **FAR-READ A.** The four strengths at atom lines, and the statements tying K4^(3) and the Fano plane to census 6. They hold in the
  stored orders.
- **FAR-READ B and C (`FAR-READ-20261106-001-D002`).** The four-step rule's split step compares whole vectors, census 6 in its stored
  order included. Ticket B shows that with native vectors it cuts atoms.
- **GLUE-READ A and ATOM-ONE B.**
  - **Far-side statements.** Those about census 6 hold for each fixed order covered by their letters.
  - **Creation statements.** Those about whether creation occurs, and those about K4^(3), the Fano plane and census 58, are unaffected.
- **ATOM-ONE C.** It compared the exact maps with verdicts computed in the same stored orders, so its equalities stand. A Fano atom acting
  as one is checked natively in tickets B and C.
- **Unaffected throughout.** Every statement about whether creation occurs: twins, footprints, the receiving-cut law's creation table,
  transparency, and acts-as-one for creation.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Symmetry at the split point | K4^(3), Fano, census 58: 6 of 6 permutations; census 6: 2 of 6; census 58's orbits 2 and 6 |
| 2 | Measured on 64 saved spaces | stored order reproduces the maps; K4^(3), Fano, census 58 and creation order-free in 11,552 of 11,552; census 6 changes in 8,046 |
| 3 | The Fano plane alone | stored: census 6 at 14 of 42; native: one gluing of three at every pair |

## What this does not establish

- **Exactly two gluings.** It might occur outside the sample.
- **Choosing a better far side.** Whether another census far side would be a better probe is not considered.

## Novelty

- **New here.** The gluing classification and the correction it implies. The far sides themselves are the project's (TWO-BIT-SCREEN,
  BRACE-TREE).
- **Provenance.** Invariance of a gadget's verdict under symmetries of the gadget is standard.
