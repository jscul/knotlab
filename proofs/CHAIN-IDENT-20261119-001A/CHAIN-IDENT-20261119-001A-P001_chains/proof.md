# The floor's endless chains: the identification with chains, and the dimension

Status: Proved

Ticket `CHAIN-IDENT-20261119-001A`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-IDENT-20261119-001#2`.
This extends `RING-IDENT-20261119-001A-P001` (refereed, confirmed) to starts that take distinctions from the floor of three places.
The advisor checked the statement and the case table before the freeze, and its three amendments are folded in: the right condition
on loose distinctions, the relay named in (S5⁺), and the corollary's factorial and hypothesis. `machine_check.py` is a separate
algorithm in the same task. Referee pending.

## Setting

As in RING-IDENT: the cheapest parity growth, the knot graph K (connected, simple, at least two knots), d_k, and the bare
convention. Knot k holds max(3, sh_k + d_k) + (surplus_k) distinctions, so it has open_k = max(3 − sh_k, d_k) + surplus_k loose
distinctions. Of these, d_k go to its round-1 groups and s_k = open_k − d_k are left over. A knot is **live** when open_k ≥ 1.

**The extended complex X⁺.**
- **Points and blocks from X.** The live knots, with a block N(w) ∩ live for each knot w having at least two live K-neighbours.
- **Pendant points.** For each live knot w, s_w of them, each joined to w by a block {w, o}.
- **Rays.** At each pendant point o of w, R(open_w) rays: R = 0 if open_w ≥ 3, R = 1 if open_w = 2, R = 2 if open_w = 1. A ray is an
  infinite path o − a_1 − a_2 − … of blocks of two points.

The pendant points of knots with open ≥ 3 are RING-PAIR's surplus points. The rays are CLUSTER-ALL's endless chains. A **knot** in
X⁺ means a live knot; pendant and ray points are not knots. A knot that is not live (open 0) is a round-0 junction with nothing
open; it has no live candidate (Lemma 0), so it is no point of X⁺.

**The cover.** Rays and pendant points add no cycle to the incidence graph I(X⁺). So the cover T⁺ is RING-IDENT's cover T of the
core, with the pendants and rays hung at every lift. The deck group Γ, clusters, [C], ∂C, R*(C) and O_m are as in RING-IDENT,
read in X̃⁺.

**The class.**
- (S3) No round-1 group of three or more.
- (S4) No two knots have two common K-neighbours.
- (S5⁺) Every component of X⁺ holding a live knot is infinite: it holds a cycle of I(X), or a ray.

