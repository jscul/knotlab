# How emergence adds up

Status: Proved

Ticket `EMERGENCE-BITS-20261021-001B`, 2026-10-21. It uses:
- `EMERGENCE-BITS-20261021-001A-P001` ("the measures proof"): logical
  emergence E, statistical emergence I, knots as complements of independent
  sets;
- `KNOT-LOOPS-20261019-001B-P001` ("the ring theorem", Lean):
  - a ring excludes a pattern exactly when every transfer is a permutation
    and an odd number swap;
  - a link's transfers are all permutations exactly when it is a parity
    relation;
- `LOOP-HOMOLOGY-20261021-001A-P001`: the full-product dichotomy for rings of
  any number of values (Protasov–Voynov);
- `BASE-THREE-20261021-001B-P001`: a law on bits keeps lasting memory exactly
  when every polymorphism is affine. This uses one fact from Post's lattice:
  a clone with a non-affine operation contains conjunction, disjunction or
  majority;
- `KNOT-COMPETITION-20261019-001A-P001`, part (iii): with hidden variables,
  least sets of pairwise energies project onto every relation.

It also cites:
- the Galois connection between polymorphisms and pp-definable relations;
- limited backtracking for two-literal instances (Even, Itai and Shamir
  1976; Aspvall, Plass and Tarjan 1979).

## Standard statement

Relations are nonempty subsets of {0,1}^n, and E(R) = log₂|pc(R)| − log₂|R|
for the pair closure pc. Then:
1. **Joins.** Let R and S have all two-coordinate projections full. Their
   natural join at one shared coordinate e satisfies
   E(R ⋈ S) = E(R) + E(S) − log₂(1 + β_R β_S), where β is the mean of ±1 at e.
2. **Projections.** Majority-closed relations are closed under projection.
   Facial sets of the pairwise model are not: a cyclic join of three copies
   of {000, 011, 101} is facial, and its projection is even parity.
3. **Rings and chains.** Read a relation whose one-coordinate-deleted
   projections are full as a family of 2×2 Boolean matrices. The fraction of
   cyclic products with zero trace is ((a+b)^m − (a−b)^m)/2, where a and b are
   the shares of identity and swap matrices. The expected number of zero
   entries of a random product is 2 for parity and decays geometrically
   otherwise.
4. **Long knots in a law.** In a Boolean constraint language whose
   polymorphisms are all affine, even parity of every even length at least 4
   is pp-definable. Otherwise every pp-definable relation with full
   one-deleted projections excludes at most N of its 2^N points.
5. **Networks.** Place such a relation L(h, x, h') on every edge of a simple
   graph G. Let V be the set of edge labellings x for which the induced
   binary constraint network on the vertices is satisfiable. Then:
   - |V| ≥ 2^(|E|−b₁(G)), with equality exactly when L is parity;
   - −log₂(|V|/2^|E|) is superadditive over edge-disjoint subgraphs;
   - V is everything when L has a constant common solution, and when L is
     not-all-equal and G is bipartite;
   - on a torus grid with an odd side, the substitution h ↦ h ⊕ (i+j mod 2)
     turns not-all-equal into uniformly random implications, plus monotone
     two-literal clauses on the seam.

## Nearest known result

- **(1)** is elementary counting for natural joins.
- **(2)** is standard. Relational clones are closed under projection.
  Projections of least sets of pairwise energies reach every relation (the
  gadget of Garey, Johnson and Stockmeyer 1976; competition proof part (iii)).
- **(3)** restates the ring theorem and the full-product dichotomy in bits.
  New here are only the exact emergence formulas for rings and chains.
- **(4)** is Post's lattice with the Galois connection. The shape of
  conjunction-closed knots is elementary.
- **(5)** is classical for parity: the visible relation is the space of
  coboundaries, of codimension b₁ (Tseitin 1968; cohomology of graphs).
  Satisfiability of the induced network is a two-literal problem. The
  checkerboard substitution is the usual gauge between antiferromagnets and
  ferromagnets on bipartite lattices. Random orientations of the square
  lattice are Grimmett's model (Grimmett 2001).

Novelty: `known-overlap-found` for (2) and (3). The delta is
`candidate-local-delta`:
- the cycle-rank bound with equality only for parity;
- superadditivity as emergence accounting;
- the long-knot dichotomy;
- the torus recolouring;
- the correction of an earlier small-graph summary (see "What this means").

## Definitions

- **Link.** A knot L on bits with two designated joints h, h'. The remaining
  coordinates are its spokes x. Its transfer for a spoke value x is the table
  M(x)[h][h'] = [L(h, x, h') holds].
  - A knot's one-deleted projections are full, so every transfer has no zero
    row and no zero column.
  - Over all spoke values, the transfers cover all four patterns.
- **Chain and ring.** Copies of a link joined joint to joint, with the inner
  joints forgotten. A chain keeps its end joints; a ring closes up.
