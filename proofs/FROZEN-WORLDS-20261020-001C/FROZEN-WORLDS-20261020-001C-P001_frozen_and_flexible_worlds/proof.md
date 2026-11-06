# Colourings have frozen and flexible worlds

Status: Proved

Ticket `FROZEN-WORLDS-20261020-001C`, 2026-10-20. It builds on
`FROZEN-WORLDS-20261020-001B-P001`: linear laws are frozen everywhere or
nowhere. It also uses two results of
`HOLES-AT-INFINITY-20261020-001C-P001`, bound through
`HOLES-AT-INFINITY-20261020-001Z`:
- the flat colouring's class is dense (Theorem 5(b));
- no two-literal system has a knot among its variables (Proposition 4).

## Standard statement

Consider proper 3-colourings of the square grid Z² and of the 3-regular tree.
- A colouring is **frozen** if no other proper colouring differs from it at
  finitely many vertices.
- A vertex is **flexible** at a colouring if some proper colouring that
  differs from it at finitely many vertices recolours that vertex.

We show:
1. **Frozen and flexible colourings.**
   - The colouring (x + y) mod 3 of Z² is frozen. So is any colouring of the
     tree in which every vertex's children carry both other colours.
   - The 2-colourings by bipartition are flexible at every vertex.
   - On both graphs, for each finite vertex set W, the colourings at which
     every vertex of W is flexible form a dense open set.
2. **Three neighbours.** Three neighbours of a vertex never receive three
   distinct colours, and on these graphs that is the only constraint among
   them. The relation "not all distinct" is constrained as a whole, yet
   unconstrained once any one of the three is forgotten.
3. **The hard-core model.** In the independent sets of a graph, every vertex
   is flexible at every configuration, and no three variables are related in
   that way.

## Nearest known results

- **Frozen colourings and height functions on Z².** (x + y) mod 3 is the
  standard frozen colouring (Peled and Spinka, *Lectures on random proper
  colorings of Z^d*). See also Chandgotia, Peled, Sheffield and Tassy; Ray and
  Spinka.
- **Frozen variables in random colourings.**
  - The rigidity threshold, where typical solutions acquire frozen vertices:
    Zdeborová and Krzakala (2007); Achlioptas and Coja-Oghlan (2008).
  - Molloy's freezing threshold: above it, a linear number of vertices cannot
    be recoloured without changing a linear number of vertices.
- **Homomorphism spaces.** Brightwell and Winkler (2000) on dismantlable
  graphs and single-vertex moves.
- **Majority closure of two-literal clauses.** Schaefer (1978).

**Classification: known with a delta.**
- Frozen and flexible colourings and freezing are classical.
- The delta is the knot reading. Under the source-aware reading, the same knot
  of one law is native at some worlds and not at others. The hard-core law has
  native loops at every world and no knot.

## Setting

- **Worlds.** A world of a law is a solution.
  - At a world s, a vertex is **flexible** if some solution differing from s
    at finitely many vertices changes it.
  - s is **frozen** if no other solution differs from it at finitely many
    vertices.
  - Under the source-aware reading, a K1–K3 knot on a vertex set is **native
    at s** if every vertex of the set is flexible at s.
- **K1–K3 over finite domains.** The relation is a proper subset of the
  product (K1). Forgetting any one variable leaves the full product of the
  others (K2). It is nonempty (K3).
- **Heights.** On Z², a proper 3-colouring lifts to a height function
  h: Z² → Z with |h(u) − h(w)| = 1 on edges and h ≡ colour (mod 3)
  (`HOLES-AT-INFINITY-20261020-001C-P001`, Theorem 5(b)). On a tree every
  proper 3-colouring lifts the same way, since a tree has no cycles to
  obstruct the lift.

## Statements

**Theorem 1 (Z²: frozen and flexible worlds).**
- **(a)** The plane colouring π = (x + y) mod 3 is frozen, and so is
  (x − y) mod 3.
- **(b)** The flat colouring φ = (x + y) mod 2 is flexible at every vertex. So
  is every colouring that differs from φ at finitely many vertices.
- **(c)** For each finite W, the worlds at which every vertex of W is flexible
  form a dense open set, which does not contain π.
