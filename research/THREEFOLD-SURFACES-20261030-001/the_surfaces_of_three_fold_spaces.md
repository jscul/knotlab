# The surfaces of three-regular contradictions

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction; a knot space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `THREEFOLD-SURFACES-20261030-001`, 2026-10-30.

## The question

- **The owner's request (2026-10-30).** "I recommend the surfaces of three-regular contradictions (2/3). Does each space define a closed surface whose
  genus equals its number of Fano pieces? … A yes would be the first place the knot builds a canonical topological object rather than a
  combinatorial class."
- **Setting.**
  - A three-regular contradiction of the knot is read through its triangle–contact incidence graph B(H). H is the dual triple system, a connected
    3-regular triple system that is not 2-colourable.
  - By `THREEFOLD-GRAMMAR-20261030-001`, B(H) decomposes along tight 3-edge cuts into Fano pieces (Heawood graphs) and glue (doubled
    squares, planar braces and trisums of them).
  - The question is about the least genus of a closed orientable surface carrying B(H), and the maps that achieve it.
- **Scoping before activation (not evidence).**
  - Genus is not additive over 3-edge cuts in general: K₃,₃ spliced with K₃,₃ has genus 1.
  - On all eight spaces up to 22 points, SAT gave genus equal to the number of Heawood braces.
  - So the answer had to come from something special about Fano pieces.
- **Intuitions targeted:** space from logic without a drawn space; the two/three boundary.

**The evidence:**
- [Fano pieces are handles](../../proofs/THREEFOLD-SURFACES-20261030-001A/THREEFOLD-SURFACES-20261030-001A-P001_fano_atoms_are_handles/proof.md)
  (A, proof).
- [Exact genera and minimal maps by SAT](../../proofs/THREEFOLD-SURFACES-20261030-001B/THREEFOLD-SURFACES-20261030-001B-P001_exact_genera_and_minimal_maps/proof.md)
  (B, proof by exhaustive and exact computation).
- **Literature.** A bounded search found classical additivity over blocks (Battle–Harary–Kodama–Youngs), near-additivity over
  2-amalgamations (Decker–Glover–Huneke, Stahl) and Alpert's complete-graph amalgamations. It found no statement for 3-edge splices with
  the vertex-deletion hypothesis.

## Outcome in one paragraph

**Yes. Each Fano piece is a handle, and the glue adds none.**
- **The answer.** The least genus of the knot's three-regular contradiction equals its number of Fano pieces whenever the glue is planar. In general
  it is the sum of its pieces' genera, as long as each non-planar piece keeps its genus when a vertex is deleted. The one non-planar glue
  piece found, the trisum of three cubes, does keep it and adds one handle.
- **The reason (A).**
  - Across a 3-edge splice, the genus is exactly additive when one side keeps its genus after its splice vertex is deleted.
  - The proof traces faces across the cut: three permutations of the three cut edges decide the defect. A face that turns back across a
    cut edge costs that side a handle.
  - The Heawood graph minus a vertex is still non-planar (its girth is 6), so Fano pieces always add their handle. K₃,₃ minus a vertex is
    planar, which is why K₃,₃ ⊙ K₃,₃ loses one.
- **The surface is canonical, and its minimal maps are classified (A, B).**
  - Every minimal map is a connected sum of Heawood maps, one per atom, with planar maps of the glue, glued compatibly at each cut.
  - No minimal map crosses a cut in any other way.
  - Their number is 16 per atom (and 4 per doubled square), halved at each cut: 16, 128 and 1024 for one, two and three atoms, exactly as
    enumerated.
  - Up to symmetry there are 1, 2 and 3–6 minimal maps. The choices are each atom's handedness and its position of attachment.
