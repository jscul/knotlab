# One-sided grid Sperner is PPADS-hard in the decision-tree world

Status: Proved by hand. The construction is checked exhaustively on 3 nodes and on random instances, with a locality check and
negative controls (`check.py`).

Ticket `COUNT-TFNP-20261107-001A`, 2026-11-07.

## Standard statement

**SINK** (Beame–Cook–Edmonds–Impagliazzo–Pitassi): nodes 0, …, N − 1 carry successor and predecessor pointers. The edge u → v is present
when succ(u) = v and pred(v) = u. Find a sink v ≠ 0 (an in-edge and no out-edge), or output 0 if 0 is not a source.

**One-sided Sperner_m:**
- **The grid.** The side-m triangular grid, with the fixed boundary: corners coloured 0, 1, 2, and each side taking its far corner's
  colour after its first vertex.
- **The search.** Given colours for the interior vertices, find a small triangle whose colours read 0, 1, 2 counterclockwise.
- **Two-sided version.** Any fully labelled triangle counts.

**Theorem.** SINK on N nodes reduces to one-sided Sperner_m with m = O(N²):
- every vertex's colour is a function of O(1) pointers;
- the answer recovered from a solution is too;
- so both are computed by decision trees of depth O(log N).

Consequences:
- One-sided 2D grid Sperner is complete for PPADS^dt under decision-tree reductions.
- The same construction reduces SOURCE.OR.SINK to two-sided Sperner_m, so two-sided grid Sperner is complete for PPAD^dt.

## Nearest known result

- **Beame–Cook–Edmonds–Impagliazzo–Pitassi**, *The relative complexity of NP search problems* (JCSS 57, 1998):
  - PPADS is the class reducible to SINK;
  - "positive Sperner's lemma (for dimensions three and above)" is PPADS-complete;
  - PPADS ⊄ PPA relative to a generic oracle (§3.3).
- **Friedl–Ivanyos–Santha–Verhoeven**, *Locally 2-dimensional Sperner problems complete for the polynomial parity argument classes*
  (CIAC 2006): Sperner problems complete for PPAD, PPADS and PPA on surfaces of non-zero genus. The handles avoid crossings.
- **Chen–Deng**, *On the complexity of 2D discrete fixed point problem* (ICALP 2006; TCS 2009): 2D Sperner is PPAD-complete. They embed
  END-OF-LINE in a planar grid and resolve each crossing by re-pairing its arms (exposition: Mehrabian 2011, "RLEAFD").
- **Classification.** known-with-delta.
  - **The delta.** The planar one-sided case. Chen–Deng's re-pairing keeps every in- and out-degree, so it keeps sinks, sources and
    orientations. Here it is written in the decision-tree model with the boundary that `FLAT-STATES-20261107-001B`'s reduction to the
    knot sphere uses.
  - **Folklore risk.** High for the idea, which an expert would see at once. Its value here is as the lemma that
    `COUNT-TFNP-20261107-001B` needs.

## Construction

**Normalization.**
- Drop node 0's in-edges. Call the drawn graph G′.
- 0 is fed by the boundary's door instead, so the sinks and non-standard sources of G′ map to SINK answers (Lemma 4).

**Layout** (scale S = 4, turn radius r = 4, margins X0 = 4, Y0 = 12).
- Node j's port is P_j = (X0, Y0 + 6Sj), in grid coordinates (a, b).
- The potential edge i → j runs:
  - east from P_i along its row to the column c(i, j) = X0 + 3S(Ni + j + 1);
  - north or south to the row of P_j plus 3S;
  - west to a = X0;
  - south to P_j.
- The standard source's path enters from the door. It runs west along the bottom row from (m − 1, 0), north along a = X0 to P_0, and
  continues as node 0's out-edge.
- The grid side is m = X0 + 3S(N² + 1) + Y0 + 6SN + 3S + 8 = O(N²).

**Present runs.**
- At most one present edge leaves each port and at most one enters it.
- So the drawn runs of present edges overlap nowhere: each edge has its own column, and each node owns two rows.
- They meet only where a vertical run of one edge crosses a horizontal run of another.

**Uncrossing.** At a crossing X of a horizontal run with direction d_h and a vertical run with direction d_v:
- remove both runs within distance less than r of X;
- send the horizontal incoming arm from X − r·d_h through the quadrant (−d_h, +d_v) to X + r·d_v;
- send the vertical incoming arm from X − r·d_v through the quadrant (+d_h, −d_v) to X + r·d_h.

**Tubes.**
- **Lane 1.** The points of the drawn paths get colour 1.
- **Lane 2.** Colour 2 goes to their right-hand neighbours: p + R(d) for the incoming and outgoing directions d at p, plus the outer
  corner p + R(d_in) + R(d_out) at a left turn, minus lane 1.
