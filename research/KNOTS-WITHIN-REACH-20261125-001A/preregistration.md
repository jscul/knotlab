# How many knots lie within reach, and whether the growing end carries a distance of its own: pre-registration

Ticket `KNOTS-WITHIN-REACH-20261125-001A` of epic `KNOTS-WITHIN-REACH-20261125-001` (sub-goals B261 and B269; goals G1 and
G2 with G5; assumptions A110, A97, A98, A105). The engine will be written by a helper that has not seen the drafter's
prototype, from this text ("PR"), [the claim](../KNOTS-WITHIN-REACH-20261125-001/claim.md), [the
definitions](../KNOTS-WITHIN-REACH-20261125-001/definitions.md) ("KD"), [the survey](../KNOTS-WITHIN-REACH-20261125-001/survey.md),
the shared definitions ("SD") and the definitions of the study of parts that meet again ("FD"), and the data files beside
this text: [census_starts.json](census_starts.json), [named_starts.json](named_starts.json),
[five_knot_order.json](five_knot_order.json), [run2_small_starts.json](run2_small_starts.json). It may import the fold
study's engine (`experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/pm.py` and
`knots.py`) read-only. The canonical K1–K3 test is unchanged. No claim is made about physical space or time, living
things or minds.

**Frozen on 2026-11-25 (UTC), after the advisor's two passes and before the study's code is written.**

## The question

