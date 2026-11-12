# Referee report FAR-BOUND-R1: bounded at every distance?

**Verdict: Confirmed with fixes. Ticket B's proof is confirmed, and ticket A's far-range reading is narrowed.** The completion run
for question (ii) has finished and is folded into section 4: it finds no growing base among the 8 dropped.

- **Ticket B: confirmed.** I reran it with my own code and two different certificates, the proof's parameters and my own.
  - C1, C2 and C4 hold, and the representative argument is sound.
  - Every representative of the quadrant has a covering triple.
  - Three of the 1,620 checked parts are knots of the base, so they are never free. The proof does not use them, because another j
    covers those representatives.
- **Ticket A: narrowed.** "Rise by 2" is a rise in certified upper bounds:
  - in two of the five bases the window bonds stay within near + 1;
  - in one (183/4) the window bonds are 4 at every far target, and its certificates are missing at 31% of the targets;
  - only 17/4 and 17/5 rise in both, and their far profiles are identical.

  So the far data are compatible with a bound of 6. They neither show nor exclude growth.
- **The exploratory direction pattern weakens.** With my certified second-direction search, a second direction goes with staying
  bounded in 8 of 9 decided bases, but one direction grows in only 4 of 12, not 4 of 9. Neither split is significant on 21 bases.

Referee: the background referee thread, 2026-11-12. My code:
- `ref_quadrants.py` for ticket B, my own window and two-way certificate. It imports none of `check.py`, `census.py` or TRAVEL-READ's
  census.
- `ref_far_recount.py`, which recounts F2 from the census's records.
- `ref_far_dropped.py`, which reruns the 8 dropped bases with the census's own code and a longer cap. That run completes the data and
  is not independent.

Second directions come from my TRAVEL-READ-R1 search (`result_second.jsonl` there). I used CaDiCaL. Validation: V2 for ticket B and the
recount. The advisor model was not consulted for this job.

## 1. Ticket B: the two-quadrant theorem

**The frame.** In t′ = (1, 2), u = (0, 1) the kinds are {(0, 0), (0, 1), (1, 0)}, {(0, 0), (1, −6), (2, −4)} and {(0, 0), (0, 4),
(2, −2)}, as the proof says. The along-span is 2 and the across-span is 6.

**C1 holds.** In a window of 17 × 61 frame cells, 000 on T_0 makes value 0 impossible at every cell of T_0 + t′ and of T_0 + 4u, and
value 1 possible. A window refutation is sound for the infinite base.

**The certificate (Eventual2) is sound.** I derived it independently.
- **The construction.** A word Z on the window [a₀ − 2p, a₁ + 2p) × [b₀ − 2q, b₁ + 2q) repeats with period p in both along-tails and
  with period q in both across-tails, two blocks each, constrained equal. It is extended by that repetition.
- **Why a solution extends.** Take any edge of ℤ². Its along-extent is at most 2 ≤ p. If it starts in an along-tail it lies wholly in
  that tail, and shifting it by a multiple of p brings it inside the window's two tail blocks without changing its values. The same
  holds across, with q ≥ 6, independently: the repetition along holds at every across-count and vice versa.
- **The corners** are covered because both shifts apply there. So every edge of the extension is a translate of an edge inside the
  window, with the same values.
- **The census's `Eventual2` code does the same:** the same window, the same two tail blocks per side, the same equalities in both
  directions, and the edges inside the window. Its assertions P ≥ 2 and Q ≥ 8 cover the across-span 6.

**A condition the proof needs and does not state.** Travel along 4u complements the pattern at each step, so a repetition across must
be a multiple of 8. My first own parameter set, with q = 12, failed: T_0 was not even free in it. The proof's q = 8 and my q = 16 work.
Travel along t′ also complements at each step, so p must be even. Both 4 and 6 are.

**The representative argument is sound.**
- **The representative.** For α ≥ a₁ it is a₁ + (α − a₁) mod p; for y ≥ b₁ it is b₁ + (y − b₁) mod q. The certificate's value at x
  equals its value there.
- **No collision with T_j.** A representative has α ≥ 1, so it never coincides with a cell of T_j (α = 0). T_j lies inside the core
  for j ∈ {0, −1, −2}.
- **The forcing condition carries over.** q is a multiple of 4, so y and its representative agree mod 4, and C1's condition
  (y − j) mod 4 ∈ {0, 1, 2} is read correctly.

**C3, rerun.**

