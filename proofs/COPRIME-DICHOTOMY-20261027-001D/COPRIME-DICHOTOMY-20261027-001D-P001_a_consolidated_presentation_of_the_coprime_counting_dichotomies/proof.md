# A consolidated presentation of the coprime counting dichotomies

Status: Proved

## Standard statement

`presentation.md` (this directory) is a self-contained, corrected presentation for independent review. It consolidates the
counting results for G = N ⋊ C_r, where N has exponent p and class c < p and r | p − 1, on closed oriented 3-manifolds with
H₁(M; F_p) = 0 and boundedly many sectors. It states and proves (or cites, with the chain of reasoning) the following.

- **Structure** (Lemmas 2.1–2.4).
  - The pair condition (P2_d) holds iff the C_d action collapses to an involution θ_d.
  - Given (P2_d), the triple condition (P3_d) holds iff θ_d's triple system is abelian.
  - The criterion passes to divisors. Under (P2_d) only near triples can fail, and brackets obey parity.
- **Theorem A** (polynomial side, every class, no grading). The criterion at the sector order gives the rigid count
  Π_{α≢0} |Z¹(π; F_p^{αψ})|^{dim 𝔤_α}.
- **Theorem B1** (class 2). A pair failure gives #P-hardness (class-(K) route, with knot groups as well).
- **Theorem B2** (graded, class ≤ 4, every sector order d). (P2_d) holding with (P3_d) failing gives #P-hardness, on S³_{d/p}(K)
  for d ≥ 3 and on S³₂(K) for d = 2.
- **Theorem B3.** The cross-layer pair is #P-hard although its class-2 quotient is easy.
- **Corollary C.** The dichotomy for graded algebras of class ≤ 4 and sector orders in a divisor-closed set 𝒟. It is open only for
  algebras of class 3 or 4 whose criterion fails, at every failing d ∈ 𝒟, through a pair failure.

**Corrections incorporated** (§9 of the presentation). Frozen predecessors are unchanged.
- The reversed Artin-product identity replaces the forward one in `BEYOND-CLASS2-20261027-001C` Lemma 2.2(iii). The same
  left-kernel vector, up to sign, results.
- The polynomial side needs a bounded number of sectors and no grading.
- Lemma I (anchor isolation) is a reduction for each fixed group.
- The r > 2 channel terms are removed by slope d/p, and local Massey terms by the summand constructions.
- B2 needs (P2_d).
- r counts the characters of the action, not Boolean variables; these are counting-complexity statements only.
- The crashed first run of the r > 2 experiment is kept as invalid.

The presentation separates uniform proof obligations (§13), classical ingredients (§10), literature (§11) and finite validation
(§12).

## Nearest known results

See `presentation.md` §11.
- Samperton–Weiss (arXiv:2602.02885): class 2, bounded H².
- Galindo (arXiv:2605.06984): unbounded homology.
- Kuperberg–Samperton and Rowell: solvable targets open; Rowell's conjecture.
- Moussard: equivariant triple intersections.
- Bulatov–Grohe and Cai–Chen–Lu.

Novelty and folklore risk are as stated in the component tickets. This ticket adds no new theorem beyond them. It consolidates and
corrects them.

## Proof

The mathematical content is in `presentation.md`, §§3–8. Each theorem there is proved in the cited artifact, and every one is
closed as Proved:
- Theorem A: `COPRIME-DICHOTOMY-20261027-001A`;
- B1: `CLASSK-DICHOTOMY-20261026-001C`;
- B2: `COPRIME-DICHOTOMY-20261027-001C`, with d = 2 also in `TRIPLE-SYSTEM-20261027-001C`;
- B3: `BEYOND-CLASS2-20261027-001A`.

The presentation's own arguments are of two kinds:
- the structural lemmas, re-proved in a few lines;
- the corrected Artin identity, proved in §6.2.

## What `check.py` verifies

1. Every cited proof artifact has result status Proved and ticket status proved. Every cited experiment (including
   `COPRIME-DICHOTOMY-20261027-001B-E002`) has verdict and ticket status supported.
2. The SHA256 values of `CLASSK-DICHOTOMY-20261026-001C`, `BEYOND-CLASS2-20261027-001C`, `TRIPLE-SYSTEM-20261027-001A` and
   `TRIPLE-SYSTEM-20261027-001C` equal those recorded by the independent reviews, so the frozen predecessors are unchanged.
3. The corrections replay:
   - the reversed Artin identity holds on 40 of 40 random braids, and the forward one fails on most of them;
   - the Squier form at t = −1 equals the earlier J for n ≤ 12.
4. The presentation's artifact index names every cited ticket, and its corrections section names each correction.
