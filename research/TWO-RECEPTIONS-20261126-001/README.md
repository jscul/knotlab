# Two receptions from a far pattern, and whether the model makes the shortage itself

Epic `TWO-RECEPTIONS-20261126-001`, at the coordinator's go-ahead under the owner's standing rule, after the referee of
[`LINKED-UNDER-CAP-20261126-001`](../LINKED-UNDER-CAP-20261126-001/decision.md) found that a second far change can
cancel the first. A check by the thread, not a registered study; computed; referee pending.

## A. Two receptions ([`two.py`](two.py))

In the 28 far ends that stay linked to the switch kind through round 16 (caps of three and four), a first change at
the nearest or second-nearest linked far member after round 3 (heard at round r₁), then, in the once-changed growth,
a second change at each of the eight nearest linked far members after each round t = 4 to r₁ − 1. Each is sorted as
*cancels* (the receiver's own births return to the unchanged growth's), *merges* (the first response itself changes,
at r₁ or before), *two* (the first response is kept and a later, lasting difference from both growths follows),
*second, not kept* (a later difference that does not last) or *unheard*. 32 rounds or 10,000 knots.

Seen before the full run (one pair, the cap of three): the once-changed growth has linked far members only after
rounds 4 and 5 (the link ends by round 6), so three second changes; none heard.

**Expected:** no *two* in any pair: second changes are unheard, cancel or merge, because the link they would travel
ends within three rounds of the first change. (The advisor thinks this at real risk: a second change at a farther
member should arrive later and need not cancel.)

## B. Does the model make the shortage itself?

