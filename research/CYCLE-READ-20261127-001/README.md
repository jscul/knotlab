# Reading a growth from its start on pieces with a cycle, and a fresh test of the twin exception

Epic `CYCLE-READ-20261127-001`, under G17 with G1, at the coordinator's pick after `GRADED-ORDER-20261126-001`. Design
and predictions frozen before any start below is scored; the code is `GRADED-ORDER-20261126-001`'s (`order.py`,
`twins.py`, `graded.py`), extended as stated. Results go in a section of their own after the run.

## The reading

The **node reading** (`GRADED-ORDER-20261126-001`): build the start's finite core's births round by round with Lemma R's
round rule (`REDUCE-BLOCKS-20261119-001A`, items 1 and 3) from the round-1 groups and offshoots, each birth a node; count
births along endless chains with `late.py`'s binomial terms on those nodes; a finished piece's one last core birth
relays. On a piece with a cycle the core may never finish: the round rule keeps making births whose union is the whole
piece (on a ring of n knots, the literature's intervals of the infinite path that covers the ring, counted up to its
shift by n). Here the core is built to rank 25 (enough for 24 rounds).

**Changes before the freeze, from the advisor's review** ([question](advisor/question_freeze.md),
[answer](advisor/answer_freeze.md); nothing had been scored):
1. **The relay is decided by the core, not by `late.py`'s count.** `late.py` calls a piece a cycle by a count on its
   blocks and cells; some such pieces have cores that finish with one last birth, which relays as on a tree. So a piece
   relays exactly when its core finishes with one last birth holding the whole piece, it holds no chains, and the law
   is not-all-equal or another piece is present; a core that does not finish by rank 25 never relays.
2. **Chains on a core that does not finish are not read.** There a birth can hold two copies of a chained point (its
   set in the unrolled map holds it twice) and so two chains, while the node's points are a set. Such starts are
   reported as *not predicted*, never as agreements or misses; reading them needs the unrolled map's copies.
3. **The cap is a count.** A core whose round rule lists more than 20,000 families (core births) is *unending* and not
   predicted; no time limit decides a start. (Lowered from 200,000, at which one start took over five minutes.)
4. The twin flag takes a pair of twins as chained when any of its shared pairs of parents has the chain (it took the
   first pair only); twins are found from each pair of parents' common children (the same pairs, faster). The same
   flag on the 417 earlier sample starts still finds exactly the two known starts, and the node reading's scores on
   the 76 held-out `grow` starts are unchanged.
The first-coded reading (relay keyed to `late.py`'s count, chains on unfinished cores read with points as sets) is also
scored, as a check of the advisor's analysis (Y4, Y5).

## Part 1: pieces with a cycle (frozen)

**Population** (structure only before the freeze; nothing scored):
- the late-views study's uniform held-out six-knot starts with a piece with a cycle (41, grown there under both laws and
  never predicted) ([cyc6_uniform.jsonl](cyc6_uniform.jsonl));
- seven-knot `tree+` starts with a piece with a cycle, seed 20261129, 20,000 draws, up to 50 a bucket by the number of
  such pieces and whether they hold chains, repeats removed up to renaming: 52 ([cyc7_treeplus.jsonl](cyc7_treeplus.jsonl));
- seven-knot `grow` starts, the same, 200,000 draws: 66 ([cyc7_grow.jsonl](cyc7_grow.jsonl)).
Each is grown to round 24 under both laws with the look-alike study's growth (the late-views rows for the six-knot set),
at most two minutes a start: one `tree+` start under not-all-equal and four under parity were not grown in that time and
are *not run*.

**Strata, read off the start before the freeze** ([strata.py](strata.py), [strata.txt](strata.txt)):

`late.py` calls a piece a cycle by a count; the round rule decides whether its core finishes. A core is *unending* when
the round rule lists more than 5,000 families or a round's births share parents in more than 250,000 pairs (counts; the
cap was lowered from 200,000 births before the freeze after one start passed five minutes).

| Starts | Core finishes | Does not finish by rank 25, no chains on it | The same, chains on it (not predicted) | Unending (not predicted) | Chained twins |
| --- | ---: | ---: | ---: | ---: | ---: |
| six knots, uniform (41) | 41 (23 with chains) | 0 | 0 | 0 | 11 |
| seven knots, `tree+` (52) | 32 (1 with chains) | 6 | 0 | 14 | 0 |
| seven knots, `grow` (66) | 53 (10 with chains) | 1 | 2 | 10 | 0 |
| all (159) | 126 | 7 | 2 | 24 | 11 |

