# Accretion needs a named face

Status: Proved

Ticket `GROW-FACE-20261110-001A`, 2026-11-10, the board line's deciding epic. Pre-registered in commit 9df96cd7f before any
computation; the three targets were sketched by hand while the registration was written (disclosed there). Revised after an
independent review, before publication (decision note, "Review"):
- G1 is narrowed. Each component is the seed's with trees attached, of asymptotic dimension at most 1, where the target said "a
  tree" and "nothing of dimension two".
- G2′, the spiral without its arrow, is added.
- G3 is fixed, and it now covers every fixed priority, so that it is a law in the frozen sense of one action per view. Its heading is
  narrowed from "no marker" to the one law it is about.
- The pre-registration's decision is corrected in `docs/CORRECTIONS.md`.

## Setting (frozen)

- **Accretion laws.** Over abstract names (`BARE-NAMES-20261110-001A`): a board grows from a finite seed. A step picks a site and
  applies the law's action for the site's radius-r view (its graph and values, with no names): add one new place with a value, joined
  to the site and possibly to places of the view, or join the site to a place of the view. Values come from a finite alphabet. Places
  are never removed or merged.
- **Orders.** A growth order is fair when every action that stays enabled is eventually taken. A result belongs to the law only if it
  holds in every fair order (`GROWTH-LAW-20261107-001`). The limit of an order is the union of its boards.
- **Naming a face.** An action names a face when it closes a cycle: it joins a new place to two or more existing places, or joins two
  existing places. Such a cycle runs through the view, so its length is at most 2r + 2, and the view fixes it.
- **Forcing the plane.** A law forces the plane when every fair order's limit is the square grid of Z².

**What the definition decides.** Read as frozen, an action that names no face adds a leaf, so G1 follows from the definition. The
escape the pre-registration described, growth forcing the plane without a named face, could not exist, and the registration should
have said so. The content of the ticket is in G2, G2′ and G3: which laws that do name faces force the plane.

## G1. No named face, no plane

**Statement.** If no action of an accretion law names a face, then in every limit each component is a component of the seed with
trees attached. It has only the seed's finitely many cycles, it is quasi-isometric to a tree, and so its asymptotic dimension is at
most 1 and it is not quasi-isometric to the square grid. It can still grow quadratically: see the comb below.

**Proof.** An action that names no face adds one new place joined to one existing place, the site. That keeps every component's
cycles and adds no component, so every cycle of every board, and of the limit, lies in the seed, and each component of the limit
contains exactly one component of the seed. A connected graph with finitely many cycles is a finite graph with trees attached,
which is quasi-isometric to a tree. Trees have asymptotic dimension at most 1 and the square grid has 2, which quasi-isometries
keep. ∎

**The comb.** Growth without faces can have quadratic volume growth. Take radius 1, values R, A and B, and a seed of one R place:
- R adds an A leaf if it has no A neighbour, and a B leaf if it has no B neighbour;
- A adds an A leaf while exactly one of its neighbours is A or R, and a B leaf if it has no B neighbour;
- B adds a B leaf while it has one neighbour.

Every fair order grows the comb: a ray of A places from R, with a ray of B places hanging from R and from each A. Its balls have
about n²/2 places, but it is a tree. (Found by the referee.)

So the frozen escape, growth forcing the plane without a named face, does not exist. Every way for growth to close a cycle names it,
because a local action can reach only places of its view.

## G2. A named face and an arrow grow the plane

**Statement.** The following radius-2 law has exactly one enabled action at every step, and its only order grows the square grid:
after its k-th full turn the board is the (2k + 1) × (2k + 1) block of Z², with every grid edge between its places.
- **Values.** A coordinate mod 3 and an arrow, one of the four unit offsets.
- **Seed.** One place, coordinate (0, 0), arrow e₁.
- **The action.** A place is enabled when it has no neighbour at the offset of its arrow a. Its action adds a place there, joined to it
  and to q, the neighbour at offset a of its own neighbour at offset left(a), when q exists. That join closes a square: the law names
  the face. The new place keeps the arrow a if it got q, and turns to left(a) otherwise.

**Proof.** This is the square spiral, which turns left whenever the cell on its left is empty.
- **The spiral.** The spiral visits every cell of Z² once, in rings, and after (2k + 1)² cells it has visited the block [−k, k]².
- **One enabled place.** Every place except the last has its successor, which it added itself at the offset of its arrow. So only the
  last place, the head, is enabled, and the cell its action fills is empty, since the spiral visits each cell once.
- **Every edge.** When a cell is added, its earlier neighbours are its predecessor and, if already placed, its left cell, which is
  then q. The cell ahead of it and the cell on its right lie further along the spiral. The action joins both earlier neighbours, so
  every grid edge is joined when its later end is added. ∎

