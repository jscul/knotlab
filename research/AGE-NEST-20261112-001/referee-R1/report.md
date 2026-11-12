# Referee report AGE-NEST-R1: what the expanding growth's degrees do not carry

**Verdict: Confirmed with fixes.**
- **The data reproduce.** The fairness check reproduces exactly with my own enumeration. The resampling ladder reproduces within its
  sampling noise on all 183 cores, so N1 and N2 hold.
- **The chains mix on the cores tested.** Longer chains and a long chain after a burn-in do not move the shares.
- **R2 and FULL do what they say.**
- **The fix is about reading.** What carries the end is the age profile, how many knots have their youngest member at each age.
  Keeping only each knot's youngest member (R2p) ends as often as keeping the degrees too (R2). R2p is the growth's own law given that
  profile, and no early part of the core is dense enough to pass the uniform end. So the result is real, but its mechanism is
  known in kind: age-inhomogeneous random patterns, as with grown networks against degree-matched ones.

Referee: the background referee thread, 2026-11-12.
- **Code.** `ref_agenest.py` holds my own chains, R2p, FULL, the exact enumeration and transition matrices, the ladder and the mixing
  test. It builds on OLD-CORE-R1's `ref_oldcore.py` (regenerated growths, satisfiability) and imports neither census.
- **Validation.** V2. The advisor model was not consulted for this job.

## 1. Fairness, recomputed exactly

For the five degree sequences of the census, I enumerated every simple pattern with my own code: 330, 27, 65, 17 and 16,534 patterns,
as in the census. I then rebuilt both transition matrices.

| Check | SW | R2 |
| --- | --- | --- |
| Symmetric | yes, on all five | yes, on all five |
| Rows summing to 1 | yes | yes |
| Components | one | one per assignment of youngest members: 7, 3, 4, 4 and 30 |

So each chain is uniform on exactly the class it must preserve.

## 2. The ladder, recomputed

I regenerated the 183 non-pilot cores and confirmed each is without a state. I then resampled each rung 20 times with my own code,
using the census's scheme: 20 independent chains of 20 m steps from the core for SW and R2.

| Process | SW (mine; census) | R2 | R2p | FULL |
| --- | --- | --- | --- | --- |
| X(0.3), 81 cores | 0; 0 | 0.45; 0.40 | 0.40; 0.40 | 0.35; 0.35 |
| X(0.35), 94 cores | 0; 0 | 0.47; 0.50 | 0.53; 0.55 | 0.55; 0.575 |
| X(0.25), 8 cores | 0; 0 | 0.10; 0.15 | 0.15; 0.125 | 0.10; 0.075 |

The values are medians.
- **The differences are noise.** Per-core mean differences are 0.01 to 0.11, as expected from 20 resamples per rung, whose standard
  deviation is up to about 0.11.
- **N1 holds:** the median SW share is 0.
- **N2 holds:** among cores where R2 and SW differ, R2's share exceeds SW's in 78 of 80 at X(0.3) and 84 of 86 at X(0.35), on my
  resamples.

## 3. (Check 1) Mixing

**The test.** For 40 cores, the smallest 20 with m ≥ 150 at X(0.3) and at X(0.35) (m from 155 to 616), I ran SW and R2 three ways:
- the census's scheme, 20 chains of 20 m steps;
- 20 chains of 100 m;
- one chain with a burn-in of 200 m, then 20 samples 20 m apart.

| Process, chain | 20 m | 100 m | long chain |
| --- | --- | --- | --- |
| X(0.3), SW | 0.00 | 0.00 | 0.00 |
| X(0.3), R2 | 0.25 | 0.23 | 0.25 |
| X(0.35), SW | 0.08 | 0.08 | 0.05 |
| X(0.35), R2 | 0.40 | 0.47 | 0.43 |

The values are medians.
- **The shares do not move.** Per-core differences are 0.01 to 0.15, which is sampling noise.
- **No sign of inflation.** If anything, R2 rises slightly with longer chains at X(0.35) (mean 0.41 to 0.47). The 20 m chains do not
  inflate the shares by staying near the dead core.
- **Not tested.** The largest cores, up to about 5,000 knots, were not tested for mixing.

## 4. (Checks 2 and 3) R2 and FULL

**R2 keeps what it says.**
- **The rule.** It takes u among the two older members of one knot and v among the two older of the other, and requires v older than
  the first knot's youngest and u older than the second's.
- **Each knot keeps its youngest member,** so every count of knots among the oldest j distinctions is kept, and the degrees are kept
  too.
- **Checked on every core:** a resample has the same multiset of youngest members and the same degrees.
- **The proposal is symmetric.** The reverse move picks the same pair with the same probability. The exact check in section 1
  confirms it.

**FULL reads the schedule correctly.**
- **What counts as a birth.** Walking the growth in order, a knot with a new member is a birth, whose youngest member is the new
  distinction, and a knot with none is a closing, timed by the number of distinctions then present.
