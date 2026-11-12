# Across the fold: pre-registration

Epic `ACROSS-FOLD-20261112-001` (`FOLD-20261112-001` direction 1; G1, question 9; program topology, group spacing), 2026-11-12, at
the coordinator's go-ahead under the owner's standing mandate. The canonical K1–K3 test is unchanged.

## Words

As in `FOLD-20261112-001`: base 16, the sheared frame (knot kinds {0, (0,1), (1,0)} and {0, (0,2), (1,2)}), columns and rows there,
bond, bond distance, steps apart. The **fold** is the column direction: by FOLD's theorem the origin is at bond distance at most 3 from
the distinctions (k, t) with t in −2 .. 2 and every k ≥ 3. **Across the fold** means changing the row. The **ladder** L_y (y ≥ 2) is a
set in column 0: the triple {0, 1, 2} with the rungs 4, 6, …, y when y is even, or the triple {−1, 0, 1} with the rungs 3, 5, …, y when
y is odd. It contains the origin.

## The question

How does the law's bond distance grow across the fold: between the origin and (k, y) for rows y away from 0 and far columns k? Does the
law read base 16 as a line across its fold?

## Disclosed before freezing

Pilots outside the registered run, in the scratchpad:
- **A first guess failed.** A whole column segment (rows 0 to y) with (k, y) is not a bond for y ≥ 3, and at y = 4 a bond of five
  exists: the law's distance across grows more slowly than one per row.
- **The column-0 profile.** At k = 5 and 8, the least bond made of a set in column 0 containing the origin and the target (k, y) has
  size 4, 4, 4, 5, 5, 6, 6, 7, 7 for y = 0 to 8, always a ladder (y ≥ 2) or a triple (y ≤ 1): size floor((y + 1)/2) + 3 for y ≥ 2, the
  same at both k. For y = −3 and −5 none was found up to size 7.
- **The ladder check** (ticket A's `check.py`) was run before this record, three times: it passed C1 (a ladder all equal forces the
  same ladder, opposite, one column on) and C3; C2 failed at k = 1, where the set contains a knot, and, for y ≥ 5, at the nearest
  columns: L_y with (k, y) is a bond exactly from k = floor((y + 1)/2) + 1 on (from k = 3 for y ≤ 4) among k ≥ 3. Nearer, a cheaper
  set does it: a pure ladder of rungs two rows apart shrinks by one rung per column (rows −1, 1, 3, 5 all equal force row 5 three
  columns on), so the full ladder is not minimal there. The statement below is the one the check passed.

## What is settled by definition, and what is not

- **The upper bound is FOLD's mechanism.** A ladder all equal travels one column at a time, its value flipping, as FOLD's triple does:
  each rung r forces row r one column on through the pair (r − 2, r). So d(origin, (k, y)) ≤ floor((y + 1)/2) + 2 for y ≥ 2, at every
  k ≥ 3, once freeness is checked (ticket A).
- **The lower bound is not.** That no smaller bond exists is the content. Ticket B checks it in the column-0 family to y = 10 and,
  among all bonds of size at most 4, in a box for y = 3 and 4.
- **Rows below.** Forcing moves values only onto the rows of the forcing pairs or two rows up, never below the lowest known row; so
  sets in column 0 reach downward targets only by containing their rows. Whether any bond reaches (k, y) for y ≤ −3 is open.

## Ticket A: the statement (`proofs/ACROSS-FOLD-20261112-001A/`)

**Theorem L.** For y = 2 to 8 and every k ≥ max(3, floor((y + 1)/2) + 1), L_y with (k, y) is a bond of size floor((y + 1)/2) + 3.
Failure would be such a k and y where a proper part is not free, or a rung the chain does not need. (Checked before freezing, as
disclosed; the referee is the independent test.)

## Ticket B: the lower bounds (census, frozen in `experiments/ACROSS-FOLD-20261112-001B/`)

- **M.** For k in {5, 8, 11} and y in 0 .. 10 with k ≥ floor((y + 1)/2) + 1, the least column-0 bond with (k, y) has size 4 for y ≤ 1
  and floor((y + 1)/2) + 3 for y ≥ 2. Failure: a smaller one, or one that depends on k. Nearer columns are measured, not predicted.
- **D.** For y in {−3, −4, −5} and k in {5, 8, 11}, no column-0 bond up to size 7. Failure: one found.
- **N.** No bond of size at most 4 contains the origin and (5, 3), or the origin and (5, 4), with its other members anywhere in
  columns −1 .. 6 and rows −3 .. 7. Failure: one found, a shorter way across than the column-0 family.

## Decision rules

- **L, M and N hold:** across the fold, upward from the origin, the law's distance grows by one for every two rows, at every far
  column; so a ball of bond radius r holds rows 0 to 2(r − 2) above the origin at every far column: one dimension across, read
  natively, at half the rows' rate. **D holds:** below, the column-0 family reaches nothing, an asymmetry to explain. Near the
  origin the distance across is shorter still (the shrinking pure ladders); the far-column profile is the one that measures the fold's
  cross-section.
- **M or N fails:** the law's distance across is shorter than the ladders, and the first shorter bond is the next object.

## Prior work

As in `FOLD-20261112-001` (Ledrappier's shift and non-mixing shapes; directional determinism). Travelling patterns that grow with the
forcing set are the same mechanism; none stated for not-all-equal was found.

## Stop rule

Theorem L checked and refereed, one registered run of ticket B, one referee pass; report and hold.

## Runtime

Ticket A's check: about ten minutes. Ticket B: about half an hour on 8 workers (the pilot took up to 170 s a target); registered in
`docs/LONG_RUNNING.md`.
