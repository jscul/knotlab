# Which faces a handle uses

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `FACE-CLAIM-20261103-001` (program topology), 2026-11-03.

## The question

- **The approval.** The owner said "Yes, please continue." to PHASE-HALO-20261103-001's recommendation.
- **What it asked.**
  - Classify handles by the faces they create through, their own or the opposite ones.
  - Explain the Fano plane against census 58 through the handle's port relation.
  - Prove the opposite-face law for the handles that obey it.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The reading lemma.** In the split at the attachment point, the merged face takes its one skip on the arc opposite the port that is odd relative to an all-agree pattern fixed by the arc constants. So the own arc between two ports is barred exactly when they disagree, and whenever they agree the face opposite the third port is claimed by that port's line. Barred faces fix two points of each of their lines. | proof; brute force on 2,148 solutions | A |
| 2 | **The claim lemma.** A frozen line claims an own arc from one port pattern per value, and the face opposite a port from at most two, which share the other two ports. | proof; brute force on 432 corners | A |
| 3 | **The claim rule.** An opened handle creates at a frozen line exactly when a pair of its points freezes it and each point alone still allows the line's claim at either fixed value. | route direction proved; converse computed with no disagreement against exact creation (728 cases) and the pipeline (26,634 far lines) | A |
| 4 | **The census of handles.** 24 non-planar contradictions, 305 handles, all port orders on a ladder (1,830 cases). Which faces are used depends only on the bottom port, and nine signatures occur. | computation | B |
| 5 | **Faces used are a property of the port relation.** The rule's port form decides all 3,660 (case, face) pairs. The opposite face of c is used when a pair pins one class-c pattern and each single point keeps both disagreeing values of the other ports. The own arc is used when each single point keeps both class-c patterns. | computation (exact on the census) | B |
| 6 | **The Fano plane.** Every removal meets the removed line at one port. Pairs pin that port's class, and every single point removes exactly one pattern of each other class. So it never uses an own arc (proved) and uses the opposite face at every port (computed). | proof plus finite check | B |
| 7 | **Census 58.** It uses the own arc exactly when the bottom port is 0 or 5, the third points of its two lines that share two points. | computation | B |
| 8 | **The frozen region.** Creation needs a frozen line. Generically the frozen region is exactly the faces around the point: two-sided unit propagation from the class's seeds finds it on ladders, a grid, a tube and grown spaces. On a ladder arm spliced onto a grid, a global rigidity extends it along the arm's far long face at junction points. | proof (bound) plus computation | C |
| 9 | **The PHASE-HALO law fails.** At one junction point the extended frozen lines claim from two patterns, and all three handles create there, off the faces around the point. Exact creation confirms this on a 21-point piece (12 instances). | counterexample, exact on the small piece | C |

## Answer

- **Which faces a handle uses.** Those carrying frozen lines whose claims survive the handle's single points.
  - **The plane decides each claim's type.** An own arc's claim is one port pattern. An opposite face's claim is a value of the other two
    ports, two patterns.
  - **The handle decides which claims survive.** It does so through what one of its points removes from the port patterns.
- **The Fano plane against census 58.**
  - **The Fano plane.** Its single points always remove one pattern per other class: enough to kill every one-pattern claim, never a
    two-pattern one. That is why it uses only opposite faces.
  - **Census 58.** At two of its points, its single points leave the own arc's claims alive.
- **The opposite-face law.**
  - **On faces around the point (proved).** The Fano plane never creates on an own arc. Its opposite-face creation is computed.
  - **The PHASE-HALO generalization is false.** The halo is not confined to the faces around the point. It lies on frozen lines with
    surviving claims, which a junction can carry along a long face elsewhere.

## Reading

- **What a face reads.** Each face around the point reads one bit of the handle: whether two of its ports agree.
- **What the plane adds.** Frozen structure carries that bit further, along a strip.
- **What the handle adds.** How sharply one of its points cuts the port patterns.
- **So** the halo is where those three meet.
- **The phase reading returns, refined.** The frozen region of the port pattern is the dimer model's frozen region for that boundary
  condition. Generically it is the faces around the point, and at junctions it is larger.
- **Doctrine.**
  - Distances only describe where creation was found.
  - The heights and patterns are a proof device.
  - Hubs remain equality fan-out.

## Literature

- **Ours.** PHASE-HALO A–B, HALO-FORCING A–C.
- **Classical.** Kasteleyn parities and corner matchings, unit propagation for perfect matchings, and frozen regions of dimer models
  under boundary conditions.
- **New here.**
  - The arc identity and the reading lemma.
  - The claim lemma and the claim rule.
  - The census and its port form.
  - The Fano pin structure.
  - The junction counterexample.

## Pending the owner

- **New.** Whether to supersede or qualify `PHASE-HALO-20261103-001-D001`. Its statement "the reach is set by those faces' size, not
  by a dimer phase" generalizes beyond the 126 points it tested. Conclusion 9 refutes the generalization; the tested facts stand.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — which faces a handle uses | **Status:** Successful, with a corrected law | **Proved.** What each face reads, the claim types, and the claim rule's route direction. **Computed.** The census of 305 handles, decided by the port relation, and the rule's converse with no disagreement. **Explained.** The Fano plane: it never uses an own arc (proved). **Refuted.** The law of the faces around the point, exactly on a small piece. |
| Local direction — the halo | Practically complete as a description; the rule's converse unproved | **What is left.** The converse as a theorem, and a description of the frozen region beyond the faces around the point (junctions). |
| Broader exploration — where selection creates | Mapped through one criterion | **The criterion.** Handles create at gluing lines on them and at frozen lines whose claims their single points leave. Planar sides never create. Line-attached handles are screened. |
| Long-term goal — topology from native emergence | Capability gained | **Gained.** Native selection reads an opened handle through a one-bit reading of its ports, carried by the plane's frozen structure. Which faces it reads is a property of the handle. |
| Next recommendation — the frozen region by heights, and rigid strips | **Next step:** Continue. Prove that a port pattern freezes exactly the points whose height difference to the ports cannot vary, explain the junction extension as a rigid strip, and build plane pieces with long rigid strips through liquid bodies to test whether the halo follows them. | **If yes.** The halo is fully described: frozen region by heights, claims by the handle, and a handle visible arbitrarily far through a rigid strip. **If no.** The strips stay rigid (no claims), and the faces around the point are the generic limit. **Alternatives.** The converse of the claim rule as a theorem (2/3). The structure of the nine signatures (1/3). The screened line-attached handle (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** The heights already compute the transfer exactly, and a zero height range forces a fixed value. The junction shows rigid strips exist and can carry creation. **Main uncertainty.** Whether long strips keep two-pattern claims or turn rigid. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** Plane pieces up to a few hundred points with the existing pipeline. **Stop when** the frozen-region lemma is proved or refuted and the strip test is decided. |
