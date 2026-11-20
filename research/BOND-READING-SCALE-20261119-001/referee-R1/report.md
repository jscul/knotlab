# Referee report, group 3: the remaining studies of 2026-11-19 evening (lean)

**One correction is logged (Not a block): the first round-nine average for start-03.** Otherwise what was checked stands. Several
studies were not refereed in depth (listed at the end).

## BOND-READING-SCALE: how many distinctions must be read together. Stands.

- **The limiting reading: proved, read line by line.**
  - **The test.** A set S is a bond exactly when K(S) = |S|. Bonds on shared distinctions alone, with the growing end, span all
    the equations, and the equations then carry every later round by equation transport.
  - **The converse holds.** Equations on old names stay exactly the old span at every later stage, so a different span is
    always seen later.
- **The size bounds: read and correct.**
  - "Reading through J knots suffices": a unique least bond through one name per neighbour recovers each spent knot's support.
  - The 1 + ⌊(2n − 1)/5⌋ and 1 + ⌊(2n + 9)/7⌋ bounds. The second uses a cut-tree basis lemma and the interval argument checked
    in GROWN-END-READING-R1.
- **The order-two minima: checked directly.** The five-knot, 11-distinction witness and the six-knot meet-once witness were each
  regrown from their predecessors with the referee's engine.
  - Each keeps every pair reading and not every triple.
  - Each maps a bond outside the span: {1, 2, 7, 8} and {0, 6, 10}.
  - At the next stage all 91 pair entries are kept, while the image lies in no bond.
- **Not rebuilt:** the censuses behind "minimum" and "21 exactly", the 3r + 4 construction, and the three-attachment result.

## The partnered starts. Stand.

- **PARTNER-SEVEN.** The 32-knot, 78-distinction start of at most six places, regrown by the referee's engine, makes 6 knots of
  (4 parents, 4 fresh) whose growing end is the order-three partnered arrangement. It then follows the partnered recurrence,
  (3, 5) × 8 and (4, 12) × 10.
- **JUNCTION-SIZE-FOLLOW.** Birth sizes of 8, 16, 2,048 and 2^2042 are p + f along the partnered start, which the referee's
  WALL-READ check reproduced.

## The round-nine size of start-03 (start-03 is EXPLOSIVE's start of sizes 5, 5, 7, 6, 4, 5)

- **NINTH-ROUND-SAMPLE: does not stand as an estimate.**
  - Its average of 4.70×10¹² is more than 74-fold below the later exact count of three disjoint group families (at least
    2.17×10¹⁵), and far below the later sampled reading of about 9×10²⁷.
  - **Still standing:** its proved lower bound (16,777,243), its statistical lower limit as a weak lower limit, and the exact
    round-8 figures.
  - **Logged** in `docs/CORRECTIONS.md` as Not a block.
- **HUB-GUIDED-SAMPLE** (group 2) stands as a sampled estimate.

## THREE-RIGID: three-way rigidity on stages of at most 14 knots

- **Its all-size R3 is refuted** (GROWN-END-READING-R1), and that is already logged ("Three-way rigidity holds to 14 junctions, not
  at size").
- **Not rerun:** its bounded hunt.

## FIVE-PLACE-RATE

- **The stated rate is a root of λ³ − 4λ − 4 = 0** (2.3829757679…), checked.
- **Not read:** the ceiling proof.

## Not refereed in depth (headlines read only)

BOND-READING-WEIGHTINGS, GROWTH-CONTINUES, HEAVY-GROWTH and PARTNER-RETRACT. READ-ORIGIN-20261120-001 is newer and was not in this
queue.

## How the work was split

- **The referee:** read the decision notes and the proofs named above. It checked the witnesses with its own engine and readings,
  run directly; each check took seconds.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
