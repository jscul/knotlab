# Points interact only through a shared line

Status: The frozen prediction **failed** (computed, sampled pairs; the order test exhaustive per pair); a corrected locality is
**proved by hand**. `check.py` (8 seconds), ticket C of `research/COMPOSITE-FN-20261110-001/preregistration.md`, frozen in commit
`36d02b296` before any run: B112's observation, made after `MANY-POINTS-20261110-001B`'s run, re-tested as a prediction.

## What is checked

Fresh composites: the outer host K_2 with two composites C(3, leaf), for the Fano and thin (2,1,2) leaves; four floors each, written by
the frozen search; at each floor 150 pairs of flipped points at distance 2 or more and 50 at distance 1 (1,600 pairs). Classes and the
rule D as in `MANY-POINTS-20261110-001B`.

## Results

| Pairs | Independent | Cancel | Bind | Meet |
| --- | --- | --- | --- | --- |
| distance 2 or more (1,200) | 1,199 | 0 | 0 | 1 |
| of these, sharing a face (19) | 19 | 0 | 0 | 0 |
| distance 1 (400) | 23 | 249 | 126 | 2 |

L2 held (94% of distance-1 pairs interact). **L1 failed, and with it the frozen failure line was crossed:** one pair at distance 2 (thin
leaves, floor {0, 1, 3}, points 81 and 89, both in the second composite) did not combine. Each flip alone is repaired by one flip (points
76 and 80), and I = 0, and every order is legal, but the two repairs together leave the space two units above the floor. The points share
no line, but the repair of point 89 flips point 80, which shares a line with point 81. So "points interact only through a shared line" is false as stated.

## The corrected locality (by hand)

For a move, its **support** is the set of lines and faces whose terms in the dissonance weight W it can change: a state flip at a point
r touches r's three lines and the three faces at r's corners; a learning step on side e of line i touches line i and e's two end faces.
For a disturbance p repaired by D_p, let supp(p) be the union of the supports of p's flip and of D_p's moves.

**Lemma L.** If each repair reaches the floor alone and supp(p) and supp(q) are disjoint, then I = 0, every interleaving of D_p and D_q is a sequence of legal moves that never
raises W, and it ends at the floor. If moreover D_p and D_q change no sign, the floor's address is kept.

*Proof.* W is a sum of one term per line and one per face, and a move changes exactly the terms in its support. A term in supp(p) reads
only variables that p's side changes: if a move on q's side changed one, that term would lie in its support. So at every point of any
interleaving, the terms in supp(p) have the values they had at the matching point of D_p alone, and likewise for q. Each move therefore
changes W by what it did alone, which is negative; a learning step's legality (its line violated, or an end face even) reads only terms
in its support, so it is legal as it was alone; and at the end W exceeds the floor by the sum of the two single excesses, which are zero.
With no sign changed, the law and so every atom's role is the floor's. ∎

Disjoint supports are not the same as distance 2: a point's repair can reach a line through the other point. The failing pair is
such a case. The
correction to `MANY-POINTS-20261110-001`'s wording is logged in `docs/CORRECTIONS.md` (Narrowing).