- **The rest.** Interior vertices off both lanes get 0, and the boundary keeps its fixed colours.

## Lemmas

**Lemma 1 (uncrossing keeps degrees).** After uncrossing, the drawn curves are pairwise disjoint and every port keeps its in- and
out-degree. A curve's ends are exactly the ports of G′'s sinks (where it ends) and non-standard sources (where it starts). The door
feeds node 0.

*Proof.*
- **Degrees.** At a crossing, each incoming arm continues into exactly one outgoing arm, so degrees are unchanged.
- **Disjointness.** The two detours lie in opposite quadrants. In the triangular lattice the quadrants (−1, +1) and (+1, −1) are joined
  by a lattice direction, and the detours' starting points are then r = 4 steps apart. That still leaves a free vertex between the
  lanes.
- **Ends.** Away from crossings the curves are the present runs, which overlap nowhere. ∎

**Lemma 2 (tubes).** Every fully labelled triangle lies at a curve's end:
- colours 0, 1, 2 counterclockwise at a sink's port;
- the reverse at a non-standard source's port;
- none at the door.

*Proof.*
- **Locality.** A triangle's colours are decided by the drawing within distance r + 2 of it. Every such local picture is a translate
  of one of finitely many:
  - a straight run in one of four directions;
  - a left or right turn;
  - one of three crossing gadgets: a horizontal run east against a vertical run north, or west against north or south. East against
    south cannot occur: node i′'s out-run crosses the column of an edge i → j with j < i only if j < i′ < i, but reaches that column
    only if i′ ≥ i;
  - a port that is isolated, a sink, a source or a through node;
  - the door, where lane 1 is the bottom row, coloured 1, and lane 2 meets the hypotenuse, coloured 2.
- **Away from ends.** Along runs and turns a triangle meets at most two of the colours. Background 0 touches lane 1 on the left and
  lane 2 on the right, never both in one triangle, because lane 2 is continuous: the outer corner is filled at left turns.
- **At an end.** The end triangle meets 0 ahead, lane 1 on the left and lane 2 on the right. That is 0, 1, 2 counterclockwise at a
  sink, and reversing the direction swaps left and right at a source.
- **Decided by computation.** Checks 1 and 2 contain every local picture: all three crossing types and all four port types occur.
  Every triangle of every instance is tested, so the claim is decided exactly for each picture. ∎

**Lemma 3 (shallow).** Each vertex's colour is a function of O(1) pointers, read with O(log N) queries.
- A vertex on node i's row needs succ(i) and pred(succ(i)).
- A vertex on node j's in-row needs pred(j) and succ(pred(j)).
- A vertex on column c(i, j) needs succ(i) and pred(j).
- A vertex in a crossing gadget needs the pointers of the two edges crossing there.

Check 3 confirms it: when one pointer changes, every vertex whose colour changes lies within distance r + 2 of an edge whose presence
changed. ∎

**Lemma 4 (answers).** A positive triangle at port j maps back to j when j is a sink of the input graph G, and to 0 otherwise.
- **0 itself.** If j = 0, then 0 has no out-edge, so 0 is not a source.
- **Any other j.** j's out-edge was the dropped edge into 0, so 0 has an in-edge and is not a source.

Either way the answer is a SINK solution. ∎

**Proof of the theorem.**
- **Hardness.** Lemmas 1–4 give the reduction, of depth O(log N) into an instance with O(N⁴) vertices.
- **Membership.** One-sided Sperner is in PPADS^dt, by following doors from the boundary: the path from the door ends at a positive
  triangle (Papadimitriou). So it is PPADS^dt-complete.
- **The two-sided version.** For SOURCE.OR.SINK (PPAD) the same instance's fully labelled triangles of either orientation are exactly
  the sinks and non-standard sources. So two-sided grid Sperner is PPAD^dt-complete. ∎

## Checks

`check.py` (`result.json`), about 5 minutes:

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Every pointer structure on 3 nodes, each also with one pointer changed (520 instances, 78 crossings) | fully labelled triangles exactly at the ports of sinks (positive) and non-standard sources (negative); no boundary clash; every positive triangle maps back to a SINK solution |
| 2 | 36 random instances on 4–7 nodes (132 crossings) | the same; all three possible crossing types and all four port types occur; m ≈ 16–21·N² |
| 3 | Locality: one pointer changed, 10 instance pairs | every changed vertex lies within r + 2 of an edge whose presence changed |
| 4 | Controls | dropping the uncrossing, turn radius 2, and mirrored lanes are each rejected |

## What this does not establish

- **Circuit version.** The white-box (circuit) version is not written out, although the same construction applies.
- **Constants.** The scale and grid size (S = 4, m ≈ 20N²) are not optimized.
- **The sphere.** Nothing here concerns the knot sphere; that is `COUNT-TFNP-20261107-001B`.
