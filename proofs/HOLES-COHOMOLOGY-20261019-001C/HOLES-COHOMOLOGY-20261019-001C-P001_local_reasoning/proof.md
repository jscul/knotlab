# Where local reasoning fails on networks of permutation contact

Status: Proved

Ticket `HOLES-COHOMOLOGY-20261019-001C`, 2026-10-19. The proofs below are in
prose. `check.py` builds the certificate that each proof describes, for 469
declared networks, and verifies it by substitution into equations rebuilt from
scratch:
- 85 rings of length 3 to 7, one for every cycle type on 2 to 5 values;
- 384 random networks on seven graphs with 3 to 5 values.

Three broken certificates are rejected as controls. The exact census
`HOLES-COHOMOLOGY-20261019-001A-E001` reached the same verdicts with a general
linear solver (its prediction P5).

## Setting

- **Network.** A connected simple graph with permutation contact, as in
  `HOLES-COHOMOLOGY-20261019-001B-P001`.
  - W is the set of witness values, r = 0 the base vertex.
  - H is the holonomy group at r.
  - The network is **impossible** when H has no common fixed point
    (statement 8 there).
- **Level-k affine relaxation over a commutative ring R (1 ≠ 0).**
  - Variables z[S, f], for every set S of at most k vertices and every
    assignment f of S that satisfies the copies with both ends in S.
  - Equations z[∅] = 1 and z[S, f] = Σ z[S + v, f'] over the extensions f' of
    f.
  - The relaxation accepts when the system has a solution in R.
  - On a simple graph, level 2 is the basic relaxation: one marginal per
    vertex and one joint table per edge. Over Q it is the basic LP without
    nonnegativity, and over Z it is AIP.
- **Pinned level 2 at u.** Level 2 plus z[{r}, w] = 1 if w = u, else 0.
- **Arc consistency** removes values without support across an edge. **Path
  consistency** is (2,3)-consistency on all pairs of vertices.

## 1. The basic relaxation sees exactly the orbit arithmetic

**Claim.** Level 2 over R accepts exactly when some H-invariant vector
μ ∈ R^W has coordinate sum 1. Equivalently, 1 lies in the ideal of R generated
by the sizes of the H-orbits.

**Proof.**
- **Edge equations.** On an edge u → v with permutation p, the only local
  assignments are (x, p(x)). So the two marginal equations give
  z[{u}, x] = z[{u,v}, (x, p x)] = z[{v}, p x]. The marginals μ_v = z[{v}, ·]
  satisfy μ_v ∘ p = μ_u.
- **Invariance.** Transport around any closed walk at r gives
  μ_r(h(x)) = μ_r(x) for every holonomy h. So μ_r is H-invariant, and
  Σ μ_r = z[∅] = 1.
- **Converse.** Given such a μ:
  - put μ_v = μ ∘ g_v⁻¹ along a spanning tree;
  - set z[{u,v}, (x, p x)] = μ_u(x) on every edge (consistent on non-tree
    edges by invariance);
  - on a non-adjacent pair, set z(x, y) = μ_u(x)·[y = 0] + [x = 0]·(μ_v(y) − [y = 0]),
    which has the right marginals and stays in R.
- **Orbits.** An invariant vector is constant on orbits, so its sum is
  Σ_O c_O |O|, and the value 1 is reachable exactly when 1 ∈ (|O|)·R. ∎

**Corollaries.** An impossible network has no orbit of size 1.
- **Over Q**, level 2 accepts every network.
- **Over F_p**, it accepts exactly when some orbit size is prime to p. An odd
  parity loop has one orbit of size 2, so F₃ accepts it. A 3-cycle holonomy is
  accepted by F₂.
- **Over Z**, it accepts exactly when the orbit sizes are coprime. Then the
  Bézout coefficients give an integer solution.
  - **The smallest integer-fooled impossible network has five witness values**
    with orbits of sizes 2 and 3. On at most four values the fixed-point-free
    orbit partitions are {2}, {3}, {4} and {2, 2}, all with gcd > 1.
  - It occurs as one loop with holonomy (01)(234).
  - It also occurs as a **coprime tie**: two loops with holonomies (01) and
    (234). Each loop closes alone, since (01) fixes 2, 3, 4 and (234) fixes 0
    and 1, but not together. The vector −1 on {0, 1} and +1 on {2, 3, 4} sums
    to 3 − 2 = 1.
- **The refutation, when 1 is not in the ideal.**
  - Add z[∅] = 1, the marginal equation at r, and the lasso identities
    μ_r(x) = μ_r(h(x)).
  - This gives 1 = Σ_O |O| μ_r(w_O), whose variable coefficients are all
    divisible by d = gcd of the orbit sizes, or by p.
  - Read mod d, it says 0 = 1.

## 2. One pin decides

**Claim.** Pinned at u, level 2 over any R accepts exactly when u is a common
fixed point of H. So pinning the base witness and trying each value refutes
every impossible network, over every ring.

**Proof.**
- If some holonomy h moves u, the lasso identity μ_r(u) = μ_r(h(u)), with the
  pins μ_r(u) = 1 and μ_r(h(u)) = 0, gives 1 = 0. This is an integer
  combination of the equations, so it refutes over every ring.
- If u is a common fixed point, the point mass on the global solution through
  u is a solution. ∎

Pinning a local section before solving is what separates the singleton
algorithms (Zhuk, arXiv:2509.18434) and cohomological k-consistency
(Ó Conghaile 2022) from plain affine relaxations. Here a single pin already
suffices.

## 3. Three witnesses at a time see every loop

**Claim.** Level 3 refutes every impossible network, by an integer
combination of its equations that reads 0 = 1, and therefore over every ring
at once. Level-3 Sherali–Adams and path consistency refute it as well.

**Proof.** Fix w ∈ W and a lasso r = v_0, v_1, …, v_m = r whose holonomy h
moves w. Such a lasso exists because the network is impossible. Let x_i be w
carried along the lasso to position i.

- **Walk identity.** For every i with 1 ≤ i ≤ m − 2, the bag {r, v_i, v_{i+1}}
  allows (w, y, t(y)), where t is the edge's permutation. Its two marginal
  equations give z[{r, v_{i+1}}, (w, t y)] = z[{r, v_i}, (w, y)], with absent
  variables read as 0.
- **Closing.** The last edge forces μ_r(w) = z[{r, v_{m−1}}, (w, y*)], where y*
  is the value compatible with w across that edge. Since h(w) ≠ w, y* differs
  from x_{m−1}.
- **Chain back.** Walking the identity back along the lasso, the value stays
  different from x_i at every position, by bijectivity. It reaches position 1,
  or an earlier position adjacent to r, with a value the edge to r forbids. So
  the variable is absent, and μ_r(w) = 0.
- **Sum.** Summing over w gives z[∅] = Σ_w μ_r(w) = 0, while z[∅] = 1. All
  coefficients are ±1. ∎
- **Sherali–Adams and path consistency.** Level-3 Sherali–Adams is this system
  with nonnegativity added, so it is infeasible too. Path consistency runs the
  same walk on relations instead of numbers: the relation between r and v_i
  shrinks to the graph of the transport, and the closing edge empties the
  values of r.

**Correction.** At planning time we conjectured that relaxations below the
loop's length are fooled. The walk above refutes that. The conjecture was
withdrawn before the census was frozen, and the census contract records it.

## 4. What never refutes

- **Arc consistency** removes nothing: every value has exactly one support
  across each edge.
- **The basic LP** accepts every network, with the uniform distribution at
  every vertex.
- **BLP+AIP.** The uniform point has full support. So BLP+AIP (Brakensiek,
  Guruswami, Wrochna and Živný 2020) accepts exactly what AIP accepts, which is
  statement 1 over Z. This matches Nakajima and Živný (arXiv:2210.03343): for
  balanced templates, BLP+AIP is no stronger than AIP.

## Summary table

| Method | Refutes an impossible network of permutation contact |
| --- | --- |
| Arc consistency; basic LP; level-2 affine over Q | never |
| Level-2 affine over F_p | exactly when p divides every orbit size |
| Level-2 affine over Z (AIP); BLP+AIP | exactly when the orbit sizes are not coprime |
| Level 2 pinned at one witness, over any ring | always |
| Path consistency; level-3 affine over any ring; level-3 Sherali–Adams | always |

## What it means for knots and holes

- **The holes of permutation networks are shallow.** A network is impossible
  exactly when its loops' holonomies share no fixed point: a hole in the
  composite. Any method that holds three witnesses at once, or pins one, sees
  it over any coefficients. Only unpinned two-witness linear reasoning misses
  it, and then exactly by arithmetic.
- **The coprime tie is the smallest blind spot of integer reasoning.** It is a
  tie between two loops in the sense of `HOLES-COHOMOLOGY-20261019-001B-P001`,
  statement 4. One loop carries a two-element obstruction and the other a
  three-element one, and integer reasoning accepts the pair because 3 − 2 = 1.
- **The same arithmetic, without the robustness.** Lichter and Pago
  (arXiv:2407.09097) build their counterexample to Z-affine k-consistency from
  unsatisfiable Tseitin systems over Z₂ and Z₃ on expanders, combined by an or
  construction. Their integral solution is assembled from a 2-solution and a
  3-solution. Expanders make it robust at every level k. Permutation networks
  cannot be robust: level 3 always sees them.
- **Deep failures need more.** Local reasoning that fails at every level needs
  contact that is not a permutation network, such as constraints on three or
  more distinctions over an expander. That is where the hole criterion of
  `HOLE-CRITERION-COLOURING-20261019-001` lives.

## Nearest known results

- **Bounded width.** Systems of bijection constraints are decided by
  propagation and by path consistency. This is classical, and is the
  satisfiable side of Unique Games.
- **BLP+AIP and AIP.** Brakensiek, Guruswami, Wrochna and Živný (2020).
  Nakajima and Živný, *On the complexity of symmetric vs. functional PCSPs*
  (arXiv:2210.03343, ACM TALG 2024).
- **Coprime counterexamples.** Lichter and Pago (arXiv:2407.09097), for
  Z-affine k-consistency at every level.
- **Pinned, or singleton, reasoning.** Zhuk, *Singleton algorithms for the
  Constraint Satisfaction Problem* (arXiv:2509.18434). Singleton BLP+AIP solves
  every tractable CSP on at most seven values, and a CSP from the dihedral
  group on eight values fools it.
- **Cohomology of local sections.** Abramsky, Mansfield and Barbosa (2011), and
  Ó Conghaile (2022).

**Novelty: known-overlap-likely.** Statements 1–4 follow by elementary
arguments from known characterizations. We found no statement of the
orbit-ideal criterion for permutation networks over an arbitrary ring, with
explicit certificates, or of the coprime tie as the smallest integer-fooled
case.

## Nonclaims

- **This class only.** Nothing is claimed about other CSP classes,
  Nullstellensatz degree, the higher levels of cohomological k-consistency, or
  complexity separations.
- **No native structure.** No claim is made about native structure, distance
  or physics.
