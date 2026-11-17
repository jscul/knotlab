# Referee report STATE-RULES-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - The proofs S1 to S5 are correct.
  - The two amendments changed no read-out or prediction. Amendment 2's class equivalence is right, by DISTANCE-ORDER statement
    3(a).
  - "Number of orders" is read from the states alone, so no arrangement is smuggled in.
  - The referee's own code recomputes, one size past:
    - C(n, 3) zero-cost fills, all two orders, to n = 10;
    - the conservation of (k, λ) to n = 13 from all three starts;
    - the exact probabilities of two orders from one knot: 1, 1/2 and 0 at n = 5, 6 and 7, and 5/12 at n = 6 with each class
      counted once.
- **What changes, about the owner's premise (how the knots meet).**
  - **The knots do change what grows, but not the number of orders.** With 1,000 runs per start (the study had 30), the fan and the
    non-fan, with identical states, give the same number of orders at n = 8, 10 and 12 (two orders at 8: 375 and 361; χ² p = 0.55,
    0.68, 0.81). The grown bases themselves differ: at n = 7 the two starts share 1 of their 4 classes of states, with total
    variation distance 0.76, and at n = 8, 0.81.
  - So "it does not change where the growth goes" holds for the count of orders only. The study's 30 + 30 runs had 3% power at the
    rates seen, so its "within sampling" could not have shown anything either way. **Narrowing.**
  - **"Two orders at n = 6 two times in three rather than one in two" is not an effect of reading knots.** The knot arm weighs each
    knot set, the states-only rule each extension. The closure control, a function of the states with the knot arm's weighting,
    gives 0.70 (1,000 runs), against 0.65 for the knot-local rule and the states-only rule's exact 1/2. The difference is the
    weighting. **Narrowing.**
  - **"No rule tried makes two orders and keeps them" is fair as scoped,** with "tried" and A99 kept everywhere. **Not a block.**

## What holds

- **S1 (proved).** B(u, p, v) leaves N + d(u, v) states and B(u, v, p) leaves 2N − d(u, v). Both are at least N + 2, with equality
  exactly at subdivisions and pendants.
- **S2 (proved; the conservation of (k, λ)).**
  - **Subdivision.** X is the only split separating the adjacent pair u, v. Its two copies cross exactly what X crossed: p lies on
    u's and v's side of every other split, and both sides already hold u or v. The copies are nested twins, so k is kept. In a chain
    …Y ⊂ A ⊂ Z…, Y misses u (else Y would separate u from v) and Z holds v, so A ⊂ A ∪ {p} slots in and λ is kept. Nestings away from
    X are kept, because p always joins u's and v's side.
  - **Pendant.** v lies in every side of a chain or in none. Orienting so v is in every side puts {p} at the head.
  - **Fresh check** (`referee_fresh.py`, item 2): 20 runs each from the line, the 2 × 2 cut system and the star to n = 13, choosing
    uniformly among the fewest one-knot extensions at every step. (k, λ) is (1, 1), (2, 2) and (1, 2) at all 220, 200 and 200 steps.
    λ was read by the referee's brute force over orientations with Dilworth, which agrees with Eppstein's formula wherever both were
    computed.
- **S3 and S4 (proved).**
  - **S3.** L-copies nest, R-copies nest, and an L-copy of s_i crosses an R-copy of s_j exactly when i < j.
  - **S4.** The case analysis is complete for at most three knots:
    - the constants need a middle knot;
    - two middle knots either conflict or leave one open interval, which gives a tie;
    - one middle knot with two end knots gives R^a L^i R^j L^r.

    That is C(n, 3) patterns, as four parts summing to n − 1 with the inner two positive.
  - **Fresh check** (item 1): at n = 3 to 10 the zero-cost extensions number 1, 4, 10, 20, 35, 56, 84 and 120, which is C(n, 3).
    All are two orders. Every admitted extension has k, λ ≤ 2, and exactly n + 1 keep a line, all at N + 2.