- **(d)** A world is frozen exactly when, for every finite region, the region's
  colours are the only completion of the colours outside it. All of its
  distinctions are supplied by the rest of the world, that is, at infinity.

**Theorem 2 (the star knot).** Let z be a vertex with neighbours a, b, c. For
example, take z = (1, 0) with a = (0,0), b = (1,1), c = (2,0) in Z², or any
vertex of the 3-regular tree.
- The projection of all proper 3-colourings onto (a, b, c) is exactly N, the
  set of triples that are not all distinct: 21 of the 27.
- N passes K1–K3.
- The knot is native at a world exactly when a, b and c are flexible there. By
  Theorems 1 and 3 this happens on a dense open set of worlds, and at no
  frozen world.

**Theorem 3 (the 3-regular tree: frozen and flexible worlds).**
- **(a)** Root the tree. There is a colouring in which every vertex's children
  carry both colours other than its own, and it is frozen.
- **(b)** The bipartition colouring is flexible at every vertex, and its class
  is dense.
- **(c)** So for each finite W, the worlds at which W is flexible form a dense
  open set that excludes the frozen colouring.

**Theorem 4 (the hard-core law).**
- At every independent set of a locally finite graph, every vertex is flexible.
- No three variables carry a K1–K3 knot.

**Reading under the source-aware reading.** There are three behaviours:
- **Linear laws** (`…001B-P001`) are native at every world or frozen at every
  world.
- **3-colourings are world-relative.** One knot is native in flexible worlds
  and not native in frozen worlds.
- **The hard-core law** has native loops at every world and no knot, so native
  loops are necessary for native knots but not sufficient.

Under the source-blind reading, the colouring knot is a knot at every world,
and the frozen/flexible difference does not show.

## Proofs

**Proof of Theorem 1.**
- **(a)** Let g be a height function agreeing with h = x + y outside a finite
  set, and put D = g − h, which is even.
  - Along an edge in the +x or +y direction, h rises by 1 and g changes by ±1,
    so D changes by 0 or −2. D never increases in those directions.
  - Moving from any vertex in the +x direction eventually leaves the finite
    set, where D = 0. So D ≥ 0 everywhere.
  - The −x direction gives D ≤ 0. So D = 0, and the colouring is unchanged.
  - For x − y, use the +x and −y directions.
- **(b)** At φ, a vertex's four neighbours share one colour, so the vertex can
  take the third colour alone. Now let s differ finitely from φ, and let v be
  any vertex.
  - If s(v) ≠ φ(v), then φ itself differs finitely from s and recolours v.
  - Otherwise, φ with v recoloured is proper, differs finitely from s, and
    recolours v.
- **(c) Open.** Suppose finite changes s₁, …, s_k of s recolour the vertices of
  W, with change sets U_i. Whether a change is proper depends only on the
  colours on U_i ∪ N(U_i). So every world agreeing with s there admits the same
  changes.
- **(c) Dense, and missing π.** The class of φ is dense (HOLES-AT-INFINITY C,
  Theorem 5(b)) and lies in the set by (b). π is frozen.
- **(d)** This restates the definition. ∎

**Proof of Theorem 2.**
- **Projection ⊆ N.** a, b and c all avoid z's colour, so they use at most two
  colours.
- **N ⊆ projection.** Given a triple in N, give z a colour the triple misses.
  - On the tree, {z, a, b, c} is a subtree. Every proper colouring of a finite
    subtree extends one vertex at a time: each new vertex has one coloured
    neighbour, so two colours are left.
  - On Z², a, b and c are pairwise non-adjacent. `check.py` finds all 21
    triples realized on a 5×5 box. Every proper colouring of a box extends to
    Z² by height-function patching (HOLES-AT-INFINITY C, Theorem 5(b)).
- **K1–K3.**
  - K1: the 6 triples with three distinct colours are excluded.
  - K2: every pair (x, y) extends by making the third colour equal to x.
  - K3: N is nonempty.
- **Nativity** follows from the definition. ∎

