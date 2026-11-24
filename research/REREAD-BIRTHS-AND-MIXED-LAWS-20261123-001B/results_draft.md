# Can ordinary growth with both laws reach the structures with a hidden excess?: draft result

Ticket `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B`, experiment `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001`, 2026-11-23.
Draft written by the implementing sub-agent from the frozen [pre-registration](preregistration.md) (commit 43762c5b04). The
verdicts below apply its "Fails when" column to the data; the thread judges them. Referee pending. Readings taken where the
note was open, and one settled statement found false, are in
[deviations.md](../../experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach/deviations.md).
Outputs: `artifacts/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach/`
(`summary.json` collects every number below).

**Ordinary growth does make structures with a hidden excess from founder starts that have none.** One round from a
7-knot start whose table is hidden with score exactly 2 makes a single birth, a three-place knot on Bob's y1 and y2 with
one fresh distinction; when that knot is not-all-equal the stage is the 8-knot target itself, up to renaming, and the score is
exactly 55/27 with both complete records hidden (full enumeration). Ten 8-knot targets are grown this way (scores 55/27
and 109/54), twenty more from starts that already had an excess, and 34 histories in all reach a hidden excess their
start did not have. The seven-knot structure is not reachable: each of its 19 founder starts already allows more observer
words than it does, and growth never changes that set.

Two versions are reported. **c2** is the frozen one: each newborn even parity or not-all-equal. **c3** gives each newborn
even parity, odd parity or not-all-equal, because the note's statement that the parity sign is a renaming fails after the
first round (deviations item 4). The verdicts are the same in both.

## Denominators

| What | c2 | c3 |
| --- | ---: | ---: |
| Targets (THIRD-HOLDER list; the seven-knot structure is entry 0, the pencil 9-knot structure entry 291) | 292 | 292 |
| Founder starts grown (connected proper subsets holding all six observer distinctions) | 49,961 | 49,961 |
| Proper subsets counted and not grown: an observer distinction missing / not connected | 1,049,680 / 102,975 | same |
| Founder starts with a distinction held three or more times (grown with every two holders meeting) | 37,814 | same |
| Histories that made at least one round | 13,205 | same |
| History ends: past 20 distinctions / 3 rounds / whole-round stall / no live knot | 21,398 / 651 / 27,887 / 25 | same |
| Stages tested (stage 0 included) / grown stages | 67,303 / 17,342 | same |
| Law assignments tested over all stages (tables) / at grown stages | 2,029,891 / 1,979,930 | 15,631,067 / 15,581,106 |
| Histories whose assignments were drawn (more than 4,096) | 26 | 2,111 |
| T2 target stages of at most 16 distinctions (stage, assignment) / distinct structures within each run of 5,000 starts | 22,817 / 18,667 | 43,549 / 30,653 |
| T2 observer choices tested, unordered / ordered | 85,090 / 680,720 | 153,102 / 1,224,816 |
| T2 draw stages (280 funded draws x 2 founder laws; stages 0 and 1 of at most 16 distinctions) | 1,812 | 4,777 |
| T2 observer choices in the draw stages | 0 | 0 |

In the draw stages 229 (c3: 447) have an exactly tied pair, 6 (18) have two tied pairs on four different distinctions,
and none has two tied pairs that no one knot touches, so no observer choice passes the frozen rule there.

## Verdicts

