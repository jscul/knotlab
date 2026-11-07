# The sphere's count needs resolution size 2^Θ(√n)

Status: Proved by hand from `SPHERE-SIZE-20261107-001A` and a random restriction. The constants inherit `SPHERE-WIDTH-20261107-001A`'s
sketched lemmas. The packing's properties are checked by computation. The grid-Sperner corollary is by sketch.

Ticket `SPHERE-SIZE-20261107-001B`, 2026-11-07.

## Standard statement

**Theorem.** There is an absolute constant c > 0 such that every resolution refutation of the not-all-equal formula of the octahedral
knot sphere K_k (n = 4k² points) has size at least 2^{c·k} = 2^{Ω(√n)}. Size n^{O(1)}·2^{O(√n)} suffices
(`TWO-ROUND-BRIDGE-20261106-001B`), so the resolution size is 2^{Θ(√n)} up to polynomial factors.

**Corollary (sketch).**
- **Grid Sperner.** Islands are also allowed to touch the boundary away from its three doors. With that, the same argument gives size
  2^{Θ(m)} for grid Sperner (`SPHERE-WIDTH-20261107-001B`).
- **Itsykson et al.'s CSP.** Their 2D Sperner CSP restricts to this instance, so it too needs size 2^{Ω(n)} in general resolution. Only
  tree-like size was known.

## Nearest known result

- **Sizes for grid principles.** Mutilated chessboard and grid Tseitin need resolution size 2^{Ω(n)} on n×n grids (Dantchev–Riis 2001;
  Alekhnovich 2004).
- **2D Sperner.** Tree-like size 2^{Θ(n)} (Itsykson–Malova–Oparin–Sokolov 2014). A general-resolution size bound was not found.
- **Sherali–Adams.** It refutes the knot sphere at level 3 (`TWO-ROUND-BRIDGE-20261106-001B`). So the sphere's count separates
  Sherali–Adams from resolution, as the mutilated chessboard does.
- **Classification.** new as far as found for these formulas. It is a known paradigm (local randomization) applied to a height
  principle with a vortex; its new ingredient is the island lemma.

## Proof

**The random restriction.** Fix s = 1, separation 17, and M = |B(2s + 17)| (at most 3·19² + 3·19 + 1 = 1141 points).
- **Proposals.** Every point farther than s + 3 from the corners proposes itself as an island centre independently, with probability
  ε = 1/M.
- **The hard-core rule.** Keep a proposal when no other proposal lies within distance 2s + 17. Kept islands, the balls of radius s
  around kept centres, are then pairwise at least 17 apart.
- **Labels.** Each island gets an independent uniform label, read in a frame over the island. ρ fixes the island points' colours.

**Properties** (check 1).
- (P1) **Coverage.** A point p farther than 2s + 3 from the corners is fixed with probability at least Σ_c ε(1 − ε)^{|B(c, 2s+17)| − 1},
  summed over the centres c within s of p. Equality holds when every point near c may propose; otherwise there are fewer competitors. At most one kept centre covers p, so these events are disjoint. This is at least
  |B(s)|·ε·(1 − ε)^M ≥ 7/(eM) =: p₀.
- (P2) **Fair colours.** Given that p is fixed, its colour is uniform (half of the six labels give each colour). So each literal on p is
  satisfied with probability at least q = p₀/2.
- (P3) **Locality.** Whether p is fixed, and its colour, depends only on proposals within distance 3s + 17 = 20 of p and one label.
  Events for points more than 40 apart are independent.
- (P4) **Corners.** At most N_c = O(1) points (near the six corners) are never fixed.

**Surviving clauses are narrow.**
- **Spread literals.** Let C be a clause with W literals. Discard the at most N_c literals near the corners. Greedily choose literals
  on points pairwise more than 40 apart; there are at least (W − N_c)/V of them, where V = |B(40)| = 4921.
- **Survival probability.** By (P2) and (P3), each of these satisfies C independently with probability at least q. So
  P(C|ρ ≠ 1) ≤ (1 − q)^{(W − N_c)/V}.

**Conclusion.** Let Π be a refutation of size S. Let W₀ = c(1)·k − 1, the width that `SPHERE-SIZE-20261107-001A` requires of every
restricted formula; its hypotheses hold: separation 17 and corners avoided.
- **Many wide clauses would die.** Suppose S·(1 − q)^{(W₀ − N_c)/V} < 1. Then some ρ satisfies every clause of Π with W₀ or more
  literals.
- **A narrow refutation would remain.** Π|ρ is then a refutation of NAE(K_k)|ρ of width < W₀, a contradiction.
- **So** S ≥ (1 − q)^{−(c(1)k − 1 − N_c)/V} = 2^{α(c(1)k − 1 − N_c)}, with α = −log₂(1 − q)/V > 0. ∎

The constants are poor: check 2 gives α ≈ 3.3·10⁻⁷ bits per literal. They are absolute.

## The grid-Sperner corollary (sketch)

- **Same argument.** Use colour islands (uniform in {0, 1, 2}) on the side-m Sperner grid, with `SPHERE-WIDTH-20261107-001B`'s boundary
  lemma.
- **The boundary strip.** Islands must also be allowed to touch the fixed boundary, away from its three doors. Otherwise a strip of
  points along the boundary would never be fixed, and clauses inside it would survive.
- **Why boundary islands are harmless.** An island touching a side of constant colour b, of any colour c, never forms a negative cycle
  with fixed points alone. Entering it from the boundary and leaving it again contributes ⌊(1 + b − c)/3⌋ + ⌊(1 + c − b)/3⌋ = 0, and
  boundary arcs cost 0.
- **Not checked.** The details (doors, and corner islands touching two sides) are only sketched and were not checked by computation.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Hard-core packing on K_16 and K_20 | islands always at least the separation apart; coverage at least the formula (Monte Carlo 0.016–0.029 against bounds 0.012–0.021) |
| 2 | Constants at s = 1, separation 17 | coverage ≥ 7/(eM); literal probability q = p₀/2; independence distance 40; size exponent α > 0 |

## What this does not establish

- **Constants.** Optimal constants, and any fine-grained exponent: α is tiny.
- **Decorations.** The decorated three-fold spaces are not covered. Whether their decorations can be restricted away was not checked.
- **Other systems.** Nothing here concerns cutting planes, Res(⊕) or bounded-depth Frege. The count is easy for Sherali–Adams.
