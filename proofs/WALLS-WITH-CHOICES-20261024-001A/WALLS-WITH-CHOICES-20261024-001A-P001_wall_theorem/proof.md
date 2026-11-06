# Periodic walls decide every direction

Status: Proved

Ticket `WALLS-WITH-CHOICES-20261024-001A`, 2026-10-24.

**What it uses:**
- from `DIRECTIONAL-RIGIDITY-20261023-001B-P001`:
  - the setting: places, the constant frame, lone places, free and pinned places, the four kinds;
  - Lemma A (the lifted picture) and Lemma B (the frame flip and the half turn);
  - the proof of its Theorem 7, which shows that the walls of an assignment have a constant left value;
  - its Theorems 2, 3 and 7 and Remark 8, which this proof generalizes;
- from `LINE-DETECTOR-20261023-001B-P001`: the cylinder covers by strips and by cyclic covers;
- from `DIRECTIONAL-RIGIDITY-20261023-001A-E001` (frozen, supported): the exhaustive rows used to test Theorem 3.

## Standard statement

### Setting

- **Worlds and classes.** As in `DIRECTIONAL-RIGIDITY-20261023-001B-P001`. Work in the constant frame, where U contains the
  constants.
  - Φ is the set of free places: the lone places of doubly allowed patterns.
  - Π is the set of pinned places. For k ∈ Π, R contains exactly one lone-k pattern, whose lone value is v_k.
  - Λ = Φ ∪ Π is the set of allowed places.
  - 27 of the 30 three-place tiling contacts have a constant frame. The other three (91, 94, 123) have diagonal stripes and are
    settled by Theorem 2 there.
  - In the frame the twist is the relative twist, and an odd class c has q(c) = 1.
- **Wall moves.** A wall state is a triangle T, the edge E through which the wall enters it, and the value ℓ on the wall's left.
  - In T the wall turns left or right and leaves through the corresponding edge. The corner inside the turn is its lone corner:
    the start of E in counterclockwise order for a left turn, the end of E for a right turn.
  - The turn is allowed when its lone corner's place k is free, or pinned with v_k + x̃(T) = ℓ for a left turn and ℓ + 1 for a
    right turn. Here x̃ is the frame's lifted coin.
  - The wall keeps its left value ℓ.
- **Periodic walls.**
  - A periodic wall is a bi-infinite sequence of allowed moves in ℤ² invariant under translation by a nonzero lattice vector h,
    its period.
  - Equivalently, it is the lift of a closed walk C in the torus's wall graph, whose states are wall states taken modulo the
    torus with ℓ read relative to the twist. Its class e(C) is h in class units.
  - The overlap set D(C) is the set of differences of the positions of two distinct visits of C to one torus triangle within one
    traversal.
- **Crossing and simple.** Let w = (c₁L, c₂M).
  - A periodic wall W crosses the cylinder along c when det(c, e) ≠ 0.
  - It is simple there when it meets none of its translates W + kw (k ≠ 0) and crosses no triangle twice.

**Lemma 1 (crossing walls are read off the torus).** A periodic wall that crosses the cylinder along c is simple there exactly
when D(C) ∩ (ℤc + ℤe(C)) = ∅.

**Lemma 2 (cyclic covers).** The cylinder along any class has an assignment exactly when some cyclic cover of it by finitely many
sheets has one.

**Theorem 1 (periodic walls decide every direction).** Take a three-place tiling contact with a constant frame, any twist and
configuration, and an odd class c. The cylinder along c has an assignment exactly when some periodic wall crosses it and is
simple there; that is, exactly when the torus's wall graph has a closed walk C with det(c, e(C)) ≠ 0 and
D(C) ∩ (ℤc + ℤe(C)) = ∅.

**Corollary 2 (the earlier theorems as cases).**
- **Straight walls** (`DIRECTIONAL-RIGIDITY-20261023-001B-P001`, Theorem 3). The periodic walls are the compatible diagonal
  staircases. One of them serves every odd class at once.
- **Rotating walls** (Theorem 7 there). The moves are forced, so the closed walks are the cycles of a partial permutation.
- **Remark 8 there** is the direction (⇐) of Theorem 1.

**Theorem 3 (the quadrant rule for directed walls).** Take one of the six bending contacts whose allowed places are {0, 2}: 54,
62, 110, 147, 155 and 203.
- **Walls are directed.** Their walls cross the diagonal edge of every triangle, so they move only up or left through unit
  squares.
