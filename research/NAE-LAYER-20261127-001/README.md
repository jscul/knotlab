# Facts held by the whole under not-all-equal, and a second layer

Epic `NAE-LAYER-20261127-001`, at the coordinator's pick after `ONE-STATEMENT-20261127-001`. A check by the thread, not
registered; computed. The sections down to "Frozen" were committed before the runs.

## The question, and the advisor's answer ([question](../ONE-STATEMENT-20261127-001/advisor/question_nae.md), [answer](../ONE-STATEMENT-20261127-001/advisor/answer_nae.md))

Under not-all-equal no law is a sum of others, so parity's facts (sums kept by every small change) have no analogue to
lean on. The advisor expects no second layer beyond the first composed with itself: (a) no function is kept by every
small change, since a knot blocks at most one place of a state; (b) every exact relation among the loose
distinctions' values is a composition over a part with no ring (two knots sharing one distinction hide it as one
not-all-equal knot with one side reversed), and a ring erases it, the reverse of parity, where rings carry the facts;
(c) no pair of distinctions is tied. Its smallest concrete case is T7, a tree of seven three-place knots on which three
relayed facts g_0, g_1, g_2 (each read on one loose distinction and two of a hung knot's) should never be all + or all
−, though every pair is free. It says that even so the triple is not a new layer: it is the first knot's own law read
through relays (whenever g_i is nonzero it fixes distinction i). Census start 959, the one start whose not-all-equal
states admit a second presentation, is the record's Pasch pattern (its distinctions fall into three pairs no knot holds
together; exchanging one pair's members exchanges the two presentations).

## Frozen

**Predictions (the advisor's, unverified until run)** ([`t7.py`](t7.py), [`census.py`](census.py)).
- **N1.** T7 has 4,374 not-all-equal states.
- **N2.** Its nine loose distinctions show 510 of 512 patterns.
- **N3.** (g_0, g_1, g_2) takes 25 of 27 triples, missing (+,+,+) and (−,−,−); every pair takes 9 of 9.
- **N4.** With 11 renamed 9 (a ring of five closes), the seven loose distinctions show all 128 patterns.
- **N5.** T7 stalls in round 1; with 15, 16 and 17 added to its three middle knots it has 55,566 states, shows 4,094 of
  4,096 loose patterns, and after one round its stage's loose distinctions show every pattern.
- **C1 to C3, on every census start under not-all-equal.** One class under single-distinction changes; no tied pair;
  the loose distinctions show 2^m − 2 patterns on tree-shaped starts (no cycle of shared distinctions, no two knots
  sharing two) and 2^m on the others. **C4**, on the first 500 census starts that grow a round (stages of at most 14
  loose distinctions): every loose pattern after it. **C3'** for comparison: under parity 2^(m − 1) on every start with
  loose distinctions.

**Stop and rung.** All as predicted: under not-all-equal a fact held by the whole is a composed relation over a part
with no ring, the first layer read through relays, which rings and growth erase; that is repetition, and no second
layer. A missing pattern where none is predicted (on a ring, or after a round) is a relation a ring or growth carries,
the second-layer candidate, frozen and tested on its own.