| # | Prediction | Verdict | Evidence |
| --- | --- | --- | --- |
| G | Checks of the code | **Holds** | Each of the 292 targets taken whole gives its recorded score exactly, hidden (and the census's recorded table, up to the evaluation's 32 symmetries, for the 290 that have one). The projected table agrees with word-by-word enumeration on 100 of 100 drawn grown stages (13 to 24 distinctions). Support never shrinks, and never changes, along any history: 0 of 1,979,930 (c2) and 0 of 15,581,106 (c3) grown-stage tables against the same assignment one stage before; 0 of 1,446,561 draw assignments and 61 closing births. Extra checks: the extended end equals the recorded one on all 12,147 starts with at most two holders; batched and single contractions agree on 880 tables; the evaluator agrees with the recorded scorer on 2,004 tables. |
| P1 | No proper founder start of the seven-knot structure reaches its table in support | **Holds** | 19 founder starts; each allows 24, 36 or 48 observer words against the target's 16, and growth keeps that set. Reasons per start below. |
| P2 | No proper founder start of any target gives a hidden excess at any stage | **Fails** | Trivially at stage 0: 630 founder starts are themselves structures with a hidden excess under the target's observers. Substantively: 34 histories (28 targets) from starts with no hidden excess reach one at a grown stage, 354 tables (c3: 1,212 tables, the same 34 histories); the smallest is written out below. |
| P3 | No grown stage examined in T2 gives a hidden excess | **Fails, by inheritance only** | 4 grown stages (c3: 6) give 20/9 with a tied-pair observer choice; in each, the same choice already gives 20/9 at stage 0 of the same history. No grown stage gives a hidden excess its start did not have under the same observers. The smallest is written out below. |

## The smallest new hidden excess, in full

Target 79 of the list (8 knots, recorded score 55/27):
Alice: nae(x1,x2,s1), nae(x1,x3,s2), even(x2,Ah1,Ah2), odd(x3,Ah1,Ah2).
Bob: nae(y1,y2,Bh1), even(y1,y3,Bh2), odd(y2,s2,Bh2), odd(y3,s1,Bh2).

- **Start** (founder start 2236, bitmask 239): the target without nae(y1,y2,Bh1): 7 knots, 11 distinctions, loose
  distinctions y1 and y2 (each held once). Its observer table has the target's support (16 observer words), both
  complete records hide the far setting, and its score is exactly 2.
- **Round 1.** The two live knots even(y1,y3,Bh2) and odd(y2,s2,Bh2) are adjacent (both meet odd(y3,s1,Bh2)); the round
  makes one birth on them, taking y1 and y2, with one fresh distinction f11.
