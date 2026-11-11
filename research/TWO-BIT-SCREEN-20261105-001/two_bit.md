# The two-bit screening lemma

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction; a knot space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `TWO-BIT-SCREEN-20261105-001` (program topology), 2026-11-05.

## The question

- **The approval.** The owner said "Yes, proceed." to the updated recommendation: make the two-bit screening lemma the next epic.
- **The aim.** A theorem that native creation reads the directed handle tree of every three-regular contradiction built from Fano pieces, with exact
  checks on the existing families.
- **The question.** Does a side split from a contradiction at a point act as its line for creation, as it does for solutions? Every
  receiving atom is such a side, so BRACE-TREE's dictionary needed this to become a theorem.
- **Kept in view.** Proof debt: rules need proofs before more is built on them. Wording: "the tree can be recovered from creation by a
  short rule", where creation rests on the chosen far sides.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | The elimination closure behind creation is a tetrahedron rule: four classes with two derived knot triples have all their knot triples derived. | proved | A |
| 2 | **No loss.** An intact Fano side never removes creation. The new knots off the side are those of the closed space, generated knots through it have generated port shadows, and no crossing knot meets two hidden classes. The same holds for a pendant line, one new point on one new line through two near points. | proved | A |
| 3 | **Reduction.** That an intact Fano side never adds creation follows from the pendant-line statement: a pendant line never adds creation. | proved reduction; statement conjectured (117,344 cases) | A |
| 4 | The pendant-line statement is neither local (320 Fano-side configurations) nor a consequence of the knots alone (42 misses, all where the closed side creates). Two knots forced by one assignment need not share their status (434 of 67,702). Eliminating only through the gluing line's points loses nothing (9,225 of 9,225). | computed | A |
| 5 | **The bound is sharp.** A point on two or three new lines through a line's points, such as the ports' majority, creates where the space without it does not. The 19 subcube profiles never do; every knot-space side tried has only subcube points. | computed | A |
| 6 | **Contraction theorem.** In a Fano tree, creation in the chain of two atoms implies creation in the whole space, with equality when the rest emits toward the path. | proved | B |
| 7 | **Block lemma.** Every Fano piece in a Fano tree is a block of mutual creation. | proved | B |
| 8 | **The touching rule.** Between atoms, a removal creates at a line exactly when that line touches its atom's cut toward the removal; the removed line's role never matters. This is BRACE-TREE's dictionary in one rule. It holds on all 294 two-atom and 576 three-atom gluings and on four-atom paths (all 36 places up to distance three). Its creating half holds in every Fano tree at distances one and two. | creating half proved at distances one and two (exhaustive chains + 6); the rest computed | B |
| 9 | Non-creation at lines that do not touch holds in every chain and in four 25-point trees (2,148 pairs). Distance three follows the touching rule on 16 four-atom paths. | computed | B |

## Answer

- **Does an intact side act as its line for creation?** Half of it is now a theorem. Attaching an intact Fano side at a line never
  removes creation, and the other half reduces to one clean statement about a single new point on a single new line. That statement
  held on all 117,344 cases tried, including random systems unrelated to contradictions, but it is not proved.
- **The theorem about the handle tree.** For spaces built from Fano pieces alone:
  - **Proved.** Each atom is a block of mutual creation. A removal creates at every line, at most two atoms away, that touches its
    atom's cut toward the removal. Cut directions are read correctly wherever the rest of the space emits toward the cut.
  - **Not proved.** "The tree can be recovered from creation by a short rule" still needs two things: the pendant-line statement, for
    non-creation, and a transfer along chains, for atoms three or more apart.
- **Proof debt.**
  - **Discharged.** The block lemma for atoms attached at a point, and the creating halves of the dictionary at distances one and two,
    were computed and are now proved.
  - **Remaining.** Two named gaps, where before the whole dictionary was computed.

## Reading