## G2′. The arrow is not needed

**Statement.** Let the values be coordinates mod 3 only, with radius 2.
- **Enabled.** A site is enabled when its radius-2 view is one of the 77 views the spiral's head has (listed in `result.json`).
- **The action.** It adds a place at the arrow read from its radius-1 view: e₁ with no neighbour, right(f) with one neighbour at
  offset f, and −f with two neighbours at f and right(f). The new place is joined to the site and to q as in G2.

Exactly one action is enabled at every step, and the law's only order grows the square spiral, so the law forces the plane. Its
values are those of SQ_r below. At radius 1 the construction fails: 13 of the head's views are also views of other places.

**Proof.** By induction on the steps the board is a prefix of the spiral with every grid edge, as in G2.
- **The head.** By G2's proof, the head's neighbours are its predecessor and, if placed, its left cell q. One neighbour at f means the
  spiral is turning: the predecessor is at f = −a′ for the previous arrow a′, and the new arrow is left(a′) = right(f). Two neighbours
  are at f = −a and right(f) = left(a), so the arrow is −f. The action is therefore G2's step.
- **The others.** It remains to show that no other place's view is ever one of the head's views. Lemma S below shows that every view
  that occurs, together with whether its place is the head, already occurs with the head on a ring below 20. `check.py` lists all
  views to ring 40: the head's 77 views and the other places' 366 never coincide. ∎