| Parameters | Representatives | Cases (representative, j, pair, pattern up to flip) | Not carried | Every representative has a covering j |
| --- | --- | --- | --- | --- |
| the proof's: core [−2, 2) × [−4, 4), p = 4, q = 8 | 60 | 1,620 | 3 | yes |
| mine: core [−3, 3) × [−6, 6), p = 6, q = 16 | 176 | 4,800 | 3 | yes |

**The 3 cases not carried.** They are the pattern 000 on {(0, 0), (0, 1), (1, 0)} (with j = 0 and j = −1) and on {(0, 1), (0, 2),
(1, 1)}. Those parts are knots of the base, so no state carries 000 on them. For x = (1, 0) the proof uses j = −2, and for x = (1, 1)
it uses j = −1, both fully carried.
- **The census agrees.** Its `result.json` counts 1,620 checks and 0 representatives without a covering triple, which is the same
  statement.
- **The proof's wording** "every pattern of every part ... carried (1,620 cases)" should say 1,620 cases checked, 3 of them knots
  at j's the proof does not use.

**C2 holds:** all 8 patterns on T_0 are carried by the two-way certificate.

**C4, certified.**
- **Travel along 4u.** Without the third kind, 000 on T_0 with a 0 at each of (0, 4), (0, 5), (0, 6) is carried by my certificate.
  So the travel along 4u disappears, certified. The census's C4 is only a window non-refutation, which does not certify it.
- **Travel along t′.** It disappears too: (1, 2) is no longer forced (certified), and only (1, 0) and (1, 1) are, by the first kind's
  own knots.

So both travels need the third kind, which the proof might say.

**Spot checks of soundness.** With all three kinds, my certificate refuses 000 on T_0 together with a 0 on any cell of T_0 + t′ or
T_0 + 4u. It also refuses 000 on a knot.

**The bond step** follows from these:
- T_j ∪ {x} is not shattered (C1);
- T_j is free (C2);
- each pair with x is free (C3);
- every T_j holds the origin;
- the second quadrant follows by translation and d(0, v) = d(0, −v).

**Confirmed.** Bond distance is at most 3 on both quadrants, on this base.

## 2. F2 recounted, and (iii): is "rise by 2" growth?

**The recount** (`ref_far_recount.py`), with the frozen rule read as "bounded only with at least 80% certified":

| Outcome | Census | Recount |
| --- | --- | --- |
| bounded | 16 | 16 |
| grows by 2 or more | 5 | 4 |
| certificates missing | 5 | 6 |
| dropped | 8 | 8 |

The difference is 183/4. The census's `summary.py` lets growth take precedence over missing certificates. Its certificates are missing
at 15 of 48 far targets (31%).

**The five growing bases at both levels:**

| Base | Certified b_cert | Window b_win |
| --- | --- | --- |
| 17/4 and 17/5 (identical far profiles) | 4 out to 15 across, then 5 or 6 from 19 | the same |
| 109/3 | 6 only at 23 across | 5 there |
| 112/4 | 6 at 19 to 23 across | 5 there |
| 183/4 | 5 or 6, or missing | 4 at every far target |

**(iii) Weak evidence.** b_cert is the least size of a certified bond in the searched family, so it bounds the least bond from above.
A rise in b_cert does not show that no smaller bond exists. No lower bound on the least bond is computed anywhere: that would need
every smaller set holding the origin and x to be certified free. b_win does not bound it either way.

So the rise is compatible with a fixed bound of 6, with slow growth, and with certification failing farther out. Only one law, 17/4
and 17/5 with identical profiles, rises at window level too. Its values (4, 4, 4, 4, 4, 5, 6, 5 at along 7) are not monotone in the
across-count.

"The bound creeps up on 5 bases" should read: certified upper bounds rise by 2 on 4 or 5 bases (by how missing certificates are
ranked), and window values on one law only.

## 3. (i) The exploratory direction pattern against a certified search

My certified search for a second travelling direction (TRAVEL-READ-R1) covers shifts with 0 ≤ a ≤ 4 and |b| ≤ 4, and sets in
[0, 2]². Crossed with F2's outcomes:

| Outcome | Second direction (mine, certified) | One direction (mine) | Second (census, exploratory) | One (census) |
| --- | --- | --- | --- | --- |
| bounded (16) | 8 | 8 | 11 | 5 |
| grows by 2 (5) | 1 | 4 | 1 | 4 |
| certificates missing (5) | 4 | 1 | 4 | 1 |
| dropped (8) | 4 | 4 | 4 | 4 |

