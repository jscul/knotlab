# Uniform laws and the spheres they can close into

Epic `UNIFORM-SPHERES-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Please do both" to `COUNT-SURFACES-20261107-001`'s two recommendations. This epic is (ii), question
  9: low-dimensional shape from a uniform local law, with nothing drawn.
- **The question asked.** Which uniform laws of lines and co-lines build their own closed surface? On which does the knot's count force
  its contradiction, a sphere grown rather than drawn?
- **The setting.** A law of lines and co-lines is points, lines (triples) and co-lines (cyclic sequences), in which each pair of a line's
  points lies in exactly one co-line and each point's link alternates the two. Such a law is a closed surface by itself. The knot's count
  (COUNT-SURFACES-20261107-001A) then reads its Euler characteristic, with the co-lines as faces.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Laws build surfaces.** The Cayley law of a group G = ⟨x, y⟩ (lines {g, gx, gxy}, co-lines the cosets of ⟨x⟩, ⟨y⟩, ⟨(xy)⁻¹⟩) always builds a closed orientable surface, with every point of co-line sizes (\|x\|, \|y\|, \|xy\|). | known-with-delta (Cayley maps); proved | A |
| 2 | **Uniform spheres are few.** A law with one kind of point has χ = n(1/d1 + 1/d2 + 1/d3 − 1). It closes into a sphere only as an antiprism (2,2,d), n = 2d, or a snub polyhedron (2,3,3), (2,3,4), (2,3,5), n = 12, 24, 60. It is flat for (3,3,3), (2,4,4), (2,3,6) and hyperbolic otherwise. | known-with-delta (vertex-transitive maps); proved; realized on V4, D_d, A4, S4, A5 | A |
| 3 | **Uniform signs never force the lines.** With uniform signs every even co-line is an even face, so χ − \|D\| ≤ n(Σ_odd 1/d − 1) ≤ 0. The count never forces the knot's lines to fail on any uniform law; on uniform spheres it forces faces to over-agree instead. | new as far as found; proved | A |
| 4 | **Only shallow contradictions.** Kasteleyn signs, which are never uniform on a sphere, make the knot fail on every uniform sphere, but only on at most 60 points or on an antiprism. Every (2,2,d) law is a cyclic chain, so a violated line is found by binary search in O(log n) queries (FP^dt). | new as far as found; proved | A |
| 5 | **The census.** With uniform signs the knot is satisfiable on every uniform law tested (spheres, flat quotients, the Klein quartic law PSL(2,7)) and on all 327 circulant laws with n ≤ 48, except the Fano plane, whose contradiction the count does not see. The knot sphere has exactly two kinds of points. | computed | A |

## Answer

- **Every uniform law builds its own closed surface, and its co-line sizes fix the shape.** It is flat or hyperbolic for most types, and
  a sphere only when small (at most 60 points) or thin (an antiprism).
- **No uniform law forces the knot's contradiction through the count.** Positive curvature sits on digons, and a digon closes only under a
  sign that breaks uniformity.
- **Even with such signs, the uniform spheres' contradictions are shallow.** The knot sphere's deep, PPADS-complete contradiction needs at
  least two kinds of points: twelve special points at six digons, with a sign defect at each.

## Reading

**Interpretation, not a theorem.**
- **What a uniform law can grow.** A law that treats every place alike can grow flat space without end: the number line and plane of
  LOGIC-AXIS and OPEN-END-GROWTH, closed up here as tori. It can also grow negatively curved surfaces.
- **What it cannot grow** is a large sphere.
- **The knot's contradiction marks non-uniformity.** Its contradiction is the count of positive curvature, so it marks exactly where a
  law stops treating every place alike. A coherent uniform world is flat or hyperbolic; a world that closes into a sphere must have
  special places.

## Literature and provenance

- **Classical sources.** Vertex-transitive maps and Cayley maps (Biggs 1972; Gross–Tucker, *Topological Graph Theory*, 1987). The spherical
  list: prisms, antiprisms and Archimedean solids; here the snub types with alternate triangles. The Klein quartic is PSL(2,7)'s (2,3,7)
  Hurwitz surface.
- **This program.** COUNT-SURFACES-20261107-001A (the count on surfaces), COUNT-TFNP-20261107-001B (the knot sphere's class),
  THREEFOLD-SURFACES-20261030-001 (the Fano plane as the 7-vertex torus; Fano atoms are handles), and LOGIC-AXIS-20261107-001 and
  OPEN-END-GROWTH-20261107-001 (uniform laws and growth).
- **Provenance.** The holes view supplied the question (which surfaces a law builds, read by the knot's count) and the mechanism (curvature
  at digons closed by signs). The geometry is classical.
- **Folklore risk.** High for theorems 1–2, low for 3–4.

## Ratio

Since the epic opened:
- **Substantive.** One proof family: theorems 1–4 and the census.
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
| Current attempt — which uniform laws close into spheres, and does the count force the knot there? | **Status:** Successful | Classified: antiprisms and snub polyhedra only. Uniform signs never force the lines. Non-uniform signs force only shallow contradictions. Computed census with one non-count exception (the Fano plane). |
| Local direction — laws that build their own surface | Continue (with two kinds of points) | One kind of point is settled. The knot sphere shows that two kinds suffice for large spheres and deep contradictions. Laws with a few kinds of points, and how their defects could arise, are unmapped. |
| Broader exploration — question 9 (shape from a uniform local law, nothing drawn) | Known alternatives | Rulers and the number line (LOGIC-AXIS), growth at open ends (OPEN-END-GROWTH), native genus readings (GENUS-READ, REFINE-READ), and now self-built closed surfaces. The rung "a law that lays out its own network" is partly answered: laws of lines and co-lines lay out closed surfaces, flat or hyperbolic if uniform. |
| Long-term goal — question 9 and "hardness at three places" | Capability gained | A law builds its own closed surface, its shape is read from its co-line sizes, and the knot's count reads its curvature. Uniformity bounds positive curvature, so the knot's deep contradiction requires special places. |
| Next recommendation — two kinds of points | **Next step:** Research directions. (i) Laws with two kinds of points: which close into large spheres, and can a local growth rule (as in OPEN-END-GROWTH) place the six digon defects itself, so that a law grows its own sphere and with it the knot's contradiction? (ii) Large uniform contradictions without the count: vertex-transitive non-2-colourable triple systems beyond the Fano plane. Your call. | (i) moves question 9 directly: it asks whether a sphere, and the knot's hardness, can be grown with nothing drawn. (ii) asks whether the Fano plane is the only uniform obstruction. |
| Interest — those recommendations | **(i) 2/3 — Promising; (ii) 1/3 — Exploratory** | **(i)** Euler's formula fixes the defect budget (six digons), and the knot sphere realizes it with two point types. The open part is whether a rule that does not know where the defects go can still close a sphere. **(ii)** The circulant census found only the Fano plane; larger groups were sampled only. |
| Execution — that action | Deferred to the owner | **Not started.** (i) Stop when laws with two point types that close into spheres are classified (or shown unbounded) and a growth rule producing them is found or shown impossible within a stated class of rules. |

## Final report as sent

Sent to the owner on 2026-11-08 at 00:40 UTC and copied here verbatim. One report covered this epic and `COUNT-ANTIVORTEX-20261107-001`, which closed together.

I did both, as two epics; both are proved, committed and published.

**(i) Negative curvature: yes, the forced face is PPADS-complete.**
- **The surface.** Take a lattice torus, cut out a hexagonal hole, and glue two copies along the hole. The result has genus 2 and six special vertices, the mirror image of the knot sphere's six corners.
- **The knot holds, a face fails.** The knot's lines can all be satisfied there. Some face must still over-agree, and I built an assignment with exactly one such face.
- **The class.** Mirroring the sphere's Sperner embedding (reversed orientation) puts the forced faces exactly in the clockwise triangles. So finding an over-agreeing face is PPADS^dt-complete, and "violated line or over-agreeing face" is PPAD^dt-complete.
- **Answer.** The sign of the curvature decides which constraint fails, not how hard the failure is to find.
- **The construction is narrow.** The obvious genus-2 host, the double cover of the knot sphere, does not work: its handles twist the lattice structure. The torus lattice has to be chosen so this twist vanishes.

**(ii) Question 9: no uniform law grows the knot's contradiction.**
- **No drawing needed.** A law of lines and co-lines (each pair of a line's points lies in exactly one co-line) builds its own closed surface.
- **Its shape.** When every point is alike, the co-line sizes alone fix the shape: χ = n(1/d1 + 1/d2 + 1/d3 − 1).
  - **Spheres** arise only as antiprisms or the snub polyhedra, with at most 60 points (realized on the groups A4, S4, A5 and the dihedral groups).
  - **Otherwise** the space is flat (a torus) or hyperbolic. One example is the Klein quartic's law on PSL(2,7), with 168 points.
- **Uniform signs never trigger the count.** Positive curvature sits on digons (two lines sharing two points). When every line carries the same constraint, every digon stays open, so the count never forces a line to fail on any uniform law.
- **Even breaking uniformity gives only shallow contradictions.** Signs that close the digons make the knot fail only on those small spheres or on antiprisms. Antiprisms are chains: binary search finds the violated line in O(log n) queries.
- **The knot sphere needs two kinds of point.** It has exactly two (regular points, and twelve at its six digons), and that is where its PPADS-complete contradiction comes from.
- **One exception, computed.** With uniform signs the knot was satisfiable on every uniform law I tested and on all 327 circulant laws up to 48 points, except the Fano plane. The Fano plane fails by its own structure, not through the count.

Provenance: the curvature formula and the list of uniform spheres are classical (vertex-transitive and Cayley maps). Reading them as self-built knot worlds, the bound on uniform contradictions, and the genus-2 antivortex are new as far as I found. Two limits: laws with a few kinds of points are not classified, and whether a large uniform law can fail without the count, as the Fano plane does, is open.

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt (both directions) | **Status:** Successful | (i) The forced face on genus 2 is PPADS-complete. (ii) Uniform laws close into spheres only as small polyhedra or antiprisms, and never force the knot's contradiction. |
| Local direction: laws that build their own surface | Continue, with two kinds of points | One kind of point is settled. The knot sphere shows that two kinds suffice for large spheres and deep contradictions. |
| Broader exploration: question 9 | Known alternatives | Rulers and the number line, growth at open ends, circles from logic, native genus readings, and now self-built closed surfaces. |
| Long-term goal: question 9 and "hardness at three places" | Capability gained | A law builds its own closed surface and the knot's count reads its curvature. Uniformity can grow flat space but not a large sphere, so the knot's deep contradiction needs special places. The count-complexity chain is practically complete. |
| Next recommendation | **Next step:** Research directions. (i) Laws with two kinds of points: which close into large spheres, and can a local growth rule place the six digons itself, so a law grows its own sphere and with it the knot's contradiction? (ii) Large uniform contradictions beyond the Fano plane. Your call. | (i) moves question 9 directly. (ii) asks whether the Fano plane is the only uniform obstruction. |
| Interest | **(i) 2/3 — Promising; (ii) 1/3 — Exploratory** | Euler's formula fixes the budget at six digons, and the knot sphere realizes it with two point types. The open part is whether a rule that doesn't know where the digons go can still close a sphere. |
| Execution | Deferred to you | Not started. |

Commits: ad3709cbb and f914769ba, plus the question-9 entry in the knot intuition doc (3782cd4e6). Notes:
- https://github.com/jscul/knotlab/blob/main/research/COUNT-ANTIVORTEX-20261107-001/count_antivortex.md
- https://github.com/jscul/knotlab/blob/main/research/UNIFORM-SPHERES-20261107-001/uniform_spheres.md
