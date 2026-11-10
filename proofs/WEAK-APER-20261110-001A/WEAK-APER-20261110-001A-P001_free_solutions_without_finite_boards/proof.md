# Free solutions without finite boards

Status: Proved

Ticket `WEAK-APER-20261110-001A`, 2026-11-10. Pre-registered in commit 15131fc29 before the proof attempt and before ticket B's census
ran.

## Setting

- **The law.** A value law on the Cayley tree T of F2 = ⟨x, y⟩ is a set P₀ of allowed patterns over a finite alphabet A: a value and
  the values of its x-, X-, y- and Y-neighbours (X = x⁻¹, Y = y⁻¹). X is the set of its solutions, and P is the set of patterns
  that occur in solutions (the census's tree patterns). Every law with finite windows takes this form after a higher-block recoding.
- **The action.** F2 acts by (k·s)(g) = s(k⁻¹g), and Stab(s) is the stabilizer. A solution is **free** when Stab(s) = 1. Under
  Leibniz's rule its board is then the tree (`LEIBNIZ-BOARDS-20261110-001A`, T1).
- **Recoding to edges.** Give each place its pattern as its value. Then p may be followed by q along the letter g exactly when
  q₀ = p_g and q_{g⁻¹} = p₀ (the census's `compat`). Every constraint is now on a single edge. The recoding commutes with the action,
  so it keeps stabilizers. Sections 2 to 5 use the recoded shift.
- **Half-trees and rigidity.**
  - For a directed edge e = (a → b), H(e) is the component of T minus the edge that contains b.
  - Given s, a **completion** of H(e) is a configuration on H(e) that, with s outside, is again a solution.
  - The only constraint joining H(e) to the rest is the edge e. So the completions depend only on the **state** of e: the value s(a)
    and the letter of e.
  - e is **non-rigid** in s when H(e) has at least two completions.
- **Ends.** The ends of T are the equivalence classes of rays. ∂T, the set of ends, is a Cantor set on which F2 acts. Each k ≠ 1
  translates along an axis and fixes exactly its two ends, so only countably many ends are fixed by a nontrivial element.

## Target 1. Balance: when a finite board exists

**Statement.** X has a solution with finite orbit (a finite board) iff the balance equations over P have a nonzero nonnegative
solution n. For each letter g ∈ {x, y} and pair of values (a, b), the equation is
Σ_{p : (p₀, p_g) = (a, b)} n_p = Σ_{p : (p_{g⁻¹}, p₀) = (a, b)} n_p.

**Proof.**
- **From a board.** A finite board with a solution gives n by counting the places with each pattern. Each g-edge from a place with
  (centre, g-value) = (a, b) ends at a place with (g⁻¹-value, centre) = (a, b), and the g-edges form a permutation, so the two
  counts agree.
- **To a board.** Scale a rational solution to integers.
  - Take n_p places labelled p. For each letter and each pair (a, b), choose any bijection from the places whose label leaves with
    (a, b) to those whose label arrives with (a, b). The bijections together make a permutation for each letter.
  - Colour each place by its label's centre. Following g from a place labelled p reaches a place whose centre is p_g, and so does
    following g⁻¹ (with p_{g⁻¹}). So each place's pattern is its label, as in Theorem 7, part 2, of `BOARD-DIST-20261110-001A`.
  - The colouring is therefore a solution on a finite board (any connected component). ∎

The equations have integer coefficients, so a real solution gives a rational one.

**Known.** This is the periodic-point criterion for tree shifts: Piantadosi (2008, Theorem 3.6) gives it, and in this
pattern-as-tile form it is the condition of Chazottes, Gambaudo and Gautero, which Hellouin de Menibus and Maturana Cornejo prove
equivalent to Piantadosi's with the same bijection construction (arXiv 1904.03907, Theorems 3.5 and 3.11).

**Certificate of no finite board.** By Farkas' lemma the program is infeasible iff there is a **potential**: numbers y_g(a, b) such
that every pattern p ∈ P gains at least 1, where gain(p) = Σ_g [y_g(p₀, p_g) − y_g(p_{g⁻¹}, p₀)]. Summed over a finite board the
gains cancel edge by edge, so they cannot all be positive. For the horofunction law, y_g(a, a + 1) = 1 and y_g(a, a − 1) = −1 give
every place the gain (number of higher neighbours) − (number of lower ones) = 3 − 1 = 2.

## Target 2. Lemma A″

**Statement.** If some solution s has infinitely many non-rigid edges e₁, e₂, … whose half-trees are pairwise disjoint, then X
has a free solution.

**Proof.**
1. **Independent choices.**
   - For each i let A_i = s|H(e_i), and let B_i be another completion.
   - If a tail a_i lay in H(e_j), the edge e_i would join H(e_j) to the rest, so it would be e_j reversed. Then H(e_i) and H(e_j)
     would split T between them, and no third half-tree could be disjoint from both. So no tail a_i lies in any H(e_j), and no
     edge joins two of the H(e_j).
   - The only constraint joining H(e_i) to the rest is e_i, and its tail keeps its value. So for c ∈ {0, 1}^ℕ the configuration s_c,
     with B_i on H(e_i) wherever c_i = 1, is a solution.
   - c ↦ s_c is continuous and injective.
2. **Each nontrivial element is avoided.** Fix k ≠ 1.
   - A half-tree that contains no end of k's axis is disjoint from the axis, so k moves it off itself. The H(e_i) are disjoint, so at
     most two of them contain an end of the axis.
   - Given c₁, …, c_m, take i > m with k⁻¹H(e_i) ∩ H(e_i) = ∅ and fix every other coordinate.
   - (k·s_c)|H(e_i) = s_c(k⁻¹·)|H(e_i) does not depend on c_i, while A_i ≠ B_i. So one value of c_i gives k·s_c ≠ s_c.
3. **Baire.** {c : k·s_c = s_c} is therefore closed and nowhere dense. By the Baire category theorem some c lies outside all of
   these countably many sets, and s_c is free. ∎

## Target 3. L1, a doubly recurrent branching type

**Statement.** Call a pattern p ∈ P with a parent direction d a **type**; its children are the compatible types in the other three
directions. Suppose some type τ = (p, d) can reach a branching choice (a type with two compatible children in one direction), and
has two different child directions h₁ ≠ h₂ each with a child type in τ's strongly connected component. Then X has a free solution.

**Proof.**
1. **Two recurrences at once.** The children of a place are chosen independently, each compatible only with p. So below an
   occurrence of τ a configuration can return to τ inside both the h₁-branch and the h₂-branch. Every other direction is completed
   greedily, since every pattern in P has a compatible pattern in every direction.
2. **Infinitely many disjoint copies.** Repeating this inside every copy gives a binary tree of occurrences of τ. Along its
   h₁-path, the h₂-occurrences have pairwise disjoint half-trees (a comb).
3. **Each copy is non-rigid.** τ reaches a branching choice, so the half-tree below each copy has two completions. Lemma A″
   applies. ∎

## Target 4. L2, an orientation toward a generic end

**Statement.** If a level law on Z/3 allows (1, 0, 3) (one neighbour one level lower, none level, three one higher), then for every
end ξ the Busemann function b_ξ mod 3 is a solution, and it is free when no nontrivial element fixes ξ. The reflection v ↦ −v of
values carries a place's triple (a, b, c) to (c, b, a). So the same holds with −b_ξ for a law that allows (3, 0, 1).

**Proof.**
- **A solution.** b_ξ falls by 1 toward ξ and rises by 1 along each of the other three edges, which is the triple (1, 0, 3).
- **Its stabilizer.** Each place's neighbour one level lower is its next step toward ξ. A stabilizing element keeps these
  pointers, so it maps rays toward ξ to rays toward ξ and fixes ξ (as in T2 of `LEIBNIZ-BOARDS-20261110-001A`).
- **Free.** Only countably many ends are fixed by a nontrivial element, so for the others Stab(b_ξ mod 3) = 1. ∎

## Target 5. Theorem W: every infinite shift of finite type on F2 has a free solution

**Statement.** If X is infinite, some solution has trivial stabilizer.

**Proof.**
1. **A non-isolated solution.** X is compact and infinite, so some solution s is not isolated.
2. **Isolated means rigid far away.** Fix a base place o. s is isolated iff, for some r, every edge leaving the ball of radius r
   around o, directed away from o, is rigid in s.
   - If s is isolated, an alternative completion beyond such an edge would give a second solution agreeing with s on the ball.
   - If those edges are rigid, a solution agreeing with s on the ball gives each of them the same state. So it agrees with s
     beyond them too.
3. **Non-rigid ends.** Let N(s) be the set of edges directed away from o that are non-rigid in s.
   - N(s) is closed toward o. If e lies in H(e′), a second completion of H(e), extended by s on the rest of H(e′), is a second
     completion of H(e′).
   - For the non-isolated s, N(s) meets every sphere around o, so by König's lemma it contains a ray.
   - Let E(s) be the set of ends whose ray from o lies in N(s). Then E(s) ≠ ∅ for every non-isolated s.
   - E(s) does not depend on o. ζ ∈ E(s) iff every edge directed toward ζ is non-rigid, since such an edge has a final segment of
     o's ray to ζ inside its half-tree. Hence E(k·s) = k·E(s).
4. **Case I.** Some solution has infinitely many non-rigid edges with pairwise disjoint half-trees. Lemma A″ gives a free solution.
5. **Case II: no solution does.** Then E(s) is finite for every s. Otherwise infinitely many ends of E(s) accumulate at some end ζ,
   so rays from o toward ends of E(s) leave o's ray to ζ at depths going to infinity. The first edge of each such branch lies in
   N(s), and branches leaving at distinct depths have pairwise disjoint half-trees.
6. **The non-rigid ends fill the boundary.** Let Ends(X) = ∪_s E(s).
   - It is nonempty and F2-invariant.
   - It is closed. Let ζ_n ∈ E(s_n) with ζ_n → ζ, and pass to a subsequence with s_n → s. Each edge on the ray from o to ζ lies on
     the ray to ζ_n for large n, where it is non-rigid in s_n. Non-rigidity is a property of the edge's state, which s_n and s share
     for large n. So ζ ∈ E(s).
   - The action of F2 on ∂T is minimal: every orbit is dense. So Ends(X) = ∂T.
7. **A free solution.** ∂T is uncountable, and only countably many ends are fixed by a nontrivial element. Pick ζ fixed by none, and
   s with ζ ∈ E(s).
   - Stab(s) permutes the finite set E(s), so the elements of Stab(s) fixing ζ form a subgroup K of finite index.
   - Then K = 1, so Stab(s) is finite, and F2 is torsion-free, so Stab(s) = 1. ∎

**Corollaries.**
- **W.** Under Leibniz's rule the tree is a board exactly when the law has infinitely many solutions; a law with finitely many has
  only finite boards. So no law forces the plane (P).
- **Both kinds of board.** Every nonempty shift of finite type on F2 also has a solution with nontrivial stabilizer (Piantadosi
  2008). So a law with infinitely many solutions has the tree and at least one board other than the tree, and no law forces one
  infinite board: a board other than the tree comes with the tree, and the tree comes with another board.
- **Uncountable.** An infinite shift of finite type on F2 is uncountable. In Case I, c ↦ s_c is injective. In Case II, countably
  many solutions would give only countably many non-rigid ends, short of ∂T.
- **Free groups of higher rank.** The proof uses only the tree's branching, the free action, torsion-freeness, the two ends fixed
  by each nontrivial element and the minimal boundary action. So it holds verbatim for F_n with n ≥ 2.

## Target 6 (found after the census, not pre-registered). No finite board means a drift

**Level laws.** A level law on Z/q allows a place of value k according to how many of its four neighbours have each value k + d,
d ∈ Z/q. The census's laws are the case q = 3, where (a, b, c) counts the neighbours with d = −1, 0 and 1. Such a law is unchanged by
adding a constant to every value and by any permutation of the four neighbour slots, and the proof uses only these invariances.

**Statement.** A level law on Z/3 that has solutions has no finite board iff every pattern its solutions use has more neighbours one
level up than one level down, or every one has more down than up. On Z/q the condition reads: some weighting ψ of the level steps
with ψ(−d) = −ψ(d) gives every used pattern a positive total Σ_h ψ(p_h − p₀) over its four neighbours.

**Proof.**
- **If.** The potential y_g(a, a + 1) = 1, y_g(a, a − 1) = −1 (and 0 on level edges) gives each pattern the gain c − a, the number
  of neighbours one level up minus the number one level down. Target 1's certificate applies.
- **Only if.** Suppose a potential exists (target 1).
  - The law and its patterns are unchanged by adding a constant to every value and by the automorphisms x ↔ y and x ↦ x⁻¹ of F2,
    which permute the neighbour slots.
  - Each of these acts on potentials and keeps gains; x ↦ x⁻¹ sends y_x(a, b) to −y_x(b, a). So the average over this finite group
    is again a potential.
  - An invariant potential has y_g(a, b) = ψ(b − a) with ψ antisymmetric, so gain(p) = Σ_h ψ(p_h − p₀) over the four neighbours.
  - On Z/3, ψ(1) = −ψ(2) = t, so gain(p) = t(c − a). It is positive on every used pattern only if c − a has one sign on all of
    them. ∎

**Reading.** On a finite board every step up along an edge is a step down from its other end, so the steps cancel. A law that makes
every place climb, on balance, can only live where there is room to climb forever. In this family that drift is the only
obstruction to a finite board: 48 laws drift up and 48 down. Each has infinitely many solutions, since finitely many would all have
finite orbits, and so free solutions by Theorem W.

## Checks

`check.py` (result in `result.json`):
- **Mirror invariance.** The census's classes (E, D, A, P, WA) and its L1 certificates are invariant under the reflection
  (a, b, c) ↦ (c, b, a), on all 32,768 laws. The census did not use the symmetry.
- **The undecided laws.** All 10 contain (3, 0, 1), and each one's mirror is certified by L2 (classed WA-L2 or P-L2). On the ball of
  radius 10, −b_ξ mod 3 has the triple (3, 0, 1) at every place. For ξ = x^∞ the elements of length at most 6 that fix this colouring
  are x^{±3} and x^{±6}; for a random end, none.
- **Exact verdicts.** Every balance verdict of the census is re-decided in rational arithmetic, on tree patterns pruned by
  independent code:
  - each weakly aperiodic law (WA) by a potential (a Farkas certificate);
  - each law of class A by an explicit finite board, built as in target 1 and checked place by place, that uses a branching pattern;
  - each law of class P by an explicit finite board and a potential that forbids branching patterns on every finite board.
- **Small boards.** No law classed E or WA has a solution on a board of at most 4 places.
- **Drift.** The 96 laws of class WA are exactly the 48 whose tree patterns all drift up and the 48 whose tree patterns all drift
  down; no law of class A or P drifts.

All checks pass (88 s). The largest board built has 2,292 places; every potential has denominator at most 2.

## Scope and sources

- **Scope.** Shifts of finite type on F_n, n ≥ 2, over a finite alphabet.
- **Sources.**
  - The Baire category theorem; König's lemma; the minimal boundary action of a free group; Farkas' lemma.
  - Piantadosi (2008, and his thesis): every nonempty SFT on a free group has a weakly periodic point, and some have no strongly
    periodic point.
  - Cohen (2017): a group with two or more ends has no strongly aperiodic SFT.
  - Bitar (2024, arXiv 2406.04132): stabilizers realized by SFTs; for nearest-neighbour SFTs on Z, the trivial stabilizer occurs
    iff infinitely many stabilizers do (Lemma 5.8).
  - Target 1: Piantadosi (2008, Theorem 3.6); Chazottes, Gambaudo and Gautero; Hellouin de Menibus and Maturana Cornejo (arXiv
    1904.03907, Theorems 3.5 and 3.11).
- **Novelty.** Theorem W was not found stated (bounded searches, 2026-11-10, including Piantadosi's thesis and the papers of Cohen
  and Bitar, and the referee's own searches). The argument is short and uses standard tools, so folklore risk is moderate. Target 1
  is known; targets 2 to 4 and 6 are elementary.
- **Review.** An independent referee read this proof before publication, found no error in any target, and asked for the changes
  made here: target 6's statement restricted to laws with solutions, the corollary on forcing one infinite board tied to
  Piantadosi, target 1 credited, and several steps written out.
