# Closure of the two-bit screening epic

Status: Proved

Ticket `TWO-BIT-SCREEN-20261105-001Z`, 2026-11-05.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/TWO-BIT-SCREEN-20261105-001/two_bit.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: a Fano atom is a Fano piece; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The elimination closure behind creation is a tetrahedron rule. | new; proved | A, §1 |
| 2 | An intact Fano side attached at a line never removes creation: new knots off it are the closed space's, generated knots through it have generated port shadows, no crossing knot meets two hidden classes. The same holds for a pendant line. | new; proved | A, §2–3 |
| 3 | That the side never adds creation reduces to the pendant-line statement (one new point on one new line never adds creation), conjectured on 117,344 cases. | new; reduction proved, statement computed | A, §4 |
| 4 | The pendant-line statement is neither local nor a consequence of the knots alone, and the twin statement is false; elimination through the gluing line's points suffices. | new; computed | A, §4 |
| 5 | A point on two or three new lines through a line's points can create (8 of 27 profiles); subcube points never did; knot-space sides tried have only subcube points. | new; computed | A, §5 |
| 6 | Contraction theorem in Fano trees: chain creation implies creation; equality when the rest emits toward the path. | new; proved | B, §1 |
| 7 | Block lemma: every Fano piece of a Fano tree is a block of mutual creation. | new; proved | B, §2 |
| 8 | The touching rule: between Fano pieces, a removal creates at a line exactly when that line touches its Fano piece's cut toward the removal (all chains computed, distances one to three). Its creating half holds in every Fano tree at distances one and two. | new; creating half proved, rest computed | B, §3 |
| 9 | Non-creation at non-touching lines holds in every chain and in four 25-point trees; distance three follows the rule on paths of four Fano pieces. | new; computed | B, §4 |

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): prove the pendant-line statement.
- **The plan.** Start from the computed fact that eliminating through the gluing line's points suffices.
- **What a proof would give.**
  - The two-bit screening lemma for Fano sides.
  - Every non-creating entry of the dictionary at distances one and two.
  - Equality in the contraction theorem.
- **Alternative.** The bridge to proof complexity (2/3), still the leading alternative for the next arc.

The table is in the decision note.
