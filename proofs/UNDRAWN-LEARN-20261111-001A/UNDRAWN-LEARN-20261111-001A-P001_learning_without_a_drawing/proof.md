# Learning counts with dissonance at knots alone

Status: Proved (V and R exact; learning computed, frozen). `check.py`, ticket A of
`research/UNDRAWN-LEARN-20261111-001/preregistration.md`, frozen with the code in commit `6be010d59` before any learning run. The harness
and summary parts reproduce; the learning parts were run once (30 minutes per run on J1 and U, 120 on J2, ten processes) and are recorded
run by run in `runs_learn1.jsonl`, `runs_learn2.jsonl` and `runs_learn3.jsonl`.

## The test

The credit learner with the sturdier probe, run on an engine whose dissonance is 2 × (violated knots), floor 0, with sign changes only at
violated knots and the credit rule reading distinctions where it read the drawing's faces. Three bases: J1, one copy of the drawn knot
pattern (2, 0, 4); J2, two copies sharing a distinction; U, a pattern of 6 distinctions and 8 knots, with 2 to 6 knots at a distinction,
which no drawing as a drawn knot pattern fits, chosen by a frozen rule. Ten runs per base; targets the count of the held inputs, its
negation, the count again; budget 8,000,000 steps per target.

## Results

| Check | Result | Evidence class |
| --- | --- | --- |
| V: the engine's running dissonance equals a fresh count after 20,000 random moves (J1, J2) | yes | computed, exact |
| R: laws counting three at J1's interface | 4 of 512 (with faces the learner rests among 4 law classes, 1 counting) | exhaustive |
| R: laws counting three at U's interface | 1 of 2,048; no other counting set in any law | exhaustive |
| L1: J1, learned and held in at least 8 of 10 | **0 of 10**: one run stopped at the count for all three targets but held none of them; nine reached the 30-minute cap | computed, frozen |
| L2: J2, learned and held in at least 8 of 10 | **0 of 10**: all ten reached the 120-minute cap | computed, frozen |
| L3: U, learned and held in at least 8 of 10 | **0 of 10**: two runs stopped at the count (one held the negation once, 1 of 6 writes); eight reached the cap | computed, frozen |

With faces, the same learner learned and held J1's count in 10 of 10 runs at a median of 13,400 steps, and J2's in 10 of 10.

## What the failures show

- **Not held.** Every stop at the right count but one was lost after the disturbance: after one distinction is flipped, the repair (M1)
  re-signs knots as freely as it flips distinctions, so the law drifts, and the map read afterwards is another one (J1, seed 9405:
  `01101001` became `0x1uu0x1`). With faces a sign change costs dissonance at the faces beside it, so the repair flips distinctions and
  the law stays (a reading of the mechanism; the two jobs were not tested apart, B158).
- **Not found in time.** Nine of ten J1 runs did not stop within 30 minutes, where with faces the median took 13,400 steps: the learner
  may now rest at any of 512 laws, 4 of which count, instead of 4 law classes, 1 of which counts.

## Against the pre-registration

V and R as computed. I predicted L1 would pass, slower; it failed. L2 and L3 failed. By the frozen criterion the faces did real work for
these counts, so A66 is Confirmed: the learner's success on J1 and J2 rested on reading each copy's drawn faces.

## What it says

The faces did two jobs for the learner: they narrowed the laws it can rest at (here 128-fold) and they made a learned law cost something
to change, so repairs flip distinctions instead. A learner on a base with no drawing has neither, and without them it neither finds nor
keeps the count on one copy.
