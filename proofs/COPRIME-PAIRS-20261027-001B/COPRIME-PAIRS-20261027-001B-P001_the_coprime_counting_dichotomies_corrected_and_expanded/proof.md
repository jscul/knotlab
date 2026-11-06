# The coprime counting dichotomies: the corrected and expanded presentation

Status: Proved

## Standard statement

`presentation.md` (this directory) is a self-contained presentation for independent review. It replaces, for reading, the frozen
presentation of `COPRIME-DICHOTOMY-20261027-001D`, which stays unchanged.

It consolidates the counting results for G = N ⋊ C_r, where N has exponent p and class c < p and r | p − 1, on closed oriented
3-manifolds with H₁(M; F_p) = 0 and boundedly many sectors:
- **Structure** (Lemmas 2.1–2.4). (P2_d) holds iff the parity map θ_d is a Lie automorphism; it then commutes with the action, a
  *compatible parity automorphism*. The action itself need not factor through C₂. Given (P2_d), (P3_d) says θ_d's triple system is
  abelian. The criterion passes to divisors; under (P2_d) only near triples can fail, and brackets obey parity.
- **Theorem A** (polynomial side, every class, no grading).
- **Theorem B1** (class 2), **B2** (pairs hold, triples fail; graded class ≤ 4; every sector order), **B3** (the cross-layer pair).
- **Corollary C**, open only for pair failures in classes 3 and 4.

**Corrections from the independent AI review of `COPRIME-DICHOTOMY-20261027-001`** (§9 of the presentation, items 8–11):
- the parity-automorphism wording;
- the Fox normalization t⁻¹(Bur_t − I);
- the integer exponent in the cable homomorphism (θ′ may have order greater than 2);
- the withdrawn claim that the edge weight does not depend on the κ_t.

**Expansions** (items 12–13): canonical pinned coordinates for the amphichiral class-4 argument; the reading strands and the basis
for both summand families. Their proofs are in `COPRIME-PAIRS-20261027-001A-P001`.

**Also new.** Precise references (§10); all reviews recorded as independent AI reviews with finite V2 checks, not human expert review
or formal certification (header, §12); a remark that (P2_2) always holds, so an algebra failing (P3_2) is hard whenever 2 ∈ 𝒟 (§2.4).

## Nearest known results

See `presentation.md` §11: Samperton–Weiss; Galindo; Kuperberg–Samperton and Rowell; Moussard; Matei–Suciu and Nosaka;
Bulatov–Grohe and Cai–Chen–Lu. Novelty and folklore risk are as stated in the component tickets. This ticket adds no new theorem
beyond them.

## Proof

The mathematical content is in `presentation.md`, §§3–8. Each theorem there is proved in a cited artifact closed as Proved:
- Theorem A: `COPRIME-DICHOTOMY-20261027-001A`;
- B1: `CLASSK-DICHOTOMY-20261026-001C`;
- B2: `COPRIME-PAIRS-20261027-001A` (successor of `COPRIME-DICHOTOMY-20261027-001C`), with d = 2 also in
  `TRIPLE-SYSTEM-20261027-001C`;
- B3: `BEYOND-CLASS2-20261027-001A`.

The presentation's own arguments are the structural lemmas (a few lines each, §3), the corrected Artin identity (§6.2), the Fox
normalization (Lemma 6.2.0), and summaries of the expanded lemmas whose full proofs are in `COPRIME-PAIRS-20261027-001A`.

## What `check.py` verifies

1. Every cited proof artifact has result status Proved and ticket status proved; every cited experiment has verdict and ticket status
   supported.
2. The proof files reviewed by Codex are unchanged: the SHA256 values of `CLASSK-DICHOTOMY-20261026-001C`,
   `BEYOND-CLASS2-20261027-001C`, `TRIPLE-SYSTEM-20261027-001A` and `-001C`, and of `COPRIME-DICHOTOMY-20261027-001A`, `-001C` and
   the `-001D` presentation, equal those recorded in the reviews.
3. The corrections replay:
   - the literal Fox closure rows equal t⁻¹(Bur_t − I) on random braids;
   - the integer-exponent cable map with θ′ of order 6 satisfies the T(2, 13) relators and kills the longitude;
   - the parity-automorphism example: a one-dimensional abelian algebra over F₇ with an order-3 action satisfies the criterion;
   - the reversed Artin identity holds and the forward one fails; J₋₁ is the earlier J.
4. The text: every cited ticket appears in the artifact index; every correction item is present; the replaced wordings
   ("collapse to an involution", "I − Bur_t" as the Fox matrix, the exponent ψ(g), independence of the κ_t) occur only where the
   presentation reports them as corrected; every reference tag used is defined in §10.