- **Network.** A simple graph G with a link on every edge (oriented either
  way), joints at the vertices (forgotten), spokes visible. Its visible
  relation V is the set of spoke assignments that extend to the joints.

## Theorem 1: visible joins

Let R on X ∪ {e} and S on {e} ∪ Y have all two-coordinate projections full
(for example, knots). Let β_R and β_S be the means of (−1)^(1+e) under the
uniform distributions. Then the join T = R ⋈_e S has all pairs free, and

E(T) = E(R) + E(S) − log₂(1 + β_R β_S).

*Proof.*
- **Pairs are free.** Pairs inside R or S stay free, because the other
  factor accepts both values of e. A pair across them is free, because any
  value of e serves.
- **The count.** So pc(T) is the whole cube, and |T| = Σ_e |R_e||S_e| =
  |R||S|(1 + β_R β_S)/2. Take logarithms. ∎

So emergence adds exactly when the shared distinction is balanced in one of
the two knots. It gains when the two lean opposite ways and loses when they
lean the same way.
- **Chains.** A chain of knots kept fully visible holds the sum of their
  emergences, corrected at each joint.
- **Parity chains** add exactly one bit per knot.

*Check.* All 10,404 placements of two three-variable knots satisfy the
formula with every pair free, 3,600 of them with a nonzero correction.
Visible parity chains of 1–4 knots hold 1–4 bits.

## Theorem 2: forgetting

1. **Pairs never gain by forgetting.** Forgetting coordinates never creates
   logical emergence from clauses of at most two literals.
2. **Triples can,** even from a statistically silent part. The relation
   R₀ = {000, 011, 101} has E = log₂(4/3) and I = 0, since it is a least set
   of a pairwise energy. The system
   R₀(h₁,h₂,a) ∧ R₀(h₂,h₃,b) ∧ R₀(h₃,h₁,c) is a least set on all six
   variables, so its I is 0. With h₁, h₂, h₃ forgotten, it is even parity on
   (a, b, c), with E = I = 1.
3. **With hidden distinctions, least sets of pairwise energies give every
   relation** (competition proof, part (iii)).

*Proof.*
1. If R is majority-closed, so is every projection of R. Lift three rows of
   the projection to rows of R, take their majority, and project. So the
   projection has E = 0 by the measures proof.
2. R₀(hᵢ, hⱼ, y) says y = hᵢ ⊕ hⱼ and not both hᵢ and hⱼ are 1. So at most one
   h is 1. Then a ⊕ b ⊕ c = 0, and h = 000, 100, 010, 001 give the four even
   points. The sum of the three energies is least exactly on the conjunction,
   because the conjunction is nonempty. ∎

*Check.*
- **Pairs.** Every forgetting of every one of the 4,169 majority-closed
  relations on four bits has E = 0, and so do 271 projections of random
  pairwise systems.
- **The gadget.** Exact feasibility confirms that R₀ and the six-variable
  system are least sets. The visible relation is parity with E = I = 1.

## Theorem 3: chains and rings with forgotten joints

For a link with transfers M(x), and x uniform:
- a ring of m ≥ 3 links has E = −log₂(1 − ((a+b)^m − (a−b)^m)/2), where
  a = Pr[M = identity] and b = Pr[M = swap]. With two links the ring closes
  with the same chance, but its two spokes can be tied. Two parity links give
  x₁ = x₂, a pair constraint with E = 0;
- a chain of m links with visible ends has E = −log₂(1 − z_m/4), where z_m is
  the expected number of zero entries of the product of m random transfers;
- for parity both are exactly 1 at every length; for every other link both
  tend to 0 geometrically.

*Proof.*
- **Rings.** For m ≥ 3 the ring is a simple cycle, so the visible pairs are
  free (Theorem 5(a)), and E is minus log₂ the chance that the ring closes. A product of transfers with no zero
  rows has zero trace only when it is the swap (the ring theorem). That
  happens exactly when every factor is a permutation and an odd number swap,
  with chance ((a+b)^m − (a−b)^m)/2.
- **Chains.** Each zero entry of the product excludes one pair of end
  values.
- **Parity.** The transfers are exactly the permutations, half of them swaps
  (ring theorem), so the product is a permutation with two zeros.
- **Other links: J is reached.** Consider the seven 2×2 Boolean matrices
  with no zero row or column. The subsemigroups that avoid the all-ones
  matrix J lie in {I, S}, {I, U} or {I, L}, where U and L are the two
  triangular matrices. The transfers of a knot cover all four patterns, so
  they lie in none of the last two.
- **Other links: decay.** Hence either all transfers are permutations
  (parity) or J is a product of transfers. J absorbs, so a product avoids it
  with geometrically falling chance, and z_m → 0. For rings,
  E ≤ −log₂(1 − (a+b)^m) with a + b < 1. This is the Boolean case of the
  full-product dichotomy. ∎

