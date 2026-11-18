<!-- modelUsage: claude-fable-5-2 -->

**Your reading is wrong: this is not {5,4}.** The growth rate is the root of x⁶ = x + 1 (≈ 1.135 per round), and the cube dimension is unbounded. I derived the structure below by hand and checked its count against your sequence at t = 0–3, 6, 7, 8, 12, 13; I did not run anything.

## 1. The structure

Write the plain cylinder in quadrant coordinates v = (a, b), with round h(v) = a + b, parents (a−1, b) and (a, b−1), and (a, b) ~ (a+5, b−5). Unroll it, so the five-place knot has lifts p_k = (5k, −5k), k ∈ ℤ.

- **Junctions.** Pairs (v, S), where S is any finite set of lifts of the five-place knot lying below v (p_k ≤ v coordinatewise), taken modulo the ring shift. Round = h(v) + |S|.
- **Lifts below v.** m(v) = ⌊a/5⌋ + ⌊b/5⌋ + 1, or 0 if v is not above the knot.
- **Parents of (v, S).** (v, S∖{k}) for each k ∈ S, plus (v − e_a, S) and (v − e_b, S) where S is still below.
- **Demand.** 2 + m(v) − |S|.

The offshoot is one extra direction that commutes with everything, available on the cone above the five-place knot. The cone's two ends meet at round 5 at one cylinder junction X, but their offshoot copies have no common neighbour. So X gets two copies in round 6 (hence 11), and they pair to give (X, {0, 1}) in round 7 (hence 13). Each lap adds one more independent direction over every junction.

So the object is the cylinder times a cube whose dimension grows by one per lap, a two-dimensional base carrying about t/6 extra commuting directions.

## 2. Proof strategy

**Count.** c(t) = Σ_v C(m(v), t − h(v)) over cylinder junctions v. Raising b by 5 raises m by exactly 1, so Pascal's rule C(m+1, s) = C(m, s) + C(m, s−1) is the recurrence: a lap costs 5 without the new direction and 6 with it. That is your compositions into 5s and 6s.

**Induction on rounds**, with the claim that rounds ≤ t equal the (v, S) complex:

1. **No surplus.** Demand always meets the minima, so the offshoot is the only leftover ever made. This is a one-line check from the demand formula.
2. **Candidates.** Two round-t junctions are candidates iff they are u + x and u + y for a common lower u and distinct directions x, y ∈ {a, b, e_k}.
3. **Groups.** A set of pairwise candidates with no common neighbour is exactly the parent set of one (v, S) with at least 3 parents; the remaining pairs are 2-parent junctions. This is the real lemma. Prove it in the unrolled complex, where it is a statement about a product of the quadrant with a cube.
4. **Descent to the ring.** Such a set spans a loop of length at most 6, and the shortest loop around the ring has length 10, so it lifts.

**Checks to compute first:**
- the full formula against all 41 terms;
- parent and demand histograms per round;
- first 6-parent junction at round 21 (v = (11, 6), |S| = 4);
- first demand 7 at round 20 (v = (10, 10), S = ∅).

If the last two disagree with your data, my model is off somewhere.

## 3. Predictions

Step 4 needs the loop around the ring to be longer than 6, which splits the cases:

| Ring | Prediction |
|---|---|
| n = 7 | c(t) = c(t−7) + c(t−8), rate ≈ 1.097 |
| n = 8 | Splits into two interleaved cylinders of period 4. The offshoot lives on one; the other stays inert with 4 per round. So c − 4 satisfies g(t) = g(t−4) + g(t−5), rate ≈ 1.167 |
| n = 6 | No prediction. Period 3 means R0, R2, R4 are pairwise candidates with no common neighbour, so a group wraps the ring and even the plain ring is not a cylinder |
| n = 4 | No prediction. R0 and R2 share two neighbours, so it is degenerate |

For j extra loose bits on a clean ring of period n, in any positions (a six-place knot counts as 2), all directions commute and m rises by j per lap. Then c(t) = Σ_i C(j, i) c(t − n − i) after an initial transient, with rate the root of x^(n+j) = (1 + x)^j. For n = 5 that is about 1.26 for j = 2 and about 1.38 for j = 3.

## 4. Plain words

On a chain the offshoot's sheet is one copy of the cone above the five-place knot: it never meets itself, and growth is linear. On a ring the sheet comes back over its own origin once per lap. Each return is a new independent direction rather than a re-identification, and wherever k turns overlap the completion fills in all 2^k combinations.

- **"Folded, overlapping":** yes, literally. It is the unrolled cone wound over the ring.
- **"Logic-based fractal":** only in the sense that the counts are diagonal sums of Pascal's triangle wound round the ring. There is no scale self-similarity, and I would not call it a fractal.