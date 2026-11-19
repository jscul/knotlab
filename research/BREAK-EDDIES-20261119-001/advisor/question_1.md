# Advisor question 1 (BREAK-EDDIES-20261119-001, pilot stage, before any design is frozen)

Analysis please; I will check it.

**Setting.** The cheapest parity growth (FRESH-COUNT's complete-round policy, fewest counts max(d, 3 − p, 1), A104). Inside the
cluster rule's scope, a one-loop piece of the block graph grows with rate 1/y*, where W(y*) = 1 and W is the loop's
round-weight: y per loop knot, a transit per block, (1 + U) per side entry (your earlier answer, confirmed in
LOOP-CATALOGUE-20261119-001). The rule fails in two shapes:
- **(a)** a merged block with a missing pair (the overlapping sunflowers);
- **(b)** first-round groups of three (hyperedges) that overlap another block in two knots, or meet each other at a knot.

Growth finds self-feeding starts there that the rule cannot read. LOOP-CATALOGUE's search to eight knots marked 30 of them
provisionally minimal.

**Pilot (disclosed).** I grew the 30 to 40 rounds or 300,000 junctions, each in its own process with a 6 GB address-space limit
and 900 s. Then I ran Berlekamp–Massey on the counts.
- **Rational, with W read off the recurrence.** I write the annihilator x^d − Σ a_k x^(d−k) as W = Σ a_k y^k.
  - #1–3 (7 knots), #22: x^6 − x − 1, so W = y^5 (1 + y).
  - #17–19: x^5 − x − 1, so W = y^4 (1 + y).
  - #23–28: x^4 − x − 1, so W = y^3 (1 + y) (three of them show (x^4 − x − 1)(x^4 + x + 1)).
  - #20, 21, 29: x^3 − x − 1, so W = y^2 (1 + y), the plastic number 1.3247.
  - #7–15: x^8 − x^3 − 3x^2 − 3x − 1, so W = y^5 (1 + y)^3.
  - #16: x^8 − x^3 − x^2 − 2x − 1, so W = y^5 + y^6 + 2y^7 + y^8.
- **Not settled.**
  - #0, the six-knot theta (the ring 0-1-2-3-4, plus 5 touching 0 and 3), holds break (a). Its ratio rises 1.43, 1.43, 1.47,
    1.67, and it hit the memory limit at round 18.
  - #4, #5 and #6 grow explosively (#6: 26, 34, 49, 94, 489, 2,359) and hit time or memory limits.

So loops of length 2 and 3, which no ring of knots makes, appear through the break shapes. A ring of three is one hyperedge, a ring
of four is a pair with two common neighbours, and a ring of six is two hyperedges.

**Data** (sizes; touches; open places; round-1 groups; first counts):
#1: sizes [5, 4, 4, 5, 5, 4, 6]; touches [(0, 1), (0, 4), (1, 4), (2, 3), (2, 5), (3, 5), (3, 6), (4, 6)]; open [3, 2, 2, 2, 2, 2, 4]; round-1 groups [[0, 1, 4], [0, 6], [1, 6], [2, 3, 5], [2, 6], [3, 4], [5, 6]]; counts [7, 8, 10, 11, 12, 13, 15, 18, 21, 23, 25, 28, 33, 39, 44, 48, 53, 61, 72, 83, 92, 101]
#7: sizes [6, 6, 7, 5, 5, 3, 4, 4]; touches [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 6), (3, 7), (4, 5), (6, 7)]; open [4, 3, 5, 2, 2, 2, 2, 2]; round-1 groups [[0, 1, 4], [0, 2], [0, 5], [1, 3], [1, 5], [2, 4], [2, 6], [2, 7], [3, 6, 7]]; counts [8, 11, 18, 26, 35, 45, 58, 81, 121, 178, 246, 324, 425, 583, 842, 1224, 1717, 2313, 3076, 4190, 5924, 8498]
#17: sizes [5, 7, 6, 5, 5, 4, 4, 5]; touches [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (2, 7), (3, 7), (4, 5), (5, 6), (6, 7)]; open [3, 4, 3, 3, 2, 2, 2, 2]; round-1 groups [[0, 1, 4], [0, 2], [0, 5], [1, 3], [1, 5, 7], [2, 3, 7], [2, 4, 6], [3, 6]]; counts [8, 9, 11, 13, 15, 17, 20, 24, 28, 32, 37, 44, 52, 60, 69, 81, 96, 112, 129, 150, 177, 208]
#20: sizes [7, 6, 6, 5, 5, 4, 4, 5]; touches [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (2, 7), (3, 7), (4, 5), (5, 6), (6, 7)]; open [5, 3, 3, 3, 2, 2, 2, 2]; round-1 groups [[0, 1, 4], [0, 2], [0, 5], [1, 3], [1, 5, 7], [2, 3, 7], [2, 4, 6], [3, 6]]; counts [8, 10, 15, 21, 27, 33, 43, 61, 84, 108, 136, 180, 249, 337, 436, 560, 745, 1015, 1359, 1769, 2301, 3065]
#23: sizes [4, 7, 5, 5, 5, 4, 4, 4]; touches [(0, 4), (0, 7), (1, 2), (1, 3), (2, 5), (2, 6), (3, 4), (4, 7), (5, 6)]; open [2, 5, 2, 3, 2, 2, 2, 2]; round-1 groups [[0, 3], [0, 4, 7], [1, 4], [1, 5], [1, 6], [2, 3], [2, 5, 6], [3, 7]]; counts [8, 10, 15, 19, 22, 27, 31, 34, 43, 59, 75, 90, 107, 123, 142, 179, 236, 299, 362, 427, 495, 586]
#25: sizes [4, 6, 5, 6, 5, 4, 4, 4]; touches [(0, 4), (0, 7), (1, 2), (1, 3), (2, 5), (2, 6), (3, 4), (4, 7), (5, 6)]; open [2, 4, 2, 4, 2, 2, 2, 2]; round-1 groups [[0, 3], [0, 4, 7], [1, 4], [1, 5], [1, 6], [2, 3], [2, 5, 6], [3, 7]]; counts [8, 10, 14, 16, 18, 24, 30, 34, 42, 54, 64, 76, 96, 118, 140, 172, 214, 258, 312, 386, 472, 570]
#0: sizes [5, 5, 5, 5, 5, 5]; touches [(0, 1), (0, 4), (0, 5), (1, 2), (2, 3), (3, 4), (3, 5)]; open [2, 3, 3, 2, 3, 3]; round-1 groups [[0, 2], [0, 3], [1, 3], [1, 4], [1, 5], [2, 4], [2, 5], [4, 5]]; counts [6, 8, 10, 13, 17, 22, 30, 42, 58, 80, 111, 155, 220, 315, 450, 643, 920, 1352, 2258]
#6: sizes [4, 8, 7, 4, 3, 4, 3, 7]; touches [(0, 1), (0, 6), (1, 2), (1, 7), (2, 3), (2, 7), (3, 4), (4, 5), (5, 7)]; open [2, 5, 4, 2, 1, 2, 2, 4]; round-1 groups [[0, 2], [0, 7], [1, 2, 7], [1, 3, 5], [1, 6], [2, 4, 7], [2, 5], [3, 7]]; counts [8, 11, 18, 22, 26, 34, 49, 94, 489]

**What I tried.** "Merge two simplices only when the merged block is complete, else keep them as two blocks (a loop of length two)",
run through the rule's machinery. It is worse: the theta now differs from the growth at round 1 instead of round 3. Most of the 30
are outside the rule's scope (hyperedges overlapping another block in two knots), so the rule gives no series for them.

## Questions

1. For a hyperedge-bearing start such as #23 or #25 (W = y^3 (1 + y)), or #20 (W = y^2 (1 + y)), which loop in the candidate
   structure gives these lengths? State it in terms of the round-1 groups (as nodes?) and the knots. Is there a natural object,
   for instance a graph on the round-1 groups (junctions), or "junctions as valid sets", whose unrolled cover gives exactly these
   round-weights?
2. Propose an extended rule that reduces to the cluster rule inside its scope and covers shapes (a) and (b). Give its predicted
   counts or W for #1, #17, #20, #23 and the theta, so that I can check it against the growth. Be concrete about the first two or
   three rounds.
3. The theta: is it algebraic (two loops), and with what system or rate? Its knot graph has a 5-cycle and a 4-cycle 0-4-3-5-0
   sharing the path 0-4-3. Your earlier cover-model weight was y^5 (2 + y) at rate 1.2298, but the growth is faster.
4. The explosive ones (#6, with 489 junctions at round 8): what mechanism makes one round jump fivefold? Is the count still
   exponential with a fixed rate, or faster? How would you test this within memory?
5. Which frozen predictions would discriminate your rule? I want five to eight, at least two risky.