- **The quadrant.** Every periodic wall crosses every cylinder whose class has c₁c₂ > 0, and is simple there.
- **Hence** all odd classes with c₁c₂ > 0 contradict together, exactly when the wall graph has no cycle. Selectivity can only
  separate classes with c₁c₂ ≤ 0 from one another and from that block.

**Remark 4 (walls that turn both ways).** For the six bending contacts with Λ = {0, 1, 2}, the first quadrant can split.
Placement 151 on 3 × 3 (twist 01, configuration 110633) has an assignment along (1, 1) and contradicts along (2, 1)
(certified in `DIRECTIONAL-RIGIDITY-20261023-001B-P001`, Proposition 4).

**Remark 5 (the window form).** For directed walls put t = j − i and s = i + j. Along a wall t rises by 1 per square and s
changes by ±1.
- So W meets W + w exactly when some stretch of |w₂ − w₁| squares changes s by w₁ + w₂ (with the orientation of w that makes
  w₂ − w₁ ≥ 0). That is, the wall travels exactly w in that many steps.
- For c₁c₂ > 0 this cannot happen, since |w₁ + w₂| > |w₂ − w₁|.

## Nearest known result

- **Lemma 2.** The standard fact that a nonempty one-dimensional shift of finite type has periodic points (Lind and Marcus);
  transfer matrices for strips rest on it.
- **Theorem 1.** It decomposes a periodic configuration of a strip into domain walls. Both steps are standard in the theory of
  two-dimensional shifts of finite type. Reading cylinder satisfiability off periodic walls that avoid their own copies is new to
  the program; low to moderate folklore risk.
- **Theorem 3.** An elementary Lipschitz argument; new to the program.

## Proof

### Lemma 1

- **Overlap ⇒ not simple.** Let two visits of C to one torus triangle sit at positions differing by d ∈ D(C).
  - Then W contains a triangle T and its translate by d (in lattice units). Since W + h = W, it meets W + d + jh for every j.
  - If d = kc + je(C) with k ≠ 0, then W meets W + kw.
  - If k = 0, the second visit coincides with a translate of the first by a multiple of the period, so W crosses one triangle
    twice.
- **Not simple ⇒ overlap.** Conversely, take two distinct visits of W to the same triangle up to translation by kw (k ≠ 0, or
  k = 0 for a repeated triangle). Reduce both modulo the period to one traversal of C.
  - They become two visits to one torus triangle whose positions differ by kc + je(C).
  - They are distinct visits, because equal indices would force kc + je(C) = 0, hence k = j = 0 by det(c, e(C)) ≠ 0. ∎

### Lemma 2

- **The strip is a shift of finite type.** In the cover of `LINE-DETECTOR-20261023-001B-P001`, the cylinder's nodes are pairs
  (vertex, sheet t ∈ ℤ), and the clauses of every sheet are the same pattern shifted in t.
  - So the assignments of the cylinder are the bi-infinite sequences of sheet assignments in {0, 1}^{LM} that satisfy one finite
    set of constraints on windows of a fixed width K.
  - That is a one-dimensional shift of finite type.
- **A periodic point.** If it is nonempty, some sequence has two equal windows of width K − 1, at positions i < j. Repeating the
  block from i to j − 1 gives a sequence all of whose windows of width K occur in the original. It is periodic with period
  m = j − i.
- **The cover.** A periodic sequence of period m is exactly an assignment of the cyclic cover by m sheets; the converse is the
  lift. ∎

### Theorem 1

**(⇐)** This is the construction of `DIRECTIONAL-RIGIDITY-20261023-001B-P001`, Theorem 7 (⇐), which uses only that the moves are
allowed.
- By Lemma 1 the translates W + kw are pairwise disjoint and cut the plane into strips.
- Give the strip left of W + kw the value ℓ + k. Crossed triangles then carry lone patterns their coins allow, and every other
  triangle is constant.
- Since q(c) = 1, translation by w changes every coin and moves each strip to the next, so F(p + w) = F(p) + 1.

**(⇒)**
- **A cover.** By Lemma 2 some cyclic cover T_m = ℤ²/(ℤw + ℤmu) has an assignment F, where u is a lattice vector with
  det(c, u) = 1 in class units.
- **Its walls.** Every triangle of F is constant or lone, so it has 0 or 2 cut edges. The cut edges therefore form disjoint
  simple closed walls on T_m. By the proof of Theorem 7 there, each wall has a constant left value and makes allowed moves.
