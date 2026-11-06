# Independent replay of the S4 knot hardness

Status: Proved

## Standard statement

**What is replayed.** `BOUNDED-H1-20261025-001A` proved three theorems about the alternating diagram D(G⁽³⁾) of a plane graph G with
every edge tripled:
- **Theorem 1 (bicycle law).** The number of S₄ transposition colourings is Σ_{φ: V → Z₃} 2^{c(H_φ) + dim B(H_φ)}. Equivalently, it is
  2^{−n} times a twelve-state spin model with edge matrix J − 2N.
- **Theorem 2 (links).** With every edge subdivided first, the count is 2^{−n}·4^m·Z(G; 12, 1/2). So link counts are #P-hard, with one
  query.
- **Theorem 3 (knots).** Counting homomorphisms from knot groups to S₄ that send meridians to transpositions is #P-hard under Turing
  reductions. The reduction uses gadgets with odd tree and forest counts, doubled non-tree edges and interpolation.

**Result.**
- A separately written code path confirms every finite claim it was tested on.
- A line-by-line audit of the written proof finds no gap.

**Independence.** This is V1. The code path was written by the same agent in the same session, after reading the producer's proof
and parts of its check. It imports nothing from the producer's check, and it rebuilds the diagrams by a different construction. It is
not external or human review.

## Nearest known result

- **The producer's proof**, `BOUNDED-H1-20261025-001A-P001`.
- **Provenance of the bicycle law.** The law is a statement about the twisted cohomology H¹(X; V_φ) of the knot exterior.
  - In `CLOSED-H1-20261025-001B` the lift count over φ is |Z¹(X; V_φ)|/4 per meridian value. So the bicycle law says that, for tripled
    alternating diagrams, dim Z¹ − 1 equals the number of left-right cycles of H_φ.
  - Lifts of dihedral colourings are known to carry homological information about irregular branched covers. Ishikawa (Geom. Dedicata
    2025) says so in his abstract, and the idea goes back to the covering-linkage invariants of Hartley and Murasugi.
  - So a lift formula in covering-space terms may be known.
  - The combinatorial form (left-right cycles of the monochromatic subgraph of a tripled alternating diagram) was not found in the
    bounded scan.
  - The hardness reductions (Theorems 2 and 3) are separate claims and stand whether or not the lift formula is known.

## Audit of the written proof

| Step of `BOUNDED-H1-20261025-001A` | Audit |
| --- | --- |
| Lemma 1.1(a): σ³ fixes pairs of S₃ transpositions | Correct: σ³(a, b) = (3b − 2a, b) = (a, b) mod 3. |
| Lemma 1.1(b): bits swap at equal colours, keep positions plus constants at unequal colours | Correct as stated. It is a finite table fact. The replay tests it indirectly: any coupling between the two strands' bits at a jump twist would break the law on graphs with jump twists, and the law holds on all 16 graphs tested in part 2. |
| Lemma 2.1: S₃ colourings are vertex potentials | Correct: each twist transmits colours by position, and smoothing leaves one circle per black region. |
| Theorem 1: the fibre is an affine space with one dimension per curve | Correct. Bits propagate along curves with no coupling, the section S₃ = Stab(4) gives a lift so the fibre is not empty, and the internal arcs of a twist are determined by its boundary bits. The number of curves is c + dim B, by Rosenstiehl–Read, which is cited. |
| Parity and twelve-state forms | Correct: dim ker L_H = c + dim B via x ↦ δx, and the Fourier step is routine. The replay checks the twelve-state sum against brute force directly (part 2). |
| Theorem 2 | Correct: ½(J − 2N)² = ½(12J − 4J + 4I) = 4J + 2I, and links have 1 + β₁ components. Replayed in part 3. |
| Lemmas 5.1 and 5.2 | Correct. Odd twists permute strands like one crossing, and components number 1 + dim B, which is zero exactly when τ is odd (matrix-tree theorem mod 2). Replayed: odd parallel powers give knots, even ones links (part 4). |
| The gadget S(e, P(e, S(e, e))) | Its matrix 68J + 32I − 8N is recomputed by summing internal states (part 4). |
| Theorem 3, steps 1–4 | Correct. τ(H̃) is odd and P(H̃, 12) = P(H, 12). The 2^{−N} factor counts internal vertices. The bases 5^{2i+j} 3^j 17^{−i−j} are distinct by unique factorization. The Vandermonde system in β² is solvable, and Σ_j N_{0j} counts proper colourings. Sizes are O(m³). Replayed in parts 4 and 5. |

No gap was found. One point of presentation: Theorem 3's count formula is the twelve-state form applied to the substituted graph, with
every gadget summed out. The replay checks that formula end to end against brute force on four knots (part 4), not only through
Theorem 1.

## Replay

`check.py` uses the standard library only and imports nothing from the producer's check. Its output is `result.json`.

1. **Diagrams.**
   - The alternating diagram is rebuilt from ports and corners. The corner at v joins (e, v, +) to (succ_v(e), v, −), and the strand
     (e, u, +)–(e, w, +) is over.
   - On 19 plane graphs (11 named, 8 random), every diagram:
     - alternates;
     - has 1 + dim B(G) components, with dim B computed from the Gram matrix of the cut space;
     - has determinant |Δ(−1)| equal to the spanning-tree count.
2. **Bicycle law.** On the tripled diagrams of every tested graph with at most 7 vertices (16 graphs), the brute-force count of S₄
   transposition colourings of the Wirtinger presentation equals both the bicycle-law sum and the twelve-state sum. This includes the
   4-cycle with two pendant edges, where the law without the bicycle term fails.
3. **Links.** For the subdivided edge, path, theta graphs, C₃ and C₄, the brute-force counts equal 2^{−n}·4^m·Z(G; 12, 1/2), and the
   component counts are 1 + β₁.
4. **Gadgets and knots.**
   - The gadget matrix is 68J + 32I − 8N.
   - For the hosts edge, path and C₃, odd parallel powers give knots and even powers give links.
   - Brute-force counts of four gadget knots (edge with k = 1 and 3, path and C₃ with k = 1) equal 2^{−N}·68^{km}·Σ N_ij β_ij^k.
5. **Interpolation.** For K₄, C₅ and the diamond:
   - doubling the non-tree edges gives an odd tree count and the same P(H, 12);
   - the bases are distinct;
   - the exact Vandermonde solve recovers P(H, 12) from the predicted counts;
   - the diagrams for k = 1 and 3 are knots.
6. **Controls.**
   - The law without the bicycle term is rejected.
   - Wrong Potts parameters are rejected.
   - A wrong gadget matrix is rejected.

## Scope

- **Covered.** The tested diagrams, and the written argument of `BOUNDED-H1-20261025-001A`.
- **Independence.** V1 only. The same agent wrote both code paths in one session.
- **Cited, not re-proved.** Rosenstiehl–Read and Vertigan.
- **Not done by brute force.** The large interpolation diagrams are not colour-counted directly. Their counts come from the
  twelve-state formula, which parts 2 and 4 test.
- **No overclaim.** No claim about P versus NP.
