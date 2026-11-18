# SEED's copy clause read in the knots: pre-registration

Epic `COPY-READ-20261118-001`, 18 November 2026, by Claude. It takes `MID-RULE-20261118-001`'s first direction, with the
coordinator's go-ahead. Goals G1 and G16; challenges A101. Frozen before any read-out of ticket B. The canonical K1–K3 test is
unchanged.

## The question

A local rule that never adds a crossing cannot pull in a split the first fill left uncrossed (`MID-RULE-20261118-001`). SEED does,
with its copy clause, through fills that must have two end knots. Can the knots near such a fill tell an absorbing fill from a
refused fill that also makes a crossing?

## Ticket A (written before this freeze)

`proofs/COPY-READ-20261118-001A/COPY-READ-20261118-001A-P001_absorb/proof.md`.
- **A1.** Absorbing fills have two end knots in every certificate.
- **A2.** The clean-witness bound.

## Ticket B

`experiments/COPY-READ-20261118-001B/COPY-READ-20261118-001B-E001_copy/`: `copylib.py`, `run.py`, `checks.py`, building on
`KEEP-READ-20261118-001B`'s `keeplib.py` and its pinned predecessors. 1 check passes.
- SEEDK from every bracketing of 5, 6 and 7 and every third of 8 (105 starts) to n = 30. After the switch, every zero-cost move
  that makes a new crossing is labelled absorbing or refused and given its tier-0, closure and tier-1 pictures, with the radius-one
  ball's coverage.
- **Held-out scoring** (the KEEP-READ referee's request). Classes are learnt on the runs with an even start index and scored on those
  with an odd one, reporting the share of test absorbing extensions whose class was seen at all.

## Decision rules (frozen)

- **A tier reads the copy clause on these bases** if every absorbing extension has a knot set in a class with no refused move, in
  the pooled data and in the held-out score.
- **Obstruction** if some absorbing extension has every knot set alike, at that tier, to a refused move (confirmed by exact
  isomorphism within a run).

## Predictions (frozen)

| # | Prediction |
| --- | --- |
| P1 | Absorbing fills are rare: fewer than 1% of the crossing-making fills after the switch |
| P2 | Tier 0 and the closure tier: clean-witness fraction 0, every absorbing extension alike to a refused one |
| P3 | Tier 1: held-out, fewer than half the test absorbing extensions have a seen, clean class |
| P4 | Absorptions happen early: the median n at which an absorbing fill is offered is below 15 |

**Exploration disclosed.** Before this freeze, six SEEDK runs (bracketings of 6 to 8, seed 11, to n = 22) were read: 20 absorbing
moves against 21,609 refused crossing-making moves, all 20 in tier-0 and closure classes that also hold refused moves. P1 and P2
rest on that look. The gate check's four short runs found 8 confirmed look-alikes.

The advisor was not consulted for this design. It reuses `KEEP-READ-20261118-001`'s method, which the advisor and the referee
shaped, with the referee's held-out request added.
