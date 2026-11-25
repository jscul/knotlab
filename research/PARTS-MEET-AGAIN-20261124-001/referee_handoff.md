# Referee hand-off: PARTS-MEET-AGAIN-20261124-001

Ticket A is referee pending. Its pre-registration has the prior-work searches under "Prior work in the program"; run
`python3 -B scripts/track.py objects-gate research/PARTS-MEET-AGAIN-20261124-001A/preregistration.md`. It builds on
`RING-IN-BALANCE-20261123-001`, `COPYING-PARTS-20261123-001`, `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` and
`ONE-PARENT-REREAD-20261123-001`, all referee pending. The next study waits on nothing here but the law it names.

| Record | Claims to check | Evidence class | Code and data |
| --- | --- | --- | --- |
| [Pre-registration](../PARTS-MEET-AGAIN-20261124-001A/preregistration.md), "Settled by construction", arguments 1 to 5 | That under a law in which every distinction a new knot takes is held by one of its parents, and joinable is read from the structure, two parts that are wholly apart never become one part and never have a joint birth; that under the release rule every two parts are wholly apart after round 0 on the registered starts; that joining by the record alone cannot rejoin either | An argument (one induction), checked by the advisor in a first form and rewritten since; not checked in its present form by anyone but the drafter and the thread | The pre-registration |
| Ticket A, [result](../PARTS-MEET-AGAIN-20261124-001A/results.md) | The gate against three existing engines; that rules Q and R never rejoin (P1, P2, P5); that they undo the ring and the copier (P3, P4); the 302 marks for parts that came apart with their verdicts and linking knots; the smallest case round by round; the cost of each law; the swap results; the knot tests | Exact computation by an engine written from the frozen text; a second, independent program (the drafter's prototype) agrees on all 302 marks | `experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/` (`README.md`, `deviations.md`, `test_engine.py`), outputs in `artifacts/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/` (`summary.md`, `replays.json`, the run files) |

Things a referee should know.

- **A registered run is unfinished.** The enumeration of every choice under rules Q and R with the swaps has 285 of 360
  parts done; the rest are running (long-running check `PARTSMEET-RUN2`). Nothing in it has gone against the argument.
- **Two programs.** The drafter wrote a prototype before the freeze and disclosed what it found; the engine's author never
  saw it. They agree on every mark and verdict. Their agreement does not cover the argument, which neither program proves.
- **The knot test for large knots is by an argument.** Under not-all-equal, knots of more than 12 places are tested by a
  method stated in the definitions, section 7, and checked against the direct test on every smaller knot and on 600 drawn
  structures. A referee may want to check that method.
- **Two failed clauses and one open reading** (P15, P16, P11) come from wording in the frozen text that did not fix which
  parts or which comparison was meant. The result note says how each was read.
- **What "made by the growth" means here**: that the meeting and the dependence are made by births under a stated law with
  nothing placed by hand after the start. The law and its way of choosing are supplied in every case.
- **Words.** "Ancestral common knot" and "ancestor-taking" were chosen with the advisor and approved by the owner; his own
  phrases for the first were "axis point" and "access point".

**Update of 25 November 2026.** The unfinished enumeration has done 358 of its 360 parts (3,571,746 histories: every
possibility in 326 parts, 100,000 taken at random in each of 32). Nothing against the argument; two parts still running.

**Second update of 25 November 2026.** The last two parts were stopped at the owner's word, and the enumeration is
left unfinished at 358 of 360. Both are on Ring(5, 3) with the swap ONE-FEWER: 59,000 of 100,000 histories had been
taken under parity and 2,000 of 100,000 under not-all-equal, with nothing against the argument in either. Read P1 as
checked on 358 parts.