The owner's words of 24 November 2026 (Pacific time; the record's tickets carry 25 November, its date in UTC), "Could you
work your way through all 4 of these? You can work in parallel", take up the thread's direction "Space and dimension from
the growth (goals G1, G2) ... how many knots lie within reach, and whether the growing end carries a distance of its own"
([the owner's request](../KNOTS-WITHIN-REACH-20261125-001/owner_request.md)), with his founding premise (A97), his "you
can't just skip 4 to get to 5, so there is an order" (A98) and his direction on blow-up (A110) behind them. **Read here
as** (the claim, section 1): the count of the growth's history within r holder steps of a knot (H); the roster at one
round apart (P); and, among members of one part, how strongly their loose distinctions are related against their
witnessed steps and their arrival delay.

## In standard terms

In the literature's words: the grown object is a hypergraph whose edges carry constraint relations (parity: a binary
linear code; not-all-equal: 2-colourings). H is the volume growth (the literature's) of its line graph over the whole
history, counted from a stated vertex; under a taking-free law that graph is the descent order of knots made symmetric,
plus the start's own edges. P is the volume growth of one slice's own graph (the literature's slice of a growing order).
Question 2 asks whether two-point correlations of degree-one variables under the uniform measure on solutions are
monotone in the slice's graph steps and in a first-common-descendant time.

## Prior work in the program

Searches, each `python3 -B scripts/track.py objects "<words>" --until 2026-11-25 --exclude KNOTS-WITHIN-REACH-20261125-001`,
run read-only by the drafter on 25 November 2026; the top three rows of each:

- "within reach": `RULER-LEVEL-20261114-001`, `CHEAP-COUNT-20261112-001`, `LOCAL-ROOM-20261118-001`.
- "growth of balls": `FRESH-COUNT-20261118-001`, `INFLUENCE-CONE-20261120-001`, `COUNT-BALLS-20261118-001`.
- "knots within r steps": `LOCAL-ROOM-20261118-001`, `LEVEL-REACH-20261114-001`, `ADDR-KNOTS-20261113-001`.
- "ball growth grown structure": `COUNT-BALLS-20261118-001`, `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`,
  `KNOT-RATION-GAME-20261121-001`.
- "bond distance": `RING-READ-20261118-001`, `MEET-ONCE-20261119-001`, `ORDINARY-DYNAMICS-20261120-001`.
- "state distance loose distinctions": `CREATED-PAIR-20261119-001`, `ORDINARY-DYNAMICS-20261120-001`,
  `BOND-CLOSURE-20261120-001`.
- "arrival delay": `MEET-HIST-20261118-001`, `OLD-CORE-20261112-001`, `RANDOM-FATES-20261112-001`.

Used ([the survey](../KNOTS-WITHIN-REACH-20261125-001/survey.md) gives lines and standing): FRESH-COUNT and CUBIC-FROM-A-KNOT
(bond balls Θ(r^a) and Θ(r³) on the infinite counting pattern, proved; not counts of knots by holder steps); the cluster
theorem and the kinds of growth by round (lesson 8.2, refereed); INFLUENCE-CONE (under ordinary growth two members first
share a descendant after exactly their witnessed steps; proved, referee pending); the state-distance study (the
disagreement share; the parity statement for loose distinctions; |1 − 2r| ≤ 1/((2^f − 1)(2^g − 1)); near pairs that never
meet on reached cuts; the rival joins inactive on every reached cut; referee pending); the ring study's and the copier
study's settled statements; the copying-parts study's census of starts and its "each two-knot part becomes one chain
gaining a member a round" under a cap of three. Not used: RULER-LEVEL, LEVEL-REACH, LOCAL-ROOM (their "reach" is another
object), CHEAP-COUNT, ADDR-KNOTS, KNOT-RATION-GAME, MEET-HIST, OLD-CORE, RANDOM-FATES, RING-READ, MEET-ONCE, CREATED-PAIR.

Also among the top rows of the searches, on other objects and not used: `EVEN-PERIOD-20261112-001`,
`IDLE-PHASE-AND-TREE-CLOSURE-20261121-001` and `ODD-SEARCH-20261112-001`.

## Prior work outside the program

From memory, the literature's, not checked, not leaned on: volume growth and the degree of polynomial growth (Milnor;
Gromov; Bass–Guivarc'h), which concern homogeneous graphs and limit objects, neither of which is here; causal sets and
growth models (Rideout and Sorkin's sequential growth; reading a partial order's dimension by chains and intervals,
Myrheim and Meyer), where reading an order by its two-way neighbourhoods gives the slice's exponent plus one, which is why
H and P are read apart; correlation decay for 2-colourings on trees (the product formula). What this would add: the first
counts of knots by holder steps in what the record's laws make, read exactly where the counts are polynomials; the gate of
"the same power from every knot examined" with its scaling condition; the start-by-start table that separates the cap
from the treatment; and the order test on the growing end with the members' own loose and shared-place counts held equal.

## Known before the runs (disclosed)

The drafter's prototype (unreviewed; not the study's engine; Python scripts importing `pm.py` and `knots.py`: `common`,
`controls`, `grow1`, `grow2`, `census`, `verdict2`, `drive_census`, `nae_rates`, `nae_exact`, `growing_end`, `ge_census`,
`ge_strata`, `parity_ties`, `table7`, `table7b`, `c3_v2`, `gate_v3`). Floating point unless said; every count is
not-all-equal unless said.

1. **Controls** (KD 8): R_400 gives H = 2r + 1 and the gate j = 1 on [4, 64] (16 knots, spread 1.12); T_9 and T_12 give
   H = 3·2^r − 2; W_99 gives H = 6r² + 6r + 1 and the gate j = 2 on [4, 32] (16 knots, spread 1.22); L8 from one knot gives
   b(t) = C(t + 2, 2) and H = C(r + 3, 3) from the start knot through r = 40; the comb gives C(r + 2, 2) from its first
   spine knot and r + 1 from a far leg end for r ≤ 63, and **no gate** with its 192 knots examined.
2. **The amended gate on the registered positive case** (KD 4; checked by the drafter before the freeze, as the advisor required):
   Ring(33, 2) under L0, start knots and 64 knots of each of classes (b) and (c): **no gate at 66 or 132 rounds** (least
   kept range 33 and 66: j = 2 fails because the start knots' own counts are 2r² + 2r + 1 only to r = 16, then rise by 34 a
   step, so their own C_u/c_u on [4, 32] is 2.41; j = 1 needs a ≥ 16 and so z ≥ 128); **the same power 1 from every knot
   examined at 264 rounds on [16, 132] and at 528 rounds on [16, 264]** (161 knots; spread 2.02 both times, band "at most
   4"; start knots alone 1.02 and 1.03; made knots 2.02). The scaling condition holds (264 ≥ 1.8 × 132). Ring(15, 2) at 264
   rounds: the same power 1 on [7, 132], spread 2.05. The advisor's hand figures, checked: from a made knot H/r² is 2.562
   at r = 4 and 2.063 at r = 32 (as it said); from a start knot it is 1.063 at r = 32 (it said about 1.05), but the start
   knot's count is not r² + 1.5r + 1: it is 1, 5, 13, 25, 41, 61, 85, … (2r² + 2r + 1) to r = 16 and 1,089 = 33² at r = 32.
   On [4, 32] the made knots alone read j = 2 (spread within 2) and the start knots do not. Two-share under L0 at 66 and
   132 rounds: no gate (start knots alone j = 2 on [4, 33] and [4, 66]; made knots share no j); L8 from one knot at 66
   rounds: no gate (the start knot's C(r + 3, 3) has C/c of 2.75 on [4, 33]).
3. **The start-by-start table** (64 census starts: `random.Random(20261125).sample` of the 3,376 in file order; 40 rounds,
   50,000 knots; births read exactly by KD 3.2; the degree of b(t)):

   | Law | births of degree 0 | degree 1 | degree 2 | ended |
   | --- | --- | --- | --- | --- |
   | L0 (ORD, STALL) | 8 | 25 | 2 | 29 |
   | L9 (ORD, CANCEL-RETIRE) | 10 | 49 | 2 | 3 |
   | L10 (CAP-2, CANCEL-RETIRE) | 1 | 60 | 0 | 3 |
   | L6 (CAP-3, CANCEL-RETIRE) | 5 | 56 | 0 | 3 |
   | L11 (CAP-4, CANCEL-RETIRE) | 8 | 53 | 0 | 3 |
   | L7 (CAP-3, CANCEL-OFFSHOOT) | 4 | 60 | 0 | 0 |
   | L1 (CAP-3, CANCEL-WAIT) | 4 | 55 | 0 | 5 |

   Start by start: of the 29 starts that end under L0, 24 have births of degree 1 and 2 of degree 0 under L9, without any
   cap; the 2 starts of degree 2 under L0 (census 3103 and 3192) stay at degree 2 under L9 and have no births of degree
   2 under any cap (degree 1 under L6); of L9's 49 starts of degree 1, all 49 are of degree 1 under L6; 5 of L9's degree 0 become degree 1 under L6. Under
   L9 the largest part gained 1 member a round over rounds 36 to 40 in 41 runs, 0 in 10, and 4, 8, 16 or 148 in 10; under L6
   it gained 1 in 51 runs, 2 in 5 and 0 in 5, the number of parts unchanged in all 61 runs that lasted 10 rounds. **So on
   this sample the treatment (retiring for stalling) accounts for 49 of the 56 starts with births of degree 1 under L6,
   and the cap is what
   stops them rising faster (degree 2 in 2 of 64 without a cap, in none with a cap of 2, 3 or 4) and keeps the largest
   part's gain at 1 or 2 a round.** The 64 starts shaped P1 to P3; every share is reported with and without them.
4. **The count census** (the same 64 starts, 8 laws, 100 rounds, 50,000 knots, the fold engine's guard at its own limits,
   512 runs, 450 s), read by the doubling reading (the swap): counted from start knots, the commonest reading under L1, L6,
   L7 was 2 (41, 47 and 50 runs), under L3–L5 a count rising above every power of degree 4 to 7 on the ranges reached (60,
   63 and 38 runs), under L0 ended (29), 2 (22), 1 (5), 3 (2), a rising count (1), undecided (5). The same power from every start and made
   knot examined was read once, power 1 (census 3083 under L0, 17 births a round). Made knots: 195 of 280 undecided under
   L0. The first version's member count is withdrawn (KD 2.2).
5. **Re-timing at the registered bounds** (20 five-knot starts of the registered order each, 100 rounds, 50,000 knots, the
   guard as KD 7.4, counts from every start knot and 16 made knots): mean (maximum) seconds per run L0 1.57 (11.5), L6 0.90
   (1.9), L3 1.94 (2.7), L4 2.78 (4.7), L1 1.46 (3.2), L9 1.69 (9.5); L8 from one knot 6.2 s to 50,000 knots. Run 4 on 20
   runs of three- and four-knot starts (100 rounds, readings at rounds 1 to 10, 25, 50, 100, the knot test at round 25 and
   100 later knots): 0.6 s in all, 0.03 s mean, 0.1 s maximum, at most 325 knots, no failing knot.
6. **The growing end** (the first version's census: 208 three- and four-knot starts and 8 named starts, rounds 1 to 3, 4
   laws, at most 30 members, elimination width at most 20; 2,330 stages, 55,566 pairs; re-read in the strata of KD 5.8,
   each comparison once, pooled over stages). The statement on loose counts, in the advisor's words: under L0, 17,247 of
   the 17,448 discordant comparisons (98.8 percent) are between pairs with unequal loose counts; among comparisons with
   equal loose counts, 201 of 13,896 untied are discordant (1.4 percent), against 38 percent with unequal counts; under the
   between-knots reading 5,438 of 59,100 remain (9.2 percent). Under the cap laws loose counts account for less: 1,570
   falls to 963, with 443 at equal counts (L1); 1,051 falls to 606, with 165 (L6). Neither reduction is "the share due to
   loose counts": γ removes them in part, and the equal-count comparisons are a different set. Discordance survives on 130
   stages under |γ| and on 33 at equal counts, the smallest included. Under L3 every one of the 1,224 comparisons of
   stratum (i) is tied in δ. Strata sizes (L0, L1, L6, L3): one part with δ decided 6,872, 5,473, 5,092, 1,102 pairs;
   δ = ∞ 2,342, 11,880, 6,684, 10,153.
7. **The smallest disagreeing stage** (exact, every state enumerated, and an integer contraction agreeing): census start
   157 after round 1 under L0 (also under L1 and L6), 7 knots, 17 distinctions, 38,178 allowed states, three members (a
   four-parent join and two offshoots), each with two loose distinctions: κ = −1/2,121 (join and first offshoot; ws 1,
   δ 1), −1/707 (join and second offshoot; ws 1, δ 1), 19/19,089 (the two offshoots; ws 2, δ 2). Its comparisons: one
   concordant, one discordant, one tied; S = 0. The join has four shared places and the offshoots one each, so it is "not
   loose counts; shared-place counts not separated". Under L1 the smallest |κ|-against-δ disagreement (census start 133
   after round 1, 6 knots) is between two waiting start knots that still share a distinction (|κ| = 1/27, δ 2) and two
   offshoots (4/243, δ 1).
8. **Betweenness** (on the saved data): failing triples 878 of 5,734 (149 of 435 stages tested) under L0; 315 of 3,917
   (69 of 494) under L1; 220 of 3,594 (47 of 490) under L6; 197 of 1,320 (38 of 435) under L3.
9. **Integer contraction, timed**: 114 stages of 40 four-knot starts under L0, rounds 1 to 3, 2,606 pairs, 2.7 s; the first
   60 five-knot starts of the registered order under L0 and L6, rounds 1 to 4: 397 stages, 12,049 pairs, 41.4 s (0.35 s per
   start and law); 17 stages over elimination width 20, each with at least 58 shared distinctions.
10. **Taking rules** (4 named starts × 2 base laws × Q, MET, STEPS-1, STEPS-2 × 2 seeds of uniform takes, parity, 20
    rounds; 64 runs, 2.4 s): from round 10 to 20 no run doubled its knots with its greatest holder steps from start knot 0
    not rising. At 100 rounds (three runs): Ring(5,3) under T2 514, 1,575, 3,389 knots at rounds 25, 50, 100 with greatest
    holder steps 8, 14, 17 (weighted step 25, 38, 55); Ring(7,3) under T4 228, 378, 678 knots, 9, 14, 21; three-knot under
    T4 125, 250, 500 knots, 23, 48, 98. Λ_t at rounds 10 and 20: rank 0 in 120 of the 128 stages read (59 of the 64 runs); rank 1
    with a least number of distinctions in one rule of 4, 5 or 7 in 8 stages of 5 runs (the number of loose distinctions
    was not recorded, so whether these rules use fewer than all of them is unknown). Tied pairs of loose distinctions at two
    knots, both passing K1–K3, two or three holder steps apart, in 5 of 160 runs with a taking rule, 8 rounds (rounds 3 to 6);
    none in the 32 runs without one.
11. **The census reproduced**: 3,376 starts of three to five knots (19, 200, 3,157), 32 failing the parity knot test at
    round 0 (3 and 29 at four and five knots), none failing under not-all-equal. Small starts whose births under L0 read
    degree 2 or more (40 rounds): degree 2 at census indices 19, 164, 172, 178, 179, 214, 219; degree 3 at 177, 218.
12. **Corrections found by the advisor and checked**: C(r + 3, 3) first reads within 0.3 of 3 at r = 13; the bare ring's step
    from n − 1 to n is 3n − 1 (26 then 18 for n = 9; 44, 30 for n = 15; 62, 42 for n = 21); the golden-ratio eddy passes
    50,000 knots after round 17, so the doubling reading there reaches at most 5; the 325 checks of Lemma F covered H only.

**Not run by the drafter**: the gate on the census sample; LINREC and RATIO on S; BOUND; every swap of the scaffold table;
the order-test controls; the member shuffle; the exact numbering check (run 4b); the history weighting; parity runs of the
count census; the knot test of runs 3, 4 and 5 at their registered scale; HOLD; CARRY; L2, L5 and L8 on census starts.

## Settled by construction (stated, not tested)

1. Lemmas E, F (with its induction), R, N, P (KD 1.6, 2.6, 2.8, 5.3, 5.4): argued, not refereed, each with exact
   hypotheses where stated and a check (KD 7.7) that could contradict it.
2. **Renaming** for taking-free laws (the copier study's Settled 1, checked exactly there): counts of L0–L11 do not depend
   on the numbering; the weighting of each sampled class does not either; a given sample does.
3. **Uniform takes**: with each take of Q, MET, STEPS-1, STEPS-2 drawn uniformly among its candidates, the weighting of runs
   from a renamed start is the image of the weighting from the start. It holds for the weighting of runs, not for one seeded
   run; it is checked exactly in run 4b if run 0's probe fits, and otherwise reported "argued, unchecked".
4. **Parity runs** of a taking-free law equal the not-all-equal runs up to the first birth that takes every loose
   distinction of the structure, none barred, after which the parity run has ended.

## What is supplied

Everything SD (line 157) and FD (section 8) list for the laws used; every law beyond ordinary growth; the starts and both
census weightings with their estimators; the holder step, stepping through dead and retired knots, members as the growing
end, the classes of knots counted from and their sampling; the readings of KD 3 and their precedence; the gate's
thresholds; the RATIO floor; the kept range; the bounds and the guard; the stage weighting and the history weighting; γ
(post hoc); the delay horizon; the order rule, the strata and the member shuffle; the stage cap; the controls; the order of
running. **Supplied or made**: every count is of a pattern the law makes from a supplied start; one degree of every POWER
of H comes from the rounds we run; a range set by the start's size is said to be the start's.

## Scaffolds and their swaps

| Scaffold | Swap (fixed direction where a reading is swapped) | Run |
| --- | --- | --- |
| Holder step | parent step (runs 1, 2: null outside the start's meetings by Lemma E); steps through distinctions of at most two holders, and the weighted step (run 4) | 1, 2, 4 |
| Stepping through retired knots | retired knots counted, not stepped through | 2 |
| Members as the growing end | every live knot (barred included), for P | 2 |
| Exact reading primary | BOUND(j); the doubling reading with 0.3 (the reading first used) | 1, 2 (re-read only) |
| Gate thresholds z ≥ 8a, C_u/c_u ≤ 2, 1.8 | z ≥ 4a, C_u/c_u ≤ 3, 1.5 | 2 (re-read only) |
| RATIO floor 1.25 | 1.1 and 1.5 | 1 (re-read only) |
| Census weighting | labelled weighting (KD 7.5) | 1, 5 |
| Bounds 100 rounds (66 and 132 for the gate; 264 and 528 for the bare rings), 50,000 knots | 60 rounds, 20,000 knots (named starts) | 2 |
| RELEASE | HOLD under L3 and L6 (named starts) | 2 |
| Uniform takes | OLDEST and NEWEST under the numberings of KD 7.3 | 4c |
| Stage weighting | the history weighting (stages of at most 20 distinctions) | 5 |
| |κ| (larger = more strongly related) | |γ| (larger = more strongly related); ρ (smaller = more strongly related), with the sign counts | 5 |
| Delay horizon 6 rounds | 10 rounds (three- and four-knot starts) | 5 |
| Stage cap 30 members, 50 shared distinctions | 40 members, 60 shared distinctions (three- and four-knot starts) | 5 |
| The optional class (d) near 3·s_min/4 | read beside the gate only | 2 |

## What a result would and would not show

As the claim, section 6: no limit object; the count depends on the knot counted from; the birth order read in both
directions gives the roster's exponent plus one where the number of parts is fixed; the step convention under hubs; a
discordance and its headline level; under parity, tied or unrelated.

## Starts and files

- [census_starts.json](census_starts.json): the 3,376 census starts in file order, each with n, atlas graph, loose tuple,
  stars and labelled weight `w_labelled` (and 4 entries of one and two knots, not in the census). Denominators: 3,344 under
  parity (the starts passing the knot test at round 0), 3,376 under not-all-equal.
- [five_knot_order.json](five_knot_order.json): the 3,157 five-knot starts in the order of
  `random.Random(202611251).shuffle` of their file indices; the first 1,000 are run 1's sample, the first 50 run 2's; each
  marked whether it is among the 64 starts of the drafter's runs (23 of the first 1,000).
- [named_starts.json](named_starts.json): Ring(5,3), Ring(7,3), Ring(9,3), D2(5,3), the seven-knot generator, two-knot,
  three-knot, three-knot-larger, one-knot, two-share, Ring(n, 2) for n = 5, 7, 9, 11, 15, 21, 33; and the controls R_400,
  T_12 and the comb (the weave W_99 is built by KD 8.3).
- [run2_small_starts.json](run2_small_starts.json): the 9 three- and four-knot census starts of run 2 (births of degree 2 or
  more under L0), which the engine recomputes before run 2.

## Runs (in the order of their value, highest first; this is the order of running; at most 6 processes, each under 6 GB)

| Run | Items | Measured seconds per item | Wall time, 6 processes | Readings |
| --- | --- | --- | --- | --- |
| 0 | controls of KD 8; checks E, F, R, I on the named starts; the run 4b probe (one case, capped at 10 minutes) | < 1 per control; probe ≤ 600 | ≤ 15 min | exact counts; every check; whether run 4b runs |
| 2 | the full gate: the named starts under L0, L6, L7 at T = 66 and 132; the bare rings under L0 at 264 and 528; the first 50 five-knot starts of the registered order and the 9 small starts of run2_small_starts.json under L0, L6, L7 at 66 and 132; start knots, 64 knots of each of classes (b) and (c), class (d) beside; 8 members for P; check F at t + 10 | 0.3 to 7 per run including 129 to 161 counts (scratch: two-share at 132 rounds 1.4 s, Ring(33, 2) at 528 rounds 7.0 s, L8 at 66 rounds 6.2 s) | about 460 runs × 5 s, and check F ≈ 15 min | the gate (j, [a, z], k of K, spread by band, start knots apart), scaling, earlier ranges, P; the comb must fail |
| 5 | the growing end: L0, L1, L3, L6, L7 (the laws with predictions) on every census start, rounds 1 to 3 (1 to 4 on three- and four-knot starts), within the stage cap, integer arithmetic; the knot test on every knot of every stage computed, once at its birth; the history weighting on stages of at most 20 distinctions; the order-test controls | 0.35 per (start, law) for growth and contraction (five-knot, rounds 1 to 4, scratch) + about 0.36 for the knot test (60 knots at 6 ms) | 3,376 × 5 ≈ 16,900 items × 0.7 s ≈ 33 min | strata, nested counts, headline levels, S with the member shuffle, L-W, betweenness |
| 1 | the screen and the table: L0–L7 and L9–L11 on the 219 three- and four-knot starts and the first 1,000 five-knot starts (in that order, the laws in the order of the table within each start), L8 on the 219 only; not-all-equal (parity derived, Settled 4); 100 rounds, 50,000 knots, the guard of KD 7.4; start knots and 16 made knots | 15.9 per start for the 11 laws (sum of the measured means; L2 and L5 estimated), 6 per start for L8 | 1,219 × 15.9 + 219 × 6 ≈ 20,700 s ≈ 58 min; a run cut for time leaves a prefix of starts that is still a uniform sample | b(t) exact; H's verdicts; the screen; the table with b(t) by part; shares with the estimators, with and without the 64 |
| 4 | T1–T8 with 2 seeds and T9, T10 under OLDEST, on the 17 named starts and the 219 small census starts, parity and not-all-equal, 100 rounds, 50,000 knots; readings at rounds 1 to 10, 25, 50, 100 under the four steps; Λ_t at rounds 1 to 10 and 25; the knot test on every knot after round 25 and on 100 later knots | 0.03 mean on small starts (measured, 20 runs); about 3 on named starts (estimated from the 100-round runs and 6 ms a tested knot) | 219 × 36 × 0.05 + 17 × 36 × 3 ≈ 2,200 s ≈ 6 min | claim 3; claim 4; the knot test |
| 3 | the knot test of runs 1 and 2: every start knot, and 200 sampled knots per run (class `knot-test`) on run 2's runs and run 1's runs of the 219 small starts, both knot laws | 200 × 6.7 ms ≈ 1.3 per run | ≈ 2,860 runs ≈ 11 min | "n of N knots tested, all passed; ..." (five-knot runs of run 1: no test) |
| 4b | (conditional on run 0's probe) every choice enumerated: two-knot, three-knot, Ring(5,3), 3 rounds, T1–T8, the weighting of structures up to renaming under the 4n numberings; at most 10⁵ histories per case, else "not finished" | measured by the probe | ≤ 10 min | Settled 3 checked, or "argued, unchecked" |
| 4c | (conditional) T9, T10 in full under the 4n numberings on the named starts; T1–T8 under OLDEST and NEWEST with all 4n numberings only if at least one run of run 4 is "held by hubs", otherwise 10 numberings each (the first 10 of KD 7.3's list) | 0.3 per run | ≤ 5 min | how many numberings change a claim-3 verdict |

In all, about 2 h 30 min of wall time on 6 processes, each run within the hour.

**How many rounds and knots a reading needs, and whether these runs reach them.** The exact reading needs j + 8 values:
for b(t) about a dozen rounds decide a start knot's degree (all 256 table runs and all 192 separating-arm runs were decided
within 40 rounds). The gate needs z ≥ 8a with a ≥ 4, so z ≥ 32, and the knots of class (c) need ℓ ≥ 32, so s_min ≥ 66 and
T = 66; the scaling condition then needs 132 rounds. A power 2 at 132 rounds is about 20,000 knots (reached); a power 3 at
66 rounds is about 50,000 knots and at 132 about 400,000, **so a third power's scaling condition cannot be decided at the
knot bound**, and run 2 reports it "undecided at the bound". A gate with j = 1 that needs a large a (the bare rings: a ≥ 16
on Ring(33, 2)) needs z ≥ 128 and so 264 rounds; these are cheap (Ring(33, 2) at 528 rounds is 17,457 knots). RATIO needs 9
steps of S, reached by every exponential law of the drafter's runs. A fourth power is not reachable and is not registered.

**Not asked for, with the advisor's reasons**: (i) all 3,157 five-knot starts in run 1 (a sample of 1,000 gives shares
within ±2.6 points at 95 percent in the worst case, and "none seen" excludes 8 or more such starts, not "none in the
census"; to be asked only if the sample turns up a candidate for the gate, or if the owner wants "no start of the
census"); (ii) the knot test on every knot of every run (the sample with the cited argument is honest); (iii) bounds of a
million knots (nothing registered needs a fourth power, and the exact reading of b(t) decides RING-LAW's t² cheaply).

## Predictions

Marks: **(a)** seen in the drafter's runs, **(b)** by argument, **(c)** undecided; **replication**: a count the registered
runs repeat on the same exhaustive family. Engine checks (E, F, R, N, P, I) and the controls are not predictions. Shares
are under the census weighting with KD 7.5's estimator unless said.

| # | Prediction | Mark | Fails when |
| --- | --- | --- | --- |
| P1 | Under L6, at least three quarters of census starts have births of degree 1. | (a): 56 of 64 at 40 rounds | below three quarters |
| P2 | Under each capped law (L1, L6, L7, L10, L11), no census start of run 1 has births of degree 2 or more, or LINREC with a root above 1, or RATIO(x ≥ 1.25), to round 100. | (a): 0 of 64 at 40 rounds (which bounds the share only below 4.7 percent) | one start does |
| P3 | Under L9, at least one census start of run 1 has births of degree 2, and at least two thirds have births of degree 1. | (a): 2 and 49 of 64 | none of degree 2 (then the cap is not what stops faster births), or below two thirds |
| P4 | Under L6, at least 90 percent of runs that go on to round 100 have the same number of parts at rounds 36 and 40 and at 96 and 100, and a largest part whose gain per round is the same over each of the two spans. | (a): 61 of 61 at rounds 36 to 40 | below 90 percent, or parts multiplying after round 40 |
| P5 | No run of run 2 passes the gate with the scaling condition at j ≥ 2; at least half of run 2's runs are decided (both, gate only, or no gate). | (a) on two named starts (two-share under L0: no gate at 66 or 132; L8 from one knot: no gate at 66); (c) on the census starts of run 2 and for the decided share | a run passes both at j ≥ 2, or fewer than half are decided |
| P6 | Ring(n, 2) under L0, odd n from 5 to 33: at 264 and 528 rounds the gate holds with j = 1 and the scaling condition holds; on [4, n − 1] the made knots alone read j = 2 and the start knots do not. | (a) for n = 33 (264 and 528) and n = 15 (264); (b) sketch for the counts | the gate fails, j ≠ 1, scaling fails, or start knots read j = 2 on [4, n − 1] |
| P7 | Under L6 and L7, the knots of class (c) of run 2's runs that hold the gate read j = 2 (so the 2 is not a count of births only). | (c): two-share's made knots shared no j | they read another j, or no run holds the gate |
| P8 | L8 from one knot: H from the start knot reads POWER(3) on [0, 64] and births of degree 2 from round 1. | (b) | not read |
| P9 | The roster count P under L1, L6, L7 reads POWER(1) or ALL WITHIN r from every member counted from, on run 2's runs. | (a): the witnessed-step counts of the drafter's 512 runs read 1, undecided or ended in all but one | a POWER(j ≥ 2) |
| P10 | Under T1–T8, no run of run 4 is "held by hubs" (knots at least doubling from round 50 to 100 with greatest holder steps rising by at most 2); both ratios reported. | (a): none of 64 from round 10 to 20 under "not rising"; 3 of 3 rose by 3 to 50 from round 50 to 100 | a run held by hubs |
| P11 | Under parity, at rounds 1 to 10 of run 4, at least one stage has a tied pair of loose distinctions at two knots that both pass K1–K3. | (a): 5 of 160 runs, rounds 3 to 6 | none |
| P12 | For L0, L1 and L6, the smallest stage at the level "not loose counts" has 7 knots (census start 157 after round 1), with S = 0 there. | replication | another smallest stage |
| P13 | For L0, L1, L6, ΣS of |γ| against δ in stratum (i) is positive. | replication (the drafter's ratios to the pair shuffle, 48 to 53, are descriptive; the member shuffle's is (c)) | ΣS ≤ 0 |
| P14 | Under L3, every comparison of stratum (i) on rounds 1 to 3 of the three- and four-knot starts is tied in δ. | replication | an untied comparison |
| P15 | L-W fails on at least one stage that tests it, and the betweenness test fails on at least one triple, for each of L0, L1, L6 and L3. | replication (L0, L1, L6, L3 seen for betweenness; L-W for L0, L1, L6); (c) for L-W under L3 | it holds for one of them |

Registered questions, not predictions: whether the history weighting keeps the order where the stage weighting does not;
whether the level "not loose or shared-place counts" has any discordance; whether any law of L0–L11 gives the same power 1
from every knot examined other than with constant births per round.

## Runs and stop rule

- One engine from this text; run 0 passes before any other run.
- **Stop**, read (the filed stop): for each law and class of knot counted from, H's verdict on its final segment with its
  interval; the gate and scaling verdicts with P beside them; the table with the separating arm; for the growing end the
  smallest stage at each headline level against δ, per law and knot law, or none, with L-W and betweenness; every
  prediction given a verdict.
- Disagreements with the disclosed prototype are replayed round by round; the listing decides.
- Every run within about an hour of wall time on at most 6 processes, each under 6 GB; the order of items is the registered
  order, so a run cut for time leaves a prefix that is still a sample; a cut is reported with the number of items run.
- Deviations in `deviations.md` of the experiment family before the affected run.

## Words

Kept range; the knot counted from; counted from; greatest steps within the start; the between-knots reading γ; the same
power from every knot examined; how strongly related (either sign), more strongly related, less; rank and the least number
of distinctions in one rule (for Λ_t); RATIO(x) and LINREC(k); the verdict said in place of "dimension", which names only
the program's target. Literature's names, once each and marked: volume growth, slice, comb, binary linear code.
"Counterexample" is an ordinary word and is kept; the ban is on "counter" as a noun for a thing that counts.

## What the advisor's passes changed

**First pass, the cold review: "freeze after listed changes", eleven required.**
- H was named a count of the growth's history, and the roster count P added as its own reading; the member count, empty
  below the kept range, was withdrawn.
- One gate: a two-sided bound on one common range that lengthens with the rounds, for every knot examined, with made knots
  near half of s_min; the exact polynomial reading made primary, on H and on births per round, with the doubling reading as
  swap, a ratio rule for fast counts and a precedence rule.
- The growing end: the between-knots reading beside |κ|, strata, a reference for S, integer arithmetic, fixed directions.
- The knot test moved to the runs where knots can fail; the source claim dropped; the taking-rule claim rescaled; the
  checks, symbols and controls defined (the comb, the order-test controls, the start-by-start table).

**Second look: "freeze with listed fixes", eleven required.**
- The gate made per knot (each knot examined within a factor 2 of its own c_u·r^j on one canonical range), with the spread
  reported in bands and start knots apart; checked before the freeze on Ring(33, 2) and the comb (Known 2).
- Run 1 made a screen and the full gate moved to run 2 with a census sample; class (c) corrected by one; the rule of three
  stated per class.
- The growing end: δ when growth ends, three nested strata and headline levels, |κ| primary as "how strongly related,
  either sign", the member shuffle as the reference, the statement on loose counts.
- The table read as "cap and treatment together" and separated by L9 to L11 (run now, Known 3); P1 to P4 as shares on
  births per round.
- The RATIO floor, ENDED with stalled and jammed, j from 0 to 3, verdicts for P; run 4 read at rounds 1 to 10 and 25 with a
  later-knot sample; the helper's missing items stated; the runs re-timed and ordered; words.
