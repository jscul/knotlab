# Is the standing wave forced?

Epic `WAVE-UNIQUENESS-20261029-001`, 2026-10-29.

## The question

- **The owner's request (2026-10-29).** "Yes, continue," on the recommendation of `SIGNED-3D-20261029-001`. Classify the laws, with
  real or complex weights, that reproduce themselves on consecutive Sierpinski levels, and decide whether every non-degenerate one is a
  standing wave.
- **Setting.** Planar gaskets SG_k with copies of one three-bit law. A law is exact at level k when the corner relation is a nonzero
  multiple of the law.
- **Why it matters.** Three earlier epics found the standing wave building every gasket, in every dimension. The ±1 censuses found nothing
  else that persists. Is the harmony forced by self-similarity, or just the first thing found?
- **Intuitions targeted:** everything relational (harmonies as cancelling phases); space from logic (what a self-similar gluing selects);
  the two/three boundary.

**The evidence:**
- [Symmetric laws: four levels force the standing wave](../../proofs/WAVE-UNIQUENESS-20261029-001A/WAVE-UNIQUENESS-20261029-001A-P001_symmetric_laws_four_levels_force_the_wave/proof.md)
  (A, proof);
- [General three-bit laws: rotations of the wave and implication laws](../../proofs/WAVE-UNIQUENESS-20261029-001B/WAVE-UNIQUENESS-20261029-001B-P001_general_laws_rotations_and_implications/proof.md)
  (B, proof);
- scoping (scratch, not evidence):
  - the first eliminations and the high-precision intersections;
  - an attempt to install a computer-algebra system, which was declined, so all algebra was done in sympy;
  - a numerical search in the W-type stratum. Unconstrained runs converged only to products, because the parametrization can collapse to
    rank one. 150 runs held at full multilinear rank found no law exact at levels 2 and 3. A positive-dimensional W-type family is
    therefore unlikely. Isolated W-type laws do exist (the limits (−1)^a E and the frozen laws, with their images under the symmetries),
    and random starts would miss them, so the stratum stays open.

## Outcome in one paragraph

**Among knots the harmony is forced; among all laws it is joined only by degenerate laws, and it takes four levels to tell.**
- **A (symmetric laws, complete).**
  - A law symmetric in its two non-base corners is exact at levels 2, 3, 4 and 5 iff it is one of these: a standing wave (any complex
    angle, with its limits), a product, a law forcing the two corners equal, or one of two frozen laws.
  - Fewer levels admit impostors. At levels 2 and 3 there is a whole irreducible curve of degree 10 with real points. At levels 2 to 4
    there are 16 complex laws. Each fails the next level.
- **B (general laws).**
  - The generic laws split by a hexagon of vanishing pairings. Three of its covers are rotations of the symmetric case.
  - The other two give a new family, the *implication laws* e₀⊗v⊗y + Jv⊗Jy⊗e₁, with support "a = 1 implies c = 1". They reproduce
    themselves at every level, with a chain-like factor (1 + st)^(k−1).
  - Laws of rank one in a corner give products and equal-corner laws.
  - The stratum of vanishing hyperdeterminant is open.
- **Knots.** In every classified stratum the only knots that reproduce themselves are signed not-all-equal and its rotations.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemmas 4-5 | Two-sector laws: level 2 iff biorthogonal plus one balance; biorthogonality locks the sectors along the edges from A, so level k is one equation Z_k(1) = Z_k(2). |
| A, Theorem 2 | Levels 2-3: the waves and an irreducible curve K (degree 10, real points). Levels 2-4: 16 complex laws (8 conjugate pairs). Level 5 kills them. |
| A, Theorem 1 | Exact at levels 2-5 iff a standing wave (complex angle, limits (−1)^a E and equality), a product, u(a)[b = c], or one of two frozen laws, each exact at every level where its factor is nonzero. |
| A, Corollary 3 | The only knot among them is signed not-all-equal. |
| B, Lemma 1 | General generic laws: level 2 forces a cover of a hexagon of cross pairings; five minimal covers (three pair-symmetric, two cyclic). |
| B, Theorems 2-3 | The cyclic branch gives exactly the implication laws (twelve types), exact at every level by a sector-closure argument. |
| B, Proposition 4 and Corollary 5 | Rank one in a corner: products and u(a)[b = c] up to rotation. In the classified strata, the knots that persist are the rotations of signed not-all-equal. |

## Reading

- **Harmony is forced at the knot level.**
  - In the plane, a three-place knot that reproduces itself on every gasket must be a standing wave: two opposite phases held in step.
  - Everything else that persists is degenerate as a relation: products, equal-corner laws, frozen laws and implication laws. These are
    the laws that do not couple three places.
  - The implication laws make the point exactly. They pass every level, but they compose like a chain of k edges, and a sector change can
    only sweep through the whole gasket.
- **Self-similarity needs depth.** Two levels admit a curve of real impostors, three admit 16 complex ones, and only four separate the
  wave. A law that looks self-similar across two scales need not be.
- **The two/three boundary, once more.** The persistent laws other than the wave are those whose relation is effectively pairwise or
  trivial. Coupling three places and still reproducing at every scale requires interference: a cancelling phase pair.
- **What is still drawn.** The gasket gluing was chosen. This epic classified the laws a fixed gluing admits. The converse, which gluings
  a given harmony admits, is open, and it is the question closest to the program's aim of space not drawn in advance.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — is the standing wave forced? | **Status:** Successful | Symmetric laws are classified completely at levels 2-5. General laws are classified outside the W-type stratum. Among knots the wave is forced; among all laws only degenerate ones join it. Open: the W-type stratum. |
| Local direction — uniqueness on planar gaskets | Practically exhausted | Only the W-type stratum remains. It is completion work, and its symmetric part (ticket A's tangent stratum) gave nothing new. |
| Broader exploration — space from a law (question 9) | Known alternatives | The converse question is open: given the harmony, which finitely ramified gluings does it reproduce on? So is uniqueness in higher dimensions. |
| Long-term goal — space from logic without a drawn space | Capability gained | Building every self-similar scale with a knot requires a harmony. The gluing is still chosen. |
| Next recommendation — which spaces the harmony builds | **Next step:** Continue, as a fresh epic. Run a census of small connected three-corner gadgets (triangles glued at vertices, every vertex in at least two triangles, finitely ramified) on which signed not-all-equal, and the wave family, reproduce themselves. Derive a combinatorial criterion (sector locking plus odd flip parity) and the growth exponents of the towers each gadget builds. | It reverses the question: the law selects its space. A sharp criterion would say which self-similar spaces a knot can build, with nothing drawn but the gadget size. |
| Interest — that recommendation | **2/3 — Promising** | The sector mechanism gives a concrete candidate criterion, and the census is finite at each size. Main uncertainty: whether "space" can be made intrinsic, which needs a native notion of size for gadgets beyond counting triangles. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: the sector mechanism in A and B. Stop when gadgets up to a fixed number of triangles are classified and the criterion is proved or refuted. |

**Recommendation.** **Continue**, as a fresh epic: which spaces the harmony builds (2/3). Three alternatives were considered.
- **Completing the W-type stratum (1/3).** Completion work. A numerical scan found no family there, only the known isolated laws are
  expected, and a proof needs a decomposition that sympy struggles with.
- **Uniqueness on Sierpinski tetrahedra with complex weights (1/3).** The ±1 censuses already point the same way, so it is the same method
  one dimension up.
- **A short write-up of the planar classification (1/3).** Deferred until the converse is known.
