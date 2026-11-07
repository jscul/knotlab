# The sphere's count needs resolution width Θ(√n)

Status: Proved by hand (lemma 3's winding bound and lemma 4's isoperimetric constant by sketch). The window criterion, the certificates
and a simulated game are checked by computation.

Ticket `SPHERE-WIDTH-20261107-001A`, 2026-11-07.

## Standard statement

**Theorem.** Let K_k be the octahedral knot sphere: the Kasteleyn-signed plane cubic triple system dual to the k-frequency
octahedron, with n = 4k² points. Every resolution refutation of its not-all-equal formula has width at least c·k − 1, for an absolute
constant c > 0. Width O(k) suffices. So the resolution width is Θ(√n).

**Corollary (sketch).** The decorated three-fold spaces of `TWO-ROUND-BRIDGE-20261106-001B` add only bounded local pieces. A Duplicator
that answers their variables from local completions keeps the bound Ω(√n).

## Nearest known result

- **Width and pebble games.** Width is the existential pebble game (Atserias–Dalmau). Width lower bounds for Tseitin formulas come from
  expansion or treewidth (Ben-Sasson–Wigderson; Galesi–Talebanfard–Torán).
- **Grid principles.** Size lower bounds for grid matching and Tseitin use tiling games (Dantchev–Riis 2001; Alekhnovich 2004).
- **2D Sperner.** Tree-like resolution needs size 2^Θ(n) (Itsykson–Malova–Oparin–Sokolov 2014), and finding a solution needs Θ(√N)
  queries (Crescenzi–Silvestri; Friedl–Ivanyos–Santha–Verhoeven).
- **Classification.** new as far as found for these formulas.
  - **The delta.** A density argument for a height principle with a vortex. Any obstruction to moving the vortex is a closed walk with
    a bounded number of steps per pebble, so pebbles can trap only an area quadratic in their number.
  - **The tools are standard:** difference constraints (McShane extension, Bellman–Ford), the Vitali covering lemma and discrete
    isoperimetry.

## Setting

**Label states** (`FLAT-STATES-20261107-001A`).
- **Frames.** Fix a vortex point z (not on a corner face). Cut the sphere along six disjoint paths from z to the corners and develop
  frames (sublattice and sign gauge) over the rest.
- **Shifts.** For a line l and two of its points a, b ≠ z, let t(a, b) ∈ {−1, 0, 1} be the label shift between b's developed frame and
  b's frame seen from a through l. The shift is 0 off the cut and ±1 across it.
- **Label states.** A label state with vortex z is an integer function L on the points other than z, with |L(b) + t(a, b) − L(a)| ≤ 1
  for all such l, a, b. A line through z still binds its other two points.
- **Colours.** Colour each point by S_{L mod 6}[σ] ⊕ g. Every line not through z sees labels within two consecutive values, so it is
  not-all-equal (`SPHERE-COUNT-20261106-001A` lemma 1).
- **The vortex.** The shifts around z's six neighbours add up to 6, so they read 0..5 in order and exactly one line through z is
  violated (lemma 2).
- **In short,** a label state is a single-defect state with its defect at z.

**Weights.** Define the directed weight w(a → b) = 1 − t(a, b) ∈ {0, 1, 2}; it is the most L can rise from a to b. Let d_z(p, q) be the
shortest-path distance for these weights. For a path β, d(β) = ℓ(β) − H(β), where ℓ is its length and H(β) the sum of its shifts. A
closed walk B has H(B) equal to its label holonomy: 6 times its winding around z minus its windings around the six corners.

**Pebbles.** A pebbled colour at p allows exactly three consecutive labels, a_p, a_p + 1, a_p + 2 (mod 6).

## Lemma 1 (window criterion)

Pebbled colours admit a label state with vortex z iff the integer system

  s_q − s_p ≤ ⌊(d_z(p, q) + a_p + 2 − a_q)/6⌋   (all pebbles p ≠ q)

has no negative cycle. When it has none, the largest L with L(p) ≤ a_p + 6s_p + 2 is a label state matching every pebble.

*Proof.*
- **Without pebbles.** The system has no negative cycle, because flat states exist.
- **Fixed sheets.** Fix the pebbles' sheets s_p, so each pebble's label lies in the interval [a_p + 6s_p, a_p + 6s_p + 2]. A
  difference system with interval bounds is feasible iff every pair of bounds is compatible, lo_q − hi_p ≤ d_z(p, q) (McShane). The
  largest solution is L(v) = min_p (hi_p + d_z(p, v)).
- **Sheets.** Compatibility is exactly the displayed inequality. An integer difference system is feasible iff it has no negative
  cycle (Bellman–Ford). ∎

Check 1: the criterion agrees with a solver in 216 of 216 cases, and every feasible case realizes a valid state.

## Lemma 2 (certificates)

Suppose the pebbles admit a state at z but not at z′. Then there are distinct pebbles p_1, …, p_r and d_{z′}-shortest paths
β_i from p_i to p_{i+1} whose concatenation B satisfies:
- (a) ℓ(B) ≤ 3r − 6 + H_{z′}(B);
- (b) B passes through z, or winds differently around z and z′.

*Proof.*
- **The negative cycle.** Take a negative cycle at z′ (lemma 1), with each bound attained by a shortest path β_i. Its sum
  Σ⌊(d_i + a_i + 2 − a_{i+1})/6⌋ is at most −1. Since ⌊x⌋ ≥ x − 5/6 on sixths and the a_i telescope, Σ d_i ≤ 3r − 6. As
  d(β) = ℓ(β) − H(β), this gives (a).
