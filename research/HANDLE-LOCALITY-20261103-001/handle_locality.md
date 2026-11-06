# Handles seen from a gluing line

Epic `HANDLE-LOCALITY-20261103-001` (program topology), 2026-11-03.

## The question

- **The approval.** The owner said "Yes, let's continue." to PLANAR-THEOREM-20261102-001's recommendation.
- **What it asked.**
  - Prove that access at a gluing line depends only on a planar patch around that line.
  - Test, on spaces with one and two Fano atoms, whether new knots appear exactly at gluing lines on handles.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Plane matching systems.** A plane signed system with as many lines as odd faces has as solutions exactly the perfect matchings of lines to odd faces, and the access lemma holds on it for every pinning. A plane knot space split at a point is one. | proof; 301 splits, 260,892 pinnings | A |
| 2 | **The interface lemma.** In a splice, an intact side acts on the cut as the point or line it replaced. So the solutions restricted to a plane piece are its closure minus a line, the point split, or one of two gadget forms, each a plane matching system. | proof; 266 piece–removal pairs | A |
| 3 | **Access is local.** Every pinning of a plane piece's line by two points of that piece has access, wherever the removed line is. Pinnings by two points outside the piece fail only when the removal is outside too. | proof; 31,596 pinnings (computation for outside pinnings) | A |
| 4 | **The screening lemma.** If the cut carries one bit after the removal, creation at a plane gluing line is creation on a plane knot space minus a line. One bit crosses when the removal lies in the plane piece next to a handle attached at a point, or inside a handle attached at a line. | proof | B |
| 5 | **No handle at either line, no creation.** No new knot appears when neither the gluing line nor the removed line lies on a handle (896 cases), nor at a plane gluing line beside a handle attached at a line (224). | computation, up to three points (four on part) | B |
| 6 | **An opened handle creates at a distance.** A handle attached at a point and opened by the removal creates at plane gluing lines at distance 1, 3 and 5 from it. Two handles act independently. | computation | B |
| 7 | **The premise fails on composite spaces.** Near an opened handle, 1,092 of 2,496 new knots are unpinned three-point knots through the hub. Inside handles, four-point new knots appear (2,965). | computation; brute-force spot checks | B |

**Scouting after ticket B (not a claim; `reach_condition_scout.py`).**
- **Necessary.** Every plane gluing line that an opened handle reaches has at most two patterns left once the split point's three copies
  are fixed on the plane piece. This held for 76 creating cases; none of the 36 lines left with three patterns creates.
- **Not sufficient.** 236 cases meet the condition and do not create.

## Answer

- **Access is local, and proved.** Inside a plane piece, every pinning reaches the ports, whatever happens elsewhere. A handle cannot
  break access from outside its piece, except through pinnings by its own points.
- **Creation is not confined to handles.** "New knots appear exactly at gluing lines on handles" is false.
  - **A gluing line on a handle** creates.
  - **An opened handle attached at a point** also creates at plane gluing lines around it, out to distance 5 on the spaces tested.
  - **Nothing else creates.** This covers a handle attached at a line, and an unopened handle (computation).
- **The premise breaks.** On composite spaces, new knots include unpinned three-point knots and four-point knots. The earlier picture,
  "every new knot is a pinned three-point knot through the hub", held only on census and plane near sides.

## Reading

- **What a handle shows to the plane glue.** An intact handle looks exactly like the point or line it replaced.
- **A handle attached at a point, opened.** It talks to the plane glue through that point's three copies, two bits. That is enough to
  force a plane gluing line some distance away.
- **A handle attached at a line, opened.** The plane glue screens it. The glue minus the line forces the line's points equal, so only one
  bit crosses.
- **So** native selection reads a handle in two ways: where it sits, and, once opened, in a halo spread through the plane glue by forced
  matchings.
- **Doctrine.**
  - Distances here are incidence-graph distances used only to describe where creation was found. They are not a native magnitude.
  - Hubs remain equality fan-out.

## Literature

- **Ours.** PLANAR-THEOREM A–C (heights, every pinning, one-port 2-sums), PLANAR-COMPOSE A, HANDLE-EMERGENCE B–C, THREEFOLD-SURFACES
  (Fano atoms as handles).
- **Classical.** Kasteleyn's face condition; heights of plane bipartite matchings (Thurston, Propp); L-convex sets (Murota); 2-sums across
  separations.
- **New here.** All seven conclusions and the scout.

## Pending the owner

Still open from earlier epics:
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — handles seen from a gluing line | **Status:** Partially successful | **Proved.** Access is local (plane matching systems, interface lemma); the screening lemma. **Computed.** The creation map on one- and two-handle spaces. **Refuted.** Creation exactly at gluing lines on handles: an opened handle attached at a point creates at plane lines out to distance 5. **Learned.** The pinned three-point premise fails on composite spaces. |
| Local direction — locality of creation | Continue, narrowed to the halo | **What is left.** Which plane gluing lines an opened handle reaches, and why. A necessary condition is known: fixing the split point leaves at most two patterns. Also unexplained: two bits cross from an intact handle attached at a line, yet nothing is created. |
| Broader exploration — where selection creates | Remapped | **The sources.** Handles at the gluing line, and opened point-attached handles within a halo. No other source has been seen. **New knot types.** Unpinned three-point knots and four-point knots. |
| Long-term goal — topology from native emergence | Capability gained; picture corrected | **Gained.** A proof that plane glue is locally transparent to access. **Corrected.** Native selection reads a handle not only where it sits but, once opened, in a halo that the plane glue carries by forced matchings. |
| Next recommendation — the halo as dimer forcing | **Next step:** Continue. Characterize the plane gluing lines an opened handle reaches by forcing in the matching picture of the point split. First turn the necessary condition into a criterion that also uses the handle's own port relation. Then prove it, and measure the reach on large plane pieces, ladders against grids (frozen against liquid regions). | **If yes.** Creation becomes a computable topological signal: a handle plus a matching-forcing halo. **If no.** The failing cases show what else the handle transmits. **Alternatives.** Explain the screened line-attached handle (1/3). Finish the planar reduction lemma (1/3). Classify the new unpinned and four-point knots (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The necessary condition held for all 76 creating cases, and the reach grew from 3 to 5 as the plane pieces grew. Classical dimer forcing and frozen-region theory supply tools. **Main uncertainty.** The condition is far from sufficient (236 non-creating cases meet it), and large plane pieces need a matching-based solver instead of enumeration. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** Plane pieces up to about 30 points via the join method. **Stop when** the reach is characterized or a case defeats every forcing criterion. |