- **The Fano space is the seven-vertex torus.**
  - The Fano plane's minimal map is the Heawood map, unique up to symmetry and chiral.
  - Its dual is K₇ on the torus. The 14 triangles of that seven-vertex torus are the seven points and seven lines of the Fano plane
    (the knot's seven triangles and its seven contacts, the corner line counted as one), coloured like a checkerboard.
- **Confirmed by exact SAT (B).**
  - All 32 classes up to 22 points.
  - Fano compositions, cycles of 5 and 7 blocks, the twisted cube, and prism and truncated-octahedron glue: up to 180 vertices, genus 12.
  - Two spaces whose glue is the trisum of three cubes: a twisted 22-point one and the 35-point one, where the glue adds its handle.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemmas 1–3 | Face-tracing identity across a 3-edge cut, 2(g − g₁ − g₂) = cyc(rτ) + cyc(r̃π) − cyc(πτ) − 3; the S₃ table; a face that turns back costs a handle. |
| A, Theorem 4 | Splice lemma: genus is additive when one side keeps its genus after deleting its splice vertex; fails without it (K₃,₃ ⊙ K₃,₃ = 1). |
| A, Theorem 5 | With both sides rigid, the minimal maps of a splice are exactly the compatible gluings of minimal maps of the sides; count N(A)·N(R)/2. |
| A, Theorems 6–7 | Genus of a three-regular contradiction = number of Fano pieces (planar glue), or the sum of brace genera (rigid non-planar glue); every minimal map is a connected sum of Heawood maps and planar maps; count Π N(B)/2^(cuts). |
| A, Proposition 8 | The Heawood map: 16 rotation systems, one orbit, chiral, dual K₇ with the Fano plane's points and lines as the two colour classes. |
| B | Exact genera by SAT on 32 small classes and 9 large spaces (to 180 vertices); minimal maps enumerated to 19 points (16, 128, 1024; all standard); additivity tests with one rigid side. |

## Reading

- **The knot determines a canonical surface.**
  - The least genus of the incidence graph of its triangles and contacts is an invariant of the space itself, not a drawing.
  - It counts exactly the three-place atoms. The two-place glue is planar and adds nothing.
  - This is the first place in the program where the knot's own space determines a canonical topological object: a closed orientable
    surface, up to homeomorphism.
- **The minimal maps are made from one map.** Every minimal map is built from copies of one chiral map, the seven-vertex torus of the Fano
  plane. Each copy is joined along the glue with a handedness, and the space keeps only finitely many such choices.
- **The two/three boundary.** The three-place obstruction becomes a handle, and the two-place parity glue stays flat.
- **Limits.**
  - This is the topology of an incidence graph, not a native contact topology in the K1–K3 sense, and not a metric.
  - The surface is determined. The minimal map is determined up to those finitely many choices.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the surfaces of three-regular contradictions | **Status:** Successful | The owner's question is answered yes. Genus = number of Fano pieces (planar glue) is proved, minimal maps are classified, and SAT confirms both to 180 vertices. |
| Local direction — genus of three-regular contradictions | Practically complete | Open only for non-planar glue in general: does every trisum keep its genus under vertex deletion? A yes would make the formula unconditional, but it would be completion work. |
| Broader exploration — space from a law (question 9) | Known alternatives | Now that the knot's contradictions have surfaces, the next question is what the law does on them. Mixed contact sizes and spaces with boundary remain unmapped. |
| Long-term goal — space from logic without a drawn space | Capability gained | A canonical surface determined by the knot's own space, with its handles identified as the Fano pieces. |
| Next recommendation — the knot's amplitude on its surface | **Next step:** Continue, as a fresh epic. Prove that the knot's exactness factor λ(0) on a three-regular contradiction is 5 per handle times a factor from planar glue, and find what that factor is. Scratch probe (not evidence): λ(0) = 5^genus at every corner line for all spaces whose glue is doubled squares (7 to 35 points, 12 spaces); the twisted cube, whose glue includes the planar cube, gives 31250 = 2·5⁶. | λ(0) is the law's own number: the factor by which its gadget reproduces it. If it reads off the genus, the knot's quantitative output measures the topology it builds. |
| Interest — that recommendation | **2/3 — Promising** | Clean evidence on twelve spaces and every corner line. Main uncertainties: the glue factor (2 for the cube) may be an ordinary colouring count with no topological meaning, and the factorization over tight cuts may be elementary. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: this epic plus the probe. Stop when λ(0) is proved to factor over tight cuts with the factors identified, or a counterexample shows the atom factor is not 5. |

**Recommendation.** **Continue**, as a fresh epic: the knot's amplitude on its surface (2/3). Two alternatives were considered.
- **Rigidity of trisums (1/3).** Would make the genus formula unconditional; completion-like.
- **Spin structures (1/3).** In the minimal maps up to 19 points every face has length 2 mod 4, so the knot's trivial signs satisfy
  Kasteleyn's face condition and define a spin structure on the surface. Do they always? Speculative.
