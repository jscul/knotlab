# Tree-like Res(⊕) size is bounded by F2 polynomial-calculus degree

Status: Proved by hand. `check.py` is a sanity check on small random formulas, where the bound holds with room to spare.

Ticket `TREE-XOR-20261110-001B`, 2026-11-10.

## Standard statement

- **Polynomial calculus over F2.** Lines are multilinear polynomials over F2 (x² = x built in). From the axioms (the falsifiers J_C of
  F's clauses, and any linear axioms ℓ + b) one may add two lines and multiply a line by a variable. A refutation derives 1; its degree is
  the largest degree of a line.
- **Parity decision trees** as in `TREE-XOR-20261110-001A`; the size of a tree is its number of leaves.

**Theorem.** If a parity decision tree with s leaves solves the false-clause search of a CNF F of width w, then F has an F2
polynomial-calculus refutation of degree at most log₂ s + w. So every tree-like Res(⊕) refutation of F has size at least
2^{deg_PC(F) − w}, where deg_PC(F) is F's least F2 polynomial-calculus degree.

**Corollary (the count).** Tree-like Res(⊕) refutations of the sphere's NAE formula have size at least 2^{deg_PC − 3}. A size lower bound
for tree-like Res(⊕) on the count follows from an F2 polynomial-calculus degree lower bound, backlog B84; the depth bound of
`TREE-XOR-20261110-001A` comes from the Nullstellensatz, which the polynomial calculus can beat.

## Nearest known result

- **Size against width and degree.** Ben-Sasson and Wigderson's tree-like size–width relation for resolution (*JACM*, 2001), and
  Impagliazzo, Pudlák and Sgall's for the polynomial calculus (*Computational Complexity*, 1999). The proof here is theirs, with linear
  queries in place of variables.
- **Classification.** Known-with-delta, folklore risk high: it is the expected transfer of those arguments to parity decision trees. Its use
  here is to name the one degree that decides the size question on the count.

## Proof

Prove, by induction on s, the claim for F together with any set A of linear axioms: if a parity decision tree with s leaves solves the
false-clause search of F on the affine subspace A defines, then F ∪ A has a refutation of degree at most log₂ s + w.

**A leaf (s = 1).** Its clause C is falsified on all of A's subspace, so A implies x_p = b_p for C's at most w variables. Each x_p + b_p is
a linear combination of A's axioms, derived in degree 1. Modulo them J_C equals 1, and the reduction multiplies them by monomials of
degree below w, so 1 is derived in degree at most w.

**A query.** Let the root query ℓ, with subtrees of s₀ (answer ℓ = 0) and s₁ (ℓ = 1) leaves, and say s₀ ≤ s/2 (the other case is
symmetric). By induction, F ∪ A ∪ {ℓ} has a refutation of degree at most log₂ s₀ + w ≤ log₂ s − 1 + w, and F ∪ A ∪ {ℓ + 1} one of degree at
most log₂ s₁ + w ≤ log₂ s + w.
- Multiply every line of the first refutation by 1 + ℓ. Axioms of F ∪ A times 1 + ℓ are derived from those axioms in one more degree;
  the axiom ℓ becomes ℓ(1 + ℓ) = ℓ + ℓ², which is 0 in the multilinear setting; sums and multiplications by variables commute with the
  factor. So F ∪ A derives 1 + ℓ in degree at most log₂ s + w.
- With 1 + ℓ derived, the second refutation runs from F ∪ A, in degree at most log₂ s + w. ∎

For the corollary, a tree-like Res(⊕) refutation of size s is a parity decision tree with at most s leaves (Itsykson and Sokolov).

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Sanity: 12 random unsatisfiable 3-CNFs on 8 variables, two trees each; the exact F2 polynomial-calculus degree (3 for all) is at most log₂ s + 3 | pass, with room: the bound is 7.6 to 10.8 |

## Nonclaims

- **No F2 polynomial-calculus degree bound for the count** is claimed; that is B84.
- **Dag-like Res(⊕)** is not covered.
