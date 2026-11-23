# Uniform present words with births as the settings: result draft

Ticket `REVIEW-LEADS-20261123-001C`, experiment `REVIEW-LEADS-20261123-001C-E001_present_words`. Draft by the implementing sub-agent;
analysis and verdict belong to the thread. Scientific referee pending. Definitions are those of `preregistration.md`, unchanged.
Readings and departures are in `experiments/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words/deviations.md`.
Code is in that directory; every output and log is in `artifacts/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words/`
(below `ART`). Every run is one process under ten minutes and 12 GB (`timeout 600 prlimit --as=12884901888 .venv/bin/python -B ...`); several runs were
started at once on the shared machine, and later runs were limited to one thread.

## Result in one paragraph

No hidden pair exceeds 2 in the exhausted census class (at most 3 knots, at most 3 internal distinctions), nor in the larger class
with at most 4 knots and at most 5 internal distinctions that was also exhausted, for a cut of one or of two. The largest
score among hidden pairs is exactly 2 in both. Without the hiding requirement the class reaches 8/3 (largest change of a complete
record 1/6). The reference over arbitrary side tables with a cut of two is 20/9 (best found, exactly verified; it is the note's own
four-type table, as a pair of side tables). In the allocation class the setting is a symmetry of the old structure, so the four
tables are relabellings of one table and the score is at most 2 whether or not the settings are hidden; this is proved below and
agrees with every pair of the census. A targeted random search over sides of up to 6 knots (1.39 million lawful structures, 284 million
pairs of table classes, allocation class and without the class condition) also found no hidden pair above 2. P1, P2, P3 and P4 all hold
as stated. The positive-structure steps were not run (no hidden pair above 2).

## Gate row G (run first; all pass)

| Gate | Result |
| --- | --- |
| Four-type distribution gives 20/9, hidden | exact best over parity outcomes **20/9**, both complete records hide the far setting, largest change of a complete record 0; the weight-ratio formula 4 - 8r/(1+r)^2 reproduced for ratios 2, 4, 8 (20/9, 68/25, 260/81). `gates_a.log` |
| Brute force agrees with the side-table product | 200 random pairs (100 per cut size, half with both sides in the allocation class): the 16 x 16 joint record counts of all four finished structures, enumerated word by word, equal F_a^T (T_A T_B^T) F_b; 0 mismatches. `gates_b.log` |
| Control weighting never exceeds 2 | largest control score 2 (exact, attained) over every unique old table of every run: census cut 1 and cut 2, extended class cut 1 (all pairs), extended class cut 2 (all hidden pairs), targeted pools; 0 above 2 |
| Code checks | batched evaluation equals the starter's `evaluate` (score, hidden flag, largest change) on 1,500 random tables and on 3,000 random census pairs, 0 mismatches; the C scoring kernel equals the numpy batch to the last bit on 2,000 random tables; the 32 symmetries of the evaluation leave score, control value, hiding and canonical key unchanged on 700 tables (300 random, 400 hidden) |

## Side tables (exhaustive listing)

A side: three observer distinctions (one holder each), a cut of 1 or 2 distinctions (one holder each on this side), I internal
distinctions (one or two holders), knots of arity 3 or 4 with law even, odd or not-all-equal. A four-knot side needs I >= 4 (at
most 3 + c + 2I places must reach 12), so the pre-registered class (<= 3 knots, I <= 3) holds only sides of up to 3 knots, and the 4-knot option was
read as <= 4 knots and I <= 5 (deviations.md, item 1). Both classes are listed in full.

| Class | Cut | Lawful structures | Distinct tables | non-empty | allocation class (flagged) | not flagged |
| --- | --- | --- | --- | --- | --- | --- |
| Census (<= 3 knots, I <= 3) | 1 | 7,023 | 596 | 595 | 160 | 435 |
| Census | 2 | 41,355 | 3,018 | 3,018 | 721 | 2,297 |
| Extended (<= 4 knots, I <= 5) | 1 | 4,501,281 | 8,647 | 8,646 | 1,810 | 6,837 |
| Extended | 2 | 27,947,475 | 51,596 | 51,595 | 10,033 | 41,563 |

