# Chains of knots off parity laws: they split from bond distance exactly at gates

Status: Proved (exhaustive finite census; `check.py`, standard library only, about two minutes).

Ticket `BOND-CHAIN-20261108-001B`, 2026-11-08.

## Standard statement

- **Gate.** Two knots that share one distinction b meet at a *gate* when one value of b satisfies both by itself: fixing b to it
  leaves every value of each knot's other distinctions allowed.
- **Theorem.** For every law made of two three-place knots sharing one distinction (1,156 laws), a knot contains both far ends
  exactly when the knots do not meet at a gate; the least such knot then has four distinctions. For chains of up to four single
  clauses, a knot contains both ends exactly when every shared distinction is read with opposite signs by its two clauses, so
  that the clauses chain as implications.
- **So.** Off parity laws, chain distance and bond distance part exactly at gates: a chain joins the two sides of a gate, and no
  knot does.

## Nearest known result

That a common variable which can satisfy both constraints at once decouples them is the elementary reason a pure literal can be
set without loss in satisfiability (Davis and Putnam 1960). Its use as the line between the two measures was not found
(known-with-delta).

## Terms

As in `BOND-CHAIN-20261108-001A`: knots are read from allowed states (constrained, with every projection forgetting one
distinction full, at least three distinctions); chain distance is counted in knots, or in the distinctions of the chain's union.

## Theorem 1 (two three-place knots)

Of the 34 three-place knots (5 classes up to permuting and negating variables), glue any two at one distinction: R1 on (x, a, b),
R2 on (b, c, y). In 1,084 of the 1,156 gluings a knot contains x and y, always with four distinctions, so bond distance between x
and y is 3, chain distance is 1 knot and 4 counted in distinctions. In the other 72 no knot does: the only knots are R1 and R2, so
bond distance is infinite while a chain of two knots joins x and y. The 72 are exactly the gated gluings, and only knots of two
classes have gates: single clauses (each value that satisfies one of its literals frees the other two) and the six-state class of
"x implies y = z" (x = 0 frees y and z).

*Proof.* Exhaustive computation over the 1,156 laws. ∎

## Theorem 2 (chains of single clauses)

For T = 2, 3, 4 and every choice of signs (8^T laws), the chain of clauses on (s0, a1, s1), ..., (s(T−1), aT, sT) has a knot
through s0 and sT exactly when, for each shared s_t, the forbidden values of s_t in its two clauses differ: in one clause s_t is a
conclusion and in the next a premise. The atom thread, every clause w(t−1) ∧ L(t) → w(t), is of this kind: a knot of T + 2
distinctions spans T clauses (checked at T = 5, as `LOGIC-AXIS-20261107-001A` proved for all T). The NAND thread, every clause
not(s(t−1) ∧ a(t) ∧ s(t)), is gated at every shared distinction: its only knots are its clauses (checked at T = 5).

*Proof.* Exhaustive computation (64, 512 and 4,096 laws). ∎

## What it says

- **A gate is a common hub.** At a gate the shared distinction can switch both knots off at once, so neither side constrains the
  other through it. The foundation already says that a shared distinction alone is not a touch: two independent relations on A and
  k and on B and k make k a common hub (`AGENTS.md`, canonical foundation). Bond distance follows that rule, since it needs a knot
  through both sides; chain distance does not.
- **The NAND thread** is a chain of knots that chain distance reads as a number line, one step per clause, while bond distance sees
  only separate clauses. The atom thread, the same clauses with the signs of an implication, is a line for both.

## Nonclaims

- **Not every law.** The census covers three-place knots glued at one distinction and clause chains up to four; larger gluings and
  knots sharing two distinctions are not covered.
- **Not a theorem of the foundation.** That bond distance is the native spacing is a reading of the foundation's contact rule, not
  derived from K1–K3 alone.
