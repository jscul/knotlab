# Which starts look alike to a local reader

Epic `LOOK-ALIKE-20261126-001`, at the coordinator's go-ahead on the selected direction of
[`HOW-MUCH-ARRIVES-20261126-001`](../HOW-MUCH-ARRIVES-20261126-001/decision.md) after its referee. A check by the
thread, not a registered study; computed; referee pending. The sections "Design" and "Expected" were written and
committed before any start was grown for this study.

## Why

The lamp study's referee found that two touching three-place knots and three such knots in a row, read without
names, make the same births in every round from round 4 to 32, while a ring of six with one leftover distinction,
and two rings of five with the same proved rate, never agree with their partners beyond the count. A local reader,
one who sees each birth's kind, parents, fresh distinctions and places but not its descent, can therefore not tell
some starts apart once grown, and can tell others apart forever. Which? Where far details become one case for a local
reader is the owner's "logically small" galaxy made exact.

## What it rests on, and what it adds

- **Refereed:** `REDUCE-BLOCKS-20261119-001` (Lemma R, confirmed): from round 1 on the cheapest growth reads a start
  only through its live knots, their open counts and which sets of them share a common neighbour; a shortage is a
  stall; after round 1 a new knot sees only its parents. So two starts with the same such data grow identically, by
  name, from round 1. That is the finest identity; this study asks for a coarser one, what a local reader keeps.
- **Referee pending:** `READ-ORIGIN-20261120-001` (proved): at a complete round every start that could have led to
  it gives the same future, and the holdings do not in general mark which knots were the start. That compares
  different pasts of one present; this study compares different starts' futures as a local reader sees them.
- **The lamp study** gave the readings and the first pair.

## Design

