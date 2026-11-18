<!-- modelUsage: claude-fable-5-2 -->

# Advisor answer 1 (JOIN-GROWTH, before the freeze)

Everything below is hand derivation; I ran nothing. The main points:

- One rule fits every finite row: F is the rank series of the part's own "menu", and factors multiply.
- Your hanging-pair rows contradict the nested law F(node) = 1 + y Π F(children). They fit a product, plus a self-renewing floor bit in the bare case.
- One row is inconsistent with the others on whether the ring's surplus bit counts. Check that start before freezing.
- I have no working model for two rings. The one I tried is refuted by your data.

## 1. The lap equation

**Why a factor, and why position does not matter.** In the (v, S) model the count at round t is the number of pairs with h(v) + |S| = t. Each lap adds one new lift of the site, and each lift is independently in S or not. Summing over laps gives Σ_m y^(nm) (1 + y)^m = 1/(1 − y^n (1 + y)).

Replace "in S or not" by "choose one element of a ranked menu M at each lift, with ranks adding". The same sum gives 1/(1 − y^n F), where F is the rank series of M. Several sites give independent choices, so the factors multiply. Moving a site changes only how many lifts lie under each v in the first lap, which changes the numerator and not the denominator. That is why r, r + 1 and r + 2 agree.

**Why a bare lone knot is a surplus bit one round early.** The offshoot O of a surplus bit on r has one parent and demand 2, so it gets max(2, 2, 1) = 2 fresh bits. It is a three-bit knot touching r with two loose bits, which is literally the lone knot L.

- In the surplus start at round 1, O's candidates are the two new junctions adjacent to r, through r.
- In the lone start at round 0, L's candidates are r ± 1, through r.
- In both, the triple has r as a common neighbour, so it splits into pairs.

So the lone start is the surplus start's round-1 front. The one difference is that r is both the common neighbour and a live ring knot. The exact shift in your data says this costs nothing. I have only matched the candidate structure for one round; confirm it by an isomorphism of group structures, not counts.

**F = 1 + y(1 + y)^s is right, and here is the menu.** The s offshoots of L are pairwise candidates through L, so they join in pairs. Three pair-junctions {a,b}, {a,c}, {b,c} have no common neighbour and form one group. The menu is therefore: nothing, or L (rank 1) with any subset T of its surplus bits (rank 1 + |T|). That is the general form F = 1 + y · (series of what opens once the knot is taken).

**Your rows that only gave a factor.** Where BM returned x^5 − x^4 + x^2 − x − 1, the numerator cancelled x^2 + x + 1. Such rows confirm the rate, not the equation. Mark them so.

**The other finite parts (untested guesses).**

| Part | Prediction | Confidence |
| --- | --- | --- |
| Two lone knots on the same ring knot | F = (1 + y)^2, same as lone knot plus surplus bit on r, one round early | Medium |
| A knot sharing two bits with r | Same neighbour structure as a lone knot, so 1 + y if the start does not stall | Low |
| A knot touching two ring knots | Second cycle; I expect it to leave the rational class, as in section 3 | Low; exploratory |

## 2. The hanging pair

**The A: 1, B: 2 row is a product.** Multiply your two factors back together:

(x^2 + 1)(x^8 − x^6 + x^4 − x^3 − 3x^2 − 3x − 1) = x^10 − (x^2 + x + 1)(x^3 + x^2 + 2x + 1)

So the lap equation is y^5 · F_1 · F_2 = 1, with F_s = 1 + y(1 + y)^s. The x^2 + 1 is part of the lap polynomial and should not be discarded. Two consequences:

- **Not nested.** The nested law would give 1 + y(1 + y)F_2, which does not match. B acts as if attached to the ring directly. The likely reason is that r and B are candidates through A and join in round 1.
- **No factor for the ring's surplus bit.** The polynomial is not divisible by 1 + y. Every other row has that factor when r carries a surplus bit.

**The bare pair has a self-renewing floor bit.** (1 + y)/(1 − y) = F_A · F_B with F_A = 1 + y and F_B = 1 + y + y^2 + … . My reading:

- B has demand 1, so the floor gives it a loose bit.
- Its offshoot has one parent and demand 1 (it pairs with the r–B junction through B), so the floor gives it a loose bit too.
- This repeats every round. The menu is a chain: T = 1 + yT, so T = 1/(1 − y).

The x − 1 factor is this chain's constant contribution. Cheap test: log, each round, which junctions got bits from the floor and not from demand. The reading predicts exactly one per round in the bare pair and none in the A: 1, B: 2 row.