**The argument.** Under any ration that gives a new knot at least its demand (f ≥ D: the ordinary count, with or
without the record's takes), no knot made after the start is ever short in the unchanged growth. D is read once,
after every birth and every take, on the members that will be there next round (the waiting ones included); a take
takes only a distinction already held by two knots, never a newborn's fresh one; fresh distinctions are held by their
knot alone, so they make no sharing; so next round's groups are the demand roster's, and a new knot owes D and holds
f ≥ D. An added loose distinction raises what a knot holds and makes no sharing, so it makes no knot short either;
a barred one can. (Parity's implied births receive nothing and hold no usable distinction, so they are never members:
outside the argument and harmless.) So under the ordinary count a pattern's own knots can be reached after the start
only through shortages made by the start itself, or by a distinction removed.

**The check.** On the census of receivers against the five senders (three steps by a meeting), under the ordinary
count with no take and with each recorded take, and under the rations that can give less than the demand without a
number set by hand: FLOOR1 ("just enough for three places", which uses only the ordinary count's own numbers but drops
the demand: a choice, a scaffold) and the parent-owing rations (an offshoot receives what its parent was owed: every
number read from the record, the advisor's fairest). Read: knots made after round 1 that are short, linked pairs, and
far changes after round 3 heard.

**Expected:** no short knot made after round 1 under the ordinary count with any take; under FLOOR1 and the
parent-owing rations, short knots, and (held weakly; the advisor would not bet on it) no linked pair that hears a
later far change. The cap of three is, by the same standard as FLOOR1, the ordinary count's own number of places with
the demand dropped: if FLOOR1 is admitted as the model's, so is the cap of three, and the line's results under it.

## What was found: A

All 56 pairs were read (the 28 far ends under the caps of three and four; 19 to 32 rounds); 808 second changes
([`two_runs.jsonl.gz`](two_runs.jsonl.gz)).

| first change at | heard at | second changes | unheard | cancel | merge | two | second, not kept |
|---|---|---|---|---|---|---|---|
| the nearest linked far member (56 pairs) | round 13 | 528 | 528 | 0 | 0 | 0 | 0 |
| the second nearest (40 pairs) | round 15 | 280 | 240 | 40 | 0 | 0 | 0 |

- **No pair receives two distinct changes.** Every second change made before the first was heard, at every linked
  far member among the eight nearest, is either unheard (768) or cancels the first (40). None keeps the first response
  and adds another.
- **The cancelling ones arrive with the first.** All 40 are set after round 4 at a member ten sharings away and arrive
  in round 15, the round the first (set after round 3, eleven sharings away) arrives; with both, the receiver's own
  births are those of the growth with neither. This is the referee's case, in 20 of the 28 pairs under each cap.
- **There is little room for a second.** In the once-changed growth a far member is still linked to the receiver after
  rounds 4 to 7 (4 to 6 when the first was at the second nearest), and not later, so no second change can be placed
  after round 7.

So the expectation holds: two changes from the far pattern are never both received; two that arrive together cancel.
The advisor's reading fits: the responses combine like a sum of two bits, which comes back to nothing when both
arrive in one round, and nothing arrives later because the link ends.

## What was found: B

The census ([`shortage.py`](shortage.py), [`drive_b.py`](drive_b.py), [`shortage_table.md`](shortage_table.md) by
[`tally_b.py`](tally_b.py) on `shortage_runs.jsonl.gz`): 100 receivers drawn with seed 20261126 from the 646, each
against the five senders, under 16 laws: 7,298 of 8,000 pairs read; 702 not run (eight jobs stopped by their clock or
memory cap, all reading the slow takes first in each receiver's order: not negatives).

| laws | pairs read (each) | pairs with a knot made after the start that is short | far changes after round 3 heard |
|---|---|---|---|
| the ordinary count, with no take or with MET (either choice), MET-SOLE, STEPS1-SOLE, STEPS2-SOLE | 455 to 463 | **0** | 0 of 4,143 |
| the ordinary count with J-EACH-PART | 455 | **0** | 199 of 777 at linked far members, all in rounds 4 and 5, two or three sharings away |
| FLOOR1 and six parent-owing rations (PARENT-OWING, its caps of three and four, OFFSHOOT-TWO, PARENT-OWING-1, PARENT-OWING-PLAIN) | 455 | 455 (every pair) | 2 or 3 per law at linked far members, all by one receiver, in round 9, seven sharings away; 0 at members not linked |
| OFFSHOOT-THREE, MOD2 | 455 | 455 | 0 (no pair linked after round 3) |

- **The argument holds in every pair read.** Under the ordinary count, with any recorded take, no knot made after the
  start is short (0 of 3,203 pairs). So the model's own count makes no shortage like the cap's.
- **The one take that reaches across parts carries changes without any shortage**: under J-EACH-PART a birth takes
  distinctions held in every other part, so a change there is taken over directly. It is heard early (rounds 4 and 5,
  within 2d) and from two or three sharings: a take written by hand that joins parts, not a shortage.
- **Rations that give less than the demand make the shortage, and once a late hearing.** Under FLOOR1 and the
  parent-owing rations every pair has short knots made after the start, and one receiver of the 100 (four knots: one
  sharing with each of the other three, a triangle among those three, sited at the pendant knot holding two loose
  distinctions) hears a change made after round 3 at round 9, seven sharings away, with the one-knot sender (and under
  PARENT-OWING-1 with the two-knot sender). These rations set no new number (FLOOR1 uses the ordinary count's 3 and 1;
  the parent-owing rations read the parent's owing), but each drops the demand, which is a choice by hand; the cap of
  three is the same kind of choice.

**So the answer to the line's question is no.** Nothing the model's own count makes produces a shortage after the
start: proved for every law that gives a new knot its demand, and seen in every pair read. What makes the shortage
that lets a pattern's own knots hear from afar is a ration that gives less than the demand: a cap, "just enough for
three places", or an offshoot given what its parent was owed. Each is a choice made by hand, even where it adds no new
number. Every hearing from afar found on this line rests on such a choice, and the line stops here.

## Expectations, and how they fared

- *A: no two receptions.* Holds: 0 of 808 (768 unheard, 40 cancel).
- *B: no short knot made after the start under the ordinary count with any take.* Holds (0 in every pair read).
- *B: under FLOOR1 and the parent-owing rations shortages but no linked pair hearing a later far change* (held
  weakly). Fails narrowly: one receiver of 100 hears, at round 9, under FLOOR1 and six owing rations.

## What this does not say

- 100 sampled receivers, five senders, one join, 12 rounds or 1,500 knots or the guard; the takes MET and J-EACH-PART
  mostly end at the guard (their rosters explode), so they are read for few rounds.
- The argument covers growth with no change made in it; an added loose distinction makes no knot short, a barred one
  can (as the second-switch referee found under the ordinary count).
- Whether dropping the demand can be had from something the model makes (a rule the knots themselves follow) is not
  asked here; it would be a new law.
