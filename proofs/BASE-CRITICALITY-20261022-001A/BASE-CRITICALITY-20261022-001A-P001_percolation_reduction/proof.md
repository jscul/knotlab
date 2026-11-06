# Fair distinctions make percolation

Status: Proved

Ticket `BASE-CRITICALITY-20261022-001A`, 2026-10-22. It uses
`EMERGENCE-BITS-20261021-001B-P001` ("the accounting proof"). That proof
shows:
- the emergence of a network with hidden joints is minus log₂ of the chance
  that it is consistent;
- not-all-equal networks on bipartite graphs hold nothing;
- the recolouring holds on square tori.

It cites:
- **Random orientations:** Grimmett, "Infinite paths in randomly oriented
  lattices", *Random Structures & Algorithms* 18 (2001). The coupling with
  bond percolation at 1/2 is recorded by Zhelezov (*J. Stat. Phys.* 153,
  2013).
- **Bond percolation:** Kesten (1980), p_c(Z²) = 1/2, with exponential decay
  below it; Menshikov (1986) and Aizenman and Barsky (1987), sharpness;
  Wierman (1981), the honeycomb threshold 1 − 2 sin(π/18) ≈ 0.6527.
- **Crossing estimates:** Russo (1978) and Seymour and Welsh (1978), the
  crossing bounds at 1/2; Harris (1960), positive correlation.
- **Supercritical facts:** a supercritical boundary vertex has an arm to
  every distance with probability bounded below; Grimmett, *Percolation*
  (1999), chapters 7 and 11.
- **Two-literal instances:** limited backtracking (Even, Itai and Shamir
  1976).

## Standard statement

Let G be a finite multigraph. Give each edge e = uv a uniformly random bit
x_e, and ask for bits h on the vertices with ¬(h_u = h_v = x_e) on every
edge.
1. **Recolouring.** For any two-colouring g of the vertices, the substitution
   τ = h ⊕ g turns the system into an equivalent instance of two-literal
   clauses:
   - on every bichromatic edge, an implication whose direction is uniform;
   - on every monochromatic edge, a monotone clause (τ_u ∨ τ_v or
     ¬τ_u ∨ ¬τ_v) whose sign is uniform;

   all independent.
2. **Reach is percolation.** In a uniformly random orientation, the set
   reachable from any vertex set A has the law of A's bond-percolation
   cluster at p = 1/2. If every edge is replaced by an independently oriented
   two-terminal gadget, the reachable vertices of the base graph form
   percolation at the gadget's traversal probability.
3. **Blocking.** Suppose the monochromatic edges join two disjoint vertex sets
   T and B. If no directed path runs from B to T, or none from T to B, the
   system is satisfiable. So its satisfiability probability is at least the
   probability that percolation does not connect B to T.
4. **Three regimes.** On tori of a planar lattice cut along a monochromatic
   dual cycle, at fixed shape, the satisfiability probability:
   - tends to 1 when the traversal probability is below the lattice's bond
     threshold;
   - stays bounded away from 0 on the square lattice with plain edges;
   - tends to 0 when gadgets traversable both ways percolate.

## Nearest known result

- **(1)** is the classical gauge transformation between antiferromagnets and
  ferromagnets on bipartite graphs, read as implications.
- **(2)** is the coupling behind "no infinite oriented path at p = 1/2" in
  Grimmett's model. Here it is stated for any graph, source set and gadget,
  with the same exploration proof.
- **Random two-literal instances** are known to be governed by percolation of
  their implication digraph on random graphs (Chvátal and Reed 1992;
  Bollobás, Borgs, Chayes, Kim and Wilson 2001). A bounded search found no
  lattice or torus version.
- **(4)** applies standard percolation theorems.

Novelty: `known-overlap-found` for (1) and (2). The delta is
`candidate-local-delta`:
- the reduction of not-all-equal worlds, and so of their emergence at scale,
  to percolation at an effective parameter;
- the blocking theorem and the failure of its converse;
- the three regimes.

## Definitions

- **World.** G, the spokes x, the joints h and the constraints above. Its
  **emergence** is E = −log₂ P(consistent); for simple graphs this is the
  logical emergence of the visible relation (accounting proof).
- **Seam.** Fix a colouring g. The **seam** is the set of monochromatic edges,
  and the **cut graph** G° is G with the seam removed. The seam's **sides**
  are vertex sets T and B with every seam edge joining T to B.
- **Crossings.** An **up-crossing** is a directed path in G° from B to T, and a
  **down-crossing** one from T to B.
- **Gadget.** A finite graph with two terminals whose edges are oriented
  independently and uniformly.
  - **Traversal probability:** p = P(one terminal reaches the other), the
    same both ways by reversal symmetry.
  - **Two-way probability:** p^↔ = P(both).
  - **Series and parallel.** A series of blocks of k₁, k₂, … parallel edges
    has p = Π(1 − 2^(−kᵢ)). k parallel edges have p^↔ = 1 − 2^(1−k).

