# The halo of an opened handle

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `HALO-FORCING-20261103-001` (program topology), 2026-11-03.

## The question

- **The approval.** The owner said "Yes, let's continue." to HANDLE-LOCALITY-20261103-001's recommendation.
- **What it asked.** Find which plane gluing lines an opened handle reaches, by forcing in the matching picture. Prove the criterion, and
  measure the reach on large plane pieces, ladders against grids.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The route lemma.** A three-point crossing knot at a gluing line is generated when it has a route. Either one point of the line separates, or a pair of the line's points is forced by the near pair and covered by the far point's excluded block, with a tie or a one-step near knot at the near end. | proof | A |
| 2 | **The route criterion is exact.** With the Fano plane attached at a point of five plane pieces and opened by the removal, the new knots are exactly the candidates without a route: 1,500 new; 59,984 routed candidate instances, none new. Creation depends on the plane piece only through its transfer between the handle's ports and the gluing line. | computation | A |
| 3 | **Corner matchings.** In a point split, the solutions are the corner matchings: the port lines give double edges. This clarifies HANDLE-LOCALITY A's matching statement; its conclusions are unaffected. | proof; 71 splits | B |
| 4 | **Heights compute the transfer.** Fix the gluing line's corner, project the difference constraints onto six regions by shortest paths, and test parities by halving. The result is exact and needs no enumeration. | proof; 1,221 cases | B |
| 5 | **The halo spans a ladder.** On prisms of 10 to 80 points, an opened handle creates at the farthest gluing line, with two of every four lines creating at each distance. | computation (validated pipeline) | C |
| 6 | **The halo stops at distance 3 on grids.** This holds on duals of the subdivided octahedron with 16, 64 and 256 points, from several attachment points. | computation | C |
| 7 | **Frozen against liquid.** Fixing the handle's point leaves every ladder line with two patterns at any distance. Every grid line at distance 7 or more is exactly independent of it (all 36 pairs). Random grown spaces lie between (reach 5 to 7). | computation | C |

## Answer

- **Which lines an opened handle reaches.** Exactly those where two handle points force the gluing line into one or two patterns, and no
  route rebuilds the knot. A route is a one-point separation, or a two-step elimination through a pair of the line's points. The far
  point's excluded block decides which pairs are usable. That is why K4^(3) and census 6, whose far points can exclude two adjacent
  patterns, see farther than the Fano plane and census 58.
- **How the plane glue carries it.** Only through the transfer, which heights compute exactly.
- **How far it reaches.**
  - **On a ladder, without limit.** The ladder passes the handle's two bits along its whole length.
  - **On a grid, three steps.** Beyond that, the grid forgets the handle entirely.

## Reading

- **What the owner's question becomes.** Native selection does read a handle from a distance. How far depends on the glue's dimer phase,
  not on the handle.
  - **Frozen glue (a thin strip).** Transmits a handle's presence without loss.
  - **Liquid glue (a fat grid).** Screens it within a few steps.
- **So** "topology from native emergence" acquires a phase structure. Where a handle can be detected is decided by how rigid the plane
  around it is.
- **Doctrine.**
  - Distances only describe where creation was found. They are not a native magnitude.
  - The heights are a proof device.
  - Hubs remain equality fan-out.

## Literature

- **Ours.** HANDLE-LOCALITY A–B, PLANAR-THEOREM A–C, PLANAR-COMPOSE A.
- **Classical.**
  - Heights of plane bipartite matchings (Thurston, Propp).
  - Difference constraints and shortest paths.
  - Frozen and liquid phases of dimer models (Kenyon, Okounkov and Sheffield), and arctic curves.
- **New here.**
  - The route criterion and its exactness.
  - The corner-matching transfer.
  - The halo measurements and their forcing explanation.

## Pending the owner

Still open from earlier epics:
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the halo of an opened handle | **Status:** Successful | **Found.** The criterion that decides which lines are reached (the route lemma proved; its converse exact on every small case). **Built.** The polynomial transfer that lets it run on large pieces. **Measured.** The reach: unbounded on ladders, 3 on grids. **Explained.** By forcing: frozen against liquid. **Not proved.** The converse of the criterion beyond the small spaces, and the two laws as theorems. |
| Local direction — the halo | Continue, narrowed | **The remaining step.** Turn the two observed laws into theorems. A periodic strip composes one fixed relation along its length; a grid becomes independent after a few steps. Then test the phase reading where both phases meet. |
| Broader exploration — where selection creates | Remapped with a phase structure | **Where creation happens.** Handles create where they sit, and through frozen glue at a distance. Liquid glue screens them. Line-attached handles are screened (HANDLE-LOCALITY). |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native selection's view of a handle is now computable at scale, and it has a classical counterpart: the frozen and liquid regions of the dimer model. |
| Next recommendation — creation and dimer phases | **Next step:** Continue. Build plane pieces where frozen and liquid parts meet: ladder arms on grids, and regions whose boundaries freeze part of the plane, as in arctic phenomena. Test whether the halo is exactly the frozen region joined to the handle. Prove the ladder law (periodic transfer) and the grid bound (independence after a few steps). | **If yes.** Native creation traces the dimer phase boundary, and a handle is visible exactly through frozen glue. **If no.** The mismatch shows what else carries forcing. **Alternatives.** The screened line-attached handle (1/3). The planar reduction lemma (1/3). Other handles and several handles (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The pure families split cleanly: reach equal to size on ladders, 3 on grids, with exact independence beyond distance 7. Random spaces fall between. **Main uncertainty.** Designing contradictions with controlled dimer phases, since the matching graph is the line–face graph, not the incidence graph. The phase boundary may also not be sharp at accessible sizes. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** Plane pieces up to a few hundred points, with the validated pipeline. **Stop when** the halo is compared with the frozen region on mixed pieces and the two laws are proved or shown false. |
