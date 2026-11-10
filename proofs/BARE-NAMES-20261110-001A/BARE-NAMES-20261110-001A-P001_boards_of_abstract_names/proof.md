# Boards of abstract names

Status: Proved

Ticket `BARE-NAMES-20261110-001A`, 2026-11-10, the challenge of A54. Pre-registered in commit eed41814b before any computation and
before ticket B's census; T1's and T5's arguments were sketched by hand while the registration was written (disclosed there).

## Setting

- **Names.** A countably infinite set N with no structure: no letters, and nothing a law can read to tell two names apart.
- **States.** Each unordered pair of distinct names u, v has a neighbour distinction n(u, v), so being neighbours is symmetric, and
  each name has a value s(u) in a finite alphabet Q. The board is the graph of the neighbour distinctions, with the values on its
  places.
  - In T1 only, identity distinctions e(u, v) ("one place") may be added. They form an equivalence that the values and the
    neighbour distinctions respect, and names that are one place are not neighbours. These rules are finitary clauses.
- **Laws.** A uniform law is a finite set of clause templates, each applied to every tuple of names alike, whether or not the tuple
  repeats a name.
  - A **finitary** clause has finitely many literals.
  - An **existence clause** says that every place u has neighbours v₁, …, v_m with a property φ of the names, for instance "every
    place has at least d neighbours". It is one infinite clause per name, of the kind Leibniz's rule already is.
  - A **count law of degree d** says that every place has exactly d neighbours and that its value, with the multiset of its
    neighbours' values, lies in an allowed set. The 1,024 Life-like one-bit laws, read without letters, are the count laws of
    degree four.
- **First-order laws.** A law of finitary and existence clauses is a first-order sentence of the form ∀∃.
- **Counted per name.** The source-aware reading counts a change by the distinctions it flips. Here every distinction belongs to one
  name or one pair of names (A53).

## T1. Finitary laws allow a structureless board

**Statement.** If a finitary law allows a state, it allows one in which every name has the same value and either every two names
are neighbours or no two are. With identity distinctions, it allows such a state or the state in which all names are one place.

**Proof.**
1. **A homogeneous set.** Fix an allowed state x. By the pigeonhole principle infinitely many names share a value. Colour each pair
   of them by its neighbour and identity distinctions. By Ramsey's theorem for pairs, an infinite set I of them has every pair of
   one colour.
2. **Copy it onto every name.** Take a bijection φ: N → I and let x′ = x ∘ φ, so that each distinction of names u, v in x′ is that
   of φ(u), φ(v) in x.
3. **The copy is allowed.** Every template is applied to every tuple, and φ is injective, so it keeps which names of a tuple
   coincide. Each clause at names u₁, …, u_k in x′ is therefore the same template's clause at φ(u₁), …, φ(u_k) in x, which holds.
   (Existence clauses are what this step cannot carry: in x′ they would range over I only.)
4. **It is structureless.** In x′ every name has one value and every pair one colour. If that colour has e true, all names are one
   place, and then no two are neighbours. ∎

**Corollaries.**
- **No neighbour can be forced with finite degree.** A finitary law under which every place has finitely many neighbours forbids the
  complete board. So it allows the board on which no two places are neighbours or, with identity distinctions, the one-place board.
  It can bound the degree, but it never forces a place to have a neighbour.
- **No finite board but one place.** With identity distinctions, if a finitary law allows a finite board, one of its places holds
  infinitely many names. Taking I inside that place in step 1, with no need for Ramsey's theorem, shows that the law allows the
  one-place board. So it forces no finite board other than one place. With letters, every finite board can be forced
  (`BOARD-DIST-20261110-001A`, Theorem 4).
- **Restriction, not unfolding.** Every finitary law, even one that names a relation, allows a structureless board: the complete
  board, the board with no neighbours, or one place. The mechanism is that a finitary law survives restriction to a subset of the
  names. With letters there is no such restriction, since a name's neighbour names are always there. This is not the unfolding
  theorem: its structureless board can be the collapse, the opposite of the tree.

## T2. A degree supplied by the law carries a labelling

