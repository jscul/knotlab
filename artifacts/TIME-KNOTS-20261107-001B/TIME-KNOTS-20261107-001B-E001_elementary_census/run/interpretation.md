# Which elementary automata bind their past in knots: interpretation

Experiment `TIME-KNOTS-20261107-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 88 rules × 6 lags in 18 s. Rows
are in `rows.json`, totals in `result.json`.

## Controls

All three pass.
- **Linear rules.** Rules 60, 90 and 150 have exactly one knot at every lag, of the size Theorem 3 gives.
- **AND and OR.** Rule 128 (AND), whose class also holds rule 254 (OR), is knot-free at every lag, with 2T + 1 ties.
- **Knot-free maps.** Every knot-free map is constant, a term or a clause (Theorem 2).

## Primary observable

The 88 rules (each class by its least member), by how their knots across time behave over T = 1 to 6:

| Behaviour | Rules | Count |
| --- | --- | --- |
| Knot-free at every lag: memory only pairwise, or none | 0, 2, 4, 8, 10, 12, 15, 32, 34, 51, 128, 136, 160, 170, 204 | 15 |
| Exactly one knot at every lag | 42, 60, 76, 90, 105, 138, 150, 200 | 8 |
| Knots at every lag, their number growing | 6, 7, 9, 11, 13, 14, 18, 22, 23, 26, 33, 35, 37, 40, 41, 43, 44, 45, 50, 54, 56, 57, 58, 73, 74, 77, 78, 94, 104, 106, 110, 122, 126, 130, 132, 134, 140, 142, 146, 152, 154, 156, 162, 164, 168, 172, 178, 184, 232 | 49 |
| Other | 1, 3, 5, 19, 24, 25, 27, 28, 29, 30, 36, 38, 46, 62, 72, 108 | 16 |

## What the classes hold

- **Pairwise memory.** The knot-free rules are the constants, the identity (204), the shifts (170 and its class), negation (51 and
  15), and rules whose future value stays a single AND of literals at every lag, such as 128, 136 and 160.
- **One knot per lag.** The linear and affine rules 60, 90, 105 and 150 have one knot, the support of p^T plus the cell. So do
  four nonlinear rules, 42, 76, 138 and 200, but their one knot always has three places, beside one tie.
- **Growing counts.**
  - **Traffic, rule 184.** At every lag its knots are exactly all C(2T + 1, T + 1) sets of T + 1 cells of the light cone: 3, 10,
    35, 126, 462 and 1,716. Every set of T + 1 past cells, set suitably, decides the future cell, and no T cells do. It is the
    fastest-growing family in the census.
  - **Majority, rule 232.** It has 2T + 1 knots, two of each size from 3 to T + 1 and three of size T + 2. Its least knot keeps
    three places at every lag.
  - **The least knot through the cell's own past.** It grows as T + 2 at every lag only for rules 43, 122, 142 and 184. For rule 30
    it is 3, 4, 5, 6, 6, 7, and for rule 110 it is 3, 4, 5, 5, 6, 7.
- **Other.**
  - **Period two.** Rules 1, 3 and 5 alternate: knot-free at odd lags, where the future value is a term or clause, and knotted at
    even lags.
  - **Not strictly growing.** Rule 30 has 2, 2, 9, 22, 36 and 100 knots. The rest of this class have counts that rise and fall
    or level off.
- **The cell's own past.** It lies in a knot at every lag for 52 rules. Eight rules have knots that never include it: 1, 5, 72,
  76, 90, 132, 140 and 200. For rule 90 the support of (X⁻¹ + X)^T never contains the cell itself.
- **Bounded knots.** For 33 rules some knot keeps three places at every lag (the least knot is 3).

## Reading against the decision rule

- **Late first knots.** Rules 1, 3 and 5 are knot-free at T = 1 and first knotted at T = 2.
- **Least knot T + 2.** The least knot through the cell's own past is T + 2 at every lag only for rules 43, 122, 142 and 184.
  Most growing rules have a slower least knot, and many keep a three-place knot (listed in `result.json`). So "T + 2 for all
  non-linear rules with knots" is not the pattern.
- **Against Wolfram's classes.** Knots across time do not follow them.
  - The linear class-3 rules 90 and 150 have the simplest knotted memory, one knot per lag.
  - The class-2 traffic rule 184 has the most knots.
  - Rule 30 (class 3) and rule 110 (class 4) sit between.

## Nonclaims

- **Lags up to 6, two-time knots only.** Knots through intermediate rows are counted only for linear rules, in ticket A.
- **Life is not here.** Its one-step knots are in ticket A, and two steps (25 cells) were not run.
