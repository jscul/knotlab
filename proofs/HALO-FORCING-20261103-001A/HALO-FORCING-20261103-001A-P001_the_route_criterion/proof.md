# The route criterion

Status: Proved (item 1); items 2 and 3 are exhaustive computations

Ticket `HALO-FORCING-20261103-001A`, 2026-11-03.

## Question

- **Background (HANDLE-LOCALITY B).** A Fano plane attached at a point of a plane piece, once opened by a removal, creates at plane
  gluing lines out to distance 5.
- **The question.** Which gluing lines does it reach, and why? This ticket finds the exact local rule that decides whether a candidate
  knot is new.

## Dependencies

- **`HANDLE-LOCALITY-20261103-001B`.** The creation map and the join-based method (`join_lib.py`).
- **`HANDLE-LOCALITY-20261103-001A`.** Pieces and closures.
- **`PLANAR-COMPOSE-20261102-001A`.** The route lemma for pinned knots.
- **`PLANAR-THEOREM-20261102-001B`.** One-port 2-sums.
- **`SPLICE-TREE-20261102-001C`.** Circuits and the closure.

## Setting

- **The knot.** K = {r, o, c} is a crossing knot at a gluing line L: r and o are near points, c is a far point, and (ρ, ω, γ) is an
  excluded pattern.
- **T.** The set of L's patterns compatible with r = ρ and o = ω.
- **E.** The set of L's patterns excluded by c = γ. Since the pattern is excluded, T lies inside E.
- **A block.** For an ordered pair (y, y′) of L's points and values (b, b′), the block is the set of L's patterns with (y, y′) = (b, b′).

## 1. The route lemma (proved)

**K is generated from one-sided knots if it has a route.** A route is one of the following:
- **one port:** a point of L takes one value on all of T and the other on every pattern the far point allows;
- **(i):** r is tied to a point y of L; T fixes y = b and y′ = b′; and E contains the block (b, b′);
- **(ii):** r is tied to neither y nor y′; T fixes y = b; the near set {r, y, y′} excludes (ρ, b, b̄′); and E contains the block (b, b′).

The roles of r and o may be exchanged.

*Proof.* Two facts are used throughout.
- **Pairs.** In a complement-closed solution set, every constrained pair is a tie. L's points are pairwise free because L shows six
  patterns.
- **Degenerate ties.** If c were tied to a near point, or o to a point of L used below, K would be tie-equivalent to a one-sided set and
  would lie in the base.

So the knots built below are knots: each is constrained, and each of its pairs is free unless one of these degenerate ties holds.

- **One port.** This is the one-port 2-sum (PLANAR-THEOREM B).
- **Route (i).**
  - **The knots.** K₁ = {r, o, y′} excludes (ρ, ω, b̄′), since T fixes y′. K₂ = {y, y′, c} excludes (b, b′, γ), since E contains
    the block.
  - **The elimination.** Eliminating y′ gives {r, o, y, c}. In tie classes this is K itself, because r ~ y. So one step of the closure
    produces K.
- **Route (ii).**
  - **The first knots.** K₀ = {r, y, y′} excludes (ρ, b, b̄′), and K₂ = {y, y′, c} excludes (b, b′, γ).
  - **An intermediate knot.** Eliminating y′ gives K₃ = {r, y, c}, which is constrained. Given r = ρ and y = b, K₀ forces y′ = b′, and
    then c = γ is excluded.
  - **The last step.** K₁ = {r, o, y} excludes (ρ, ω, b̄), since T fixes y. Eliminating y from K₁ and K₃ gives K.
  - **Gluing-line points.** If o is y, then K₃ is already K. If o is y′, then K₁ is K₀ and the same two steps apply. ∎

This generalizes PLANAR-COMPOSE A's route lemma in three ways:
- T may be two adjacent patterns (an edge) as well as one;
- the far point may exclude more than the pinned pattern, which opens routes through other pairs of L's points;
- either near point may serve.

## 2. The converse on one-handle spaces (computation)

- **The spaces.** The Fano plane is attached at a point (its line 0 spliced into point 0) of five grown plane pieces: 10 points, seeds 0
  and 1; 12 points, seeds 0 and 1; 14 points, seed 0.
- **The sweep.** Every removal inside the handle, every plane gluing line with six patterns, and four far sides: K4^(3), census 6, the
  Fano plane and census 58.
- **The candidates.** Every three-point crossing circuit with a near point in the handle.

| Candidates | No route | Route (i) | Route (ii) |
| --- | --- | --- | --- |
| Both near points in the handle | 2,000, all new | 480, none new | 2,528, none new |
| One near point on the gluing line | 600, all new | 1,920, none new | 18,816, none new |
| One near point elsewhere | 400, all new | 3,840, none new | 32,400, none new |

- **Counting.** Candidates are counted per value assignment.
- **The new knots.** In each case they are exactly the candidates without a route. There are 1,500 new knots, in 182 of the 1,392 cases.
  Every new knot has a near point in the handle.
- **So, on these spaces,** a three-point crossing knot at a plane gluing line is new exactly when it has no route.

## 3. Creation depends on the plane piece only through the transfer (computation)

- **The transfer R(L).** The set of (port pattern, L pattern) pairs that occur together.
- **The result.** Over all cases, creation is a function of (removal, far side, R(L)): 840 classes, none with mixed outcomes, 336 of
  them met more than once.
- **Why it should be so.** For a candidate whose near points lie in the handle, every input to the criterion is a projection of the
  handle's relation joined with R(L).
- **What decides creation.** The cases that create are exactly those with a no-route candidate whose two near points both lie in the
  handle. So creation needs only those candidates (checked in ticket C).

## Checks

`check.py` (`result.json`, about two minutes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The route criterion, knot by knot | new knots = candidates without a route, in every case |
| 2 | Creation as a function of the transfer | 840 classes, single-valued |

## What this does not establish

- **The converse in general.** That a knot without a route is always new. It is checked here only on one-handle spaces up to 14 plane
  points.
- **Larger knots.** Knots of four or more points (HANDLE-LOCALITY B found none at plane gluing lines).

## Novelty

- **New here.** The generalized route lemma, and the exact criterion on these spaces.
- **Classical analogue.** The 2-sum and 3-sum decompositions of matroid circuits.
