**Verdict:** the claims hold on my reading, with one wording error in the headline ("rational rate") and one unexplained residue in the theta's round-0 count. Your theta system reproduces the engine exactly for rounds 1–11.

I read a block as N(w) ∩ live, one per centre knot w, with w not in its own block. Say if that is wrong, because questions 1 and 3 depend on it.

## 1. The claims

- **Profile bound: right.** Distinct blocks of size ≥ 2 through k have distinct centres, and by (S4) two centres cannot give the same block. So deg_k ≥ number of blocks through k. A dead neighbour whose block is just {k} only raises deg_k, which strengthens the bound. Index blocks by centre, not by set, or "two blocks share two points" misses the equal-set case.
- **S3 ⟺ no cycle of three blocks under S4: right, with your point-based definition.**
  - A valid set of four or more contains a valid triple, because two triples with different common neighbours would break (S4).
  - A valid triple's three blocks are distinct, since a shared block's centre would be a common neighbour.
  - Conversely, a common neighbour of three points pairwise in different blocks would force all three blocks equal, by (S4).
  - Three blocks through one point form a triangle in Γ but not a valid triple. Only the profile bound excludes that, so define the cycle by points, as you did.
- **Pointing: right, but it needs a torsion-free deck group, not only a free action.** An element stabilising a finite cluster has a power fixing a point. Freeness makes that power trivial, and torsion-freeness then makes the element trivial. This holds for the universal cover (free deck group) and fails for a finite cyclic cover.
- **Blocks must stay whole in the cover.** The formula treats a 3-block as one unit, not as a cycle of three candidate pairs to unwrap. So "rank" means the rank of Γ.
- **Not checked.** I cannot verify claim 2's ray rule (why open is exactly 2) or the rank-0 dimension convention from this text.

## 2. Rank ≥ 2 and the theta

**The equation is right.** The discriminant is 1 − 4z² − 4z³, so ρ ≈ 0.41964 and the rate is ≈ 2.383. I expanded a·b by hand and took 6·[z^t](ab)/(t+1) for the main piece:

| Round | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Main piece | 6 | 9 | 14 | 24 | 42 | 77 | 144 | 276 | 538 | 1,065 | 2,136 | 4,332 | 8,874 | 18,336 |
| Engine − main | 5 | 3 | 6 | 9 | 12 | 15 | 18 | 21 | 24 | 27 | 30 | 33 | | |

- **The residue is 3t for rounds 1–11.** That is the three connectors as lone relayed points (m = 1, k junctions at round k).
- **Predictions:** round 12 = 8,874 + 36 = **8,910**; round 13 = 18,336 + 39 = **18,375**.
- **The limit is 2.383**, approached slowly from below. Orbit counts go like ρ^{−t} t^{−5/2}, and the predicted ratios are still 2.04 and 2.06.
- **Round 0 is unexplained.** The residue is 5, where three connectors give 3. The extra 2 equals the number of dead hubs. Check whether the engine counts dead knots at round 0 or the relay has a round-0 convention.

**Strong connectivity fails in general, harmlessly.** Incidences pointing into hanging trees are polynomial. Incidences pointing from trees into the core depend on the core, but nothing depends on them. The core itself is strongly connected: non-backtracking walks on a connected graph with minimum degree ≥ 2 that is not a cycle. It is nonlinear, because a core branch is a 3-block whose incidence is a product of two core unknowns. So DLW applies to the core and the rest inherits ρ.

Two caveats:
- **Periodicity.** If the core is periodic there are several singularities on |z| = ρ. The rate stands, but ratios can oscillate, so state growth along residue classes.
- **Pendant factors.** With 1/(1 − z) factors the system is analytic rather than polynomial. That is fine, since ρ < 1.

## 3. Fewer than 11 knots, and dead knots

**Fewer than 11: I believe not.**
- Branch vertices of Γ are 3-blocks of degree ≤ 3, so there is no figure-eight.
- With girth ≥ 4 and no adjacent 3-blocks, the smallest rank-2 core is your theta: 5 blocks and 6 points. A dumbbell needs at least 9 blocks.
- Every point has profile {2,3}, so d = 3 and deg is exactly 2. No point can be a centre.
- So the 5 centres are distinct from the 6 points, giving 11.

I am unsure only if two knots may share more than one place.

**Dead knots: needed.** Take a core branch 3-block with a live centre w and three live connector centres. Then w has deg ≥ 3 and d ≥ 3, which is 6 places. So the hub or one of its three connectors must be dead. A live hub with one dead connector is a hybrid that pulls the hub into the piece and changes Γ. It is worth one engine run.

## 4. Headline

It is right with two fixes:
- **"Rational rate" is wrong.** The series is rational; the rate is an algebraic number, the root of W(1/x) = 1 (the golden ratio, for example).
- **Rank 1 is constant only when the cycle is bare** (W = z^n). One spare on a cycle point already makes it exponential.

Also say that the map's growth class is the largest over its pieces.

What I would check first to break it, in order:
1. The round-0 residue of 2.
2. A dumbbell, which tests the core argument where strong connectivity is least obvious.
3. A theta with a hanging tree or a rayed pendant, which tests the two-variable count where the 1/(t+1) pointing no longer applies.
4. A periodic core, for ratio oscillation.
5. The live-hub hybrid above.
