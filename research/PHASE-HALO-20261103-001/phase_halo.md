# Creation and dimer phases

Epic `PHASE-HALO-20261103-001` (program topology), 2026-11-03.

## The question

- **The approval.** The owner said "Please continue." to HALO-FORCING-20261103-001's recommendation.
- **What it asked.**
  - Build plane pieces that mix frozen and liquid parts, and test whether the halo of an opened handle is exactly the frozen region
    joined to the handle.
  - Prove the ladder and grid laws.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The claiming lemma.** In a point split, a port is odd on its line exactly when that line takes the single skip of the face opposite the port. Every line of that face then feels it. | proof; 5,544 triples | A |
| 2 | **Opposite faces carry the halo.** With the Fano plane as handle, at 126 attachment points on ladders, thick tubes, a grid, random spaces and a ladder arm spliced onto a grid, every halo line beyond distance 3 lies on a face opposite the attachment point. In 124 cases it is exactly those faces' far lines. | computation (validated pipeline) | A |
| 3 | **So the frozen-region reading is replaced.** The reach is set by the size of the faces opposite the handle. A ladder's opposite face is a whole cycle; a grid's faces have at most three corners; a thick tube carries the halo around its polar face only when the handle sits beside it. | reading of 2 | A |
| 4 | **The handle matters.** With census 58 as handle (pipeline equal to exact creation in all 976 small cases), the halo also uses the attachment point's own long face on the mixed space's arm (5 of 24 points). The general law is "the faces around the attachment point". | computation | A |
| 5 | **The ladder law.** The prism is the cyclic chain of consecutive triples, with Kasteleyn signs constant except at two lines. Its transfer matrix has powers of period 2 from the second. So every far line's transfer depends only on its parity, the same on every prism. With the computed cases, the halo runs the full length of the opposite face on every prism. | proof (finite certificate), plus the route criterion | B |
| 6 | **The grid law.** A line with the full transfer is independent of the attachment point, and no knot through handle points reaches it. On the 64- and 256-point grids every line at distance 9 (mostly 7) or more is certified independent. | proof plus exact certificates | B |
| 7 | **Frozen against liquid, measured.** The smallest range of height differences between a port and a line is 0 at every distance on ladders, and grows with distance on grids (to 11 at distance 29). | computation | B |

## Answer

- **Is the halo the frozen region joined to the handle?** No, not as such. Beyond three steps, the halo is carried by the faces around the
  attachment point. With the Fano plane, that means exactly the faces opposite it, in 124 of 126 cases.
- **Why the phase reading worked on pure families.** A large face is a long-range constraint: exactly one of its lines may skip into it.
  - **Ladders.** All their length is in two faces, which is why they behave as frozen.
  - **Grids.** Only small faces, which is why they behave as liquid.
- **The two laws.**
  - **The ladder law** is now a theorem for every prism, given the route criterion. The prism is a one-dimensional chain whose transfer
    repeats with period 2.
  - **The grid law** is certified exactly on the grids tested, and explained by height ranges that grow with distance.

## Reading

- **What a handle shows the plane.** An opened handle speaks to the plane through the faces around the point where it is attached:
  whether its ports are odd decides which lines may claim those faces.
- **How far that carries.** As far as those faces extend: the whole ladder, or three steps into a grid.
- **What the phase is.** The dimer phase is a summary of how large the faces are and how rigidly the heights are pinned, not a separate
  cause.
- **Doctrine.**
  - Distances only describe where creation was found. They are not a native magnitude.
  - The heights are a proof device.
  - Hubs remain equality fan-out.

## Literature

- **Ours.** HALO-FORCING A–C, HANDLE-LOCALITY A–B.
- **Classical.**
  - Kasteleyn signings, unique up to gauge on plane graphs.
  - Boolean transfer matrices.
  - Plane matching heights.
  - Frozen and liquid phases of dimer models.
- **New here.**
  - The claiming lemma and the opposite-face law.
  - The chain picture of the ladder and its reduction.
  - The height-range measurements.

## Pending the owner

Still open from earlier epics:
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — creation and dimer phases | **Status:** Successful, with a corrected question | **Tested.** The phase reading, on mixed glue and thick tubes: it is replaced by the opposite-face law (Fano handle: 126 of 126 points contained, 124 equal). **Proved.** The ladder law for every prism, by a period-2 transfer matrix, given the route criterion. **Certified.** The grid law, exactly on the grids tested. **Learned.** The faces a handle uses depend on the handle (census 58 also uses its own face). |
| Local direction — the halo | Practically complete for the Fano handle; open for handles in general | **What is left.** A proof of the opposite-face law itself (why lines off the faces around the point never create beyond three steps), and the rule that decides which faces a given handle uses. |
| Broader exploration — where selection creates | Mapped for one handle class | **The sources.** Handles at the gluing line; opened point-attached handles through the faces around their point; nothing else seen. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native creation reads the plane through faces, its native "places" of exactly one skip. A handle is seen as far as the faces around it reach, which is a native, local-to-global mechanism with no metric. |
| Next recommendation — which faces a handle uses | **Next step:** Continue. Classify handles by the faces they can speak through: their own faces or the opposite faces. Explain why the Fano plane uses only the opposite faces and census 58 can also use its own, through the handle's port relation after a removal and the merged face of the split. Then prove the opposite-face law for the handles that obey it. | **If yes.** A complete, local description of where any opened handle creates: its port relation and the faces around its point. **If no.** The handles that break it show what else they transmit. **Alternatives.** The screened line-attached handle (1/3). The planar reduction lemma (1/3). Several interacting handles (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The law is exact for the Fano plane on every family tested. The census 58 deviation is clean (only its own long face) and the pipeline is validated for it, so a classification by port relation looks reachable. **Main uncertainty.** The opposite-face law has no proof route yet beyond the claiming lemma, and the handle census may be large. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The census handles and plane pieces up to a few hundred points. **Stop when** the faces each census handle uses are classified, and the law is proved or a counterexample found. |
