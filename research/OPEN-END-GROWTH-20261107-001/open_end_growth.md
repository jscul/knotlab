# Growth at loose ends

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): an open end is a loose end. Results are unchanged;
the earlier text is in git history.

Epic `OPEN-END-GROWTH-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, continue." to `LOGIC-AXIS-20261107-001`'s recommendation: let a
  uniform rule act only where the relation shows an loose end (a distinction held by one knot), with no
  chosen gadget shape, and measure how bond balls grow.
- **The picture behind it.** An axis growing outward from a single knot, and a Cartesian plane whose axes
  are such logical number lines.
- **Question served.** Question 9 (space from a law).

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Five rules acting only at loose ends.** Growing at knots holding two loose ends gives the two-way thread, a ruler of dimension one (bond distance slope 1.00; balls 4 per unit of radius). Random sprouting gives a tree, a small world. Closing the nearest loose ends seals space into cells frozen apart (no knot for 370 of 374 pairs). Closing without pins or ties gives a closed strip whose bond distance never exceeds 5. Flat-face closing gives a small world. No rule grew a plane. | exploratory experiment | A |
| 2 | **Bond distance is a boundary.** It is the least two-sided boundary of a region, counting seams and the loose ends held inside. | proved | B |
| 3 | **Sealing freezes.** A region with no loose ends behind one seam pins that seam, and no knot crosses it. Two seams tie the pair but do not decouple. | proved | B |
| 4 | **Short boundaries are shortcuts.** Every two-sided boundary is a knot, so a long region with a short boundary collapses distance. A closed three-seam strip holds bond distance 3 at every length. | proved; the strip computed | B |
| 5 | **The number line grows natively.** Growing only at knots that hold two loose ends grows exactly the two-way thread. Its bond distance counts the loops between two points, plus one. | proved | B |
| 6 | **The logical Cartesian plane.** In the product law of two laws (grids whose columns and rows are allowed states of the axes), a knot of each axis joined at a corner is a knot, so bond distance <= δx + δy − 1. The product of two threads has no ends, so it is a ruler within constants of taxicab distance, with bond balls of order r^2. | proved | C |
| 7 | **Conjecture: exact taxicab.** Bond distance in the product of two threads is exactly δx + δy − 1. | conjecture; 855 pairs, no exception | C |

## Answer

- **The line grows.** One local rule, grow wherever a knot holds two loose ends, grows the logical number
  line from a single knot, in both directions. The rule reads nothing but how many loose ends a knot
  holds. Every unit carries one open loop, and bond distance counts them.
- **The plane does not grow locally.** None of the tested local rules grew a plane, and the boundary
  principle explains why:
  - closing loose ends seals regions off, or leaves long regions with short boundaries;
  - so space either freezes into cells or collapses;
  - with no closing at all, it branches into a tree.
- **The plane is a product.** It is the Cartesian product of two grown lines, and measures distance as a
  taxicab sum of the axes' loop counts. Its dimension, 2, is read from the allowed states alone.

## Literature and provenance

- **Ticket A.**
  - **Sources.** Growth models of random recursive trees, Eden growth, causal dynamical triangulations
    and hypergraph rewriting grow drawn graphs and measure graph distance.
  - **The delta.** Here the rules read allowed states only, and distance is bond distance, which exposes
    freezing and shortcuts made by the logic itself.
- **Ticket B.**
  - **Sources.** Bonds as circuits of the cocycle matroid (Whitney; Oxley); bridge arguments.
  - **Folklore risk.** High as mathematics; the reading for growth rules is the program's.
- **Ticket C.**
  - **Sources.** Product codes (Elias 1954); their direct-sum duals (MacWilliams–Sloane); hypergraph
    products (Tillich–Zémor 2009).
  - **Not found.** The L-shaped minimal dual codewords through two given positions, the no-ends
    argument, and the exact formula.
  - **Folklore risk.** Moderate.
- **Where the ideas came from.** The rules and the boundary principle came from the program's
  perspective. The product construction answers the owner's Cartesian picture directly.

## Reading

**Interpretation, not a theorem.**
- **The axis.** It is a structure that keeps one open distinction per unit, grown outward from a single
  knot by a rule that reads only loose ends.
- **The Cartesian plane.** It is the product of two such axes. It measures like a taxi grid, never the
  diagonal, and it has as many open bits as the product of its axes': emergent information grows with
  area.
- **Why space needs loose ends or long seams.** Where growth consumes its loose ends, space freezes or
  collapses. Space holds together either through loose ends kept inside (the line) or through long seams
  (lattices and products).
- **Roundness.** Taxicab distance is not round. Whether any logical construction can make round balls,
  circles as a large-scale trend, is open.

## Workspace assumption challenged

**A rule that reads loose ends sees nothing beyond them.** The 2026-10-20 attempt to grow space
(`SPACE-LAW-REFINEMENT-20261020-001`) and the closing rules here both assumed that closing loops locally
builds a fabric. It builds frozen cells or a collapsed strip instead, because closing consumes the open
ends that keep regions' boundaries large.

## Ratio

Since the epic opened:
- **Substantive.** Three evidence families changed conclusions: A (an exploratory experiment), and B and
  C (proofs).
- **Administrative.** This note and the closure.

## Pending the owner

- **Carried from LOGIC-AXIS-20261107-001.** Whether a native knot must also be natively bound
  (`research/LOGIC-AXIS-20261107-001/canonical_correction_request.md`).
- **Carried from earlier epics.**
  - Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Counted length as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — growth at loose ends | **Status:** Successful | A native rule grows the number line, local closing rules freeze, collapse or branch, and the plane is the product of two lines. Unresolved: the exact taxicab formula, and a local rule that grows a plane. |
| Local direction — local growth rules | Practically exhausted for planes | Every closing rule tested froze, collapsed or branched, and the boundary principle explains each. A further rule would need a reason to keep seams long, which is a drawing in disguise. |
| Broader exploration — question 9 | Line and plane built | The line is grown natively; the plane is built as a product. Both measure distance in loop counts. |
| Long-term goal — space from logic | Capability gained | The owner's Cartesian picture exists in logic: logical axes, taxicab distance, dimension read from allowed states. Not reached: round (Euclidean) distance, and a single law that selects its own dimension. |
| Next recommendation — circles from logic | **Next step:** Continue, as a fresh epic. Can bond balls become round? Map the large-scale shape of bond distance in shift-invariant laws without ends (products, three-axis laws, laws whose knots mix directions) and in random local laws, and decide whether roundness can appear only as a trend. | This ties the plane to the owner's view that perfect circles are trends, not things. A clean answer would be a polygon theorem for periodic laws plus a measured limit shape for random ones. |
| Interest — that recommendation | **2/3 — Promising** | Periodic laws likely give polygonal balls (as periodic metrics do), so the open part is the random laws. The risk is that it reduces to known first-passage-percolation shape theorems. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** the shapes of four or five law families are classified, polygon or measured limit. **Alternatives:** dimension under products of k lines (1/3); a proof of the exact taxicab formula (1/3). |
