# A polynomial rule for directed walls with choices

Status: Proved

Ticket `READING-COST-20261024-001A`, 2026-10-24.

**What it uses:**
- from `WALLS-WITH-CHOICES-20261024-001A-P001`: the wall moves and the wall graph, Theorem 1 (periodic walls decide every
  direction) and Theorem 3 (the quadrant rule);
- from `DIRECTIONAL-RIGIDITY-20261023-001B-P001`: the constant frame and the allowed and pinned places of each placement;
- from `WALLS-WITH-CHOICES-20261024-001B-E001` (frozen, refuted): for these six placements, simple cycles reproduce the frozen
  record on 3 × 3 and 3 × 4, which the check uses as ground truth there;
- classical tools: Aubry's ordering argument, and the fact that max-closed constraints are decided by arc consistency (Jeavons
  and Cooper 1995).

## Standard statement

### Setting

- **Directed placements.** These are the six bending placements whose allowed places in the constant frame are {0, 2}: 54, 62,
  110, 147, 155 and 203.
  - In 54 and 147 both places are pinned.
  - In the other four one place is free.
- **Coordinates.** A square (i, j) of the lifted plane has t = j − i and s = i + j, so s ≡ t (mod 2).
- **The type-preserving lattice.** Let q_f be the relative twist of the frame.
  - Λ′ = {(aL, bM) : q_f · (a, b) even}. Translation by a vector of Λ′ keeps the lifted coins.
  - Translation by any other torus vector complements them; for an odd class c this includes w = (c₁L, c₂M).
  - T′ = ℤ²/Λ′ has |T′| = LM squares if q_f = 0, and 2LM otherwise.
- **Good walls.** A periodic wall is *good* for c if it crosses the cylinder along c and meets neither its translates W + kw
  (k ≠ 0) nor any triangle twice. Theorem 1 of `WALLS-WITH-CHOICES-20261024-001A-P001` says that c has an assignment exactly when a
  good wall exists.

**Lemma 1 (moves one at a time).** In a directed placement, take any wall and orient it suitably.
- **Its route.** It enters each square through the bottom or the right edge, crosses the diagonal, and leaves through the top or
  the left edge.
- **Its moves.** Fix its left value ℓ. Whether a move from a square to the square above, or to the square on its left, is allowed
  depends only on that move. It does not depend on how the wall entered the first square.

So a wall is the graph of a function s(t) with s(t + 1) − s(t) = ±1. For each ℓ, the allowed moves form a set of edges of the
square lattice.

**Lemma 2 (walls form a lattice).** For walls with one left value in the lifted plane, the pointwise maximum and the pointwise
minimum of two walls are again walls.

**Lemma 3 (good means strictly above or below).** Let c be an odd class with c₁c₂ ≤ 0. Let w′ be whichever of ±w has
t-component T > 0, and write D for its s-component. A periodic wall W is good for c exactly when one of these holds:
- **Case A.** W(t) − W(t − T) < D for every t; that is, W + w′ lies strictly above W.
- **Case B.** W(t) − W(t − T) > D for every t; that is, W + w′ lies strictly below W.

In each case, the good walls with one left value are closed under pointwise maximum, pointwise minimum and translation by Λ′.

**Lemma 4 (an ordered good wall).** Let W be a good wall, in case A or B, whose period h lies in Λ′. Define
W* = max{W + v : v ∈ Λ′, det(h, v) ≤ 0}. Then:
- W* is a good wall in the same case;
- it is comparable with each of its translates: for every v ∈ Λ′, either W* + v ≤ W* or W* + v ≥ W*;
- its period is the primitive vector e₀ of Λ′ along h.

**Lemma 5 (splitting).** Let W* be as in Lemma 4, and let N be the t-component of e₀. Suppose W* passes squares Q and Q + v, with
v ∈ Λ′, at times t₁ < t₁ + v_t < t₁ + N.
- **The two pieces.** The closed walks from Q to Q + v and from Q + v to Q + e₀ give walls: W_a with period v and W_b with period
  e₀ − v.
- **Which piece is good.** In case A, W_b is good if W* + v ≥ W*, and W_a is good if W* + v ≤ W*. In case B the two roles are
  exchanged.

**Theorem 6 (short good walls).** Suppose an odd class c with c₁c₂ ≤ 0 has an assignment.
- It then has a good wall that visits each square of T′ at most once per period. Its period has at most |T′| squares.
- In particular, simple cycles of the wall graph decide every class for the six directed placements, on every torus.

