# Bond-pinning, the two-block window and localisation

Status: Proved

Ticket `TOP-INFO-20261114-001B`, 2026-11-14. Statements as frozen in `research/TOP-INFO-20261114-001/preregistration.md`. The setting,
Facts 1 and 2 and the pumping dichotomy are those of `proofs/READ-RULE-20261114-001A/READ-RULE-20261114-001A-P001_read_rule/proof.md`.
Decidability of boundedness is left open, and the gap is stated at the end.

## Theorem P′ (bond-pinning)

*Statement.* Let c be a covered copy at depth s, V main's ports and X_c c's own distinctions. If some shattered T ⊆ V and shattered
D ⊆ X_c have T ∪ D not full, then L(s) ≤ |T| + |D|.

*Proof.* T ∪ D is non-shattered, so it contains a minimal non-shattered subset B, a bond. If B missed D, it would lie in T, which is
shattered, and every subset of a shattered set is shattered. So B meets D, and likewise B meets T. Hence B holds a port of main and an
own distinction of c, and |B| ≤ |T| + |D|. ∎

*Remark.* Plain correlation of V with X_c is not enough. The advisor's relation NAE4(p, q, r, t) × {0, 1}, minus the states
(0011, x = 1) and (1100, x = 0), is complement-closed and correlated. But every three ports with x are full, so no bond inside
V ∪ {x} holds x.

## The two-block window

*Statement.* Let w be an S-word from a start, c the copy at its end, and J′_w the joint relation of every distinction of main's
flattened block with c's ports, in the pattern with c's subtree removed. Then the projection of the pattern onto main's block together
with c's block is {(a, b) : (a, b|ports) ∈ J′_w, b satisfies c's knots and its children's usual-limit relations}. Identical
distinctions are merged as in Lemma W. Hence every bond of this projection holding a port of main and an own distinction of c is a
bond of the pattern, and U₂(s) ≥ L(s).

*Proof.* As for Lemma W (`research/CARRY-BOUND-20261114-001/preregistration.md`).
- **Separation.** c's subtree meets the rest only through c's ports.
- **Composition.** J′_w = Start′ · R_{w₁} ⋯ R_{w_s}. Start′ is main's block, with every call but the chosen S-call replaced by its
  usual-limit relation, projected onto main's block and the chosen call's arguments. The composition is exact by the same separation
  at every copy on the way.
- **Main's block.** It lies outside every copy's subtree, so it is part of the context of each step.
- **Periodicity.** The pair (J′_w, the identity partition) takes finitely many values, so U₂ is eventually periodic by the same
  state iteration. ∎

## Localisation

*Statement.* Suppose L(s) ≤ C for every large s on a residue modulo Π = m!. Here m counts the states (copy type, product of
per-call relations from a copy, carry map) over words started from any copy. Then for every s on that residue beyond
(C + 1)·m·(Π + 1) + C, some bond of size at most C has a constrained shape:
- along the target's word, its occupied levels lie within B = C·m·(Π + 1) levels of the root or of the target copy;
- inside a side subtree or the target's subtree, each member lies within m + 1 levels of the previous occupied level on its path, so
  within C·(m + 1) levels of where the subtree branches off.

(Corrected on the advisor's check. The first draft said "within m levels of where they branch off", left the copy type out of the
state, and did not say how large s must be.)

*Proof.* Take a bond W of size at most C at depth s. Call a level of the target's word occupied when the copy there, or a copy in its
side subtrees, holds a member of W as its own distinction; each member counts once, at its allocating copy, as READ-RULE's referee
required. Stretch products run over the blocks strictly inside the stretch, as repaired there. There are at most C + 1 member-free stretches.
- **Shortening a stretch by a multiple of Π.** In a member-free stretch of at least m·(Π + 1) levels, some state (the product from
  the stretch's top and the carry map) occurs at least Π + 1 times. Two of these occurrences, at levels l < l′, have l′ − l ≡ 0
  modulo Π. Cutting the levels between them keeps the stretch's product and its carry map. So it keeps the projection of the moved set,
  as in the dichotomy's proof, and it lowers the target's depth by a multiple of Π.
- **Restoring the depth.** Apply this to every stretch but the longest until each is shorter than m·(Π + 1). Then lengthen the
  longest by the removed amount, a multiple of Π, by the dichotomy's pumping. The longest still has more than m levels, since the
  depth is large. The result is a bond of the same size at depth s, on the same residue, whose occupied levels lie within B of the
  root or of the target.
- **Side subtrees and the target's subtree.** On the path from where a side subtree branches off down to one of its members, a run
  of more than m levels between occupied levels repeats a state, copy type included, so the cut word is a legal word. Cutting it
  changes no depth that counts. Along the target's word every copy is a copy of S, so the type is constant there. ∎

*What remains open: decidability.* B depends on the bound C, and C is not known in advance. So the localisation turns "is L bounded on
this residue?" into a search over growing windows that halts when the answer is yes. Without an a priori bound on C, a no is not
certified. An a priori bound on the least bounded value in terms of m would make boundedness decidable per family. The advisor
sketched one route, not checked here. The condition "W non-full while W∖V and W∖X_c are full" depends on finite types of the members
above and below each level, and cutting between equal types removes members. That would bound the occupied levels in terms of m, the
number of ports and the block size.
