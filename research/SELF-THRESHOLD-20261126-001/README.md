# Laws whose threshold a new knot reads from itself

Epic `SELF-THRESHOLD-20261126-001`, the last round of the line at the coordinator's go-ahead, after
[`HOLD-BACK-20261126-001`](../HOLD-BACK-20261126-001/decision.md). A check by the thread, not a registered study;
computed; referee pending. Program: [`thr.py`](thr.py), on that study's readings.

## Why

Two laws that hold back at nearly every join part the patterns at once and nothing is heard; the cap of three, which
binds only where a knot is owed more than three, lets far changes be heard late. Is it where the threshold binds, or
the number three, supplied by hand?

## The laws (frozen with the advisor: [question](advisor_question.md), [answer](advisor_answer.md))

Each is min(the ordinary count, a threshold), kept above the ordinary count's own floor max(3 − p, 1):

- **PLACES**: threshold p + 1, no more fresh distinctions than one more than the knot was given. On these starts it is
  the cap of three on joins and a cap of two on offshoots (the advisor: a cap in disguise; the offshoots owed three or
  more are where it differs). *Corrected after the run:* a join given three distinctions gets p + 1 = 4, so PLACES
  differs from the cap at joins given three and owed four; that is where it differs on the histories read ("What was
  found").
- **HALF**: threshold ⌈D/2⌉ + 1, a little over half of what the knot is owed. It binds exactly where the cap of three
  does (D ≥ 4) but has no fixed number: its shortfall grows with what is owed. The advisor's informative test.
- **Controls:** the cap of three on joins only, offshoots ordinary (CAP3-JOINS, to isolate PLACES's offshoot cap); the
  cap of three (positive); the ordinary count (negative).

Read, as in the hold-back study: B1, the census (101 receivers, five senders, changes after rounds 1, 2, 3); B2, the 28
far ends that stay linked to the cap's switch kind (changes after rounds 3, 5, 8, 24 rounds); and, on the growth with no
change, how many births each law gives less than the ordinary count, by kind. Both laws are registered as a scaffold
(A285).

**Stop rule (the coordinator's):** if late hearing from afar appears under one self-read threshold, say whether it
survives the second; if under neither, the line closes as an obstruction learned.

## Expected (written before the full run, after one linked pair)

Trial (the first of the 28): every law keeps the pair linked through round 24, and none gives any birth less than the
ordinary count in the growth with no change (so there the cap of three is the ordinary count); with a far change after
round 3, 5 or 8, the cap of three, CAP3-JOINS and HALF hear it at rounds 13, 17 and 23; PLACES and the ordinary count
do not. So the hearing comes from the threshold biting in the changed growth.

1. **HALF hears late in all 28 linked pairs, at the cap's rounds.** Late hearing survives the change from the number
   three to a threshold read from what the knot is owed.
2. **PLACES hears in none of the 28,** because its cap of two on offshoots binds in the changed growth; CAP3-JOINS hears
   in all 28, so the difference is the offshoot cap.
3. **In the census,** HALF hears late where the cap of three does (the switch kind and its twin) and PLACES not.

## What was found

[`tally.py`](tally.py) on the census (`census_runs.jsonl.gz`, 101 receivers against five senders, 505 pairs per law,
all read; [table](census_table.md)) and on the 28 linked pairs (`linked_runs.jsonl.gz`, with `places_runs.jsonl.gz`
for the two controls added after the hold-back referee; [table](linked_table.md)).

| law | census: short knot made after the start | census: linked after round 3 | census: far changes heard (of 3,088 to 3,437) | census: late | 28 linked pairs: heard (of 249 to 252), all late |
|---|---|---|---|---|---|
| PLACES (p + 1) | 427 | 62 | 0 | 0 | 0 |
| HALF (⌈D/2⌉ + 1) | 399 | 62 | 6 | 6 (rounds 9, 11) | 124 (rounds 13 to 23) |
| CAP3-JOINS | 399 | 62 | 6 | 6 | 124 |
| the cap of three | 399 | 62 | 6 | 6 | 124 |
| the ordinary count | 0 | 231 | 0 | 0 | 0 |
| PLACES-JOINS (p + 1 at joins only) | — | — | — | — | 0 |
| PLACES-OFFSHOOTS (p + 1 at offshoots only) | — | — | — | — | 0 |

- **HALF hears late, and wherever it hears it is the cap of three, birth for birth.** In the census it hears the same
  six far changes as the cap (the switch kind `n3:g7:122@0` and its four-knot twin `n4:g17:1212@0`, against the senders
  `g6:122@0` and `g7:122@0`), and on those four pairs its whole record equals the cap's. In the 28 linked pairs its
  whole record, changed growths included, equals the cap's in all 28: every birth there at which HALF gives less than
  the ordinary count is owed exactly four, where ⌈4/2⌉ + 1 = 3. HALF departs from the cap in 145 census pairs (births
  owed five or more, where it gives four and the cap three), and in those pairs neither law hears anything. So these
  starts cannot tell HALF from the cap; the late hearing is the cap's, read again.
- **PLACES hears nothing,** in the census or in the 28 linked pairs, although on 25 of the 28 its growth with no change
  is the cap's and the pairs stay linked. A far change under PLACES does change the far pattern's births (from round 4
  in the first linked pair) but never the receiver's; under the cap the same change sets off a burst (311 births in
  round 14 against 127) and is heard at round 13.
- **Where PLACES differs from the cap: at a join, not at an offshoot.** PLACES-JOINS (p + 1 at joins, the ordinary
  count at offshoots) gives PLACES's whole record in all 28 linked pairs, and PLACES-OFFSHOOTS gives the ordinary
  count's. The birth that decides is the one the hold-back referee found: a join given three distinctions and owed four
  gets four under p + 1 and three under the cap. So the advisor's description of PLACES as "a cap of two on offshoots"
  missed the joins given three, and expectation 2's reason was wrong (corrected: `docs/CORRECTIONS.md`).

## Expectations, and how they fared

1. *HALF hears late in all 28 linked pairs, at the cap's rounds.* Holds, but not as a survival: on these pairs HALF
   gives exactly the cap's births. Late hearing has not been separated from the number three.
2. *PLACES hears in none of the 28; CAP3-JOINS in all 28; the difference is the offshoot cap.* The first two hold; the
   third fails: the difference is at joins given three and owed four.
3. *In the census, HALF hears late where the cap does, PLACES not.* Holds.

**The stop rule.** Late hearing appears under one self-read threshold (HALF) and does not survive the second (PLACES).
Where it appears, HALF's births are the cap's. What carries a far change late, on every history read in this line, is
one allocation: a join owed four given three. The ordinary count never gives it (the funding argument of the
two-receptions study); a rule that does is a rule added, whether its number is fixed (the cap) or read from the demand
(HALF here, the referee's binary-count ceiling). The line closes as an obstruction learned.

## What this does not say

- That a self-read threshold cannot carry a change late by its own allocations: no history was found where HALF (or the
  referee's binary-count ceiling) gives less than the cap and a far change is still heard. The referee's next direction
  (find a birth owed five or more before a hearing, change its allocation, compare) was not run.
- Not-all-equal only; one join (a meeting through two link knots), d = 3; the census's 101 receivers and five senders;
  12 rounds (24 for the linked pairs); changes at no more than five linked and two unlinked far members.