**Theorem 7 (a polynomial rule).** For a directed placement, one can decide whether an odd class contradicts in time polynomial in
L · M and in the bit length of c.
- **If c₁c₂ > 0:** test whether the wall graph has a cycle (Theorem 3 of `WALLS-WITH-CHOICES-20261024-001A-P001`).
- **Otherwise:** loop over each period e ∈ Λ′ with t-component between 1 and |T′|, each left value, and each case. For each, decide
  by arc consistency whether some wall with period e satisfies the inequality of Lemma 3.

**Corollary 8 (where the question stays open).** Among the twelve bending placements, a class can now be read in polynomial time for
all but the four honeycomb placements with a free place (111, 125, 159, 215):
- the four whose walls have no choices (54, 109, 147, 151) by the cycles of a partial permutation;
- the four directed placements with a free place by Theorem 7.

The straight-wall placements have the explicit rule of `DIRECTIONAL-RIGIDITY-20261023-001B-P001`, Theorem 3. The diagonal class of
the diagonal-stripe placements is not examined here.

## Nearest known result

- **Lemma 4.** This is Aubry's ordering argument for ground states (Aubry and Le Daeron 1983; Bangert 1988), with a maximum in place
  of energy minimization.
- **Lemma 5.** Splitting a periodic orbit at a repeated point is standard.
- **Theorem 7.** The last step is the tractability of max-closed constraints (Jeavons and Cooper 1995).
- **Provenance.** Reducing the reading of a direction for directed walls to these tools is new to the program.
- **Folklore risk: moderate.** Periodic monotone paths in periodic directed lattices with non-crossing conditions are close to the
  theory of rotation numbers of monotone circle maps.

## Proof

### Lemma 1

- **Which edges a wall uses.** Place 1 is not allowed, so a wall separates corner 0 or corner 2 of each triangle it meets.
  - In an up triangle, with places 0 = (i, j), 1 = (i + 1, j), 2 = (i + 1, j + 1), lone corner 0 means the wall uses the bottom edge
    and the diagonal; lone corner 2 means the right edge and the diagonal.
  - In a down triangle, with places 0 = (i, j), 1 = (i, j + 1), 2 = (i + 1, j + 1), lone corner 0 means the left edge and the
    diagonal; lone corner 2 means the top edge and the diagonal.
- **The route.** So every wall crosses the diagonal of each square it meets, using one of the square's bottom and right edges and one
  of its top and left edges. Orient it from the first pair to the second.
- **What decides a turn.** The turn in the up triangle is fixed by the entry edge (bottom: lone 0; right: lone 2). The turn in the
  down triangle is fixed by the exit edge (left: lone 0; top: lone 2). Whether a turn is allowed depends on its lone place, the
  triangle's coin and ℓ, since the lone corner's value is ℓ or ℓ + 1 according to the turn's side.
- **The moves.** A move up from Q passes the top edge of Q's down triangle and then the bottom edge of the up triangle above. A move
  left passes the left edge of Q's down triangle and then the right edge of the up triangle on the left. Each move is therefore
  allowed exactly when the exit turn of Q's down triangle and the entry turn of the next up triangle are both allowed. Neither turn
  depends on how the wall entered Q.
- **The function form.** Each move raises t by one and changes s by ±1. ∎

### Lemma 2

- **The maximum.** Let W₁ and W₂ have left value ℓ, and let W = max(W₁, W₂).
- **Where W switches walls.** Values at one t have the same parity and change by ±1. So if W follows W₁ at t and W₂ at t + 1, then
  W₁(t) = W₂(t): if W₁(t) ≥ W₂(t) + 2, then W₁(t + 1) ≥ W₂(t + 1).
- **Every move of W is allowed.** Each move of W is a move of W₁ or of W₂ out of the square W occupies, and by Lemma 1 a move is
  allowed whatever came before. So W is a wall.
- **The minimum.** The same argument applies. ∎

### Lemma 3

- **The copy W + w′.** Translation by w′ complements the coins. A turn's condition is unchanged when both the coin and ℓ are
  complemented, so W + w′ is a wall with left value ℓ + 1. It too is the graph of a function of t.
- **When two walls meet.** Two walls share a triangle exactly when they occupy the same square at some t. The difference
  W(t) − (W + w′)(t) is even and changes by 0 or ±2 per step. So the two walls are disjoint exactly when the difference keeps one
  sign, which is case A or case B, since (W + w′)(t) = W(t − T) + D.
