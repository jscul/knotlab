<!-- modelUsage: claude-fable-5-2 -->

**Caveat first:** answer 1 and the definitions of the (v, S) model and the menus are not in this thread, and I ran nothing. Everything below comes from your tables by hand arithmetic. I have no exact model for question 1, and I did not invent one.

## 1. No exact model, but the data constrain its type

**The exponent is −3/2 in all five joins.** Fix α = −3/2 and estimate λ_t = (c_t/c_{t−1})·(t/(t−1))^{3/2}. The last three or four estimates then settle:

| Join | λ_t, successive rounds | λ, α fixed at −3/2 | Your free fit |
| --- | --- | --- | --- |
| 5–5 shared bit | 2.5370, 2.5342, 2.5326, 2.5325 | ≈ 2.53 | 2.49 |
| 5–5 shared knot | 2.7793, 2.7824, 2.7852 | ≈ 2.79 | 2.77 |
| 5–5 path of one | 2.3600, 2.3599, 2.3608 | ≈ 2.36 | 2.30 |
| 5–7 shared bit | 2.3265, 2.3253, 2.3242 | ≈ 2.32 | 2.27 |
| 5–9 shared bit | 2.1985, 2.1957, 2.1945 | ≈ 2.19 | 2.13 |

Your fitted α running from −1.08 to −1.46 is what a true −3/2 looks like at 14–17 rounds; it is furthest off where the transient (n + j) is longest.

**What this rules out.** Any finite linear system has a rational generating function, so its counts go as λ^t·t^k with k a whole number ≥ 0. That covers the (v, S) model with fixed menus and a product of the two rings' positions with finitely many lifts. So my answer to "is the cross region a product of positions with lifts" is no, not a finite one. A rational series with close competing roots can mimic a negative α over 16 terms, so this is strong evidence, not proof.

**What it points to.** A stable −3/2 is the mark of a square-root singularity, which is an algebraic, non-rational series. That needs your nested law's product with the nesting closed on itself. On a tree the nesting ends, so the series is rational. With two rings, a lap of ring 1 through the joint spawns ring-2 laps, and those pass the joint and spawn ring-1 laps. The template I would fit is:

- A = 1 + y^a·P₁(y)·A·B
- B = 1 + y^b·P₂(y)·A·B

Here A and B are the series of a ring-1 and a ring-2 lap started at the joint, and P₁, P₂ are small polynomials from the bare sizes. I cannot derive P₁, P₂ from here. It also explains "no recurrence of order ≤ 7": the right recurrence has polynomial coefficients in t.

**How to get the system from data.**
- Record per-junction series at the joint (the F's of the nested law), not totals. Totals carry delays y^n, so a guessed equation needs degree about n + 2 and more than 16 terms.
- Guess a quadratic relation Q₂(y)F² + Q₁(y)F + Q₀(y) = 0 on those series, holding back at least five terms as a check.

**The state space I would use is the candidate graph** (knots two apart), not a product of positions. For the shared-bit join it is the two 5-cycles plus two sunflower triples, {0′, 1, 4} through knot 0 and {0, 1′, 4′} through knot 0′. A single odd ring has one independent cycle there; this graph has five (10 knots, 14 links). Both triples are live from round 1, which is where I would look for the doubling.

## 2. Falsifiable predictions

**Next counts**, assuming α = −3/2 (tolerance about 0.2%):

| Join | Round | Predicted count |
| --- | --- | --- |
| 5–5 shared bit | 16 | ≈ 822,800 |
| 5–5 path of one | 16 | ≈ 319,300 |
| 5–7 shared bit | 16 | ≈ 303,800 |
| 5–9 shared bit | 17 | ≈ 344,800 |
| 5–5 shared knot | 14 | ≈ 484,300 |

A miss beyond about 0.5% refutes the −3/2 reading.

**Unseen joins** (extrapolation, less sure):
- **7–7 shared bit:** λ between 2.10 and 2.16, below 5–9, with α = −3/2.
- **5–5 through a path of two:** λ between 2.20 and 2.28, giving the order shared knot > bit > path of one > path of two.
- **Limit in ring size:** the 5–n rates (2.53, 2.32, 2.19) have shrinking gaps that suggest a limit near 2, not 1. This rests on three points; 5–11 and 5–13 would test it.

**Closing rule.** A start closes, at least in part, exactly when its candidate graph has three pairwise candidates with no common neighbour. In knot terms that is a 3-cycle or a 6-cycle of knots (alternate knots of a six-ring). This matches your 0–1 closing case and the ring of eight splitting into two fours. The test is two 5-rings sharing two consecutive bonds, whose outer cycle has six knots: it should close or contain a closed part. Sharing one bond (outer cycle of eight) should not.

## 3. The nested law

It looks right for chains, but I would not yet call it the law for trees.

**Why chains are safe.** "Candidate children" is well defined only where the candidate relation on the hanging piece is a forest. For a tree of knots that holds exactly when no knot has three neighbours. A chain meets this, and the law is then the standard product over a forest.

**Where it stops being defined.** At a knot with three neighbours, those neighbours are pairwise candidates through it, so "siblings multiply" treats mutually candidate knots as independent. In a tree every such triple has a common neighbour, so it is always the sunflower case. I therefore expect trees never to close and the law to survive in a corrected form. The correction should be the one the model already makes at r, where r−1, r+1 and K1 form the same triple.

**Trees most likely to break it:**
1. **A fork at K1:** r–K1, with K1–K2 and K1–K2′. K2, K2′ and r are pairwise candidates. The law gives F(r) containing F(K2)·F(K2′); I expect a deficit from the junction all three share.
2. **Chains of two or more at neighbouring ring knots r and r + 1.** K1 is a candidate of r + 1 and K1′ of r, so the two nestings interlock. Your "positions varied" checks were lone adjuncts, which don't test this.
3. **Chains at r and r + 2,** whose roots are candidates of each other through r + 1. This is milder.

I would run the fork first. Also compute the law's series for bare chains of five and six before running them, as you did for four.
