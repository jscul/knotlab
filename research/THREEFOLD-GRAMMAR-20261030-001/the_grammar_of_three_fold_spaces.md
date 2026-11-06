# The grammar of three-fold spaces

Epic `THREEFOLD-GRAMMAR-20261030-001`, 2026-10-30.

## The question

- **The owner's request (2026-10-30).** "Yes, let's continue," on the recommendation of `THREEFOLD-SPACES-20261030-001`.
  - Prove that every three-fold space of the knot is assembled from Fano blocks by splices and odd cycles.
  - Extend the SAT census to pieces with a repeated point on a line.
- **What changed before activation.** The approved grammar is incomplete.
  - Put twisted 14-point pieces on three skew edges of the cube, an arrangement that obeys Kasteleyn's face parity. The result is a
    43-point system (the *twisted cube*) whose tight-cut decomposition contains the cube itself.
  - Splices and cycles of Fano blocks only ever produce Heawood graphs and doubled squares, and the list of braces is unique.
  - The more interesting reading, adopted under the owner's standing rule: is the Fano plane the only leaf, with every planar Kasteleyn
    connector as possible glue?
- **Setting.** By `SPACE-SELECTION-20261030-001C`, the knot's three-fold spaces are the duals of the connected 3-regular triple systems
  that are not 2-colourable. By `THREEFOLD-SPACES-20261030-001A`, these are exactly the systems with a sign-nonsingular incidence matrix,
  i.e. whose cubic incidence graph has a Pfaffian trivial signing.
- **Intuitions targeted:** space from logic without a drawn space; the two/three boundary.

**The evidence:**
- [Fano leaves and planar glue](../../proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue/proof.md)
  (A, proof).
- [Census with doubled incidences](../../proofs/THREEFOLD-GRAMMAR-20261030-001B/THREEFOLD-GRAMMAR-20261030-001B-P001_census_with_doubled_incidences/proof.md)
  (B, proof with exhaustive SAT).
- **Literature:**
  - Robertson, Seymour and Thomas (Annals 1999), Theorem 6.8 and its proof: a Pfaffian brace is the Heawood graph, planar, or a trisum of
    three smaller Pfaffian braces. Read in full.
  - Gorsky, Johanni and Wiederrecht (arXiv 2408.08128), Lemma 3.4: every 4-cycle of a non-planar Pfaffian brace other than the Heawood
    graph is edge-disjoint from another 4-cycle. Statement read, proof not read.

## Outcome in one paragraph

**The knot's three-fold space is made of Fano atoms held together by glue that is planar or assembled from planar pieces.**
- **The atoms are Fano planes, always (A).**
  - Every leaf of the tight-cut decomposition is a Fano plane with one element removed, attached by three edges. So every three-fold
    space other than the Fano plane holds at least two such atoms.
  - The proof is unconditional. A 4-cycle lemma, proved for planar braces by Euler's formula and carried through RST's trisums by
    induction, shows that one twisted edge can never make a brace Pfaffian except the untwisted Heawood graph.
- **The glue is planar Pfaffian (A).**
  - Every other brace is a doubled square, a planar brace, or a trisum built from planar braces.
  - Every planar cubic bipartite graph occurs as glue. A Kasteleyn signing tells where the twisted 14-point pieces go, and the
    decoration is then not 2-colourable. Examples: the cube (43 points), the hexagonal prism (45), the truncated octahedron (90).
  - Original incidences carry no sign, so every 4-cycle of the glue passes through a twisted attachment, like a flux through each face.
  - Non-planar glue really occurs: a 35-point space carries the trisum of three cubes (B).
- **The census and the spectrum (B).**
  - SAT enumerates the cores (systems that may repeat a point on a line) up to 10 points: 160 untwisted and 2,492 twisted classes. Every
    one matches ticket A's predictions.
  - Contracting the Fano atoms of a space leaves a core at least 12 points smaller. So the census decides every space up to 22 points:
    they have exactly 7, 13, 19, 21 or 22 points, with 1, 1, 4, 1 and 1 isomorphism classes.
  - Twisted pieces have 14, 15, 18, 20, 21 or 22 points, with 1, 1, 1, 11, 7 and 3 classes.
  - A direct SAT run confirms the gap at 14 and the uniqueness of T14.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | The approved grammar is incomplete: the twisted cube (43 points) has the cube as a brace, which splices and cycles of Fano blocks never produce. |
