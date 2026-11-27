# Facts held by the whole under not-all-equal, and a second layer


> **Referee R1: refuted, two Blocks** ([report](referee-R1/report.md)). Every frozen number reproduces (all 7,075
> census starts; every current loose pattern on all 5,111 funded first rounds). **Block:** "the only relations are
> compositions over parts with no ring, and nothing survives one round of growth" is false: on the census's three-knot
> ring, one ordinary birth makes a fresh distinction that takes part in a relation among three readings on disjoint
> distinctions, seven of eight triples across 44 states, every pair free; removing any one of the four laws restores
> the missing triple, and it stays missing through round four ([certificate](referee-R1/carrier_birth.json)). The test
> here read only the current loose set, which a ring frees; it never tested relations among carriers using shared
> distinctions. **Block:** "growth erases": every funded round keeps the projection onto earlier distinctions (each
> birth can satisfy its law at its own fresh distinction), so the patterns missing on the original distinctions stay
> missing (a six-knot chain: the same two of 1,024 through round four); it is each round's new loose set that is free.
> **Narrowings:** the census's tie test was implied by its class test; only the chosen seven-knot tree was tested for
> relayed values; weighted claims need a carrier and a weighting (a four-knot chain breaks the advisor's independence on
> ring-free starts, 1/81 against 1/729); "fixes the knots but keeps no fact" becomes "the census recovers 7,074 of 7,075
> marked presentations; ordinary not-all-equal growth can bind readings on separate carriers; their selection and
> iteration remain open". The bound readings are not kept by single changes, and growth admits three equivalent choices
> of them.

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

## What was found

Every frozen prediction held exactly ([`t7.json`](t7.json), [`census.jsonl`](census.jsonl)).
- **T7.** 4,374 states (N1); its nine loose distinctions show 510 of 512 patterns (N2); (g_0, g_1, g_2) takes 25 of 27
  triples, missing exactly (+,+,+) and (−,−,−), with every pair taking all 9 (N3). With 11 renamed 9 a ring of five
  closes and all 128 loose patterns occur (N4; 2,178 states). T7 stalls in round 1; with 15, 16, 17 added it has 55,566
  states and shows 4,094 of 4,096 loose patterns, and after one round its stage of 16 knots shows all 32,768 (N5).
- **The census.** On all 7,075 starts the not-all-equal states form one class under single-distinction changes (C1) and
  no pair of distinctions is tied (C2); on all 6,845 starts with loose distinctions the loose patterns number 2^m − 2 on
  the 15 tree-shaped ones and 2^m on the other 6,830 (C3); after one round all 2^m occur on all 500 starts read (C4).
  Under parity 2^(m − 1) on every start (C3').

**So, under not-all-equal.** A fact held by the whole is a relation among separately carried values that no proper part
implies: on a part with no ring it exists (exactly two loose patterns missing), and it is the first knots' own law read
through relays (whenever a relayed value is nonzero it fixes the first knot's distinction), not a new law. A ring
erases it, and so does one round of growth, since growth's joins close rings. Nothing is kept by small changes (one
class) and nothing is tied. **On the owner's rungs:** repetition, in the weak form of the first layer composed with
itself; no second layer; and growth removes even the composed relation after one round. Under parity it is the reverse:
rings carry the facts, and growth makes them last.

**Not run.** Starts past the census; rounds past 1; readings of a fact other than relations among values (the equal
weighting of states and its correlations, which the advisor describes but which were not tested here).