- **Case A, or case B, implies good.** In case A, W + (k + 1)w′ > W + kw′ for every k, so W meets none of its translates.
  - W meets each triangle at most once, because it occupies one square per t.
  - It crosses the cylinder. If det(c, e) were 0, then some multiple kw′ (k ≠ 0) would be a multiple of the period, and
    W + kw′ = W would contradict the strict order.
  - Case B is the same with the order reversed.
- **Good implies case A or case B.** A good wall is disjoint from W + w′, so the difference keeps one sign.
- **Closure.** In case A, max(W₁, W₂) + w′ = max(W₁ + w′, W₂ + w′) > max(W₁, W₂) at every t. The same holds for the minimum and for
  case B. Translation by Λ′ commutes with translation by w′ and keeps the coins. ∎

### Lemma 4

- **A finite maximum.** Let σ = h_s/h_t, and let A bound |W(t) − σt − c₀| for a suitable constant c₀.
  - The mean of (W + v)(t) − W(t) is v_s − σv_t = det(h, v)/h_t.
  - If det(h, v)/h_t < −2A, then W + v < W everywhere, so it does not change the maximum.
  - The remaining v with det(h, v) ≤ 0 fall into finitely many classes modulo ℤh, and W + v depends only on the class.
- **W\* is good.** So W* is the maximum of finitely many good walls with one left value and case. By Lemmas 2 and 3 it is a good wall
  in that case. Its index set is invariant under adding h, so W* + h = W*.
- **Comparable with its translates.** For u ∈ Λ′ with det(h, u) ≤ 0:
  W* + u = max{W + v′ : det(h, v′) ≤ det(h, u)} ≤ W*.
  For det(h, u) > 0, apply this to −u to get W* ≤ W* + u.
- **The period.** Let h = n e₀. If W* + e₀ ≤ W*, then W* = W* + ne₀ ≤ W* + (n − 1)e₀ ≤ … ≤ W* + e₀ ≤ W*, so W* + e₀ = W*. The case
  W* + e₀ ≥ W* is the same. ∎

### Lemma 5

- **Both pieces are walls.** At each junction, a piece arrives at a square by one of W*'s moves and leaves it by another of W*'s
  moves, translated by a vector of Λ′. Translation by Λ′ keeps the coins, and by Lemma 1 a move does not depend on the entry. So
  W_a and W_b are walls with left value ℓ.
- **What the pieces look like.** By the definition of the periodic extension, W_a equals W* + kv on its k-th period
  [t₁ + kv_t, t₁ + (k + 1)v_t]. Likewise W_b equals W* − kv on its k-th period.
- **Case A with W\* + v ≥ W\*.** Then W* − kv ≤ W* − k′v whenever k ≥ k′.
  - Take t in the k-th period of W_b, and let t − T lie in its k′-th period. Then k′ ≤ k, because T > 0.
  - W* − k′v is good in case A (Lemma 3), so
    W_b(t) = (W* − kv)(t) ≤ (W* − k′v)(t) < (W* − k′v)(t − T) + D = W_b(t − T) + D.
- **The other three combinations** are the same argument, with W_a in place of W_b or with the inequalities reversed. ∎

### Theorem 6

- **A periodic good wall exists.** By Theorem 1 of `WALLS-WITH-CHOICES-20261024-001A-P001`, c has a good periodic wall. Its period
  lies in Λ′, because a closed walk of the wall graph returns to the same relative left value.
- **Shortening.** Apply Lemma 4.
  - If the result visits a square of T′ twice within a period, Lemma 5 gives a good wall with a strictly shorter period.
  - Apply Lemma 4 to that wall, which does not lengthen the period, and repeat.
  - The period strictly decreases, so the process stops at an ordered good wall that visits each square of T′ at most once per
    period. Such a period has at most |T′| squares.
- **Simple cycles.** A wall state of the torus fixes a square and, through the relative left value, its class modulo Λ′. So two
  visits to one state would be two visits to one square of T′. Hence the projection of this wall is a simple cycle of the wall
  graph. ∎

### Theorem 7

- **If c₁c₂ > 0.** Theorem 3 there: c contradicts exactly when the wall graph has no cycle. Testing that is linear in the 12LM
  states.
- **Otherwise: a finite search.** By Theorem 6 and Lemma 3, c has an assignment exactly when some combination of the following
  admits a periodic wall W with period e that satisfies the inequality of its case:
  - a left value ℓ;
  - a case, A or B;
  - a period e ∈ Λ′ with t-component N between 1 and |T′|; every wall then has |e_s| ≤ N.
