# The depth of a charge hole

Status: Proved

Ticket `DEEP-HOLES-20261020-001B`, 2026-10-20. The proofs are in prose.
`check.py` builds the certificate that each proof describes and verifies it
by substitution into equations rebuilt from scratch. It covers two rosters:
- **The census networks.** All 30 charge networks of the exact census
  `DEEP-HOLES-20261020-001A-E001`: parity (Z₂) networks on every connected
  cubic graph with at most 8 vertices under three charge placements, and
  sum-mod-3 (Z₃) networks on K₄, K₃,₃ and the prism under two.
- **Ten-vertex graphs.** Parity networks on all 19 connected cubic graphs with
  10 vertices:
  - the sweep refutation is verified on every graph;
  - the Fourier solution is checked for consistency on every graph and on 300
    random equations each;
  - on the graph where it matters most, the solution is verified on every
    equation.

Three broken certificates are rejected as controls.

## Setting

- **Charge network.** Take a connected graph G = (V, E) with its edges
  oriented, and a prime p.
  - Each edge carries a distinction with values in Z_p.
  - Each vertex v carries a knot on its incident edges: out-flow minus
    in-flow equals the charge c(v).
  - The network is impossible exactly when the total charge c(V) is nonzero.
    That is a nonzero class in the reduced homology H̃₀(G; Z_p).
  - For p = 2 this is a Tseitin formula.
