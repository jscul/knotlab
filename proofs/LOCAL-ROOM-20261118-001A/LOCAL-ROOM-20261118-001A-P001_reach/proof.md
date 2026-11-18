# Reach limits cannot hold two orders

Status: Proved

Ticket `LOCAL-ROOM-20261118-001A`, 18 November 2026, by Claude. Epic `LOCAL-ROOM-20261118-001`. Words as in
`CUBE-DOUBLING-20261118-001A`:
- orientations, the differing set A(x), and the certificate rules L2:
  - a middle knot B(u, p, v) is consistent iff A(u) ∩ A(v) = ∅;
  - an end knot B(u, v, p) is consistent iff A(v) ⊆ A(u);
  - a zero-cost fill needs a middle knot, since only middle knots cover the constants.
- **The reach limit r.** Every knot's two old distinctions lie within r splits of each other: their disagreement count is at most
  2r. This is read from the states alone.
- **LF3(r).** The cheapest rule under that limit.

## Statements

- **R1. Within one split there is never a free fill.** Under r = 1 no zero-cost admitted extension exists, on any base. So LF3(1)
  never fills.
- **R2. Within two splits the cheapest growth still reaches the cube at every doubling.** From one knot, LF3(r) for r ≥ 2 reaches
  Q_d at n = 2^d for every d ≥ 2, in every run.
- **R3. A reach limit cannot tell a grid's fill from a line's.**
  - Any limit that allows the fill completing a cell of a two-way grid (r ≥ 2) also allows the fill F(a, c, b) on three consecutive
    distinctions of a line.
  - That fill makes a second order from a line (`STATE-RULES-20261117-001A`, S4). On a base with two orders, it is the step that
    crosses a row split with the next one in the same row: the twisted corner of `CUBE-DOUBLING-20261118-001A`, L5.
  - So no reach limit read from the states keeps exactly two orders while still filling cells.

## Proofs

**R1.**
- A zero-cost fill needs a consistent middle knot B(u, p, v). Under r = 1, u and v differ on exactly one split t, so
  A(u) Δ A(v) = {t}.
- Consistency needs A(u) ∩ A(v) = ∅, so A(u) ∪ A(v) = {t}. Hence one of A(u), A(v) is empty.
- So the target is the orientation of u or v, a copy, which is not admitted. ∎

**R2.** Follow `CUBE-DOUBLING-20261118-001A` with every certificate checked for reach.
- **From Q_s, the cheapest step.** It is a subdivision, by one knot on an adjacent pair (reach 1). A pendant needs B(v̄, v, p) at
  reach s, so for s ≥ 3 only subdivisions are allowed. At s = 2 both kinds are.
- **After a subdivision** (splits a, b and w, new point (1, 0, w₀)):
  - **The targets (1, 0, w).** The middle knot B((0,0,w), p, (1,1,w)) has reach 2. The end knots B((0,0,w₀), (1,0,w₀), p) and
    B((1,1,w₀), (1,0,w₀), p) have reach 1. So every (1, 0, w) is forceable.
  - **The targets (0, 1, w), once (1, 0, w) is present.** The middle knot B((0,0,w), p, (1,1,w)) has reach 2. The end knots
    B((1,0,w), (0,0,w), p) and B((1,0,w), (1,1,w), p) have reach 1. Consistency: A((0,0,w)) = {b} ⊆ {a, b} = A((1,0,w)), and
    likewise with a.
  - By L3 the (1, 0, ·) layer fills first or interleaved; either way every orientation becomes forceable, and the cube fills.
- **After a pendant at s = 2** (Q₂ plus p copying c, trivial split t):
  - the targets (x, 1) with x adjacent to c are certified by `CUBE-DOUBLING-20261118-001A`'s pendant certificate, whose pairs have
    reach at most 2;
  - the last, x = c̄, by the same certificate with c replaced by a filled neighbour (x′, 1) of c̄. Its middle pair (x′, 1)–(c̄, 0)
    has reach 2.
- The rest is the doubling induction. ∎

**R3.**
- In a two-way grid the fill of a cell with corner c and neighbours a, b (`GRID-GROW-20261117-001A`, G3) uses pairs (a, b) at
  reach 2 and (c, a), (c, b) at reach 1.
- On three consecutive distinctions a, c, b of a line, the fill F(a, c, b) uses the same reaches.
- A limit read from the states sees only the disagreement counts of the pairs used, so it allows both or neither. ∎

## Provenance

Local; builds on `CUBE-DOUBLING-20261118-001A` and `STATE-RULES-20261117-001A`. The advisor gave R3's point that a grid's corner and
a line's three points are both three points of a square, and the bootstrap reading of R2.