So 133 starts are predicted: 122 without chained twins (Y1) and 11 with them (Y2).

| # | Prediction | Fails when |
| --- | --- | --- |
| Y1 | The node reading agrees in every round read, both readings, both laws, on every predicted start without chained twins (55%) | any such start differs |
| Y2 | It differs on every predicted start with chained twins, if any (80%) | one agrees |
| Y3 | Every miss under Y1, if any, is on a start with twins or chains on a piece with a cycle (60%) | a miss with neither |
| Y4 | The first-coded relay misses `tree+` draw 335 at round 2 under not-all-equal and agrees under parity, and misses six-knot entry 13560 at round 5 under not-all-equal; the reading of item 1 agrees on both (advisor; 65%) | any of these fails |
| Y5 | The first-coded chain count, with the core built to rank 10 (its core is unending by rank 25), misses `tree+` draw 109 (a ring with a chained knot hung on it) by round 9 under both laws (advisor; 60%) | it agrees through round 9 under either law |

The count of unending cores among these starts is read off the start, so it is reported (Part 3), not predicted (the
draft's Y3, "at most 10", was withdrawn before the freeze for this reason).

## Part 2: the twin exception, fresh (frozen)

**The explanation under test** (found after the two misses, post hoc): the node reading fails exactly on starts with
**chained twins**, two core births of one round that share two parents C and D with a chain base in the points of a
common parent of C and D. Since then referee R2 of `GRADED-ORDER-20261126-001` proved that without chained twins the
core's groups are those of the core alone, that at the first chained twins the parent roster always changes (whether
the counts show it is open), and built two more failing starts, both with chained twins. What is still computed, not
proved, is the chain counting, including the fresh counts of births with core and chain parents. So the test can fail
both ways: a start without chained twins that differs (a fault in the chain counting) and a start with them that agrees.

**Population** (structure only; nothing grown before the freeze): two weightings, every start of the earlier samples
excluded up to renaming, buckets by the twin flag and whether chains are present, up to 40 a bucket, cores over 5,000
births excluded and counted:
- **W1**, the standard `tree+` weighting of `WEIGHTINGS-20261119-001B` at nine knots, seed 20261130, 20,000 draws:
  890 new distinct accepted starts whose pieces are all trees, of which 49 have chained twins, 175 unchained twins, 643
  none, 22 an unending core and one was not run (a 120-second backstop); kept 192 ([twin9_draw.jsonl](twin9_draw.jsonl)):
  40 with chained twins, 40 with unchained twins and no chains, 32 (all found) with unchained twins and chains, 40
  without twins with chains, 40 without twins or chains.
- **W2**, the scaffold `tree+s50` (`tree+` with one more loose distinction on each knot with chance one half) at eight
  knots, seed 20261131, 6,000 draws, the same buckets ([twin8_draw.jsonl](twin8_draw.jsonl)): drawn by that fixed
  command after this text was frozen, structure only, and added before any of its starts is grown: 3,347 new distinct
  accepted starts, 15 with chained twins, 31 with unchained twins, 3,167 with none, 133 unending, one not run; kept 126
  (15 chained, 25 unchained without chains, 6 unchained with chains, 40 without twins with chains, 40 without either).
Each kept start is grown to round 24 under both laws with the look-alike study's growth, two minutes a start at most.
Starts without twins and without chains are read by the proved core theorem and the proved relay alone, so they check
the code; the starts with chains test the chain counting. The twin flags are computed with the predictor's own node construction (`twins.py` uses
`order.NodePiece`), so a fault shared by both would pass unseen; the referee is asked to flag twins independently.

