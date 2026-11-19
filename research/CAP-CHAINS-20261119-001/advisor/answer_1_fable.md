# Advisor answer (CAP-CHAINS, before the freeze)

Claim 1 holds as a statement about rays, and Claims 2 and 3 are in the class with your d and p values. The headline does not hold as worded, because cap 5 admits all-live cyclic starts that your own cycle rule calls exponential.

## 1. Claim 1

The proof is right as a count of rays per piece, with three things to fix.

- **Step 1 misses the 6-cycle.** Girth ≥ 5 still allows a 6-cycle a‑x‑b‑y‑c‑z, where {a, b, c} are pairwise candidates with no common neighbour (one would make a 4-cycle). S3 excludes it, so "groups are exactly the pairs" is S3 itself, not a consequence of girth. State it as: K̄ has no 3-, 4- or 6-cycle. The formula for d_k is right.
- **Step 3 is right.** I rechecked each case:
  - d = 0 forces a star centre, either end of a single edge (n = 2), or a lone knot (open ≥ 3, no rays). Each is an isolated point with at most two rays.
  - d = 1 occurs only at a core end or its single leaf, at most one per parity class per end, each with exactly one ray.
  - The path of three and the double star both come out at two rays per piece.
  - Multiplicities only raise sh, so they help.
- **The relay is not accounted for.** A tree has two pieces, so relay points appear. If "finite piece" means a piece with no rays, the bound of two survives. If a piece with one ray can also receive a relay, it reaches three. I cannot tell which from your text, so pin the definition down.

"All live" is a hypothesis on the start only. I take it the refereed growth theorem does not need liveness to persist.

## 2. Claims 2 and 3

**Claim 2** checks out: branch knot d = 3, p = 6; connector d = 4, p = 6; a has d = 2, p = 4; leaf has d = 1, open 2, one ray. S3 and S4 hold because K̄ is an all-live tree, where three knots pairwise at distance 2 share their median.

- "Branch knots at mutual distance 2" is impossible for three or more, since it would need a degree-3 connector. Say "neighbouring branch knots at distance 2". With b branch knots, R = b + 2.
- The other parity class (connectors and a's) has s = 0 everywhere, so under the ray-free reading of "finite" it gets the relay and is a two-ray piece.

**Claim 3** checks out:

- M has d = 3, p = 5, open 3, no rays.
- X has d = 0 because H is dead and so not a candidate. N(M) ∩ live = {X} is not a block, so X is isolated with two rays.
- K has d = 1 and one ray.
- The blocks N(H) and N(X) = {M, K or M′} tie all M and K into one piece.
- No S3 or S4 failure: K̄ is a tree, and each triple of members has H as common neighbour.

Depth 2 has 31 knots (4 H, 12 M, 9 X, 6 K) and 6 rays. The one assumption is that the refereed tree theorem covers dead knots.

## 3. Predictions

I can predict degrees only, from the tree theorem. I cannot give coefficients without the ray growth rule.

| Start | Rays in largest piece | Degree of per-round count |
|---|---|---|
| Claim 2, R = 3 (7 knots) | 3 | 2 |
| Claim 2, R = 4 (11 knots) | 4 | 3 |
| Claim 2, R = 6 (17 knots) | 6 | 5 |
| Claim 3, depth 1 (10 knots) | 3 | 2 |
| Claim 3, depth 2 (31 knots) | 6 | 5 |

Expect linear side terms from the two-ray pieces: the relay piece in Claim 2, and the three or nine X pieces in Claim 3. Fit only after the early rounds settle.

## 4. Headline

It is not right as worded. Claim 1 bounds rays, and that gives a dimension only for trees. Cap 5 admits all-live cyclic starts:

- A cycle core needs ℓ_k + ℓ_a + ℓ_b ≤ 1 for every three consecutive core knots (ℓ = number of leaves). So bare C5, C7, C8 and longer are in the class, and so is C7 with one leaf.
- C7 with one leaf has p = 5 at the leaf's knot and its two neighbours, and the leaf has d = 2, p = 3. X⁺ is one piece: a 7-cycle plus a three-point block. That is not a bare cycle, so by your computed rule it grows exponentially.
- Even cycles split into two cycle pieces, each of which gets a relay. Whether that still counts as "bare" is unclear.

A safer headline: "for all-live tree starts, five is the largest cap that bounds the dimension, and the bound is two; at cap 5 cyclic starts have no rays, and their growth is decided by the cycle rule."

To break it, grow these first:

1. C7 with one leaf at cap 5.
2. Bare C8, for the relay on a cycle piece.
3. A tree with a one-ray piece, to see whether a relay ever joins it.
