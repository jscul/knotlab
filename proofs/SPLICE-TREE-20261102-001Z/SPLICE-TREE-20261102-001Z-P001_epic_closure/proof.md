# Closure of the splice-tree epic

Status: Proved

Ticket `SPLICE-TREE-20261102-001Z`, 2026-11-02.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/SPLICE-TREE-20261102-001/splice_tree.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In a knot space assembled along a tree of simple 3-edge cuts, removing a line holds the cuts that point toward it and opens those that point away. Beyond a held cut nothing depends on the removal. | a corollary of HUB-GLUE A–C; the orientation reading is new | A |
| 2 | The knots crossing only held cuts are exactly the iterated 2-sums, through held hubs, of knots crossing no cut. So new emergence lives only across opened cuts. | new in this relational setting; the matroid analogue is standard | B |
| 3 | Opened cuts interact: new knots are carried across opened cuts and created jointly by two or three of them. Touching hubs, a shared port on the removed line and the removed line's hub each fail to decide this on 96 chains. | new | C, items 1–2 |
| 4 | Every joint knot has three or four points, and chains of K4^(3) pieces create nothing. | new; finite | C, item 3 |
| 5 | A derivation by eliminations never uses a knot larger than its result, so bounded closures are exact within their bound. HUB-GLUE C's count is reproduced with tie classes. | elementary; a verification | C, lemma and item 4 |

## Pending the owner

- **Still open.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (3/3): emergence needs a handle.
- **The conjecture.** At an opened cut, new emergence needs both a knot on the hub (six patterns) and a non-planar removed side, so planar
  glue only composes.
- **The scout behind it.** 0 of 560 removals with a planar side and 100 of 160 non-planar six-pattern removals in the census.
- **First test.** Planar knot spaces beyond the census.

The table is in the decision note.
