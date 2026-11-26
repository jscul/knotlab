# Recursion's lead: does growing and then exchanging give a start back?

Epic `RECURSION-LEAD-20261126-001`, at the coordinator's pick after `LAYERS-20261126-001`, on the owner's question whether
recursion exists in the framework. A check by the thread, not a registered study; computed. The sections down to
"Frozen" were committed, after the advisor's review in the repository ([question](advisor/question.md),
[answer](advisor/answer.md)), before the frozen runs.

## The rungs

The owner: "So that's repetition, but we don't have recursion yet." Repetition is the same kind of whole-held fact at
two layers; a tower is a step carrying any layer to the next; recursion is a pattern that grows back into itself, or
whose product is fed back as its own start. The coordinator: a return under a pinning we choose is a curiosity; a return
with nothing supplied would be recursion.

## The lead

`SECOND-CHECK-20261126-001` (refereed): grow a ring of knots one round under parity (G), then read each shortest allowed
change of the grown stage as a knot holding the distinctions it changes (the exchange E), with the loose values pinned;
for rings of five, seven and eight knots, E(G(ring)) is the ring again. [`recur.py`](recur.py) runs G and E (the record's
exchange, recomputed by shortest cycles of the graph reading and checked equal to the record's on 28 stages).

## Seen before the freeze (exploration)

- **Rings return, nothing else does.** With loose pinned: rings of 5, 7, 8, 9 and 10 knots with two loose distinctions
  each return; at 6 the exchange gives a new six-knot start that then closes; at 4 the exchange is not lawful (a knot of
  fewer than three places or a distinction held by three). Rings with three or four loose each map to the ring with two,
  which is fixed. Every tree tried (12) and every pair of joined rings: not lawful. With loose free: never lawful.
- **The pinning is always ours.** Every birth under every recorded arm has at least three places (the fresh count is never
  below max(0, 3 − p): `rival_growth.py`, `cut`), except a birth whose law the present ones already fix. So no recorded
  law fixes a loose value.
- **The advisor's explanation (by hand, to check).** Where every round-1 group is a pair, the pinned E∘G is the line graph
  of the start's sharing pattern: each exchanged knot is a pair of shared distinctions at one start knot. A connected
  pattern equal to its line graph is a cycle (classical), so only rings return: the return is bookkeeping of the
  exchange, not recursion. It also predicts that a chain of knots is lawful and shrinks, and that the ring of 6 fails
  because knots 0, 2 and 4 form one group of three.
- **The tower re-read** ([`tower2.py`](tower2.py)): under a second reading of a small change (every allowed change of at
  most five distinctions) a ring of 5 keeps no class at rounds 1 and 2, a ring of 7 none at round 1 and one at round 2;
  whole-held facts at most one in every case tried.

## Frozen

**Sets.** Every census start of three to five knots (7,075) and the 900 fresh starts of six to eight knots of the layers
study (`forbid.sampled`, seed 20261206 + n), one round of ordinary growth under parity; for the tower, a seeded sample of
400 census starts (`random.Random(20261208)`), the 16 starts with four or more classes, and the built joined rings, at
rounds 1 to 3.

**Predictions.**
- **R1.** With loose pinned, E(G(S)) is S up to renaming only where S is one ring of five or more knots (not six) with
  two loose distinctions at every knot.
- **R2.** With loose free, E(G(S)) is never lawful.
- **R3.** With loose pinned, E(G(S)) is lawful only where no knot of S holds more than two shared distinctions (S a chain
  or a ring). Reported: which lawful ones reach a fixed start, a cycle, or stop.
- **T1.** Under both readings of a small change, no start read has two or more independent whole-held facts at rounds 1
  to 3.

**Stop.** A start breaking R1, R2, R3 or T1; or none. A start that returns without being a ring would be the first
non-bookkeeping return; a start with two whole-held facts would be the first step of a tower.

**What a pass would and would not show.** That the only recorded return is the ring's, under a pinning we supply, and
explained by the line-graph fact; so recursion with nothing supplied is not found. It would not show that no law or
exchange could make one, and it reads one round.

## What was found

Five runs ([`recur_census.jsonl`](recur_census.jsonl), [`recur_heldout.jsonl`](recur_heldout.jsonl),
[`tower_census.jsonl`](tower_census.jsonl), [`tower_multi.jsonl`](tower_multi.jsonl),
[`tower_rings.jsonl`](tower_rings.jsonl)), scored by [`score.py`](score.py) ([`score.json`](score.json)).

**The stop is met: R1, R2 and R3 break.**
- **R1.** One census start that is not a ring returns: census entry 165, four knots, three of them sharing pairwise with a
  dead knot among them and the fourth hung on the dead knot (loose 0, 2, 2, 2). Its pinned exchange after one round has
  four knots in the same pattern with the same loose counts. No ring of the census returns (the census holds no ring of
  five knots with two loose each), and none of the 900 fresh starts returns or gives a lawful pinned exchange.
- **R3.** Of the 56 census starts with a lawful pinned exchange, 46 have a knot holding three or more shared
  distinctions, so the advisor's line-graph reading (pairs of shared distinctions at one knot) does not cover them. Their
  exchanges are smaller starts (one to five knots) that stop within two steps: they close, stall or become unlawful.
- **R2.** With loose values free, 12 census starts give a lawful exchange; each becomes a new start that closes, stalls or
  is unlawful at the next step. None returns.

**T1 holds.** Under both readings of a small change (the shortest changes, and every change of at most five
distinctions), at rounds 1, 2 and 3, no start read has more than one whole-held fact: 400 sampled census starts, the 16
multi-class starts and the built joined rings. So the tower's negative survives the swap of the reading and two more
rounds: it is about the growth at these sizes, not only about one reading.

**What it says about recursion.** Every return found, the rings of the second-check study and census entry 165, needs two
things we supply: the exchange itself (reading each shortest change as a knot is our operation, not the growth's) and
the pinning of loose values, which no recorded law makes. With nothing pinned, no start returns or cycles. So on the
owner's rungs this is a curiosity, not recursion: a pattern that grows back into itself with nothing supplied is not
found. The ring that returns under laws added by hand (lesson 8.7) is the record's other lead, also with a supplied law.
