# Referee hand-off: LOCAL-ROUND-20261123-001

Ticket A is referee pending. Its pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/LOCAL-ROUND-20261123-001A/preregistration.md`. It builds on the shared
definitions and the engine of `RING-IN-BALANCE-20261123-001`, itself referee pending. Nothing in the next step waits for the
verdict.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| Ticket A, [result](../LOCAL-ROUND-20261123-001A/results.md) | That the law R3 (a birth is allowed when the brood of its parents is all-weaned) builds what the complete rounds build in every order searched; that R2 fails at exactly 13 births on the cycle of eight with three extra dead knots and R1 at exactly 7 births wherever a knot waits; that reading within d holder steps first matches at d = 4 on the cycles through dead knots and at d = 6 on the new start; that R0 and R3L fail and the control underbuilds under waiting (P1 to P14) | Exact computation: breadth-first search over every order where it finished (126 of 193 searches), 200 uniformly sampled orders and one order per knot elsewhere | `experiments/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round/` (`README.md` says how to rerun each run; `test_lr.py`; `deviations.md`), outputs in `artifacts/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round/` (`summary.md`, `gate.json`, `runs/`, `listings/`) |
| [Definitions](definitions.md), section 1.4 | The brood argument: under the release rule all children of a parent are born in one complete round, a knot past the start meets only its parents and children, and so an all-weaned brood's roster at birth is the part the complete rounds read next, with its waiters' rosters the parts read after | An argument, not a proof | The definitions |
| The thread's [checks](checks/) | The new start on the earlier study's engine (place counts, who is short in each round, the knot test); a hand trace of the order that defeats R2 | Exact computation and hand work by the designer | `checks/new_start_check.py`, `checks/hand_trace.md` |

Things a referee should know.

- **Two programs.** The drafter of the definitions wrote a prototype before the freeze and disclosed what it found; the
  engine's author never saw it. The two agree on every verdict and on every least number of births that the prototype had
  found by a finished search. They disagree on counts of states in one family (the brood laws where a short knot retires),
  apparently by when a barring is made; this was not run down.
- **The reference is shared.** Both programs are compared with the earlier study's engine, so an error in that engine's
  complete rounds would be shared. The new engine's own rounds were checked against it structure by structure.
- **The advisor's part.** It reviewed the first draft cold and found by hand the start on which R2 fails. Its estimate of
  the distance needed there (10) was wrong; the runs give 6. Its account of the mechanism is right except for which reading
  first goes wrong.
- **Unfinished searches.** 67 of the searches over every order did not finish: 21 at their cap on states and 46 at a time
  budget that the thread added and the pre-registration did not have. Three are being run again to the registered cap (long-running check `LOCALROUND-P7-CAP`). No
  unfinished search found a mismatch for a law predicted to match.
- **What a sampled order is.** At each step a uniform choice among the allowed sets of parents; a member's several offshoots
  count as one choice. Shares of sampled orders are under that choice only.
- **Readings.** The engine's author recorded 27 readings before the runs. The ones that could matter: a barring is made only
  for a knot born by the cutoff; all barrings allowed at one moment are made together.
- **Scope.** The start clause is known to be wrong where a start knot that acts meets one that waits; holding, the fillers
  and the cap of three were not run.
