# The sphere's count has a unary Sherali–Adams refutation of degree 3

Status: Proved by hand. The identity is checked symbolically on K_2, …, K_8 and by brute force on K_2. The solver record is
experimental evidence, not proof.

Ticket `COUNT-NOTE-20261107-001B`, 2026-11-07.

## Standard statement

Let K_k be the octahedral knot sphere (n = 4k² points and 4k² lines) and NAE(K_k) its Kasteleyn-signed not-all-equal formula. Each
line l = {a, b, c} has literals y_p = x_p ⊕ s_{l,p} and clauses (y_a ∨ y_b ∨ y_c) and (¬y_a ∨ ¬y_b ∨ ¬y_c).

**Theorem.** As multilinear polynomials in x,

  Σ_l [y_a y_b y_c + (1 − y_a)(1 − y_b)(1 − y_c)] − Σ_f [J_f + J̄_f] = 1.

- **The terms.** f runs over the n − 4 three-point faces of the plane incidence graph. J_f and J̄_f are the two complementary
  conjunctions of literals on f's three points that make all of f's corners agree.
- **As a refutation.** This is a Sherali–Adams refutation of NAE(K_k):
  - degree 3;
  - 4n − 8 terms, all with coefficient +1 or −1;
  - every positive term is the falsifying conjunction of one of the formula's clauses.

**Corollaries.**
1. **PPADS.** Unary Sherali–Adams of polylogarithmic degree captures PPADS^dt: a polylog-width CNF has a polylog-degree,
   quasipolynomial-size unary Sherali–Adams refutation iff its false-clause search problem is in PPADS^dt (Göös, Hollender, Jain,
   Maystre, Pires, Robere, Tao, *Separations in Proof Complexity and TFNP*, JACM 2024, corollary 4). So "find a violated line of
   K_k" is in PPADS^dt.
   - It is at least as hard as one-sided grid Sperner: `FLAT-STATES-20261107-001B` reduces one-sided Sperner_m to it by depth-2
     decision trees.
   - So the count sits between one-sided 2D Sperner and PPADS.
2. **A separation.** Resolution needs size 2^{Θ(√n)} on the same formulas (`COUNT-NOTE-20261107-001A`). So constant-degree unary
   Sherali–Adams is exponentially stronger than resolution on a natural planar family, as the linear count is for the mutilated
   chessboard.

## Nearest known result

- **The count.** `TWO-ROUND-BRIDGE-20261106-001B` (theorem 4) showed that the level-3 Sherali–Adams relaxation is infeasible, by the
  same corner count. This identity is the dual certificate written out, with its coefficients bounded.
- **The characterization.** PPADS = unary Sherali–Adams, PPAD = unary Nullstellensatz (Göös et al. 2022/2024). The same paper shows
  that resolution is not simulated by unary Sherali–Adams; this is the opposite direction.
- **Classification.** known-with-delta. The Euler count is known from upstream. New here:
  - the unary bound, which places these formulas in PPADS^dt;
  - the solver record.

## Proof

**Corners.**
- The incidence graph (points and lines) is plane, cubic and bipartite.
- A corner of a line l on a face f is the pair of l's two points that are consecutive along f.
- Every line has three corners, and every corner lies on exactly one line and one face.

**Agreement.** For a corner (l; a, b), let A = 1 − y_a − y_b + 2y_a y_b, which is 1 when the two literals agree and 0 otherwise.

**Lines.** For a line, Σ_corners A = 1 + 2N_l, where N_l = y_a y_b y_c + (1 − y_a)(1 − y_b)(1 − y_c). A satisfied line has one
agreeing corner and a violated line three. Both sides are multilinear in three variables and agree on all eight points, so they are
equal as polynomials.

**Faces.**
- **Odd agreement.** Kasteleyn's condition makes the number of agreeing corners of every face odd under every assignment
  (`TWO-ROUND-BRIDGE-20261106-001B`, theorem 2).
- **Corner faces.** A two-point face has two corners, so exactly one agrees: Σ A = 1 identically.
- **Three-point faces.** Here Σ A ∈ {1, 3}, so M_f := (Σ A − 1)/2 is {0, 1}-valued. It equals 1 exactly when all three corners
  agree. The three agreements fix the face's points up to global complement, and three agreeing corners do occur, so exactly two
  complementary assignments qualify. Multilinear representations are unique, so M_f = J_f + J̄_f.

**The count.**
- Sum the corner agreements by lines and by faces: L + 2Σ_l N_l = F + 2Σ_f M_f.
- Euler's formula for the incidence graph gives F = L + 2: it has n + L vertices, 3L edges, and n = L.
- So Σ_l N_l − Σ_f M_f = 1.

**As a refutation.** On an assignment satisfying every clause, each N_l is 0 and each M_f is at least 0. The left side is then at most
0, but it equals 1. ∎

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The certificate on K_2, …, K_8 | line and face identities hold; the sum is the constant 1; coefficients ±1, three literals per term; positive terms are exactly the clauses' falsifiers (1,016 terms at k = 8) |
| 2 | Brute force on K_2 | violated clauses minus monochromatic faces is 1 at all 65,536 assignments |
| 3 | Solver record (read) | below |

## Solver record (experiment)

Instances are K_2, …, K_8, with a limit of 600 s per instance (`solvers/`, `solvers/solver_runs.json`).

| k | n | CaDiCaL (CDCL) | Exact (cutting planes) | CryptoMiniSat with XOR |
| --- | --- | --- | --- | --- |
| 2 | 16 | 36 conflicts | 40 conflicts | 0.01 s |
| 3 | 36 | 354 | 657 | 0.02 s |
| 4 | 64 | 3,530 | 7,893 | 0.13 s |
| 5 | 100 | 51,332 (0.3 s) | 143,408 (2.5 s) | 4.2 s |
| 6 | 144 | 1,182,667 (18 s) | not refuted (29 M conflicts) | 108 s |
| 7 | 196 | not refuted | — | not refuted |

**Reading.** Neither stronger reasoning helps a solver on this count.
- **Cutting planes.** The cutting-planes solver uses the native constraints 1 ≤ y_a + y_b + y_c ≤ 2. It does worse than plain CDCL
  from k = 3 on, and fails at k = 6.
- **XOR reasoning.** The XOR solver works on parity variables of point pairs. It also trails CDCL: 108 s against 18 s at k = 6.
- **What this is evidence of.** The count is a degree principle, not a parity one, and these solvers do not find its counting
  argument.
- **What it is not.** Solvers do not find optimal proofs, so this says nothing about whether short cutting-planes or Res(⊕)
  refutations exist.

## What this does not establish

- **Cutting planes.** Whether polynomial-size cutting-planes refutations exist is open. The LP relaxation is feasible at
  y ≡ 1/2, so rounding is needed. The degree-3 identity does not translate directly into cutting planes.
- **Res(⊕).** No lower or upper bound is proved.
- **PPADS-completeness.** It is not shown that every PPADS^dt problem reduces to the count, nor that one-sided grid Sperner is
  PPADS^dt-hard.
