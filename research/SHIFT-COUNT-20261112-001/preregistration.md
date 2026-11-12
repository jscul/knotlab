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

## Tickets A and B (frozen after the advisor's critique, before their runs)

**Weighting.** As in COMMON-FOLD: uniform r-sets of the 171 knot kinds of the box [0, 2] × [−2, 2], r = 3 to 6; the 169 bases with a
certified travelling pattern there. Shares read as typical or rare under that weighting only.

**What is settled by definition (checks, not predictions).** The cone corollary: one pattern on a free set A travelling along two
independent shifts t₁, t₂ forces ±p on A + m t₁ + n t₂ for all m, n ≥ 0 (COMMON-FOLD's lemma, twice), so every distinction of those
translates is within bond distance |A| of some member of A; it covers those translates, not every distinction of the cone, and it gives
no bound from a fixed origin (bond distance has no triangle inequality): FAR-BOUND's one-base proof needed residues and certificates
for that. The referee's certified count (at least 130 of 169 with two directions, shifts to 4, sets of 2 or 3 in [0, 2]²) is contained
in ticket A's family, so at least 130 certified is settled by data. A base with a measured certified bond of 5 or more at a cell
cannot carry, through a set of four or fewer, a second direction whose cone holds that cell (the lemma's bound), so "the three bases
that grow across stay one-direction" is partly settled; only directions whose cones miss the measured cells test it.

**Ticket A (frozen in `experiments/SHIFT-COUNT-20261112-001A/`).** Family: sets of 2 to 4 cells of [0, 2]² holding the origin, every
pattern, every primitive shift with entries up to 6 in absolute value (both senses), multiples up to 4; forced by window SAT,
certified by tori or eventually periodic strips (p with σ(p) on A + kt, and A free). Reported per base: forced, certified and forced-
but-uncertified directions; ranks. Negative control: base 16 has one direction only (checked before freezing: only (1, −1)).
Predictions: **A1** certified rank 2 on at least 140 of 169 (the referee's 130 plus at least 10 from the wider family; my uncertified
search found 136 with a smaller family); **A2** certification yield: the bases with forced rank 2 but no certified second direction
are at most 10% of those with forced rank 2; **A3** none of the three bases growing across near the origin, nor base 16, gets a
certified second direction. Failure: any of these below its bound; A1's failure with A2's holding means the family, not the
certificates, is the limit.

**Ticket B (frozen in `experiments/SHIFT-COUNT-20261112-001B/`).** Bases fixed now: FAR-BOUND's five creeping bases ((17, 4),
(17, 5), (109, 3), (112, 4), (183, 4)) and its five one-direction bases that stayed bounded to 23 across ((11, 5), (109, 4), (137, 4),
(97, 5), (133, 4)). Tests S1 (structure of the least certified far bond: relay, the largest gap at most 6, or two clusters, a gap over
|y|/2), S2 (two clusters: the far cluster translated by s u, s = 1 to 12, a certified bond of the same size at y + s, y + 2s and
past y + 40), S3 (creeping bases: the exhaustive least certified bond at 27 across on the side of the rise, |S| ≤ 6; censored if
none). **What distinguishes growth from a higher bound, said in advance:** no finite computation does. A relay structure (S1) means
the bond must hold cells spread across the whole offset, so its size grows with the offset unless relays can be spaced ever wider: it
points to growth. A two-cluster bond whose far cluster translates (S2) is a bound along that progression, and a travelling pattern
across (ticket A's kind, with a larger set) would make it a theorem: it points to boundedness. S3 checks whether the rise continues.
Predictions: **B1** the creeping bases' far bonds are relays on at least 3 of 5; the bounded ones' are two clusters on at least 3 of
5. **B2** where two clusters are found, a translation works on at least half. **B3** on the creeping bases b(27) ≥ b(23) on all
decided, and b(27) ≥ b(23) + 1 on at least 2 (censoring at |S| ≤ 6 counts as undecided, not as growth). Failure: each below its bound.

**Runtime.** A: about an hour on 6 workers; B: up to an hour on 5 workers; each base saved as it finishes, caps 1,800 s (A) and
3,600 s (B); registered.
