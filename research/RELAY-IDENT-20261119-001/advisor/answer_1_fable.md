**Verdict:** the argument is sound as far as this text lets me check, with four places to fix before freezing. I have no access to the rule's text or CHAIN-IDENT's proof, so everything below rests on your summary.

## 1. Step by step

**Step 1 (pieces don't interact):** fine.

**Step 2 (before the top):** fine, on two conditions.
- CHAIN-IDENT's proof must use (S5⁺) only through "∂C ≠ ∅, hence not implied". Please confirm this against the proof itself.
- For q = 1 you also need that no junction before the top is implied. This holds: a second cluster C′ of the same size has at least two parents, at most one of which lies inside C, and the other holds a loose distinction because it is a proper cluster.

**Step 3 (the implied test):** the conclusion is right, but the case list has a hole and the induction is on the wrong thing.
- **The hole:** a piece that finished at round r − 1 has only its top in the latest round, and the top holds 1 loose distinction, not 2. "J's always hold 2" does not cover it.
- **The fix:** induct on rounds over all pieces at once, with one invariant: *if q ≥ 2, at every round each piece's latest-round junctions hold at least one loose distinction.* The latest-round junctions are proper clusters (∂ ≠ ∅), a top (1), or J's (2 each).
- **What it gives:** a junction's parents lie in its own piece, so nothing is ever implied when q ≥ 2. That covers same-round finishing (each top sees the other's round-(r − 1) parents) and a top forming while another relay runs. It also covers the relay J(0,0) at round r + 1, which takes *all* of Y's loose distinctions and so needs the other piece's round-r junctions.
- **Assumption to write down:** a round-t junction's loose distinctions are all taken at round t + 1 (every x ∈ ∂C gives a child). Without it, q = 1 does not give "implied".

**Step 4 (after the top):** correct.
- J(i, l) has parents J(i − 1, l) and J(i, l − 1), so two J's of one round share a parent iff |i − i′| = 1. The candidate graph is a path, which has no three pairwise candidates.
- The unions are right: J(i, l) ∪ J(i + 1, l − 1) = J(i + 1, l).
- The fresh formula as written, max(0, 3 − p, 1), gives 1 for a group with p = 2, yet you say groups get 2. The third term must be max(d, 1) or similar. Write the formula once with d in it.

**Three gaps in the statement itself:**
1. **q must count deck orbits of pieces.** A finite tree piece has trivial stabiliser, so under a nontrivial deck group it has many translates that are one junction family. If its orbit is the only one, the top is implied and the growth closes. Your examples all appear to have K a tree, so they don't test this. Test a K with a cycle and a finite ray-free piece.
2. **|Y| = 1.** Then r = 0, the "top" is the knot itself and p = 0, so "p ≥ 2" fails. Exclude it or treat it separately.
3. **Loose distinctions outside the live pieces.** With the floor allowed, q = 1 gives "implied" only if no loose distinction sits on the floor or on non-live knots at round r − 1. State this or prove it.

## 2. The single statement

The statement is right in content, but "z enters only with all of Y" is an extra rule, not a cluster property. A cleaner form applies the pendant rule to the top as if it were a knot:

> A finished piece's top has open = 1 and d = 0, so it carries s = 1 pendant point with R(1) = 2 rays.

This gives the same z, makes "a relay feeds two chains" exact, and extends loose = |∂C| uniformly: ∂Y = {z}, and every J(i, l) has |∂| = 2.

**Dimension.** "Adds 2 to its piece's chain count" is true only because that count was 0. The relay's rays never combine with another piece's chains. The extension I would write is:

> Dimension = max over piece orbits of the chain count, where a finite ray-free piece counts 2 if q ≥ 2 and the growth closes if q = 1.

So a relay matters for dimension only when every other piece has at most 2 chains.

## 3. Predictions

These rest on a model I inferred from your path of five: the junctions of a piece at round t are the clusters of t + 1 points that meet its live core. That reproduces your {A, C, E} count (t + 3). The spider also assumes (S3) and (S4) hold at a centre of degree 4.

**Path of seven.**
- {A, C, E, G} with two chains gives t + 4 per round.
- {B, D, F} gives 3, 2, 1 (top at round 2), then t − 2.
- Per round: 7, 7, 7, 8, 10, 12, …, which is 2t + 2 for t ≥ 3, the same tail as the path of five.
- Dimension is unchanged: two chains in each piece, linear rounds.

**Spider with legs 2, 2, 2, 2.**
- The four middle knots form a finite piece of 4 points with clusters 4, 6, 4, 1. Its top is at round 3 with p = 4 and gets 1 fresh distinction, then t − 3 junctions per round.
- The centre plus four tips has four chains: C(t + 3, 3) + 4 per round.
- Per round: 9, 14, 18, 25, 40, 62, …, which is C(t + 3, 3) + t + 1 for t ≥ 4.
- Dimension is 4 chains (cubic rounds); the relay adds only a linear term.

**Calibration.** The same model gives 7, 9, 10, 14, 20, … for your spider with three legs of two, which is C(t + 2, 2) + t + 1 for t ≥ 3. If the machine disagrees there, my reading of the pieces is off and both predictions need redoing.