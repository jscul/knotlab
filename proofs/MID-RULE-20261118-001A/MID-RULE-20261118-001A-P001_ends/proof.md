# A crossing needs two end knots

Status: Proved

Ticket `MID-RULE-20261118-001A`, 18 November 2026, by Claude. Epic `MID-RULE-20261118-001`. Written before the run.

## Words

As in `KEEP-READ-20261118-001A`, `KNOT-SWITCH-20261118-001A` and `PICK-TWO-20261118-001A`.
- **Certificate.** A fill's certificate is a set of at most three knots on the new distinction r and old pairs that forces r on
  every state.
- **Middle and end knots.** A **middle knot** B(u, r, v) pins r to u where u = v. An **end knot** B(u, v, r) pins r to v where
  u ≠ v.
- **The rules.**
  - MID2 takes any fill while nothing crosses. Afterwards it takes only fills with a certificate of two or more middle knots.
    Else it subdivides.
  - ONE is the same with "at most one end knot".
  - ANY takes any fill (the control).
  - Each has a knot-local form (KF3's moves) and a free form (any old pairs).

## Statements

- **E1. A new crossing needs two end knots.** If a fill makes two old splits cross, then in every certificate the two states that
  realise the newly occupied quadrant are pinned by two different end knots.
- **E2. At most one end knot keeps everything.** A fill with a certificate of at most one end knot makes no new crossing. It changes
  no relation of splits, so k and λ are unchanged, on any base of betweenness knots. MID2's certificates have at most one end knot.
- **E3. From a line, MID2 and ONE keep two orders forever.** Their first fill makes exactly two (`PICK-TWO-20261118-001A`, S6). After
  it, each fill keeps every relation (E2), and so does each subdivision. Nothing in either rule names a number of orders; after the
  switch, both read only the move's knots.
- **E4. From a full two-way grid, the free forms refill every new row.** At a full grid no fill has a certificate with at most one
  end knot, so they subdivide. After the subdivision, each empty cell of the new row is the median of the new distinction and its
  two old neighbours, forced by three middle knots. So the free forms pass through a full grid after every new row or column
  forever, from the 2 × 2 pattern.
- **E5. From a line, the free forms reach a full grid exactly when the first fill spans the line.** A split that crosses nothing
  never comes to cross under them (E2). If the first fill's ends are the line's two ends, every split crosses. Every empty cell is
  then the median of the fill's cell and two cells of the line, and E4 takes over. Otherwise an uncrossed split stays, and no full
  grid occurs. A uniform first fill spans the line with chance 6 / (n (n − 1)).

## Proofs

**E1.**
- *Copy principle.* Each knot makes r copy one old distinction on the states it pins: u for a middle knot, v for an end knot.
- *Same knot.* Let t₁ and t₂ come to cross. Then r takes, on the two states T₁ and T₂ (of t₁ and t₂) that realise the new
  quadrant, a pair of values that no old distinction takes. If one knot pinned both states, r would copy one old distinction on
  both, and that distinction would take the same pair. So two different knots pin them.
- *Neither is a middle knot.* Suppose a middle knot on (x, y) pins T₁, so x = y = r there. Then x and y lie on r's side of t₁. The
  quadrant is empty of old distinctions, so x and y are on the other side of t₂ from r. Hence x = y there too, and the knot pins r
  to x's value on T₂, which is not r's. The same holds with t₁ and t₂ exchanged.
- So both pins come from end knots, and they are different. ∎

**E2.** By E1, a new crossing needs two end knots in every certificate. A certificate with at most one end knot makes none.
- Without a new crossing no empty quadrant of any pair of splits is filled, so no relation changes.
- k depends only on crossings, and λ only on the relations (`PICK-TWO-20261118-001A`, S2).
- Two middle knots among at most three leave at most one end knot. ∎

**E3.**
- *The first fill.* It makes λ = k = 2 (S6).
- *After it.* Fills are E2's, and subdivisions keep every relation (`NEVER-NEST-20261118-001A`, N1).
- *What the rules read.* The switch is the first filled knot (`KNOT-SWITCH-20261118-001A`, W3). The fill test reads only the move's
  knots. ∎

**E4.**
- *At a full grid.* Every fill makes two splits of one order cross (N3 (i)), a new crossing, so by E2 it has no certificate with
  at most one end knot.
- *After a subdivision.* The new row's empty cells are medians of p and two old cells (N3 (iii)), forced by the three middle knots
  on their pairs, which are any old pairs in the free forms.
- *Repeat.* The base returns to a full grid (N3), and the argument repeats. ∎

**E5.**
- *Uncrossed splits stay uncrossed.* No phase-two fill makes a crossing (E2), and subdivisions make none (N1). So a split that
  crosses nothing after the first fill crosses nothing forever, and no full grid (whose crossing graph is complete bipartite) can
  occur.
- *A spanning first fill.* Let it have ends 0 and m and middle c. Its cell is the far corner of the grid of the two chains, whose
  first side is the line's first c steps and whose second side is the rest. Every empty cell (i, j) is the coordinatewise median
  of that corner, the line's cell (i, 0) on the first side, and the line's cell (c, j) on the second. So it is a fill with three
  middle knots, and the grid fills; then E4 applies.
- *The chance.* There are n − 2 triples with ends 0 and m among the C(n, 3) triples. ∎

## What this leaves to the computation

The knot-local forms. After a subdivision the new distinction shares knots only with its two neighbours, so the median certificate
is not knot-local. Do MID2K and ONEK starve? The advisor predicts that they fill about once per run.

## Provenance

Local; builds on `PICK-TWO-20261118-001A`, `NEVER-NEST-20261118-001A`, `KNOT-SWITCH-20261118-001A` and `KEEP-READ-20261118-001A`. The
advisor, consulted before the freeze, gave E1's copy principle and its strengthening from "two middles" to "at most one end knot",
E5's count and the controls.
