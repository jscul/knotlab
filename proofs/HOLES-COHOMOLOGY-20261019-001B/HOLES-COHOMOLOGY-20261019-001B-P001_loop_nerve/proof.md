# What permutation contact remembers: loops, nerves and knots among loops

Status: Proved

Ticket `HOLES-COHOMOLOGY-20261019-001B`, 2026-10-19. Statements 1–7 are
kernel-checked in `LoopNerve.lean` (Lean 4.32.2, core only, standard axioms;
`check.py` runs five controls that alter a statement, and the kernel rejects
each). Statements 8–11 are proved here in prose and agree with the exact
census `HOLES-COHOMOLOGY-20261019-001A-E001`.

## Setting

A **network** is a connected graph with a witness at every vertex, taking
values in a finite set W, and a copy of a link on every edge u → v. For each
value m of its middle variable, the link allows exactly the pairs
(w_u, w_v) with w_v = p_m(w_u), where p_m is a permutation of W. This is
**permutation contact**: given the middle value, the witness out is a function
of the witness in, and conversely. The **composite** is the relation on the
middle variables left after every witness is forgotten. A pattern is allowed
when some witness assignment satisfies every copy.

For a pattern, the **holonomy** of a closed walk at a vertex r is the
composed permutation along it. The holonomies of the closed walks at r form
the **holonomy group** H_r.

## Kernel-checked statements (`LoopNerve.lean`)

1. **Loop rule** (`loop_rule`). A loop of permutation contact closes exactly
   when the composed map has a fixed point. This is the ring case of the
   network rule, statement 8.
2. **Bouquet rule** (`bouquet_rule`). Take loops sharing one base witness.
   Each loop has a selector: unselected, its holonomy is the identity;
   selected, it is h_i. The bouquet allows a selector pattern exactly when the
   selected holonomies share a fixed point.
3. **The shape is the nerve** (`shape_is_nerve`). A set S of selectors is free
   (every pattern on S extends to an allowed pattern) exactly when the
   holonomies of S share a fixed point. So the shape of the selector composite
   is the nerve of the fixed-point sets Fix(h_i).
4. **Knots among loops are atoms** (`minimal_nonface_excludes_only_all`,
   `minimal_nonface_is_knot`). Let S be a minimal non-face: the holonomies of S
   share no fixed point, but they do once any one loop is left out. Seen on S,
   the composite excludes exactly one pattern, the one that selects every loop
   of S. So it is constrained (K1), unconstrained once any loop is forgotten
   (K2), and allows some state (K3).
   - With two loops this is a **tie**.
   - With three or more it is a **knot among loops**: any proper subset of the
     loops can be selected together, but not all of them.
   - Its excluded set is a single point, so it is the atom. It hides
     log₂(2^k/(2^k − 1)) bits, the least any knot hides.
5. **Free contact binds nothing** (`free_contact_binds_nothing`). Suppose
   every holonomy that fixes one value fixes all of them. Parity, addition
   mod q and every regular group action are like this. Then a minimal non-face
   has at most one loop, so free contact makes no ties and no knots among
   loops.
6. **A knot among k loops needs k + 1 values** (`knot_needs_more_values`,
   `star_is_knot`). Suppose k ≥ 1 permutations of n values are such that
   every k − 1 of them share a fixed point but all k do not. Then n ≥ k + 1.
   The star transpositions (j k), j < k, on k + 1 values achieve this.
   - Proof of the bound: pick p_j, fixed by every h_i with i ≠ j and moved by
     h_j. The p_j are distinct.
   - The point q = h_0(p_0) differs from every p_j. For j = 0 because h_0
     moves p_0. For j ≠ 0 because h_0 fixes p_j and is injective.
   - So k + 1 distinct values exist. Pigeonhole is proved in the file.
   - Corollaries (`three_loops_need_four_values`,
     `four_values_knot_three_loops`, `boolean_contact_never_ties`):
     - three loops cannot knot on three witness values, and (03), (13), (23)
       knot them on four;
     - with two witness values no two loops ever tie.
