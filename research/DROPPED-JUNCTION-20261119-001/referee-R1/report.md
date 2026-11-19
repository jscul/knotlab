# Referee report DROPPED-JUNCTION-001-R1 (own completed systems, own growth)

Code shared with STATES-GROWTH-001-R1: `research/STATES-GROWTH-20261119-001/referee-R1/job_states.py` (part P, under
`scripts/longrun.py`), `states_readout.py`, `referee_states.json`.

**Verdict: the headline (D1) is confirmed. No Block; one Narrowing on the sample readouts.**
- **`droplib.rechoice` is right.** The referee rebuilt the completed system and every dropped choice itself: 177 choices on the 23
  eddies, and 360 on every fifth of the 300 sample starts. In all 537, the junction equations span the original's space, so the
  parity states are the same.
- **D1 holds (23 of 23).**
  - **The counts.** On every choice of every eddy, the referee's engine (complete rounds, fewest counts, GF(2) implication)
    gives the study's counts.
  - **Exponential:** the original choice, in 22 by the referee's classifier. Ring-7 reaches the referee's 30,000-junction cap
    before the classifier has rounds enough; its counts, equal to the study's, grow like 1.618ⁿ.
  - **The rest:** none of the 154 other choices is exponential. 110 are quasi-polynomial, 42 close and 2 stall.
- **A ring by hand: the ring of five with a spare (`cat-0`), dropping knot 1.**
  - **The presentation.** The junctions are knots 0, 2, 3 and 4 and the former out. The loose lines are (0,1) at knot 0, (1,2) at
    knot 2, and two (1,out) lines at out.
  - **Round 1.** The three live junctions pairwise share a neighbour: 0 and 2 share out, 0 and out share 4, 2 and out share 3. No
    junction is a neighbour of all three, so they form a group of three. It joins (0,1), (1,2) and one (1,out); the other (1,out)
    is an offshoot. That makes 2 junctions.
  - **Round 2 on.** The two new junctions share out. Fewest counts give the joined one 1 fresh distinction and the offshoot 2. They
    pair, and one offshoot stays, so the counts run 5, 2, 2, 2, …: a chain, one-dimensional.
  - **Both engines agree.** Dropping the spare knot instead closes (3, 3, 1).
- **Narrowing: the study's engine is not the cheapest growth on some non-original choices.**
  - **Where.** On the sample, 19 of the 360 choices differ from the referee's counts after round 1 or 2: 12 with every junction of
    three places or more, 7 with smaller junctions. None is an original choice and none is on an eddy.
  - **Why.** droplib grows with GF(2) elimination switched off (`P.linalg = False`, JOIN-GROWTH's structural implied-parity test,
    which that study justified for its own connected starts). A re-choice can hold two junctions that differ by one distinction,
    which forces that distinction constant.
  - **An example.** In S-000 dropping knot 1, the junctions [3, 4, 5, 6] and [1, 3, 4, 5, 6] force distinction 1 to be 0. The
    offshoot on 1 then has an implied parity and demand 0, so the policy gives it no fresh distinction. The study's engine (run as
    a labelled cross-check) gives it 2.
  - **What it touches.** The sample readouts (the class counts under the other choices) and D3's 14 of 171 rest partly on such
    choices. They were not recomputed in full.

## Other points

- **Junctions of fewer than three places.** 70 of the 537 choices make one: a dropped neighbour can leave the former out, or a
  knot, with one or two lines. These are not presentations in the program's sense, yet "every choice" includes them.
- **Starts that do not grow.** One sample start (S-065) has no loose distinction, so its out is an isolated point and every other
  choice leaves an empty junction. "300 random growing five-knot starts" also counts 67 that close under the original choice (the
  note's own readout). "Growing" means "not stalled at the start".

## Corrections for the owner (listed, not folded in)

1. **The sample readouts and D3 (Narrowing).** Grown with GF(2) elimination off, some re-choices are not grown by the cheapest
   growth: 19 of 360 choices checked differ. The original choice and every eddy choice are unaffected, so D1 and the headline stand.
   Rerun the sample with elimination on, or say "the structural test" in place of "the cheapest growth" there.
2. **Choices with a junction of fewer than three places** (70 of 537) should be set apart or named. **Not a block.**
3. **"Growing" starts** (67 close under the original choice): reword. **Not a block.**

## How the work was split

- **The referee:**
  - read `dropped_junction.md`, `droplib.py` and `job.py`;
  - wrote part P of `job_states.py` (completed system, re-choices, span equality, growth with its own engine), on its FIRST-KNOT-R1,
    TOUCH-CENSUS-R1 and LOOP-CATALOGUE-R1 code.
- **Read as data:** the study's starts and records (`runs/dropped-junction`).
- **Run as a labelled cross-check, once:** the study's engine (`joinlib`), on the S-000 choice above, to locate the difference.
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
