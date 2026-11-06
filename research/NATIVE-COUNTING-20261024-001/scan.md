# Bounded scan: counting native witnesses

Date 2026-10-24. Scope: one bounded idea-and-barrier scan before activating evidence tickets. External sources calibrate selection and
enter claims only as cited hypotheses, never as admitted evidence.

## Question

A native network is a constraint problem in which every variable occurs in exactly two constraints, possibly with pins. Counting its
solutions is a Holant problem. What is known about which constraints make such counting tractable?

## Query families

- Holant dichotomies with the two pins available (Holant^c), symmetric and general.
- Fibonacci gates and holographic algorithms.
- Holant problems on three-regular graphs without pins; planar tractability through matchgates.
- Kac–Ward and Kasteleyn determinants; their extension to surfaces of higher genus.

## Sources and relevance

| Source | Relevance |
| --- | --- |
| Cai, Lu and Xia, *Holographic algorithms by Fibonacci gates*, Linear Algebra Appl. (2013) | Symmetric signatures with f_{k+2} = m f_{k+1} + f_k are tractable on general graphs; their algorithm is a holographic transformation. |
| [Cai, Guo and Williams, *Holographic algorithms beyond matchgates*, arXiv:1307.7430](https://arxiv.org/abs/1307.7430) | Generalized Fibonacci gates are product type after a holographic transformation; [1, 0, 1, 1] is the example of a Fibonacci gate. |
| [Backens, *A complete dichotomy for complex-valued Holant^c*, ICALP 2018, arXiv:1704.05798](https://arxiv.org/abs/1704.05798) | Theorem 15: Holant^c(F) is #P-hard unless F is tractable for Holant* (products of unary and binary functions, orthogonally or K-transformed generalized equalities, K-transformed weight-at-most-one functions), F ⊆ S∘A, or F is local affine. |
| Cai, Huang and Lu, *From Holant to #CSP and back*, Algorithmica (2012), as quoted by Backens (Theorem 6) | Holant on three-regular graphs with a symmetric ternary signature and a binary edge function, without pins: #P-hard outside explicit exceptions. |
| Cai, Guo and Williams, *A complete dichotomy rises from the capture of vanishing signatures*, SIAM J. Comput. (2016) | Symmetric Holant without pins on general graphs. |
| [Lis, *A short proof of the Kac–Ward formula*, arXiv:1502.04322](https://arxiv.org/abs/1502.04322) | For planar graphs drawn with straight edges, det(I − Λ) equals the square of the even-subgraph generating function. |
| [Cimasoni, arXiv:1101.5559](https://arxiv.org/abs/1101.5559); Galluccio and Loebl (1999) | Determinant and Pfaffian formulas on surfaces of higher genus need a number of terms exponential in the genus (4^g Pfaffians for perfect matchings). |

## Imported ideas and local discriminators

- **Native networks with pins are Holant^c instances** with one knot as the only non-unary signature.
- **The gluing criterion as a recurrence.** The topological gluing criterion of `SURFACE-GLUING-20261024-001A` (two glued copies
  symmetric in four legs) reduces, for symmetric signatures, to f0 f2 + f1 f3 = f1² + f2². This is the Fibonacci-gate recurrence when
  f1 ≠ 0.
- **Discriminator for A.** Classify all 34 knots against Backens's families, with positive controls for each family.
- **Discriminator for B.** The Fourier transform of not-all-equal is [6, 0, −2, 0], supported on even weights. So closed not-all-equal
  worlds are even-subgraph sums, that is Ising partition functions.

## Overlaps and barriers

- **Every complexity statement here is classical** or follows from the cited dichotomies.
- **Local contribution.** The identification of topological gluing with Fibonacci gates, and of the topological knots with exactly the
  tractable ones; the reading of counting cost against genus. These are probably known to experts in a different language (Fibonacci
  gates are diagonalizable commutative Frobenius algebras).

## Effect on selection

- Ticket A: the recurrence, the count formula and the classification.
- Ticket B: not-all-equal worlds as Ising models, planar determinants.

## Novelty status

- `known-overlap-found` for the complexity statements.
- `no-overlap-in-bounded-search` for the explicit identification of the two notions in this form. Folklore risk is high.