- **Law assignment.** The newborn not-all-equal: nae(y1,y2,f11). (Even parity gives the start's table, score 2.)
- **Stage 1**: the eight knots above with nae(y1,y2,f11) in place of nae(y1,y2,Bh1), 12 distinctions; it is the target
  up to renaming f11 as Bh1 (incidence and laws matched).
- **Observers**: Alice x1, x2, x3; Bob y1, y2, y3. **Setting births** (supplied): nae(x1, x2, za) or nae(x1, x3, za);
  nae(y1, y2, zb) or nae(y1, y3, zb). y1 and y2 then have three holders.
- **Result, by enumerating every word of the four finished structures** (14 distinctions; 120, 108, 120 and 108
  allowed words): both complete records have the same distribution for either far setting (largest change 0), and the
  best four-correlation score over parity outcomes is exactly **55/27**. The contraction gave the same table and score.
- Stages 2 and 3 of the same history keep 55/27 for every assignment with this newborn not-all-equal (2 of 4 and 8 of 16
  tables), and those tables stay proportional to the target's.

## Targets grown exactly

In 30 histories a grown stage (stage 1, one not-all-equal newborn) is a target itself up to renaming its non-observer
distinctions. All 30 targets have 8 knots and are a 7-knot start plus one three-place not-all-equal knot on two of
Bob's observer distinctions and one distinction of its own.

| Start's stage 0 | Targets | Scores of the grown target |
| --- | ---: | --- |
| No hidden excess (hidden, score exactly 2) | 10 (79 to 88) | 55/27 (2), 109/54 (8) |
| Already a hidden excess at stage 0, under the same observers | 20 | 58/27 (2), 19/9 (2), 56/27 (8), 37/18 (8) |

Four more histories (targets 171 and 172, 10 knots, starts with an excess) reach a table proportional to the target's
without being the target. In all, 34 histories (32 targets) reach the target's table only by growth, 3,377 grown tables
(c3: 24,147) are proportional to their target's, and 649 starts already have the target's support at stage 0.

All 34 histories with a new hidden excess: one each for the twenty 8-knot targets 79 to 98 (55/27 for 79, 80, 89, 90;
109/54 for the others; ten of the twenty are the exact growths above), two each for targets 193 (109/54), 224 (109/54),
250 (1765/882), 273 (109/54), 278 (883/441 and 631/315) and 285 (757/378 and 541/270), and one each for 235 (2059/1029)
and 264 (127/63); these eight targets have 11 to 15 knots and their starts 8 to 13 founders. In all 34 the first new
excess is at stage 1, and the share of tables with an excess at stages 2 and 3 equals the share at stage 1.

**Verification by full enumeration.** c2: 322 of the 354 new-excess tables (stages of 12 to 29 distinctions) were
checked by enumerating every word of their four finished structures; every one is hidden with an exact score above 2,
and the word counts and score equal the contraction's. On the 254 stages of at most 22 distinctions the separate
enumeration of each finished structure gave the same counts. The other 32 are the tables of one history (start 20633 of
target 250, stage 1, 32 distinctions, 1765/882 by contraction) and rest on the contraction. Scores of the 322: 109/54
(237 tables), 55/27 (44), 2059/1029 (16), 883/441 (8), 1765/882 (4), 127/63 (4), 631/315 (4), 541/270 (3), 757/378
(2). c3: of its 1,212 new-excess tables, 957 were written out (at most 50 per stage and kind); 857 of those were
enumerated in full, all hidden with an exact score above 2 and equal to the contraction; the 100 on stages of 29 and 32
distinctions, and the 255 counted but not written, rest on the contraction.

## Why each seven-knot founder start fails

The seven-knot structure: nae(x1,x2,s1), nae(x1,x3,s2), even(x2,Ah1,Ah2), odd(x3,Ah1,Ah2) | even(y2,Bh1,Bh2),
odd(s1,Bh1,Bh2), odd(y1,y2,y3,s2). Its table allows 16 observer words. Two facts decide every start:

- **The support.** Every founder start allows more observer words (48, 36 or 24) and ordinary growth keeps the set of
  allowed words on existing distinctions (checked on every history), so no stage of any history has the target's
  support, whatever the laws given to the newborns.
- **No left-out knot can be born.** Six of the seven knots hold no distinction of their own (every distinction they hold
  has a second holder in the structure), and a newborn under the not-all-equal rule always has a fresh distinction.
  even(x2,Ah1,Ah2) and odd(x3,Ah1,Ah2) share two distinctions, as do even(y2,Bh1,Bh2) and odd(s1,Bh1,Bh2), so each pair can
  only be founders. The seventh, odd(y1,y2,y3,s2), holds y1 and y3 alone and is in every start.

| Start (bitmask) | Knots left out | Observer words allowed (target 16) | History: knots per stage; outcome | Largest hidden score met |
| ---: | --- | ---: | --- | --- |
| 67 | even(x2,Ah1,Ah2), odd(x3,Ah1,Ah2), even(y2,Bh1,Bh2), odd(s1,Bh1,Bh2) | 48 | 3, 8, 15; past 20 distinctions | 0.667 |
| 71 | odd(x3,Ah1,Ah2), even(y2,Bh1,Bh2), odd(s1,Bh1,Bh2) | 48 | 4, 9, 14; past 20 | 0.680 |
| 75 | even(x2,Ah1,Ah2), even(y2,Bh1,Bh2), odd(s1,Bh1,Bh2) | 48 | 4, 8, 11, 12; 3 rounds | 0.684 |
| 78 | nae(x1,x2,s1), even(y2,Bh1,Bh2), odd(s1,Bh1,Bh2) | 24 | 4, 8, 12; past 20 | 1.333 |
| 79 | even(y2,Bh1,Bh2), odd(s1,Bh1,Bh2) | 24 | 5, 8, 11, 12; 3 rounds | 1.385 |
| 83 | even(x2,Ah1,Ah2), odd(x3,Ah1,Ah2), odd(s1,Bh1,Bh2) | 48 | 4, 9, 15; past 20 | 0.667 |
| 87 | odd(x3,Ah1,Ah2), odd(s1,Bh1,Bh2) | 48 | 5; stall at round 1 | 0.667 |
| 91 | even(x2,Ah1,Ah2), odd(s1,Bh1,Bh2) | 48 | 5, 10, 14; past 20 | 0.667 |
| 94 | nae(x1,x2,s1), odd(s1,Bh1,Bh2) | 24 | 5; stall | 1.000 |
| 95 | odd(s1,Bh1,Bh2) | 24 | 6, 10, 15; past 20 | 1.444 |
| 99 | even(x2,Ah1,Ah2), odd(x3,Ah1,Ah2), even(y2,Bh1,Bh2) | 48 | 4, 9, 14; past 20 | 0.727 |
| 103 | odd(x3,Ah1,Ah2), even(y2,Bh1,Bh2) | 48 | 5; stall | 0.667 |
| 107 | even(x2,Ah1,Ah2), even(y2,Bh1,Bh2) | 48 | 5; stall | 0.667 |
| 111 | even(y2,Bh1,Bh2) | 24 | 6, 11; past 20 | 1.333 |
| 115 | even(x2,Ah1,Ah2), odd(x3,Ah1,Ah2) | 36 | 5, 8, 12; past 20 | none hidden |
| 119 | odd(x3,Ah1,Ah2) | 36 | 6, 10, 15; past 20 | none hidden |
| 123 | even(x2,Ah1,Ah2) | 36 | 6; stall | none hidden |
| 125 | nae(x1,x3,s2) | 24 | 6, 10, 14; past 20 | 1.333 |
| 126 | nae(x1,x2,s1) | 24 | 6, 9, 12; past 20 | 1.333 |

For some left-out knots the start knots they meet are not even pairwise adjacent in the start's end, so no birth could
have them as parents (starts 83, 87, 91, 95, 99, 103, 107, 111, 125, 126; `seven_reasons.json`). The last column is the
largest hidden score over every stage and law assignment of the history, in floating point (none is within 10^-6 of 2).

## T2: any grown stage

| | c2 | c3 |
| --- | ---: | ---: |
| Target stages with an exactly tied pair / two tied pairs on four distinctions / two tied pairs no knot joins | 16,692 / 5,857 / 2,408 | 32,387 / 10,064 / 4,360 |
| Observer choices hidden (unordered) | 78,252 of 85,090 | 141,516 of 153,102 |
| Stages giving a hidden excess (stage 0 / grown) | 12 (8 / 4) | 14 (8 / 6) |
| Grown stages whose excess is inherited from stage 0 (same observers) | 4 of 4 | 6 of 6 |
| Largest hidden score | 20/9 | 20/9 |
| Symmetry check: 8 orientations of drawn choices agree | 2,073 of 2,073 | 2,073 of 2,073 |

The smallest grown stage with a hidden excess in T2 (c2 and c3): founder start 6375 of target 176 (bitmask 1013), stage 1,
newborn even parity: even(x2,x3,Ah6), odd(x2,Ah3,Ah6), nae(x1,x3,s2), nae(x1,s1,Ah3), even(s2,Bh1,Bh2), even(y1,Bh1,Bh2),
odd(y1,y2,y3,s1), odd(y3,Bh1,Bh2), even(y2,f12,f13); 9 knots, 14 distinctions. Observers: Alice x1, Ah3, x3 (Ah3 and x3
always unequal); Bob y2, y1, y3 (y1 and y3 always unequal); no knot holds distinctions of both. Full enumeration of the
four finished structures (16 distinctions, 144 words each): hidden, 20/9. The same observers give 20/9 at stage 0 (the
start, 8 knots, 12 distinctions, 72 words each), so the excess is the start's, carried through the round. Every T2 excess
was verified this way (12 of 12 in c2, 14 of 14 in c3).

## Largest hidden scores met

| Where | c2 | c3 |
| --- | --- | --- |
| Grown stage, start with no hidden excess (target observers) | 55/27 | 55/27 |
| Grown stage, any start (target observers) | 58/27 (targets 39 to 42, stage 1, from 7-knot starts with 19/9) | 58/27 |
| Seven-knot founder starts, any stage | 1.444 in floating point (start 95) | same |
| T2, any stage and tied-pair observers | 20/9 | 20/9 |

## The parity sign of a newborn (checked once)

On the 153 histories of the ten 7-knot targets and the pencil with at most 9 newborns (361 stages), the observer tables
met with even / odd / not-all-equal newborns equal those met with even / not-all-equal at stage 0 (153 stages) and stage
1 (100), and are more at 88 of the 88 stage-2 stages and 20 of the 20 stage-3 stages (never fewer); a table met only with
an odd newborn was confirmed word by word. So the sign is a renaming while the newborn's fresh distinctions are loose (a
newborn of the last round made), and stops being one once a knot of a later round takes a fresh distinction: renaming
it would change that knot too, and a not-all-equal knot with one place renamed is not a not-all-equal knot. Neither
version changes a verdict; c3 adds tables (1,212 new-excess tables against 354) but no new history.

