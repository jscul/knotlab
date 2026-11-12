# A direction the knot law does not lengthen: pre-registration

Epic `FOLD-20261112-001` (`BOND-BALLS-20261111-001` direction 1; G1, question 9; program topology, group spacing), 2026-11-12, at
the coordinator's go-ahead under the owner's standing mandate. The canonical K1–K3 test is unchanged.

## Words

As in the guide's glossary and `BOND-BALLS-20261111-001`: steps apart, bond, bond distance, ball, shortcut. **Base 16** is
BOND-BALLS's base with index 16: one kind of distinction over Z² and the knot kinds {0, (0,1), (1,−1)} and {0, (0,2), (1,1)}. The
**sheared frame** is (x, y) ↦ (x, y + x), an automorphism of Z²; there the knot kinds are {0, (0,1), (1,0)} and {0, (0,2), (1,2)},
every knot is a pair in one column with a distinction in the next, and the **travelling triple** T_x = {(x,0), (x,1), (x,2)} keeps its
rows. A base **folds, to six steps,** when some distinction five steps from the origin and some six steps away each lie in a bond of
four with it.

## Disclosed before freezing

The exact check of ticket A (`proofs/FOLD-20261112-001A/.../check.py`) was written and run before this record was committed, and it
passed: the parts below are free for every k ≥ 3, by states repeating in one shift with period 3 to 8, whose transfer graphs' powers
repeat with period 2 from the ninth (so k = 3 to 11 decide every k). The failure lines for ticket A are therefore stated for the
record, not as a blind test; ticket B's census has not run. The referee of `BOND-BALLS-20261111-001` found bonds of four at five and six
steps on 14 of the 16 four-step shortcut bases it tested (not on 81 and 88).

## What is settled by definition

- **Not the fold.** By `OVERLAP-READ-20261111-001B`'s L5 the law reads a base only through how many knots lie on each pair. On base 16
  (sheared) the pair class (1, 0) lies in two knots and (0, 1), (1, −1), (0, 2), (1, 2) in one each. These classes span both shifts,
  so no knot pattern with the same counts repeats along one shift only, and steps apart grow along the fold (the triple k columns back
  is k steps away). So "no length" is not how the shifts were supplied; it is the law's "two equal force the third opposite" iterated
  along the pair class that carries two knots.
- **Faithfulness is not at stake.** The law never ties the origin to one far distinction: each pair is free (checked below). It binds
  the origin only jointly with a whole triple, and only when that triple is all equal.

## Ticket A: the statement (proof in `proofs/FOLD-20261112-001A/`)

- **Theorem F.** On base 16, for every k ≥ 3, the sets {(−k, k−2), (−k, k−1), (−k, k), origin} and, for j = 0, 1, 2,
  {origin, (0,1), (0,2), (k, j − k)} are bonds of four, and every pair of the origin with one of their far distinctions is free. So
  every distinction (−k, k−i) and (k, j−k), k ≥ 3, i and j in {0, 1, 2}, is at bond distance at most 3 from the origin: the ball of
  bond radius 3 contains a whole line in both directions, at least six distinctions for every k ≥ 3.
- **Failure would be** a k ≥ 3 at which some part is not free (the triple stops being a bond there), or a forcing step needing a knot
  the base does not have. Not claimed: which other distinctions lie in the radius-3 ball, or the law's balls at larger radius.

## Ticket B: which shortcut bases fold (census, frozen in `experiments/FOLD-20261112-001B/`)

- **Family.** BOND-BALLS's 42 bases with a shortcut, 18 of them with a four-step shortcut.
- **Reading.** For k = 5 and 6, a distinction w k steps away and two distinctions within one step of w that form, with the origin and
  w, a bond of four (constrained in the window of radius 15, parts free by PERIODIC-READ's bounds); the first found is recorded.
- **Prediction G.** Every base that folds to six steps has a four-step shortcut: none of the 24 bases with only three-step shortcuts
  folds. Failure: one that does, a fold the four-step search missed. Measured: how many of the 18 fold.

## Prior work (bounded search, 2026-11-12)

Deterministic propagation of a constraint along a direction is classical: in the Newman–Moore triangular plaquette model a ground state
fixes each spin from the row below, which gives cellular-automaton rules and fractal symmetries; the theory of expansive and
non-expansive directions for Z² actions (Boyle and Lind, "Expansive subdynamics", 1997) classifies directions along which a pattern
determines its neighbours. Here the propagation is one-sided and partial (a column fixes only some of the next), and what is new, as far
as found, is its reading as a bond distance that does not grow on a base the law reads faithfully. Classification expected:
known-with-delta.

## Stop rule

The proof refereed, one registered run of ticket B, one referee pass; report and hold.

## Runtime

Ticket A's check: under a minute. Ticket B: minutes on 8 workers (0.2 to 0.3 s a base in a timing run on bases 16 and 14, which fold and do not).
