# Referee report CLAMP-LEARN-R1 (lean, as asked)

**Verdict: Confirmed, with one wording fix (Not a block).** The restricted blind chances and medians, the tallies and the step
sums all check. The steps currency for runs that are not found never applies: no run reached the 2,000,000-step budget, and every
run not found was stopped by the five-minute cap. That cap reads about 25 to 42 million steps, at similar rates for all three rules.

Referee: the background referee thread, 2026-11-12. `ref_clamp.py` reads the census's records; there was no regeneration, as asked.
The advisor model was not consulted.

## 1. The restricted blind computation

**The consistency rule is as stated.** `check.py`'s `consistent(m, target)` requires each output to equal the target's or be u. A u
in the target needs a u in the map: both outputs must be reachable.

**The restricted chance** is P(the map is the target) / P(the map is consistent). Both are over uniform draws of a law at rest and a
uniform flip of the three inputs and of the output.

| Setting / target | Uniform chance | Restricted chance | Blind medians (uniform, restricted) |
| --- | --- | --- | --- |
| GE / count | 1/32 | 0.03125 / 0.25 = 1/8 | 22, 6 |
| GE / g | 1/64 | 0.015625 / 0.15625 = 1/10 | 45, 7 |
| F / count | 1/8 | 1/2 | 6, 1 |
| F / g | 1/16 | 1 | 11, 1 |

I recomputed the blind medians, the least t with 1 − (1 − p)^t ≥ 1/2, and they match the census's in every case.

**One choice to note.** The draw weights each law at rest and each flip equally. It is not, say, a uniform pick among the 24
consistent laws first.

## 2. The steps currency and the tallies

**The tallies.** Of 600 runs:

| Rule | Count found (of 100) | g found (of 100) |
| --- | --- | --- |
| B | 48 | 73 |
| C | 13 | 36 |
| CA | 12 | 55 |

- **Every run not found was dropped at the 300 s cap,** 363 runs in all. None stopped at the 2,000,000-step budget, so the rule
  "B's steps when not found are set to the budget" never applies.
- **How the summary treats them.** It counts these runs as never finished (infinite steps), so no pass depends on the currency.
- **Bookkeeping checks out.** On every run with a record, "found" equals "the map at the stop is the target", and all steps =
  learning + wrong copy + probe walk.

**What the cap means in steps.** On the runs that were found, the median rate is about 93,000 to 96,000 steps per second for B, 81,000
to 99,000 for C and 136,000 to 142,000 for CA. So 300 s is about 25 to 42 million steps, far past the restricted blind medians in
steps (0.97 million for the count and 1.9 million for g).

The comparison of C and CA with B is not explained by speed: CA is the fastest per step and still finds the count least often. But
the found counts are counts within five minutes of a shared machine, not within the step budget.

## 3. The walk (claim 3)

The shares are as stated, in setting F (1,200 probes each):

| Start | Rests at the count's law | Rests at g's |
| --- | --- | --- |
| fixed | 3.4% | 15.3% |
| random | 4.3% | 13.2% |

Uniform is 12.5% for the count and 6.25% for g. In GE the walk rests at the count's law in 0.17% of probes (uniform 3.1%) and at g's
in 0.3% and 0.5% (uniform 1.6%). These were not part of the claim, but they agree with it.

## Fix (Not a block)

Say that the found counts (13 and 12 against 48) are counts within the frozen five-minute cap. The cap stopped every run not found, at
about 25 to 42 million steps. None reached the 2,000,000-step learning budget, so the stated currency for runs not found is never used.