(Structures by internal distinctions and knots are in `sides_c*_k*_i*.json`; counts were re-derived independently by itertools
enumeration (`sides_independent_check.py`) for cut 1 with I <= 3 and cut 2 with I <= 1 and agree: 7,023 structures / 596 tables and 180 / 112.) For each table one structure
that makes it, and one allocation-class structure if there is one, are stored in the same files.

## Pairs

Every ordered pair of tables with the same cut size. Tables were divided by their gcd (scaling a side does not change any
evaluated quantity) and old tables M = T_A T_B^T deduplicated up to scaling and the 32 symmetries of the evaluation. Counts of pairs (with an allowed old word):

| Class | Cut | Ordered pairs of exact non-empty tables | Ordered pairs of projective tables evaluated | with no allowed word | hidden | both sides allocation class (all hidden) |
| --- | --- | --- | --- | --- | --- | --- |
| Census | 1 | 354,025 | 245,025 (all) | 18 | 130,427 | 17,689 |
| Census | 2 | 9,108,324 | 6,943,225 (all) | 86 | 2,962,619 | 383,161 |
| Extended | 1 | 74,753,316 | 43,454,464, as 5,539,231 unordered pairs of 3,328 symmetry classes of tables | 225 | 2,896,072 class pairs | 500,436 class pairs |
| Extended | 2 | 2,662,044,025 | 1,582,050,625, as 216,282,717 unordered pairs of 20,798 symmetry classes (12 row blocks, all done; hidden pairs only kept) | 6,084 | 79,561,437 class pairs | 18,339,150 class pairs |

Unique normalised old tables M evaluated: census cut 1 19,270 (11,985 hidden), census cut 2 193,580 (83,104 hidden), extended cut 1
2,674,139 (1,362,597 hidden), extended cut 2 20,827,543 hidden (sum over the 12 blocks; a table can recur in several blocks).

## Predictions

| # | Verdict | Values (exact where stated) |
| --- | --- | --- |
| G | pass | see above |
| P1 cut of one: no hidden pair above 2 | **holds** | Census: 130,427 hidden pairs; largest hidden score **2** (exact); 150 hidden old tables reach 2 (42 in the allocation class), 0 exceed it (exact check of every one). Extended: 2,896,072 hidden class pairs; largest 2; 2,971 reach 2; 0 exceed. The argument for one shared distinction is in `research/REVIEW-LEADS-20261123-001C/one_shared_distinction.md`. |
| P2 reference above 2, at least 20/9 | **holds** | The reference is **20/9**: the note's four-type table written as side tables with a cut of two (below), exact, hidden. 2,000 random-start local optimizations found nothing above 2; a vertex search found nothing above 20/9 (below). |
| P3 census class, cut of two: no hidden pair above 2 | **holds** | Census: 2,962,619 hidden pairs of 6,943,139; largest hidden score **2**; in the allocation class **2**; 879 hidden old tables reach 2 (189 allocation class), 0 exceed. Extended class (all 216,282,717 class pairs): 79,561,437 hidden; largest 2; 14,774 distinct hidden old tables reach 2; 0 exceed. |
| P4 without hiding the class exceeds 2 | **holds** | Largest score without hiding **8/3** (exact) in the census at cut 1 and cut 2, and in the extended class at cut 1; largest change of a complete record 1/6; attained by 32 pairs (cut 1), 32 (cut 2). In the allocation class the largest score without hiding is **2** (all allocation pairs are hidden, and bounded by the exchangeability argument below). Also 90 / 689 / 2,087 old tables above 2 (census cut 1, census cut 2, extended cut 1) of which none in the allocation class. (The extended class at cut 2 kept hidden pairs only.) |

Example of the 8/3 table (cut 1): Alice's side has odd(x1,x3,s1), odd(h1,h2,h3), even(x2,h1,h2,h3), which forces x2 = 1; Bob's side is
the same with even(x1,x3,s1). Each side's own birth weight then depends on x1 (a tied value), the settings are not hidden, and the score is 8/3.