## Theorem 1: recolouring

For any g, h ↦ τ = h ⊕ g is a bijection of joint assignments, and each
constraint becomes:
- **on a bichromatic edge (g_u ≠ g_v):** τ_u ⇒ τ_v when g_u = 1 − x_e, and
  τ_v ⇒ τ_u otherwise (an arc from the endpoint whose colour differs from
  the spoke);
- **on a monochromatic edge (g_u = g_v):** τ_u ∨ τ_v when x_e = g_u, and
  ¬τ_u ∨ ¬τ_v otherwise.

Each spoke value gives each form once, so with uniform spokes the directions
and signs are uniform and independent.

*Proof.*
- **Bichromatic edges.** If g_u ≠ g_v, then h_u = h_v exactly when
  τ_u ≠ τ_v. The forbidden pattern h_u = h_v = x_e becomes
  (τ_u, τ_v) = (c, 1 − c) with c = x_e ⊕ g_u, which is an implication.
- **Monochromatic edges.** If g_u = g_v, the forbidden pattern becomes
  τ_u = τ_v = x_e ⊕ g_u, which is a monotone clause. ∎

*Check.* On C₅, K₄, the prism, the 3 × 3 torus and a 3 × 2 torus with a
double edge:
- for three colourings each (constant, alternating, random) and every spoke
  pattern, the world and its recoloured instance agree, 786,432 of 786,432
  cases on the 3 × 3 torus and all cases on the others;
- every edge takes both forms.

## Theorem 2: reach is percolation

Let H be a finite multigraph, each edge e replaced by a gadget with traversal
probability p_e, all orientations independent and uniform. For any A ⊆ V(H),
the set of vertices of H reachable from A has the law of the open cluster of
A in independent bond percolation on H with edge probabilities p_e. With
plain edges, p_e = 1/2.

*Proof.* Explore the reachable set.
- **The exploration.** Repeatedly pick a gadget with exactly one terminal w
  reached, and test whether w reaches the other terminal inside the gadget.
- **Each gadget is tested once.** Its internal vertices connect only through
  its terminals, so before its second terminal is reached its only entrance
  is w. If the test fails and the other terminal is reached later, the gadget
  can no longer add a vertex of H. So each gadget is tested at most once, in
  one direction.
- **The tests are percolation.** Each test succeeds with probability p_e,
  independently of everything revealed before. The exploration of a
  percolation cluster tests each edge once with the same probabilities, and
  maps outcomes to final sets in the same way. ∎

*Check.*
- **Plain edges.** On the 2 × 3 grid, K₄ and a 3 × 2 cylinder (from its bottom
  row), the reachable set over all orientations and the percolation cluster
  over all edge subsets have identical distributions.
- **Gadgets.** On a triangle and a 4-cycle with parallel pairs, parallel
  triples, a series of three edges and a series of three parallel pairs, the
  distributions agree exactly in rational arithmetic with percolation at
  3/4, 7/8, 1/8 and 27/64.
- **Gadget probabilities.** The two-way probabilities are 1/2, 3/4, 0 and
  1/8.

## Theorem 3: blocking

If the seam's sides T and B are disjoint and there is no up-crossing, the world
is consistent. Likewise if there is no down-crossing. Consequently:
- **Two-way crossings are needed.** An inconsistent world has directed
  crossings both ways.
- **A percolation bound.** P(consistent) ≥ 1 − P_perc(B ↔ T in G°), at the
  effective parameter of Theorem 2.

The converse fails: worlds with crossings both ways can be consistent.

*Proof.*
- **The witness.** Let U be the set reachable from B in G°. It is closed under
  the arcs, so τ = 1 on U and 0 elsewhere satisfies every implication.
- **The seam holds.** With no up-crossing, U contains B but no vertex of T. So
  every seam edge has (τ_t, τ_s) = (0, 1), which satisfies both monotone
  clauses.
- **The other direction.** Swap the roles of T and B for down-crossings.
- **The bound.** P(no up-crossing) = P_perc(B not connected to T in G°) by
  Theorem 2. ∎

*Check.* On the cut-open 3 × 2 and 5 × 2 tori (every spoke pattern: 4,096 and
1,048,576) and the 3 × 4 torus (200,000 sampled):

| Torus | Blocked one way, all consistent | Crossed both ways | ... of which consistent |
| --- | --- | --- | --- |
| 3 × 2 | 3,200 | 896 | 554 |
| 5 × 2 | 1,004,672 | 43,904 | 27,098 |
| 3 × 4 (sampled) | 70,906 | 129,094 | 58,297 |

## Theorem 4: the three regimes

