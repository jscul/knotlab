# Question for the advisor (RING-CORES-20261119-001, before the freeze)

You have no tools. Answer only from this text, say where you are unsure, and keep it short.

**Setting.** This is as in the cap study you checked. A start is a connected set of knots with p_k places. In the proved class with every knot live, K̄ has no 3-, 4- or 6-cycle, groups are candidate pairs, and d_k = Σ_{w∈N(k)} (deg_w − 1). With p_k ≤ 5 the non-leaves form a path, a cycle or a star (refereed). The growth is the clusters of t + 1 points of the universal cover of the relayed map X⁺:
- the points are the live knots;
- the blocks are N(w) ∩ live with |·| ≥ 2;
- s_k = open_k − d_k pendant points on each knot, each with R(open) rays (R = 2, 1, 0 for open = 1, 2, ≥ 3);
- a relay is added on finite pieces.

Round t's junctions are the orbits under the deck group of clusters of t + 1 points that contain at least one knot point. Pendant-only clusters do not count. Path cores never grow exponentially (tree dimension theorem).

**Claim (ring cores, cap 5, every knot live).**

1. **Shape.** The core is a ring c_0, …, c_{L−1}, with L = 5 or L ≥ 7. Each core knot carries at most one leaf, and in any three consecutive core knots at most one carries a leaf, from p_c ≥ deg_c + d_c = 4 + ℓ_{c−1} + ℓ_c + ℓ_{c+1} ≤ 5. The open counts are forced except at two kinds of knot:
   - a leafed core knot has open 2;
   - its two neighbours have d = 3, so open 3;
   - every other ("plain") core knot has open 2 or 3, and open 3 is one spare, a pendant with no ray;
   - a leaf has d = 2 and open 2, 3 or 4, so b = 0, 1 or 2 spares.

   Every such start is in the class, and multiplicities add nothing by Lemma M.
2. **Map.** The blocks are N(c_i) = {c_{i−1}, c_{i+1}}, plus the leaf of c_i if there is one. So the points of a piece run along the step-2 walk c_0, c_2, c_4, …:
   - L odd gives one piece with n = L line points;
   - L even gives two pieces with n = L/2 each.

   A leaf of c_i is a third point in the block joining the consecutive line points c_{i−1}, c_{i+1}. There are no rays and no relay.
3. **Count.** The cover of a piece is a bi-infinite line of points x_k with periodic decorations: a_k ∈ {0, 1} spares on x_k, and a leaf on some edges (x_k, x_{k+1}) carrying b spares. A cluster containing a knot is one of two kinds:
   - a nonempty interval of the line, any subset of its spares, any subset of the leaves on edges meeting it, and any subset of each included leaf's spares;
   - a leaf with any subset of its spares.

   Choosing the leftmost line point in a fundamental domain,

   F(z) = Σ_{i=0}^{n−1} Σ_{j≥i} Π_{k=i}^{j} z(1+z)^{a_k} · Π_{edges meeting [i,j]} λ_e + Σ_leaves z(1+z)^b, with λ_e = 1 + z(1+z)^{b_e}.

   Round t's count is the sum over pieces of [z^{t+1}] F. This is rational, with denominator 1 − W(z), where W(z) = z^n (1+z)^A Π_leaves (1 + z(1+z)^b) per piece and A is the number of spares on the piece's line points.
4. **Classification.**
   - A bare piece (no leaf, no spare) gives exactly n junctions every round.
   - Otherwise W(1) > 1, and W has terms of degrees n and n + 1, so it is aperiodic. 1 − W then has a unique simple root ρ in (0, 1) of least modulus, and the count grows like ρ^{−t}.
   - The rate is the root x > 1 of W(1/x) = 1, maximised over the pieces.
   - So within the cap, an in-class all-live start grows exponentially exactly when its core is a ring with a leaf or a spare. Its round-weight is the product of three pieces: y for each line point, (1 + y) for each spare, and 1 + y(1 + y)^b for each hung knot with b spares.
5. **Pilot (disclosed).** The formula reproduces the program's engine exactly to round 30 on seven starts: C5 with a spare, C8 with a spare, C8 with a leaf, C7 with a leaf of b = 2, C9 with a leaf (b = 1) and a spare, C10 with a leaf and a spare, and C11 with a leaf (b = 1) and a spare. It also matches C7 with a leaf to round 60, the referee's a_t = a_{t−7} + a_{t−8}.

**Questions.**
1. Is each step right? In particular:
   - the cluster structure in 3 (can a leaf join a cluster through a block whose line points are both outside it?);
   - the even-L piece assignment;
   - the uniqueness and dominance of ρ.
2. Is every shape in 1 in the class? I argue S3 by "three pairwise candidates need a 6-cycle or a common neighbour".
3. Predict, before I compute them, the rates of C5 with two spares at non-adjacent knots; C7 with a leaf of b = 1 and one spare; C9 with three leaves (b = 0) at mutual distance 3; and C14 with one spare.
4. What stays outside? I would list: knots of six or more places (the catalogue's hanging path (1 + y)/(1 − y) needs one), dead knots, and first-round groups of three or two common neighbours (the break-shape and explosive eddies). Is the headline "within the cap, in the class, the eddies are exactly the decorated rings, with W a product of three pieces" right as worded?