**Statement.** Let G be a countable simple graph in which every place has exactly 2k neighbours. Then there are permutations
σ₁, …, σ_k of its places, with no fixed points, such that every edge of G is {v, σ_i(v)} for exactly one i and one v. So each
component of G is the Schreier graph of a subgroup of the free group F_k, and every board of a law of degree four is a disjoint union
of simple Schreier graphs of F2.

**Proof.**
1. **An Euler orientation.** Orient the edges so that every place has k edges in and k out.
   - For a finite set F of places, take the edges at F and merge every endpoint outside F into one new vertex z. Every place of F
     has even degree 2k, so z has even degree too, every component of this finite multigraph has an Euler circuit, and following
     the circuits orients the edges at F with k in and k out at each place of F.
   - Each place's condition involves its 2k edges only. So by compactness (Tychonoff's theorem on the orientations of the countably
     many edges) one orientation satisfies all of them.
2. **k perfect matchings.** Form the bipartite graph D with a copy v⁺ and a copy v⁻ of each place, and an edge v⁺w⁻ for each edge
   oriented v → w. D is k-regular and locally finite.
   - For a finite set F of its vertices, Hall's theorem gives a matching covering F's left vertices and one covering its right
     vertices, since in a k-regular bipartite graph every finite set has at least as many neighbours. The Mendelsohn–Dulmage
     theorem combines them into one matching covering F. (A matching covering one side of the bi-infinite path need not cover the
     other, so the combination is needed.)
   - By compactness again, with each vertex's condition "exactly one chosen edge" involving its k edges only, D has a perfect
     matching. Removing it leaves a (k − 1)-regular graph, so D splits into k perfect matchings.
3. **The permutations.** The i-th matching sends each v⁺ to one w⁻ and reaches each w⁻ once, so v ↦ w is a permutation σ_i. Every
   edge is oriented once, so it lies in exactly one matching, and no σ_i has a 2-cycle. σ_i has no fixed point because G has no
   loops. ∎

For finite graphs this is Petersen's 2-factor theorem (1891).

**What the letters draw.**
- With letters, every name has four neighbour names, and the board is a quotient of one tree of names, so it is connected. Its
  boards may have loops and repeated edges, and the collapse is one place.
- Over abstract names an existence clause can supply a degree, and T2 then supplies a labelling. But a law cannot read that
  labelling: it exists, and no clause can name it. With letters a law addresses its four neighbours directly, while the law of T4
  has to rebuild the directions from coordinates in the values. So the letters draw four neighbour names per name, a labelling the
  law can read, and one connected world, which no law of bounded degree can force (T4).

## T3. The unfolding theorem for count laws

**Statement.** Let a count law allow a board G. Then it allows every countable covering graph of every component of G, with the
values lifted, and every disjoint union of countably many of its boards. So if it allows a board with a cycle, it allows a board
whose components are trees: the universal cover of that component.

**Proof.**
- **Covers.** A covering map sends the neighbours of a place bijectively onto the neighbours of its image, and lifted values agree
  with their images. So every place of the cover has the degree and the multiset of neighbour values of its image, which is
  allowed.
- **Disjoint unions.** A count law reads only each place and its neighbours.
- **Placing it on the names.** The universal cover of a component with a cycle is a countably infinite tree, so it can be put on N.
  A finite board is put on N as infinitely many disjoint copies. ∎

**Beyond count laws.** A finitary clause that reads a walk through several distinct names can exclude the tree. Take degree four,
values in Z/3, every place of value q with two neighbours of value q, one of q + 1 and one of q − 1, and forbid a path u–v–w–z of
four distinct names with values 0, 1, 2, 0. The cylinder Z × C₃ with the value j at (i, j) is allowed, since its only such walks
close up (z = u). On the tree that walk has distinct ends, so no tree is allowed. Distinct names tell a walk that closes from one
that does not, so such a clause plays the part that a named relation plays with letters. With letters, the tree comes back for every
law that names no relation and allows an infinite board (`BOARD-DIST-20261110-001A`, Theorem 3); without letters this is proved here
for count laws.

