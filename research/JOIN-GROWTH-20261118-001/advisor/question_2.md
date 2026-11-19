# Advisor question 2 (JOIN-GROWTH-20261118-001, after the freeze, on two joined rings)

Same growth and words as question 1 (your answer 1 is the background). Analysis please, not encouragement; I will check it.

## What the frozen census has shown so far (single rings)

Your product law held exactly on every scored single-ring start so far (lone adjuncts on rings of 5, 7, 9 with s = 1..4; several
adjuncts at separate knots, positions varied; two lone adjuncts on one knot; the bare hanging pair on rings of 7 and 9; hanging
pairs with surplus; the ring's surplus bit beside a hanging pair, at r and at r + 2). Your renewing-offshoot reading checks: in the
bare pair exactly one junction per round gets a floor bit beyond its demand, and none in pieces with surplus.

Post hoc I found a nested law for chains hanging from r (r, K1, K2, K3, ...). The candidate relation links knots two apart along the
chain, so knots at even removes nest under r and knots at odd removes under K1 (a candidate of r's ring neighbours). Each knot's
series is F = 1 + y (1 + y)^s Π F(candidate children), a floor-only end renewing (1/(1 − y)). It predicted the bare chain of four,
F = (1 + y + y²)/(1 − y), annihilator (x − 1)(x^(n+2) − x^(n+1) − x² − x − 1), on rings of 5 and 7 before those runs finished, and it
holds; the bare chain of three gives the bare pair's (1 + y)/(1 − y) on rings of 5, 7, 9.

Exploratory: a knot sharing two bits with r acts as one surplus bit (x^6 = x + 1), as you guessed. A knot touching ring knots 0 and
3 of a ring of seven gives x^6 = x + 1 too. A knot touching two neighbouring ring knots 0 and 1 (bare sizes 6, 6, 4, 3, 4 and the
knot 4) closes the whole start in five rounds: {0, 1, 3} are pairwise candidates (through the new knot, 2 and 4) with no common
neighbour, a group of three.

## Two rings joined (bare unless said; per-round junction counts from round 0)

| Join | Bare sizes | Counts |
| --- | --- | --- |
| 5–5, one shared bit between knot 0 of each | 7,5,4,4,5 / 7,5,4,4,5 | 10, 14, 24, 42, 78, 154, 310, 638, 1346, 2888, 6278, 13822, 30776, 69168, 156748, 357928 |
| 5–5, shared knot (ring 2 passes through ring 1's knot 0) | 8,6,4,4,6 / 6,4,4,6 | 9, 14, 26, 47, 95, 204, 452, 1037, 2407, 5632, 13366, 32199, 78627, 194214 |
| 5–5, path of one knot | 6,5,4,4,5 / 6,5,4,4,5 / path 6 | 11, 15, 24, 40, 69, 125, 236, 458, 907, 1825, 3716, 7638, 15841, 33156, 70014, 149036 |
| 5–7, shared bit | 7,5,4,4,5 / 7,5,4,4,4,4,5 | 12, 16, 26, 44, 76, 138, 261, 502, 975, 1925, 3861, 7829, 16014, 33042, 68750, 144076 |
| 5–9, shared bit | 7,5,4,4,5 / 7,5,4,4,4,4,4,4,5 | 14, 18, 28, 46, 78, 136, 245, 454, 850, 1601, 3044, 5850, 11349, 22182, 43637, 86392, 172097 |

Fits of log c = a + t log λ + α log t on rounds 8 on: 5–5 bit λ 2.49 α −1.30; shared knot 2.77, −1.46; path 2.30, −1.15; 5–7 2.27,
−1.19; 5–9 2.13, −1.08 (residuals ≤ 0.002). No recurrence of order ≤ 7. (7–7 and a 5–5 with a surplus bit elsewhere are rerunning.)

## Questions

1. A model for two rings joined by one shared bit that reproduces these counts (or at least λ), built from the (v, S) model and
   the menus: what is ring 2's menu at ring 1's joint knot, given that the joint knot's own ring-2 laps carry ring 1 again? Your
   refuted attempt gave 1.81; the counts double from round 1, so something branches at the joint every round. Is the join's cross
   region a product of the two rings' positions with lifts from both (each junction near the joint lying over a position in each
   ring)? Please give a system we can iterate to many rounds and compare with the counts above exactly.
2. If no exact model: a sharp, falsifiable prediction for the next study (a rate, an exponent, an ordering, or the first rounds'
   counts of an unseen join, such as 7–7 or 5–5 through a path of two knots).
3. Does the nested law above look right to you as the general law for trees of knots hanging from a ring (siblings multiply,
   candidate children nest)? What tree would most likely break it?
