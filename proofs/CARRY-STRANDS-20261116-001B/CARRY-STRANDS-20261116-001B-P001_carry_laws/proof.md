# What carrying distinctions can and cannot save

Status: Proved (refereed: `CARRY-STRANDS-R1`, confirmed with fixes)

Ticket `CARRY-STRANDS-20261116-001B`, 16 November 2026. Written by Claude in one session; checked by `check.py` beside this file,
which reruns the experiment's gates (exhaustive comparisons on 400 random patterns of 5 to 14 distinctions, ladders, the advisor's
example). The advisor model was consulted before the freeze. Labels: **known**, **known-with-delta**, **local**. No claim about P
versus NP or P versus NC.

## Setting

Atoms, held and forced distinctions, derivation trees, the Strahler number σ and the forcing law are as in
`SEQUENTIAL-WALL-20261116-001B` (proof of that ticket). Within a phase with forced set F, the **w-carry law** carries at most w open
distinctions at once. Its steps: **begin** (carry c for an atom (a, b → c) with a, b ∈ F); **follow a rule** (for an atom (x, b → c)
with b ∈ F and x carried, carry c); **open use taken while carried** (for an atom (x, y → c) with x, y carried, carry c);
**release**. In the **spend-only law** a step that uses carried distinctions removes them (follow replaces x by c; an open use
replaces x and y by c), and a distinction may be derived again while another copy is carried, so states are multisets. In the
**keep law** a step may keep what it uses (follow may keep x; an open use may keep x, y or both), and states are sets. The phase
forces every distinction carried in some reachable state; P_w counts phases. The phase's doubling rounds are ⌈log₂(1 + L_t)⌉,
L_t the largest breadth-first distance, in steps, to the first state carrying a distinction newly forced in that phase; T_w is
their sum. For w = 1 both laws are the forcing law (gate G1).

For a set F, σ_F(v) is the least Strahler number of a derivation tree of v whose leaves lie in F (an atom over two members of F
has number 1).

## Theorem 1 (spend-only: phases are Strahler numbers divided by w)

For every distinction v, the spend-only phase of v is ⌈σ(v)/w⌉.

*Status: known-with-delta (Ershov 1958, Nakata 1967 and Sethi and Ullman 1970: an expression tree is evaluated with r registers
exactly when its Strahler number is at most r), applied phase by phase.*

*Lemma 1 (one phase).* In a phase with forced set F, the spend-only law carries v in some reachable state exactly when
σ_F(v) ≤ w. (⇐) Evaluate a tree of number s ≤ w: a tree of number 1 is a beginning followed by rules; for a node with children of
numbers i ≥ j, evaluate the child of number i (at most i carried), carry its result, then the other child (at most j ≤ i carried
besides, and j < i or i = j = s − 1), then take the open use; at most s are carried at once. (⇒) Each carried distinction of a
spend-only run is produced by one step and spent by at most one, so the steps that lead to v form a derivation tree in which each
node is produced once; evaluating a tree with every node produced once needs at least its Strahler number of registers (the cited
lower bound).

*Lemma 2 (shift).* If every distinction with σ_F ≤ k is added to F, then every σ above k drops by exactly k. Lower bound: in a
least tree over the larger set, replace each new leaf by a tree of number at most k; since combine is monotone and
combine(i + k, j + k) = combine(i, j) + k, the number rises by at most k. Upper bound: cut a least tree over F at its maximal
subtrees of number at most k; every number above k drops by exactly k (by the same identity). ∎

*Proof of Theorem 1.* By Lemma 1 the first phase forces exactly the distinctions with σ ≤ w; by Lemma 2 the remaining numbers drop
by w; induction. ∎ (Gate G3 checks it on 400 random patterns for w = 2, 3.)

## Theorem 2 (spend-only: the rounds never fall below the Strahler number)

For every w, the spend-only law's doubling rounds satisfy T_w ≥ max σ, while the forcing law has T_1 ≤ σ · ⌈log₂(n + 1)⌉.

