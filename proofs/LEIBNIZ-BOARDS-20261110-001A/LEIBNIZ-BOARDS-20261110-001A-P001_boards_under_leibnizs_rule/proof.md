# Boards under Leibniz's rule

Status: Proved (T1 to T4, and T5 and T6 for the laws named; the general W is reduced, not proved)

Ticket `LEIBNIZ-BOARDS-20261110-001A`, 2026-11-10. Pre-registered in commit 3592c5641 before the proof attempt and before ticket B's
census ran.

## Setting

- **Names and boards.** As in `BOARD-DIST-20261110-001A`: names are the words of F2 = ⟨x, y⟩, and e(u, v) says names u and v are
  one place (transitivity, letter closure, constancy).
- **Laws.** A value law is finitely many finitary clause templates over a finite alphabet Q that read values only. After a
  higher-block recoding it is a nearest-neighbour law, which we assume.
- **The solutions.** X is the law's set of solutions on the tree of names, a tree shift. F2 acts on it by (k·s)(g) = s(k⁻¹g), and
  Stab(s) = {k : k·s = s}.
- **Leibniz's rule.** Names u and v are one place exactly when s(ug) = s(vg) for every word g.
- **Patterns, completions and branching.**
  - A directed edge (a → b) has a **half-tree** beyond b, away from a.
  - A **completion** of it is any configuration there that, with the rest of a solution, is again a solution.
  - A pattern p is **branching** in direction h when two different patterns in the half-tree set H[h] are compatible with p.

## T1. The boards

**Statement.** Under Leibniz's rule the allowed states are exactly (s, ~s) with s ∈ X, where u ~s v ⇔ s(ug) = s(vg) for all g. The
board of s is Sch(Stab(s)).

**Proof.**
- The rule fixes the board as ~s, which is a right congruence with s constant on its classes. The law reads values only.
- The class of 1 is {k : s(kg) = s(g) ∀g} = Stab(s), and u ~s v ⇔ uv⁻¹ ∈ Stab(s), by substituting g = vg′. ∎

## T2. The strong form S is false

**Statement.** Take the horofunction law on Q = Z/3: a place of value k has exactly one neighbour of value k − 1 and three of value
k + 1. Its solutions are exactly s = b_ξ + c mod 3, for an end ξ of the tree and its Busemann function b_ξ. For ξ = x^∞ the
stabilizer is ⟨x³⟩, so Sch(⟨x³⟩), a 3-cycle with trees attached, is an infinite board other than the tree.

**Proof.**
1. **The orientation.** In a solution each vertex has exactly one neighbour of value k − 1, its parent. Every edge {u, v} has
   s(v) = s(u) ± 1, so it is oriented child → parent in exactly one way.
2. **The end.** An orientation of a tree with out-degree 1 everywhere points every edge toward one end ξ, and s − b_ξ is then
   constant. Conversely every b_ξ + c is a solution.
3. **The stabilizer for ξ = x^∞.** k·s = s needs k·ξ = ξ, so k ∈ ⟨x⟩. Then b_ξ(x^m g) = b_ξ(g) − m, so k = x^m stabilizes s exactly
   when 3 | m. ∎

`check.py` confirms the law on the ball of radius 9, the invariance under x³, and that every other element of length at most 6
moves s.

## T3. Lemma A: periodic branching gives the tree and an infinite cyclic board

**Statement.** Suppose s0 ∈ X has finite orbit and uses a branching pattern. Then X has a solution with trivial stabilizer, and a
solution whose stabilizer is infinite cyclic. So the tree and the Schreier graph of an infinite cyclic subgroup are both boards.

**Proof.**
1. **Translates of one branching edge.** Let K = Stab(s0), of finite index, and let p be branching at the directed edge
   e0 = (u0 → u0h). Its lifts k·e0 (k ∈ K) carry the same pattern, because s0 is K-invariant.
2. **Disjoint half-trees.** In the finite graph Sch(K), a non-backtracking walk can reach e0's image from any vertex. So every
   branch of the tree, deep enough, contains a lift of e0 that points away from 1. Hence there are infinitely many lifts whose
   half-trees T_1, T_2, … are pairwise disjoint and escape to infinity.
3. **Two completions on each.** On each T_i take two completions: A_i = s0|T_i, and B_i, a translate of one fixed completion with a
   different root pattern. For c ∈ {0, 1}^ℕ let s_c be s0 with B_i on T_i where c_i = 1. Each s_c ∈ X, since disjoint half-trees
   complete independently.
