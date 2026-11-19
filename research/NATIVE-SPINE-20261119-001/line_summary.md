# The break-shape eddies and the states-only growth: line summary

19 November 2026, by Claude, at the coordinator's request, closing the search for a finite object behind the break-shape eddies.
One page for the owner. It covers two lines of seven studies, each with its referee's corrections folded in, and adds no evidence:
every figure comes from the linked decision notes.

## Line 1: what produces the eddies where the cluster rule breaks?

The cluster rule reads a start's growth from its candidate map. It is exact in its scope and breaks where groups of three knots
meet or overlap (`LOOP-CATALOGUE-20261119-001`). Four finite objects were tried for the self-feeding starts in those break shapes.
None carries their count.

| Study | What it found | Referee (folded) |
| --- | --- | --- |
| [BREAK-EDDIES](../BREAK-EDDIES-20261119-001/break_eddies.md) | The 122 break-shape eddies that fitted in memory grow at rates of the catalogue's family (118 rational). Their round-weights, read from every factor of the counts' recurrence, are members built from the catalogue's pieces. An explosive kind exists whose counts leap in its last rounds. | **Block** on "short loops through groups of three": W had been read from the rate alone; such loops are consistent with 12 starts and shown for none. **Narrowing:** the explosive groups jump at the end, not "without bound". Narrowed again by part U in full: the 122 were the cheap starts, and 626 more still rise past the memory limit. |
| [JUNCTION-MAP](../JUNCTION-MAP-20261119-001/junction_map.md) | A later stage read by the rule, with the excluded overlap kept as a loop of length two, is right one round and wrong the next, wherever the overlap stands (261 of 261). | Confirmed, nothing to fold. |
| [JUNCTION-KINDS](../JUNCTION-KINDS-20261119-001/junction_kinds.md) | No finite set of kinds of junction carries an exact transfer. The shares a junction passes back take ever more values, in the catalogue's eddies too, because a junction is a growing cluster. | Pending. **Narrowed the same day** by NATIVE-SPINE: the pairing of each round with the two rounds its recurrence names is weak evidence, since a shuffled relation pairs off too. |
| [NATIVE-SPINE](native_spine.md) | No rule tried (newest ancestor, most chains, fewest chains) picks that pairing, and no pair is forced. | Pending. |

**Where it stands.** The steady eddies of the break shapes have the catalogue's rates and round-weights. How the growth produces
them there is unexplained by the cluster map, the junction map, junction kinds or the ancestry. The line is closed as practically
exhausted. The one remaining test that could prove more is the automorphism test (NATIVE-SPINE #1); the explosive kind is a
separate open question.

## Line 2: does the growth need more than the allowed states?

A108 says the cheapest growth reads which junction holds which distinction, not only the allowed states. The question was how far
a growth reading only the states can go.

| Study | What it found | Referee (folded) |
| --- | --- | --- |
| [STATES-GROWTH](../STATES-GROWTH-20261119-001/states_growth.md) | Under not-all-equal, counting constraints of every size, the states' minimal constraints are exactly the knots on 79.8% of small irredundant stages. There the cheapest growth reads only the states. Under parity, which distinctions are loose is a choice of dropped junction beyond the states (Whitney's theorem). | **Block** on the first headline, 93%: the search had stopped one place above the largest knot, a bound read from the knots. A single knot after one round already holds a constraint that is no knot. The parity part is confirmed. |
| [MANY-VALUED](../MANY-VALUED-20261119-001/many_valued.md) | Drawn from the states' minimal constraints, the presentation is unique up to renaming at every point tested. A growth built on it equals the cheapest growth on 1,805 of 1,806 trajectories; the exception is a knot with more places than its constraint needs. | Confirmed and stronger: 1,031 points with every constraint. The uniqueness now names its pool. |
| [DROPPED-JUNCTION](../DROPPED-JUNCTION-20261119-001/dropped_junction.md) | Under parity, only the original dropped junction feeds each of 23 eddies; the same states read with another dropped junction only circulate, stall or close. | **Narrowing:** the sample figures used a shortcut test for implied parity, which differs from the cheapest growth on 19 of 360 re-chosen presentations; no original or eddy choice is affected. |

**Where it stands.** Under not-all-equal, a states-only growth exists (MANY-VALUED's rule). It differs from the cheapest growth only
at redundant knots and at knots with more places than their constraint needs. Under parity the eddies depend on a choice the
states do not record. A108 stays Confirmed, with its reach line corrected.

## Corrections in these lines

All are logged in [docs/CORRECTIONS.md](../../docs/CORRECTIONS.md) and knotlab's `HISTORY.md`:
- 2 Blocks on readings: the short loops; the 93%.
- 5 Narrowings: part U's cheap starts; the explosive groups; the dropped-junction samples; the JUNCTION-KINDS pairing; and the
  LOOP-CATALOGUE prefilter, from its own referee.
- Several corrections that are not blocks.

Lessons added:
- Read W from every factor of the minimal recurrence.
- A run split by memory finishes its cheap part first.
- Compute a states-only quantity from the states alone.
- Check a growth engine's shortcut on every new kind of start.
- Test a matching against a null with the same degrees.