| # | Prediction | Fails when |
| --- | --- | --- |
| T1 | The node reading agrees in every round read, both readings, both laws, on every start without chained twins (70%) | any such start differs |
| T2 | It differs within the rounds read, under at least one law, on every start with chained twins (85%; the advisor's 90%) | one agrees through the rounds read under both laws |
| T3 | On each chained-twin start where it differs, the first difference is at the round equal to the least rank of its chained twins, under each law where it differs (60%) | an earlier or later first difference |
| T4 | T1 and T2 hold under each weighting separately (scaffold check; implied) | — |

## Part 3: how often a core is unending

The count, among accepted drawn starts whose pieces are all trees, of those whose core passes the cap: reported with the
weighting, the size, the cap (5,000 core births; a count, not a time) and both counts (distinct starts, and draws with
repeats, the weighting's own count). Under the standard weightings `tree+` and `grow` of `WEIGHTINGS-20261119-001B`
at seven to ten knots, and the scaffold `tree+s50` (one more loose distinction on each knot with chance one half) at
seven and eight.

## Prior work in the program

Searched before the freeze, `--exclude CYCLE-READ-20261127-001`:

`python3 -B scripts/track.py objects "pieces with a cycle unrolled ring"`
`python3 -B scripts/track.py objects "two sunflowers share two knots"`
`python3 -B scripts/track.py objects "two births share two parents chain grandparent" --until 2026-11-26`

- `RING-IDENT-20261119-001` (proved) and `RING-PAIR-20261119-001` (computed): the cheapest parity growth on starts with a
  cycle in their scope is read off the clusters of the unrolled candidate map, a round's births the deck orbits of its
  clusters. That is the reading this study's Part 1 is checked against where scopes meet; the node reading differs by
  building births from the round-1 groups (cells included) and by not unrolling, which is why chains on a core that does
  not finish are not read here (the unrolled map holds the copies).
- `CLUSTER-ALL-20261119-001` (computed): the extended cluster rule is exact on 24,383 five-knot arrangements and breaks
  "where two sunflowers share two knots (a block with a missing pair carries two junctions on one cluster)"; the node
  reading was built to carry two births with one union, which is that case.
- `PLUS-ONE-20261118-001` (computed): chains of offshoots born apart combine when partners share a neighbour; the
  chained-twin mechanism (chain births of two parents that share a parent a round earlier) is a case of chains combining.
- `GRADED-ORDER-20261126-001` and its referees R1 and R2: the node reading, its two misses, the conditional core theorem
  and its converse; this study's direct predecessor.

## Results (added after the run)

### Part 1: pieces with a cycle

[Scores](scores.jsonl) ([tally.py](tally.py)); [Y4, Y5 and the twins' rank](checks45.txt) ([checks45.py](checks45.py)).
Nothing was changed after scoring.

| Stratum (159 starts) | Starts | Node reading, both laws | Prediction |
| --- | ---: | --- | --- |
| core finishes, no chained twins | 115 | agrees in every round read on all 115 | Y1 holds |
| core does not finish by rank 25, no chains on it | 7 | agrees in every round read on all 7 | Y1 holds |
| core finishes, chained twins (all six-knot) | 11 | **differs on all 11, under both laws, first at round 5**, the least rank of their chained twins on every one | Y2 holds |
| core does not finish, chains on it | 2 | not predicted | — |
| core unending (over the cap) | 24 | not predicted (5 of their 48 growths were also not run) | — |

- **Y1 holds:** 122 of 122 predicted starts without chained twins, 244 start-and-law cases, every round read (24, or
  to a parity closing). That includes 23 starts with chains on a piece `late.py` counts as a cycle and 7 whose core
  does not finish (rings in the unrolled sense), read with no relay.
- **Y2 holds:** the 11 starts with chained twins, all from the six-knot uniform set, differ under both laws, first at
  round 5, which is the least rank of their chained twins on each. **Y3 holds** (no miss outside it).
- **Y4 holds as the advisor worked it out:** the first-coded relay misses `tree+` draw 335 at round 2 under
  not-all-equal and agrees under parity, and misses six-knot entry 13560 at round 5 under not-all-equal; the frozen
  reading agrees on both under both laws. **Y5 holds:** the first-coded chain count misses draw 109 at round 9 under
  both laws (with the core built to rank 10); the frozen reading does not read it.

So on pieces with a cycle the node reading is exact wherever it reads, and its only misses are the chained twins:
the late-views study's six-knot cycle starts it could not predict are now read, except 11 with chained twins.

### Part 2: the twin exception, fresh

[Scores](scores2.jsonl) ([tally2.py](tally2.py), [tally](tally2.txt)). Nothing was changed after scoring.

| Weighting | Starts without chained twins | Of them with chains | Agree, both laws, every round | Starts with chained twins | Scored | Differ, both laws | First difference at the twins' least rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| W1, `tree+`, nine knots | 152 | 72 | **152** | 40 | 32 | **32** | **32** |
| W2, `tree+s50`, eight knots | 111 | 46 | **111** | 15 | 10 | **10** | **10** |

- **T1 holds** under both weightings: 263 of 263 starts without chained twins agree in every round read under both laws,
  including the 118 with chains, where the chain counting (computed, not proved) is what is tested, and the 103 with
  unchained twins.
- **T2 holds** on every scored start: all 42 with chained twins differ, under both laws. Twelve were not scored: the
  growths of eight W1 and four W2 chained-twin starts did not finish in two minutes (*not run*; every growth not run in
  Part 2 is of a chained-twin start, since those carry both chains and twins and grow most), and one W2 start's core
  passed the pairs cap at scoring (the draw ran before that cap was added; *not predicted*).
- **T3 holds** on all 42: the first difference is at the round equal to the least rank of the start's chained twins,
  under each law. **T4 holds**: the same under the standard weighting and the scaffold.

### Part 3: how often a core is unending

A core is unending here when the round rule lists more than 5,000 families (core births) before it finishes; a
120-second backstop marks a start *not run*. Counted among accepted drawn starts whose pieces are all trees (the
late-views class), by draw with repeats (the weighting's own count) and by distinct start ([the tallies](part3/)):

| Weighting | Knots | Draws | Unending, accepted draws with repeats | Unending, distinct starts |
| --- | ---: | ---: | --- | --- |
| `grow` | 7 | 3,000 (seed 31) | 0 of 234 | 0 of 231 |
| `grow` | 8 | 3,000 | 0 of 157 | 0 of 156 |
| `grow` | 9 | 3,000 | 0 of 149 | 0 of 149 |
| `tree+` | 7 | 3,000 | 0 of 2,278 | 0 of 144 |
| `tree+` | 8 | 3,000 | 0 of 2,162 | 0 of 253 |
| `tree+` | 9 | 3,000 | 9 of 2,077 (0.4%), 1 not run | 5 of 417 (1.2%), 1 not run |
| `tree+` | 9 | 20,000 (seed 20261130, W1's draw) | 55 of 13,562 (0.4%), 1 not run | 22 of 890 new (2.5%) |
| `tree+` | 10 | 3,000 | 35 of 1,969 (1.8%), 4 not run | 30 of 583 (5.1%), 3 not run |
| `tree+s50` (scaffold) | 7 | 3,000 | 25 of 2,281 (1.1%), 2 not run | 24 of 1,513 (1.6%), 2 not run |
| `tree+s50` (scaffold) | 8 | 3,000 | 74 of 2,161 (3.4%), 3 not run | 74 of 1,924 (3.8%), 3 not run |

So under the program's two standard weightings an unending core does not occur up to eight knots in these draws; under
`tree+` it is about 0.4% of accepted draws at nine knots and 1.8% at ten, and it grows with the extra loose
distinctions of the scaffold. Among the 159 starts with a piece with a cycle (stratified samples, not a weighting's
count), 24 have an unending core. Every unending core seen is explosive: its rounds' births multiply (9, 11, 13, 17, 22,
38, 127, 720 on one `tree+` start), as in the explosive starts of `WALL-READ-20261119-001`.

### What is proved and what is computed

1. **Proved** (`GRADED-ORDER-20261126-001`, referee R2): without chained twins the core's groups are those of the core
   alone; at the first chained twins the parent roster changes.
2. **Computed, now on fresh frozen samples**: the node reading is exact on every read start without chained twins
   (122 with a piece with a cycle, 263 fresh tree-piece starts of two weightings, the 415 earlier ones), chains
   included; it differs on every scored start with chained twins (11, 42, and the four earlier), first at the twins'
   least rank. The chain counting, and so the whole reading without chained twins, is not proved.
3. **Not read**: chains on a core that does not finish (two starts here), unending cores, and the chained-twin starts'
   own growth.

### An intuition (a link, not evidence)

Each group of three or more that the round rule makes is a family of births that pairwise share a parent and share no
parent in common: in the literature's terms, a failure of the Helly property of the family of parent sets (a family is
Helly when every pairwise-meeting subfamily has a common member). An unending core keeps making more such failures each
round than it merges, which is the literature's divergence of iterated clique graphs (Neumann-Lara's octahedra, already
linked to explosive starts by `WALL-READ-20261119-001`; Escalante's theorem that clique-Helly graphs converge is the
matching statement on the other side). Chained twins are a Helly failure that only a chain creates: the twins and
their parents' one-step chain births pairwise share parents and have none in common. Cheapest test: on the Part 3
draws, whether the number of groups of three or more in the first few rounds already separates the unending cores from
the rest.