- **Where the searches differ.** The two agree on 29 of 34 bases. The census's wider, uncertified search (shifts to 6, sets in a
  2 × 3 box) finds 4 second directions mine does not. Mine finds 1 it misses.
- **"A second direction means bounded".** It holds as 8 of 9 decided bases on certified directions, against the census's 11 of 12.
- **"One direction grows in about half".** It becomes 4 of 12, a third.
- **Significance.** Fisher's exact test gives p = 0.34 on mine and p = 0.12 on the census's. Neither is significant on 21 decided
  bases, and the 4 growing one-direction bases are 3 laws (17/4 and 17/5 have identical profiles).

What survives is "no base with a certified second direction grew by 2 at window level". The one growing base with a second direction
is 109/3, and it rises only in certified values. SHIFT-COUNT's own certified search found sample 97/3 to have two directions. Either
way the pattern is exploratory and after the run, as the note says.

## 4. (ii) Do the dropped and uncertified bases bias the split?

**The dropped bases are not the hard, growing ones.**
- **The proved base is among them.** Sample 24 at r = 3, the base ticket B proves bounded on two quadrants, is one of the 8 dropped at
  the 1,800-second cap. At least half of its far targets, those with positive across-count, lie in a quadrant with bond distance at
  most 3.
- **Directions.** The dropped bases have a second direction as often as the decided ones (4 of 8, on mine).
- **The missing-certificate bases** have window values within near + 1 or + 2 (`result_recount.json`). They read as uncertified, not as
  growing.

**The range of possible splits.** Bounded-far could be anywhere from 16 of 34 (47%), if every undecided base grew, to 29 of 34
(85%). The 16 of 21 decided (76%) is not biased in any direction the data show. Dropping depends on the cost of the search, not on
the outcome, as 24/3 shows.

**The completion run (folded in after the first commit).** I reran the 8 dropped bases with the census's own code and a
5,400-second cap (`ref_far_dropped.py`, FAR-BOUND-R1-cap), classified as in section 2.

| Outcome | Bases |
| --- | --- |
| bounded | 9/4 |
| certificates missing | 55/3, 79/6, 88/5, 128/4, 155/3 and 159/3 (certified shares 0.02 to 0.75) |
| dropped again | 24/3, the proved base |

None grows by 2. On every one of the seven decided bases, the window bonds stay within near + 1.

So, with them, the split over 34 is 17 bounded, 4 or 5 growing (by the ranking of missing certificates), 11 or 12 with
certificates missing, and 1 dropped. The dropped bases did not hide growth: they are mostly bases whose far bonds the strips cannot
certify.

## 5. Not recomputed

- F1 (34 of 66), judged in TRAVEL-READ-R1.
- F3 (77 of 102 at window level), whose rings use window bonds, as the note says.
- The control (base 16's 4, 5, 5, 6, 6), whose certificate TRAVEL-READ-R1 judged sound.

## 6. Fixes for the thread

1. **"The bound creeps up on 5 bases".** It is a rise in certified upper bounds. Window values rise on one law only (17/4 = 17/5), stay
   within near + 1 on 109/3 and 112/4, and are 4 everywhere on 183/4, whose certificates are missing at 31%. State it as "certified
   upper bounds rise by 2; no lower bound computed; compatible with a bound of 6". **Narrowing** (Overreading: upper bounds read as
   growth).
2. **The Reading's direction pattern** (already corrected for 97/3). On certified directions it is 8 of 9 and 4 of 12, not
   significant. Keep it as exploratory and say so with these numbers. **Not a block.**
3. **Ticket B's C3 wording.** Say 1,620 cases checked, 3 of them knots of the base at j's the proof does not use. Add the condition
   that the across period is a multiple of 8 (travel along 4u complements). Note that C4's census check is a window non-refutation;
   the referee's certificate certifies it, and also shows the travel along t′ needs the third kind. **Not a block.**
4. **The dropped bases.** Say that the proved base 24/3 is among them, so dropping is not a sign of growth. The completion run found
   no growing base among them (1 bounded, 6 with certificates missing, 1 dropped again). **Not a block.**

## Files

`brief.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_quadrants.py` | `result_quadrants.json` | ticket B: C1 to C4 under two certificates |
| `ref_far_recount.py` | `result_recount.json` | F2 recounted, with the window check |
| `ref_far_dropped.py` | `far_dropped/` | the completion run: 1 bounded, 6 with certificates missing, 1 dropped again, none growing |