**The two unsettled rows.**

| Start | Predicted equation | Predicted rate | Your ratio |
| --- | --- | --- | --- |
| No ring surplus, A: 2, B: 2 | x^11 = (x^3 + x^2 + 2x + 1)^2 | 1.5135 | 1.512–1.517 |
| Ring surplus on r, A: 2, B: 2 | x^12 = (1 + x)(x^3 + x^2 + 2x + 1)^2 | (1 + √5)/2 = 1.6180 exactly | 1.613–1.626 |

The second polynomial is divisible by x^2 − x − 1. Orders 11 and 12 explain why BM found nothing at order ≤ 9. You can test both now by checking that the predicted recurrence annihilates the tail of the existing counts. That is a fit on seen data, not a frozen prediction.

**The inconsistency.** The A: 2, B: 2 rows need the factor 1 + y for the ring's surplus bit (1.618 against 1.5135). The A: 1, B: 2 row excludes it: with the factor the rate would be about 1.555, not 1.4506. One of three things is true:

- In the A: 1, B: 2 start, r's "surplus" bit was consumed by the demand B puts on r through A.
- The start differs from its description.
- One of my readings is a coincidence.

Print r's loose bits and groups in round 1 for both starts.

## 3. Two joined rings

**Exponent.** Your data cannot tell −1.35 from −3/2. With α = −3/2 and a shift, c(t)/c(t − 1) ≈ λ(1 − 1.5/(t + t0)) is flat for t0 ≈ 0.8. That gives λ ≈ 2.52 on rounds 11–15, against 2.51 for your free fit. I would state λ = 2.52 ± 0.02 and "consistent with t^(−3/2)". An algebraic series with a square-root branch point is what I expect, because with two independent cycles the menu of each ring contains the other.

**A model that fails.** I tried "F = series of rooted sub-trees of the unrolled start, one round per knot". With R the series along one ring from the join and U the series for entering a ring:

- R = (1 + y + y^2 + y^3 + y^4)/(1 − y^5 U)
- U = 1 + y R^2

The branch point is at (1 − y)^3 (1 + y + y^2 + y^3 + y^4) = 6.75 y^6, so λ ≈ 1.81. Your ratios already exceed 2.28, so this is refuted. A lap-limited model cannot reach 2.5 at n = 5; the counts double from round 1, so the branching is local to the join. I cannot predict λ.

**What I would do instead of guessing.** Classify junctions by a refined type: the multiset of parent types and group sizes, iterated until stable through round 12 or so.

- If the types close into a finite set with production rules, you have a rational or algebraic system you can iterate to hundreds of rounds.
- If the number of types grows with depth, that is itself evidence of a stack-like (algebraic) structure, and the nesting pattern will suggest the system.

## 4. What to freeze

**Sharp** (exact recurrences, disjoint from the data):

- Lone knot with s surplus bits on a ring of n: x^(n + s + 1) = x^(s + 1) + (1 + x)^s, for n = 6, 7, 8 and s = 1, 2, 3.
- Products on separate ring knots: y^n (1 + y)^j Π F_(s_i) = 1. Examples:
  - n = 5, s = (1, 1): x^9 = (x^2 + x + 1)^2, rate ≈ 1.382.
  - n = 6, s = (1, 2): x^11 = (x^2 + x + 1)(x^3 + x^2 + 2x + 1).
- Bare hanging pair on a ring of n = 6, 7: (x − 1)(x^(n + 1) − x^n − x − 1).

**Medium:**

- Two lone knots on one ring knot: x^(n + 2) = (1 + x)^2.
- Hanging pair with surplus a ≥ 1, b ≥ 2 and no ring surplus: x^(n + a + b + 2) = (x^(a + 1) + (1 + x)^a)(x^(b + 1) + (1 + x)^b). Try (1, 3), (2, 3), (3, 2).

**Risky** (run first, as discriminators):

- The ring-surplus factor beside a hanging pair. Run (1, 2) with the surplus on r, on r + 2, and absent.
- A chain of three, a knot sharing two bits with r, and a knot touching two ring knots.
- Two rings: freeze only "t^(−3/2) with a fitted shift" and "λ decreases as either ring lengthens". I have no numeric λ to offer.

## 5. Words

- **"Attached part":** "adjunct" is a grammar word with no spatial reading.
- **"Delay series":** already non-spatial; keep it.
- **"Lap equation":** "return equation" (the growth returns to the same knot).
- **"Hanging":** "at two removes".
- **The self-renewing floor bit:** avoid "thread", which already means the number line in your records. "Renewing offshoot" would do.
