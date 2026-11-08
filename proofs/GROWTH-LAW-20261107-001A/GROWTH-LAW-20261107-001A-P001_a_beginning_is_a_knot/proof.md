# A beginning is a knot: a growth history under the knot test

Status: Proved by hand. The finite claims (the knots of the joint laws, the acyclic-orientation knots, the step counts, the
random laws) are checked by computation with controls (`check.py`).

Ticket `GROWTH-LAW-20261107-001A`, 2026-11-07.

## Standard statement

- **The setting.** A growth process builds a finite constraint system step by step. Write its history (which element came
  first, which elements exist) as Boolean variables beside the system's own, and read the whole as one relation, its set of
  allowed joint assignments. A set of variables is a *knot* when the relation's projection on it excludes some assignment while
  every projection on one variable fewer excludes none (minimal dependent sets of size at least three).
- **The results.**
  1. **Order and states are independent.** For a fixed final system the joint relation is a product of the history relation and
     the system's own, so no knot mixes them. When the final system varies, free variables for absent elements and constraints
     that only accumulate make every knot that contains an order variable also contain an existence variable. Existence enters
     only as a guard: "if this element exists, its constraint holds" is itself a knot.
  2. **Local order is pairwise, acyclicity is not.** "Each node has at most one earlier neighbour" is a 2-CNF and has no knot.
     The knots of the set of acyclic orientations of a graph are exactly its cycles, each excluding its two directed
     orientations. On a cycle, "some node has no earlier neighbour" is not-all-equal on every edge, and it contradicts the local
     condition.
  3. **Euler's count.** Along any growth order the steps' changes of the Euler characteristic sum to the final one. So growth by
     sprouting builds only trees, growth by disc moves only discs and spheres, and each cycle or handle costs closing steps.
  4. **Pumping.** A radius-r local rule with k hidden labels per node that accepts some path of more than about
     (2r + 1)·k^(2r+1) nodes also accepts a cycle. A seeded growth process that only sprouts never makes a cycle. In two
     dimensions a local rule rejects every flat torus exactly when its flat configurations are all aperiodic.

## Nearest known result

- **Products.** A relation that is a product over disjoint variable sets has all its minimal dependent sets inside one factor
  (folklore; `OPEN-END-GROWTH-20261107-001B`, Proposition 2, uses the same step).
- **Acyclic orientations.** The acyclic orientations of a graph are the topes of its graphic oriented matroid. A set of
  elements is independent exactly when the topes restricted to it take every sign vector, and a circuit's restriction misses
  exactly its two signatures (Björner, Las Vergnas, Sturmfels, White and Ziegler, *Oriented Matroids*, 1993). Theorem 2(b) is
  this fact for graphs, with K1–K3 in place of independence. The parity law's knots are the circuits of the dual matroid
  (`OPEN-END-GROWTH-20261107-001B`, Proposition 1).