- **One wall crosses.** A loop of class w meets the cut edges an odd number of times, since F(p + w) = F(p) + 1. So some wall W₀
  meets it an odd number of times.
  - Write W₀'s class in T_m as αw + βmu. The loop meets W₀ ±β times, so β is odd.
  - In particular det(c, e) = βm ≠ 0 for its class e in classes.
- **Its lift.** Lift W₀ to the cylinder ℤ²/ℤw and to ℤ². The lift W is a periodic wall that crosses the cylinder.
  - A lift of a simple closed curve is simple: two parameters with one image upstairs have one image on T_m, so they differ by a
    multiple of W₀'s period, which moves the lift by a nonzero multiple of its class, not a multiple of w.
  - So W is simple on the cylinder. Its torus projection is the required closed walk, by Lemma 1. ∎

### Corollary 2

- **Straight walls.** In `DIRECTIONAL-RIGIDITY-20261023-001B-P001`, Theorem 3, every wall runs along a diagonal staircase. A
  periodic one is a compatible staircase, and it crosses every cylinder except the diagonal one without meeting its copies.
- **Rotating walls.** In Theorem 7 there, each state has at most one successor and one predecessor. So a closed walk retraces a
  cycle, and Lemma 1 is the overlap condition stated there. ∎

### Theorem 3

- **Directed walls.** A crossed triangle's lone corner is place 0 or place 2, the ends of the diagonal edge. So the wall crosses
  the diagonal of every triangle it enters, and passes between the up and down triangles of one unit square.
  - In the square of (i, j) the up triangle has its bottom and right sides, and the down triangle its left and top sides.
  - So the wall enters each square through the bottom or the right and leaves through the left or the top: it moves only up or
    left, from square to square.
- **The Lipschitz bound.** Put t = j − i and s = i + j for squares. Along W, t rises by 1 per square and s changes by ±1.
  - So W is the graph of a 1-Lipschitz function s(t). It crosses no square twice, and a fortiori no triangle twice.
  - Let c₁c₂ > 0 and orient w so that both coordinates are positive. Then W + kw at time t sits at s(t − kτ) + kσ, with
    τ = w₂ − w₁ and σ = w₁ + w₂ > |τ|.
  - Since |s(t) − s(t − kτ)| ≤ |kτ| < |kσ|, W and W + kw share no square for k ≠ 0.
- **Crossing.** A periodic wall's class e has e₁ ≤ 0 ≤ e₂ and e ≠ 0, because t rises along it. A class with c₁c₂ > 0 has
  det(c, e) = c₁e₂ − c₂e₁ ≠ 0.
- **Conclusion.** By Theorem 1, for odd c with c₁c₂ > 0 the cylinder has an assignment exactly when some periodic wall exists,
  that is, when the wall graph has a cycle. Every cycle has e ≠ 0 since t rises. ∎

## Checks

`check.py` uses the standard library only (seed 20261024) and the shared machinery of the predecessor's check. Every result below was obtained:
- **Theorem 1 on samples.** 153 configurations of the 27 placements with a constant frame: one random configuration per non-fitting
  twist on 3 × 3 and 3 × 4, plus the certified examples on 3 × 3. That gives 761 odd classes certified by the own solver, none
  undetermined.
  - **292 have assignments.** For every one, the check does four things:
    - it finds a wall of the cover assignment that meets the cylinder's loop an odd number of times;
    - it confirms that the wall's moves are valid with its left value;
    - it confirms that its closed walk has a transverse class and no overlap in ℤc + ℤe;
    - it rebuilds an assignment from that walk alone and confirms that it passes every triangle of a window.
  - **469 contradict.** In every one, no simple cycle of the wall graph passes the criterion; the enumeration was never capped.
- **Theorem 3.**
  - On the samples, all 84 first-quadrant odd classes of directed contacts contradict exactly when the wall graph has no cycle.
  - On the frozen exhaustive rows, none of 363331584 configurations and twists of the six directed contacts with a
    first-quadrant odd class splits the first quadrant.
- **Controls.**
  - Comparing each visit only with the first visit misreads one class of placement 151's configuration 210021 (twist 01), which
    all pairs read right.
  - Placement 151's configuration 110633 splits the first quadrant.
  - A traced wall's moves are valid with its left value and invalid when that value is read from the other end of the entry
    edge.

## What this does not show

- Whether simple cycles of the wall graph suffice. Theorem 1 quantifies over all closed walks; ticket B tests simple cycles on
  small tori.
- Any bound on the number of sheets of the cover, or on the length of the closed walk needed.
- That every bending contact is selective on every large torus (ticket C).
- Anything about other triangulations, or about space or physics. Lattices and twists are declared.
