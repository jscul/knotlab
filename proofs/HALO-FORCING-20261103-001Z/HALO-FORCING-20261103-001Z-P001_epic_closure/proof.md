# Closure of the halo-forcing epic

Status: Proved

Ticket `HALO-FORCING-20261103-001Z`, 2026-11-03.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/HALO-FORCING-20261103-001/halo_forcing.md`.

Words (2026-11-11). The statements use the literature's words for triple systems, gadgets and drawn substrates: a line is a
knot, a point a distinction, a triangle a copy of the knot, and a contact where copies meet a shared distinction (Intuitions
guide, Glossary). Reworded under the owner's language rule: plane glue and plane sides are planar; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Route lemma: a three-point crossing knot at a gluing line is generated when one point of the line separates it, or a pair of the line's points (forced by the near pair, covered by the far point's excluded block) carries a two-step elimination. | new; generalizes PLANAR-COMPOSE A | A, §1 |
| 2 | With the Fano plane attached at a point of five planar pieces and opened, the new knots are exactly the candidates without a route. Creation is a function of the transfer (840 classes). | new; finite | A, §§2–3 |
| 3 | In a point split the solutions are the corner matchings, with double edges at the port lines. This clarifies HANDLE-LOCALITY A's wording; its conclusions are unaffected. | clarification | B, §1 |
| 4 | Heights decide the transfer exactly (shortest paths and parity halving), in polynomial time. | new; classical ingredients | B, §2 |
| 5 | The halo of an opened handle reaches the farthest gluing line of every ladder (prisms to 80 points). | new; finite | C |
| 6 | On grids (subdivided-octahedron duals to 256 points) the halo stops at distance 3. Grid lines at distance 7 or more are exactly independent of the handle's point, while ladder lines stay forced to two patterns. | new; finite | C |
| 7 | Open: the criterion's converse beyond small spaces, and proofs of the ladder law and the grid bound. | open | C |

## Pending the owner

- **Still open.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): creation and dimer phases.
- **The test.** On planar pieces where frozen and liquid parts meet, is the halo exactly the frozen region joined to the handle?
- **The proofs.** The ladder law and the grid bound.
- **Alternatives (1/3 each).**
  - The screened line-attached handle.
  - The planar reduction lemma.
  - Other and several handles.

The table is in the decision note.
