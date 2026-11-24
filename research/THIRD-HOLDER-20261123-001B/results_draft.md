# The smallest structure with a hidden excess, and whether a third holder is enough: result draft

Ticket `THIRD-HOLDER-20261123-001B`, experiment `THIRD-HOLDER-20261123-001B-E001_smallest`. Draft by the implementing
sub-agent; analysis and verdict belong to the thread. Scientific referee pending. Definitions are those of
`research/THIRD-HOLDER-20261123-001B/preregistration.md`, unchanged; readings and departures are in
`experiments/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest/deviations.md` (cited below as D1, D2, ...).
Code is in that folder (`E` below); outputs and logs in
`artifacts/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest/` (`ART` below). Every run is one process
under ten minutes and 12 GB.

## Result in one paragraph

In class S (an observer distinction may already have two old holders) a hidden excess needs no old distinction with a third
holder: the smallest structure found has **7 knots and no extra holder** (the only third holders are those the setting
births give to observer distinctions) (score **19/9**, both complete records hide the far setting,
verified by full enumeration), and with 8 knots the score reaches **20/9** (2 extra holders). The census shows that nothing
smaller exists in class S with at most 5 internal distinctions a side. In class L (every observer distinction loose) **no
hidden excess was found below the 18-knot structure**: none with both sides of at most 4 knots, none with both sides of at
most 5 knots and two shared distinctions, none in the seeded search, and the 18-knot structure cannot lose a single knot. Its
two distinctions held four times remain; **no class-L structure with every distinction held at most three times was found**,
so P1 fails as frozen. With one shared distinction no pair has a hidden excess, at any size (proved, D4). The pencil
structure gives 20/9 with hidden settings (P4 holds). The largest hidden score found anywhere is 20/9.

## Row G (run first; all pass) — `ART/gates.json`, `ART/gates.log`

| Check | Result |
| --- | --- |
| Holder bound two, sides of at most 3 knots, one shared distinction | 596 side tables (7,023 labelled structures), 130,427 hidden ordered pairs, largest hidden score **exactly 2**, none above |
| Holder bound two, two shared distinctions | 3,018 side tables (41,355 structures), 2,962,619 hidden pairs, largest hidden score **exactly 2** |
| Same listings as ticket C | the sets of tables equal ticket C's files for sides of at most 3 and at most 4 knots (596, 3,018, 8,647, 51,596) |
| Product of side tables vs full enumeration, 100 drawn pairs with a third holder | 25 pairs from each of class L and S with one and two shared distinctions (4-knot lists); every word of the four finished structures enumerated: 0 mismatches of the 16 x 16 joint record counts, 0 mismatches of stored structure vs listed table, 0 mismatches of hiding and exact score |
| Reduction vs every ordered pair | hidden pairs counted by the reduction equal those of full pairing (130,427; 691,311; 2,962,619; 6,970,674); on a test class holding excess pairs both give the same 145 excess old tables with the same scores and sizes; on the two 20,000-table pools both give none (D4) |
| Search generator | 200 pool tables re-enumerated from their stored structures: 0 mismatches |
| 18-knot structure, full enumeration (28 distinctions finished) | **20/9**, both complete records hidden, agrees with the side tables |

## Side tables and pairs

Sides: 1 to 4 knots (5 where stated), at most 5 internal distinctions, internal distinctions held one to three times, shared
distinctions held once on each side (D1). "Pairs" are ordered pairs of projective side tables (tables divided by the gcd of
their entries). Where pairs were scored through the reduction (D4), "scored" counts pairs of orbit representatives (D3) that
the reduction does not exclude; the rest are excluded by proof.