RING-IDENT's (S1), (S2) and (S5) are dropped: the floor is allowed, surplus may sit anywhere, and K may be a tree. What (S5⁺)
excludes is the relay. A finite ray-free component finishes at its top cluster, with ∂ = ∅. That top is not implied while other
live components remain, so the floor gives it one fresh distinction, which starts an offshoot that is no point of X⁺
(`CLUSTER-ALL-20261119-001`'s relay; `RING-IDENT-20261119-001` Proposition 5).

## Theorem 1 (the identification with chains)

In the class, for every t ≥ 0 there is a bijection φ_t from the junctions born in round t to O_{t+1}, together with the non-live
knots at t = 0. It satisfies RING-IDENT's (a) and (b):
- **(a)** the parents of j are the junctions φ_{t−1}^{−1}[C − v], for v ∈ R*(C), pairwise distinct;
- **(b)** j holds exactly |∂C| loose distinctions after its birth.

Junctions with |R*(C)| ≥ 2 are groups. Those with |R*(C)| = 1 are offshoots.

## Theorem 2 (the dimension)

If moreover K is a tree, then:
- Γ is trivial and X⁺ is the cover.
- For each component Y of X⁺, let F_Y be its finite core (its knots and pendant points), R_Y ≥ 1 its number of rays, and N_Y ≥ 1
  the number of clusters of F_Y that hold a knot and every pendant point carrying a ray.
- Then, for t ≥ max_Y |F_Y|, the number of junctions of round t is a polynomial in t of degree R − 1, where R = max_Y R_Y. Its
  leading coefficient is (Σ_{R_Y = R} N_Y)/(R − 1)!.

So the growth's dimension, the exponent of its cumulative count, is the largest number of endless chains in one component.

## Corollary 3 (where chains come from in a bare tree)

For a bare tree (no surplus) with at least four knots, a ray comes from each leaf whose neighbour has degree 2, one ray each, and
from nothing else. So R is the largest number of such leaves in one parity class of K. The two small trees:
- K2: each knot has two pendant points, each with one ray.
- The path of three knots: the middle knot has one pendant point with two rays.

## Lemma 0 (the shape of X⁺)

1. **Knots.**
   - Two knots are adjacent in X⁺ exactly when they have a common K-neighbour.
   - A knot k with a common K-neighbour with another knot has d_k ≥ 1, computed with every knot live, so open_k ≥ d_k ≥ 1 and k is
     live. Hence a knot that is not live has no candidate and is isolated, as the Setting says.
   - Pendant and ray points lie in blocks of two, and their only path to a knot runs through their pendant point's knot.
2. **Holding a knot.** A cluster that holds a knot and a pendant or ray point also holds that point's knot, by the same lift. Its
   path to the knot must pass through o and then w̃. So the intersection of two clusters that both hold knots, if not empty, holds a
   knot.
3. **∂C ≠ ∅.** Under (S5⁺), every cluster holding a knot lies in an infinite component, so ∂C ≠ ∅.
4. **Block graphs.** RING-IDENT's Lemma 0.3 holds verbatim: X̃⁺'s adjacency graph is a block graph, and so is any cluster's.
5. **Removable points.**
   - If C holds two or more knots, R*(C) is the set of C's non-cut points, so |R*(C)| ≥ 2.
   - If C holds exactly one knot w̃, then C is a tree made of w̃, some of its pendant points, and prefixes of their rays. R*(C) is the
     set of its leaves other than w̃.
   - So |R*(C)| = 1 exactly for C = {w̃, o} and for C = {w̃, o, a_1, …, a_k}, one ray entered from a lone pendant point: the *chain
     clusters*.
   - The two-ray case: {w̃, o, a_1..a_k, b_1..b_l} with both rays entered has R*(C) = {a_k, b_l}.
   - For distinct v, v′ ∈ R*(C) with |C| ≥ 3, C − {v, v′} is a cluster holding a knot. It is connected by part 4. If C has one knot
     w̃, it is not among v, v′. If C has two or more knots, a pendant point in C makes its knot a cut point, so C − {v, v′} keeps a
     knot unless C = {v, v′}.
6. **Spans.** RING-IDENT's Lemma 0.5 holds verbatim.

## Lemmas 1–3

RING-IDENT's Lemma 1 (incidence girth at least 8, from (S3) and (S4)), Lemma 2 (the union lemma: a cluster and a nontrivial
translate fit only in a cluster at least 4 points larger) and Lemma 3 (L1–L3) hold verbatim.
- Pendant points and rays lie on no cycle, so the girth is unchanged.
- An axis of a deck element is a doubly infinite geodesic, so it lies in the core and cannot run into a ray.
- The union lemma's span argument uses only Lemma 0.6.

## Lemma 4 (the groups)

**Claim.** RING-IDENT's Lemma 4 holds with "every junction of round t is live" and (a) through round t. The groups formed from
round t are exactly the sets G(C′), one for each [C′] ∈ O_{t+2} with |R*(C′)| ≥ 2.

*Proof.* The proof is RING-IDENT's. Each place that needed "holds a knot" is now supplied by Lemma 0.2:
- In (F2), W = A ∩ gB holds a knot because A and gB do.
- In (iii) step 2, A_1 − b = A_1 ∩ A_j holds a knot for the same reason.
- In (i), C′ − {v, v′} holds a knot (Lemma 0.5).

Clusters with |R*(C′)| = 1 enter no group, since a group needs two members.

The advisor's check: three junctions such as {w, o}, {w, o′} and {w, w′} are pairwise candidates through w. They have w as a common
neighbour, so they form no valid set, and they enter only as the pairs G({o, w, o′}), G({o, w, w′}) and G({o′, w, w′}). ∎

## Lemma 5 (the counts)

Let j be a junction of round t with φ_t(j) = [C], and x ∈ ∂C.
- C ∪ {x} is a cluster, and x ∈ R*(C ∪ {x}).
- If |R*(C ∪ {x})| ≥ 2, then j lies in the group G(C ∪ {x}).
- If R*(C ∪ {x}) = {x}, then C ∪ {x} is a chain cluster whose only parent is j: an *offshoot extension*.

The orbits [C ∪ {x}] are distinct by (L3), and j occurs once in each G by (L1). So the demand of j is d = the number of group
extensions, the number of offshoot extensions is r, and d + r = |∂C|.

**Offshoot extensions occur only from three kinds of C.** C ∪ {x} is a chain cluster, so C is one too, or C = {w̃}.
- **If |R*(C)| ≥ 2, then r = 0.** x attaches through some z ∈ C. Every y ∈ R*(C) other than z stays removable in C ∪ {x}, so
  |R*(C ∪ {x})| ≥ 2.
