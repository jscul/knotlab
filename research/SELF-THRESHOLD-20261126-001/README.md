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
  more are where it differs).
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
