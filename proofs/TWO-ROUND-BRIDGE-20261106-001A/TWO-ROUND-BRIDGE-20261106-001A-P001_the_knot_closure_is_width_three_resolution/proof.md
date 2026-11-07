# The knot closure is width-3 resolution

Status: Proved (the elimination lemma and the translation by hand; the local data checked exhaustively)

Ticket `TWO-ROUND-BRIDGE-20261106-001A`, 2026-11-06.

## Standard statement

Let S be the solution set of a satisfiable system of signed not-all-equal constraints on three variables, written as the join, over
three interface variables Y on which it shows all six non-constant patterns, of a near relation and a fixed far relation. A
three-variable implicate of S is a pair of complementary 3-clauses. Call it crossing when it mentions a variable private to each side.
Then the crossing 3-implicates that resolution of width 3 derives from the one-sided implicates on at most three variables are exactly
those of the program's elimination closure, each derived in depth at most two by resolving only on interface variables; every other
crossing 3-implicate is still implied by the one-sided 3-implicates and is derived from them in width exactly 4.

## Nearest known result

- **Interpolation through a separator.** If F and G share only the variables Y, every consequence of F ∧ G on its own variables
  factors through Y (Craig); Davis–Putnam elimination of the interface variables makes this a resolution derivation.
- **Bounded-width resolution is local consistency** (Atserias–Dalmau 2008).
- **Classification.** known-with-delta. The delta is the exact identification: the program's knot closure is width-3 resolution, and
  creation is the width-4 part of the interpolant.

## Setting

- **Splices.** As in `PENDANT-LINE-20261106-001A`: a near side (any complement-closed set of assignments showing the gluing line's six
  patterns) joined at the line's points Y with one of the four census far sides (K4^(3), census 6, the Fano plane, census 58).
- **Knots as clauses.** A knot {a, b, c} (a minimal constrained set of three tie classes) misses exactly one complementary pair of
  patterns {v, v̄} (check 2: all non-degenerate knots). As clauses it is the pair forbidding v and v̄: a signed not-all-equal
  constraint.
- **Base.** The one-sided implicates on at most three variables: the near side's and the far side's knots and ties, which are the
  splice's non-crossing knots and ties.
- **Shapes.** c, c′ far classes; x, w near classes off Y; y, z points of Y. Crossing knots are {c, x, y}, {c, x, w} and {c, c′, x}.

## 1. The elimination lemma

**Two knots A and B sharing two variables h, s have resolvents of width 3 exactly when they are sign-compatible: their forbidden
patterns relate h and s differently (one forbids h = s, the other h ≠ s, in literal terms). The resolvents are then the clauses of the
knots that A and B imply on the other two triples of A ∪ B.**

*Proof.*
- **Shape of a resolvent.** A resolvent of width 3 of two 3-clauses on A and B needs exactly one clashing variable among h, s and one
  agreeing one; otherwise the clauses clash on both (a tautology) or on neither (no resolvent).
- **Compatible.** Exactly then one clause of A and one of B clash on h and agree on s, and their complements do the same. The
  resolvent on h forbids one pattern of (A ∪ B) − h and its complement: the implied knot. Resolving on s instead gives the knot on
  (A ∪ B) − s.
- **Incompatible.** Every clause of A clashes with every clause of B on both or on neither of h, s. ∎

Check 1 runs all 64 sign patterns: resolvents exist exactly on the 32 compatible ones and equal the implied knots.

**So width-3 resolution on these clauses is elimination between sign-compatible knots.** A width-3 step between two clauses of
different knots is the lemma's step. Two knots on the same triple would give a tie, which non-degenerate classes exclude. Steps
through ties rename classes.

## 2. The translation

**Theorem.** At a gluing line, the crossing knots that the elimination closure reaches are exactly the crossing knots that resolution of
width 3 derives from the base. Each is derived:
- in depth one when it meets the line: {c, x, y} is the resolvent of a far knot {c, y, z} and a near knot {x, y, z} on z;
- in depth two otherwise: {c, x, w} is the resolvent of such a round-one knot {c, x, y} and a near knot {x, w, y} on y, and {c, c′, x}
  of a round-one knot and a far knot {c, c′, y} on y.

Every step resolves on a point of the gluing line. So every crossing derivation is a linear chain from one far knot through at most two
near knots, or from two far knots through one near knot.

*Proof.*
- **Resolution lies in the closure.** A width-3 step between knots is a sign-compatible elimination (the lemma). Its conclusion is
  implied, so it is constrained; its classes are untied, so it is a knot. Every such step is a closure step, and the closure's crossing
  knots are those of the two-round rule (`PENDANT-LINE-20261106-001A`).