- **The relaxation.** The level-k affine relaxation over a ring R has a
  variable z[S, f] for every set S of at most k edges and every assignment f
  of S that satisfies the knots whose edges all lie in S.
  - Its equations are z[∅] = 1 and z[S, f] = Σ z[S + e, f'], summed over the
    extensions f' of f.
  - L_R is the least k at which no solution in R exists.
- **Cuts and the toggle width.** δ(U) is the set of edges leaving a vertex set
  U.
  - A toggle path is a sequence of vertex sets from ∅ to V, each obtained
    from the previous one by adding or removing one vertex v. The step costs
    |δ(U) ∪ star(v)|, where U is the set before the step.
  - The **toggle width** tgw(G) is the least k such that some toggle path has
    every step cost at most k.

## 1. The plain hole criterion is stuck at level 2

Let S be the scope of one knot on three distinctions, with no other knot
inside S. Let Δ_S be the complex of partial assignments to subsets of S that
the knot allows.

**Claim.** For a Boolean knot with excluded set E, H̃₁(Δ_S; K) has rank
|E| − 1 over every field K. So every knot that excludes two or more states
is a hole at its own scope: parity, not-all-equal, and all but the atoms
among the 34 two-loop knots. The sum-mod-3 knot's hole has rank 10.

**Proof.**
- **The full complex.** With nothing excluded, Δ_S is the join of three
  two-point sets, the octahedral 2-sphere J.
- **Removing excluded faces.** Removing the |E| excluded triangles kills the
  sphere's single 2-cycle, since every coefficient of that cycle is ±1.
  Without the 2-cycle, the |E| − 1 further removals each open a 1-cycle.
- **In general**, by the long exact sequence of the pair (J, Δ_S),
  H̃_{|S|−2}(Δ_S) is the cokernel of the restriction map from the top cycles
  of J to K^E.
  - For two values per distinction, the top cycles are the multiples of the
    parity character, so the image has rank 1. ∎

**Consequence.** Moments can always be extended through sets without holes
(the cycle-filling argument of `HOLE-CRITERION-COLOURING-20261019-001`).
But every scope of a parity, sum-mod-3 or not-all-equal network has a hole.
The criterion therefore certifies only L > 2, which says nothing: bags of two
edges contain no knot.

## 2. Rings that compute in the charge group see the hole at once

**Claim.** If R has characteristic p, or R = Z, then L_R is at most the
maximum degree, and exactly 3 on cubic graphs.

**Proof.**
- **The certificate.** In the bag of v's star, every allowed assignment has
  out-flow c(v). Marginalizing, Σ_{e ∋ v} ±μ_e = c(v)·z[∅] in R, where
  μ_e = Σ_a a·z[{e}, a] is read in R.
- **Summing.** Over all v, each edge appears twice with opposite signs, so
  0 = c(V)·z[∅] = c(V), which is nonzero in R.
- **Integers.** The same combination refutes over Z modulo p.
- **Lower bound.** Bags with fewer edges than a star contain no knot, so
  lower levels accept. ∎

## 3. Every other field sees it exactly at the toggle width

**Claim.** If K is a field in which p is invertible, then L_K = tgw(G), for
every charge placement with c(V) ≠ 0.

### Upper bound: the sweep (valid over every ring)

Take a toggle path whose steps cost at most k.
- **Flux.** For an assignment g of δ(U), let flux_U(g) be the net out-flow
  of g across δ(U).
- **One step.** Let v be the vertex toggled from U to U'. In the bag
  S = δ(U) ∪ star(v), of at most k edges, v's knot lies inside. So every
  allowed f has flux_{U'}(f) = flux_U(f) ± c(v), with the sign depending on
  whether v enters or leaves.
- **The step identity.** Marginalizing from S to δ(U) and to δ(U') gives the
  identity F_{U'}(t ± c(v)) = F_U(t), where F_U(t) sums z[δ(U), g] over the g
  with flux t. It is a combination of equations with coefficients ±1.
- **Telescoping.** Along the path, F_∅(0) = z[∅] is carried to F_V(c(V)).
  Since δ(V) = ∅ and c(V) ≠ 0, that is an empty sum. So z[∅] = 0, against
  z[∅] = 1.

The refutation has integer coefficients, so it refutes over every ring.
`check.py` builds it along an optimal path for every network and confirms
that no equation it uses involves more than tgw(G) edges.

### Lower bound: a solution in closed form below the toggle width

Let k < tgw(G), and let ζ be a primitive p-th root of unity, adjoined to K if
needed.

- **Reachable labellings.** A labelling u: V → Z_p is reachable if it can be
  reached from 0 by changing one vertex at a time, each change of v costing
  |supp δu ∪ star(v)| ≤ k.
  - If u and u + a·1 were both reachable with a ≠ 0, the vertices labelled a
    along the way would form a toggle path from ∅ to V of cost at most k.
    That is impossible.
  - So each cut γ = δu has at most one reachable representative. Put
    h(γ) = ζ^{−⟨c, u⟩} for that representative, and h(γ) = 0 when there is
    none. Then h(0) = 1.
- **The relation.** Let w be supported on vertices whose stars lie in a bag S
  of at most k edges, with γ ⊆ S. Changing w one vertex at a time stays
  inside S, so h(γ + δw) = ζ^{−⟨c, w⟩}·h(γ).
- **The solution.** For every bag S with |S| ≤ k and allowed f, define

  z[S, f] = p^{−|S|} · Σ_{cuts γ ⊆ S} h(γ) · ζ^{−⟨f, γ⟩}.

  Then z[∅] = h(0) = 1. Take an extension from S to S + e:
  - **No new knot inside.** The character sum over e's value keeps exactly
    the cuts that avoid e.
  - **One endpoint's knot completed.** Pair the cuts in cosets of
    {a·δ1_v}. The relation and v's knot make all terms of a coset equal, and
    each coset has exactly one cut avoiding e.
  - **Both endpoints' knots completed.** If the two knots are compatible, the
    same pairing works. If they are not, then f has no extension. The
    character sum over the subgroup {a·δ(1_u + 1_v)} ⊆ cuts(S) vanishes, so
    z[S, f] = 0, as the equation requires.
- **Back to K.** The values lie in K(ζ). Applying the trace with a scalar of
  trace 1 gives a solution in K, because the equations have integer
  coefficients:
  - over Q or F₅ with p = 3, (z + z̄)/2;
  - over F₂ with p = 3, Tr(ζ·z).
  `check.py` builds this solution at level tgw(G) − 1 for every network over
  Q, F₃ and F₅ (parity) and Q, F₂ and F₅ (sum mod 3), and verifies every
  equation. ∎

**Where the charges sit does not matter.** The toggle width depends only on
G.

## 4. The toggle width and cutwidth

**Claim.** For a connected cubic graph on at least 4 vertices, the monotone
toggle width (vertices only added) equals cutwidth + 1.

**Proof.** When v is added to U with d neighbours in U, the step costs
|δ(U)| + 3 − d = |δ(U + v)| + d.

- **Upper bound.** Run along an ordering with every prefix cut at most cw.
  A step with d = 0 or 3 costs at most cw, and one with d = 1 or 2 costs at
  most cw + 1.
- **Lower bound.** Take an ordering whose steps cost at most T.
  - Every step with d ≥ 1 leaves a prefix cut of at most T − 1.
  - A step with d = 0 can leave a cut of exactly T. Then the next vertex has
    d = 3, since its step also costs at most T.
  - Swapping the two vertices brings every prefix cut down to at most T − 1.
  - The first cut is 3 ≤ T − 1, since some step costs at least 5. ∎

**Monotonicity is observed, not proved.** On all 27 connected cubic graphs
with 4 to 10 vertices, letting vertices also leave never helps:
tgw = monotone tgw = cutwidth + 1. So on every one of them, the depth of a
charge hole over a field that cannot compute in the charge group is
**cutwidth + 1**.

**Signed reasoning can need more than the variable graph's treewidth + 1.**
The network's own variable graph is the line graph of G: two edges are
adjacent when they share a knot.
- On the 8 census graphs and on 18 of the 19 ten-vertex graphs, the line
  graph's treewidth equals the cutwidth.
- On the remaining ten-vertex graph it is 4 while the cutwidth is 5. There the
  depth is 6: the sweep refutes at 6, and the level-5 Fourier solution is
  verified on every equation.
- By the standard argument that glues local distributions along a tree
  decomposition, Sherali–Adams with nonnegativity refutes any impossible
  network by its variable graph's treewidth + 1, which is 5 on this graph.
  This is not computed here.
- So on this graph, signed linear reasoning needs one more level than
  nonnegative reasoning.

**It is not a function of treewidth.**
- Among the census graphs of treewidth 3, K₄, the prism and two 8-vertex
  graphs have depth 5, while K₃,₃, the cube and a third 8-vertex graph have
  depth 6.
- The Wagner graph, of treewidth 4, also has depth 6.

## What it means for knots and holes

- **Two kinds of network hole.**
  - Witnesses at vertices with contact on edges (`HOLES-COHOMOLOGY-20261019-001`)
    give loop holes. They are classes in H¹, seen by any reasoning that holds
    three witnesses, over every ring.
  - Distinctions on edges with knots at vertices give charge holes. They are
    classes in H̃₀.
- **Charge holes are shallow only for matched rings.** Arithmetic in the
  charge group sees one at the size of a single knot. Any other field must
  carry the charge across a cut. It sees the hole only once it can hold the
  widest cut of the best sweep together with one more vertex's star.
- **The program's plain hole criterion cannot see this.** Every non-atom knot
  is a hole at its own scope. The right measure of depth is the cut sweep,
  not the local holes.

## Nearest known results

- **Tseitin formulas over different characteristics.**
  - Tseitin formulas are easy over characteristic 2, by Gaussian
    elimination.
  - They need linear Nullstellensatz and polynomial-calculus degree over
    other characteristics on expanders (Grigoriev 2001; Buss, Grigoriev,
    Impagliazzo and Pitassi 2001).
  - The averaging-and-characters method used here is standard in those lower
    bounds.
- **Exact game characterizations.** Galesi, Talebanfard and Torán (SAT 2018;
  ACM TOCT 2020) characterize resolution width, depth and variable space of
  Tseitin formulas by a cops-and-robber game related to treewidth.
- **Treewidth and counting logics.** The CFI construction, which is Tseitin
  on a graph, defeats counting logics and Weisfeiler–Leman of dimension below
  the treewidth (Dawar and Richerby 2007). The Sherali–Adams connection is by
  Atserias and Maneva (2013).

**Novelty: known-overlap-likely** for the method and for statements 1–2. We
found no statement of the exact level of the affine relaxation for charge
networks over a field of the other characteristic, as the toggle width, nor of
its coincidence with cutwidth + 1 on cubic graphs.

## Nonclaims

- **No other relaxations.** No claim about Sherali–Adams with nonnegativity,
  Nullstellensatz or polynomial-calculus degree, or OR-combinations of charge
  networks.
- **Monotonicity is open.** That allowing vertices to leave never helps is
  observed on 27 graphs and not proved.
- **No native structure.** No claim is made about native structure, distance
  or physics.
