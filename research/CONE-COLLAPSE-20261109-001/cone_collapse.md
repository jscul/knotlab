# The cone behind the collapse at powers of two

Epic `CONE-COLLAPSE-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `FULL-REACH-PROOF-20261108-001` computed that on the n × n torus of rule-60 rings cut open both ways every
  eigenvalue of the walk over GF(2) is a (2n − 1)-th root of unity exactly at n = 4, 8, 16, 32, 64 among sides 3 to 64, and reduced the
  spectrum at powers of two to a 2n × 2n determinant on the cut lines. Its direction 1, the collapse at every power of two, had the
  coordinator's go-ahead on 2026-11-09, after `TIE-LAW-20261109-001`.
- **The question.** Compute the Smith form of the cut-line matrix at 4, 8, 16, look for a row reduction that holds at every power of
  two, and prove the collapse there, or find a power of two where it fails.

## The question in standard terms

A is the adjacency matrix over GF(2) of the alternating medial digraph of the n × n grid with the outer face's arcs removed. Is every
eigenvalue of A in GF(2n)* when n is a power of two, that is, does A^(2n − 1) − I nilpotent hold there?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Two particles.** A = T_e ⊗ R + T_o ⊗ L = L ⊗ T_e + R ⊗ T_o: a contact is two particles on one side's 2n − 1 sites, one crossing an even or odd bond while the other steps right or left. | proved | A |
| 2 | **Four copies of a cone.** At every side the quarter turn acts freely and commutes with A, so det(xI − A) = det(xI − A_cone)⁴ for the walk on its n(n − 1)/2 orbits. | proved | A |
| 3 | **The dyadic resolvent.** At n = 2^m the uncut walk's 2^j-th power is the four translations by 2^j, so (I − wM)⁻¹ = (I + wM) ∏_{j=1}^{m−1} (I + w^(2^j) τ_(2^j)). | proved | A |
| 4 | **The cone is a return map.** At n = 2^m, det(I − wA_cone) = det(I + C_s(w)): C = (I + w²K)HJ is the cut line's first passage around the corner, C_s its action on J-symmetric vectors, an (n/2) × (n/2) matrix of odd polynomials of degree at most n + 1. | proved | A |
| 5 | **The Smith form.** At 4, 8 and 16 the invariant factors of I + C_s are the cone's Jordan data. | computed, exact | A |
| 6 | **The Jordan law.** At 4 to 64 every eigenvalue λ of the cone is a (2n − 1)-th root of unity, of multiplicity k(k + 1)/2 with Jordan blocks 2k − 1, 2k − 5, ..., the pattern of a symmetric square in characteristic 0. | computed, exact | A, stress test |
| 7 | **The parity law.** The multiplicity is odd exactly when Tr(1/λ) = 1; equivalently tr(A_cone^j) = 1 exactly when j is a power of two mod 2n − 1. | computed, exact | A, stress test |
| 8 | **Stability.** The cone polynomials det(I − wA_cone) of sides n and 2n agree below degree 2n and differ there. | computed, exact | A, stress test |
| 9 | **The return map's characteristic polynomial.** Its j-th coefficient has w-adic valuation j(2j − 1), the first is w + w³, the next to last is w^((h−1)(2h−3)) (Σ_{i<m} w^(2^i − 1))², h = n/2: the trace of C_s⁻¹ is w^(−(2n − 1)) times a trace polynomial of GF(n). | computed, exact | A, stress test |

## Answer

The collapse is not proved; the structure around it is much narrower now. The walk is two particles on one segment, and its spectrum is
four copies of the spectrum of a cone, the box folded by its quarter turn. At powers of two the cone's spectrum is one (n/2) × (n/2)
determinant, the return map of the cut line around the corner, and its Smith form is the cone's Jordan data, as the coordinator's first
step asked. The eigenvalues follow a rigid law at every side read (4 to 64): λ appears k(k + 1)/2 times with Jordan blocks
2k − 1, 2k − 5, ..., the multiplicity is odd exactly when Tr(1/λ) = 1, and the cone polynomials of n and 2n agree to degree 2n. No power
of two breaks the pattern. What is missing is the reason the eigenvalues lie in GF(2n), which the laws suggest is a hidden symmetric
square.

## Reading

**Interpretation, not a theorem.**
- **A symmetric square.** The multiplicities k(k + 1)/2 and the blocks 2k − 1, 2k − 5, ... are what a two-particle system gives when
  each particle has one Jordan block of size k: the symmetric square of an sl₂-module in characteristic 0. In characteristic 2 neither
  the symmetric nor the exterior square of a Jordan block has this type (table below), so the pattern is not a formal accident of
  squaring. Theorem 1 shows the two particles; the single-particle object whose square the cone is has not been found.
- **Why GF(2n) and not GF(n).** Squared, the walk is two free particles except on the top and bottom rows, where one direction of the
  move is lost. Without that loss the eigenvalues would lie in GF(n) (the path on n sites has its eigenvalues there); GF(n) and GF(2n)
  meet only in GF(2), so the one-way rows move the whole spectrum.
- **Stability.** Short cycle collections near the cone's apex do not see the far boundary, so the cone polynomials converge 2-adically
  as the side doubles; the parity law says the limit's odd multiplicities are a trace.
- **Nothing here is a length or a distance.**

Jordan types (kernel dimensions of the nilpotent part, power by power) in characteristic 2, against the law:

| k | the law: blocks 2k − 1, 2k − 5, ... | Λ² of a block of size k + 1 | Sym² of a block of size k |
| --- | --- | --- | --- |
| 2 | 1, 2, 3 | 1, 2, 3 | 2, 3 |
| 3 | 2, 3, 4, 5, 6 | 2, 4, 5, 6 | 2, 4, 5, 6 |
| 4 | 2, 4, 6, 7, 8, 9, 10 | 2, 4, 6, 7, 8, 9, 10 | 3, 6, 8, 10 |
| 5 | 3, 5, 7, 9, 11, 12, 13, 14, 15 | 3, 5, 7, 9, 11, 13, 14, 15 | 3, 6, 9, 11, 12, 13, 14, 15 |
| 6 | 3, 6, 9, 11, 13, 15, 17, 18, 19, 20, 21 | 3, 6, 9, 12, 15, 17, 19, 21 | 4, 7, 10, 13, 15, 17, 19, 21 |

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every computation is exact over GF(2) or GF(2)[w]: kernel dimensions of exact matrix polynomials, Bareiss and
  Berkowitz determinants, an exact Smith form.
- **Census-only.** Conclusions 5 to 9, read at sides 4 to 64 (the Smith form at 4, 8, 16; the return map's characteristic polynomial
  at 4 to 32), and at 128 in the stress test.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The collapse (4 to 64) | side 128, a cone of 8128 states | pass: A_cone^(255 · 32) = I exactly, so every eigenvalue is a 255-th root of unity |
| The Jordan law and the parity law (4 to 64) | every class of 255-th roots of unity at 128 | stress test pending (CONE-COLLAPSE-S1, `docs/LONG_RUNNING.md`; the classes read so far pass) |
| The traces (j to 2n − 1, sides 4 to 64) | j = 1 to 255 at 128 | pass: tr(A_cone^j) = 1 exactly at the powers of two mod 255 |
| Stability (n = 4 to 32) | the cone polynomials of 64 and 128, to degree 128 | pass: they first differ at degree 128 |
| The return map's characteristic polynomial (4 to 32) | 64, and the trace at 128 | pass |

The script is `stress_test.py` beside this note, with `stress_test.json` and `stress_test_log.txt` (written as each stage ends).

## Literature and provenance

- **Sources.** Schur complements and Jacobi's complementary minors; modules over GF(2)[Z/4] = GF(2)[ε]/(ε⁴); Lucas' theorem and the
  Frobenius on commuting translations; the Clebsch–Gordan rule for sl₂; rule 90 with null boundaries over GF(2) (Martin, Odlyzko and
  Wolfram 1984; Sutner's σ-automata).
- **Related records here.** `FULL-REACH-PROOF-20261108-001` (the reduction to the cut lines, extended here); `HONEY-REACH-20261109-001`
  and `LATTICE-REACH-20261109-001` (symmetries that pair up walks on uncut tori).
- **Classification.** New as far as found; no literature search beyond these sources was made.

## Workspace assumptions

- **Relied on.** A30, A32, A37, A38, as `FULL-REACH-20261108-001`.
- **Added.** None.
- **Scope.** The square torus of rule-60 rings with equally spaced law-(12, 12) contacts, cut open both ways.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (four theorems, nine checks) and the stress run.
- **Administrative.** This note and the closure.

## Corrections

None to published claims. One slip inside this epic, before anything was committed: the stability was first read as agreement below
degree n; the check's own failure showed it is below degree 2n, and the statement was corrected before it was recorded.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the collapse at every power of two | **Status:** Inconclusive | Four reductions proved and the Smith form computed; the collapse is not proved |
| Local direction — composed topology across time on the cut-open torus | Continue | The eigenvalues follow a rigid, testable law that points at a mechanism |
| Broader exploration — G5 with G1 | Known alternatives | Backlog B22 to B43 |
| Long-term goal — G5 Dynamics (question 4) | No demonstrated advance | Why powers of two are special is narrowed, not proved |

**Corrections:** none. **Goals:** a G5 checkpoint (no demonstrated advance). **Assumptions:** none added.

- **What the attempt leaves open.** The collapse at every power of two; why the multiplicities are k(k + 1)/2; the failing set; full
  reach at the other sides.

**Next step:** Continue — selected: #2, the return map digit by digit, at the coordinator's go-ahead (2026-11-09), following it into #1 if the recursion exposes the single particle; #3 parked as backlog B44.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The single particle behind the symmetric square | 3/3 — Breakthrough | 1/3 — Stated | Look for an operator on n or 2n − 1 sites whose symmetric square, eigenvalue by eigenvalue, has the cone's Jordan data at 4, 8, 16 → a proof of the collapse, or a reason no such operator exists | Alternative · within #2 |
| 2 | The return map digit by digit | 2/3 — Substantial | 2/3 — Testable | Write C_s through Theorem 3's dyadic product as a sum over binary digits and look for a recursion in m for det(I + C_s) → a proof, or a digit where the recursion fails | Selected · started |
| 3 | Prove the parity and trace laws | 1/3 — Incremental | 2/3 — Testable | Count closed walks of the cone near its apex with Lucas' theorem → a proof of tr(A_cone^j) = [j a power of two] for j < 2n, or a counterexample | Alternative · parked (B44) |

1. **The symmetric square.** Payoff 3: a single-particle picture would explain the field GF(2n), the multiplicities and the Jordan
   blocks at once, and would likely prove the collapse; Concreteness 1: Theorem 1 gives the two particles, but no candidate operator
   is in hand.
2. **Digit by digit.** Payoff 2: a recursion in m would prove the collapse; Concreteness 2: Theorem 3 makes every entry of C_s an
   explicit sum over binary digits, and the stability law says consecutive sides agree to degree 2n.
3. **The traces.** Payoff 1: local facts that support but do not prove the collapse; Concreteness 2: the cone's closed walks near its
   apex are plane walks, counted by Lucas' theorem.

**Recommendation.** Continue with #1, keeping #2 as the fallback if no operator appears within the sides already computed.

## Final report as sent

Sent to the owner on 2026-11-09 at 22:35 UTC and copied here verbatim.

The collapse epic is closed and published, but the collapse at every power of two is still unproved. What's new: the walk is two particles on one side of the box, and its quarter turn folds the box into a cone whose spectrum, four times over, is the whole spectrum. At powers of two that cone's spectrum is one return map of the cut line, half a side across. Its Smith form, the first step asked for, is exactly the cone's Jordan data. Up to side 64 the eigenvalues follow a rigid law: each one appears k(k+1)/2 times with Jordan blocks 2k−1, 2k−5, …, the pattern of a symmetric square. A count is odd exactly when Tr(1/λ) = 1. The collapse also holds at side 128.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the collapse at every power of two | **Status:** Inconclusive | Four reductions proved and the Smith form computed; the collapse isn't proved |
| Local direction: the cut-open torus | Continue | The eigenvalue law is rigid and testable, and points at a mechanism |
| Broader exploration: G5 with G1 | Known alternatives | Backlog B22–B43 |
| Long-term goal: G5 Dynamics | No demonstrated advance | Why powers of two are special is narrowed down, not proved |

**Next step:** Continue. I recommend #1 and have asked the coordinator to choose.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | The single particle behind the symmetric square | 3/3 | 1/3 | An operator whose symmetric square has the cone's Jordan data at 4, 8, 16 → a proof, or a reason none exists | Recommended |
| 2 | The return map digit by digit | 2/3 | 2/3 | Write the return map through the dyadic product and find a recursion in m → a proof, or the digit where it fails | Alternative |
| 3 | Prove the parity and trace laws | 1/3 | 2/3 | Count the cone's closed walks near its apex → a proof for j < 2n, or a counterexample | Alternative |

**Corrections:** none. **Goals:** G5 checkpoint (no demonstrated advance). **Assumptions:** none added. The side-128 stress run's second stage (each class's multiplicity and Jordan blocks) is still running, and every class checked so far passes. I'll fold it in when it finishes. Commits 32e9f536d and cfb2fb3a9.
