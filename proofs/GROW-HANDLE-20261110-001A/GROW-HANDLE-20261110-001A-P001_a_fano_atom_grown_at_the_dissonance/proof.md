# A Fano atom grown at a knot sphere's dissonance

Status: Proved by hand where marked (theorems 1, 3 and 4); theorem 2 and the costs are computed (`check.py` checks 3, 5 and 6, and the
stress test `research/GROW-HANDLE-20261110-001/stress_test.py`). Check 1 tests the builder on its own. Pre-registered in
`research/GROW-HANDLE-20261110-001/preregistration.md`.

## 1. The builder

`grow_lib.build` turns a rotation system of a two-coloured cubic graph (each vertex's three darts in cyclic order, and each dart's partner)
into a `surface_lib.Surface`: vertex v becomes a triangle whose side j is v's j-th dart. Tracing faces by d ↦ rot(partner(d)), the angle
of v between its darts j − 1 and j lies in the same face as the angle of the vertex across dart j between its darts j′ and j′ + 1, where
j′ is that dart's own position. So corner j + 1 of the triangle is glued to corner j′ + 2 across side j, and corner j + 2 to corner j′ + 1.
`rotation_of` reads an oriented surface back as a rotation system.

**Check 1 (computed).** Rebuilt from their own rotation systems, K_2, K_3, K_4, the Fano torus, a thin torus and torus(4, 2, 3) keep their
triangles, faces, line corners per face, Euler characteristic and orientability. Under the solver's Kasteleyn signing, K_2 keeps its
1,728 states violating one line, the Fano torus its 70, and the two other tori their 12 and 528 states violating one line; the three tori
keep their numbers of unsatisfiable classes (1, 1 and 0).

## 2. The growth move

The **atom** is the Fano torus (the Heawood map, `surface_lib.torus(7, 2, 1)`) less a point P\*, with all its signs 0: the Fano plane's
uniform law, which no state satisfies. **Splice** it at a line l of the octahedral knot sphere K_k: remove l and P\*, and join l's three
points to the three lines that went through P\* by a bijection σ, keeping both rotations (`grow_lib.splice`). The sphere's sides keep their
Kasteleyn signs, the atom's keep 0, and the three new sides take signs that leave no even face. The state x is a least state of the sphere
(one violated line l0, no over-agreement; `steer_lib.flat_state`), extended to the atom's six points by the first assignment that violates
the fewest lines, and then held fixed while learning acts (A26).

**Theorem 1 (the grown space; proved).**
1. For three of the six bijections the spliced map is a torus; for the other three it has genus 2.
2. On the torus the old signs extend to the new sides with no even face in exactly two ways, which differ by a gauge change.

