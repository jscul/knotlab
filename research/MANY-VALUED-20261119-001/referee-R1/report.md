# Referee report MANY-VALUED-001-R1 (own presentations, own growth)

Code shared with STATES-GROWTH-001-R1: `research/STATES-GROWTH-20261119-001/referee-R1/job_states.py` (parts T and X, under
`scripts/longrun.py`), `states_readout.py`, `referee_states.json`.

**Verdict: confirmed, and stronger than stated. No Block; two wording points.**
- **The refined rule holds with every minimal constraint.** The study's M(S) stops at one place above the largest knot
  (STATES-GROWTH-001-R1). The referee recomputed M(S) over every size and redid the whole trajectory part with its own engine
  (complete rounds, fewest counts, implication by SAT) and its own presentation search.
  - **The result:** the refined states-only growth equals the cheapest growth on **1,805 of 1,806** census trajectories without a
    redundant knot.
  - **The one exception is the study's:** the start (3, 3, 3, 5) with the non-minimal five-place knot.
- **Uniqueness holds at far more points than 146.** With every minimal constraint, 1,031 unsaturated points along the trajectories
  have at least one presentation drawn from M(S):
  - every one has exactly one up to renaming;
  - the K4 case has two presentations in one class;
  - 36 points (on trajectories with redundant knots) have none, as the note reports.
- **`manylib.presentations` is right in both pools.**
  - **Admissibility** checks three places or more, every distinction held once or twice, and every distinction held.
  - **Irredundancy** checks that removing any member changes the states. Removing constraints never removes a state, so an equal
    count means equal sets.
  - **"Same states"** compares the sorted state lists.
  - **The referee's own search** (backtracking over the pool, every distinction at most twice) agrees with it.
- **The exceptional start, by hand (the owner's second point).** Knots (0, 1, 2), (3, 4, 5), (0, 3, 6), (1, 2, 4, 5, 6) allow 52
  states, and so does the same with (1, 2, 4, 5).
  - **The core.** NAE(1, 2, 4, 5) holds on every state. The minimal constraints are exactly B's four knots, and (1, 2, 4, 5, 6) is
    not minimal.
  - **The growth.** In A every distinction is held twice, so the referee's engine closes it at once. B holds 6 once and grows 1, 2,
    3, 4.
  - **The presentations.** From M(S) alone there is one, B. From M(S) and A's knots there are two, A and B, not isomorphic.

## Wording points for the owner (listed, not folded in)

1. **"The allowed states have exactly one presentation up to renaming"** (the answer, the final report). It holds among
   presentations drawn from M(S) and the stage's own knots. The exceptional start shows that a non-minimal support outside that
   pool gives a second, non-isomorphic presentation of the same states (A and B above). The Limitations say the full pool was not
   enumerated, and the headline should carry the same qualifier. **Not a block.**
2. **The 146 points were counted at STATES-GROWTH's cut.** With every minimal constraint there are 1,031 unsaturated points, and
   the uniqueness and the 1,805 of 1,806 hold there too. This strengthens the result, and the note could say so. **Not a block.**

## How the work was split

- **The referee:**
  - read `many_valued.md`, the pre-registration, `manylib.py` and `job.py`;
  - wrote parts T and X of `job_states.py` and the readout, on its NAE-GROWTH-R1, FIRST-KNOT-R1 and TOUCH-CENSUS-R1 code.
- **Read as data:** the census keys and the study's records.
- **No study code was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