- **The closure lies in resolution.** Whether a crossing knot T is reached by the two-round rule, and what resolution derives from the
  base on the variables T ∪ Y, both depend only on the near relation's projection onto (T ∩ near) ∪ Y and the far relation's onto
  (T ∩ far) ∪ Y. Check 3 enumerates every such pair: the 27 near relations on {x} ∪ Y and the 3,375 on {x, w} ∪ Y that show the six
  patterns, against every far class and pair of the four far sides. On every non-degenerate one, width-3 resolution from the base
  implicates on T ∪ Y derives T exactly when the rule reaches it (52,308 crossing knots), in depth one for {c, x, y} and two for the
  others, resolving only on gluing-line variables. Check 5 shows the depth-two route for {c, x, w} is the one stated. ∎

**Corollary (whole splices).** On census and random near sides at every gluing line and far side, the closure under sign-compatible
eliminations equals the knot closure on all 120,606 crossing classes (check 4).

### The literal two-round rule is not itself a resolution derivation

- **Round one is.** Every knot {c, x, y} the rule reaches has a sign-compatible witness z: 0 exceptions among 92,193,676 local
  instances (check 2).
- **The pairs step is not.** For {c, x, w}, the rule's step from {c, x, y} and {c, w, y} is sign-incompatible at every y in 1,645,912
  of 1,685,232 local instances (check 2), and compatible in only 56 of the 1,392 reached cases of check 5.
- **Another depth-two route always works.** It is the near-knot route above (check 5, all 1,392). The closure's semantic test hides the
  difference; resolution does not.

## 3. What creation costs

**Theorem.** Every new crossing knot (one outside the closure) is implied by the base, and resolution derives it from the base in width
exactly 4 and depth 2, resolving only on gluing-line variables.

*Proof.* Width 3 does not suffice, by §2. Check 3 shows, on the same exhaustive local data, that every crossing knot is implied by the
one-sided implicates on at most three variables, and that every new one (5,116 of shape {c, x, y}, 2,368 of shape {c, x, w}, none of
shape {c, c′, x}) is derived at width 4 in depth 2 resolving only on Y. ∎

*Why width 4 suffices for {c, x, y}, by hand.* Given the line's six patterns, a near point's relation to Y is fixed by the knots it forms
with Y's pairs: at the pattern whose equal pair is {y_i, y_j}, the excluded values of x are read off the projection onto
{x, y_i, y_j}. So {c, x, y} is forbidden at three patterns π¹, π², π³ of Y with y = a. One side's 3-clause excludes the pattern at each.
Resolving the clauses for π¹ and π³ on their shared line point gives a clause of width at most 4, and resolving that with the clause
for π² gives the knot. When the sides at π¹ and π³ agree, the middle clause is one-sided and the derivation stays at width 3; that is
round one. When they differ, the same derivation passes through width 4. This is HANDLE-EMERGENCE's "pin and separate" in clause
form.

## What "depth two through a cut" bounds

| Measure | Value | Scope |
| --- | --- | --- |
| Rounds (resolution depth across the cut) | 1 for knots through a gluing-line point, 2 otherwise | relative to the base; new knots also need 2 |
| Width | 3 for the closure, exactly 4 for creation | every clause on at most six variables (T ∪ Y) |
| Resolved variables | the three gluing-line variables only | |
| Formula depth | 1 (clauses throughout) | Res(⊕) and bounded-depth Frege are not needed |
| Not bounded | the cost of the base | one-sided implicates may need large width or size inside each side |

So the two-round rule is a statement about interpolation through a three-variable interface. Interpolation through such an
interface is classical. What is new is that the native closure is exactly its width-3 part, and that creation is exactly the part
that needs a fourth variable.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The elimination lemma | 32 compatible, 32 incompatible sign patterns; resolvents = implied knots |
| 2 | Exhaustive local configurations (348,376,032; 346,754,982 non-degenerate) | every knot misses one pair; compatible steps conclude knots; round one always has a compatible witness; literal pairs step incompatible in 1,645,912 of 1,685,232; control fails as it should |
| 3 | Widths on the exhaustive local data | 52,308 crossing knots: width-3 derivable ⟺ reached; all implied by the base; new ones width 4, depth 2; only gluing-line pivots |
| 4 | Whole splices (600 seeds) | 120,606 crossing classes: compatible closure = knot closure |
| 5 | The route to {c, x, w} | all 1,392 reached by a round-one knot and a near knot; literal pairs compatible in 56 |

## What this does not establish

- **Other far sides.** As in PENDANT-LINE A, the local checks cover the four census far sides used by the creation map.
- **Global cost.** Nothing here bounds a refutation of a whole space; that is ticket B.
- **Knots of more than three points.** Not covered, matching the creation map.

## Novelty

- **Classical.** Interpolation through a separator; resolution of not-all-equal constraints.
- **New here.** The closure is exactly width-3 resolution through the cut, and creation is exactly its width-4 part. The rule's
  literal pairs step is not a resolution step, while a linear near-knot chain always is.