4. **Each nontrivial element is avoided.** Fix k ≠ 1. At most two T_i contain an end of k's axis, so for every other i the half-tree
   k⁻¹T_i is disjoint from T_i.
   - Given c_1, …, c_m, take such an i > m and fix every other c_j.
   - (k·s_c)|T_i = s_c(k⁻¹ ·)|T_i does not depend on c_i, and A_i ≠ B_i. So one value of c_i gives k·s_c ≠ s_c.
5. **Baire.** {c : k·s_c = s_c} is therefore closed and nowhere dense in {0, 1}^ℕ. By the Baire category theorem some c avoids all
   countably many of these sets, and Stab(s_c) = 1.
6. **An infinite cyclic stabilizer.** Fix k* ∈ K, k* ≠ 1, and repeat the construction with half-trees T_i off k*'s axis and choices
   constant along their k*-orbits. Then s_c is k*-invariant.
   - An element k ∉ ⟨k*⟩ cannot map T_i onto any k*^n T_i: that would fix a directed edge, and F2 acts freely.
   - So step 5 applies to every k ∉ ⟨k*⟩, and Stab(s_c) = ⟨k*⟩ for generic c. ∎

## T4. Lemma B: without a free solution, an open set of isolated rigid solutions

**Statement.** If no solution has trivial stabilizer, then for some h ≠ 1 and some nonempty open set U = [P] ∩ X, every s ∈ U is
fixed by h. Each such s is uniquely completed on every half-tree outside a finite region that contains no end of h's axis.
Consequently U is finite, and its points are isolated in X.

**Proof.**
1. **Baire.** X = ∪_{h≠1} Fix(h), a countable union of closed sets in a compact space, so some Fix(h) has interior U.
2. **Rigidity off the axis.** Let s ∈ U, and let T be a half-tree beyond an edge outside P's support that contains no end of h's
   axis, so that hT ∩ T = ∅. Suppose s″ is a second completion of T.
   - Then s″ ∈ U ⊆ Fix(h), and so is s. Their difference set D ⊆ T therefore satisfies hD = D.
   - That contradicts hT ∩ T = ∅. So T is uniquely completed.
3. **Finite data.** Every vertex off the axis, outside a finite neighbourhood of P, lies in such a half-tree. Along the axis s is
   h-periodic. So s is fixed by its values on a finite set that depends only on P and h, and U is finite. ∎

## T5. The dichotomy W

**Statement (proved).** W holds for every law that is deterministic (no branching pattern: every solution is fixed by its pattern at
one name, so X is finite and every board is finite) and for every law with a periodic solution using a branching pattern (T3). By
ticket B's census that covers all 1,024 Life-like one-bit laws and the atom: 31 have no solution, 97 are deterministic, and 896 and
the atom have a periodic branching solution.

**Reduction (W in general, not proved).** W is equivalent to: a tree shift with no solution of trivial stabilizer has no
non-isolated point (it is then finite, so every orbit is finite). In that case, the following is proved for every point t of a
nonempty open subset of the non-isolated points (Baire on the derived set, then step 2 of T4):
- t is fixed by some h ≠ 1;
- t is uniquely completed on every far half-tree not containing one end ξ of h's axis, and not uniquely completed toward ξ;
- every far alternative completion t″ toward ξ is isolated.

**The gap.** Excluding such a t would prove W. The natural argument is that t″'s stabilizer must preserve the infinite ray of t's axis
states toward the other end, so it is trivial. That argument fails if the rigid completion inside T recreates those states along
other rays.

## T6. The plane P

**Statement (proved where W is).** A law that forces the plane would have only infinite boards and none on the tree, contradicting
W. So P holds for every law covered by T5, in particular for every one-bit Life-like law and the atom. In general P follows from W.

**Remark.** P can fail only for a law with no finite board and no free solution, which is weakly but not strongly aperiodic. Free
groups carry such laws, and no strongly aperiodic ones (Piantadosi 2008).

## Checks

`check.py` (result in `result.json`):
- the horofunction colouring obeys its law on the ball of radius 9, is invariant under x³, and is moved by every other element of
  length at most 6;
- all 897 class-A certificates of ticket B's census (896 Life-like laws and the atom) are re-verified from the law.

## Sources

- **Classical.** Busemann functions and ends of trees; the Baire category theorem.
- **Shifts on free groups.** Piantadosi (2008): no strongly aperiodic SFT; free groups are weakly periodic but not strongly
  periodic (via Carroll and Penland). Bitar (arXiv 2406.04132): stabilizers of SFT points and periodically rigid groups.
- **Graph subshifts.** Arrighi, Durbec and Guillon (2023).
- **Novelty.** T2, T3 and T4 are elementary and close to folklore. W was not found stated for free groups (bounded search,
  2026-11-10).