| Class | Shared | Knots per side | Labelled structures | Side tables | Ordered pairs | Method | Pairs scored | Hidden among scored | Hidden old tables above 2 | Largest hidden score |
| --- | ---: | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| L | 1 | <= 3 | 20,145 | 1,364 | 1,490,841 | every pair | 1,490,841 | 691,311 | 0 | exactly 2 |
| L | 2 | <= 3 | 74,700 | 5,170 | 21,160,000 | every pair | 21,160,000 | 6,970,674 | 0 | exactly 2 |
| S | 1 | <= 3 | 212,439 | 8,413 | 55,130,625 | proof (K = 2) | 0 | (21,174,987 hidden, all of kinds 1-2) | 0 | at most 2 |
| S | 2 | <= 3 | 502,344 | 28,426 | 630,512,100 | reduction | 32,663,568 | 131,880,938 hidden in all | 0 | exactly 2 |
| L | 1 | <= 4 | 41,591,133 | 49,081 | 1,615,396,864 | proof (K = 2) | 0 | (587,010,182 hidden) | 0 | at most 2 |
| L | 2 | <= 4 | 133,604,145 | 221,545 | 33,711,897,664 | reduction | 15,913,716 | 9,508,749 | **0** | at most 2 (859 old tables reach 2) |
| S | 1 | <= 4 | 428,105,511 | 390,107 | 112,415,360,656 | proof (K = 2) | 0 | (34,275,224,078 hidden) | 0 | at most 2 |
| S | 2 | <= 4 | 1,006,014,636 | 1,620,095 | 1,932,605,993,124 | reduction | 2,429,395,545 | 1,772,118,146 | **145** | **20/9** |
| L | 2 | <= 5 | 2,279,242,395 | 2,403,586 | 5,098,947,867,225 | reduction | 4,033,081,096 | 2,066,619,576 | **0** | at most 2 (93,615 reach 2) |

Not covered: class S with 5-knot sides (D2). With one shared distinction no excess is possible at any size (D4, case K = 2).

## Predictions

| # | Verdict | Exact values |
| --- | --- | --- |
| G | **passes** | see row G above |
| P1 Some class-L structure has a hidden excess with no distinction held more than three times | **fails** | none found: census (class L, sides <= 4 knots, and <= 5 knots with two shared distinctions, holders <= 3): 0 hidden old tables above 2; reduction from the 18-knot structure: no knot removable in any of 200 orders, its distinctions d, e keep four holders; seeded search (pools and every distinct table of the 2,000,000 class-L draws): 0 |
| P2 Class L has no hidden excess with both sides of at most 4 knots | **holds** | 0 of 9,508,749 hidden scored pairs (and 0 of 2,066,619,576 with 5-knot sides, two shared distinctions) |
| P3 Class S has a hidden excess with at most 10 knots in all | **holds** | 7 knots, score 19/9; 8 knots, score 20/9 |
| P4 The pencil 9-knot structure gives 20/9 with hidden settings | **holds** | full enumeration: 20/9, both complete records hidden (largest change 0), 64 old words, 144 finished words per setting pair |

## The smallest structures found (frozen order: knots, then extra holders)

**Class S: 7 knots, 0 extra holders, score 19/9** (census; verified by full enumeration of the four finished structures:
hidden, 19/9, agrees with the side tables, 64 old words, 144 finished words each).

- Alice: nae(x1,x2,s1), nae(x1,x3,s2), even(x2,Ah1,Ah2), odd(x3,Ah1,Ah2)
- Bob: even(y2,Bh1,Bh2), odd(s1,Bh1,Bh2), odd(y1,y2,y3,s2)
- shared: s1, s2. Holders: x1, x2, x3 and y2 two old holders each; Ah1, Ah2, Bh1, Bh2 two each; no distinction is held
  three times in the old structure. The setting births give x1 and one of x2, x3 (and y1 and one of y2, y3) one more holder.

Ten such old tables at 7 knots (up to the symmetries of the evaluation), all with 0 extra holders, scores 19/9 and 37/18.
With 8 knots the census has 135 more, including **20/9 with 2 extra holders**: Alice as above; Bob even(y2,Bh1,Bh2),
odd(y3,Bh1,Bh2), odd(s2,Bh1,Bh2), even(y1,y2,y3,s1) (Bh1, Bh2 held three times). Fewest extra holders found by number of
knots in class S: 7: 0, 8: 0, 9: 1, 10: 1, 11: 4, 12: 3, 13: 3, 14: 6, 15: 7, 18: 8. Smallest number of extra holders at
any number of knots: **0** (at 7 knots).

