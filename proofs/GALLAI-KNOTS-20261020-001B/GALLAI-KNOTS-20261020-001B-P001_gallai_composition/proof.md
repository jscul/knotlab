# Colouring knots compose along Gallai trees

Status: Proved

Ticket `GALLAI-KNOTS-20261020-001B`, 2026-10-20. It uses the census
`GALLAI-KNOTS-20261020-001A-E001` ("A" below) and the freezing results of
`FREEZING-KNOTS-20261020-001B-P001` ("the freezing proof" below).

## Standard statement

Fix q ≥ 2 colours. A **witness network** is a finite connected graph W of
maximum degree at most q. Attach q − deg(v) pendant **leaves** to each vertex
v, so that every witness has exactly q neighbours. Under the proper q-colouring
law, the **leaf relation** R_W is the set of leaf colourings that extend to the
witnesses. The witnesses are hidden.

A **Gallai tree** is a connected graph in which every block is a complete
graph or an odd cycle. We show:

1. **Knot exactly on Gallai trees.**
   - R_W passes K1–K3 exactly when W is a Gallai tree with at least one leaf.
   - K2 and K3 hold for every witness network, so only K1 depends on W.
   - When W is not a Gallai tree, the hidden witnesses impose nothing.
2. **Gluing law.** Glue two witness networks at a vertex. The colourings the
   composite excludes are joins of the colourings its parts exclude, through a
   unique hidden split of the glued vertex's colours.
3. **Knot types and mass.**
   - The excluded colourings are described block by block.
   - Their number is q! times a product of block masses.
   - For a tree witness network on k vertices, the number is
     q!·((q − 1)!)^(k−1), whatever the tree's shape.
4. **Nativity on regular trees.**
   - On the d-regular tree with p* = 0 (d = q for every q ≥ 3, and below the
     freezing thresholds), every such knot is native at almost every
     broadcast world.
   - In the rainbow world at d = q, no such knot is native.
5. **Hub, not contact.** Two knots that share a visible vertex form a common
   hub, not a knot. Absorbing that vertex into the hidden witnesses gives one
   knot, over the larger witness network.

## Nearest known results