- **C = {w̃}:** r = s_w.
- **C = {w̃, o}:** r = R(open_w).
- **C = {w̃, o, a_1..a_k} with k ≥ 1:** r = 1, the next ray point.

## Proof of Theorem 1

By induction on t, carrying (a), (b) and "every junction of round t is live".

**Round 0.**
- φ_0 sends each live knot to the orbit of its lifts, and each non-live knot to itself.
- By (S3), the round-1 groups are the candidate pairs, so d_w is the number of X⁺-neighbours of w that are knots.
- So |∂{w̃}| = d_w + s_w = open_w, which is w's number of loose distinctions. A non-live knot has none.
- Every live knot is live in the growth, by definition.

**Round 1.**
- **The groups.** Candidates are the live knots with a common K-neighbour, which are the adjacent knot pairs, each in one block by
  (S4). By (S3), the groups are these pairs.
- **The offshoots.** Knot w gives d_w distinctions to its pairs, and its s_w leftover ones become offshoots, one for each pendant
  point.
- **φ_1.** It sends pairs to their adjacent lifts and offshoots to [{w̃, o}]. These are all the clusters of two points holding a knot,
  and (a) holds.

**Fresh distinctions, and (b), at every round t ≥ 1.** A new junction with φ_t = [C], p = |R*(C)| parents and demand d gets
max(d, 3 − p, 1) distinctions, or exactly d if it is implied. By Lemma 5, (b) at t is the statement that this number is d + r.
1. **|R*(C)| ≥ 2.** Here p ≥ 2, r = 0 and d = |∂C| ≥ 1 by Lemma 0.3, so it gets max(d, 1) = d, whether implied or not.
2. **C = {w̃, o}.** Here p = 1, d = d_w + (s_w − 1) = open_w − 1, and r = R(open_w).
   - open_w ≥ 3: max(d, 2) = d and r = 0.
   - open_w = 2: max(1, 2) = 2 = 1 + 1.
   - open_w = 1: max(0, 2) = 2 = 0 + 2.
3. **C = {w̃, o, a_1..a_k}, k ≥ 1.** Here p = 1 and r = 1. The group extensions are:
   - the knots adjacent to w̃ (d_w of them);
   - w's other pendant points (s_w − 1);
   - the first point of o's other ray, if open_w = 1.

   With open_w = 2, d = d_w + s_w − 1 = 1. With open_w = 1, d = 0 + 1 = 1. So it gets max(1, 2) = 2 = d + r.
