# Where creation happens

Status: Proved (item 1); items 2–5 are exhaustive computations on the stated spaces

Ticket `HANDLE-LOCALITY-20261103-001B`, 2026-11-03.

## Question

- **Background (ticket A).** Access is local: every pinning by points of a plane piece has access, wherever the removal is.
- **The question.** Do new knots appear exactly at gluing lines on handles? Is a single handle's effect local?

## Dependencies

- **`HANDLE-LOCALITY-20261103-001A`.** Pieces, closures and the interface lemma.
- **`PLANAR-THEOREM-20261102-001B`.** The one-port 2-sum lemma.
- **`SPLICE-TREE-20261102-001C`.** Circuits and the closure (`elim_lib.py`).
- **`HANDLE-EMERGENCE-20261102-001B`.** The join lemma.

## Setting

- **The spaces.** Knot spaces built by splicing the Fano plane (a handle) into a plane knot space.
  - **At a point:** the Fano plane minus a line replaces a point of the plane space.
  - **At a line:** the plane space minus a line replaces a point of the Fano plane.
  - **Two handles:** two Fano planes, each at a point of the same plane space, the second as far from the first as possible.
- **Creation at a gluing line L after a removal M.** A new crossing knot when L is spliced into a far side. The far sides are K4^(3),
  census 6, the Fano plane and census 58.
- **Pieces.** As in ticket A. Every line belongs to the plane piece or to a handle.

## 1. The screening lemma (proved)

**Suppose that, after the removal, the three ports of the cut between a piece P and the rest R take a single antipodal pair, so that
they carry one bit. Then creation at a gluing line of P equals creation at that line on P's closure, minus the removal if it lies in P.**

*Proof.*
- **Factorization.** The solutions factor over one bit b, the ports' common class. Since the solution set is closed under complement,
  every two-point constraint is a tie. So each point of R is tied to b or free of everything outside R.
- **A crossing knot that meets R.** Split it into its part in R and the rest. Any excluded pattern restricts b to opposite values on the
  two parts. So b separates it, and the one-port 2-sum lemma (PLANAR-THEOREM B) applies: the knot is the elimination, through b's class,
  of a knot inside the near side (in the base) and a knot of P's closure spliced at L. It is new only if the second knot is.
- **Knots that miss R.** These are knots of P's closure spliced at L. ∎

**When one bit crosses.**
- **Removal in the plane piece of a handle attached at a point.** The intact handle is a knot space minus a line, so it forces its ports
  equal (ticket A, item 3).
- **Removal inside a handle attached at a line.** The plane piece is a knot space minus that line, so it forces the line's points equal.
- **The consequence.** In both cases, creation at a plane gluing line is creation on a plane knot space minus a line. By PLANAR-THEOREM,
  no one-port or pinned three-point knot is new there.

## 2. The method (checked)

- **The join lemma.** At a removal where L shows six patterns, the far side admits exactly L's six patterns, and the near side is the
  space minus M. Every set of up to k points is tested from the two sides' solution sets. No 2^n enumeration of the splice is needed.
- **Exactness.** A derivation never uses a knot larger than its target, so new knots up to k points are exact.
- **Validation.**
  - On census 6, 14, the Fano plane and census 58, spliced into K4^(3) and census 6 at every line: all 184 splices have every circuit up
    to four points equal to brute force.
  - All 56 far sides built this way equal the library splice's.

## 3. The creation map (computation, new knots up to three points)

Six near sides: one handle at a point (two seeds), one at a line (two seeds), two handles at points (two seeds). The plane parts are
10-point grown spaces. Entries are (removal, gluing line, far side) cases.

| Near sides | Gluing line on a handle | Plane line, removal on a handle | Plane line, removal in the plane piece |
| --- | --- | --- | --- |
| One handle at a point (16 points) | creates with census 6, Fano, census 58; never with K4^(3) | creates in 68 of 480 | none (320) |
| One handle at a line (16 points) | creates with census 6, Fano, census 58; with K4^(3) only when the removal is in the plane piece | **none** (224) | none (256) |
| Two handles at points (22 points) | as for one handle | creates in 144 of 960 | none (320) |

- **Neither line on a handle.** No new knot in any of the 896 cases. The screening lemma covers each of these splices.
- **A handle attached at a line** never creates outside itself, whatever the removal. With the removal inside the handle, this is the
  screening lemma.
- **A handle attached at a point** creates at plane gluing lines only when the removal opens it. Then two bits cross the cut.
- **Two handles.** Each opened handle creates near itself as a single handle would. The other, intact, handle acts as its point.

## 4. The reach of an opened handle (computation)

- **The test.** On plane pieces of 12 and 14 points, the Fano plane is attached at a point and the removal lies inside it. Distances are
  in the incidence graph.
- **The reach.** Plane gluing lines create at distance 1 (36 of 162 cases), 3 (48 of 360) and 5 (12 of 162).
- **So** the effect is not confined to the lines through the cut. In the two-handle spaces of item 3, creating plane lines also occur at
  distance 5 from the opened handle (4 cases).
- **A necessary condition (scout, not a claim).** Fix the split point's three copies on the plane piece. Every creating plane line had at
  most two patterns left (76 creating, none among the 36 lines left with three). The condition is not sufficient: 236 such cases do not
  create.

## 5. What the new knots are (computation)

- **At plane gluing lines near an opened handle.** All new knots have three points, both near points inside the handle and in the hub
  class. 1,092 of 2,496 are **not pinned**: when the two near points agree, they force the gluing line into two adjacent patterns. One far
  value rules that pair out. Brute force on the whole splice confirms examples.
- **Up to four points** (one-handle near sides, far sides K4^(3) and census 6).
  - Both prohibitions of item 3 still hold.
  - Every new knot at a plane gluing line still has three points (288).
  - Four-point new knots appear at gluing lines inside handles (2,965), with three near points.
- **So** the premise of PLANAR-COMPOSE fails on composite spaces, in two ways: unpinned three-point knots near an opened handle, and
  four-point knots inside handles. That premise was that every new knot is a pinned three-point knot through the hub. It had held on
  every census and plane near side.

## Checks

`check.py` (`result.json`, about four minutes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The join-based method | 56 far sides equal; 184 splices with all circuits up to four points equal to brute force |
| 2 | The creation map (six near sides, four far sides, up to three points) | both prohibitions hold; counts as in item 3 |
| 3 | The reach (plane pieces of 12 and 14 points) | creating plane lines at distances 1, 3 and 5 |
| 4 | Up to four points (one-handle near sides, K4^(3) and census 6) | both prohibitions hold; four-point creation only inside handles |

## What this does not establish

- **No creation without a handle.** The 896 cases are a computation. A proof would also need the residual knots of PLANAR-THEOREM C.
- **The intact handle attached at a line.** With the removal in the plane piece, two bits cross the cut, yet nothing is created. This is
  unexplained.
- **The reach.** Which plane lines an opened handle reaches, and how far, beyond the scout's necessary condition.
- **Larger knots.** Beyond four points on the creation map, and beyond three on the reach map, nothing is computed.

## Novelty

- **New here.** All of it.
- **Classical analogue.** The screening lemma is the 2-sum across a one-element separation.