| A, Theorem 2 | Structure: 3-edge tight cuts with cubic pieces; a brace with a repeated incidence is the doubled square; every leaf is simple with at most one twist at its contracted vertex; every brace is Pfaffian. |
| A, Lemma 3 | In a Pfaffian brace other than the Heawood graph, every 4-cycle is edge-disjoint from another; non-planar ones have three pairwise edge-disjoint 4-cycles. |
| A, Theorem 4 | One-twist lemma: a brace with a Pfaffian signing negating at most one edge is the Heawood graph, untwisted. |
| A, Theorem 5 | Fano leaves: every leaf is a Fano plane minus a line or minus a point; every space other than Fano holds two disjoint such atoms. |
| A, Theorem 6 | Decoration: every sign-nonsingular signed core becomes a space when T14 and Fano blocks are put on its signed and repeated points; every planar cubic bipartite graph is glue. |
| B, Theorem 1 | Census of cores to 10 points, untwisted and twisted, with every prediction of A confirmed; the one non-planar glue brace is the trisum of three cubes. |
| B, Lemmas 2–4 | Fano pieces act as points and lines; twisted dictionary; every space is a decorated census core with at least two atoms. |
| B, Theorem 5 | Spectrum to 22 points: sizes 7, 13, 19, 21, 22 (classes 1, 1, 4, 1, 1; 3 at 19 up to duality); twisted 14, 15, 18, 20, 21, 22. |
| B, Theorem 6 | Independent SAT at 14 points: no untwisted space; one twisted class, T14, not a brace. |

## Reading

- **Space from a law, two-dimensional and atomic.** A gluing made only of the knot's own three-fold contacts is a space for the knot iff its
  dual resists 2-colouring.
  - Such a space is a two-dimensional (planar, Kasteleyn-signed) web of glue studded with at least two Fano atoms.
  - The planarity is forced by the law through sign parity (Robertson–Seymour–Thomas). It is not drawn.
  - It is a combinatorial planarity of incidence graphs, not a metric.
- **The two/three boundary, once more.** The atoms are the three-place obstruction (the Fano plane). The glue is a two-dimensional parity
  structure whose twists sit where atoms attach.
- **Quantized sizes.** Below 23 points the knot's three-fold spaces come in five sizes, each a small core plus a multiple of six (one atom
  is six points beyond the element it replaces). The gaps at 14–18 and 20 come from the cores.
- **Duality is free.** Transposition preserves sign-nonsingularity. So the dual of every three-fold space is again one, and swapping
  triangles and contacts maps the knot's spaces to its spaces. This settles the "self-dual spaces" alternative left by the previous epic.
- **Method lessons.**
  - The approved grammar was refuted before activation by building the predicted counterexample.
  - The open case of the leaf theorem was closed by reading RST's own trisum form and running a short induction.
  - Two checks of mine were wrong and were corrected by computation:
    - I first assumed a Fano block could not sit on a twisted point, but T14 is exactly that.
    - I first predicted only planar glue, but the trisum of three cubes occurs.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the grammar of three-fold spaces | **Status:** Successful | The approved form was refuted and reframed. The Fano-leaf theorem is proved unconditionally, glue is classified by RST and realized by decoration, and every space up to 22 points is enumerated. |
| Local direction — three-fold spaces of the knot | Practically complete as structure | The description now matches the Pfaffian structure theory: atoms, planar glue, trisums. More sizes or counts would be completion-like. |
| Broader exploration — space from a law (question 9) | Known alternatives | Not yet classified: mixed gluings with locks and free contacts (weighted phase models), and contacts of other sizes. The surface-like picture suggests asking which surface the knot builds. |
| Long-term goal — space from logic without a drawn space | Capability gained | The law's own three-fold spaces have a forced two-dimensional glue and atomic three-place pieces. What remains open is whether the space defines a canonical surface, and how its topology relates to the atoms. |
| Next recommendation — the surfaces of three-fold spaces | **Next step:** Continue, as a fresh epic. Embed the incidence graph of each three-fold space in a closed orientable surface built from the decomposition: planar glue gives spheres, each Fano atom a torus (the Heawood map), splices give connected sums. Then prove or refute that the genus equals the number of Fano atoms. The first discriminator is already positive (scratch probe below). The next is the twisted cube (six atoms) and the 35-point space with trisum glue. | A yes would say that the knot builds a closed surface whose handles are its Fano atoms. A no would show which glue adds or removes handles. |
| Interest — that recommendation | **2/3 — Promising** | The Heawood map (Fano on the torus), Kasteleyn signings as discrete spin structures, and splices as connected sums all point the same way. A scratch probe found the 13-point splice has genus exactly 2: its three cut edges lie on no hexagon, so it has no torus embedding, and local search finds genus 2. Local search also finds genus at most 3 for the 19- and 21-point spaces. Main uncertainties: genus is not additive over 3-edge cuts in general, trisum glue may add handles, and the surface may not be canonical. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: this epic, plus the scratch probe (not evidence). Stop when the genus of the small spaces (up to 22 points, the twisted cube, the 35-point space) is determined and either matches the atom count with a proof over tight cuts, or fails with a classified counterexample. |

**Recommendation.** **Continue**, as a fresh epic: the surfaces of three-fold spaces (2/3). Three alternatives were considered.
- **The knot's amplitude on its spaces (1/3).** λ(0) counts the colourings of the space minus its corner line with that line held fixed.
  Each Fano block contributes 5. Does λ(0) factor over the decomposition? Likely yes and elementary.
- **Mixed gluings with locks and free contacts (1/3).** These are weighted phase models; a census at six triangles would be
  completion-like.
- **A write-up of the three-fold spaces (1/3).** The atoms-and-glue theorem and the spectrum are clean, but they follow quickly from RST,
  so folklore risk is moderate. Deferred.
