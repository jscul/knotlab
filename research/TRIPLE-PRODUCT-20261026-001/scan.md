# Bounded scan: the twisted triple product and bounded-homology hardness

Epic `TRIPLE-PRODUCT-20261026-001`, 2026-10-26.
- **Who did it.** A delegated literature agent, whose report was reconciled here.
- **What it read.** Every source marked "read" below, in full text via pdftotext. The downloads are kept outside the repository, in
  the session scratchpad.
- **What was verified directly in this task:**
  - the text of Massuyeau's Lemma 3.2;
  - Samperton–Weiß v2 §1.1–1.5 and footnote 11;
  - Galindo's dichotomy, read in `DICHOTOMY-3D-20261025-001`.

## Searches

- **Group-theory phrasing.** Counting homomorphisms from 3-manifold groups to finite solvable groups with bounded first homology:
  rational homology spheres, H₁ = Z/p, twisted coefficients.
- **TQFT phrasing**, following the lesson of `DICHOTOMY-3D-20261025-001`. Dijkgraaf–Witten and Turaev–Viro complexity; type-III
  cocycles; Vec(G) for solvable G.
- **Algebra phrasing.** Counting kernels of 3-tensors; homogeneous bilinear systems; average kernel sizes; Gowers U³ norms of
  cubic polynomials; weight enumerators of extension codes.
- **Topology phrasing.**
  - Borromean and Y-surgery and the triple cup product, including torsion and mod-p versions.
  - Sullivan and Turaev realization; equivariant realization.
  - Triple cup products of cyclic covers.
- **Old phrasings.** "cup product forms of 3-manifolds", "triple cup product #P", "cohomology ring complexity".
- **Citation follow-up.** Citations of Samperton–Weiß, Galindo, Kuperberg–Samperton and Bridges–Samperton on Semantic Scholar. No
  citing paper was found for Samperton–Weiß.

## Literature

| Source | Status | Relevance |
| --- | --- | --- |
| Samperton and Weiß, arXiv:2602.02885 (v1 2 Feb, v2 20 Apr 2026) | read | Class-2 nilpotent G with bounded \|H²(M, Z(G))\| is in FP (v2; v1 claimed it for all M). Footnote 11: "not clear that the conclusion … holds in the twisted setting". Whether class 2 is hard is left for future work. |
| Chlopecki and Samperton (announced, "to appear 2026") | not on arXiv | Finite class-2 2-groups encoded by 3-tensors. Maps to D₈ are equivalent to non-homogeneous symmetric bilinear systems over F₂, which they call hard. These are finite groups, not 3-manifolds. |
| Galindo, arXiv:2605.06984 (v2 7 Jun 2026) | read | Turaev–Viro is #P-hard unless the category is trivializable pointed, so \|Hom(π₁M, G)\| is hard for every nonabelian G. The hard instances are graph manifolds with growing b₁. Nothing on bounded homology. |
| Kuperberg and Samperton, Geom. Topol. 22 (2018) | read | Simple targets are hard on homology spheres. Fig. 3 marks nilpotent and solvable targets "?". |
| Delaney, Maria and Samperton, arXiv:2311.08514 | read | Fig. 1: "Vec(G) for G non-abelian solvable — unknown". |
| Bridges and Samperton, arXiv:2503.02945 | read | On restricted classes such as integer homology spheres "the classification might change". |
| Matei and Suciu, J. Algebra 286 (2005) | read | The twisted lifting test ρ*[χ] = 0 in H²_{σρ}(G, A). No complexity bounds. |
| Massuyeau, AGT 3 (2003), Lemma 3.2 | read (verified) | Y-surgery changes the triple cup product with Z_n coefficients by ⟨y₁ ∧ y₂ ∧ y₃, [L₁] ∧ [L₂] ∧ [L₃]⟩. Torsion is allowed; untwisted. Remark 3.3: Turaev's Borromean replacements. |
| Massuyeau, survey arXiv:2301.12428; Hillman arXiv:2410.00560 | read | Sullivan and Turaev realization, untwisted, with H₁ free or the linking pairing prescribed. |
| Niu, arXiv:2606.12094 (June 2026) | read | Borromean band-sums realize arbitrary mod-p triple cup tensors on rational homology spheres with H₁ ≅ (Z/p)⁶. Untwisted, fixed rank. |
| Nosaka, arXiv:1808.08532, Thm 3.1 | read | The trilinear form with coefficients Z[t^{±1}]/(n, t² + t + 1) is the triple cup product of the 3-fold cyclic branched cover of a link. The closest statement to our eigenspace identification; no realization or complexity. |
| Burton, Maria and Spreer, arXiv:1503.04099; Kirby and Melvin, math/0410358 | read | TV₄ is #P-hard through cubic forms over Z/2 on 0-surgeries on large links (spin structures). Unbounded homology; no cup-product language. |
| Rossmann, Bull. LMS 54 (2022); Rossmann and Voll, Mem. AMS 294 (2024) | read | Commuting-pair and average-kernel counts for modules of alternating matrices. Proposition D proves NP-hardness of one related polynomial. Remark 1.6 says it "resembles the Tutte polynomial … unclear … whether this is more than a formal similarity". No complexity result for trilinear kernel counts. |
| Galindo §9 (type-III Dijkgraaf–Witten) | read | Pointed or abelian Dijkgraaf–Witten is in FP exactly when there is no type-III part, and #P-hard otherwise. Unrestricted manifolds; untwisted. |

## Assessment

**No preemption was found** for:
- `TRIPLE-PRODUCT-20261026-001A`: the twisted obstruction as a single cubic form with bounded homology.
- `TRIPLE-PRODUCT-20261026-001C`: the twisted Y-surgery formula and steering with H₁ fixed.
- `TRIPLE-PRODUCT-20261026-001D`: #P-hardness with H₁ = Z/3 for a solvable group of Fitting height 2, and the Potts formula for
  trilinear kernel counts.

**Closest overlaps:**
- Massuyeau's lemma, which is the untwisted engine of C;
- Nosaka, the eigenspace identification in A(e);
- Galindo, hardness with unbounded homology for all nonabelian groups;
- Rossmann, kernel counts without a Tutte link.

**Preempted.** Counting maps to D₈ with unbounded homology is covered by Galindo, so it is not claimed.

**Folklore risk:**
- medium for the Potts gadget (elementary);
- medium for the twisted realization (routine once the cover is used);
- high for A(a)–(c) (standard obstruction theory and duality).