**The setting.**
- **The lattice.** A planar periodic lattice whose faces are all even, a
  sequence of its tori, non-bipartite, at a fixed shape and growing size n.
- **The colouring.** Each torus has a colouring g whose seam is one dual cycle
  in the odd class, so G° is a cylinder whose sides B and T are at lattice
  distance at least c·n, with circumference at most C·n.
- **The gadgets.** Every edge carries the same gadget, with traversal
  probability p and two-way probability p^↔.

**(a) Below the threshold: emergence vanishes.** If p < p_c of the lattice,
then P(consistent) ≥ 1 − |B|·e^(−cn/ξ(p)) → 1, so E → 0 exponentially fast.
- **The honeycomb** with plain edges qualifies: 1/2 < 0.6527.
- **So does the square lattice** with a series of three edges (1/8), or a
  series of three parallel pairs (27/64).

*Proof.* By Theorem 3 and exponential decay below p_c,
P_perc(B ↔ T) ≤ Σ_{x∈B} P(x reaches distance cn) ≤ |B| e^(−cn/ξ). ∎

**(b) At the square lattice's threshold: emergence stays bounded.** For plain
edges on square tori of fixed shape, P(consistent) ≥ c(shape) > 0 for every
size, so E ≤ log₂(1/c(shape)).

*Proof.*
- **Duality.** B not connected to T in the cylinder is the event that a dual
  circuit winds around it.
- **Crossing bounds.** At 1/2 the dual is again critical bond percolation. The
  crossing bounds give each of a fixed number of overlapping boxes of fixed
  aspect ratio, laid around the circumference, a crossing with probability at
  least c₀. Positive correlation glues them into a winding circuit.
- **Uniformity.** The number of boxes depends only on the shape. ∎

**(c) When two-way gadgets percolate: emergence diverges.** On square tori of
fixed shape with one odd side and k ≥ 3 parallel edges per gadget
(p^↔ = 1 − 2^(1−k) ≥ 3/4 > 1/2), P(consistent) → 0, so E → ∞.

*Proof.*
- **Two-way clusters are rigid.** The two-way gadgets form independent
  Bernoulli(p^↔) percolation on the cut cylinder. Each of its clusters is
  strongly connected, so τ is constant on it.
- **The seam gadget.** At a seam column m it is k parallel monotone clauses of
  independent uniform signs. With both signs present (probability
  1 − 2^(1−k)) it forbids τ_t = τ_s.
- **The count.** Let K be the number of seam columns whose two endpoints lie
  in one two-way cluster. Given the orientations,
  P(consistent | K) ≤ 2^((1−k)K).
- **K grows.** Take L = ⌈C log n⌉ and seam columns spaced 2L + 1 apart, about
  b/(2L+1) → ∞ of them.
  - "Both endpoints have two-way arms of length L inside their own boxes" is
    independent across these columns, with probability at least θ_∂(p^↔)² > 0
    each.
  - With high probability all two-way clusters of diameter at least L are one
    cluster: two of them are separated only by a dual path of length at least
    L, which has probability at most O(n²)·e^(−c′L) at the subcritical dual
    parameter 1 − p^↔.
  - So K → ∞ in probability, and P(consistent) ≤ P(K < M) + 2^((1−k)M) → 0
    for every M. ∎

**What is not proved.**
- **Two cases.** Parallel pairs (p^↔ = 1/2) and cubic 3-tori (no two-way
  edges) diverge in the experiment; no proof is given here.
- **The lower bound at criticality is open.** It would show that emergence
  stays bounded away from 0 on square tori.
  - **Why it is hard.** Inconsistency needs crossings both ways (Theorem 3),
    and given them a world stays consistent with probability bounded away
    from 0 and 1 at every tested size. A proof must control the joint law of
    forward and backward reach, and Theorem 2 controls only one direction at
    a time.

## What this means (interpretation, not theorem)

- **The parameter 1/2 is the fairness of the visible distinctions.**
  - **Why.** Recoloured, a fair spoke orients its hidden implication by a
    coin flip, and reach through coin-flipped implications is percolation at
    exactly 1/2.
  - **On the square lattice** 1/2 is the bond threshold (self-duality), so
    the global emergence of a not-all-equal world sits at a critical point.
    That is why it is the same at every size.
- **One number sets the phase:** the chance that a contact passes an
  implication on.
  - **Below threshold** (honeycomb; contacts in series), global emergence
    vanishes.
  - **At it** (the plain square lattice), it is scale-free.
  - **Above it, with two-way contact,** it diverges.
- **Which lattice is critical depends on how it is declared.** No law here
  creates the lattice. The program's guardrail still applies: these are
  declared surfaces, and nothing is said about space.

## Scope

- **Assumptions.** Finite checks support the exact statements. The asymptotic
  regimes rest on the cited percolation theorems.
- **What is covered.** Tori and their decorations only. The lower bound at
  criticality is open.
