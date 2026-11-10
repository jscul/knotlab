# Pre-registration: credit from pinned dissonance

Epic `CREDIT-PIN-20261110-001` (backlog B132, G15), at the coordinator's go-ahead of 2026-11-10. Written in two stages, each committed
before the runs it governs: **stage 1** (this section and the next two) freezes the defect fix, ticket A's re-run, ticket B's targets and
marks, including the mark for "pinned dissonance misleads"; **stage 2** (appended below, before ticket B runs on any test space) freezes
the credit learner's details, developed on the dev spaces only.

## The question

`IN-OUT-20261110-001` learned gates of held inputs at single atoms (53 of 56) but not through composites (1 of 16): a composite's
interface reads its inner atoms only through the AND of their acting bits (lemma C), so the examples give no signal until every inner
atom acts. Each acting atom holds dissonance the state cannot walk away (P1 of `NATIVE-WRITE-20261110-001`), and the learner can see
that. Does using it as partial credit let the learner reach composites, and does it mislead?

## Ticket A: the defect fixed, and the frozen re-run

- **The defect.** The frozen learner of `IN-OUT-20261110-001` probes only at its floor and widens its attention only after failed probes.
  A failed write could leave it above its floor with dissonance outside its attention, and it never probed again (three composites,
  every later target).
- **The fix (frozen in `proofs/CREDIT-PIN-20261110-001A/CREDIT-PIN-20261110-001A-P001_the_fixed_learner/fix_lib.py`).** A run of 40 probe
  slots in a row that pass above the floor counts as one failed probe for widening. Nothing else changes.
- **The re-run.** `IN-OUT-20261110-001`'s test exactly: S1 to S4, its 18 interfaces, targets `1uu0`, `u10u`, `uuuu`, `0uu1`, `0001`,
  learner seed 3000 + k, the same outcomes and marks (L, C, A, R, K) and census. Reported: whether 53 of 56 at leaves and 1 of 16 at
  composites change, and how often the probe is fooled (inexact stops). The probe stays marked computed.
- Checked on dev only before this freeze: the fix lets a learner that stalled above its floor recover (dev runs).

## Ticket B: targets and marks (frozen now)

- **Targets.** At every interface of S3 and S4 (8 leaves, 4 composites) and of S5 (the outer K_3 with three composites C(2, thin): 6
  leaves, 3 composites), the targets `1uu0`, `u10u`, `uuuu`, `0uu1` and then `0001`, from each space's start. Learner seed 3000 + k for
  S3 and S4 as in ticket A (the same k), 5000 + k for S5's interfaces.
- **Outcomes** as in ticket A, each counted on its own.
- **C2:** credit reaches composites iff at least 90% of the 16 composite writes of S3 and S4 (four targets at four composites) are learned
  and held.
- **M (pinned dissonance misleads):** on S3 and S4, at the same interfaces, targets and seeds, pinned dissonance misleads iff the credit
  learner has fewer writes learned and held than ticket A's fixed learner (leaves and composites together), or more inexact stops.
  Reported with it: the share of the lines the learner cooled that lie in an atom acting at that moment (read by SAT afterwards).
- **A:** `0001` never stops.
- **S5 (one size past):** the C2 mark on its 12 composite writes, and the M comparison is not made there (ticket A does not run S5).

Assumptions in force: A20, A21, A46, A47, A49, A50 (its temperature alternative), A52, A58.