7. **Every complex is a nerve** (`every_complex_is_a_nerve`,
   `flip_involutive`). Let N be any family of sets of loops that is closed
   under subsets and contains the empty set.
   - On the values (F, b), where F is a set of loops and b a tag, loop i fixes
     (F, b) when F is in N and contains i. Otherwise it flips b.
   - Each such map is an involution.
   - A set S of loops shares a fixed point exactly when S is in N.
   - With statement 3, **every simplicial complex is the shape of a bouquet of
     loops with permutation contact.**

## Statements proved in prose

### 8. The network rule

**Claim.** A connected network allows a pattern exactly when the holonomy
group H_r has a common fixed point, at any base vertex r.

**Proof.** Fix a spanning tree T rooted at r, and let g_v be the composed
permutation along the tree path from r to v. A witness assignment determines
w_r, and the copies on tree edges then force w_v = g_v(w_r) for every v.
Conversely, any value w_r propagates this way to an assignment that satisfies
every tree copy.

A non-tree edge e = u → v is then satisfied exactly when
p_e(g_u(w_r)) = g_v(w_r), that is, when w_r is fixed by the fundamental
holonomy h_e = g_v⁻¹ p_e g_u. The fundamental holonomies generate H_r. So the
pattern is allowed exactly when some w_r is fixed by all of them, that is, by
H_r.

Changing the base vertex conjugates H_r, which preserves "has a common fixed
point". ∎

**Equivalent covering form.**
- The label-extended graph has vertices (v, w), and an edge
  (u, w) — (v, p_e(w)) for each copy.
- It is a |W|-sheeted covering of the network.
- A pattern is allowed exactly when some component of this covering meets
  every vertex once: a sheet that closes up.
- The H_r-orbits are the components' intersections with the fibre over r. The
  census's independent checker uses this form.

**Reduction to a bouquet.** By the proof, every network behaves like the
bouquet of its fundamental loops. With selectors on the non-tree edges,
statements 2–7 apply to any network.

### 9. Free abelian contact: one class in H¹ per loop

Let the contact be a group Γ acting regularly on itself, written additively,
so that each edge carries a value c_e ∈ Γ and w_v = w_u + c_e.
- The holonomy of a cycle Z is translation by ⟨c, Z⟩ = Σ_{e ∈ Z} ±c_e. It has
  a fixed point exactly when ⟨c, Z⟩ = 0.
- By statement 8, a pattern is allowed exactly when ⟨c, Z⟩ = 0 for every
  cycle Z. That is, the class [c] ∈ H¹(G; Γ) = Hom(H₁(G), Γ) ≅ Γ^{b₁}
  vanishes, where b₁ = E − V + 1.
- Each of the b₁ independent loops contributes one independent condition.
  With uniform edge values exactly |Γ|^{−b₁} of the patterns are allowed.
- For Γ = Z/2 this is one bit per loop, the parity-network result of
  `KNOT-LOOPS-20261019-001C-E001`, read as the vanishing of a Z/2 class in H¹.

**Non-free, non-abelian contact.**
- A pattern determines its fundamental holonomies (h_1, …, h_{b₁}) only up to
  simultaneous conjugacy, by changing the gauge at r. This is the
  non-abelian H¹(G; Sym(W)) = Hom(π₁(G), Sym(W))/conjugation.
- The composite asks whether that class has a common fixed point.
- This is not a function of the individual conjugacy classes. In S₄, the pairs
  ((03), (13)) and ((03), (12)) consist of transpositions. The first shares
  the fixed point 2; the second shares none. So a network's composite records
  how its loops' holonomies sit relative to one another, not just what each
  one is. Under free contact a holonomy has a fixed point only when it is the
  identity, so the composite is a function of the individual classes.
- The census (P6) finds such type-ambiguous pairs for S₃ and S₄ links on
  two-loop networks, and none for Z₂ and Z₃.

### 10. Memory of uniform group contact depends only on the number of loops

Let every edge value be uniform on a permutation group G ≤ Sym(W), each value
naming itself.
- Conditionally on the tree edges, each fundamental holonomy
  h_e = g_v⁻¹ p_e g_u is a bijective image of p_e. So h_e is uniform on G, and
  independent across non-tree edges.
