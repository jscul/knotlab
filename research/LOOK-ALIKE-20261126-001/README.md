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