## T4. Connectedness cannot be forced with bounded degree, and one named face gives planes

**Statement.**
1. If a first-order law allows a board with a component of infinite diameter, it allows a board with at least two components. A
   law of bounded degree whose boards are infinite and connected has such a component, so no law of bounded degree forces a single
   connected infinite board. (The finitary law "every two names are neighbours" forces a connected board, of unbounded degree.)
2. There is a first-order law, naming the square, whose boards are exactly the disjoint unions of planes (grid graphs of Z²), each
   with a tiling by a fixed aperiodic set of Wang tiles.

**Proof of 1.** Add two names c, d and, for every m, the sentences "c and d are joined by no path of length at most m" and "there
are at least m places". Every finite part of this theory holds in the given board, with c and d far apart in the infinite component.
By compactness and the downward Löwenheim–Skolem theorem the whole theory has a countably infinite model. It can be put on N, and in
it c and d lie in different components. ∎

**Proof of 2.**
- **The law.** Values are pairs (c, t): a coordinate c in (Z/3)² and a tile t of an aperiodic Wang set W, such as Jeandel and
  Rao's eleven tiles.
  - Neighbours' coordinates differ by a unit vector ±e₁ or ±e₂.
  - Every place has a neighbour at each of the four offsets (existence clauses) and not two at one offset (finitary).
  - Squares close: if v and w are u's neighbours at +e₁ and +e₂, then v's neighbour at +e₂ is w's neighbour at +e₁ (finitary, on
    five names). This clause names the square.
  - Neighbours at +e₁ match their east and west colours, and neighbours at +e₂ their north and south colours (finitary).
- **Each component is a quotient of the plane.** In a component C, let e₁ move each place to its neighbour at +e₁.
  - The move is well defined by the uniqueness clause. −e₁ is its inverse: u's neighbour at +e₁ has u as its neighbour at −e₁.
  - e₁ and e₂ commute because squares close. So Z² acts on C, transitively because every edge is a unit move.
  - An element g of Z² that fixes a place adds g mod 3 to its coordinate, so g lies in 3Z². So C is the Cayley graph of Z²/L for a
    sublattice L of 3Z². It is a simple graph, since each place's four neighbours have four different coordinates.
- **The tiles leave only the plane.** The tiles give a tiling of Z²/L, that is, a tiling of the plane by W with every element of L as
  a period. A Wang set with a tiling that has one nonzero period also has a doubly periodic tiling (the lemma used in
  `BOARD-DIST-20261110-001A`, Theorem 8). W has none, so L = 0 and C is the plane.
- **Conversely,** every tiling of the plane by W, with coordinates mod 3, is an allowed component, and W tiles the plane. ∎

So without letters the plane still follows from one named face, as with letters (`BOARD-DIST-20261110-001A`, Theorem 8), but the
law must also carry coordinates mod 3 to rebuild the directions, and by part 1 it forces planes only componentwise.

## T5. Boards of abstract names are not frozen

**Statement.** Let x be a state allowed by a count law of degree d ≥ 1.
1. **The switch.** If {u, v} and {u′, v′} are disjoint edges with s(u) = s(u′) and s(v) = s(v′), and u–v′ and u′–v are not edges,
   then replacing the two edges by {u, v′} and {u′, v} gives an allowed state. It differs from x in four neighbour distinctions.
   If the two edges are one edge in two copies of a finite component, and it lies on a cycle there, the switch joins the copies
   into one connected component, a double cover, so the board changes up to isomorphism. If they are one bridge in two copies, as on
   copies of a tree, the switch only exchanges the names beyond it.
2. **The exchange.** Exchanging two names u and w gives an allowed state. It differs from x in finitely many distinctions: the two
   values and the neighbour distinctions at u and w.
3. **Every distinction is flipped.** Suppose x is made of infinitely many disjoint copies of one board, possibly disconnected, that
   uses at least two values. Then every neighbour distinction and every value of x is flipped by a finite change. So every knot
   among them passes the source-aware condition, counted per name.

