# Creation between glue lines depends only on the switching class

Status: Proved (from PENDANT-LINE A's two-round rule and a finite lemma on the edge atom, checked exhaustively; cross-checked on 22
placements and 136 random switchings)

Ticket `SWITCH-PROOF-20261108-001A`, 2026-11-08.

## Question

SWITCH-READ found, on five glues, that two placements of the atoms in one switching class give native creation maps that agree exactly
between glue lines and differ through the atoms. Is the first half a theorem?

## Dependencies

- **`PENDANT-LINE-20261106-001A`.** The two-round rule: the crossing knots in the closure are exactly those it reaches, and a far side
  creates at the gluing line exactly when some crossing knot is not reached. Its setting: knots are minimal constrained sets of at
  most three tie classes, the near side is complement-closed, and complementing points changes no constrained set.
- **`CHAIN-TRANSFER-20261106-001A`.** Complementing further points changes no constrained set.
- **`SWITCH-READ-20261108-001A`.** The placements and the computed comparison.
- **HANDLE-COUNT A's edge atoms** (`families.py`).

## Setting

- **The glue and its signing.** A glue H is a cubic incidence system. A signing S is a set of its incidences. The signed glue (H, S)
  allows an assignment of the points when on every line the three literals, the point's value xor the incidence's sign, are not all
  equal.
- **The plain space X_S.** H with an edge atom on every incidence (i, p) of S: seven fresh points r0 to r6, the root line {r1, r2, p} and
  the other six Fano lines on r0 to r6, while line i holds r0 in place of p. All signs are zero.
- **Switching.** S and S' are in one switching class when S' = S xor δ(U) for a set U of points and lines of H, δ(U) being the
  incidences with exactly one end in U.
- **Creation between glue lines.** For lines a ≠ b of H: remove a from the space, glue a far side at b's three points Y, and ask whether
  a new crossing knot appears (PENDANT-LINE A). The order-free vector records this for K4^(3), the Fano plane and census 58.

## Theorem

**For every cubic glue H, every two signings S and S' of H in one switching class, and every two lines a ≠ b of H, removing a and
gluing at b gives the same result in X_S and in X_S': both degenerate, or the same verdict for each far side.**

*Proof.*

1. **The edge atom (check 1).** Its own seven lines, over all 256 assignments of its eight points, force r0 = r1 = r2 = ¬p. For each
   value of p they leave its four inner points five configurations, in which each inner point takes both values, and over the two
   values of p each pair of inner points takes all four pairs. The atom meets the rest of the space only at p and at r0 on line i
   (check 2), so given the values outside the atom every one of these configurations is available, independently of the other atoms.
2. **Inner points take part in no knot the rule uses.** Work in the joint system: X_S without line a, with a far side glued at Y. The
   points r0, r1 and r2 are tied to p, so they lie in p's class. Let T be a triple of classes containing an inner point q.
   - **One inner point of its atom.** By step 1, q takes both values whatever the other two classes of T do, so T's projection is a
     product of the other two classes' projection with both values of q. T is constrained only if those two are, and then forgetting
     q leaves a constrained set: T is not a knot.
   - **Two inner points q, q′ of one atom, and a class u.** If each value of u occurs with both values of p, the projection is u's
     values times all four pairs, so T is unconstrained. Otherwise some value of u forces p. The joint system is complement-closed, so u
     is then tied to p and is p's class. Then T has no far class and at most one class meeting Y, so it is neither a crossing knot nor a
     base knot {c, y, z} or {x, y, z}.
   - **Three inner points.** No far class, and no class of Y: not used either.
   So every knot the two-round rule uses, and every crossing knot, lies among the other classes. Whether a triple is a knot is decided by
   its projection. So the far side's verdict is decided by the projection of the joint system onto the points of H, with p's class
   holding r0, r1 and r2, together with the far side.
3. **That projection is the signed glue.** Each atom forces r0 = ¬p, so line i reads the literal ¬p: the near side's projection onto
   the points of H is the solution set of (H, S) without line a. Conversely every such solution extends to every atom, by step 1. If b
   holds an atom's r0, the gluing line's values are its literals in (H, S).
4. **Switching only complements points.** Complementing the points of U carries the solutions of (H, S) without a onto those of
   (H, S′) without a. On a line ℓ each literal x_q xor s changes by [q ∈ U] xor [q ∈ U] xor [ℓ ∈ U] = [ℓ ∈ U]: nothing changes, or all
   three literals flip, which not-all-equal does not see (check 2 verifies the map on every pair of placements). In particular the
   values at b's points change all together or not at all. Complementing points changes no constrained set (PENDANT-LINE A,
   CHAIN-TRANSFER A), and complementing all of Y turns the far side into its far-complement, again a complementing of points. So the
   two joint systems have the same tie classes, knots and two-round verdicts, and Y shows its six patterns in both or in neither. ∎

## Corollary

- **The glue block is the signed glue's map.** Creation between glue lines of X_S is creation in the signed glue (H, S), by steps 2 and
  3. Computed: in all 22 stored and mapped placements the two agree on all 3,500 entries (check 3).
- **Only the atoms see the placement.** Removing a line of an atom breaks r0 = ¬p, so step 3 fails there; SWITCH-READ found that these
  rows do differ between placements.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The edge atom, all 256 assignments | 10 solutions; r0 = r1 = r2 = ¬p; inner points and pairs free as stated |
| 2 | Atom contacts in every placement; switching as complementing, every pair of placements, every line removed | pass |
| 3 | The glue block against the signed glue's map | 22 placements, 3,500 entries, all equal |
| 4 | Random switchings of each signed glue | 136 of 136 unchanged |

## What this does not establish

- **Atom removals.** Removing a line of an atom is outside the theorem, and SWITCH-READ shows it sees the placement.
- **Other atoms.** The proof uses the edge atom's own lemma (step 1); other gadgets need their own.
- **Counting.** Whether the glue block carries exactly what Pfaffian counting uses is not shown.

## Novelty

- **New here.** The theorem and its proof.
- **Classical.** Switching classes of signed graphs (Zaslavsky).
