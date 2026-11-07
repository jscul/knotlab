# The pendant-line statement

Epic `PENDANT-LINE-20261106-001` (program topology), 2026-11-06.

## The question

- **The approval.** The owner said "Yes, let's continue." to TWO-BIT-SCREEN's recommendation: prove the pendant-line statement,
  starting from the computed fact that eliminating through the gluing line's points suffices.
- **The statement.** One new point on one new not-all-equal line through two points of a near side never adds creation.
- **Why it mattered.** It was the only open half of the two-bit screening lemma, and through it of the brace dictionary's
  non-creation entries.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Creation is decided at the gluing line, in two rounds.** The closure's crossing knots are exactly: in round one, {c, x, y} when some z on the line makes {c, y, z} a far knot and {x, y, z} a near knot; in round two, near pairs sharing a round-one point, and two-far knots through a line point. | proved: reduction to local configurations, all 348,376,032 checked | A |
| 2 | Corollaries: the closure reaches its crossing knots within two rounds and through the gluing line alone; a crossing knot is new exactly when its near and far parts fail to meet at a pair of gluing-line points. | proved | A |
| 3 | **One new line never adds creation**, whatever its signs and wherever its two points lie. | proved: from 1, all 347,149,320 local configurations checked | B |
| 4 | **The two-bit screening lemma.** An intact Fano side standing in for a line acts as that line for creation. | proved (TWO-BIT-SCREEN A's reduction + 3) | C |
| 5 | The splitting lemma for atoms attached at points and at lines. | proved | C |
| 6 | **In Fano trees, contraction is exact.** A line creates at another exactly when it does in the chain of their atoms. | proved | C |
| 7 | **The touching rule up to distance two.** A line receives creation from another atom at most two away exactly when it touches its atom's cut toward it. So the brace dictionary up to distance two is a theorem, and every cut is read in its direction. | proved (6 + TWO-BIT-SCREEN B's exhaustive chains) | C |
| 8 | Distance three follows the touching rule on the 16 four-atom paths computed. | computed | C |

## Answer

- **The pendant-line statement is proved.** A single hidden point on a single new line adds no creation.
  - **How.** Ticket A first turns the closure into an explicit two-round rule at the gluing line. A knot through the new point is
    then decided by a handful of classes around the line, and every such configuration was checked.
- **The two-bit screening lemma is complete.** An intact receiving side acts as its line for creation, as it does for solutions, so
  the one-bit and two-bit screening lemmas together contract any untouched side.
- **The handle tree, as a theorem.** In spaces built from Fano atoms alone, the following are proved:
  - native creation keeps every atom whole;
  - it reads every cut in its direction;
  - it fixes every relation between atoms at most two apart by one rule, touching.
- **What remains for the source rule.** "The tree can be recovered from creation by a short rule" now rests on a single gap: a
  transfer along chains of four or more atoms. Plane glue and non-Fano handles remain outside.

## Reading

- **Emergence is selected where the parts meet.**
  - **The two rounds.** A crossing knot is derived exactly when the near side and the far side form knots with the same pair of
    gluing-line points (round one), or share such a point (round two).
  - **New knots.** New knots, the native selection's output, are the crossing constraints that the parts carry together but that do
    not pass through any pair of the line's points. This is the precise form of HANDLE-EMERGENCE's "pin and separate".
- **One line of hidden information is safe; two are not.**
  - **The threshold.** A hidden point that hangs on one new line never adds creation (proved); one on two lines can (TWO-BIT-SCREEN
    A).
  - **Two bits.** The threshold between one and two lines is the "two bits" of the screening lemma's name.
- **A line is seen from a direction when it touches the cut facing it.** Up to distance two, that is now a theorem about native
  creation in Fano trees.
- **Doctrine.**
  - **No space is assumed.** Directions are which side of a cut lost a point. Touching is incidence.
  - **The far sides.** Everything is read through the creation map's four census far sides.

## Literature

- **Ours.**
  - The tetrahedron form and the no-loss theorem (TWO-BIT-SCREEN A).
  - The chains and the contraction theorem (TWO-BIT-SCREEN B).
  - The join method (HANDLE-LOCALITY B, HANDLE-EMERGENCE B).
  - The dictionary (BRACE-TREE B).
- **Classical.**
  - Reducing a global closure to finitely many local configurations is the standard route to a finite verification.
  - Bootstrap closures on hypergraphs.
  - Tight-cut decompositions (Lovász).
  - No statement of these results was found.
- **New here.** The two-round rule, the pendant-line theorem, and the completion of the two-bit screening lemma and of the dictionary
  up to distance two.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the pendant-line statement | **Status:** Successful | **Proved.** The two-round rule at the gluing line (348,376,032 local configurations), the pendant-line statement (347,149,320), and with them the two-bit screening lemma, the splitting lemma for both kinds of atom, exact contraction in Fano trees, and the touching rule up to distance two. |
| Local direction — screening in Fano trees | Practically complete | The dictionary up to distance two is a theorem, non-creation included. Nothing below distance three remains open. |
| Broader exploration — reading the handle tree | One gap for Fano trees | **The gap.** A transfer along chains of four or more atoms, after which the source rule becomes a theorem. **Outside.** Plane glue and non-Fano handles. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native selection provably keeps each handle whole and reads each cut's direction. Where it creates is decided by a two-round rule at the gluing line. **Missing bridge.** Distances of three atoms and more. |
| Next recommendation — a transfer along chains | **Next step:** Continue. Prove the touching rule at every distance in Fano trees. Use the two-round rule: show that an atom between a removal and the gluing line passes the gluing-line meetings through unchanged, or find an inductive step from three to four atoms, checked on all four-atom gluings. | **If yes.** The source rule becomes a theorem: native creation recovers the directed handle tree of every space built from Fano atoms. **If no.** The first distance where the touching rule fails, which would refine the source rule. **Alternative.** The bridge to proof complexity (2/3). The two-round rule says derivations through a cut have depth two, a statement in the language of bounded-depth elimination. |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The touching rule is exact up to distance two and held at all 18 distance-three places. Creation is now decided locally at the gluing line. **Main uncertainty.** Near knots that meet the gluing line can involve classes far down the chain, so locality at the line is not yet locality in the tree. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The touching rule at every distance in Fano trees. **Stop when** it is proved, refuted at a first distance, or reduced to a finite check that is then run. |