*Check.*
- **Rings.** For all 204 links (34 knots × 6 placements of the joints):
  - the closing chance of rings of length 2–7 matches the formula;
  - the visible pairs of rings of length 3 and 4 are free;
  - the two-link parity ring is a tie.
- **The semigroup step.** All 127 sets of the seven tables are enumerated.
  Every set whose semigroup avoids J lies in one of the three families.
- **Permutation transfers.** These occur exactly for parity, for all 204
  links and for all 742 four-variable knots with joints at the ends.
- **Decay.** Parity holds one bit at lengths 1–12. Every other link is below
  0.055 bits by length 12. The slowest, "if x then h ≤ h′ else h ≠ h′",
  falls by a factor of about 0.805 per link.

## Theorem 4: long knots in a law

Let a law be a set of relations on bits, and consider the relations it
defines with witnesses forgotten.
1. **If every polymorphism of the law is affine,** it defines even parity on
   every even number N ≥ 4 of distinctions. That is a knot with E = I = 1.
2. **Otherwise,** every knot it defines on N distinctions holds at most
   −log₂(1 − N·2^(−N)) bits, and none exists when majority is a
   polymorphism.

So a single contact can carry a full bit at every size exactly in laws with
memory. In every other law the emergence of one contact vanishes as
N·2^(−N).

*Proof.*
1. **Memory laws.** The law defines every relation preserved by all affine
   operations (Galois connection). An affine operation applied coordinatewise
   to rows of even parity of even length gives even parity, because the
   constant part cancels.
2. **Other laws.** By Post's lattice the law has conjunction, disjunction or
   majority as a polymorphism. Majority leaves no knots (measures proof,
   Theorem 1).
   - **Conjunction.** Every defined relation is closed under conjunction.
     Take an excluded point z with zeros at i ≠ j. Its neighbours at i and j
     are allowed, since a knot excludes no two neighbours, and their meet is
     z. That contradicts closure. So every excluded point has at most one
     zero.
   - **The count.** The all-ones point is adjacent to every point with one
     zero. So Z is {1^N} or a set of points with exactly one zero, and
     |Z| ≤ N.
   - **Disjunction** is dual. ∎

*Check.*
- **Shapes and bound.** The 8 conjunction-closed and 8 disjunction-closed
  knots on three bits, and 16 of each on four bits, have the stated shapes
  and reach the bound exactly.
- **Even parity.** On four and six bits it is preserved by minority, both
  constants and negation, and is a one-bit knot.

## Theorem 5: networks with hidden joints

Let G be a simple graph with b₁(G) = |E| − |V| + (number of components)
independent cycles, and place a link L on every edge.
- **(a) Emergence is a satisfiability chance.** Every pair of spokes is free
  in the visible relation. So E = −log₂ Pr_x[the induced network is
  satisfiable]. Given the spokes, each edge carries a binary relation on its
  two joints, so the induced network is a two-literal instance on the
  joints.
- **(b) One bit per cycle at most.** E ≤ b₁(G), with equality exactly when L
  is parity (for b₁ ≥ 1).
- **(c) Superadditivity.** E(G) ≥ Σᵢ E(Hᵢ) for edge-disjoint subgraphs Hᵢ.
- **(d) Zeros.** E = 0 on every graph when L has a common vacuum, a value c
  with L(c, x, c) for every x. Of the 204 placed three-variable links, 144
  have one, including every one-clause link. E = 0 for not-all-equal on
  every bipartite graph.
- **(e) Patches.** If L holds emergence on some finite graph H, every graph
  with k edge-disjoint copies of H holds at least k·E(H) bits. So on the
  tori of a periodic lattice that contains H, emergence grows at least
  linearly with the area.
- **(f) Torus recolouring.** On the a × b torus grid, write τ_v = h_v ⊕ g_v,
  where g_v = (i + j) mod 2 is the checkerboard colour in the fundamental
  domain. Then not-all-equal on an edge:
  - joining different colours becomes an implication between τ_u and τ_v
    whose direction is set by x_e, uniformly at random;
  - joining equal colours (the wrap-around edges across an odd side, the
    seam) becomes the monotone clause τ_u ∨ τ_v or ¬τ_u ∨ ¬τ_v.

  Every part of the torus that does not wrap around is a system of
  implications, satisfied by all zeros. So no such part holds emergence, and
  only the seams can make the torus inconsistent.

*Proof.*
- **(a)** Spokes on two different edges: some spanning forest contains both
  edges, since two edges of a simple graph never form a cycle.
  - Choose all tree spokes freely. Propagate joints from the roots: every
    transfer has no zero row or column, so a joint value always exists.
  - Each other edge then accepts at least one spoke value, because the
    link's projection that forgets one spoke is full.
  - Spokes of one edge are free because the link is a knot.
