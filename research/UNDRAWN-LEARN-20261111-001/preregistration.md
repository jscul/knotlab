# Pre-registration: learning without a drawing

Epic `UNDRAWN-LEARN-20261111-001` (sub-goal B153, G15 with G16; program learning; challenges A66), written on 2026-11-11 before any
learning run, at the coordinator's go-ahead. The learner, the bases, the marks and the caps are frozen here with the code in
`proofs/UNDRAWN-LEARN-20261111-001A/UNDRAWN-LEARN-20261111-001A-P001_learning_without_a_drawing/` (`undrawn_lib.py`, `check.py`). Nothing
is tuned after a result is read.

## The question

Every learner of the learning line feels its dissonance partly through the faces of a drawing: the corners of the knots around each vertex
of the two-coloured triangulation on which a drawn knot pattern is drawn. The owner's bases are knots that overlap freely, finitely or
infinitely many, and have no drawing. `SHARED-COUNT-20261111-001` learned the count of five held distinctions on two copies sharing a
distinction, still reading each copy's own drawn faces (A66). Does a learner that feels dissonance at knots alone learn the same counts,
and does it learn a count on a base that cannot be drawn at all?

## The drawing-free dissonance, and why it is not the same quantity

- **The learner's dissonance with faces** (`NATIVE-WRITE-20261110-001` onward) is W = 2 × (violated knots) + the sum over the drawing's
  faces of a face term, 0 when a face has exactly one agreeing corner and rising with each further agreeing corner and with an even
  count. Its floor is reached only at a Kasteleyn law (the literature's term: every face odd), where the floor states are the satisfying
  states. A sign may change only where dissonance shows: at a violated knot, or at a knot with a corner on an even face.
- **The drawing-free dissonance** is W = 2 × (violated knots), floor 0. A sign may change only at a violated knot.
- **They are different quantities.** At a Kasteleyn law the floor states coincide, but with faces the learner can rest only at a
  Kasteleyn law (on one copy, 4 law classes, one of which counts), and without faces it can rest at any law with a satisfying state. On
  one copy there are 512 laws (signings modulo flipping a distinction and complementing a knot), and exactly 4 of them count three held
  distinctions at the interface (check R, computed before freezing; no learning run). So the drawing-free learner searches a space 128 times
  larger, and a pass is not settled by definition.
- **The credit rule, read without faces.** The credit learner cools a knot whose surroundings stay dissonant through a short walk. With
  faces, a face was pinned when it and every face sharing a knot with it never cleared of dissonance, and a knot was cooled when its three
  corner faces were pinned. Without faces, a distinction is dissonant when it lies in a violated knot; it is pinned when it and every
  distinction sharing a knot with it never clear; a knot is cooled when its three distinctions are pinned and none is held or read. This
  is the one change to the learner: `credit_lib.py`, `io_lib.py`, the sturdier probe and the harness run unchanged on an engine that
  presents distinctions where the drawn engine presented faces (`undrawn_lib.KnotEngine`).

## The bases (structure checked before freezing; no learning run)

- **J1:** one copy of the drawn knot pattern (2, 0, 4) (the literature's torus, drawn), `SHARED-COUNT-20261111-001`'s J1 and
  `LEARN-PARITY-20261111-001`'s T1: inputs 0, 1, 4, read 5. 4 of its 512 laws count.
- **J2:** two copies sharing one distinction, `SHARED-COUNT-20261111-001`'s J2: five held distinctions. Its laws were not counted
  (2^18 laws of 2^15 states); the copies' tightest classes count, by definition.
- **U, a base with no drawing:** the frozen rule (`chosen_undrawn`) takes the first (distinctions, knots) among (6, 7), (6, 8), (7, 8),
  (7, 9), (8, 9), (8, 10), and in it the first seed below 100, whose random pattern of three-place knots (distinct, connected) has a law
  that counts three held distinctions, while its plain law (every sign 0) has a satisfying state and does not count there. It is (6, 8),
  seed 92: 6 distinctions and 8 knots, {2,3,4}, {0,3,5}, {0,1,2}, {0,4,5}, {1,4,5}, {3,4,5}, {0,1,5}, {1,3,5}, with 4, 4, 2, 4, 4 and 6
  knots at its distinctions, so it is not a drawn knot pattern (where every distinction lies in three knots). Inputs 0, 1, 3, read 4;
  distinctions 2 and 5 hidden. Exactly 1 of its 2,048 laws counts there, and it is the only counting set in any law. Its plain law's map
  is `u001011u`; the learner starts there. With 6 distinctions it counts three held distinctions with fewer distinctions than any drawn
  knot pattern found so far (8, `PARITY-NEEDS-20261111-001`); that is an observation of the search, not a minimum.
- The engine counts distinctions and knots with one number, so J2 and U are padded with inert distinctions in no knot, never held, read
  or disturbed.

## The learner and runs (frozen)

`SHARED-COUNT-20261111-001`'s harness with the drawing-free engine: the credit learner, the sturdier probe over every input pattern, the
floor 0. Budget 8,000,000 steps per target. Ten runs per base, learner seeds 9400 + k (J1), 9500 + k (J2), 9600 + k (U). Targets: the count
of the held inputs, its negation, the count again. After each stop one random real distinction off the interface is flipped, M1 runs to
the floor, and the map is read again by SAT.

## Marks (decisive, one line each)

- **V:** the engine's running dissonance equals a fresh count after 20,000 random moves on J1 and J2 (computed before freezing: it does).
- **R (exact):** the law counts above (4 of 512 on J1, 1 of 2,048 on U).
- **L1:** on J1, the count of three (first target) learned and held in at least 8 of 10 runs.
- **L2:** on J2, the count of five learned and held in at least 8 of 10 runs.
- **L3:** on U, the count of three learned and held in at least 8 of 10 runs.
- **When the faces did real work (frozen).** The faces did real work for these counts if L1 or L2 fails, since the learner with faces
  passed both (10 of 10, `LEARN-PARITY-20261111-001` and `SHARED-COUNT-20261111-001`). Then A66 is **Confirmed** for that reason. If L1 and
  L2 both pass, the faces were not needed for them, and A66 is **Overturned** as the line's reading: the learner for bases with no drawing
  reads violated knots alone. Steps are compared with the learner with faces and reported, but are not a mark. L3 bears on whether the
  learner learns on a base that cannot be drawn, not on the faces.

## Predictions

V and R as computed. L1 passes but slower than with faces (128 times the laws); L2 is uncertain; L3 fails more likely than not (1 law of
2,048, and the plain law starts far from it).

## Caps and long runs

Runs are written one by one as they finish (`runs_learn1.jsonl` and so on). Per run: 30 minutes on J1 and U, 120 on J2; a run over its cap
is dropped and counts as not learned. Per part (systemd, MemoryMax 24G, no swap): 40, 150 and 40 minutes; runs missing at a part cap
count as not learned. The learning parts are registered in `docs/LONG_RUNNING.md` before they start.

## Stop

L1, L2 and L3 settled and the faces' role stated; then report.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58; A66 under challenge.