- **One line is the limit.** A hidden point that hangs on one new line through two visible points is conjectured never to add a new
  knot. One that hangs on two such lines can. The first passes a single relation between two points; the second can encode a parity or
  a majority of three, a two-bit quantity no single visible point carries.
  - **Why the Fano side is safe, in the reduction's terms.** Each of its hidden points, seen alone, is a point on one line through two
    ports.
  - **"Two bits" made precise.** The lemma's name now has a meaning: a side is screened when everything it hides is one-line
    information.
- **A line is seen from a direction if it touches the cut facing that direction.**
  - **The rule.** The whole atom-only dictionary collapses into this: a removal elsewhere creates at a line exactly when the line
    touches its atom's cut toward the removal.
  - **What it reads.** The rule reads the tree locally, at the receiving line. A cut's direction is visible as which side presents
    all its lines to the other: an emitting atom does, a receiving atom presents only its three cut lines.
- **Creation is a bootstrap.** New knots are crossing triples that a two-out-of-four rule on tetrahedra cannot reach from the
  non-crossing ones.
  - **Why the remaining statement is hard.** It is not a property of the knots alone: seeding every other knot is not enough. Which
    knots the base actually reaches matters.
- **Doctrine.** Hidden points are witnesses in the canon's sense: quantified away, never supplying an input. The no-loss theorem says
  that quantifying away a Fano side's witnesses loses no emergence.

## Literature

- **Ours.**
  - The one-bit screening lemma and interface lemma (HANDLE-LOCALITY).
  - The join method and three-point locality (HANDLE-EMERGENCE B).
  - The elimination closure (SPLICE-TREE C).
  - The dictionary and source rule (BRACE-TREE).
- **Classical.**
  - Tight-cut decompositions (Lovász).
  - Bootstrap percolation (the tetrahedron rule is a bootstrap closure on a 3-uniform hypergraph).
  - Principal extensions of matroids (a new element in the closure of two old ones), the nearest classical analogue of a pendant line.
    None was found stating these results.
- **New here.** The tetrahedron form, the no-loss theorem, the pendant reduction and its sharpness, the contraction theorem and the
  proofs of the block lemma and the creating entries.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the two-bit screening lemma | **Status:** Partially successful | **Proved.** No loss: an intact Fano side never removes creation, and the same for pendant lines. The rest of the lemma reduces to one statement, and that reduction is proved. The contraction theorem, the block lemma, and the creating half of the touching rule at distances one and two, all in Fano trees. **Unresolved.** The pendant-line statement (117,344 cases, none against). |
| Local direction — screening in Fano trees | Continue, one gap | **The gap.** The pendant-line statement is the only gap for distances one and two. **Known about it.** It is not local and not a consequence of the knots alone, but eliminating only through the gluing line's points always suffices. |
| Broader exploration — reading the handle tree | Advanced; two named gaps | **The gaps.** Non-creation (pendant line) and atoms three or more apart (a transfer along chains; four-atom paths are deterministic). Plane glue and non-Fano handles are outside the proofs. |
| Long-term goal — topology from native emergence | Capability strengthened | **Gained.** Native creation provably sees every Fano piece as a block, and sees the creating side of every cut. **Missing bridge.** That it sees nothing else (non-creation); the source rule stays computed. |
| Next recommendation — prove the pendant-line statement | **Next step:** Continue. Attempt a proof that one new point on one new line through two near points never adds creation, starting from the computed fact that eliminating through the gluing line's points suffices. If that fact is proved, creation becomes a statement about how near pairs pin the gluing line. | **If yes.** The two-bit screening lemma for Fano sides, every non-creating entry at distances one and two, and exact equality in the contraction theorem. **If no.** A counterexample would locate the first space where one line of hidden information creates. **Alternative.** The bridge to proof complexity (2/3), still the leading alternative for the next arc. |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** A crisp, side-free statement, true on 117,344 cases, including random systems; it is the single remaining gap below distance three. **Main uncertainty.** Seeding every other knot does not suffice, so a proof must follow which knots the base reaches, a bootstrap problem. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The pendant-line statement and the gluing-line reduction. **Stop when** it is proved, refuted on a counterexample, or its unproved core is isolated past the gluing-line reduction. |
