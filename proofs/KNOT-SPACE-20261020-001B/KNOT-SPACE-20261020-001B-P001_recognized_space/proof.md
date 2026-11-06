# A law recognizes its space rather than creating it

Status: Proved

Ticket `KNOT-SPACE-20261020-001B`, 2026-10-20. It uses:
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001` ("the circuits
  proof");
- the census `KNOT-SPACE-20261020-001A-E001` ("A") and its continuation
  `KNOT-SPACE-20261020-001C-E001` ("C");
- Theorem 1 of `HOLES-AT-INFINITY-20261020-001B-P001`, for the remark on
  infinite graphs.

**What "space" means here.** It means a graph, or a complex of vertices,
edges and faces, that is read from a law's allowed states. The object is
combinatorial. It is not a composed topology in the protected sense, a contact
network, a native path or a metric, and no contact gate is checked.

## Standard statement

**Setting.**
- A system is read only through its **allowed states**: the set S of joint
  states of its declared variables, with any witnesses quantified away.
- **Circuits** are minimal constrained sets of variables, relative to each
  variable's range (the circuits proof). **Ties** are circuits of two
  variables and **knots** are circuits of at least three. When the circuits
  satisfy circuit elimination, they form the **knot matroid**.
- **Parity laws.** A law is a parity law when S is a coset a + C of a binary
  code C ⊆ F₂^E. C is its **direction code**, the set of sums s + s′ of
  allowed states. M[C] is the column matroid of a generator matrix of C:
  - its cocircuits are the minimal supports of C;
  - its circuits are the minimal supports of the dual code C^⊥.
- **Two laws on a graph G with edge set E**, one variable per edge:
  - The **gauge law** over a group Γ, with edges oriented, allows the edge
    values x_e = p(tail) · p(head)⁻¹ for vertex potentials p ∈ Γ^V. The
    potentials are quantified away. Over F₂ its allowed states are the cut
    space B(G).
  - The **Tseitin law** with charge c allows the x ∈ F₂^E whose edges at each
    vertex v sum to c(v). Its allowed states are a coset of the cycle space
    Z(G) = B(G)^⊥.
- **The graph reading** of a binary code D on E.
  - Its **vertices** are the minimal supports c of D for which M[D] \ c, the
    matroid with c's coordinates deleted, is connected.
  - It **succeeds** when every coordinate lies in exactly two vertices and the
    vertices span D. The **read graph** then has these vertices, with each
    coordinate an edge joining the two vertices that contain it.
  - The **dual reading** is the reading of D^⊥, and its vertices are the
    **read faces**.

**Results.**
1. **Presentation invariance** (Proposition 1). Systems with the same allowed
   states have the same circuits, knots, knot matroid and readings.
2. **Parity laws** (Lemma). The knot matroid of a parity law is M[C].
3. **Gauge and Tseitin** (Proposition 2).
   - A gauge law over any group with at least two elements has the cycles of
     its graph as circuits.
   - A Tseitin law has the bonds as circuits.

   So the two laws of one graph have dual knot matroids, M(G) and M*(G).
4. **The graph, up to twists** (Theorem 3).
   - If G is 3-connected, the reading of the gauge law's allowed states
     returns exactly G's vertex stars, and so G itself.
   - Two graphs on one edge set have the same allowed states exactly when they
     are 2-isomorphic. A Whitney twist changes the graph but not the states.
5. **The sphere** (Theorem 4). If G is 3-connected and planar, the dual
   reading returns the face boundaries of G's unique embedding. Vertices,
   edges and faces then form the 2-sphere.
6. **Recognition** (Theorem 5). Suppose a parity law's knot matroid M is
   3-connected with at least 4 elements.
   - The reading succeeds exactly when M is graphic. It then returns the only
     graph G with M(G) = M, and the law has G's gauge states, translated by
     one state.
   - The dual reading succeeds exactly when M is cographic.
   - Both succeed exactly when the graph is planar, and the law then carries a
     sphere.
   - By Tutte, the reading fails exactly when M has a minor F₇, F₇*, M*(K₅)
     or M*(K₃,₃).
7. **Space is recognized, not created** (Corollary 6).
   - The space is read from the allowed states alone.
   - It is present exactly when the knot matroid is graphic.
   - It does not come from how the law was written. A local law of 8 random
     constraints on 16 variables, written on no graph, carries a sphere.
   - Most laws carry none (Remark 8).
8. **Infinite graphs** (Remark 7, cited). On a locally finite graph, the
   Tseitin law's circuits depend on the reading.
   - Over all solutions, they are the minimal finite cuts with a finite side.
   - Within one class of finitely different solutions, they are the finite
     bonds. By Bruhn and Diestel, the dual matroid then has the circles
     through the ends as circuits.

## Nearest known results

- **Whitney (1932, 1933).**
  - A graph is planar exactly when it has an abstract dual.
  - A 3-connected planar graph has one embedding in the sphere.
  - Two graphs have the same cycle matroid exactly when they are
    2-isomorphic.
- **Tutte (1958, 1959).** A binary matroid is graphic exactly when it has no
  minor F₇, F₇*, M*(K₅) or M*(K₃,₃).
- **Tutte (1963), *How to draw a graph*.** In a 3-connected planar graph, the
  face boundaries are the induced non-separating cycles. Theorem 3(a) uses the
  cocircuit form of this idea, which holds for every 3-connected graph and has
  an elementary proof.
- **Binary matroids** (Oxley, *Matroid Theory*, 2nd ed., 2011, chapters on
  binary matroids and 3-connectivity).
  - A binary matroid determines its code.
  - Duality preserves 3-connectivity.
  - For a graph with at least 4 vertices and no isolated vertex, M(G) is
    3-connected exactly when G is 3-connected and simple.
- **Infinite graphs.**
  - [Bruhn and Diestel, *Infinite matroids in graphs*](https://arxiv.org/abs/1011.4749)
    show two things:
    - the bonds, finite and infinite, are the circuits of the matroid dual to
      the finite-cycle matroid;
    - on a locally finite graph, the matroid dual to the finite-bond matroid
      has as circuits the edge sets of circles in the Freudenthal
      compactification.
  - `HOLES-AT-INFINITY-20261020-001B-P001` Theorem 1 gives the constant
    parities of an infinite Tseitin system.

**Classification: classical mathematics, read in the program's terms.**
- Nothing below is new as mathematics.
- The delta is the reading:
  - the knot matroid is what carries a law's graph;
  - the gauge–Tseitin duality is knot-matroid duality;
  - a randomly written local law carries a sphere;
  - the infinite case splits into two readings.

## Proposition 1 (presentation invariance)

Let two systems, with any constraints and any witness variables, have the same
allowed states S on the same declared variables. Then they have the same
circuits, ties, knots and knot matroid. For parity laws they also have the same
direction code and readings.

*Proof.* Each of these is defined from S alone:
- a set Y is constrained when |π_Y(S)| is less than the product of the range
  sizes |π_v(S)|;
- the direction code is {s + s′ : s, s′ ∈ S};
- the readings use only the code. ∎

Census A checked this on scrambled presentations: random row operations on
the constraints changed no reading. The point is that whatever space a law
carries belongs to its allowed states, not to its constraints.

## Lemma (parity laws)

Let S = a + C, with C a binary code on E.
- A variable constant on S lies in no circuit.
- If no variable is constant, a set Y is constrained exactly when some nonzero
  y ∈ C^⊥ has its support inside Y.
- So the circuits are the minimal supports of C^⊥, and the knot matroid is
  M[C]. Its cocircuits are the minimal supports of C.

*Proof.*
1. **Constant variables.** If j is constant, it adds a factor 1 to both
   |π_Y(S)| and the product of ranges. So Y is constrained exactly when
   Y − j is, and j lies in no minimal constrained set.
2. **Other variables.** Every other range is {0, 1}, and π_Y(S) is a coset of
   π_Y(C). So Y is constrained exactly when π_Y(C) ≠ F₂^Y. That holds exactly
   when some nonzero y ∈ F₂^Y is orthogonal to π_Y(C), that is, when y,
   extended by zeros, lies in C^⊥.
3. **The matroid.** A set of columns of a generator matrix of C is dependent
   exactly when a nonzero vector of C^⊥ is supported on it. So these minimal
   sets are the circuits of M[C]. Its cocircuits are the minimal supports of
   the row space C. ∎

## Proposition 2 (gauge and Tseitin laws)

Let G be a finite graph without loops.

**(a)** For any group Γ with at least two elements, the circuits of the gauge
law are the edge sets of the cycles of G. So its knot matroid is the cycle
matroid M(G):
- its knots are the cycles of length at least 3;
- its ties are the pairs of parallel edges.

*Proof.*
1. **Ranges are full.** Every edge takes every value: put p(tail) = g and
   p(head) = 1.
2. **Forests are unconstrained.** Let F be a forest and (g_e) any values on
   it. In each tree, put p = 1 at a root and walk outward:
   - if p(tail) is known, set p(head) = g_e⁻¹ p(tail);
   - if p(head) is known, set p(tail) = g_e p(head).

   This realizes the values, so F is unconstrained.
3. **Cycles are constrained.** Walk around a cycle v₀ e₁ v₁ … e_k v₀. Take
   x_{e_i} when e_i is traversed from tail to head, and x_{e_i}⁻¹ otherwise.
   Each factor is p(v_{i−1}) p(v_i)⁻¹, so the ordered product telescopes to 1.
   An assignment with the value g ≠ 1 on one edge and 1 on the others violates
   this.
4. **Conclusion.** A set is constrained exactly when it contains a cycle. ∎

No commutativity is used, so a gauge law over S₃ carries its graph's cycles
just as one over Z₂ does.

**(b)** For a satisfiable charge, the Tseitin law's allowed states are a + Z(G),
and Z(G)^⊥ = B(G).
- By the Lemma, its circuits are the bonds of G with at least two edges. A
  bridge is constant.
- So its knot matroid is M*(G), with the coloops removed.

**(c)** Over F₂, the gauge law's direction code B(G) and the Tseitin law's Z(G)
are dual codes. Their knot matroids M(G) and M*(G) are dual matroids. ∎

## Theorem 3 (the graph, up to twists)

**(a)** Let G be 3-connected: at least 4 vertices, no loops, and no separating
pair of vertices. Then the minimal supports c of B(G) with M(G) \ c connected
are exactly the vertex stars.
- So the reading of the F₂ gauge law's allowed states succeeds and returns G.
- For a gauge law over any group, the same reading applied to the knot
  matroid M(G) of Proposition 2 returns G. Its vertices are the cocircuits
  whose deletion leaves the matroid connected.

*Proof.* The minimal supports of B(G) are the bonds of G.
- **Stars qualify.** Let v be a vertex.
  - G − v is connected, so the star δ(v) is a bond.
  - M(G) \ δ(v) is the cycle matroid of G − v. That graph is 2-connected,
    loopless and has at least 3 vertices, so its cycle matroid is connected.
- **No other bond qualifies.** Let D = E(A, B) be a bond that is not a star.
  - Then G[A] and G[B] are connected and each has at least two vertices.
  - So each has an edge, and M(G) \ D = M(G[A]) ⊕ M(G[B]) is disconnected.
- **The reading succeeds.** The read vertices are the n stars. Each edge lies
  in the two stars of its ends, and the stars span B(G). ∎

**(b)** Let G and G′ be graphs on one edge set E, with no isolated vertices.
Their F₂ gauge laws have the same allowed states exactly when M(G) = M(G′).
By Whitney, that holds exactly when G′ is obtained from G by:
- identifying two vertices in different components, or the reverse,
  splitting a cut vertex;
- Whitney twists, which reflect one side of a 2-separation {u, v} and so
  swap u and v on that side.

The same holds for Tseitin laws, with the charges matched.

*Proof.*
1. **Same states give the same matroid.** If B(G) = B(G′), their minimal
   supports agree, and these are the cocircuits of M(G) and M(G′).
2. **The same matroid gives the same states.** Conversely, B(G) is spanned by
   the bonds of G. So two graphs with the same cocircuits have the same cut
   space.
3. **Whitney.** The description of the graphs is Whitney's 2-isomorphism
   theorem.
4. **Tseitin.** The allowed states are a + Z(G) with Z(G) = B(G)^⊥. Taking
   G′'s charge to be the boundary of a in G′ gives the same coset. ∎

So the allowed states determine a 3-connected graph exactly, and a
2-connected one only up to Whitney twists. A twist writes a different graph
with the same states. The law cannot tell which graph it was written on.

## Theorem 4 (the sphere)

Let G be simple, 3-connected and planar.

**(a)** The dual reading of G's F₂ gauge law, which reads Z(G), succeeds. Its
faces are exactly the face boundaries of the unique embedding of G.

**(b)** The read vertices, edges and faces form a cell decomposition of the
2-sphere, and V − E + F = 2.

*Proof.*
- **(a) Faces.**
  1. G has one embedding (Whitney). Its geometric dual G* satisfies
     M(G*) = M(G)*.
  2. M(G) is 3-connected and duality preserves that. So M(G*) is
     3-connected, and G* is 3-connected and simple, with at least 4
     vertices.
  3. The edge bijection identifies Z(G) with B(G*). By Theorem 3(a) applied
     to G*, the reading of Z(G) returns the stars of G*, which are the face
     boundaries of G.
- **(b) The sphere.**
  1. G is 2-connected, so each face of the embedding is an open disc bounded
     by its facial cycle. The cells are those of the embedding.
  2. Euler's formula is here the dimension count:
     dim B(G) + dim Z(G) = (V − 1) + (F − 1) = E. ∎

The checks confirm the surface combinatorially. Every edge lies in two faces,
the faces at each vertex form one cycle, and the complex is connected with
V − E + F = 2. By the classification of surfaces, such a complex is the
sphere.

## Theorem 5 (recognition)

Let S be the allowed states of a parity law with direction code C. Let
M = M[C] be its knot matroid, and suppose M is 3-connected with at least 4
elements.
- **(a)** The reading succeeds exactly when M is graphic. Then:
  - the read graph G is 3-connected;
  - it is the only graph without isolated vertices whose cycle matroid is M;
  - S = a + B(G), so the law has G's gauge states translated by one state.
- **(b)** The dual reading succeeds exactly when M is cographic. Then the read
  graph G′ has M = M*(G′), and S = a + Z(G′) is a Tseitin law on G′.
- **(c)** Both succeed exactly when M = M(G) with G planar. Then G′ = G*, and
  the cells form the sphere of Theorem 4.
- **(d)** The reading fails exactly when M has a minor F₇, F₇*, M*(K₅) or
  M*(K₃,₃). The dual reading fails exactly when M has a minor F₇, F₇*, M(K₅)
  or M(K₃,₃).

*Proof.*
- **(a) Success implies graphic.** If the reading succeeds, every coordinate
  lies in exactly two read vertices. So the read vertices are the stars of a
  graph H on E. They span C, so C = B(H) and M = M[B(H)] = M(H).
- **(a) Graphic implies success.**
  1. Suppose M = M(G), with G having no isolated vertices.
  2. M is connected, so G is 2-connected and loopless.
  3. M is 3-connected with at least 4 elements, so it is simple. Then G has
     at least 4 vertices: a simple graph on 3 vertices has at most 3 edges.
     So G is 3-connected and simple (Oxley).
  4. C and B(G) are binary codes with the same matroid. A binary code is
     spanned by its minimal supports, so C = B(G).
  5. Theorem 3(a) gives success, and the reading returns G.
  6. Uniqueness: the reading is a function of S. Alternatively, Whitney's
     theorem says 3-connected graphs are determined by their cycle matroids.
- **(b)** Apply (a) to C^⊥. Its matroid M* is 3-connected with at least 4
  elements.
- **(c)** M is both graphic and cographic exactly when M = M(G) with G planar
  (Whitney's planarity criterion). G is 3-connected by (a). The abstract dual
  G′ of a 3-connected planar graph is its geometric dual. Theorem 4 then
  applies.
- **(d)** This is Tutte's excluded-minor theorem for graphic matroids, applied
  to M and to M*. ∎

## Corollary 6 (space is recognized, not created)

Within parity laws on finite graphs:
- **Read from the allowed states.** By Proposition 1 and the Lemma, the space
  a law carries is read from its allowed states alone.
- **Present when graphic.** By Theorem 5, a graph is there exactly when the
  knot matroid is graphic, and a sphere exactly when it is planar-graphic.
  Then the allowed states determine the graph: exactly at 3-connectivity, and
  up to twists below it (Theorem 3).
- **Presence is a matroid property.** By Tutte, presence is decided by
  excluded minors. The way the law was written does not decide it, in either
  direction:
  - **The sphere law** has 16 variables and 8 parity constraints, each on 3
    to 5 variables chosen at random with no graph in mind (census C). Its
    allowed states carry a sphere with 9 vertices, 16 edges and 9 faces.
    - Only 5 of its 8 constraints are faces. The other 3 are sums of faces.
    - 4 of the 9 faces are not constraints.

    The sphere is in the allowed states, not in the constraints.
  - **Twists** write different graphs with the same allowed states
    (Theorem 3(b)).
- **Most laws carry none** (Remark 8 and census C).

So a law does not create a space. It carries one exactly when its knot matroid
is graphic, and then its allowed states recognize that space.

## Remark 7 (infinite graphs; cited, not checked)

Let G be connected, locally finite and infinite, with Tseitin law T(G, c).

- **Over all solutions.** The solutions form a coset of the space of all
  even-degree edge sets.
  - By Theorem 1 of `HOLES-AT-INFINITY-20261020-001B-P001`, a parity of
    finitely many edges is constant exactly when its support is a finite cut
    with a finite side.
  - The Lemma's argument, applied to finite projections, then makes the
    finite circuits the minimal nonempty finite cuts E(A) with A finite. A
    constant edge lies in none.
  - A finite bond with infinitely many vertices on both sides is
    unconstrained. Its openness is supplied by the ends. On the double ray,
    for example, no single edge is constrained, and the circuits are the ties
    formed by pairs of edges.
- **Within one class of finitely different solutions.**
  - The changes inside a class are the finite even-degree edge sets. A finite
    edge set meets all of them evenly exactly when it is a finite cut: its
    two sides can be read off by parity along paths.
  - So the circuits are the finite bonds. A bridge is constant.
  - This is the finite-bond matroid. Bruhn and Diestel show that its dual has
    as circuits the edge sets of circles in the Freudenthal compactification
    |G|, which may pass through ends.
- **The gauge law.** In both readings its circuits are the finite cycles,
  because Proposition 2's argument concerns finite sets. Its dual, by Bruhn and
  Diestel, has all bonds, finite and infinite, as circuits.

So on infinite graphs the two laws are in general no longer dual. Within a class of
finitely different solutions, the Tseitin law's knots are dual to the circles
through the ends. Over all solutions, the ends make some finite bonds open.
This proof does not choose between the readings. The source-aware reading
adopted on 2026-10-20 keeps all solutions and marks which knots are native; it
is not the same as fixing one class.

## Remark 8 (most laws carry no graph)

**Counting.**
- There are at least 2^{k(m−k)} binary codes of dimension k on m labelled
  coordinates.
- A graph with m labelled edges and no isolated vertex has at most 2m
  vertices. So there are at most (2m)^{2m} such graphs, and at most twice
  that many cut spaces and cycle spaces.
- For k = ⌊m/2⌋, the fraction of codes that are graphic or cographic is at
  most 2 · 2^{2m log₂(2m) − ⌊m/2⌋⌈m/2⌉}, which tends to 0.

So almost every parity law with a balanced number of independent constraints
carries neither a graph nor a sphere.

**Limits.**
- The count does not cover local laws, which are a sparse family.
- For them there is only census C: among 240 random local laws, 13 had
  3-connected knot matroids, and 1 of the 13 carried a graph (the sphere law).

## Census observations

- **A** (exploratory).
  - **S1.** All 39 three-connected roster graphs were recovered exactly from
    both their gauge and Tseitin allowed states, under three scrambled
    presentations each.
  - **S2.** Four twists left the allowed states identical.
  - **S4.** Gauge laws over Z₃ and S₃ have the cycles as circuits.
  - **S3** failed because the producer labelled six planar random cubic graphs
    non-planar. The dual reading succeeded on them, as Theorem 4 requires, and
    failed on all 12 genuinely non-planar graphs.
  - **S5** was vacuous: no sampled law with every variable in three
    constraints had a 3-connected knot matroid.
- **C** (exploratory).
  - **T1.** On 40 three-connected graphs whose planarity search terminated
    (25 planar), the dual reading succeeded exactly on the planar ones. This
    is Theorem 5(c) at work.
  - **T2** was refuted, as stated in Remark 8.
  - **Ledrappier's law.** On L×L tori for L = 3, …, 8, its allowed states have
    dimension 2, 0, 0, 4, 6 and 0. These are degenerate, and no space can be
    read.

## What this does not show

- **Scope.** Only parity laws are covered, plus gauge laws over any group
  through Proposition 2. A law whose circuits fail elimination has no knot
  matroid to read.
- **Below 3-connectivity** the reading as defined fails, and a 2-separated
  graph is determined only up to twists. Reading such graphs would need
  Tutte's decomposition into 3-connected pieces, which is not done here.
- **Frequency.** Nothing is claimed about how often local laws carry a graph,
  beyond census C's 13 three-connected laws. The count covers uniformly random
  codes only.
- **Infinite graphs.** The infinite remark is cited, not checked.
- **No protected structure.** The space read here is combinatorial. No
  composed topology in the protected sense is claimed, nor a contact network,
  native path, separation, metric, dimension or physical space. The parity
  knots are K1–K3 knots of their systems, but the complete contact gate is not
  checked.

## Checks

`check.py` runs in about 20 seconds and writes `result.json`. All checks pass,
and all controls are rejected.

- **Lemma.** On 40 random cosets of 4 to 9 variables, the brute-force circuits
  are the minimal supports of the dual code with at least two elements.
- **Proposition 2.**
  - On 56 gauge laws (14 random graphs, each over Z₂, Z₃, Z₄ and S₃), the
    circuits are the cycles.
  - On 14 Tseitin laws with random charges, they are the bonds.
- **Theorem 3.**
  - 30 random 3-connected graphs are recovered.
  - 8 Whitney twists of random 2-connected graphs have identical cut and cycle
    spaces and different stars.
- **Theorem 4.** The test set is K₄, the cube, the octahedron, W₆, the
  5-prism, the 5-antiprism, six stacked triangulations, and the sphere law.
  On each:
  - both readings succeed;
  - every edge lies in two faces;
  - every vertex's faces form one cycle;
  - the read graph is connected, and V − E + F = 2.
- **Theorem 5.**
  - All 80 random codes are spanned by their minimal supports.
  - The reading fails on F₇, F₇*, M*(K₅) and M*(K₃,₃), and succeeds on M(K₅)
    and M(K₃,₃).
  - On 40 random 3-connected codes (24 graphic), the reading agrees with an
    exhaustive search for a graph realization. The search looks for families
    of minimal supports that cover each coordinate twice and span the code.
- **Census agreement.**
  - A's S1, S2 and S4 and C's T1 hold.
  - The realization search confirms the graphic and cographic verdicts of all
    13 three-connected local laws of C.
- **Controls:**
  - "reading from all minimal supports": it fails on the cube;
  - "the allowed states determine the graph exactly": refuted by the twists;
  - "the reading needs no 3-connectivity": it fails on two K₄'s glued along
    an edge;
  - "a law written on no graph carries none": refuted by the sphere law.