- **Redraws.** A birth redraws its pair among older distinctions. A closing redraws three among the core's distinctions present at
  its time.
- **What this conditions on.** The growth's own closing draws among all distinctions present. So FULL is the growth's rule
  conditioned on the core's schedule, which is the advisor's reading in the pre-registration.

**Q0 is settled by the pair-count lemma, which holds.** For three bits, the number of equal pairs is 3 when all are equal and 1
otherwise. So the number of knots a state violates is (Σ over pairs of c_pair · [equal] − m)/2, which depends only on the pair counts.
- **Consequence.** A Pasch trade keeps the pair counts, so it keeps the states, and all 104 trades stay without a state.
- **No rung reproduces the core's pair counts:** the share is 0 on every rung.

## 5. (Check 4) Does "the nesting by age carries the end" hold, and is it known?

**What the rungs show.**
- **Degrees add nothing beyond the age profile.** R2p, which keeps each knot's youngest member and lets degrees go, ends as often as
  R2. On my resamples, R2p beats R2 in 38 cores and loses in 35 at X(0.3), and 37 against 42 at X(0.35); the rest tie.
- **The detailed schedule adds nothing either.** FULL is about the same.
- **Degrees alone carry none of it.** SW ends in a median of 0.

So the carrier is the age profile: how many knots have their youngest member at each age, which is every prefix count. "The nesting
by age" is a fair name for that, provided it is read as "the prefix counts, with or without the degrees".

**Not settled by definition, but close to the growth's own law.**
- **R2p is the growth's conditional law.** For a closing, a uniform triple conditioned on its youngest member is two uniform older
  members, which is exactly R2p's redraw. So R2p resamples the growth's own law given the age profile.
- **Why about half.** The core is the first dead prefix, selected at its own crossing, so resamples from the same law with the same
  profile ending about half the time is what a near-critical selection gives.
- **What the result does show.** The age profile alone carries the end, and degrees do not.

**No early dense part.** Over the oldest j distinctions, j ≥ 20, the largest density of knots has these values:

| Process | Median | Maximum | Cores at or above 2.1 |
| --- | --- | --- | --- |
| X(0.3) | 1.68 | 1.96 | none |
| X(0.35) | 1.79 | 2.4 | 3% |
| X(0.25) | 1.69 | 1.90 | none |

So the end is not a crossing of the uniform end by an early part. It comes from the inhomogeneity by age: older distinctions are
knotted among themselves more than a uniform or degree-matched pattern would make them.

**Known in kind.** Random patterns whose knots depend on the members' ages are inhomogeneous random hypergraphs, whose thresholds are
set by the age kernel rather than by degrees (Bollobás, Janson and Riordan 2007). Grown networks differ from degree-matched static ones
for the same reason (Callaway, Hopcroft, Kleinberg, Newman and Strogatz 2001). The rungs, the shares and the null result for degrees
are new data; the mechanism is known in kind.

## 6. (Check 5) The pilot, and tied cores

**The pilot.** The census holds out exactly the 12 frozen pilot endings: X(0.3) runs 0, 1, 4, 10, 11, 12 and X(0.35) runs 0 to 5, all
endings in OLD-CORE. 195 − 12 = 183 cores. These are the first runs, not chosen by outcome.

**Tied cores.** Leaving them out of the comparison of R2 with SW is as frozen. The ties number 5 at X(0.3) and 10 at X(0.35), and 8
of the 15 tie at 0 and 0. Counting ties as losses gives 72 of 81 (89%) and 77 of 94 (82%), still above the frozen 70%. So N2 does not
depend on how ties are handled.

## 7. Fixes for the thread

1. **"The nesting by age carries the end".** Say it as "the age profile (every prefix count) carries the end; degrees neither add to
   it nor carry it". R2p, which keeps only each knot's youngest member, ends as often as R2. Say that R2p is the growth's own law given
   that profile. Say that no early part of the core passes the uniform end (largest prefix density 1.68 and 1.79, median). Classify the
   mechanism as known in kind: age-inhomogeneous random patterns (Bollobás, Janson and Riordan) and grown against degree-matched
   networks. **Narrowing** (Overreading: a rung's name read as a mechanism the other rungs show is not needed).
2. **Mixing.** Add that on 40 cores (m 155 to 616) the shares do not move with 100 m chains or with a long chain after a 200 m burn-in,
   and that the largest cores were not tested. **Not a block.**
3. **N2's ties.** With ties counted as losses, 89% and 82%. Say so. **Not a block.**

## Files

`brief.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_agenest.py fairness` | `result_fairness.json` | the exact enumeration and transition matrices |
| `ref_agenest.py ladder` | `result_ladder.jsonl` | all 183 cores, the four rungs and the largest prefix density |
| `ref_agenest.py mixing` | `result_mixing.json` | the 40 cores, three chain schemes |
