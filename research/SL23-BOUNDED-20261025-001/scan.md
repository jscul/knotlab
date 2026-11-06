# Bounded scan: SL(2,3) with bounded first homology

Epic `SL23-BOUNDED-20261025-001`, 2026-10-25. Following the lesson of `S4-LIFT-PRIOR-ART-20261025-001`, the scan read the closest
algorithmic source in full and searched both the quantum-invariant and the group-cohomology phrasings.

## Searches

- **Quantum-invariant phrasing.** "counting homomorphisms 3-manifold SL(2,3) binary tetrahedral Dijkgraaf–Witten polynomial time
  bounded homology Gauss sum quadratic".
- **Algorithmic source.** The full text of Samperton and Weiß v2 (arXiv:2602.02885), fetched as a PDF and converted with pdftotext.
- **Background read earlier in this session.** Kuperberg–Samperton, Galindo, Bridges–Samperton, Matei–Suciu (`BOUNDED-H1` scan).

## Literature

| Source | Relevance |
| --- | --- |
| Samperton and Weiß, [*Obstruction theory and the complexity of counting group homomorphisms*](https://arxiv.org/abs/2602.02885) (v2, 20 April 2026) | **Read in full.** See the list below. |
| Matei and Suciu, *Counting homomorphisms onto finite solvable groups* (J. Algebra 2005) | Iterated-cohomology counting for solvable targets, with no complexity bounds (Samperton–Weiß footnote 1). |
| Kuperberg and Samperton, [arXiv:1805.09275](https://arxiv.org/abs/1805.09275) | #P-hard for simple targets, even on homology spheres. Solvable targets are not covered. |
| Chen, [arXiv:1110.0186](https://arxiv.org/abs/1110.0186) | Character formulas for counting coverings of Seifert 3-manifolds. Not general 3-manifolds. |
| Ehrenfeucht and Karpinski (1990), *The computational complexity of (XOR, AND)-counting problems* | Counting zeros of polynomials over GF(2): polynomial for degree 2, #P-complete for degree 3. Cited from memory; not re-read in this scan. |

**What Samperton and Weiß contain.**
- **Theorem 1.** Counting maps from finitely presented groups is #P-complete exactly for non-abelian targets.
- **Theorem 2.** Class-2 nilpotent targets are polynomial on triangulated 3-manifolds with |H²(M; Z(G))| bounded. Remark 1.1.2 says the
  current version "can be proven in an easier way". Bounded H² already bounds the number of maps into a nilpotent group.
- **Lemma 3.1.1.** The obstruction map Hom(Γ, B) → H²(Γ, A) is quadratic.
- **Lemma 3.1.2.** Zeros of a quadratic map into a bounded group can be counted by Gauss sums.
- **Footnote 11.** It is "not clear" that the method works with twisted coefficients.
- **Non-nilpotent targets** are not treated.

## Findings

- **Not found: a polynomial-time result for SL(2,3)**, the binary tetrahedral group, or other non-nilpotent central extensions with
  bounded homology.
- **The method used in ticket A combines two known tools:**
  - the affine twisted lifting of `BOUNDED-H1-20261025-001B`;
  - the quadratic obstruction and Gauss sums of Samperton and Weiß.

  The new point is that the quadratic map's domain is an exponentially large twisted cocycle space, while its target stays untwisted
  and bounded. Novelty is `candidate-local-delta`, with folklore risk medium.
- **The open case** is a twisted obstruction target: central layers that are not central in G. Samperton and Weiß flag it.

## Discriminators

1. **Is the SL(2,3) obstruction quadratic on the twisted lift space?** Yes: proved, and tested at random points.
2. **Are the double covers of S₄ hard?** On knots, yes, immediately. On closed manifolds the naive identity fails, so this stays open.
3. **Next.** A Fitting-height-2 group with a twisted central layer, such as UT₃(F₄) ⋊ Z₃.
