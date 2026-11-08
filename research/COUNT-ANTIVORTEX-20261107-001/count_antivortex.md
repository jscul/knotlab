# Negative curvature's count: the genus-2 antivortex

Epic `COUNT-ANTIVORTEX-20261107-001` (program complexity), 2026-11-07.

## The question

- **The approval.** The owner said "Please do both" to `COUNT-SURFACES-20261107-001`'s two recommendations. This epic is (i): on knot
  spaces of genus at least 2 with Kasteleyn signs, the count forces some face to over-agree. Is finding one PPADS-complete, as finding the
  sphere's violated line is?
- **The agreed method.** Mirror FLAT-STATES-20261107-001B's Sperner embedding with the opposite orientation, on a genus-2 cover or the
  trivially signed octahedral sphere.
- **What was done.** The host is the double of a holed lattice torus rather than a branched cover of the sphere. The double cover of
  the knot sphere turns the frames' sublattice around its handles, so no flat state develops on it. The double of a holed torus with
  lattice in L3 does not.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The genus-2 mirror.** The double of T(3a Z²) along a hexagonal hole is a genus-2 knot space whose six degree-8 faces turn the frames by +1, the mirror of the knot sphere's six corners at −1. Exactly one of its 16 Kasteleyn classes makes the handles flat. | proved; checked in all 16 classes | A |
| 2 | **The antivortex.** Developing one frame over the surface cut along six paths from z to the degree-8 faces violates no line and over-agrees at exactly one face, at z. So the knot's lines are satisfiable on genus 2, while some face must over-agree. | proved; checked | A |
| 3 | **The face problem.** Finding an over-agreeing face is PPADS^dt-complete; finding a violated line or an over-agreeing face is PPAD^dt-complete. | new as far as found; proved | A |
| 4 | **How the reduction works.** With the mirrored Sperner map, the region's boundary is the canonical one with colours 1 and 2 swapped. Over-agreeing faces sit exactly one in each clockwise fully labelled triangle, violated lines one in each counterclockwise one. | proved; checked on 80 colourings for m = 3..7 | A |

## Answer

- **Yes.** The forced defect is PPADS-complete on both sides of the curvature:
  - on the sphere, a violated line (a vortex);
  - on genus 2, an over-agreeing face (an antivortex).
- **Two-sided.** Allowing both kinds of defect gives PPAD-completeness in both cases.
- **What curvature decides.** The sign of the curvature decides which kind of defect the knot must have, not how hard it is to find.

## Reading

**Interpretation, not a theorem.**
- **The mirror.** The knot sphere and the genus-2 double mirror each other:
  - six two-corner faces at holonomy −1 against six four-corner faces at +1;
  - a vortex on a line against an antivortex on a face;
  - counterclockwise against clockwise Sperner triangles.
- **Coherence.** On genus 2 the knot's lines can all hold, so the knot is coherent. What fails is the faces' closure. Finding where it
  fails costs exactly what finding the sphere's broken line costs.

## Literature and provenance

- **The sphere side.** FLAT-STATES-20261107-001A/B (flat states, the Sperner map, "clockwise ones hold a full face, an antivortex") and
  COUNT-TFNP-20261107-001A/B (PPADS^dt and PPAD^dt classifications).
- **The count on surfaces.** COUNT-SURFACES-20261107-001A.
- **Classes.** Göös et al., JACM 2024 (PPADS^dt = unary Sherali–Adams, PPAD^dt = unary Nullstellensatz).
- **Sperner on surfaces.** Friedl–Ivanyos–Santha–Verhoeven, CIAC 2006.
- **Provenance.** The holes view supplied the mechanism: frames, holonomy, cut stars and the antivortex as the defect the count forces. The
  classification composes standard reductions.
- **Folklore risk.** Low for the classification. Moderate for the local facts, which mirror FLAT-STATES-B.

## Ratio

Since the epic opened:
- **Substantive.** One proof family: the surface, the class, the flat state and the reduction.
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — is the forced face on genus 2 PPADS-complete? | **Status:** Successful | PPADS^dt-complete on the genus-2 doubles; the two-sided problem PPAD^dt-complete; the lines satisfiable. Every local step was checked, with controls. |
| Local direction — the count's class across curvature | Practically complete | Sphere, flat and negative curvature are settled: lines or faces fail by the sign of χ − \|D\|, and the forced problem is PPADS-complete either way. Open but incremental: several antivortices (genus ≥ 3, by placing copies), non-lattice genus-2 spaces, and circuit versions. |
| Broader exploration — the complexity of the knot's spaces | Known alternatives | Knot sphere, surfaces, curvature, three-fold spaces via plane cores. Not mapped: bounded-genus spaces with non-lattice defects. |
| Long-term goal — "hardness at three places" | Capability gained | The knot's forced defect has the same class (PPADS) for both signs of curvature; orientation and curvature choose only which constraint fails. This does not move question 9; the surfaces are drawn. |
| Next recommendation — leave the count's complexity chain | **Next step:** Full pivot to question 9 (low-dimensional shape from a uniform local law, nothing drawn). That pivot is `UNIFORM-SPHERES-20261107-001`, opened in the same request: which uniform laws of lines and co-lines close into spheres, and how deep the knot's contradiction on them can be. | The complexity chain's remaining refinements are incremental. The question it leaves for question 9 is whether a law can grow the sphere that makes the knot contradict itself. |
| Interest — that pivot | **2/3 — Promising** | **Evidence:** the count reads the curvature of any surface a law builds, and uniformity bounds positive curvature by Euler's formula. **Uncertainty:** whether "uniform" (every point alike) is the right reading of the owner's "uniform local law". |
| Execution — that action | Started | Running now as UNIFORM-SPHERES-20261107-001 under the same "Please do both". Its stop rule is in its node. |
