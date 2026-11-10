# Boards under Leibniz's rule

Status: Partial

Ticket `LEIBNIZ-BOARDS-20261110-001A`, pre-registered 2026-11-10 before the proof attempt and before ticket B's census runs.

## Setting

As in `BOARD-DIST-20261110-001A`: names are the words of F2 = ⟨x, y⟩, e(u, v) says names u and v are one place (transitivity, letter
closure, constancy), and a value law is finitely many finitary clause templates over a finite alphabet Q, reading values only.
**Leibniz's rule** adds: u and v are one place exactly when s(ug) = s(vg) for every word g. It is one infinitary rule (each clause
would name infinitely many variables), so the unfolding theorem of `BOARD-DIST-20261110-001A` does not reach it. Write X for the
law's solutions on the tree of names (a tree shift) and Stab(s) = {h : s(hg) = s(g) for every g}.

## Statements frozen here

- **S (strong form).** Every board is the tree or finite. Refuted by an infinite board other than the tree.
- **W (the dichotomy).** If some board is infinite, the tree is a board: X has a solution with trivial stabilizer. Refuted by a law
  with an infinite board and no board on the tree.
- **P (the plane).** No law makes every board grow quadratically; in particular none forces the plane. Refuted by such a law.

## Targets

1. **T1.** The boards are exactly the Schreier graphs Sch(Stab(s)), s ∈ X.
2. **T2.** S is false. Found by hand before registration: the horofunction law on Q = Z/3 (a place of value k has exactly one
   neighbour of value k − 1 and three of value k + 1) has the solutions s(u) = b(u) + c mod 3 for the Busemann functions b of the
   ends of the tree, and for the end x^∞ the stabilizer is ⟨x³⟩, so Sch(⟨x³⟩), a 3-cycle with trees attached, is a board.
3. **T3 (Lemma A).** If a solution with finite orbit uses a branching pattern (a pattern with two compatible neighbour patterns in one
   direction), then X has a solution with trivial stabilizer and one whose stabilizer is infinite cyclic.
4. **T4 (Lemma B).** If X has no solution with trivial stabilizer, then some isolated solution is invariant under an h ≠ 1 and is
   rigid (uniquely completed) on every half-tree that does not contain an end of h's axis, outside a finite region.
5. **T5 (W).** The dichotomy for every finitary value law over a finite alphabet, or W reduced to an explicit statement.
6. **T6 (P).** From W; unconditionally for deterministic laws (finitely many solutions, every board finite) and for the laws T3
   covers.

## What would count against

A law with an infinite board and no board on the tree (W), or with every board quadratic (P). For T3, a periodic solution with a
branching pattern and no solution with trivial stabilizer.