**Population.** The census of small starts (`COPYING-PARTS-20261123-001A`'s `cpcensus.py`): a connected graph on
the knots, one shared distinction for each pair it joins, zero to three loose distinctions on each knot, at least
three places on every knot, each start once up to its symmetries. Phase 1: all starts of one to four knots (1 + 3 +
19 + 200 = 223). Phase 2 (held out): five-knot starts, 3,157 in all, sampled if the full set does not fit the hour.

**Growth.** Ordinary growth only: the ordinary count, not-all-equal, nothing taken, to round 20 or 30,000 knots. A
round in which some knot would give more loose distinctions than it holds is a stall, and the growth stops there; no
waiting.

**Kind.** From the counts per round: stalls; closes; dimension D, when over the last eight rounds read the count's
(D − 1)-th differences are one positive constant (D = 1 to 4); a rate x, when the ratio of successive counts stays
within 0.01 over the last four, above 1.05; otherwise unread.

**Reading a pair.** For two starts of one kind, in each reading (sig0: kind, parents, fresh distinctions, places;
sig1: and the parents' sig0): the first round r₀ from which, in every round read by both, one start's births are
contained in the other's (**agree up to the count**), and the first from which they are equal (**agree exactly**);
"never" when the last round read by both is not one of them. Pairs read for fewer than ten common rounds are set
apart.

**Phase 1** reads every pair of one kind among the 223 and looks for a criterion: a property of a start, computable
from the start or its first few rounds, that predicts which pairs agree up to the count. **Phase 2** freezes that
criterion in this note, as an addendum committed before phase 2 runs, and tests it on every pair of one kind among
the five-knot starts read. **Stop:** the frozen criterion predicts every phase-2 pair, or a pair it misses.

## Expected (written before any start was grown)

1. **Control:** two starts with the same live knots, open counts and live-neighbour sets (Lemma R's data) agree
   exactly from round 1, in both readings, wherever the census has such a pair.
2. **Dimension one:** every pair agrees up to the count, by round 6.
3. **Dimension two:** not every pair agrees; at least one pair of starts of at most four knots never does in 20
   rounds.
4. **Rates:** among starts of one rate, some pairs never agree.
5. **Early:** where a pair agrees up to the count, it does so by round 8; a local reader can tell early whether two
   starts will ever look different.
6. **The readings:** sig0 agrees no later than sig1 for every pair (it reads less).

## Phase 1: what was found (exploratory)

All 223 starts of one to four knots were grown to round 20 ([`phase1_grown.jsonl.gz`](phase1_grown.jsonl.gz)) and
every pair of one kind read in both readings ([`pairs.py`](pairs.py), [`phase1_pairs.jsonl.gz`](phase1_pairs.jsonl.gz)).
Kinds: 42 stall (all of four knots), 38 of dimension one, 134 of dimension two, 7 of three and 2 of four; none
closes and none grows at a fixed rate. Under not-all-equal a lone three-place knot does not close: it grows in
dimension two (3, 3, 1, 1, 2, 3, … births a round).

| kind | pairs | sig0: agree up to the count by round 8 / later / never | sig1: by round 8 / later / never | agree exactly (either reading) |
|---|---|---|---|---|
| dimension one | 703 | 201 / 0 / 502 | 173 / 0 / 530 | 79 |
| dimension two | 8,911 | 6,141 / 440 / 2,330 | 3,533 / 2,916 / 2,462 | 382 |
| dimension three | 21 | 9 / 0 / 12 | 9 / 0 / 12 | 9 |
| dimension four | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 |

**The control** ([`control_r.py`](control_r.py)). 116 pairs of grown starts have the same live knots, open counts
and maximal live-neighbour sets up to relabelling (Lemma R's data). All 116 are identical in sig0 from round 1, and
the 76 that do not stall are identical in sig1 from round 2 (round 1's sig1 reads the start knots' own places, which
Lemma R's data leave out). No such pair is of two different kinds.

**What a local reader sees of a grown start.** Read by kinds, late rounds are few kinds of birth, each counted by a
polynomial in the round. In dimension two (sig0) the 134 starts have six late shapes: two-parent joins with two
fresh distinctions growing by a fixed number a round, plus a constant number of one-parent offshoots (2 for 67
starts, 4 for 37), sometimes with constant defects (a group of three and a two-parent join with three fresh
distinctions, 13 starts; a two-parent join with one fresh distinction, 7); or, for starts with a larger block of
knots that share a neighbour, joins of up to seven parents growing in binomial proportions. Every start's view
settles: from some round K on, every kind's count is the polynomial fitted through rounds K − D + 1 to K and holds
through round 20; K is at most 12 in sig0 and 14 in sig1, for all 181 starts of a dimension.

**Expectations so far.**
1. *Control.* Held in sig0; in sig1 from round 2 (above).
2. *Dimension one: every pair agrees by round 6.* **Failed:** 502 of 703 pairs never agree in sig0. Dimension-one
   growths differ in what their constant rounds are made of.
3. *Dimension two: some pair never agrees.* Held (2,330 in sig0).
4. *Rates.* Not testable here: no start of at most four knots grows at a rate.
5. *Agreement by round 8.* **Failed:** 440 pairs agree in sig0, and 2,916 in sig1, only later, where the counts of
   two growths of different slopes cross.
6. *sig0 no later than sig1.* Held in all 9,636 pairs.

**The criterion this suggests.** Whether two starts agree up to the count is decided by their settled views: two
lists of polynomials, one for each kind of birth. That is a finite description, read from the first 14 rounds, of
what a local reader sees of the whole unending growth. It is frozen below for the held-out test.

## Addendum: the criterion, frozen before phase 2

Written and committed before any five-knot start was grown for phase 2 (sixty were grown once to time the run; their
results were deleted unread).

**The view.** A start's view in a reading is, for each round, the count of each kind of birth. For a start of
dimension D the view **settles at round K** when, for every kind, the polynomial of degree D − 1 through its counts
at rounds K − D + 1 to K gives its count at every later round read. Phase 2 grows every five-knot start of the census
to round 24 or 30,000 knots.

1. **Settling.** Every five-knot start of a dimension has a view that settles at some K ≤ 12 in sig0 and K ≤ 14 in
   sig1, and its fitted polynomials hold through round 24.
2. **The pair rule.** For two starts of one dimension, the first round from which they agree up to the count, as
   computed from their counts through round 14 and their fitted polynomials after it, equals the round observed
   through round 24, in every pair.
3. **Rates** are outside the criterion; any five-knot start that grows at a rate is reported, and its pairs read, but
   not predicted.

**Stop.** Both hold for every start and pair of a dimension: the criterion predicts each pair. A start whose view
does not settle in the rounds read, or a pair whose observed round differs from the rule's, is the miss.

Of the two, the first carries the content. The second follows from the first wherever both views settle by round 14
and nothing changes after; it is the check that the comparison as stated is the right one.

## Phase 2: the held-out test

All 3,157 five-knot starts of the census were grown under ordinary growth to round 24 or 30,000 knots
([`phase2_grown.jsonl.gz`](phase2_grown.jsonl.gz)), and the frozen criterion applied by [`phase2.py`](phase2.py)
([`phase2.json`](phase2.json)). Kinds: 1,587 stall; 409 of dimension one, 1,003 of two, 110 of three, 34 of four;
three grow at a rate (1.26, 1.38 and 1.62, the last the golden-ratio ring of five), one of each, so no pair of one
rate exists; 11 are unread (counts still changing their ratio when the run stopped).

**1. Settling: failed for seven starts.** 1,549 of the 1,556 starts of a dimension settle within the frozen bounds in
both readings. Seven of dimension two settle at round 14 in sig0 and 16 in sig1, inside the rounds read but past the
bounds of 12 and 14. All seven have the same counts: 11, 15, 45, 120, 210, 252, 210, 120, 45, 10, 1, then 1, 2, 3, …:
from round 3 to 11 the binomial numbers of ten things taken two to ten at a time, a burst of one block of ten live
knots that all share a neighbour, ending in one join of all ten, after which the growth goes on as a lone knot does.
The burst is longer than any at four knots, and the view cannot settle until it ends.

**2. The pair rule: every pair in sig0, all but 5,614 in sig1.** Of 592,495 pairs of one dimension, the rule computed
from counts through round 14 and fitted polynomials after gives the observed round of agreement for every pair in
sig0, and for 586,881 in sig1. All 5,614 misses are among the 6,993 pairs that include one of the seven late starts,
whose sig1 view had not settled by round 14.

| kind | pairs | sig0: agree by round 8 / later / never | sig1: by round 8 / later / never | sig1 missed |
|---|---|---|---|---|
| dimension one | 83,436 | 18,458 / 0 / 64,978 | 13,446 / 0 / 69,990 | 0 |
| dimension two | 502,503 | 269,995 / 36,172 / 196,336 | 125,261 / 176,612 / 200,630 | 5,614 |
| dimension three | 5,995 | 2,098 / 0 / 3,897 | 2,098 / 0 / 3,897 | 0 |
| dimension four | 561 | 276 / 0 / 285 | 276 / 0 / 285 | 0 |

**The stop is met, at a miss.** The criterion as frozen fails for seven starts and the 5,614 pairs that include them;
it predicts every other pair. What fails is the bound on the settling round, not the idea: the seven views do settle,
two rounds after the burst of their block ends.

**Few far views.** Read by kinds in the last rounds, the 1,003 five-knot starts of dimension two show 16 distinct late
views in sig0 (the 134 of up to four knots, 6). The commonest, 549 starts, is two-parent joins growing plus two
offshoots a round, the late view of a lone three-place knot; the next, 176 starts, has four offshoots a round, that of
two touching knots. Dimension one shows 29 late views among 409, three 3 among 110, four 2 among 34.

## Expectations, all

1. *Control (Lemma R's data):* held in sig0 from round 1, sig1 from round 2 (phase 1).
2. *Dimension one: every pair agrees by round 6:* failed (phase 1, 502 of 703 never; phase 2, 64,978 of 83,436).
3. *Dimension two: some pair never agrees:* held.
4. *Rates: some pairs never agree:* not testable; no two starts share a rate.
5. *Agreement by round 8:* failed in both phases, where counts of different slopes cross later.
6. *sig0 no later than sig1:* held in phase 1 (not re-tallied in phase 2).
7. *Addendum, settling within 12 and 14:* failed for seven five-knot starts with a burst of a block of ten.
8. *Addendum, the pair rule:* held for every sig0 pair and every sig1 pair without one of the seven.

## How this bears on what growth keeps of its start

Lemma R (refereed) says the growth reads a start only through its live knots, their open counts and which sets of
them share a neighbour: everything else about a start leaves no mark on what grows. This study finds that a local
reader, who sees each birth's kind, parents, fresh distinctions and places, keeps much less: once the bursts of the
start's blocks are over, only a late view, a few kinds of birth each counted by a polynomial in the round. Different
starts with the same late view differ to that reader only by their counts, and most starts of dimension two share one
of two late views. The study of reading a start back (`READ-ORIGIN-20261120-001`, proved, referee pending) found that
different pasts of one present give one future; here different starts give one local future up to a count. Both say
that what lies behind, in descent, is small to what comes after, read where it is.

**Reading (not tested here).** The settling round looks set by the largest block of live knots sharing a neighbour:
a block of m bursts through the binomial numbers of m and ends in one join of all m, and the view settles a few
rounds after (for the block of ten, the burst ends at round 11 and the view settles at 14 in sig0 and 16 in sig1). A
criterion from the start alone would bound the settling round by the size of its largest block plus a small constant;
that is a candidate for the next study to freeze and test.