- **S5 (proved).** It is consistent with the fresh exact computation (item 3: one option at n = 4, 8 options in 2 classes at n = 5).
- **S6** is a conjecture, and it is labelled as one. The exact values it predicts hold (1/2 at n = 6, 0 at n = 7, 5/12 with classes once), by the referee's exact enumeration.
  The cube growth to n = 16 was not recomputed.
- **The amendments.**
  - **Amendment 1** runs the parts as separate processes and stops F2's exact count at n = 7. The only F2 prediction, R6, is at
    n = 4. No read-out rule changed.
  - **Amendment 2** replaces the incidence graph by the complete graph weighted by disagreement counts, with N in the bucket key.
    - For bases of betweenness knots, a renaming that preserves the counts maps one base onto the other by statement 3(a). The pair
      table and N determine the base, and the renamed base is again a base of such knots.
    - So the classes are the same, and with knots added as nodes the same holds for the knot arm.
    - The check of 166 pairs agrees. Only speed changed.
- **"Number of orders" (the coordinator's item 5).**
  - **k** is the chromatic number of the splits' crossing graph.
  - **λ** is the least number of chains of nested oriented splits.
  - Both are invariants of the split system, that is of the set of states, under renaming. Neither uses a drawing or a coordinate.
  - The rule sees the states renamed at random before every read.
  - So nothing smuggles in an arrangement. What is chosen by the study is the move set (A99) and the weighting, and both are named.

## 1. Fan against non-fan: what was and was not tested (the coordinator's item 4; Narrowing)

The owner's premise is that how the knots meet carries information the states do not. The study's test is the knot-local
fewest-states rule (KF3) from two starts with identical states (the line of six) and different knots: the fan, one distinction in
all four, and the non-fan, none in all four.

**What the study showed.** The knots fix where the first fill can go: only on a triple whose pairs share a knot. That is a direct,
deterministic use of the knots. It is a real difference.

**What "within sampling" could carry.** The study compared two orders at n = 8: 11 against 15 of 30. At the rates the referee
measured with 1,000 runs per start (0.375 and 0.361), a 30 + 30 design detects the difference with probability 0.03 (Fisher test,
simulated). The study could not have seen a difference of that size, and with these rates there is none to see.

**What the referee ran.** The study's own rules.py (labelled; `referee_power.py`), 1,000 runs per start to n = 12:

| n | Fan: λ distribution | Non-fan: λ distribution | Test |
| --- | --- | --- | --- |
| 7 | 2: 1,000 | 2: 1,000 | — |
| 8 | 2: 375, 3: 625 | 2: 361, 3: 639 | Fisher p = 0.55 |
| 10 | 2: 2, 3: 673, 4: 320, 5: 5 | 2: 3, 3: 672, 4: 323, 5: 2 | χ² p = 0.68 |
| 12 | 3: 211, 4: 737, 5: 52 | 3: 215, 4: 727, 5: 58 | χ² p = 0.81 |

So the number of orders does not depend on the knots, now with adequate power.

**But the bases do.** The referee then classified the grown states (knots ignored, classes up to renaming), in 400 runs per start:

| n | Classes, fan | Classes, non-fan | Shared | Total variation distance |
| --- | --- | --- | --- | --- |
| 7 | 4 | 4 | 1 | 0.76 |
| 8 | 14 | 15 | 3 | 0.81 |

The knots steer the growth to different bases, almost disjoint at n = 7. Those bases simply have the same number of orders.

**Said plainly for the owner.**
- *Tested:* the knot arrangement changes which bases grow (yes, strongly), but it does not change their number of orders (no
  difference, to n = 12).
- *Not tested:*
  - other pairs of starts;
  - other knot-reading rules;
  - whether the bases that differ carry the knots' information in their states (their pair counts carry the base, but which
    differences matter for the premise is not settled).
- *What the summaries should say.* The note's "it does not change where the growth goes" and A97's "two orders appear as a stage and
  are kept by none of these laws, with or without reading the knots" are right about the number of orders. They should add that
  reading the knots changes which base grows.

## 2. "2/3 against 1/2" is the weighting (Narrowing)