- **(b)** Fix a spanning forest. Let f(p, q) = Pr_x[M(x)[p][q] = 1]. Forgetting
  one spoke leaves the link full, so f ≥ 1/2.
  - **The bound.** Given the tree spokes, choose a consistent tree
    assignment of the joints. The non-tree spokes are independent of the
    tree spokes and of each other. So the chance that all b₁ non-tree edges
    hold is a product of values of f, at least 2^(−b₁). Hence E ≤ b₁.
  - **Parity reaches it.** Parity transfers are permutations, half of them
    swaps, so f = 1/2 everywhere. The visible relation is "the spokes around
    every cycle have even sum", of codimension b₁.
  - **Nothing else does.** Σ_{p,q} f(p,q) is the expected number of ones in a
    transfer. That is 2 only when every transfer is a permutation, that is,
    only for parity (ring theorem). Otherwise some pattern (p, q) has
    f > 1/2.
  - **Strictness.** Take a non-tree edge uv. With positive chance the tree
    spokes on the tree path from u to v route p at u to q at v; the transfers
    cover every pattern. Choosing the tree assignment that maximizes the
    product then gives more than 2^(−b₁) on that event, so E < b₁.
- **(c)** If some Hᵢ is inconsistent on its own spokes, so is G. These
  events depend on disjoint sets of spokes, so they are independent.
- **(d)** A common vacuum c satisfies every edge with all joints at c. On a
  bipartite graph, a proper two-colouring of the joints makes no edge
  monochromatic, and not-all-equal fails only on monochromatic triples.
- **(e)** follows from (c).
- **(f)** is substitution:
  - Different colours (g_u ≠ g_v): h_u = h_v exactly when τ_u ≠ τ_v, so
    not-all-equal forbids exactly one of the two patterns with τ_u ≠ τ_v,
    which one being fixed by x_e.
  - Equal colours: h_u = h_v exactly when τ_u = τ_v, so not-all-equal forbids
    one equal pattern. ∎

*Check.*
- **The nine small graphs.** On all 1,836 (link, graph) cases (the cycles of
  length 3–5, theta(1,2,2), the bowtie, K₄, the prism, K₃,₃ and the cube):
  - E ≤ b₁ in every case, with equality exactly for parity;
  - all 1,296 cases with a vacuum give 0;
  - not-all-equal gives 0 on all 18 bipartite cases.
- **Pairs and the Petersen graph.** Visible pairs are free on K₄ for every
  link. On the Petersen graph (b₁ = 6): parity 6, not-all-equal 0.0863, and
  "if x then h ≤ h′ else h ≠ h′" 1.3236.
- **Superadditivity.**
  - The bowtie holds exactly twice a triangle (0.385) for the last link.
  - For not-all-equal, two bowties sharing a vertex hold 0.224, against
    2 × 0.0458.
- **Recolouring.** It agrees with the original sample by sample: 300 samples
  each on the 5 × 7 and 3 × 5 tori. Every edge takes the stated form.

| Graph | b₁ | Parity | Not-all-equal |
| --- | --- | --- | --- |
| C₃, C₄, C₅ | 1 | 1 | 0 |
| theta(1,2,2) | 2 | 2 | 0 |
| bowtie | 2 | 2 | 0.0458 |
| K₄ | 3 | 3 | 0.142 |
| prism | 4 | 4 | 0.0752 |
| K₃,₃ | 4 | 4 | 0 |
| cube | 5 | 5 | 0 |
| Petersen | 6 | 6 | 0.0863 |

## What this means (interpretation, not theorem)

- **Kept visible, emergence adds up** knot by knot. Parity adds exactly; the
  others are corrected by how the shared distinctions lean.
- **Forgetting is where pairs and triples part.**
  - Forgetting pairs never creates emergence.
  - Forgetting triples can create it, even statistical emergence from a
    statistically silent whole.
- **Over distance, only reversible contact carries emergence.** Along chains
  and rings, irreversible contact leaks it geometrically. Parity carries one
  bit at every length.
- **Networks hold at most one bit per independent cycle, and only parity
  fills every cycle.**
  - **A correction.** The working document said that knots other than parity
    "remember at most a fraction of a bit". That came from small graphs.
  - **What is true instead.** Frustrated or irreversible contact can hold
    many bits once a network contains many frustration patches (Theorem
    5(e)), always strictly less than one per cycle.
  - **Where it lives.** That emergence is local: it sits in patches.
- **Where no finite patch holds anything,** as with not-all-equal on
  bipartite patches, any emergence must come from the network's global
  cycles. Ticket C measures how much, and whether it survives at scale.

## Scope

- **Assumptions.** Joints are bits, links are knots, and networks are simple
  graphs.
- **Finite checks** support the uniform arguments; they do not replace them.
