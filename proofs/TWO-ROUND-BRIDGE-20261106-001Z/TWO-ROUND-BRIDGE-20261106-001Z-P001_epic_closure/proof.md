# Closure of the two-round bridge epic

Status: Proved

Ticket `TWO-ROUND-BRIDGE-20261106-001Z`, 2026-11-06.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/TWO-ROUND-BRIDGE-20261106-001/two_round_bridge.md`, with the comparison table and provenance.

Words (2026-11-11). Reworded under the owner's language rule: a three-fold or knot space is now a three-regular
contradiction, its lines knots and its points distinctions, and a Fano atom a Fano piece (Intuitions guide, Glossary). The
mathematics is unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Two not-all-equal constraints sharing two variables resolve at width 3 exactly when they relate the shared pair differently; the resolvents are the implied constraints. | folklore; proved | A, §1 |
| 2 | At a gluing knot, the knot closure's crossing knots are exactly the width-3 resolution consequences of the one-sided implicates on at most three variables. Each is derived in depth one or two, resolving only on the knot's variables, along a linear chain from one far knot. | known-with-delta; proved (exhaustive local data) | A, §2 |
| 3 | Every new crossing knot (creation) is implied by the same implicates and needs width exactly 4, in depth 2. | new; proved (exhaustive local data) | A, §3 |
| 4 | The rule's literal pairs step is usually not a resolution step (1,645,912 of 1,685,232 local instances); a near-knot route always is. | new; proved (exhaustive) | A, §2 |
| 5 | Refutations compose over the handle tree at constant cost per Fano piece (width at most 5, at most 80 clauses). | standard technique; proved | B, §1 |
| 6 | On a planar Kasteleyn core the contradiction is Euler's count: one agreeing corner per satisfied knot, at least one per face, two more faces than knots. Assignments modulo complement are the parity solutions on the knot–face graph. | known-with-delta; proved | B, §2–3 |
| 7 | Sherali–Adams of level max(3, d) refutes planar signed contradictions with at most d distinctions per face: level 3 on the octahedral family, constant level on its three-regular decorations. | known-with-delta (planar max-cut duality); proved | B, §4 |
| 8 | Every three-regular contradiction has resolution refutations of size n^{O(1)}·2^{O(√n)}. | standard technique; proved | B, §5 |
| 9 | On the octahedral family (one brace for every k), solver costs grow 7 to 50 times per step in k; resolution size 2^{Ω(√n)} is conjectured. | measured; conjecture | B, §6 |

## Answer

- **The standard system is resolution.** "Depth two through a cut" bounds resolution depth (one or two) and width (3; 4 for creation)
  across a three-variable interface, relative to the one-sided implicates.
- **It composes over the handle tree.** It does not compose into a global resolution bound: the glue carries the Euler count, which
  Sherali–Adams sees at level 3, while resolution has only the treewidth bound.
- **Against Tseitin.** Three-regular contradictions are the integer counterpart of Tseitin's parity.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): is the sphere's Euler count hard for resolution?
- **The question.** Prove resolution width Ω(√n) for the octahedral three-regular contradictions, from a mobility lemma for the violated knot.
  Then attempt size 2^{Ω(√n)}.
- **Alternative.** Polynomial calculus over F2 or Res(⊕), where the count is invisible to parity (1/3).

The table is in the decision note.