*Proof.* The splice removes two vertices and three edges. When σ matches the cyclic order at l to the reversed order at P\*, the three
faces around l merge with the three around P\* in pairs, so F drops by 3 and χ = χ(K_k) + χ(Fano torus) − 2 = 2 + 0 − 2 = 0. For the other
three bijections the six faces merge into one, F drops by 5, and χ = −2. Every face away from the splice keeps its parity, which is odd on
both sides. The three merged faces have parities summing to |D| ≡ χ ≡ 0 mod 2, and each new side toggles the two merged faces at its ends,
so the three new bits fix all three parities in exactly two ways, which differ by flipping all three new sides. Those three sides are the
boundary of the sphere side (the sum of its triangles' sides counts every inner side twice), so flipping them is a gauge change. ∎

**Theorem 2 (the atom acts as the line it replaced; computed).** On every grown torus tested, in the grown law's class the atom allows on
l's three points exactly the six patterns that l allowed, and in each of the other three classes it allows all eight: it is transparent.
Checked on 288 grown tori from K_2 to K_4 (every line orbit, placements at distance 0 to 4, both chiralities, all three bijections that give
a torus) and 252 from K_5 (distance 0 to 5), by enumerating the atom's 64 assignments for each pattern. Not proved for every knot sphere.

**Theorem 3 (growth alone does not resolve; proved given theorem 2).** On such a grown torus the grown law is unsatisfiable and the only
unsatisfiable class.

*Proof.* By theorem 2, in the grown class the old points satisfy the grown law exactly when they satisfy the sphere's law, which no state
does (`COUNT-SURFACES-20261107-001A` theorem 3: a Kasteleyn sphere forces a violated line). In each other class the atom imposes nothing,
so the old points need only satisfy the sphere's law less l, which the flat state of `RESIGN-STEER-20261107-001A` theorem 2, violating
only l, does; the atom's points are then completed. ∎

So growth changes what forces the dissonance: on the sphere the count forces it; on the grown torus the class does.

**Theorem 4 (learning then resolves it, through the new handle; proved).** On a grown torus, from any state with one violated line, learning
at the dissonance with the state fixed resolves the dissonance, leaving no even face, and every process that resolves it changes a sign in
the atom or on the three new sides.

*Proof.* The grown law is a Kasteleyn law on a torus in a class no state satisfies, and another class is satisfiable (theorem 3), so
`LEARN-HANDLES-20261109-001` theorem 3 applies: learning resolves the pair, and every resolution changes the law by a cycle of nonzero
homology class. A cycle whose sides all lie on the sphere side lies in a disc, so it is a boundary. Hence the change meets the atom or the
new sides. ∎

## 3. Computations

- **The extended state (checks 4 and 5).** On all 288 grown tori, and on the 252 of K_5, the extension violates exactly one line. Grown at
  the dissonance (l = l0), that line lies inside the atom (60 of 60, and every K_5 case): the dissonance moves into the handle it grew.
  Grown elsewhere, it stays at l0 (228 of 228).
- **Walks (check 4).** From every extended state, each of its three splits and each of the three other classes, the cheapest perfect
  matching was reached by a resolving walk, replayed as learning steps at the dissonance, winding and changing a sign in the atom: 2,592
  walks.
- **Cost by placement (check 5; stress test).** The cheapest resolving walk costs 3 sign changes when the atom is grown at the
  dissonance, on K_2, K_3, K_4 and K_5 alike. Grown at line distance d from it, it costs more and grows with d: on K_4 from 7 to 8 at
  d = 1 to 10 to 14 at d = 4, on K_5 a mean of 5.7 at d = 1 rising to 15.6 at d = 5 (minima are not monotone in d; on K_4 the minimum at
  d = 2 is 6, below 7 at d = 1).
- **Rules (check 6).** From one seeded split of each of the 288 starts, random moves (R0), sight of radius 3 (R3) and the outside distance
  (R7) all resolved, with mean steps 259, 24.5 and 13.7; grown at the dissonance 95.8, 2.4 and 3.1.

## 4. Against the pre-registration

H1 held. H2 held in its main claim, growth alone does not resolve and exactly one class is unsatisfiable, but its mechanism was wrong: the
pre-registration expected the other three classes to act as the replaced line re-signed; instead the atom is transparent in them. H3 held.
H4 held: the cost at the dissonance is a constant, 3, and grows with distance away from it (as a trend; minima are not monotone). H5 held.

## 5. Scope and novelty

- **Scope.** The octahedral knot spheres K_2 to K_5 with their Kasteleyn law, one Fano atom with uniform signs (A48), the learner of A26.
  Theorem 2 is computed on these spheres only.
- **Novelty: known-with-delta.** The splice and its genus are `THREEFOLD-SURFACES-20261030-001`; a Fano atom acting as one line from
  outside echoes `FAR-READ-20261106-001` and `ATOM-ONE-20261107-001` in the creation reading. New here: the transparency of the atom in the
  other classes, growth turning a count-forced dissonance into a class-forced one, and learning removing it through the grown handle,
  cheapest when the handle is grown at the dissonance.