- **One trivialization.** For (b), use one trivialization for both positions: z's cut star, plus a dual path π from z′ to z carrying
  shift 6. Then the arc starts a_p agree. A path avoiding z has d_{z′}(β) = d_z(β) + 6κ(β), where κ counts signed crossings with π.
- **The windings differ.** So each bound at z′ exceeds the same path's bound at z by exactly κ(β_i). If B avoids z, then
  Σ κ(β_i) ≤ (sum at z′) − (sum at z) ≤ −1 − 0. And Σ κ(β_i) is B's winding around z′ minus its winding around z. ∎

Check 2: 190 certificates on K_5, K_6, K_7 all satisfy (a) and (b); the largest ℓ(B)/r is 5.5.

## Lemma 3 (the walk is short)

**Statement.** Taking each β_i shortest for d and then for length, ℓ(B) ≤ 27r.

*Proof (sketch for the winding bound).*
- **No closed loops.** A closed sub-walk has d ≥ 0 (no negative cycles), so cutting it out never raises d and shortens the path. Each
  β_i is therefore simple.
- **No spirals.** A simple path could still spiral, but a turn around the vortex at distance ρ ≥ 2 costs at least 6ρ − 6 > 0 more in d
  than the radial shortcut. A turn around a corner costs at least 4ρ − 1 > 0.
- **Windings.** So each β_i winds less than twice around each charge, and |wind(B, y)| ≤ 2r for the vortex and every corner.
- **Holonomy.** Then |H(B)| ≤ 6·2r + 6·2r = 24r, and (a) gives ℓ(B) ≤ 27r. ∎

## Lemma 4 (density)

**Isoperimetry (sketch).** The point graph of K_k satisfies |∂U| ≥ c_iso·√|U| for |U| ≤ n/2. Radial projection to the round sphere is
bi-Lipschitz, the lattice discretizes it uniformly, and a ball of radius ρ ≤ k holds Θ(ρ²) points.

**Consequences.** Let B be a closed walk of length L ≤ εk. The winding number of B is constant off B.
- (i) **One generic class.** All its level sets except one, the generic one, hold at most C₁L² points in total: each has boundary
  inside B, and the boundaries add up to at most 2L.
- (ii) **Nearby.** A point x with non-generic winding has the ball around x, of radius dist(x, B) − 1, inside a non-generic class.
  Hence dist(x, B) ≤ C·L. Every point of B is within L/2 of every other, so x is within C₂L of all of B. The same holds for points
  on B.

**The bad set.** For a pebble set P, let D(P) be the set of points x with at least s/(27C₂) pebbles within distance s, for some
s ≥ 1. It contains every point within distance 27C₂ of a pebble.

**Transfer.** Let z, z′ ∉ D(P), with P of size w ≤ εk/27. Suppose the pebbles admit a state at z but not at z′.
- **The walk.** Lemmas 2 and 3 give B through r ≤ w pebbles with L = ℓ(B) ≤ 27r ≤ εk.
- **One position is bad.** B passes through z, or winds differently around z and z′. Either way one of them lies on B or has
  non-generic winding. So it is within 27C₂·r of all r pebbles of B, and lies in D(P).
- **Contradiction.** Both were chosen outside D(P). ∎

**Size of the bad set (Vitali).**
- **Covering.** Cover D(P) by balls B(x, s_x) with |P ∩ B(x, s_x)| ≥ s_x/(27C₂). Choose disjoint ones B(x_i, s_i) whose triples cover.
- **Count.** Σ s_i ≤ 27C₂·w, and |D(P)| ≤ Σ|B(x_i, 3s_i)| ≤ 63(Σ s_i)² = O(w²).
- **Room left.** For w ≤ c·k with c small enough, D(P) together with the twelve corner points covers less than the whole sphere.

## The game

**Duplicator's family.** Let 𝓗 be the set of partial assignments f to at most w points that agree with some label state whose vortex
lies outside D(dom f) and off the corner faces.
- **No falsified clause.** Each such state violates only one line, at its vortex, and the vortex is unpebbled.
- **Restriction.** D(dom f′) ⊆ D(dom f) whenever dom f′ ⊆ dom f, so 𝓗 is closed under restriction.
- **Extension.** Given f ∈ 𝓗 with fewer than w points and a new point q, pick z′ ∉ D(dom f ∪ {q}) off the corners. Both the old vortex
  and z′ lie outside D(dom f), so the pebbles of f admit a state at z′ by the transfer argument. Extend f by that state's colour at q.

**Width.** By Atserias–Dalmau, refutations need width at least w − 1 = Ω(k). ∎

**Upper bound.** The primal graph is planar with treewidth O(k). Davis–Putnam elimination along a tree decomposition refutes in width
O(k).

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Window criterion vs solver, K_4..K_6 | 216 of 216 agree; every feasible case realizes a valid single-defect state |
| 2 | Certificates, K_5..K_7 | 190 of 190 satisfy ℓ ≤ 3r − 6 + H and separate (or pass through z); max ℓ/r = 5.5 |
| 3 | Simulated game (illustration), K_6, K_8 | density Duplicator survives chaser and ring Spoilers with up to 12 pebbles |

## What this does not establish

- **Size.** Resolution size is not addressed. Width Ω(√n) on n variables gives no size bound.
- **Constants.** The constants are not optimized. Lemma 3's winding bound and lemma 4's isoperimetric constant are by sketch.
- **Grid Sperner.** The disk is `SPHERE-WIDTH-20261107-001B`. There the fixed boundary is free for Spoiler, so walks through it are
  not short.
