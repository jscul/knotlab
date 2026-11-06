# Opened cuts interact, and no hub-level feature decides how

Status: Proved (a finite classification: one elementary lemma, the rest by exhaustive computation)

Ticket `SPLICE-TREE-20261102-001C`, 2026-11-02.

## Question

- **From ticket B.** Knots that cross only held cuts are iterated 2-sums, so new emergence lives only across opened cuts.
- **The question.** When one removal opens several cuts, do they act separately?
- **The working hypothesis.** Opened cuts interact only where their hubs touch, that is, where the two cuts share a port.

## Dependencies

- **`SPLICE-TREE-20261102-001B`.** Through it, ticket A and HUB-GLUE A–C.
- **HUB-GLUE C's recorded counts.** Check 1(d) recomputes them.

## Setting

- **The space.** A knot space assembled along a tree of simple 3-edge cuts (`tree_lib.assemble`), with one line M removed so that two
  or more cuts open.
- **Ties and classes.**
  - Two points are tied when they form a two-element circuit.
  - A knot (a circuit of three or more points) never holds two tied points, since the tie would be a smaller constrained subset.
  - So replacing each point by its tie class keeps a knot's size.
- **Generation.** A knot is generated from a base when repeated eliminations produce it. An elimination takes A ∪ B minus one tie class
  shared by A and B, and is kept when the result is again a knot.
- **Four classes.** A knot that crosses k ≥ 1 opened cuts is one of these:
  - **generated from knots crossing none**;
  - **new at one cut**: k = 1 and not generated from knots crossing no opened cut;
  - **carried**: k ≥ 2, generated from knots crossing fewer opened cuts but not from knots crossing none;
  - **joint**: k ≥ 2 and not generated even from knots crossing fewer opened cuts.

## Lemma (derivations never grow)

- **Statement.** If an elimination produces T from A and B, then A and B are no larger than T.
- **Consequence.** A closure computed with knots up to b points decides generation exactly for every knot of at most b points.

*Proof.*
- **Bounding A.** T = (A ∪ B) − h with h ∈ A ∩ B and h ∉ T, so A ∪ B = T ∪ {h} and A ⊆ T ∪ {h}.
- **Ruling out the top size.** If |A| = |T| + 1, then A = T ∪ {h}. A would then properly contain a tie-variant of T, which is
  constrained, so A would not be minimal.
- **So.** |A| ≤ |T|, and likewise |B| ≤ |T|.
- **Every step.** By induction, every knot in a derivation of T is no larger than T. ∎

*A correction.* While scouting this epic I had assumed that "not generated" findings under a size bound could be artifacts of the bound.
They are not: by the lemma they are exact within the bound.

## Results

1. **The hypothesis fails both ways.**
   - K4 > Fano > K4 with disjoint hubs carries new knots across its second opened cut (6 carried knots).
   - K4 > K4 > K4 with touching hubs has no knot crossing both opened cuts that is not generated from knots crossing none.
2. **No hub-level feature decides interaction.**
   - The sample is 96 chains of three and four K4^(3) and Fano pieces, with all circuits computed. They cover every second splice line of
     the three-piece chains and selected lines of four-piece chains, 10 to 19 points, and 642 removals that open two or more cuts.
   - Carried knots occur where the opened cuts' hubs are disjoint (288) as well as where they touch (1936).
   - Joint knots occur in every one of these settings:

     | Setting | Joint knots |
     | --- | --- |
     | Disjoint hubs | 368 |
     | Touching hubs | 758 |
     | Removed line through a port shared by two opened cuts | 462 |
     | Removed line missing every shared port | 664 |
     | Through the removed line's hub | 836 |
     | Off the removed line's hub | 290 |

3. **Two regularities hold on all 96 chains.**
   - Every joint knot has three or four points: 940 have three and 186 have four.
   - The 20 chains of K4^(3) pieces alone have no new, carried or joint knot.
4. **A predecessor count stands.** The closure up to tie classes reproduces HUB-GLUE C's count at an opened hub: 72 of the 762 crossing
   knots of the 13-point Fano splice are not generated. HUB-GLUE C computed that count with one representative per class.