- **One constraint problem per combination.** Write x_t = W(t) for t = 0, …, N − 1, with x_{t+N} = x_t + e_s. The constraints are:
  - the move from (t, x_t) to (t + 1, x_{t+1}) is allowed;
  - x_t − x_{t−T} < D in case A, or > D in case B.
- **Finite domains.** Translating W by a vector of Λ′ with t-component 0 keeps every constraint. So one may require 0 ≤ x₀ < S₀,
  where S₀ (equal to 2LM/g or 4LM/g, with g = gcd(L, M)) is the smallest such s-shift. Then every x_t lies in a window of size
  S₀ + 2N.
- **Arc consistency decides each problem.** Both kinds of constraint are max-closed: if two pairs satisfy one, so does their
  componentwise maximum. For the moves this follows from the argument of Lemma 2; for the inequality, directly. A constraint problem
  whose constraints are all max-closed is decided by arc consistency: if no domain becomes empty, the domains' maxima form a
  solution (Jeavons and Cooper 1995).
- **The count.**
  - There are O(LM) periods: both components of e are bounded in terms of |T′| ≤ 2LM.
  - There are two left values and two cases.
  - Each problem has at most 2LM variables, domains of size O(LM) and 4LM constraints, so arc consistency takes polynomial time.
  - The class c enters only through T and D. ∎

### Corollary 8

- **Walls without choices.** For 54, 109, 147 and 151 the moves form an injective partial map on 12LM states
  (`DIRECTIONAL-RIGIDITY-20261023-001B-P001`, Theorem 7). So a closed walk is a power C^k of one of at most 12LM cycles.
  - C^k is good exactly when C is. An overlap d = ac + be of C gives the overlap d + je of C^k, which lies in ℤc + ℤke once
    j ≡ −b (mod k). Conversely, the overlaps of C^k are d + je with d ∈ D(C) ∪ {0}, and je lies in ℤc + ℤke only when k divides j.
  - Checking every cycle therefore takes polynomial time.
- **Directed placements with a free place.** These are Theorem 7. ∎

## Checks

`check.py` uses the standard library only (seed 20261024) and the machinery of `WALLS-WITH-CHOICES-20261024-001A-P001`'s check.
Every result below was obtained.
- **Lemma 1.** 360 random configurations of the six directed placements were tested, over every non-fitting twist on 3 × 3, 3 × 4,
  4 × 4, 4 × 5 and 5 × 5.
  - Every up-triangle state leads only to the down triangle of its square.
  - Every down-triangle state leads only to the square above or the square on the left.
- **Lemmas 4 and 5, Theorem 6.**
  - **Random walls.** 245 crossing walls of cover assignments were shortened: smallest covers, random configurations of the four
    placements with a free place on 3 × 3 and 3 × 4. None needed a split.
  - **Listed walls.** Five walls from larger covers (5 or 7 sheets), with starting periods 14 to 25, needed one or two splits each.
    They ended with periods 3, 11 or 12.
  - **Every step held.** Every intermediate wall was valid and good in its case. After each ordered maximum it was comparable with
    its translates. Every final wall visits each square of the type-preserving cover at most once.
- **Theorem 7.** The decider agrees with the ground truth on all 1432 classes tested, and none was undetermined. The ground truth
  was:
  - simple cycles on 3 × 3 and 3 × 4 (25 and 10 configurations per placement);
  - the own solver on covers and strips on 4 × 4 and 4 × 5 (4 and 3 configurations per placement).
- **Controls.**
  - Dropping the window constraint accepts 34 contradicting classes.
  - In one split of the listed walls, the other piece is not good.
  - Reading the type-preserving lattice with the placement's twist instead of the frame's leaves a repeated square in a good cycle
    of a frame-flipped placement.
- **Scoping (scratch, not evidence).** Before the check was written, the decider was compared on the four placements with a free
  place:
  - with simple cycles on 14382 classes on 3 × 3 and 3 × 4;
  - with PySAT, on covers and strips, on 5316 classes on 4 × 4, 4 × 5, 5 × 4, 5 × 5 and 3 × 5.

  It agreed on every one.

## What this does not show

- **The four honeycomb placements with a free place (111, 125, 159, 215).** Their walls are not monotone, two walls cannot be
  combined by a maximum, and `WALLS-WITH-CHOICES-20261024-001D-P001` shows that their good walls must sometimes repeat a state.
- **An efficient algorithm.** The polynomial bound is crude.
- **The diagonal class of the diagonal-stripe placements.**
- **Anything beyond the declared lattices.** Nothing about other triangulations, space or physics.