- **Degree-choosability.** A connected graph is colourable from every list
  assignment with |L(v)| ≥ deg(v) exactly when it is not a Gallai tree:
  - Borodin (1977);
  - Erdős, Rubin and Taylor, *Choosability in graphs* (1979);
  - Theorem 11 of Cranston and Rabern,
    [Brooks' theorem and beyond](https://arxiv.org/abs/1403.0479).
- **Structure of bad assignments.** If a connected graph is not colourable from
  lists of size deg(v), then:
  - each list has size exactly deg(v);
  - the graph is a Gallai tree;
  - the lists decompose into one constant list per block.

  Source: Kostochka, Stiebitz and Wirth,
  [The colour theorems of Brooks and Gallai extended](https://kostochk.web.illinois.edu/docs/old/dm96sw.pdf)
  (Discrete Math. 1996).
- **Gallai (1963).** In a k-critical graph, the vertices of degree k − 1
  induce a Gallai forest.
- **Brooks (1941).** A connected graph of maximum degree k that is neither
  complete nor an odd cycle is k-colourable. This is used once, in Lemma 4.

**Classification: known with a delta.**
- Corollary 2 is the Borodin and Erdős–Rubin–Taylor theorem, restricted to
  lists inside [q].
- Theorem 4(a) is the Kostochka–Stiebitz–Wirth decomposition.
- The proofs below are self-contained apart from Brooks. They follow the
  standard method: a greedy colouring toward a strict vertex, and induction
  over blocks.
- The delta:
  - the knot reading, in which K2 and K3 are automatic (Lemma 3), so the knot
    test reduces exactly to degree-choosability;
  - the gluing law as a law of knot composition (Theorem 1);
  - the multiplicative mass in Theorem 4(b). I did not find it stated; it is
    immediate from the decomposition.
  - nativity on regular trees (Corollary 5);
  - the hub remark (Remark 6).

## Setting

- **Colours and networks.** [q] = {0, …, q − 1} with q ≥ 2. W is a witness
  network and deg = deg_W. N(W) is W together with q − deg(v) new leaves
  attached to each vertex v. The leaves of v are written Leaves(v), and n(W) is
  the total number of leaves.
- **The leaf relation.** R_W ⊆ [q]^{n(W)} is the projection of the proper
  q-colourings of N(W) onto the leaves.
  - For a leaf colouring t, let L_t(v) = [q] ∖ t(Leaves(v)).
  - A proper colouring of N(W) restricts to a colouring φ of W with
    φ(v) ∈ L_t(v) (an **L_t-colouring**), and every L_t-colouring extends.
  - So t ∈ R_W exactly when W is L_t-colourable.
- **Degree-bad assignments.** Bad_q(W) is the set of list assignments L with:
  - L(v) ⊆ [q] and |L(v)| = deg(v) for every v;
  - W not L-colourable.
- **The knot test.** This is K1–K3 on allowed states:
  - **K1:** R_W ≠ [q]^{n(W)}.
  - **K2:** forgetting any one leaf projects R_W onto all of [q]^{n(W)−1}.
  - **K3:** R_W ≠ ∅.
- **Blocks.** Blocks are maximal 2-connected subgraphs and bridges (copies of
  K₂). A single vertex has no blocks and counts as a Gallai tree.
- **Gluing.** W₁ ∪ₓ W₂ identifies a vertex x₁ of W₁ with a vertex x₂ of W₂
  into one vertex x, adding no edges. It is a witness network when
  d₁ + d₂ ≤ q, where d_i = deg_{W_i}(x_i).

## Lemma 1 (greedy)

If G is connected, |L(v)| ≥ deg_G(v) for every v, and |L(v₀)| > deg_G(v₀) for
some v₀, then G is L-colourable.

*Proof.*
1. Colour the vertices greedily in order of non-increasing distance from v₀,
   so that v₀ comes last.
2. When a vertex v ≠ v₀ is coloured, a neighbour closer to v₀ is still
   uncoloured. At most deg(v) − 1 colours are blocked, so one of the
   |L(v)| ≥ deg(v) colours is free.
3. At v₀, at most deg(v₀) < |L(v₀)| colours are blocked. ∎

## Lemma 2 (excluded colourings are degree-bad assignments)

A leaf colouring t is excluded from R_W exactly when both:
- each vertex's leaves carry distinct colours;
- L_t ∈ Bad_q(W).

Each L ∈ Bad_q(W) arises from exactly ∏_v (q − deg v)! excluded colourings.
So |[q]^{n(W)} ∖ R_W| = |Bad_q(W)|·∏_v (q − deg v)!.

*Proof.*
1. |L_t(v)| ≥ q − |Leaves(v)| = deg(v), with equality exactly when v's leaves
   carry distinct colours.
2. If some vertex repeats a leaf colour, Lemma 1, strict at that vertex,
   colours W.
3. Otherwise |L_t(v)| = deg(v) everywhere, and t is excluded exactly when
   L_t ∈ Bad_q(W).
4. Given L ∈ Bad_q(W), the colourings t with L_t = L give Leaves(v) the
   q − deg(v) colours of [q] ∖ L(v), one each, in any order. ∎

## Lemma 3 (K2 and K3 always hold)

If W has at least one leaf, then R_W is nonempty, and forgetting any one leaf
leaves no constraint on the others.

*Proof.* Fix a leaf ℓ of a vertex v₀ and any colours t′ on the other leaves.
1. For u ≠ v₀, let L′(u) = [q] ∖ t′(Leaves(u)). Then |L′(u)| ≥ deg(u).
2. Each component C of W − v₀ contains a neighbour u of v₀, and
   deg_C(u) < deg(u) ≤ |L′(u)|. So Lemma 1 colours every component.
3. At v₀, the neighbours block at most deg(v₀) colours, and the leaves other
   than ℓ block at most q − deg(v₀) − 1. So some colour c* is free.
4. Colour v₀ with c*, and give ℓ any colour other than c*, which exists since
   q ≥ 2. The result is a proper colouring of N(W) that extends t′.

So every t′ extends, which is K2 for ℓ, and R_W ≠ ∅, which is K3. ∎

This holds for Gallai trees and all other networks alike. The knot test on R_W
reduces to K1: does the hidden network constrain the leaves at all?

## Lemma 4 (one block)

Let B be 2-connected with maximum degree at most q, and let L ∈ Bad_q(B). Then:
- L is constant, L(v) = C for every v;
- B is |C|-regular;
- B is a complete graph or an odd cycle.

Conversely:
- For B = K_m (m ≤ q + 1), Bad_q(B) consists of the C(q, m − 1) constant
  assignments with |C| = m − 1.
- For an odd cycle, it consists of the C(q, 2) constant assignments with
  |C| = 2.
- For a bridge K₂, it consists of the q assignments L ≡ {a}.
- For a single vertex, Bad_q = {L(v) = ∅}.

*Proof.*
1. **Neighbours have equal lists.** Suppose adjacent u and v have
   L(u) ≠ L(v). After swapping them if needed, pick c ∈ L(u) ∖ L(v).
   - Colour u with c.
   - B − u is connected. Removing c from the lists of u's neighbours leaves
     every list at least as large as the degree in B − u.
   - The list at v keeps all deg_B(v) > deg_{B−u}(v) colours, since c ∉ L(v).
   - Lemma 1 then colours B − u. With u coloured c, B is L-colourable, a
     contradiction.
2. **L is constant.** B is connected, so step 1 makes L constant, L ≡ C. Then
   deg(v) = |C| = k for every v.
3. **The block type.** B is not colourable from k shared colours, so it is
   not k-colourable. By Brooks' theorem, B is K_{k+1}, or an odd cycle when
   k = 2.
4. **The converse.** A constant list of m − 1 colours on K_m fails by
   pigeonhole. A constant list of 2 colours on an odd cycle fails because odd
   cycles are not 2-colourable.
5. **The small blocks.** K₂ and the single vertex are direct. ∎

## Theorem 1 (gluing law)

Let W = W₁ ∪ₓ W₂ with d₁ + d₂ ≤ q. Then L ∈ Bad_q(W) exactly when
L(x) = X₁ ⊔ X₂, with |X_i| = d_i, such that both restrictions are bad:
- L restricted to W₁, with x₁ given the list X₁, lies in Bad_q(W₁);
- L restricted to W₂, with x₂ given the list X₂, lies in Bad_q(W₂).

The split is unique. X_i is the set of colours c ∈ L(x) for which W_i has no
L-colouring with x_i coloured c.

*Proof.*
- **The split makes L bad.** Let φ be an L-colouring of W. If φ(x) ∈ X₁, then
  φ restricted to W₁ colours W₁ from its bad assignment. The case φ(x) ∈ X₂ is
  the same. So no such φ exists.
- **A bad L splits.** Let L ∈ Bad_q(W), and let F_i be the set of colours
  c ∈ L(x) for which W_i has no L-colouring with x_i coloured c. Only x
  changes degree under gluing, so the lists on W_i − x_i are as in W.
  1. If c ∉ F₁ ∪ F₂, the two colourings with x coloured c combine into an
     L-colouring of W. So F₁ ∪ F₂ = L(x).
  2. If |F_i| > d_i, Lemma 1 on W_i, with the list F_i at x_i and strict
     there, colours W_i with x_i ∈ F_i. This contradicts the definition of
     F_i. So |F_i| ≤ d_i.
  3. Then d₁ + d₂ = |L(x)| ≤ |F₁| + |F₂| ≤ d₁ + d₂. So |F_i| = d_i,
     F₁ ∩ F₂ = ∅, and X_i = F_i is a split.
- **Uniqueness.** Any valid split has X_i ⊆ F_i and |X_i| = d_i = |F_i|. ∎

## Corollary 2 (Borodin; Erdős–Rubin–Taylor)

For every witness network W, Bad_q(W) ≠ ∅ exactly when W is a Gallai tree.

*Proof.* Induct on the number of blocks.
1. **No block.** W is a single vertex, and its only assignment, L(v) = ∅,
   is bad.
2. **One block.** This is Lemma 4.
3. **More blocks.** Write W = W₁ ∪ₓ W₂ at a cut vertex x. Each part has fewer
   blocks, and together they have all the blocks of W.
   - If Bad_q(W) ≠ ∅, Theorem 1 gives bad assignments of both parts.
   - Conversely, take bad assignments L₁ and L₂ of the parts. Bad_q(W₂) is
     invariant under permutations of [q], and d₁ + d₂ ≤ q, so we may permute
     L₂'s colours to make L₂(x₂) disjoint from L₁(x₁). Theorem 1 then makes
     the join bad.
4. So Bad_q(W) ≠ ∅ exactly when every block has a bad assignment. By Lemma 4,
   that happens exactly when every block is complete or an odd cycle. ∎

## Theorem 3 (the knot)

Let W be a witness network with at least one leaf. R_W passes K1–K3 exactly
when W is a Gallai tree. Otherwise R_W = [q]^{n(W)}.

*Proof.*
- K2 and K3 hold by Lemma 3.
- K1 holds exactly when some colouring is excluded. By Lemma 2, that means
  Bad_q(W) ≠ ∅, and by Corollary 2, that means W is a Gallai tree. ∎

**The blocks decide.** A block that is neither complete nor an odd cycle
dissolves the knot entirely. An even cycle of witnesses is one example. This
does not apply to a cycle that lies inside a larger complete block: K₄
contains 4-cycles and is a knot.

**Bipartite networks.** A bipartite witness network carries a knot exactly
when it is a tree. Its blocks can be neither odd cycles nor complete graphs
larger than K₂.

## Theorem 4 (knot types and mass)

Let W be a Gallai tree. A **block colour-set system** chooses a set C_B ⊆ [q]
for each block B:
- |C_B| = |B| − 1 when B is complete;
- |C_B| = 2 when B is an odd cycle;
- the sets of blocks that share a vertex are disjoint.

(a) Bad_q(W) consists exactly of the assignments L(v) = ⊔_{B∋v} C_B, one for
each system. So a leaf colouring is excluded exactly when, at every vertex,
the colours missing from its leaves are ⊔_{B∋v} C_B.

(b) Let E(W) be the number of excluded leaf colourings. Then
E(W) = q!·∏_B m_q(B), where:
- m_q(K_m) = ((q − m + 1)!)^{m−1}/(m − 1)!;
- m_q(odd cycle of length m) = ((q − 2)!)^{m−1}/2.

Equivalently, E(W₁ ∪ₓ W₂) = E(W₁)·E(W₂)/q!. In terms of the excluded fraction
f = E/q^{n}:

f(W₁ ∪ₓ W₂)·f(K₁) = f(W₁)·f(W₂),

where f(K₁) = q!/q^q is the star. A tree witness network on k vertices
excludes q!·((q − 1)!)^{k−1} colourings.

(c) The single knot types:
- **K_m:** all m witnesses' leaves carry the same set of q − m + 1 distinct
  colours.
- **An odd cycle:** all its witnesses' leaves carry the same q − 2 distinct
  colours.
- **The star:** its q leaves use all q colours.
- **A tree:** some proper q-edge-colouring of the tree exists such that each
  vertex's leaves carry exactly the colours missing from its edges.

*Proof of (a).* Induct over blocks.
1. For one block, this is Lemma 4.
2. At a cut vertex, Theorem 1 says L is bad exactly when L(x) = X₁ ⊔ X₂ with
   both parts bad. By induction, the two parts are systems.
3. Their union is a system of W: at x, disjointness is X₁ ∩ X₂ = ∅, and every
   other vertex has all its blocks in one part.
4. Conversely, a system of W restricts to systems of the parts, with
   X_i = ⊔ C_B over the blocks of W_i at x. ∎

*Proof of (b).*
1. By Theorem 1 and its uniqueness, L ↔ (L₁, L₂) is a bijection between
   Bad_q(W) and the pairs with L₁(x₁) ∩ L₂(x₂) = ∅.
2. Permutations of [q] preserve Bad_q(W₂) and act transitively on d₂-sets. So
   every d₂-set is L₂(x₂) for exactly |Bad_q(W₂)|/C(q, d₂) assignments, and
   |Bad_q(W)| = |Bad_q(W₁)|·|Bad_q(W₂)|·C(q − d₁, d₂)/C(q, d₂).
3. Multiply by the leaf orders of Lemma 2. Only x's factor changes: from
   (q − d₁)!·(q − d₂)! in the parts to (q − d₁ − d₂)! in W. Then

   E(W)/(E(W₁)E(W₂)) = [C(q − d₁, d₂)/C(q, d₂)]·(q − d₁ − d₂)!/((q − d₁)!(q − d₂)!) = 1/q!.

4. For one block, Lemmas 2 and 4 give E(K_m) = C(q, m − 1)·((q − m + 1)!)^m and
   E(C_m) = C(q, 2)·((q − 2)!)^m. Dividing by q! gives m_q.
5. For trees, m_q(K₂) = (q − 1)!, applied to each of the k − 1 edges. ∎

*Proof of (c).*
- The single-block types read off (a) with the leaf colours [q] ∖ C.
- For a tree, every block is an edge with |C_e| = 1, and disjointness at the
  vertices makes e ↦ C_e a proper edge-colouring. ∎

**Reading.**
- Knots compose freely along Gallai trees: the excluded mass of the composite
  factorizes over its blocks.
- The star is the unit of the factorization.
- Each bridge multiplies the count by (q − 1)!.

## Corollary 5 (nativity on regular trees)

Let q ≥ 3, d ≥ q, and let σ be the broadcast q-colouring of the d-regular tree
T_d (as in the freezing proof). Take a finite subtree W ⊆ T_d with maximum
degree at most q. For each v ∈ W, choose q − deg_W(v) of its neighbours outside
W as its leaves; at d = q, take all of them.

(a) Project all proper colourings of T_d onto the chosen leaves, with every
other vertex hidden. The result is R_W, and it is a knot.

(b) Suppose p* = 0. This holds:
- at d = q, for every q ≥ 3;
- for d < 6, 10 and 15 when q = 3, 4 and 5 (the freezing proof, Theorem 4).

Then at almost every broadcast world, every such knot is native under the
source-aware reading.

(c) At d = q there is a **rainbow world**:
- the root's neighbours carry all q − 1 other colours;
- every other vertex's q − 1 children carry each colour other than its own
  exactly once.

There, no vertex is recoloured by any finite change, so none of these knots is
native.

*Proof of (a).*
1. In a tree, distinct witnesses have distinct outside neighbours.
2. Removing W leaves one subtree hanging from each outside neighbour, and any
   colour at that neighbour extends over its subtree.
3. An unchosen outside neighbour of v only needs to avoid v's colour, which is
   possible since q ≥ 2.
4. So the projection is {t : W is L_t-colourable} = R_W. W is a tree, hence a
   Gallai tree, and Theorem 3 applies. ∎

*Proof of (b).*
1. By the freezing proof, Theorem 1, a vertex is frozen with probability
   Ψ(p*) = C(q − 1, d; p*). At p* = 0, Ψ(0) = Σ_j (−1)^j C(q − 1, j) = 0.
2. At d = q, a vertex is frozen within its branch exactly when all of its
   q − 1 children are frozen within theirs and carry the q − 1 other colours.
   So Φ(p) = (q − 1)!/(q − 1)^{q−1}·p^{q−1}.
3. For q ≥ 3 the coefficient is below 1. So Φ(p) < p on (0, 1], and p* = 0.
4. With probability 1, no vertex of the countable tree is frozen. Then every
   leaf of every such knot is recoloured by some finite change, which is the
   nativity condition. ∎

*Proof of (c).*
1. Suppose a finite change recolours a nonempty set S, and let v be a deepest
   vertex of S.
2. v's children lie outside S and keep their colours. They carry every colour
   other than v's old colour.
3. So v has no other colour available, a contradiction. ∎

At q = 2 the coefficient is 1, every p is a fixed point, and every 2-colouring
of the line is frozen. This is why q ≥ 3 is needed.

## Remark 6 (a shared visible vertex is a hub)

In T_q with q ≥ 3, take witnesses a and b with a common neighbour u. The star
knots R_a and R_b, on the q neighbours of a and of b, share the variable u.
Projecting onto both neighbourhoods gives R_a ∧ R_b.

- **It is not a knot.** Forgetting any of the 2q − 2 unshared variables leaves
  R_b or R_a, which is still constrained, so K2 fails.
- **Hiding u leaves nothing.** Every constraint disappears: u can avoid the at
  most two colours that would complete all q colours on either side.
- **Absorbing u gives one knot.** Hiding u as a witness gives the knot of the
  witness path a – u – b. Its leaves are the remaining neighbours of a, u and
  b.

So in this law, knots compose by enlarging the hidden witness network, as in
Theorem 1, and not by sharing visible variables. This matches the program's
rule that two relations sharing a variable form a common hub.

## Outside the hypothesis

A found 9 knots for q = 3 and 1 for q = 4 on witness networks with a vertex of
degree q + 1. One example is two triangles sharing a degree-4 vertex at q = 3.
Another is K_{1,1,3} at q = 3: two adjacent hubs, each joined to three
witnesses that carry one leaf apiece. That relation is the star relation on
the three leaves.

Lemmas 1–3 need |L(v)| ≥ deg(v), which fails at such vertices. These knots are
not classified here.

## What this does not show

- **Substrates.** Nothing is claimed for substrates with cycles, where
  boundary vertices interact through the outside, or for witnesses above
  degree q.
- **What composition means here.** The composition here fuses knots into one
  knot over a larger hidden witness network. It is not:
  - a contact network;
  - composed topology in the protected sense;
  - a path or a distance.
- **Nativity.** Nativity is shown only where p* = 0. Beyond freezing, each leaf
  is frozen with positive probability Ψ(p*) > 0.
- **Classical content.** The mathematics of Corollary 2 and Theorem 4(a) is
  classical; the delta is the reading and the mass law.

## Checks

`check.py` runs in about 15 seconds and writes `result.json`. All of its checks
pass, and all of its controls are rejected.

- **Graph enumeration.** It enumerates the connected graphs on at most 6
  vertices up to isomorphism (1, 1, 2, 6, 21, 112; OEIS A001349).
- **Exhaustive checks** on every class of maximum degree at most q, for
  q = 2, 3, 4:
  - Lemma 4 on 74 two-connected cases.
  - Corollary 2 on 168 cases.
  - Theorem 4(a) and (b) on 65 Gallai trees, including the tree formula on 30
    trees.
  - Lemmas 2 and 3 and Theorem 3 on the 89 networks within the leaf caps. Of
    those, 33 are knots, exactly the 33 Gallai trees.
- **Random checks:**
  - Lemma 1 on 1,500 instances.
  - Lemma 3's construction on 597 networks with up to 12 witnesses.
  - Lemma 4 on 203 two-connected graphs on 7 or 8 vertices.
  - Theorem 1 on 160 glued pairs, with q up to 5 and non-Gallai parts
    included. The law and the uniqueness of the split hold on every pair.
  - Theorem 3 on 95 Gallai trees and 146 non-Gallai networks with up to 9
    witnesses.
  - Theorem 4 on 130 random Gallai trees.
- **Corollary 5.** It checks the monomial identity exactly at q + 1 points for
  q = 2, …, 8. It also checks that the rainbow colouring of balls is the only
  extension of their boundary, for (q, depth) = (3, 3), (4, 2) and (5, 2).
- **Remark 6.** It checks the hub relation for q = 3 and 4.
- **Controls, all rejected:**
  - "knot iff tree" (14 disagreements);
  - "knot iff bipartite" (25);
  - "knot iff every block is complete" (2);
  - Lemma 1 without a strict vertex (a triangle with equal pairs is not
    coloured);
  - "a glued vertex is never split", which predicts that gluing dissolves the
    knot (136 Gallai gluings keep bad assignments).