- **Euler's count.** It is the weak Morse equality of discrete Morse theory: unpaired cells counted with signs give the Euler
  characteristic (Forman, *Morse theory for cell complexes*, 1998). Disc moves are shelling steps, and every triangulated
  2-sphere is shellable (Steinitz's theorem with Bruggesser–Mani 1971).
- **Pumping.** Every nonempty one-dimensional subshift of finite type, or sofic shift, has a periodic point. Local checks certify
  that a network is a tree or a path with O(log n) bits per node, distances to a root, and crossing arguments like Theorem 4's
  show that bounded labels do not suffice (proof-labeling schemes: Korman, Kutten and Peleg, *Distributed Computing* 2010;
  locally checkable proofs: Göös and Suomela, *Theory of Computing* 2016).
- **Aperiodicity.** Two-dimensional local rules with hidden labels can forbid every periodic configuration (Berger 1966; Robinson
  1971; on the hexagonal lattice, which is the triangular lattice's dual, Socolar and Taylor 2011).
- **Classification.** Known-with-delta. Each piece is classical. The delta is their reading under the canonical test, applied to
  the program's growth rules. A history splits along the program's own two/three boundary: its local part is pairwise, and its
  global part, time without a loop, is a knot on every cycle of the world. The states knot along cuts and the history along
  cycles, which are dual matroids. The open-end rule's history is wholly pairwise, and a beginning does in one dimension what no
  bounded witness does.

## Setting

- **Worlds.** As in `OPEN-END-GROWTH-20261107-001B`, a hub-free parity law: knots are three-place parity checks, a distinction
  held by two knots is a seam and one held by one knot is an open end. Its knot graph has the knots as vertices and the seams as
  edges. In two dimensions, worlds are two-coloured triangulations of closed surfaces (`SPHERE-GROWTH-20261107-001A`). K_m is
  the octahedral knot sphere.
- **The open-end rule.** Start from one knot with three open ends. Any knot that holds at least two open ends may sprout: a new
  knot takes one of its open ends as a seam and brings two fresh open ends. It grows exactly the thread P_n
  (`OPEN-END-GROWTH-20261107-001B`, Proposition 4).
- **History variables.**
  - *Seam bits*: for each seam, which of its two knots came first. A knot's *parents* are its neighbours that came before it.
  - *Pair bits*: for each pair of knots, which came first.
  - *Existence bits*: which potential sites exist, when the world itself varies.
- **The joint law.** The allowed assignments of history and state variables together: a history of the rule, with a state that
  satisfies the world it built. A variable of a site, pair or distinction that does not exist is free (forgotten). The knot test
  is K1–K3 with erasure as forgetting, applied to this relation like any other. Knots are its minimal constrained sets of at
  least three variables, and computed knots are cross-checked with knotlab's `check_knot`.

## Theorem 1 (the order never knots with the states)

Let a growth rule read only the law, so that the histories that build a world do not depend on its states. Then:

- **(a) Fixed world.** For each world s, the joint law restricted to s is H_s × X_s, the histories that build s times the
  allowed states of s. No knot of it contains both a history variable and a state variable.
- **(b) Worlds that vary.** Suppose, further, that variables of absent things are free, that every world grows from the seed s₀,
  and that constraints accumulate: the shadow of a larger world's law on any set of distinctions lies inside the smaller world's.
  Then on every set T of order and state variables the joint law's shadow is a product, Full on T's order variables times
  (X_{s₀}) on its state variables. So every knot that contains an order variable also contains an existence variable, and the
  knots on state variables alone are the seed's.
- **(c) Existence is a presence literal.** If R is a knot on distinctions Y that holds exactly when the site with existence bit e
  exists, then e → R is a knot on {e} ∪ Y.

*Proof.*
- **(a)** H_s does not depend on the states, so the restricted relation is a product. A set S meeting both factors has its shadow
  equal to the product of its two parts' shadows. If S were a knot, K2 would make both parts free, so S would be free, against
  K1.
- **(b)** The shadow on T is the union over worlds s of (H_s)_{T∩O} × (X_s)_{T∩X}. The seed's term is Full × (X_{s₀})_{T∩X}, since
  no pair of the seed's world exists and every order variable is free there. By accumulation, every other term lies inside it.
  So the union equals the seed's term. A constrained product with a full factor stays constrained when a variable of that factor
  is forgotten, so K2 fails whenever T contains an order variable.
- **(c)** K1: the state with e = 1 and Y outside R is excluded. K2: forgetting e leaves Y free, since e = 0 allows every state of
  Y; forgetting y ∈ Y leaves {e} ∪ Y∖{y} free, since R's shadow on Y∖{y} is free (R is a knot) and e = 0 allows the rest. ∎

**Computed.**
- **Fixed world (check 2).** On the open-end rule's threads, with seam bits (n ≤ 5) or pair bits (n ≤ 4), every knot of the joint
  law is a bond of the thread, found independently as a cut with both sides connected. The history alone is 2-CNF and has no knot.
- **Worlds that vary (check 4).** Take sites −2..1 with the seed at 0, existence bits for −2, −1 and 1, and pair bits for −1, −2
  against 1. The joint law has 14 knots:
  - one on states alone, the seed's parity;
  - twelve of the form "these sites grew, so this bond holds";
  - one inside the history, "if −2 and 1 grew, −2 before 1 needs −1 before 1", an atom of four places.
  None contains an order variable without an existence variable, and in every fixed world all knots are bonds.
- **Controls (checks 3, 4).** Theorem 1 needs its hypotheses.
  - **A rule that reads a state.** Let an inner knot grow right when its own open end is 1 and left when it is 0. The joint law
    then has knots joining the order to the states: 24 of 46 knots at n = 4.
  - **Absent pair bits set to 0.** Fixing the order bits of absent pairs to 0, instead of leaving them free, makes them carry
    existence. Fourteen knots then join order and states, such as "h_m2p1 → the parity at −2".

## Theorem 2 (the local history is pairwise; time without a loop is knotted on every cycle)

Let G be a world's knot graph and orient its seams by their seam bits.

- **(a) The local part is pairwise.** "Every knot has at most one parent" is a conjunction of 2-clauses, one for each knot and
  each pair of its seams, saying the two do not both point into it. So no shadow of it is a knot (no 2-CNF defines a knot, with
  or without witnesses; `KNOT-FOUNDATION-20261019-001`).
- **(b) The global part is a knot on every cycle.** Let A(G) be the acyclic orientations, the histories whose time has no loop.
  A set T of seams is a knot of A(G) exactly when T is a cycle of G of length at least three. The cycle's shadow excludes just its
  two directed orientations: it is not-all-equal on T, after flipping the seams that run against the cycle's direction. Two
  parallel seams are a tie. A(G) is the conjunction of these not-all-equal knots over the chordless cycles.
- **(c) Rings and trees.**
  - On the ring C_n, "some knot has no parent" equals A(C_n), which is NAE over all n seams. This is the beginning: a knot that
    binds every seam of the world, while every proper part of the history is free. With (a) it is unsatisfiable, since at most
    one parent on a ring forces exactly one everywhere, which is a directed cycle.
  - On a tree, (a) alone gives exactly one beginning, since a tree has one knot more than it has seams.
  - So with at most one parent per knot and time without a loop, the world is a forest grown from one beginning per tree. A
    cycle needs a knot with two parents: a closing move.
- **(d) Events.** Linear orders of n events, on their pair bits, are A(K_n), whose knots are the cycles of K_n. For three events
  the order is NAE(b01, ¬b02, b12): any two of the three pairwise orders are free, and the three together are bound.

*Proof of (b).*
- **Extension.** Every acyclic orientation of a subgraph extends to one of G. Take a linear order of all knots extending the
  subgraph's orientation, which is acyclic, and orient every seam by it.
- **Forests are free.** Every orientation of a forest is acyclic, so it extends, and the shadow of A(G) on a forest's seams is
  free.
- **Cycles.** On a cycle C, an orientation extends unless it is one of C's two directed orientations. So the shadow on C excludes
  exactly those two, and every proper subset of C is a forest. So C is a minimal constrained set.
- **Nothing else.** A minimal constrained set T is not a forest, so it contains a cycle, and by minimality it is that cycle.
- **The conjunction.** A directed cycle of shortest length has no chord, since a chord would close a shorter directed cycle with
  one of its two arcs. ∎

**Computed (check 5).**
- **Rings.** For n = 3..10, the local history on C_n is 2-CNF with no knot and allows exactly the two cyclic orientations. The
  beginning equals NAE_n and A(C_n), and knotlab confirms it is a knot. The two together allow nothing.
- **Threads.** For n = 3..10, the local history on P_n allows exactly n orientations, each with one beginning.
- **Graphs.** On K4, the prism, K3,3 and the cube, the enumerated knots of A(G) are exactly the cycles (7, 14, 15 and 28 of them).
  On the Petersen graph (16,680 acyclic orientations) every cycle's shadow is NAE and a knot, and the conjunction over its 22
  chordless cycles is A(G).
- **Events.** Three events' order is NAE_3 with one flip. Four events' order has 7 knots, the 4 triangles and 3 four-cycles of
  K4.
- **Controls.** A cycle plus one more seam is not a knot, and NAE with the wrong flip is not the three-event order.

## Theorem 3 (Euler's count)

Grow a world one top cell at a time in any order: knots with their seams in one dimension, triangles in two. Each step changes
the Euler characteristic of what has grown, and the changes sum to the world's χ.
- **One dimension.** A seed adds 1. A sprout, a knot and its seam, adds 0. A closing seam between two knots already present adds
  −1. So χ = (number of beginnings) − (number of closings), and a connected world grown from one seed has exactly as many
  independent cycles as closings.
- **Two dimensions.** A step adds the triangle (+1), its new edges (−1 each) and its new vertices (+1 each), a change of
  a − b + 1 when a of its edges and b of its vertices were present.
  - The first triangle adds +1 (a = b = 0).
  - ADD, on one boundary edge with a new vertex, adds 0 (a = 1, b = 2).
  - CAP, on two consecutive boundary edges, adds 0 (a = 2, b = 3).
  - END, the last triangle of a closed piece, adds +1 (a = b = 3).
  - PINCH, on one edge whose opposite vertex is already present, adds −1 (a = 1, b = 3).
  So disc moves (ADD, CAP, END) build only discs (χ = 1) and spheres (χ = 2). A closed surface needs at least one END, so one
  of characteristic χ ≤ 0 needs steps that lower χ by at least 2 − χ in all. Each such step attaches a triangle at vertices the
  world already has away from its edges: it joins the growing world to a part of itself.

*Proof.* Each vertex and edge of the final world is new at exactly one step, the first that contains it, so the changes add up
to V − E + F. ADD keeps a disc a disc, CAP does too while the boundary has more than three edges, and END closes a boundary of
three edges into a sphere. ∎

**Computed (check 6).**
- **One dimension.** In 200 runs each of the open-end rule, free sprouting, and sprouting with closings, knots minus seams equals
  one minus the closings (968 closings in all), and the cycle count equals the closings. All 200 open-end runs are threads.
- **Knot spheres.** K_m (m ≤ 5) grown strip by strip (`GROW-COIN-20261107-001A`) uses one first triangle, one END and no PINCH.
  Random disc growth on each never sticks (30 runs each), as shellability predicts.
- **Flat tori.** Breadth-first growth of the p × q tori sums to 0 and needs 3 to 8 PINCH steps. Disc growth sticks every time,
  with 10 to 35 triangles never placed.
- **Controls.** Counting closings as sprouts, or pinches as ADDs, breaks the identity.

## Theorem 4 (no bounded law tells a long thread from a ring)

Let a law of radius r give each knot one of k hidden labels and allow a world when every labelled radius-r window is on its list.
If it allows a thread of n ≥ (2r + 1)·k^(2r+1) + 2r + 3 knots, it allows a ring of length between 2r + 1 and n.

*Proof.*
- **Two equal windows.** Look at positions r + 2, r + 2 + (2r + 1), …, up to n − 1 − r. Their windows hold only inner knots, and
  there are ⌊(n − 2r − 3)/(2r + 1)⌋ + 1 of them, more than the k^(2r+1) possible windows. So two of them, p < q, have equal
  labelled windows.
- **The ring.** Glue knots p..q − 1 into a ring of length q − p ≥ 2r + 1. A knot within r of the gluing sees, across it, knots
  whose labels equal those it saw in the thread, because the windows at p and q agree. Every other knot sees its thread window.
  So every window of the ring is an allowed inner window. ∎

**Consequences.**
- **What a beginning does.** The open-end rule grows threads of every length and never a ring (Theorem 2(c)). So no law with
  bounded hidden labels has exactly its worlds. The beginning does in one dimension what no bounded static witness can.
- **Its price in labels.** To allow a thread of n knots and no ring, a radius-r law needs k^(2r+1) > (n − 2r − 3)/(2r + 1), about
  log₂ n / (2r + 1) bits per knot. A knot's generation, the number of sprouts between it and the beginning, which a growth
  history knows, suffices with log₂ n bits. The counter law of check 7 is that witness.

**Computed (check 7).**
- **Random laws.** Of 3,000 random radius-1 laws with k = 2 labels, 2,197 allow a thread at the bound (29 knots) or longer. For
  every one, the proof's construction, run on a labelling the law allows, gives a ring whose windows all pass. Likewise 556 of 600
  laws with k = 3 (bound 86).
- **Short threads only.** Laws that allow threads but no ring allow only threads of at most 6 knots.
- **The counter control.** With labels 0..K − 1 counting distance from a seed, the law allows threads up to 2K − 1 knots and no
  ring.
- **Misglued rings.** Gluing at two windows that differ gives rings that fail (729 of 1,792 tried at k = 2).

## Proposition 5 (two dimensions)

A radius-r law allows a flat torus of injectivity radius greater than r exactly when one of its flat configurations is periodic.
- **Why.** A torus's labelling lifts to a periodic labelling of the plane with the same windows, and a periodic configuration
  passes to a large enough quotient torus.
- **So in two dimensions:** a law that allows arbitrarily large flat discs and no flat torus must have only aperiodic flat
  configurations. Such laws exist with hidden labels (Berger, Robinson; Socolar and Taylor on the hexagonal lattice). In one
  dimension none exists (Theorem 4).
- **The seam law allows every flat torus.** Every flat torus is a two-kind surface with all co-lines of three points, no digon,
  and faces that two-colour. So the seam law's rule S1 is empty there and the unmarked marking meets S2. The seam law
  (`SPHERE-GROWTH-20261107-001A`) was stated and proved for spheres, so this changes nothing proved there. It says that among
  closed two-kind surfaces its bit singles out the K_m only once the surface is known to be a sphere.
- **Growth excludes tori for free.** Growth by disc moves never builds one (Theorem 3).

**Computed (check 8).** The p × q flat tori for (p, q) = (3, 3), (3, 6), (4, 4), (6, 6), (5, 7) and (8, 8) all have co-line
degree 6, two-coloured faces, no digon and χ = 0.

## Remark (the infinite limit)

On the infinite thread, a history grown from one seed and a history with no beginning, every seam pointing the same way from −∞,
build the same substrate and allow the same states. The beginning's work is finitary: it excludes rings, and the ring's
infinite limit is the same line.

## Reading

**Interpretation, not a theorem.**
- **A beginning is a knot.** A history splits along the program's own two/three boundary.
  - Its local part, which neighbour came first, is pairwise and holds no knot.
  - Its global part, that time has no loop, is a knot on every cycle of the world: constrained as a whole, unconstrained in every
    part. On a ring the beginning is one knot over every seam.
  - A tree's history is wholly pairwise. The open-end rule grows trees, so its history holds no knot at all.
- **States and history are dual.** The world's states knot along its cuts, the bonds, and its history along its cycles. These
  are the circuits of a graph's two dual matroids, and the two never knot with each other.
- **What growth adds to a static law.**
  - It adds whether a world has a history from a beginning, never a knot of the world.
  - In one dimension the beginning excludes rings, which no bounded witness does.
  - In two dimensions only an aperiodic law does it.
  - On spheres the beginning is free, since every two-sphere can be grown by disc moves. What growth adds there beyond bounded
    labels is nothing, which is why `GROW-COIN-20261107-001`'s carried bit was a witness.
- **For the backlog's three hypotheses (B1).** All three hold, the first in a sharper form.
  - The order never knots with the states. Existence does, as "if this grew, its knot holds", which is the canonical test's
    presence literal.
  - The local history is bounded and pairwise. Its global part, a beginning and time without a loop, is a knot per cycle, and no
    bounded local witness certifies it (Theorem 4).
  - A beginning alone does work in one dimension: the number line's ends come from its beginning.

## Checks

`check.py`, with `growth_law_lib.py`, runs in under a minute on the repository's `.venv` and reproduces `result.json`.

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | The open-end rule's runs to n ≤ 7 knots: 2^(n−1) birth orders, seam bits the n monotone sequences, one beginning each | pass |
| 2 | Theorem 1(a): joint laws on threads (seam bits n ≤ 5, pair bits n ≤ 4): all knots are bonds; history 2-CNF, knot-free | pass |
| 3 | Control: a rule that reads a state knots the order to the states | pass |
| 4 | Theorem 1(b, c): sites −2..1: no order-state knot; existence enters as presence literals; control with absent bits set to 0 | pass |
| 5 | Theorem 2 on rings, threads, K4, the prism, K3,3, the cube, the Petersen graph, and 3 and 4 events; controls | pass |
| 6 | Theorem 3 in one dimension (600 runs) and on K_m (m ≤ 5) and flat tori; controls | pass |
| 7 | Theorem 4 on 3,600 random radius-1 laws (k = 2, 3); counter control; misglued rings fail | pass |
| 8 | Proposition 5: flat tori are two-kind with no digon, so the seam law allows them | pass |

## Nonclaims

- **The worlds.** The theorems concern hub-free parity laws and two-kind surfaces grown by the moves named. Other growth rules
  are covered only when they satisfy Theorem 1's hypotheses: rules that read the law only, absent things forgotten, constraints
  accumulating.
- **No new mathematics is claimed.** The reading is new. The mathematics is classical: products, oriented matroids, discrete
  Morse theory, pumping and aperiodic tilings.
- **Physical time.** Formation order is not physical time (`AGENTS.md`). Nothing here models one.
