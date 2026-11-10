# Free solutions without finite boards

Status: Partial

Ticket `WEAK-APER-20261110-001A`, pre-registered 2026-11-10 before the proof attempt and before ticket B's census runs.

## Setting

As in `LEIBNIZ-BOARDS-20261110-001A`.
- **The shift.** X is a nearest-neighbour shift of finite type on the tree of F2, the solutions of a value law on a place and its
  four neighbours over a finite alphabet. P is its set of tree patterns.
- **Free solutions.** Under Leibniz's rule a solution's board is Sch(Stab(s)), and a solution is **free** when Stab(s) = 1, so its
  board is the tree.
- **Weakly aperiodic.** X is weakly aperiodic when it is nonempty and no solution has a finite orbit, that is, no finite board is
  allowed.

## Targets

1. **Balance.** A finite board is allowed iff the balance equations over P have a nonzero nonnegative solution. For each letter g and
   pair of values (a, b), the patterns with (centre, g-value) = (a, b) must be as many as those with (g⁻¹-value, centre) = (a, b).
2. **Lemma A″.** If some solution has infinitely many pairwise disjoint half-trees, each with two completions, then X has a free
   solution. This is the Baire argument of Lemma A without the periodic solution.
3. **L1.** Call a vertex type a pattern with its parent direction. If some type can reach a branching choice and recurs in two
   different child directions of itself, then some solution has infinitely many disjoint such half-trees, so X has a free solution.
4. **L2.** Suppose every place of a solution has exactly one neighbour one level lower. Its stabilizer then fixes the end its
   orientation points to, so a solution whose end is fixed by no nontrivial element is free. Busemann functions of such ends qualify
   whenever (1, 0, 3) is allowed.
5. **W.** Every infinite X has a free solution, or the gap stated precisely.

## What would count against

- **Against W.** A weakly aperiodic law with no free solution.
- **Against the certificates.** A law certified by L1 or L2 whose solutions all have nontrivial stabilizers.
