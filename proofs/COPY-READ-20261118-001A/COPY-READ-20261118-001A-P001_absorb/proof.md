# Absorbing a split needs two end knots

Status: Proved

Ticket `COPY-READ-20261118-001A`, 18 November 2026, by Claude. Epic `COPY-READ-20261118-001`. Written before the run.

## Words

As in `MID-RULE-20261118-001A` and `KEEP-READ-20261118-001A`. After SEED's switch, a fill that makes a new crossing is
**absorbing** when SEED accepts it. Then it gives a split that crossed nothing exactly the crossers of a split that already crossed
something, makes no crossing between two already-crossed splits, and keeps two orders. It is **refused** otherwise. Tiers and
pictures are those of `KEEP-READ-20261118-001A`.

## Statements

- **A1. An absorbing fill has two end knots in every certificate.** It makes a new crossing. So, by `MID-RULE-20261118-001A`, E1,
  in each of its certificates the two states that realise a new crossing are pinned by two different end knots, copying two
  different old distinctions.
- **A2. The bound.** As in `KEEP-READ-20261118-001A`, R2: a rule reading a tier can accept absorbing fills and refuse the refused
  ones exactly only if every absorbing extension has a knot set whose picture class contains no refused move. The share that do,
  the clean-witness fraction, bounds every such rule, and accepting the clean classes attains it.

## Proofs

**A1.** Giving a split crossers it lacked is a new crossing. Apply E1 to each certificate. ∎

**A2.** As R2, with "absorbing" for "keeps two orders" and "refused" for "raises". ∎

## What this leaves to the computation

How many crossing-making fills are absorbing, and the clean-witness fraction at each tier. Following the KEEP-READ referee, it is
scored on runs other than those the classes were learnt from, with the share of test extensions whose class was ever seen.

## Provenance

Local; a consequence of `MID-RULE-20261118-001A` and `KEEP-READ-20261118-001A`.