- By statement 8 the allowed fraction is the probability that b₁ independent
  uniform elements of G share a fixed point. By inclusion and exclusion over
  the sets T of shared fixed points:

  allowed fraction = Σ_{∅ ≠ T ⊆ W} (−1)^{|T|+1} (|G_T| / |G|)^{b₁},

  where G_T fixes T pointwise.
- It depends on the network only through b₁:
  - for free G it is |G|^{−b₁};
  - for S₃ on three values it is 3^{1−b₁} − 2·6^{−b₁}, that is 2/3, 5/18 and
    11/108 for one, two and three loops.
- The census confirms the formula on 38 graph–group pairs, and confirms that
  graphs with equal b₁ give equal fractions.
- With S₃ the loops bind. Two loops keep log₂(18/5) ≈ 1.85 bits, more than
  twice the log₂(3/2) ≈ 0.58 bits of one loop. The extra log₂(8/5) ≈ 0.68
  bits come from ties (statement 4): in 3/18 of the patterns each loop closes
  alone but the two do not close together.

### 11. Smaller realizations and the stars

- **Facet construction.** The census realizes each complex on fewer values.
  Take W = (facets) ∪ {x, y}, and let h_i be one cycle through the facets
  missing i together with x and y. Then Fix(h_i) is the set of facets
  containing i, so the nerve is the complex. Every one of the 193 complexes on
  at most four labelled vertices is realized this way (census P4a).
- **Knots among three loops on four values are exactly the stars.**
  - A non-identity permutation of four values fixes at most two of them.
  - If one of the three fixed-point sets has a single point, the pairwise
    intersections force that point into all three.
  - So all three fixed-point sets are pairs, and the holonomies are
    transpositions.
  - Two transpositions share a fixed point exactly when they share a moved
    point. Three that pairwise share one and cover all four values form a
    star.
  - That gives 4 centres × 3! orders = 24 tuples, which is the census count
    for k = 3, n = 4.

## What it means for knots and holes

- **Loops held by free contact are recorded independently.** Parity,
  addition mod q and every regular action keep one class per independent loop.
  A minimal non-face is then a single loop that cannot close, never a tie and
  never a knot. This is the H¹ of the network with coefficients in the
  contact group.
- **Loops held by non-free contact can bind, into any shape.** The shape of
  the loop selectors is the nerve of the holonomies' fixed-point sets, and
  every simplicial complex occurs. Its holes are holes of that nerve. Its knots
  among loops are atoms: any proper subset of the loops can be on together,
  but not all of them.
- **Binding costs witness values.** A knot among k loops needs k + 1 values.
  Boolean contact cannot even tie two loops, three values can tie two loops,
  and three loops need four values.

## Nearest known results

- **Bijection constraints.** Systems of bijection constraints on a graph are
  the satisfiable side of Unique Games. Their label-extended graph is the
  covering of statement 8, and satisfiability by propagation from one vertex
  is folklore.
- **Nerves.** Every simplicial complex is the nerve of a family of finite
  sets. The fixed-point version needs only a permutation that fixes a given
  set and moves the rest.
- **Holonomy and H¹ of graphs** with abelian and non-abelian coefficients are
  classical. So are coverings of graphs.

**Novelty: known-overlap-likely** for statements 1–3, 5 and 8–10. For
statements 4, 6, 7 and 11 the mathematics is elementary and we found no
statement of it: knots among loops as atoms, the k + 1 bound with stars, and
nerves of fixed-point sets as selector shapes. The program's reading is new.
Free contact records loops one by one. Only contact with fixed points binds
loops, and it binds them into atoms.

## Nonclaims

- **Hand-made networks.** The networks and selectors here are laid out by
  hand. Nothing is claimed about a law that makes them.
- **No topology or distance.** No claim is made about native recurrence,
  composed topology, paths, distance, space or physics.
- **No complexity result.** Statements about local reasoning are in
  `HOLES-COHOMOLOGY-20261019-001C-P001`.
