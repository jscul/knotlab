# Pre-registration: the pinning theorem, and pins that vary

Epic `PIN-RULE-20261112-001` (`SUBST-NEST-20261112-001` directions 1 and 2; G17 with G8; program mathematics, group arithmetic),
written on 2026-11-12 at the coordinator's go-ahead under the owner's standing mandate. The proof below was found by hand before this
file was written, and is frozen with it; the check (`proofs/PIN-RULE-20261112-001A/PIN-RULE-20261112-001A-P001_pinning_theorem/check.py`)
is frozen too and has not been run. The canonical K1–K3 test is unchanged.

## Words

As in the guide's glossary (12 November 2026): block, distinction substitution, block triples, between-copy knots, spare
distinction, part, tied part, tie extent, steps apart. Here the block triples are always **the block's knots in every order**.

## The claims

- **Theorem (pinning).** For every block B, every pattern P whose knots hold three distinct distinctions, every state of σ(P), every
  knot (x, y, z) of P and every distinction p of B that is not spare: x_p = y_p = z_p. Hence p's part is constant on each connected
  component of P, and with SUBST-NEST's lemma N6 (a spare distinction's part is tied to nothing) the tied parts of σ(P) are exactly
  those of the distinctions B cannot spare, each tied by equality.
- **Proof.** Let a, b, c be the copies' states. If a_p ≠ b_p, say a_p = 0 and b_p = 1 (the mirror gives the other case), take a knot
  e = {p, u, w} of B. The between-copy knots include NAE(a_p, b_u, c_w) and NAE(a_p, b_w, c_u): if c_u = c_w = 0 they force
  b_u = b_w = 1, and b is constant on e. They include NAE(a_u, b_p, c_w) and NAE(a_w, b_p, c_u): if c_u = c_w = 1 they force
  a_u = a_w = 0, and a is constant on e. Both are impossible, so c differs on u and w for every knot through p, and c, a state of B,
  holds both values on every knot avoiding p: c is a spare witness for p. So a_p = b_p for any two of the three copies.
- **Corollary (pins never vary).** Under these block triples a pin is always an equality along each knot of P, so a pinned part
  takes one value on each component: it is uniform, never a relation that changes from copy to copy.

## The check (frozen; descriptive support, not the proof)

On the 87 blocks of `SUBST-NEST-20261112-001`'s census and the 300 of its stress test, with one knot of P and three copies: each
distinction is forced equal in the three copies exactly when it is not spare, by equality and never by inequality, and a spare one is
tied to nothing; and, on the 87, for every pair of states differing at p and every compatible third state, the third is a spare
witness for p (the proof's step, enumerated). Failure criterion: any exception refutes the theorem as stated and is reported as such.

## What a sceptic would call built in (frozen, to be revisited with the advisor's answer)

The between-copy knots are the block's own knots with their members drawn from three copies, so three equal copies always satisfy
them, and a pinned value is carried by equality along each knot: the reach across the whole pattern is the pattern's connectivity
chaining local equalities, a wire, not a long-range effect. What is not built in: which distinctions are pinned (a property of the
block alone, not visible from the definition) and that nothing else is.

**Referee.** The background referee thread, after the write-up (referee pending).

Assumptions in force: A75 (Assumed; this epic is about the substitution reading). Nothing here bears on P versus NP.