## Extra tests on hidden pairs that reach 2 (parity score >= 2 - 1e-9)

| Test | Cut 1 | Cut 2 |
| --- | --- | --- |
| Hidden old tables reaching 2 (extended class, distinct up to symmetry) | 2,971 (150 in the census class) | 14,774 (879 in the census class) |
| Best over all two-valued functions of the complete records (225 parity starts + 200 random starts, 4 sign patterns) | all 2,971 done: largest 2.0000000000000036 (floating rounding of 2); 0 above 2 + 1e-9 | all 14,774 done: largest 2.0000000000000044; 0 above 2 + 1e-9 |
| Extension: the same on every saved hidden table with parity score >= 1 | 12,616 of 12,616 done, largest 2.0000000000000053, 0 above 2 | 52,002 of 55,112 done (the lowest scores left), largest 2.0000000000000053, 0 above 2 |
| LP test of a common local explanation, best ten | residual 0 for all ten (a common local explanation exists) | residual 0 for all ten |
| LP test, 40 more spread over the hidden tables that reach 2 | all residual 0 | all residual 0 |

Control of the LP code: for the reference table (below) the same LP gives residual 4/27 = 0.148 (no common local explanation), so it
detects non-locality when present.

## Reference over arbitrary non-negative side tables, cut of two

* **Pre-registered method (2,000 seeded starts).** Local optimization (SLSQP, exact gradients) over side tables T_A, T_B (8 x 4,
  non-negative), hidden ratios and the exact hiding equations on M = T_A T_B^T, outcome choice re-picked each round. 1,545 of
  2,000 starts ended feasible (violation < 1e-7); the largest score is 2.0000000863 at violation 1.1e-9 (feasibility slop: projected exactly onto the hiding equations it scores 1.9999998); **none above 2**.
  So random starts do not find the tables above 2, which form a thin set (`reference_slsqp_*.log`).
* **Added method (exploratory).** For fixed hidden ratios (lam for Alice, mu for Bob) the hidden old tables are a polytope
  P(lam, mu) = {M >= 0: M(W0 - lam W1) = 0, (W0 - mu W1)^T M = 0, W1^T M W1 = 1}, every denominator of the four correlations is then
  fixed (W_a M W_b = D lam^[b=0] mu^[a=0]), the score is a convex function of M on P, and its maximum is at a vertex. Vertices
  were sampled by about 540,000 linear programs with random objectives (30 x 30 ratios in (0.5, 2), 600 each) and 580,800 more
  on 11 x 11 fine grids around the six best ratio pairs. **Best found: 20/9 at lam = mu = 1**, found only on the face
  of P(1,1) with the free-value block removed (otherwise all vertices are single-entry tables of score 2). The next distinct
  families reached 2.2191 (lam 1.087, mu 0.9916), 2.2141, 2.2014, 2.1931, 2.1876; none above 20/9. Those families are vertices with 20 to 50
  non-zero entries on 6 to 8 rows and columns (`analyze_reference.py`, `reference_vertices_distinct.json`); whether they have non-negative rank 4
  was not tested, because none exceeds 20/9. The value is a lower bound on the supremum, not a proof of it; the vertex sampling finds the
  20/9 vertex in few of its programs (it came up in the 600 programs of the grid run at lam = mu = 1, once in 5,000 programs of an earlier test, and not in
  the 800 programs of the fine run centred on it), so a higher isolated vertex could have been missed.
