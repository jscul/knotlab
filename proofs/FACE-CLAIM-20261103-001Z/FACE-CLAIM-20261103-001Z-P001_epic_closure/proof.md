# Closure of the face-claim epic

Status: Proved

Ticket `FACE-CLAIM-20261103-001Z`, 2026-11-03.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/FACE-CLAIM-20261103-001/face_claim.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: plane glue and plane sides are planar; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Reading lemma: the merged face's skip lies on the arc opposite the odd port (relative to the all-agree pattern fixed by the arc constants). So an own arc is barred exactly when its two ports disagree, and whenever they agree the opposite face of the third port is claimed by its line. Barred faces fix two points of each line. | new | A, §1 |
| 2 | Claim lemma: a frozen line claims an own arc from one port pattern per value, and an opposite face from at most two, which share the other two ports. | new | A, §2 |
| 3 | Claim rule: a handle creates at a frozen line exactly when a pair of its points freezes it and neither point alone excludes either claim. The route direction is proved; the converse is computed against exact creation (728 cases) and the pipeline (26,634 far lines). | new; converse finite | A, §3 |
| 4 | Census of 305 handles from 24 spaces: the faces used depend only on the bottom port. Nine signatures occur; the claim rule and its port form decide all 3,660 (case, face) pairs. | new; finite | B, §§1–2 |
| 5 | Fano plane: pairs pin the class of the met port, and each single point removes one pattern per other class. So it never uses an own arc (proved) and uses the opposite face at every port (computed). | new | B, §3 |
| 6 | Census 58: it uses the own arc exactly when the bottom port is 0 or 5. | new; finite | B, §4 |
| 7 | Frozen region: creation needs a frozen line. Unit propagation finds the whole frozen region on generic pieces, where it is the faces around the point; it misses rigid extensions at 8 junction points of an arm-on-grid piece. | new; bound proved | C, §§1–3 |
| 8 | Counterexample: at one junction point all three handles create off the faces around the point, along the arm's far long face. This is exact on a 21-point piece (12 instances). The PHASE-HALO law of the faces around the point is false. | new; corrects PHASE-HALO A | C, §4 |

## Pending the owner

- **New.** Whether to supersede or qualify `PHASE-HALO-20261103-001-D001`. Its generalization, that the reach is set by the opposite
  faces' size, is refuted by conclusion 8; its tested facts stand.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): the frozen region by heights, and rigid strips.
- **The lemma.** Prove that a port pattern freezes exactly the points whose height difference to the ports cannot vary.
- **The junction.** Explain its extension as a rigid strip.
- **The test.** Build planar pieces with long rigid strips, and see whether the halo follows them or they stay rigid.
- **Alternatives.**
  - The converse of the claim rule as a theorem (2/3).
  - The structure of the nine signatures (1/3).
  - The screened line-attached handle (1/3).

The table is in the decision note.
