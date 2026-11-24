# Referee hand-off: GUARD-CAP-AND-HOLD-20261124-001

Ticket A is referee pending. Its pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/GUARD-CAP-AND-HOLD-20261124-001A/preregistration.md`. It builds on
`LOCAL-ROUND-20261123-001` and `RING-IN-BALANCE-20261123-001`, both referee pending. Nothing in the next step waits for
the verdict.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| Ticket A, [result](../GUARD-CAP-AND-HOLD-20261124-001A/results.md) | That under (CAP-3, CANCEL-WAIT, RELEASE), with and without the fillers, the guard R3 matches the complete rounds in every order searched; that R1 fails at exactly 7 births and R2 at exactly 13; that under holding R1 to R3 stop early and the repaired guard R3′ makes a birth the rounds never make at exactly 13 and 15 births; the table of guards, laws, starts and cutoffs under holding | Exact computation: breadth-first search over every order to a cap of two million states (343 of 386 finished), 200 uniformly sampled orders and one order per knot | `experiments/GUARD-CAP-AND-HOLD-20261124-001A/GUARD-CAP-AND-HOLD-20261124-001A-E001_guard_cap_hold/` (`README.md`, `deviations.md`, `test_gch.py`), outputs in `artifacts/GUARD-CAP-AND-HOLD-20261124-001A/GUARD-CAP-AND-HOLD-20261124-001A-E001_guard_cap_hold/` (`summary.md`, `gate.json`, `runs/`, `listings/`) |
| [Definitions](definitions.md), section 1 | That past the start, under the release rule, the demand of a planned birth is found among the births of the same reading | An argument | The definitions; the gate compares the demand with the reference |

Things a referee should know.

- **One engine.** It is the earlier study's engine, copied and extended by the same author. No second program exists. Two
  hand predictions by the advisor (the 13th and 15th births under the repaired guard; the wrong join on the two-knot
  start) came out exactly, which is the nearest thing to an independent check.
- **The gate fails as worded.** The pre-registration asked for the demand to agree under every law. Under a fixed three with
  waiting and holding it does not, from round 3, exactly as the definitions say it would not; nothing built differs.
- **The advisor's review** corrected one column of a disclosed table (a round with no birth is not an end when knots
  retire), showed that the early stop under holding is true by definition, and proposed the repaired guard.
- **Readings.** 26 are recorded; the ones that matter are how a barring is matched under holding and how the record's
  depth guard is read with the fillers, neither of which the earlier definitions covered.
- **Scope.** The cap with holding is close to empty on the registered starts. The start where a knot that acts meets one
  that waits was left out at the owner's instruction.
