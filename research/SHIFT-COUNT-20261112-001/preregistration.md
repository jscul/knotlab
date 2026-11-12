# One unlengthened shift against two: pre-registration

Epic `SHIFT-COUNT-20261112-001` (`FAR-BOUND-20261112-001` direction 1; G1 with G17, question 9; program topology, group spacing),
2026-11-12, at the coordinator's go-ahead. Each ticket is frozen here before its own run: ticket C first (its design is the harmony
thread's, already frozen), tickets A and B in a later section of this file, after the advisor's critique and before their runs. The
canonical K1–K3 test is unchanged.

## Ticket C: which repeat sizes carry a travelling pattern (frozen now)

The test is frozen word for word in `research/LINE-LOCK-20261112-001/preregistration.md`, section "A test proposed for the
knots-alone thread" (commit 023a3da46): its run, its tiling prediction, its three refutation criteria and its rival control. Run
here by `experiments/SHIFT-COUNT-20261112-001C/.../census.py` on:
- base 16: the part {(0,0), (0,−1), (0,1), (0,5)} with (8, 5) of its heddle bond, patterns 00001 and 00010 (the two no doubly
  periodic state of period at most 8 carries; FAR-BOUND carries them by an eventually periodic strip);
- each of the 29 bases FAR-BOUND's recheck left unresolved: the first window-only set's first part pattern that no doubly periodic
  state up to 8 carries (targets in the recheck's order).
Lattices ⟨(n, 0), (k, m)⟩ of each base's frame, n, m ≤ 24, 0 ≤ k < n. Reported per pattern against the three refutation criteria
(C empty; every size past a threshold; no line count equal on parallel lines) and the rival (colliding images). Seen before freezing:
on base 16, no lattice up to 10 × 10 carries 00001 (a smoke test of the code). Each item in its own process, written as it finishes,
capped at 1,800 s.
