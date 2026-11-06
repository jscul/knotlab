# Bounded scan: coprime class-2-by-cyclic groups with bounded homology

Epic `COPRIME-CLASS2-20261026-001`, 2026-10-26.
- **Where the scan lives.** It is the TQFT-phrased prior-art pass recorded in full in
  [`../COPRIME-CLASS2-20261026-001A/review.md`](../COPRIME-CLASS2-20261026-001A/review.md), section "Prior art". This file adds the
  follow-up on Rowell's conjecture and the conclusions for this epic.
- **The earlier scan.** `TRIPLE-PRODUCT-20261026-001/scan.md` is not repeated.

## Searches

**TQFT phrasings.**
- Dijkgraaf–Witten, Turaev–Viro and Reshetikhin–Turaev complexity on rational homology spheres, lens spaces, Dehn surgeries on knots,
  and manifolds with bounded H₁.
- Twisted Dijkgraaf–Witten theories, G-crossed theories, and cubic (type-III) phases.

**Group-theory and topology phrasings.**
- Heisenberg-group counts and triple cup products, including equivariant versions.
- Kernel counts of 3-tensors.
- Y-surgery and equivariant triple intersections.

**Recency and citation follow-up.**
- Every 2026 paper (July–October) by Samperton, Galindo, Kuperberg, Chlopecki, Weiß, Maria, Spreer and Delaney.
- Rowell's original paper and the later papers that cite it.

## Literature

| Source | Status | Relevance |
| --- | --- | --- |
| Rowell, "Two paradigms for topological quantum computation", Contemp. Math. 482 (2009), arXiv:0803.1258, §3.3.5 | read | "Conjecture 3.2. Let G be a finite group and L a link. (a) There exists an FPRAS for computing H_L(G) for any group G. (b) Suppose G is solvable. Then there is a polynomial algorithm for exact computation of H_L(G)." Here H_L(G) = \|Hom(π₁(S³ ∖ L), G)\|. Supporting facts: abelian G; nilpotent G on knots (H_L = \|G\|, Eisermann); Matei–Suciu. |
| Kuperberg and Samperton, Geom. Topol. 22 (2018), §5.3 | read | They paraphrase (b) for "any link complement M" and add: "We are much less confident that this more precise conjecture is true." Fig. 3 marks solvable targets "?". |
| Krovi and Russell, CMP 2015 | read | D(A_n) invariants are #P-hard to evaluate exactly, citing Rowell's conjecture. A_n is not solvable. |
| Rowell and Wang, Bull. AMS 2018 | read | Weakly integral categories should give link invariants approximable in polynomial time. |
| Delaney, Maria and Samperton, arXiv:2311.08514 | read | For closed manifolds, "Vec(G) for G non-abelian solvable — unknown". They also say 2-step nilpotent G "should also be in fP"; Galindo later contradicted that with unbounded homology. |
| Moussard, Ann. Fac. Sci. Toulouse (2017), arXiv:1403.0446 | read | Rational, infinite-cyclic precursor of our steering formula (Prop. 2.5, Thm. 2.7). |
| Maria and Spreer, FoCM 2020 | read | TV₄ polynomial with first homology of bounded rank. |
| Delaney and McPhail-Snyder, arXiv:2608.02795 | read | Turing equivalences, with no hardness. |
| Chlopecki and Samperton | not public | Non-homogeneous symmetric bilinear systems; watch for overlap. |

## Assessment

**No earlier refutation, proof or partial result was found** for Rowell's Conjecture 3.2(b) for any nonabelian solvable G.

**This program's results bear on it directly.** Each item below fails the conjecture, unless every #P function is computable in
polynomial time:
- `BOUNDED-H1-20261025-001A` with `SL23-BOUNDED-20261025-001B` make exact counting for S₄ on knot groups #P-hard.
- `COPRIME-CLASS2-20261026-001D` does the same for UT₃(F₄) ⋊ C₃ and for every Heisenberg-by-cyclic group with a hard pair.

**The positive side is consistent with the conjecture:**
- abelian-by-nilpotent targets (`BOUNDED-H1-20261025-001B`);
- coprime class-2 targets without a hard pair (`COPRIME-CLASS2-20261026-001C`).

**Folklore risk:**
- medium for the hardness, since the method is new in combination but each step is classical;
- medium to high for the steering, because of Moussard.
