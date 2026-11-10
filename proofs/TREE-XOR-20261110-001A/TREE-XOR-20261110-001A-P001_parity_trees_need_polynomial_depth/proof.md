# Parity decision trees on the count need polynomial depth

Status: Proved by hand from Beame et al.'s degree bound and the program's reductions; Lemma 1 is checked on K_2 and the chain's sizes
are tabulated in `check.py`. The encoding step (Lemma 3) is argued at the level of the standard substitution argument.

Ticket `TREE-XOR-20261110-001A`, 2026-11-10.

## Standard statement

- **Parity decision trees and tree-like Res(⊕).** A parity decision tree (PDT) queries F2-linear forms of the variables. It solves the
  false-clause search of a CNF F when each leaf names a clause falsified by every assignment reaching it. Tree-like Res(⊕) refutations of F
  are, up to small factors, the same objects (Itsykson and Sokolov), with the tree's depth the refutation's height.
- **F2 Nullstellensatz.** A refutation of degree D is Σ_C P_C J_C + Σ_p q_p (x_p² − x_p) = 1 over F2, where J_C is the conjunction of
  literals that falsifies clause C and every P_C J_C, q_p x_p² has degree at most D.
- **The count.** NAE(K_k), n = 4k² points, clauses of width 3 (`COUNT-NOTE-20261107-001`).

**Theorem.** Every parity decision tree solving the false-clause search of NAE(K_k), and hence every tree-like Res(⊕) refutation, has
depth at least c n^{1/8} / log n.

## Nearest known result

- **The degree bound.** Beame, Cook, Edmonds, Impagliazzo and Pitassi (*JCSS* 57, 1998), §3.3 and Theorem 12: the sink-counting system
  SN, the polynomial form of "a 1-digraph with a source has a sink", needs GF(2) Nullstellensatz degree Ω(√N) on N nodes. This is the
  degree bound behind PPADS ⊄ PPA.
- **Classification.** Known-with-delta. That low-depth parity decision trees give low-degree F2 refutations, and that the count is
  outside PPA^dt (`COUNT-TFNP-20261107-001B`), are known. The delta is the polynomial bound for this formula, through explicit sizes.

## Lemma 1 (a parity tree is a low-degree F2 refutation)

If a PDT of depth d solves F's false-clause search, F has an F2 Nullstellensatz refutation of degree at most d + w, w the clause width.

*Proof.* A leaf λ reached by the answers ℓ_1 = b_1, …, ℓ_j = b_j (j ≤ d) is the affine subspace V_λ, whose indicator is
1_λ = Π_i (1 + ℓ_i + b_i), of degree at most d. Every assignment reaches exactly one leaf, so Σ_λ 1_λ = 1 at every point. At a leaf
naming clause C, every point of V_λ falsifies C, so 1_λ = 1_λ J_C at every point. Hence Σ_C (Σ_{λ names C} 1_λ) J_C = 1 at every point of
{0, 1}^n. Two polynomials over F2 that agree on {0, 1}^n differ by a combination of the x_p² − x_p of no greater degree, which gives a
refutation of degree at most d + w. ∎

Check 1 builds complete parity decision trees for K_2 (16 points, 32 clauses) under four query strategies (single variables in order,
line by line, corner parities first, random parities; 1,300 to 24,749 leaves, depth 16). For each it confirms that every leaf's clause
is falsified on its leaf and that Σ_λ 1_λ J_C = 1 under all 65,536 assignments.

## Lemma 2 (decision-tree reductions keep low degree)

If the false-clause search of F_R reduces to that of F_S by decision trees of depth t, a degree-D F2 refutation of F_S gives one of F_R
of degree O(t(D + w)).

*Proof.* The standard substitution (Göös et al., *Separations in Proof Complexity and TFNP*, 2022): each variable of F_S becomes the
polynomial of its decision tree, of degree at most t, and each substituted J_C is a sum of path indicators, each falsifying a clause of
F_R that the decoding tree names, so it is a combination of F_R's falsifiers of degree O(t w). ∎

## Lemma 3 (from the unary sink to the binary one)

SINK on N nodes, with successor and predecessor pointers in binary, needs F2 Nullstellensatz degree at least deg(SN_N) − O(log N).

*Argument.* Substitute each pointer bit by the F2-linear form that sums the edge variables x_ij over the targets (or sources) whose
binary expansion has that bit. A degree-D refutation of the binary formula becomes a combination of degree D in the x_ij. Each
substituted falsifier, the indicator that O(1) pointers spell a forbidden configuration, has degree O(log N). Modulo SN's row axioms
(Σ_j x_ij = 1 and x_ij x_ik = 0) it equals the product of the O(1) edge variables the configuration names, since a polynomial on one row
that vanishes on the row's unit vectors lies in the ideal at no greater degree. That product is annihilated by SN's axioms in constant
degree. So SN has a refutation of degree D + O(log N). ∎

## Proof of the theorem

- **The chain.** By `COUNT-SYSTEMS-20261110-001A`, SINK on N + 1 nodes reduces to the count's search on K_k by decision trees of depth
  t = O(log N), with k = 2m + 4 and m the grid side of `COUNT-TFNP-20261107-001A`. Check 2 tabulates n = 4k² ≤ 22,000 N⁴ for N ≥ 2, the
  ratio falling to about 2,600 at N = 32.
- **The degree.** By Beame et al., SN_N needs degree Ω(√N); by Lemma 3 the binary SINK needs Ω(√N) − O(log N); by Lemma 2 the count
  needs F2 degree Ω(√N / log N) = Ω(n^{1/8} / log n).
- **The depth.** By Lemma 1 a PDT of depth d gives degree d + 3, so d = Ω(n^{1/8} / log n). ∎

## Remarks

- **Height, not size.** The theorem bounds the height of tree-like Res(⊕) refutations, not their size. A tree of polynomial depth can
  still have few leaves, and turning depth into size needs a Delayer that earns a free choice at many parity queries (Itsykson and
  Sokolov's game) or a lifted structure (Beame–Koroth; Chattopadhyay, Mande, Sanyal and Sherif), neither of which this formula has
  ready.
- **Why parities do not find the vortex fast.** A parity tree of depth d is an F2 refutation of degree d + 3, and the count's F2 degree is
  polynomial because its contradiction is a count of parities that all hold (`COUNT-SYSTEMS-20261110-001B`).
- **The upper side.** A trivial tree queries every point: depth n. Ordinary decision trees solve 2D Sperner in O(√N) queries
  (Friedl–Ivanyos–Santha–Verhoeven), which suggests O(√n) here; it is not claimed.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Lemma 1 on K_2: complete parity decision trees under four strategies, every leaf's clause falsified on it, Σ 1_λ J_C = 1 everywhere | pass |
| 2 | The chain's sizes: n = 4k² ≤ 22,000 N⁴, the ratio decreasing in N | pass |

## Nonclaims

- **No size lower bound for tree-like Res(⊕)** is claimed, and nothing for dag-like Res(⊕).
- **Beame et al.'s degree bound and the substitution lemmas are cited and argued, not formalized.**