**Class L: 18 knots, 8 extra holders, score 20/9** (the 18-knot structure of ticket A; full enumeration: hidden, 20/9).

- Alice: even(x1,a,b), even(c1,a,b), even(k1,a,b), even(x2,d,e), odd(x3,d,e), even(c2,d,e), odd(c3,d,e), nae(c1,c2,n2),
  nae(k1,c3,n1), even(n2,g,h), odd(s2,g,h), even(n1,u,v), odd(s1,u,v)
- Bob: even(y1,p,q), even(s1,p,q), even(y2,r,t), even(s2,r,t), odd(y3,r,t)
- a, b, r, t held three times; d, e four times. It is the only class-L structure with a hidden excess found. Smallest number
  of extra holders at any number of knots in class L: **8** (no other was found).

## Lower bounds from the census

- **Class L:** no hidden excess with both sides of at most 4 knots; none with both sides of at most 5 knots and two shared
  distinctions; none with one shared distinction at any size (proof). All with at most 5 internal distinctions a side and at
  most three holders.
- **Class S:** no hidden excess with at most 6 knots in all. A side with two shared distinctions needs at least two knots,
  and one shared distinction cannot give an excess, so every structure of at most 6 knots has both sides of at most 4 knots
  and lies in the census, which found none below 7. So **7 knots is the minimum** in class S for sides of at most 5
  internal distinctions and at most three holders, and at 7 knots no extra holder is needed.

## Reductions — `ART/reduce_*.json`, `ART/reduce_verified.json`

200 orders each (seeds 2026112320 to 2026112519). From both starts no single knot can be removed, so every order ends at the
start (1 distinct final structure each, verified by full enumeration).

| Start | Single removals | Results |
| --- | --- | --- |
| 18-knot (class L) | 18 | 6 would leave an observer distinction without an old holder; removing a copy knot (even(c1,a,b), even(k1,a,b), even(c2,d,e), odd(c3,d,e)) loses both hidings (score 682/323 without hiding); the other 8 keep the hiding but drop the score to exactly 2 |
| pencil (class S) | 9 | 3 would leave an observer distinction without an old holder; removing even(x2,d,e) or odd(x3,d,e) loses Alice's hiding (score 14/11); the other 4 keep the hiding with score exactly 2 |

## Seeded search — `ART/search_*.log`, `ART/sides_search_*.json`

2,000,000 lawful sides per class (seed 2026112321; D7). Distinct non-empty tables in all draws: class L 194,822 (one shared
distinction) and 313,906 (two); class S 244,949 and 369,435. Pools of the first 20,000 distinct tables, filled at draws
123,237 / 81,430 (L) and 101,942 / 70,274 (S), each paired over every ordered pair:

| Pool | Projective tables | Pairs of representatives | Hidden | Above 2 | Largest hidden score |
| --- | ---: | ---: | ---: | ---: | --- |
| L, 1 shared | 15,736 | 187,470,864 | 69,588,071 | 0 | at most 2 |
| L, 2 shared | 16,026 | 214,739,716 | 70,662,536 | 0 | at most 2 |
| S, 1 shared | 15,797 | 193,822,084 | 69,250,253 | 0 | at most 2 |
| S, 2 shared | 16,221 | 218,862,436 | 64,935,427 | 0 | at most 2 |

**Extension (exploratory, beyond the cap; D8):** every distinct table of the draws with two shared distinctions, paired by
the reduction. Class L: 112,119,710 pairs scored, none above 2. Class S: 154,166,994 scored, 145 hidden old tables above 2,
largest 56/27, smallest 8 knots with 2 extra holders (43/21); sizes from 8 to 15 knots. Nothing smaller than the census
structures.

## Commands (from the repository root)