*Status: local and elementary (a corollary of "Strahler number s implies at least 2^s leaves", Ershov; Flajolet, Raoult and
Vuillemin 1979); it holds only inside this cost model and is not a lower bound on evaluating trees by other means.*

*Proof.* A tree of number s ≥ 1 over F contains at least 2^(s−1) beginnings and 2^(s−1) − 1 open uses (induction: a node of
number s has two descendants of number s − 1 in disjoint subtrees). A spend-only run producing v produces every node of such a
tree once, so it takes at least 2^s − 1 steps, and the phase costs at least s rounds when it forces a distinction with σ_F = s. Let s_t be the largest σ forced in phase t, relative to the
phase's start; adding distinctions of relative number at most s_t lowers any σ by at most s_t (Lemma 2's lower bound), so
max σ ≤ Σ_t s_t ≤ Σ_t rounds = T_w. ∎

So spend-only carrying shortens the count of phases by w (Theorem 1) but cannot lower the doubling rounds below the Strahler
number: equal-rank open uses cannot be saved by spend-only carrying. It can still lower the rounds below the forcing law's actual
cost: on a complete binary tree whose every edge is a chain of ℓ rules, T_1 is about σ · log₂ ℓ, while carrying w distinctions
gives about σ + (σ/w) · log₂ ℓ (advisor's example; measured as Q5).

## Theorem 3 (keeping: what one phase reaches)

In a phase with forced set F, the keep law with w carried distinctions reaches exactly the distinctions that the black pebble game
with sliding, F free and w pebbles, can pebble on the pattern's derivation graph (placing a pebble on c when both demanders of an
atom demanding c are pebbled or forced; sliding a pebble from a demander to c; removing pebbles).

*Status: known-with-delta (the keep law's steps are the moves of that game: begin is a placement over F, follow and open use are
placements or slides, release is removal; Cook 1974; Gilbert, Lengauer and Tarjan 1980 for the game); the advisor pointed out that
a law that copies carried distinctions instead of keeping them differs from the game by up to two pebbles.*

**Consequences proved here.**
- *Ladder (local).* With two carried distinctions the keep law forces the ladder's top in one phase at every length k: carry y₀
  and z₀ (both begin, since x₀ and the helpers are held) and take the open use, getting x₁; then follow the rule to y₁ keeping x₁,
  follow the rule to z₁ spending x₁, take the open use to x₂, and so on. The spend-only law needs
  ⌈(k + 1)/2⌉ phases (Theorem 1, σ = k + 1). Gate G6 checks both.
- *Layered circuits (local).* A layered monotone circuit of width W, as an atom pattern, is forced in one phase with 2W carried
  distinctions at any depth: carry the true gates of one layer, derive each true gate of the next by an OR rule or an AND open use
  while keeping the layer, then release the layer. Measured as Q3b.
- *Pyramids (advisor's derivation, measured as Q4).* With the bottom row held, the second row begins, and a pyramid of height h
  needs about h pebbles in one go (Cook 1974); the advisor derives P_w = ⌈h/w⌉ for both laws, since sweeps by diagonals that begin
  again instead of keeping do as well as keeping.

## What this says about the owner's picture

Read with his words: carrying several open distinctions is holding several strands at once, and keeping one after a use is letting
one strand split into two that later rejoin. Theorem 1 and 2: holding strands without splitting them cannot save the nesting of
open uses; it only trades phases for longer phases. Theorem 3 and its consequences: letting a strand split saves exactly where
strands rejoin (ladders: two strands at any length; layered circuits: two layers of strands at any depth), and costs n^w carried
sets. All of this is the classical register and pebbling picture; the knot words name it, and add no theorem to it.

## Referee (16 November 2026)

`CARRY-STRANDS-R1` confirmed Theorems 1 to 3 with fresh code: Theorem 2's step count and telescoping, and the keep law matching
black pebbling with sliding move for move. Read the text above with one relabelling: the ladder and layered-circuit constructions are
standard pebbling arguments (two pebbles slide up a ladder; layer-by-layer pebbling uses twice the width), so "local" is generous;
read them as known in kind. The advisor's "up to two" for a copying law: the referee found at most one on the patterns tried.