**Lemma S (the spiral's views repeat every three rings).** Number the cells of the spiral by ring and position. Ring m ≥ 1 is the
set of cells of max-norm m. It is entered at (m, 1 − m), which is position 0, and run north, west, south and east to (m, −m), which
is position 8m − 1. Cells come in the order of (ring, position), compared lexicographically. Then for every step whose head lies
on a ring m ≥ 20, every radius-2 view at that step, with its headness, also occurs at a step whose head lies on ring m − 3.

**Proof.**
- **What a view depends on.** The board is a prefix of the spiral with every grid edge. So the view of a place v, together with
  whether v is the head, depends only on v mod 3, on whether v is the head, and on which cells of its diamond (the 13 cells within
  grid distance 2) are placed.
  - If the whole diamond is placed, the view is the interior view of v's value. It occurs at every step with the head on ring 4 or
    beyond, for all nine values.
  - Otherwise some cell of the diamond is unplaced, so it lies on ring m or beyond, and v lies within 2 of ring m. Cells on rings
    below m are placed and cells beyond m are not. A cell of ring m is placed when its position is at most the head's.
- **Bringing the head near.** Suppose v is not the head and the head is more than 3 from v. Move the head along ring m to the cell
  just after the last cell of v's diamond that precedes it on ring m, or, if none precedes it, to the cell just before the first
  one. The same cells of the diamond are placed, v is still not the head, and the head is now next to the diamond, within 3 of v.
- **Zones and their translations.** Near ring m (within max-norm distance 4), take eight zones: four corner zones, where both
  coordinates are within 16 of the corner's, and four side zones, at least 9 from both corners along the side. Any set of grid
  diameter at most 5 near ring m lies in one zone.
  - Each zone has a translation τ toward the origin: three times the diagonal for a corner zone, three times the inward normal for a
    side zone. Since τ lies in 3Z², it keeps values mod 3.
  - τ keeps every cell of the zone on the same side of a ring exactly three lower.
  - Along one side it lowers every position by the same amount: 3 along the east side, 6 at the north-east corner, and so on up to
    21 along the south side.
  - At a corner the two sides keep their order, because on each ring the earlier side stays earlier.
  - At the south-east corner a ring ends and the next begins. There the east side's positions are unchanged and the south side's drop
    by 24, and on each ring the east side's cells, near position 0, still come before the south side's, near the ring's end.
  - So τ keeps the spiral order of the zone's cells.
- **Moving a view three rings in.** With the head within 3 of v, take a zone holding v's diamond and the head, and translate both by
  τ. The new head lies on ring m − 3, the same cells of the diamond are placed, and v − τ is the head exactly when v is. It has v's
  value mod 3, so it has v's view.
- **Conclusion.** By induction on m, every view occurs with the head on a ring below 20. ∎

`check.py` finds more than the lemma needs. No new kind of view appears after ring 6, and from ring 7 on, the views at ring m are
exactly those at ring m − 3.

**What replaces the arrow.** The head is the only place whose view looks like a head's. The coordinates mod 3 make this readable.
- **At radius 1.** In 12 of the 13 clashes a head going straight, with its predecessor behind and its left cell beside it, looks like a
  ring corner the spiral has passed. The thirteenth is a turning head against the seed after the first step.
- **Without the residues.** The shapes alone clash at radii 2 and 3, four times at each (the referee's run).

## G3. Growing everywhere at once, an order splits the square-closing law

**The law SQ_r.** Values are coordinates mod 3, so every edge has a unit offset. A place has at most one neighbour at each offset.
- **Reading the view.** The view is read breadth first, each place's neighbours taken in the fixed order e₁, −e₁, e₂, −e₂. A place's
  grid displacement from the site is the sum of offsets along that path. "The first" place with a property means the first in this
  order: by distance, then by the offsets along the path. All of this is read from values and uses no names.
- **One action per view.** The law fixes a priority P, an order of the four offsets. A site acts at the first offset d of P at which
  it has no neighbour:
  - if a place of its view sits at grid displacement d and has no neighbour at offset −d, it joins the first such place;
  - otherwise it adds a new place at d, joined to the site and, for each of the new place's other three offsets, to the first place
    of the view at that grid position that lacks the matching neighbour.
- **What it closes.** These joins close every square the view shows.

**Statement.** For every radius r ≥ 2 and every priority P, SQ_r has a fair order whose limit is not the square grid. For r ≤ 1, SQ_r
names no face, since a radius-1 view shows no place at displacement d (that would be the missing neighbour) or at any displacement
of length 2, so G1 applies.

**Proof.** Write the order in the frame where P's first offset points north. Every join it makes has exactly one candidate in the
view, so the fixed reading order never decides, and the order is the same for every P up to that frame. Every step below is the
acting site's action under the law. Actions taken on the way, at offsets of P that come before the one wanted, only add places west
of x = −1, east of x = 1 or below y = 0. Positions are written for bookkeeping; the law never sees them.
1. **The base.**
   - The seed sits at (−1, 0). It acts until it has its neighbours at north (−1, 1), east (0, 0) and south (−1, −1).
   - Then (−1, −1) acts until it has an east neighbour. That neighbour, (0, −1), is joined to (0, 0), which is visible at
     displacement (1, 1).
   - Then (0, −1) acts until it has an east neighbour, (1, −1).
   - Then (1, −1) acts at its first offset, north, and adds (1, 0). It is joined to (0, 0), visible at displacement (−1, 1).
   - Now (0, 0) lacks only its north neighbour, and its action there is delayed.
2. **Two arms.** The columns x = −1 and x = 1 grow north to height H + 1, with H > r. North is every place's first offset.
3. **The slit, filled from the top.** For y = H, H − 1, …, 1, first (−1, y) acts until it has an east neighbour, then (1, y) until it
   has a west neighbour.
   - **Outer columns.** When P puts a side's outer offset before its slit side, that side first adds its outer neighbour, so a column
     grows outside.
   - **Heights y ≥ 2.** While the column x = 0 below y is empty, (−1, y) and (1, y) are 2y + 2 apart, through the base row (the row
     below is longer). The condition 2y + 2 > r holds for every height above y once it holds at y, and the slit is filled from the
     top, so the two sides are not yet joined above. So for y ≥ 2 with 2y + 2 > r, the left side's new place at (0, y) does not see
     (1, y), and (1, y) does not see it, at 2y + 3. Two places now sit at (0, y).
   - **Height 1.** The left place joins (0, 0), which brings it within 3 of (1, 1). So for r ≥ 3 the two sides meet there, and for
     r = 2 height 1 doubles too.
   - **The lowest doubled height.** Let y₀ be the lowest height that doubles: y₀ = max(2, ⌊r/2⌋) for r ≥ 3, and y₀ = 1 for r = 2.
4. **The invariant.**
   - **Three places, fixed now.** At the end of step 3, fix the places v = (1, y₀ − 1), its west neighbour u and w = (1, y₀). For
     y₀ ≥ 2, u is the single place at (0, y₀ − 1); for y₀ = 1, u is (0, 0).
   - **Their neighbours.** u's north neighbour is the left place at (0, y₀), and w's west neighbour is the right place there. u's
     east neighbour and w's south neighbour are both v.
   - **Only two candidates.** Since w − u ≡ (1, 1) mod 3, and the only pairs of unit offsets that differ by (1, 1) mod 3 are (e₁, −e₂)
     and (e₂, −e₁), a common neighbour of u and w is joined either to u at east and to w at south, or to u at north and to w at west.
   - **Neither adds one.** The first is v. The second would have to be both u's north and w's west neighbour, which are two distinct
     places. Each place keeps at most one neighbour at each offset, so u and w share only v in every continuation.
   - **The doubling spreads.** The doubling does not stay where step 3 left it: the right place at (0, y₀) lacks a south neighbour,
     whose position u holds, so it grows another place there, and so on down. The proof uses only u, v and w.
5. **The limit.**
   - Continue in any fair order. In the square grid each place has four neighbours, and exactly four of the six pairs of them share a
     second neighbour.
   - At v, an opposite pair shares only v. A common neighbour of v's west and east neighbours must be the west one's east neighbour,
     which is v, by the coordinates mod 3; likewise north and south. The pair u, w shares only v as well.
   - So at most three pairs share two neighbours, and the limit is not the square grid. ∎

**The version that lets the order choose.** If a site may act at any missing offset, with the order choosing which, the same slit
splits SQ_r, with the base row grown straight from the seed. This was the first draft's construction (P2).

**Reading.** SQ_r grows wherever a place lacks a neighbour. So a fair order may grow two fronts apart and let them meet beyond the
view, and a local law cannot see that they are about to. The spiral of G2′ grows only at its head, so no order can do this to it.
This is the plane's version of `GROW-COIN-20261107-001`'s order that splits the equator. There a carried coin was the way out. Here,
with coordinates mod 3 among the values, the board's own shape at the head is enough.

## What this adds to what was closed

- **Static laws** (`BOARD-DIST-20261110-001` to `PLACE-FLIP-20261110-001`).
  - **What static laws needed.** The plane needs a named face. With the same nine values as G2′, coordinates mod 3, a static law that
    names the square allows every quotient of the plane by a sublattice of 3Z²: cylinders and tori, in any number of components
    (`BARE-NAMES-20261110-001A`, T4, whose check finds the tori).
  - **What growth gives.** Only tiles from an aperiodic set remove the quotients there, and even then only componentwise. Growth from
    one seed with those nine values forces the plane itself (G2′).
  - **Why.** Every cycle of a grown board is closed by one action inside one view. The square-closing laws here close only cycles of
    zero displacement, so a grown board never wraps around.
- **The pinwheel line** (`COLLAR-PLANE-20261108-001`, `ROUND-PRICE-20261108-001`): roundness of one tiling needs hidden information. This
  epic does not touch roundness.
- **The band law** (`BAND-SURFACE-20261108-001`, `GENUS-BAND-20261108-001`) grows the torus on declared rings and contacts, whose bands
  name its faces.
- **The doubling law** (`BOARD-READ-20261110-001`) reads a drawn plane's distance, scaled: scale and clock, no shape.

## Checks

`check.py` (result in `result.json`), all passed.

**Frozen in the pre-registration.**
- **P1.** The spiral law, run to 40 full turns (6,561 places): after every turn the board is exactly the expected block with every grid
  edge, and exactly one action is enabled. Its order is the ring formula's.
- **P2.** For r = 3, 4 and 6, with H = 2r + 6, the slit order of the version that lets the order choose ends its slit stage with 11, 13
  and 16 grid positions holding two places. Those are the heights y ≥ 2 with 2y + 2 > r, as step 3 predicts. Once every place within
  distance 4 of the slit's base place (0, 1) has four neighbours, its radius-3 ball is not the square grid's.
- **P3, the control.** For the same radii, filling the slit from its base upward leaves no position holding two places.

**Added after the review, not pre-registered.**
- **P4.**
  - **Priorities.** For all 24 priorities and r = 2, 3, 4 and 6, the order of G3 is built from the law's own actions. It doubles
    exactly the predicted heights.
  - **The invariant.** u and w share only v at the end of the slit and after four rounds in which every place within distance 5 of u
    acts until it has four neighbours. At v at most three pairs of neighbours share two.
  - **Both versions.** The version that lets the order choose passes the same checks, with r = 2 added. P2 and P3 now read the view
    without names, as above, and their counts are unchanged.
- **P5.**
  - **Radius 2.** The spiral's views at radius 2, to 40 rings: the head has 77 views and the other places 366, and none coincide.
    Each head view gives one arrow, and the radius-1 rule reads it. The last new kind of view appears at ring 6, and from ring 7 the
    views repeat every three rings.
  - **The run.** The law of G2′, run from the seed for 6,561 places, has exactly one enabled site at every step, its last place, and
    grows the spiral with every grid edge.
  - **Radius 1.** The head's 49 views and the other places' 58 share 13.

## Scope and sources

- **Scope.** Accretion laws over abstract names with values from a finite alphabet; growth from a finite seed; every fair order; the
  plane as the square grid. Merging places, and laws that change existing values, are outside the frozen setting.
- **Sources.** The square spiral, quasi-isometry and asymptotic dimension (Gromov); the rest is elementary.
- **Novelty.** Folklore risk high: the spiral and the order-splitting argument are standard ideas in growth processes. What the epic
  adds is the line's verdict and the comparison of a static and a grown law with the same values.