```
E=experiments/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest
ART=artifacts/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest
R="timeout 600 prlimit --as=12884901888 .venv/bin/python -B"
gcc -O3 -ffp-contract=off -shared -fPIC -o $ART/chsh_kernel.so $E/chsh_kernel.c
gcc -O3 -o $ART/sides_enum $E/sides_enum.c
gcc -O3 -march=native -ffp-contract=off -o $ART/pair_eval $E/pair_eval.c
# listings: CLASS CUT KMAX IMAX HMAX
for c in 1 2; do $R $E/sides.py L $c 3 3 2; $R $E/sides.py L $c 4 5 2; done
for k in L S; do for c in 1 2; do $R $E/sides.py $k $c 3 3 3; $R $E/sides.py $k $c 4 5 3; done; done
for p in "0 16" "16 32" "32 48" "48 64"; do $R $E/sides_parts.py L 2 5 5 3 64 $p; done; $R $E/sides_parts.py L 2 5 5 3 64 64 64
# pairs, small classes (numpy)
for t in L_c1_k3_i3_h2 L_c2_k3_i3_h2 L_c1_k3_i3_h3 L_c2_k3_i3_h3; do $R $E/pairs.py $t --mode full; done
for t in L_c1_k3_i3_h2 L_c2_k3_i3_h2 L_c1_k3_i3_h3 L_c2_k3_i3_h3 S_c1_k3_i3_h3 L_c1_k4_i5_h3 S_c1_k4_i5_h3; do
  $R $E/pairs.py $t --mode lemma --count-hidden --out ${t}__${t}_lemma; done
$R $E/pairs.py S_c2_k3_i3_h3 --mode lemma          # earlier form of the script (D14)
# pairs, large classes (compiled): prep lists the runs in pc_<name>_meta.json; eval NAME RUN or eval NAME Q0 Q1; merge
$R $E/pairs_c.py prep L_c2_k4_i5_h3; $R $E/pairs_c.py eval L_c2_k4_i5_h3__L_c2_k4_i5_h3_lemma 0
$R $E/pairs_c.py prep S_c2_k4_i5_h3                # runs 0-5 and 11; class pairs 3207-3312 in ranges of 5 (D10)
$R $E/pairs_c.py prep L_c2_k5_i5_h3 --per-run 60000000   # runs 0-66
for t in search_L_c1 search_L_c2 search_S_c1 search_S_c2; do $R $E/pairs_c.py prep $t --full --per-run 80000000; done  # runs 0-2
for t in search_L_c2 search_S_c2 search_L_c2_all search_S_c2_all; do $R $E/pairs_c.py prep $t --per-run 80000000; done
$R $E/pairs_c.py merge <name>                      # for every pc_<name>_meta.json
# reduction, search, checks, report
for s in eighteen pencil; do $R $E/reduce.py $s 2026112320 2026112520; done; $R $E/verify_reduced.py
$R $E/search.py L 0 2000000; $R $E/search.py S 0 2000000
$R $E/gates_mix.py; $R $E/pairs_c.py prep mixS; $R $E/pairs_c.py prep mixS --full   # then eval and merge
$R $E/gates.py; $R $E/report.py
```

Outputs: `ART/report.json` (all tables above, the smallest structures with their full enumeration), `ART/structures_found.json`
(every distinct structure with a hidden excess found, 292, as lists of knots), `ART/pc_*_summary.json` and
`ART/pairs_*_summary.json` (each pairing), `ART/gates.json`. Large regenerable files were removed (`ART/PRUNED.md`).

## What this is about

Supplied, as in the pre-registration: the weighting, the settings as births, the two classes, the bound of three holders,
the size order, the reduction orders and the seeded samples. The census is finite: its bounds are sides of at most 4 knots
(5 in class L with two shared distinctions), at most 5 internal distinctions, at most three holders. The class-S minimum of
7 knots holds within those bounds; the class-L null holds within them and in the samples, and says nothing about larger
class-L structures with every distinction held at most three times.