**Proof.**
1. Each of u, v, u′, v′ keeps its degree and trades a neighbour for one of the same value: u trades v for v′, v trades u for u′, and
   so on. No other place changes. So every place still has an allowed value and multiset of neighbour values. For the cycle case,
   the switched pair of copies is the double cover in which exactly the switched edge crosses, which is connected when the edge
   lies on a cycle; it has twice as many places as the copies, which are unchanged elsewhere.
2. A permutation of N carries allowed states to allowed states because the law is uniform. Only distinctions at u or w change, and
   each of them has d neighbours.
3. Exchanging u and v with the two ends of an edge in another copy makes them neighbours (d ≥ 1 gives an edge). Exchanging v with a
   place of another copy separates them. Exchanging u with a place of another value flips s(u). Each exchange changes finitely many
   distinctions. ∎

**Against the frozen boards of letters.** With letters, two boards differ in infinitely many identity distinctions, so nothing
involving the board passes the source-aware condition (`BOARD-DIST-20261110-001A`, Theorem 5; A53). Without letters a board changes
by four distinctions. Ticket B finds 90 one-bit count laws in which one neighbour distinction and its two endpoint values form a
knot. Every one of them uses both values, possibly in different components, so part 3 applies to all 90; `check.py` carries out the
moves for the 57 that have a connected board with both values in the census's frozen list.

**A reading to record.** The exchange in part 2 is a renaming: the new state is the old one with two names swapped, the same board
up to isomorphism. The source-aware condition says a knot is native only when each of its variables is flipped by a finite change.
Under abstract names renamings flip every distinction, for any uniform law of finite degree d ≥ 1 with two values, so the condition
excludes nothing and carries no information about the board. A count that ignored renamings would keep the switch's flips on cycles
of finite components; it would lose the flips at tree states and most flips that create an edge, and it would need other moves to
flip values (A58).

## Checks

`check.py` (result in `result.json`), all passed:
- **T2.** On 30 random simple 4- and 6-regular graphs with 10 to 40 places, an Euler orientation and Hopcroft–Karp matchings give
  the permutations, and their edges are exactly the graph's, each once.
- **T3.** For the 57 knotted count laws with a connected two-valued board in ticket B's frozen list, three random double covers of
  that board, with the values lifted, are allowed.
- **T5.** For the same 57 laws, the switch and both exchanges succeed on two disjoint copies.
- **T4.** On the tori C_m × C_n with 3 ≤ m ≤ n ≤ 9, the square law without tiles has a state exactly when 3 divides m and n (by
  exhaustive search with propagation), as every component must be Z²/L with L inside 3Z². The referee's own search agrees.
- **Ticket B's table.** Every pair (value, number of 1-neighbours) and every edge value pair in an allowed colouring of a frozen
  board lies in the census's lists for that law, for all 1,024 laws.

## Scope and sources

- **Scope.** Countably infinite sets of names; symmetric neighbour distinctions; finite alphabets; finitary laws (T1), laws of
  finitary and existence clauses (T2 to T5), count laws (T3, T5). Leibniz's rule with abstract names is not treated.
- **Sources.** Ramsey's theorem (1930); Petersen's 2-factor theorem (1891); Hall's theorem; the Mendelsohn–Dulmage theorem (1958);
  Tychonoff's theorem; covering graphs; the compactness and Löwenheim–Skolem theorems; Berger (1966), Robinson (1971) and Jeandel
  and Rao (2015) for aperiodic Wang tiles; the switch is the 2-switch of graph theory, restricted to edges with matching values.
- **Novelty.** Every ingredient is classical, and each statement here is a short consequence, so folklore risk is high throughout.
  What the epic adds is the reading for the board line: what the letters draw and what freezes a board.
- **Review.** An independent referee read this proof before publication. It found no error in T1 to T4's main statements or in T2,
  and asked for the changes made here: the hypotheses (countably infinite names, symmetric neighbour distinctions, d ≥ 1), the
  identity case of T1's first corollary, the switch's change of board limited to edges on cycles, the source-aware condition read
  as a necessary one, connectedness limited to bounded degree, the period lemma for Wang tiles, and the example of a walk clause
  that excludes the tree.
