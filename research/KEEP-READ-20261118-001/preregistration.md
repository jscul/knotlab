# What the knots read in SEED's second phase: pre-registration

Epic `KEEP-READ-20261118-001`, 18 November 2026, by Claude. It takes `KNOT-SWITCH-20261118-001`'s first direction, chosen by the
coordinator. Goals G1 and G16; challenges A101. Frozen before any read-out of ticket B. The canonical K1–K3 test is unchanged.

## The question

After its switch (the first filled knot), SEED takes only fills that copy or conserve crossings, and so keeps two orders. Can a
reading of the knots near a move, rather than of the crossings, tell the fills that keep two orders from those that raise them?

## Ticket A: the proof (written before this freeze)

`proofs/KEEP-READ-20261118-001A/KEEP-READ-20261118-001A-P001_local/proof.md`.
- **R1.** At tier 0 (the move's own knots) keeping and raising look alike: the corner knot set does both.
- **R2.** At any tier, the clean-witness fraction (extensions keeping two orders with a knot set whose picture class has no raising
  move) bounds every rule reading that tier, and is attained. An exact reading exists on the bases met iff it is 1.

## Ticket B: computation

`experiments/KEEP-READ-20261118-001B/KEEP-READ-20261118-001B-E001_keep/`: `keeplib.py`, `run.py`, `checks.py`, building on
`KNOT-SWITCH-20261118-001B`'s `knotlib.py` and its pinned predecessors. 3 checks pass before this freeze.
- SEED with knot-local moves (SEEDK) from every bracketing of 5, 6 and 7 and every third of 8 (105 starts), one seed each, to
  n = 24. After the switch, every zero-cost KF3 move is recorded with:
  - its outcome (λ after: 2 keeps, more raises) and SEED's acceptance;
  - its pictures at tiers 0, 1, 2 and the closure tier (Weisfeiler–Lehman hash; collisions between a keeping and a raising move
    confirmed by exact isomorphism within each run);
  - its features for the frozen candidate rules: no new filled knot, Δb₂ = 0, disconnected pair graph, the new distinction the
    middle of two or more of its knots, and two conjunctions.
- Controls the advisor asked for: the coverage of the radius-one and radius-two balls (a ball that covers the whole base makes
  purity vacuous), purity over classes met more than once, and the 2 × 2 table of SEED's acceptance against "keeps two orders".

## Decision rules (frozen)

- **A tier reads SEED's second phase on these bases** if its clean-witness fraction is 1, for "keeps two orders" and for SEED's
  acceptance. Otherwise it is obstructed there: some extension that keeps two orders has every knot set alike, at that tier, to a
  raising one.
- **A candidate rule matches SEED** if it accepts exactly SEED's accepted extensions.

## Predictions (frozen; the advisor's unless marked)

| # | Prediction |
| --- | --- |
| P1 | Tier 0 is obstructed (clean-witness fraction below 1); mine, from R1 |
| P2 | Tier 1 is obstructed; its clean-witness fraction over classes met more than once is between 0.3 and 0.6 |
| P3 | Tier 2 is not shown exact in a meaningful way: either obstructed, or its balls cover at least three quarters of the base on average |
| P4 | The closure tier gives a clean witness for at least 80% of extensions keeping two orders, but is not exact |
| P5 | No frozen candidate rule matches SEED; "two or more middle knots" accepts no raising extension and recalls 5–15% of SEED's accepted ones |

**Exploration disclosed.** Before this freeze, four SEEDK runs (16 steps, bracketings of 5 to 7 chosen with seed 1) were read for
move-level features: accepted and refused moves share pair-graph shapes, Betti changes and middles, and "two or more middle knots"
appeared only among accepted moves (9 of 117 accepted extensions). The frozen runs use other seeds.

The advisor was consulted before this freeze. It corrected the unit (acceptance is over knot sets, so an obstruction must hold for
all of an extension's knot sets), proposed R2's measure, the closure tier, the coverage control and P2 to P5.
