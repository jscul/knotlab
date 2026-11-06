# Bounded scan: S4 counting on closed manifolds with bounded first homology

Epic `CLOSED-H1-20261025-001`, 2026-10-25. This is the novelty and overlap scan for the three tickets. It covers web searches for this
epic plus the scan of `BOUNDED-H1-20261025-001` (`research/BOUNDED-H1-20261025-001/scan.md`), which already covered the quantum-invariant
phrasings: Dijkgraaf–Witten, Turaev–Viro, Reshetikhin–Turaev and Tambara–Yamagami.

## Searches

- **Quandle colourings.** "connected quandles of order 6 same number of colorings", "Galkin quandle colorings proved", "C[6,1] C[6,2]".
- **The 2009 conjecture.** "Carter Oshiro Saito conjecture 3-colorable R̃3 proved".
- **Ishikawa's paper.** "Ishikawa Galkin hyper-octahedral", and the exact title of Ishikawa 2025.
- **Longitude obstructions.** Eisermann's knot colouring polynomials (§2B) and Johnson–Livingston.
- **Bounded-homology hardness for solvable groups.** Carried over from the previous scan.

## Literature

| Source | Relevance |
| --- | --- |
| Clark, Elhamdadi, Hou, Saito, Yeatman, [*Connected quandles associated with pointed abelian groups*](https://arxiv.org/abs/1107.5777) (Pacific J. Math. 264, 2013) | Table 1 lists C[6,1] = G(Z₂, [0]) and C[6,2] = G(Z₂, [1]). Remark 6.6 conjectures equal colouring numbers for C[6,1] and C[6,2] (and other pairs) on all knots, from 2,977 knots up to 12 crossings. Remark 6.8 gives a virtual knot where they differ. **Ticket B proves the conjecture for this pair.** |
| Clark, Elhamdadi, Saito, Yeatman, [*Quandle colorings of knots and applications*](https://arxiv.org/abs/1312.3307) (J. Knot Theory Ramifications, 2014) | §5 restates the conjecture C[6,1] ≈ C[6,2] as open, with equal colouring numbers on all knots. §6 supports it with an epimorphism invariant up to 12 crossings. Proposition 5.4 proves Q ≈ Q* for simple quandles of prime-power order, which does not cover this pair. **Still open as of 2014; ticket B proves it.** |
| Carter, Oshiro, Saito, [*Symmetric extensions of dihedral quandles and triple points of non-orientable surfaces*](https://arxiv.org/abs/0905.3374) (Topology Appl. 157, 2010) | Conjecture: every 3-colourable classical knot is non-trivially coloured by R̃₃, which is C[6,2]. A virtual counterexample is given. **Follows from ticket B.** |
| Ishikawa, [*Generalization of Galkin quandles and lifting property of dihedral colorings*](https://link.springer.com/article/10.1007/s10711-025-01030-5) (Geom. Dedicata 219, 2025) | **Abstract only; the full text is paywalled.** It proves that every colouring by the dihedral quandle of order 2m + 1 lifts to the (2m + 1)-dimensional hyper-octahedral quandle, and that lifts carry homological information about irregular branched covers. It cites Carter–Oshiro–Saito and Clark et al. It may contain the existence statement of the 2009 conjecture. The abstract does not mention equal counts. **Overlap risk: medium for existence, unknown for counts.** |
| Eisermann, [*Knot colouring polynomials*](https://msp.org/pjm/2007/231-2/pjm-v231-n2-p04-p.pdf) (Pacific J. Math. 231, 2007), §2B and Prop. 2.5 | The set of longitude images is a subgroup of C(x) ∩ G′, characterized by Johnson and Livingston (Trans. AMS 311, 1989) through homological obstructions. Prop. 2.5: the longitude of a connected sum is the product of the longitudes. **Ticket B(a) is an instance of this theory (folklore risk high).** |
| Kuperberg and Samperton, [arXiv:1707.03811](https://arxiv.org/abs/1707.03811) and [*Coloring invariants of knots and links are often intractable*](https://arxiv.org/abs/1907.05981) | Hardness for non-abelian simple groups on homology spheres and on knots. A solvable group has only the trivial map from a homology sphere, so solvable targets need H₁ ≠ 0. |
| Galindo, [arXiv:2605.06984](https://arxiv.org/abs/2605.06984) (2026) | #P-hard for every non-abelian group when homology may grow. |
| Bridges and Samperton, [*Towards a Complexity-Theoretic Dichotomy for TQFT Invariants*](https://arxiv.org/abs/2503.02945) (TQC 2025) | Notes that for restricted classes (knots, links, homology spheres) the classification may change. |
| Samperton and Weiß, [arXiv:2602.02885](https://arxiv.org/abs/2602.02885) (2026) | Class 2 targets are polynomial with bounded H². No bounded-homology statement for solvable targets of higher class. |

## What the scan found and did not find

- **Not found: a proof of the 2013 conjecture.** No source proves equal colouring numbers for C[6,1] and C[6,2] on all knots. The
  closest is Ishikawa 2025, whose content beyond the abstract is unknown here.
- **Not found: bounded-homology hardness for a solvable target** on closed 3-manifolds.
- **Found: the longitude obstruction** for transposition colourings is an instance of known peripheral-obstruction theory.

## Discriminators

1. **Replay.** Does an independent code path confirm the knot hardness of `BOUNDED-H1-20261025-001A`? This is ticket A.
2. **Peripheral data.** Are transposition and 4-cycle lifts equinumerous over every S₃ colouring, with transposition longitudes
   trivial? This is ticket B. A counterexample on the hard knots would stop the closed route.
3. **Closed counts.** Do two surgeries isolate the transposition count? This is ticket C.

## Barriers and caveats

- **Duality is cited.** Ticket B uses half-lives-half-dies with local coefficients. It is standard, but cited rather than proved.
- **Ishikawa may overlap.** If his full text proves equal counts, B's novelty drops to "a short proof". The closed-manifold hardness
  (C) is unaffected.
- **Independence.** The replay is V1: same agent, same session.
