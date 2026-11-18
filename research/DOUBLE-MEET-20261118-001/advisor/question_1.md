You are advising a research thread before it freezes a study. Work only from what is written here; you have no files or tools. Be concrete; say plainly where you are unsure.

Setting. Boolean variables ("distinctions") and constraints ("knots"). Here every knot is NAE (not-all-equal) on three variables. A set S is FREE if the projection of the allowed states onto S is all of {0,1}^S, CONSTRAINED otherwise; a BOND is a constrained set all of whose (|S|-1)-subsets are free. Bond distance b(x,y) = (least bond holding x and y) - 1, infinite if none. Steps apart = number of knots on a least chain from x to y.

Base of interest: patches of the triangular lattice (the "weave"): vertices are distinctions, every lattice triangle in the patch is an NAE knot. Coordinates (i,j); up triangle u(i,j) = {(i,j),(i+1,j),(i,j+1)}, down triangle d(i,j) = {(i+1,j),(i,j+1),(i+1,j+1)}. NAE on the triangular lattice = ground states of the triangular Ising antiferromagnet; each triangle has exactly one equal pair, so states (mod global flip) are dimer coverings of the dual honeycomb, with boundary pairs (pairs in one triangle only) usable as half-dimers. Known (program, proved): on the endless weave b = steps + 1 for every pair (height function, difference constraints).

Findings so far (computed, exploratory):
1. On every DISC patch tested (355 random simply connected patches, up to 15 vertices; plus hexagons, triangles, trapezoids, parallelograms, an L-shape), every pair held by some bond has b EXACTLY = steps + 1.
2. The only pairs held by no bond are pairs of "corners" (vertices lying in a single triangle) whose triangles are of opposite kinds (one up, one down) and that sit "back to back": the far corner z is reached from x by p steps along one and q steps along the other of the two lattice directions from x to its triangle's other vertices (p, q >= 1). Same-kind corner pairs always had a bond (1,009 of 1,009); opposite-kind pairs not back to back always had a bond (576 of 576).
3. Among back-to-back opposite pairs: 329 no bond, 74 with a bond. "The parallelogram spanned by x and z lies inside the patch" predicts it imperfectly: inside -> 293 no bond, 52 bond; not inside -> 36 no bond, 22 bond.
4. Every lattice parallelogram a x b (a, b in 2..4, also 2x5) has exactly ONE pair held by no bond: its two acute corners (one in an up triangle, the other in a down triangle). The 2x2 parallelogram is two knots sharing two distinctions (a "lone double meeting"); its two thirds are those corners. Hexagonal patches (no vertex in a single triangle), triangles, trapezoids and cylinders are metric; tori too.
So in the weave a double meeting is harmless; the harmful thing is a pair of opposite-kind corners back to back.

Mechanism I see: a corner x in triangle {x,u,v} is forced only when u = v is forced with fixed values (then x = not u), i.e. when that triangle's dimer is forced onto its interior pair uv.

Questions.
1. Can you state an exact criterion for which back-to-back opposite-kind corner pairs have no bond, in terms of the patch (e.g. dimers/lozenge tilings, height function, a flux or tilt through the strip between them, boundary shape)? Give your best conjecture that fits facts 2-4 and how I could test it cheaply.
2. Can you prove (or sketch a proof of) fact 1 (b = steps + 1 whenever finite) on simply connected patches, perhaps adapting the endless-weave height-function proof? Or the easier half: b <= steps + 1 whenever a bond exists, or b >= steps + 1 always?
3. Can you prove the necessary condition in fact 2: a pair with no bond must be two corners of opposite kinds back to back? E.g. show a bond exists for every pair that is not of that form.
4. Is anything like this known (TIAFM / lozenge tilings / forcing / "defects" of opposite charge)?
5. Predictions you'd freeze for a census of all disc patches up to ~10 triangles, random ones up to ~16 vertices, parallelograms to 3x5, and closed weaves.
