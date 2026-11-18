# How far the weave's rim pushes bond distance: pre-registration

Epic `RIM-EXCESS-20261118-001` (the coordinator's go-ahead on `WEAVE-HEIGHTS-20261118-001`'s direction 1; G1; tests A39 and A97),
18 November 2026. Frozen before the run. The canonical K1–K3 test is unchanged.

## The question

On weave patches without holes, bond distance is at least steps apart + 1 (proved, `WEAVE-HEIGHTS-20261118-001`), but lone pairs of
opposite classes facing each other can be unbonded or bonded too far (steps + 2 from ten knots, steps + 3 from twelve,
`DOUBLE-MEET-20261118-001` and its referee). Which pairs carry the excess, how large can it be, and does it grow without limit?

## What was found while designing it

- A bond's tight cyclic order is a geodesic polygon of weight exactly 3(m − 2) (Lemma P); the excess is that polygon's extra length over
  the round trip, in units of 3; a least bond's members lie within detour 3e of the round trip (Lemma C). This gives a bond search with
  no state enumeration (ticket A), which matched brute force on 3,119 pairs of random small discs.
- On every disc of ten knots, all 12 pairs with an excess are lone pairs of opposite classes facing each other (excess 1).
- Probes: random patches of 15 to 40 knots (about 1,500 facing pairs) and a hill-climb on shapes found excess at most 2; the advisor's
  candidate growing family (a narrow band between two antidiagonals ending in a cap) left the pair unbonded for bands of one to five.

## In standard terms

As in `WEAVE-HEIGHTS-20261118-001`: heights of the triangular antiferromagnet, difference constraints; bonds are minimal non-shattered
sets of the states.

## Prior work in the program

`python3 -B scripts/track.py objects "weave rim excess facing lone pairs bond distance" --until 2026-11-18 --exclude RIM-EXCESS-20261118-001`
`python3 -B scripts/track.py objects "height function weave criterion constrained sets lower bound" --until 2026-11-18 --exclude RIM-EXCESS-20261118-001`

- `WEAVE-HEIGHTS-20261118-001`, `DOUBLE-MEET-20261118-001` — same objects (the criterion and the lower bound; the lone facing pairs).
- `RULER-FLAT-20261111-001`, `KNOTS-ALONE-20261111-001` — relatives: bond distance on closed not-all-equal weaves (steps apart + 1 below a
  cutoff fixed by how the knots meet; faithful readings).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates (`checks.py`): one knot; the two-knot disc; the referee's twelve-knot disc (b = 7 at steps 4 from the search); tight sub-collections over all orders | any fails |
| R1 | Lemma P on every bond of every disc to nine knots: the least cyclic D-sum of each bond is exactly 3(m − 2) | any bond differs |
| R2 | The polygon search equals brute force on every pair of every disc to nine knots (excess at most 6) | any mismatch |
| R3 | (advisor, ~80%) On every disc of eleven and twelve knots, every pair with an excess, and every unbonded pair, is two lone distinctions of opposite classes facing each other | any other pair |
| R4 | (advisor) The largest excess on discs of twelve knots is exactly 2 | larger, or never 2 |
| R5 | Random patches of 20 to 40 knots (polygon search, excess to 6): no facing pair with excess 3 or more | one found |

Recorded without prediction: the excess histogram by size; eight hill-climbs on shape (600 s each).

## Runs and stop rule

`scripts/longrun.py` with `job.py`: 109 cases (7 Lemma-P cases, 30 search-against-brute-force cases, 24 excess shards at eleven and
twelve knots, 40 random cases, 8 climbs); `merge.py` scores. Registered as RIM-EXCESS-B1 (about an hour on 8 workers). One run; no change
after seeing results. Stop at the read-out, the referee hand-off and the report.

Advisor. `claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2) checked Lemma P (with the case m = 3 made explicit), the corollary and Lemma C (sharpened to a split
of the excess between the two arcs), flagged that sub-collections must be tested in every cyclic order (the search does), sketched the
figure-eight structure of bonds through opposite lone pairs, proposed the candidate growing family (unbonded in the exploration), and
gave R3 and R4 with its confidence. It could neither prove a bound nor certify growth.