## What this is about

About the recorded ordinary growth operator on the named founder starts, at most 3 rounds, under the stated scaffolds:
the setting births, the weighting (every allowed word of the finished structure equal), the law given to each newborn
(every assignment, or 4,096 drawn), the founders' laws kept from the targets, the wrapper's placement of founders' loose
distinctions (other placements not tried; 7 of the 34 new-excess histories had a placement choice the table could see),
the reading of a distinction held three or more times in a start, and T2's restriction to exactly tied observer pairs
(under which the draws offer no observer choice at all). The structures reached are reached from founder starts that are
themselves taken from the list; nothing here says that growth from an arbitrary start reaches one.

## Not done

- Other placements of a founder's loose distinctions among its children (deviations item 6).
- Full enumeration of the 32 new-excess tables of one history with 32 distinctions (c2), and of the c3 tables on stages
  of 29 or 32 distinctions or not written out; they rest on the contraction.
- The re-reading law of ticket A (left for later by the pre-registration).

## Commands

Run from the repository root, in this order (every run under `timeout 600 prlimit --as=12884901888`; chunks as listed):

```bash
E=experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach
W="timeout 600 prlimit --as=12884901888 .venv/bin/python -B"
$W $E/build_targets.py
$W $E/gates.py                                   # row G parts 1 and 2, extra checks E1-E3
$W $E/sign_check.py                              # deviations item 4
$W $E/measure_growth.py                          # growth sizes, to plan chunks
for lo in 0 5000 10000 15000 20000 25000 30000 35000 40000 45000; do
  $W $E/grow_t1.py --lo $lo --hi $((lo+5000))                # c2
  $W $E/grow_t1.py --lo $lo --hi $((lo+5000)) --choices 3    # c3
  $W $E/t2.py --pop targets --lo $lo --hi $((lo+5000))
  $W $E/t2.py --pop targets --lo $lo --hi $((lo+5000)) --choices 3
done
$W $E/t2.py --pop draws; $W $E/t2.py --pop draws --choices 3
$W $E/support_draws.py
# full enumeration, one line of artifacts/.../verify_c2_jobs.txt, verify_c2_jobs_d29.txt or verify_c3_jobs.txt per run:
#   $W $E/verify_excess.py --tag c2 <line>      $W $E/verify_excess.py --tag c3 <line>
$W $E/verify_t2.py --tag c2; $W $E/verify_t2.py --tag c3
$W $E/seven_reasons.py
$W $E/report.py
```