4. **Implied junctions.** The implied rule gives d, which differs from the floor's value only in cases 2 and 3.
   - **Case 3.** The parent P = C − a_k has |∂P| ≥ 2 loose distinctions, a group extension and a_k, and the new junction takes
     only one of them. So it does not take every loose distinction and is not implied.
   - **Case 2.** The offshoot takes one of w's loose distinctions. It would be implied only if that were the start's only loose
     distinction. But a connected simple K with at least two knots holds at least two.
     - If some knot has a common K-neighbour with another, both are live, so each holds at least one.
     - Otherwise K has no path of two lines, so K = K2, and each of its knots holds two.

     (This is the advisor's (S6′): every K-component with a live knot holds at least two loose distinctions. It is automatic here.)
5. **Liveness.** In every case the junction holds d + r = |∂C| ≥ 1 loose distinctions (Lemma 0.3), so it is live.

**Step t → t + 1, for t ≥ 1.**
- **The groups.** By Lemma 4, the groups formed from round t are the G(C′) with |R*(C′)| ≥ 2.
- **The offshoots.** By Lemma 5, each round-t junction j holds |∂C| = d + r loose distinctions. It gives d of them to its groups,
  and its r leftover ones become offshoots, one for each offshoot extension.
  - The offshoots of one junction are interchangeable, since they have the same single parent. So are its offshoot extensions,
    since they are the pendant points of w (with equal rays) or the next points of o's rays.
  - So φ_{t+1} can send them to [C ∪ {x}] bijectively.
- **Nothing else is made.** Clusters of t + 2 points with |R*| ≥ 2 are the groups. Those with |R*| = 1 are chain clusters, whose
  parent C′ − x is a round-t junction with x as an offshoot extension.
- **The round.** No round stalls. (a) holds by construction, and (b) and liveness at t + 1 by the fresh table above. ∎

## Proof of Theorem 2

**The cover.** For a tree K, I(X) is a forest: points and blocks are both indexed by knots, a point u lying in the block of w when u
and w are K-adjacent, so I(X) is a part of the bipartite double cover of K. So Γ is trivial and every cluster is its own orbit.

**The decomposition.** Fix a component Y with core F_Y and rays ρ_1, …, ρ_{R_Y}, each based at a pendant point of F_Y. A cluster C
of Y holding a knot is Q ∪ (prefixes of the rays in a set S), where:
- Q = C ∩ F_Y is a cluster of F_Y holding a knot (removing ray points keeps C connected, since rays are pendant paths);
- S is the set of rays whose base lies in Q and whose first point lies in C.

Conversely, every such pair (Q, S) with prefix lengths ℓ_ρ ≥ 1 is a cluster.

**The count.** The clusters of m points number
    Σ_Q [|Q| = m] + Σ_Q Σ_{∅ ≠ S ⊆ rays(Q)} C(m − |Q| − 1, |S| − 1).
For m ≥ |F_Y| + 1 the first sum vanishes, and each term is a polynomial in m of degree |S| − 1. The largest degree, R_Y − 1, comes
only from the Q holding every ray base, which then holds its knot by Lemma 0.2. There are N_Y ≥ 1 of them (F_Y is one), each
contributing m^{R_Y − 1}/(R_Y − 1)! + lower terms.

**Assembly.** By Theorem 1, c(t) = Σ_Y (the number of clusters of t + 1 points of Y), plus the non-live knots at t = 0. ∎

## Proof of Corollary 3

In a bare tree, knot k has open_k = max(3 − sh_k, d_k) and s_k = max(3 − sh_k − d_k, 0).
- **A leaf** (sh = 1) has d = deg(neighbour) − 1.
  - Its neighbour has degree 1 (K2): open = 2 and s = 2, so two pendant points with one ray each.
  - Degree 2: open = 2 and s = 1, so one ray.
  - Degree at least 3: s = 0.
- **A knot of degree 2** has d = (deg u_1 − 1) + (deg u_2 − 1), so s = 1 only when both neighbours are leaves, the path of three
  knots. Then open = 1, so one pendant point with two rays.
- **A knot of degree at least 3** has 3 − sh − d ≤ 0, so s = 0.

The components of X are K's parity classes (RING-IDENT's Lemma 0.1). ∎

## What it says about dimension two

The census's growths that neither close nor feed a ring are polynomial. Their dimension, read in `CLUSTER-ALL-20261119-001` as the
largest number of chains feeding one piece, is now a theorem for trees in the class.

**Dimension two means two chains in one parity class.** That happens in two ways:
- K2 and the path of three knots;
- two leaves, each hanging from a knot of degree 2, at even distance from each other.

**Two leaves of this kind at odd distance fall in different classes**, and give dimension one: the path of four knots is constant
at 4.

**Relays are a separate case.** CLUSTER-ALL counts them as two more chains. They lie outside this class, at
`RING-IDENT-20261119-001#1`.

**Why two is typical** is then a fact about which small trees occur in the census, and is not proved here.

## Known results, and what this adds

- **Known, cited once.**
  - RING-IDENT's ingredients (Serre's trees, block graphs, site animals on tree-like covers, reverse search).
  - Compositions and the binomial count of clusters on a tree with pendant paths, which is elementary.
- **What this adds.**
  - The identification with the floor: its endless chains are rays hung from the knots' own offshoot points, so they are
    deck-invariant parts of the complex.
  - The growth's dimension as a theorem for trees without relays, with its leading coefficient.

## Validation

**`machine_check.py`.** It runs every connected simple knot graph on 2 to 7 knots, at bare sizes and with one surplus distinction
at each knot in turn. For each, it classifies the start and compares, per round to t = 6, the multiset of (parents, fresh) from the
growth with (|R*(C)|, |∂C|) over X⁺'s clusters.
- In the class: 81 of 81 agree.
- In the relay class, the control (S5⁺ failing): 137 of 137 differ.
- Out of the class by (S3) or (S4): 7,557, not compared.

**The advisor's predictions all hold.**
- The path of three knots gives 3, 4, 6, 8, …, that is 2t + 2.
- K2 gives 2, 4, 6, …, that is 2(t + 1).
- The path of four knots is constant at 4.
- The path of five knots has a relay class {B, D}, and it differs from the cluster count from round 1 (the machine check's relay
  class).

**Theorem 2, an illustration outside the class.** The spider with three legs of two has three rays in the centre's class. Its
counts (7, 9, 10, 14, 20, 27, 35, 44, …) have constant second differences from round 5 on. Its other class relays, adding a linear
term, so the start is outside the class while its quadratic growth is the three rays' count.