* **The table, as side tables (exact; `reference_final.json`).** Old table M with entries 1 at (x, y) for x, y in {001, 010, 101, 110} on an
  8-cycle; rank 3, non-negative rank 4. Side tables with a cut of two, cut values (s1 s2):
  T_A[x, s] = 1 for x = 001: s in {00, 10}; x = 010: {00, 01}; x = 101: {10, 11}; x = 110: {01, 11} (zero for other x), that is
  **x2 != x3 is forced, and if x1 != x3 then s2 = x2, otherwise s1 = x1**; T_B[y, s] = 1 exactly when (s1, s2) = (y1, y2) and
  y2 != y3 (y = 001 -> 00, 010 -> 01, 101 -> 10, 110 -> 11), that is **Bob's side copies two of his own distinctions into the cut and forces y2 != y3**.
  Exact values: hidden (both complete records, largest change 0); best parity score **20/9** with outcome masks (2, 8, 2, 14); best over all
  two-valued functions also 20/9; control weighting exactly 2; LP residual 4/27 (no common local explanation).
* A keyed-setting policy on that table (Bob's setting equal to his old value y1) changes Alice's complete record by 1/9, so the table
  is not stable under keying (run only as a check of the code; the table is not a lawful structure).
* The reference needs sides that force x2 != x3 and copy a distinction into the cut; no lawful structure of the extended class
  (<= 4 knots, <= 5 internal distinctions) makes a table that, paired with another, gives a hidden score above 2.

## The allocation class cannot violate: exchangeability (argument by the implementing agent, to be refereed)

Suppose a side holds x2 and x3 in one knot (the allocation class) and each has no other holder. Every knot law is symmetric in its
places, so swapping x2 and x3 maps the old structure to itself: T[x1, x2, x3, cut] = T[x1, x3, x2, cut]. Call this side exchangeable.
For Alice exchangeable the number of finished words with setting a = 1 and record (x, z) equals that with a = 0 and record
(x2 and x3 exchanged, z): J_1b[r, s] = J_0b[rho r, s] for a relabelling rho of her records, hence the same normalisation and
P_1b(r, s) = P_0b(rho r, s). Then both of Alice's outcome functions are functions of one record r' under the setting-0 table.
If her complete record at setting 0 has the same distribution for both of Bob's settings (hidden), draw r' from that common
distribution, then s_0 from P_00(. | r') and s_1 from P_01(. | r') independently. All four correlations are then expectations of
products of four two-valued random variables on one probability space, so the CHSH value is at most 2 for **any** outcome functions.
If both sides are exchangeable no hiding is needed (all four tables are relabellings of P_00). Consequences: (i) the allocation
class (in which the two payments are exchanged by a symmetry of the old structure) cannot give a score above 2; a violation needs
the paid distinctions x2, x3 to be held by different knots on both sides; (ii) all allocation pairs are hidden automatically
(observed: hidden pairs equal allocation pairs in every run) and their largest score is 2 without any hiding requirement (observed).

## Targeted search (exploratory; up to 6 knots, allocation class; and without the class condition)

Seeded random sides of 2 to 6 knots (uniform), arity 3 or 4, laws uniform, at most 9 internal distinctions, holder counts exact; mode
*alloc*: x2 and x3 in one knot, x1 in another (the pre-registered target); mode *free*: no condition (extension). Each pool was capped
at a number of distinct non-empty tables (14,000 in pass a, 20,000 in pass b; the cap was reached after 36 to 127 s of drawing),
then every unordered pair of symmetry classes of the pool was combined and evaluated exactly as in the census (hidden pairs kept; 6
or 12 row blocks per pool, each under 10 minutes and 12 GB). Drawing time in total about 9.4 process-minutes over the 8 pools
(longest single pool 127 s); pairing took the rest of the budget.

| Pool (cut, mode, pass) | Draws -> lawful structures -> distinct tables | Table classes | Pairs evaluated | Hidden | Largest hidden score | Hidden old tables reaching 2 (sum over blocks) | Above 2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1, alloc, a | 458,772 -> 236,053 -> 14,000 | 6,744 | 22,743,588 | 22,743,588 (all) | 2 | 4,610 | 0 |
| 2, alloc, a | 161,166 -> 89,345 -> 14,000 | 7,282 | 26,516,828 | 26,516,828 (all) | 2 | 9,242 | 0 |
| 1, free, a | 157,259 -> 114,989 -> 14,000 | 6,242 | 19,484,043 | 10,588,353 | 2 | 4,042 | 0 |
| 2, free, a | 74,741 -> 59,194 -> 14,000 | 6,883 | 23,690,996 | 12,044,317 | 2 | 4,246 | 0 |
| 1, alloc, b | 867,592 -> 446,131 -> 20,000 | 9,906 | 49,068,155 | 49,068,155 (all) | 2 | 7,355 | 0 |
| 2, alloc, b | 276,191 -> 152,898 -> 20,000 | 10,433 | 54,427,226 | 54,427,226 (all) | 2 | 17,310 | 0 |
| 1, free, b | 270,585 -> 197,280 -> 20,000 | 9,024 | 40,719,988 | 21,047,519 | 2 | 8,553 | 0 |
| 2, free, b | 122,801 -> 96,989 -> 20,000 | 9,764 | 47,672,317 | 23,356,646 | 2 | 6,471 | 0 |

Total: 1,392,879 lawful structures of up to 6 knots drawn, 152.8 million class pairs in the allocation class (all hidden, largest
score 2 exactly) and 131.6 million class pairs without the condition (67.0 million hidden, largest hidden score 2 exactly); the control
weighting never exceeded 2; every hidden table that reaches 2 was re-evaluated exactly, none exceeds it. Result: **no hidden pair above
2 in the targeted search, in the allocation class or without the class condition.** As expected from the exchangeability argument,
all allocation pairs are hidden and bounded by 2. This is exploratory: the pools are random samples of lawful sides of up to 6 knots,
not a census.

## Positive structure

None: no hidden pair exceeds 2, so the full structure, the brute-force enumeration of a finished structure, its local-explanation test
and the keyed-setting policy test on a lawful structure were not run (deviations.md, item 12).

## Commands (all from the repository root; `P` = `timeout 600 prlimit --as=12884901888 .venv/bin/python -B`, `E` = experiments directory)

```
P E/gates_a.py                       # gate row G, part 1 (20/9, code checks)
P E/sides.py 1 3 3 ; P E/sides.py 2 3 3        # census class, cut 1 and cut 2
P E/sides.py 1 4 5 ; P E/sides.py 2 4 5        # extended class (<= 4 knots, <= 5 internal)
P E/gates_b.py                       # gate row G, part 2 (brute force on 200 pairs)
P E/pairs.py c1_k3_i3 ; P E/pairs.py c2_k3_i3  # census pairs, all ordered projective pairs
P E/pairs.py c1_k4_i5 --sym                    # extended, cut 1
P E/pairs.py c2_k4_i5 --sym --hidden-only --save-min 0.999999999 --rows A B   # 12 row blocks (0 885 ... 14794 20798)
P E/extras.py 1 ; P E/extras.py 2              # general functions and LP
P E/reference.py 0 500 slsqp_0 ... (starts 0-499, 500-999, 1000-1499, 1500-1999)
P E/reference_vertices.py I0 I1 600 SEED vK    # ratio-row ranges 0-8, 8-15, 15-23, 23-30
P E/reference_fine.py LAM0 MU0 0.05 0.01 800 SEED fK
P E/reference_final.py ; P E/reference_slop_check.py ; P E/analyze_reference.py ; P E/sides_independent_check.py
P E/targeted.py CUT MODE SEED 240 14000 ; P E/pairs.py c{CUT}_t6{MODE} --sym --hidden-only --save-min 0.999999999 --rows A B   # pass a (seeds 11-14, 6 blocks)
P E/targeted.py CUT MODE SEED 240 20000 b ; P E/blocks.py c{CUT}_t6{MODE}b 12 ; P E/pairs.py c{CUT}_t6{MODE}b --sym --hidden-only ... --rows A B  # pass b (seeds 21-24, 12 blocks)
P E/pairs.py c1_k3_i3 --sym --out symcheck_c1_k3_i3 ; P E/pairs.py c2_k3_i3 --sym --out symcheck_c2_k3_i3   # symmetry-class run against the full census run
P E/summarize.py
```