**Proof of Theorem 3.**
- **(a) Construction.** Give the root colour 0 and its three children 1, 2 and
  1. Give the two children of each later vertex of colour k the colours k + 1
  and k + 2 (mod 3). The colouring is proper.
- **(a) Frozen.** Suppose s′ differs from s on a finite nonempty set U, and
  take u ∈ U of greatest depth.
  - u's children lie outside U, and they carry both colours other than s(u).
  - So s′(u) = s(u), a contradiction.
- **(b) Flexible.** In the bipartition colouring, each vertex's neighbours
  share one colour, so the vertex can take the third colour alone. The proof
  of Theorem 1(b) then applies to every colouring in its class.
- **(b) Dense.** Use the height patch of HOLES-AT-INFINITY C, Theorem 5(b), with
  tree distance in place of grid distance.
  - Lift a colouring t of a finite ball W to heights, and shift by a multiple
    of 6 so that it lies above the base heights (depth mod 2) on W.
  - Take g = max(cone, base), where cone(v) = max_{w∈W} (h_t(w) − d(v, w)).
  - Below each leaf of W, the cone falls by exactly 1 per level, so g equals
    the base below a fixed depth. The change is finite, and it agrees with t
    on W.
- **(c)** As in Theorem 1(c). ∎

**Proof of Theorem 4.**
- **Flexible everywhere.** If s(v) = 1, set it to 0. If s(v) = 0, set v's
  neighbours to 0 and v to 1. Both changes are finite and keep the set
  independent.
- **No knot.** The law consists of the two-literal clauses ¬x_u ∨ ¬x_w.
  - The majority of three independent sets is independent. If u and w were
    both 1 in the majority, some one of the three sets would contain both.
  - Projections of majority-closed relations are majority-closed, and no
    majority-closed relation passes K1–K3 (HOLES-AT-INFINITY C,
    Proposition 4). ∎

## Checks

`check.py` rewrites `result.json` and replays it. Completions are searched
depth-first, choosing the vertex with the fewest remaining colours, with
forward checking.

- **Theorem 2.**
  - On Z², the projection onto (0,0), (1,1), (2,0) computed on a 5×5 box is
    exactly the 21 triples that are not all distinct. It passes the
    finite-domain K1–K3 test.
  - The same holds for the three children of the tree's root.
- **Theorem 1.**
  - With the boundary ring fixed, the plane colourings (x ± y) mod 3 have
    exactly one completion on boxes of side 4–7.
  - At 8 random worlds of the flat class (random sequences of single-vertex
    moves from φ), every vertex of the 3×3 window is recoloured by some
    completion of a 13×13 box with its boundary fixed. At the plane world, none
    is.
  - The star knot's three vertices are flexible at a flat-class world and not
    at the plane world.
- **Theorem 3.**
  - With the vertices at the bottom depth fixed, the frozen tree colouring has
    exactly one completion at depths 3–5.
  - 60 random colourings of the radius-2 ball were patched into the
    bipartition colouring. All are valid, agree on the window, and are finite;
    the deepest change is at depth 10. The check is exact for the whole tree:
    below each leaf of the window the patched heights depend only on the depth,
    so one descending path per leaf, followed until the cone is negative,
    checks every vertex.
- **Theorem 4.**
  - At 20 random independent sets, all 180 window vertices are flexible, by
    changes within distance 1.
  - All 84 triples of the 3×3 window, projected from every independent set of
    a 5×5 box, are majority-closed and none is a knot.

**Controls**, each rejected:
- triples with no common neighbour: (0,0), (2,0), (4,0) allow all 27 triples,
  and a path of three allows 12. Neither is a knot.
- the frozen test applied to the flat colouring and to the tree's bipartition
  colouring: 2 completions each time;
- the flexibility test applied at the plane colouring: no vertex flexible.

## What this does not show

- **Classical facts.** Frozen and flexible colourings are classical. The
  contribution is that, under the source-aware reading, emergence becomes a
  property of the world as well as the law.
- **Random graphs.** Nothing here is claimed about random graphs or about the
  hardness of finding colourings. The link to frozen variables in random
  colourings is a direction, not a result.
- **Nothing here is spatial or metric.** Heights are used only to build finite
  changes.