The note, the intuition entry and the G16 goals line all say that reading which knots meet changes the odds, with two orders at
n = 6 "two times in three rather than one in two". The two rules weigh differently, though.
- **The states-only rule F3** puts equal weight on each distinct extension.
- **The knot arm** puts equal weight on each knot set (`knot_step`: distinct knot sets are distinct moves). An extension that several
  knot sets give is weighed more.

The study's closure-local control KC3 has the knot arm's weighting and reads only the states. From one knot, two orders at n = 6
come out as follows (`referee_power.py`, 1,000 runs each):

| Rule | Two orders at n = 6 |
| --- | --- |
| KC3 (states only, weight per knot set) | 0.701 |
| KF3 (knot-local, weight per knot set) | 0.647 |
| F3 (states only, weight per extension; exact) | 1/2 |

The shift from 1/2 is the weighting. Against the matched control, reading the knots changes little at n = 6 from one knot. It
matters later, from the six-starts: KF3 gives 26 of 60 two-order runs at n = 8, against KC3's 45 of 60. The comparison to quote is
KF3 against KC3, not against F3.

## 3. "No rule makes two orders and keeps them" (the coordinator's item 3; Not a block, with wording)

- **The scope.** It is fair as scoped: "no rule tried", within A99's move set (betweenness knots, at most three per step, every old
  state kept), the weightings named, n ≤ 16, and 40 to 50 runs at n = 10.
  - Sampling suffices for "keeps": zero of 40 to 50 at n = 10, with exact values to n = 7.
  - The knot-reading rules do make two orders and then pass through them, at n = 6 to 8, to three or more. So the failure is not
    failing to make two orders; it is not stopping.
- **The summaries.** They keep "tried" and the move set, except the intuition entry's last line, "none of these laws stops there",
  which is fine as worded.
- **A99** records the move set as challengeable, which is right.
- **The stress run** (STATE-RULES-B2, F3 to n = 32) is pending and not refereed.

## 4. The post hoc recounts and R16 (the coordinator's item 6; Not a block)

- **R17 and R19.** Their readings come from the frozen runs replayed from the frozen seeds (deterministic), and quantities the
  frozen output did not store were counted after the read-out. They are labelled, `posthoc.py` gives them, and the table says
  "held" with the post hoc reading noted. That is acceptable, but R17 and R19 should be counted as held on a post hoc read.
- **R16.** It failed as worded because the control's seed string includes the start. The distributions agree (22 and 23 at n = 8;
  the referee's 1,000-run comparison of KF3 shows what equal distributions look like). It is carried honestly.

## Fixes for the thread (listed for the owner, not folded in)

1. **The premise.** Say that reading the knots changes which bases grow (state classes almost disjoint at n = 7) but not their number
   of orders, now tested with 1,000 runs per start. Replace "within sampling" by those numbers. **Narrowing.**
2. **The weighting.** Compare the knot-local rule with the closure control, not with F3. Drop "two times in three rather than one in
   two" as evidence that reading knots shifts the odds, in the note, the intuition entry and the G16 goals line. **Narrowing.**
3. **Small things.** Mark R17 and R19 as held on a post hoc read. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, both amendments, the proof, rules.py, run.py, posthoc.py and the results;
  - checked S1 to S5 and the class equivalence by hand;
  - wrote its own extension enumeration, orders (k, and λ by brute force), the line counts, the conservation runs and the exact
    three-knot probabilities (`referee_fresh.py`).
- **The study's own rules.py** was run (labelled) only for the 1,000-run power comparison, the class distributions and the weighting
  control (`referee_power.py`).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_fresh.py` and `.json`:** independent code. Its items are:
  - 1, the line's extensions;
  - 2, conservation;
  - 3, the exact probabilities.
- **`referee_power.py` and `.json`:** the study's rules, more runs. It covers fan against non-fan by orders and by state classes,
  the power of 30 + 30, and the weighting confound.

Reproduce, from `research/STATE-RULES-20261117-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_fresh.py > referee_fresh.json
../../../.venv/bin/python -B referee_power.py > referee_power.json
```