5. **Example: corners at a shared port.** Take touching hubs and remove either line through the shared port p.
   - **The corners.** The port's two remaining lines (one on the near side, its slot line beyond the second cut) give 12 corner circuits.
     A corner takes one point of the removed line, one point of the near-side line and one point of the slot line.
   - **Fano far end** (Fano > K4 > Fano, Fano > Fano > Fano): the corners are exactly the joint knots.
   - **K4^(3) far end** (Fano > K4 > K4, Fano > Fano > K4): knots crossing fewer cuts generate the same corners.

## Proof

- **The lemma.** Proved above.
- **Items 1–5.** Exhaustive computation in `check.py`, whose results are in `result.json`.
  - **Circuits.** Every circuit of every removal is computed by the bitmask routine in `elim_lib.py`. Check 1(a) confirms it equals
    `glue_lib.circuits` (29 removals).
  - **Generation.** It is decided by a per-target fixed point, which uses the lemma's shape: T joins when two members inside T ∪ {h},
    both through h, cover T ∪ {h}.
  - **Cross-checks.** Check 1(b) compares the fixed point with forward elimination over every pair (24 closures). Check 1(c) compares
    a closure bounded at 5 points with the full closure on the 19-point Fano chain (12 closures). ∎

## What joint emergence looks like

- **The space.** Fano > K4 > Fano with touching hubs: the second splice uses a line of the K4 through its removed point, so the K4's
  slot line holds port 1 of the first cut, and port 1 becomes a port of both cuts.
- **The removal.** Removing the line (4, 6, 1) through port 1 ties 4, 6 and 1 into the leftover hub.
- **Port 1's other lines.** (0, 1, 3) on the near side and (10, 12, 1) beyond the second cut.
- **The joint knots.** {x, a, c} with x ∈ {1, 4, 6}, a ∈ {0, 3} and c ∈ {10, 12}. Each misses exactly the two patterns 000 and 111
  (in the printed coordinates). They are new three-point constraints reaching from the first Fano to the last.
- **No shared port needed.** Fano > K4 > K4 with disjoint hubs has 36 joint three-point knots, and none of its cuts shares a port.

## Checks

`check.py` (`result.json`, about three minutes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Method: circuits, closure, size lemma, HUB-GLUE C recount | 29/29, 24/24, 12/12 equal; 384 / 690 / 72 reproduced |
| 2 | The hypothesis as first posed | 6 carried knots with disjoint hubs; touching hubs with no interaction |
| 3 | 96 chains | carried and joint knots in every hub-level setting (table above) |
| 4 | Regularities | joint knots of 3 or 4 points only; K4^(3)-only chains create nothing |
| 5 | Corners at a shared port | joint with a Fano far end, generated with a K4^(3) far end |

## History

- **The first design.** The check tested the touching-hub hypothesis directly.
- **The failure.** Its first run found 6 carried knots in K4 > Fano > K4 with disjoint hubs, against the hypothesis.
- **The repair.** That run also showed that the closure used so far eliminated one shared point between class representatives rather
  than a shared tie class. It was replaced by elimination over tie classes, and every count stayed the same (check 1(d) for HUB-GLUE C;
  the scouts for all nine first families).
- **Two refined rules, both refuted.**
  - Joint knots need a shared port on the removed line: Fano > K4 > K4 with disjoint hubs has 36 joint knots.
  - Joint knots pass through the removed line's hub: 290 are off it.

## What this does not establish

- **No rule.** There is no rule for when opened cuts interact, only the refutation of three hub-level rules.
- **Size.** Whether joint knots stay at three or four points beyond these chains.
- **K4^(3) chains.** Why chains of K4^(3) pieces create no new emergence.
- **Trees beyond chains.** Stars whose centre gives the lines are not covered: `tree_lib.assemble` records each cut's point side as the
  assembly at the time of the splice, which is correct for chains and for stars whose leaves give the lines.
- **Non-simple cuts and other pieces.** Not covered.

## Novelty

- **New here.** The classification.
- **Elementary.** The size lemma.
