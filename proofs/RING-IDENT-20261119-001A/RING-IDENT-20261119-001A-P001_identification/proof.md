# The identification: a round's junctions are the clusters of the unrolled candidate map

Status: Proved

Ticket `RING-IDENT-20261119-001A`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-PAIR-20261119-001#2`.
The statement was checked by the advisor before it was frozen. The advisor and the machine check (`machine_check.py`) independently
found that RING-PAIR's four scope conditions are not enough, and the fifth condition (S5) below is the fix. The proof is written out
by the thread. Referee pending.

## Setting

**The growth** is the cheapest parity growth of `FRESH-COUNT-20261118-001`, in complete rounds.
- **Junctions and distinctions.** A junction is a set of distinctions. A distinction lies in one junction (it is *loose*) or in two
  (shared), and two junctions are *neighbours* when they share one. Round 0 is the start's knots.
- **Candidates and groups.** In each round, the *live* junctions are those born in the last round that hold loose distinctions.
  - Two live junctions are *candidates* when they have a common neighbour.
  - A *valid set* is a set of at least three pairwise candidates with no neighbour common to all of them.
  - The *groups* are the maximal valid sets, together with the candidate pairs that lie in no maximal valid set.
- **The round.** Each live junction gives one loose distinction to each group containing it, and the round stalls if it cannot.
  Each loose distinction left over becomes a junction of its own, an offshoot with one parent. Each group becomes a new junction, on
  the distinctions it was given; its parents are the group's members.
- **Fresh distinctions.** A new junction with p parents and demand d gets max(d, 3 − p, 1) fresh distinctions. If it takes every
  loose distinction of the presentation (it is *implied*), it gets d instead. Its demand is the number of next-round groups containing
  it, computed after the round with every new junction counted live.

**The start.**
- A connected simple graph K on the knots: each line of K is one distinction shared by its two knots.
- For each knot k:
  - sh_k is its number of shared distinctions;
  - d_k is the number of round-1 groups containing k, computed with every knot live;
  - s_k is its number of surplus distinctions.
- Knot k holds max(3, sh_k + d_k) + s_k distinctions: the bare convention, A107.

**The candidate complex X.**
- **Points:** the knots, and one *surplus point* z for each surplus distinction of each knot k.
- **Blocks:** for each knot w with at least two neighbours in K, the block N(w), its K-neighbours; and for each surplus point z of k,
  the block {k, z}.
- **I(X)** is the bipartite incidence graph of points and blocks.

**The cover.**
- T is the universal cover of each component of I(X), a tree. X̃ has T's point-nodes as its points; two points are *adjacent* when
  they have a common block-node. Γ is the group of deck transformations, which acts freely.
- A **cluster** is a finite set of points of X̃ that is connected through adjacency.
- For a cluster C:
  - [C] is its Γ-orbit;
  - ∂C is the set of points outside C adjacent to C;
  - R*(C) is the set of points v ∈ C for which C − v is a cluster containing a knot.
- O_m is the set of orbits of clusters of m points that contain a knot.

**Scope.**
- RING-PAIR's four conditions:
  - (S1) sh_k + d_k ≥ 3 for every knot;
  - (S2) s_k > 0 only where d_k ≥ 2;
  - (S3) round 1 has no group of three or more;
  - (S4) no two knots have two common K-neighbours.
- And (S5): K contains a cycle.

## Theorem

Under (S1)–(S5), for every t ≥ 0 there is a bijection φ_t from the junctions born in round t to O_{t+1}, with these properties.
- **(a) Parents.** For t ≥ 1, if φ_t(j) = [C], the parents of j are the junctions φ_{t−1}^{−1}[C − v] for v ∈ R*(C). They are
  pairwise distinct, one for each v.
- **(b) Loose distinctions.** If φ_t(j) = [C], then j holds exactly |∂C| loose distinctions after its birth. For a knot, that means
  in the start.

In particular, round t makes |O_{t+1}| junctions, which is RING-PAIR's model H.

## Lemma 0: the shape of X and its cover

1. **Components.** Two knots are adjacent in X exactly when they have a common K-neighbour. So two knots lie in one component of X
   exactly when an even walk of K joins them. A surplus point lies in exactly one block, {k, z}, and two surplus points are never
   adjacent.
2. **Under (S5), every component of X̃ is infinite, and ∂C ≠ ∅ for every cluster C.**
   - K has no cycle of three or four knots. A cycle of four would give two knots with two common neighbours, excluded by (S4). A cycle of three knots a, b, c makes them
     pairwise candidates. A knot adjacent to all three would give a and b two common neighbours, so by (S4) there is none, and
     {a, b, c} is a valid set of round 1, excluded by (S3).
   - So a cycle c_0, …, c_{n−1} of K has n ≥ 5. The walk c_0, N(c_1), c_2, N(c_3), … in I(X), with indices modulo n, closes after
     2n steps when n is odd and after n steps when n is even, once on each side.
   - This walk never steps back or around its closing point: c_i ≠ c_{i+2}, and the block-nodes N(c_{i+1}) and N(c_{i+3}) are
     different nodes. So it is a cyclically reduced closed walk, a nontrivial element of the fundamental group.
   - By part 1, each component of X contains some c_i: one component when K has an odd cycle, and one per side of K when K is
     bipartite. So every component of T is infinite.
   - A finite cluster C is then a proper subset of its infinite connected component, so some point outside C is adjacent to C.
3. **Block graphs.** The adjacency graph of X̃ is a block graph: its maximal cliques are the point sets of block-nodes, and two of them
   share at most one point. A cycle of adjacencies through points not in one clique would lift to a cycle of T. The graph a cluster
   induces is again a block graph. Standard facts for a connected block graph H:
   - H has at least two non-cut points when |H| ≥ 2.
   - A point is a non-cut point exactly when it lies in exactly one maximal clique.
   - If v ≠ v′ are non-cut points and |H| ≥ 3, then v′ is still a non-cut point of H − v. Its one clique Q survives the removal of
     v unless Q = {v, v′}. In that case v′ would be isolated in the connected graph H − v, which has at least two points.
4. **Removable points.** Let C be a cluster.
   - If |C| ≥ 3, then R*(C) is the set of non-cut points of C, so |R*(C)| ≥ 2. A connected set of two or more points holds a knot
     by part 1.
   - If v ≠ v′ are in R*(C) and |C| ≥ 3, then C − {v, v′} is a cluster holding a knot. It is connected by part 3. If it were a lone
     surplus point z, both v and v′ would be adjacent to z, but z's only neighbour is its knot k.
   - R*({u, v}) = {u, v} for two knots, and R*({k, z}) = {z}.
5. **Spans.** The span of a cluster B is the least subtree of T holding B's nodes. Its point-nodes are exactly the points of B.
   Joining consecutive adjacent points of B through their common block-node gives a connected subgraph whose point-nodes are B, and
   it contains the span.
   - So the intersection of two clusters, when it is not empty, is a cluster: its points are the point-nodes of the intersection of
     the two spans, which is a subtree.

## Lemma 1 (girth)

Under (S3) and (S4), every cycle of I(X) has length at least 8.
- **Length 4.** A cycle of length 4 is two blocks sharing two points. Surplus blocks share at most their knot. For two blocks N(w1)
  and N(w2), the two shared knots would have two common neighbours, against (S4).
- **Length 6.** A cycle of length 6 is three distinct knots a, b, c, pairwise in distinct blocks N(w1), N(w2), N(w3). Surplus blocks
  are pendant, so they lie on no cycle.
  - a, b, c are pairwise candidates.
  - A knot adjacent to all three would be a second common neighbour of two of them, against (S4).
  - So {a, b, c} is a valid set of round 1, with every knot live. A maximal valid set containing it is a group of three or more,
    against (S3).

## Lemma 2 (union lemma)

Let f ∈ Γ, f ≠ 1, and let B be a cluster. Every cluster D ⊇ B ∪ fB has |D| ≥ |B| + 4.

*Proof.*
1. **The axis.** f acts on the tree T freely and keeps points and blocks apart, so it inverts no line. It therefore has an axis ℓ, a
   doubly infinite path on which it translates by 2k ≥ 2 nodes (Serre, *Trees*, I.6.4).
2. **k ≥ 4.** A stretch of ℓ from a node x to f(x) projects to a cyclically reduced closed walk of length 2k in I(X). Such a walk
   contains a cycle, so 2k ≥ 8 by Lemma 1, and k ≥ 4.
3. **Projection.** Number ℓ's nodes by the integers in f's direction. Let π be the nearest-node projection of T onto ℓ; it satisfies
   π(fx) = π(x) + 2k. Let α be the least value of π on the span of B; the least value on the span of fB is then α + 2k.
4. **The path between them.** The span of D is a subtree containing both spans. So it contains the path from a node x of span(B)
   with π(x) = α to a node y of span(fB) with π(y) = α + 2k. That path runs along ℓ through every node from α to α + 2k.
5. **k new points.** Among the nodes α, α + 1, …, α + 2k − 1 of ℓ, exactly k are point-nodes. By Lemma 0.5 they are points of D.
   None is a point of fB, since a node of ℓ projects to itself and fB projects to [α + 2k, ∞).
6. So |D| ≥ |fB| + k ≥ |B| + 4. ∎

## Lemma 3 (consequences)

- **(L1)** For a cluster C and distinct v, v′ ∈ R*(C), the orbits [C − v] and [C − v′] differ.
  - If g(C − v) = C − v′ with g ≠ 1, then D = C holds B ∪ gB for B = C − v, with |D| = |B| + 1, against Lemma 2.
  - If g = 1, then v = v′.
- **(L2)** For clusters A and B of m ≥ 2 points, at most one g ∈ Γ has |A ∩ gB| ≥ m − 1.
  - Suppose g and g′ both do. Then gB and g′B both meet A, so D = A ∪ gB ∪ g′B is a cluster of at most m + 2 points.
  - D holds gB and (g′g^{−1})gB, so g′ = g by Lemma 2.
- **(L3)** For a cluster C and distinct x, x′ ∈ ∂C, the orbits [C ∪ {x}] and [C ∪ {x′}] differ.
  - g(C ∪ {x}) = C ∪ {x′} would put B ∪ gB, for B = C ∪ {x}, inside a cluster of |B| + 1 points, so g = 1 and x = x′.

## Lemma 4 (the groups)

Let t ≥ 1, and assume the theorem's (a) through round t, and that every junction of round t is live. For a cluster C′ of t + 2
points, let G(C′) = {φ_t^{−1}[C′ − v] : v ∈ R*(C′)}. Then the groups formed from the junctions of round t are exactly the sets G(C′),
one for each [C′] ∈ O_{t+2}.

*Proof.* Let u and w be junctions of round t, with φ_t(u) = [A] and φ_t(w) = [B].

**(F1) A round-t junction's neighbours are its parents.** Each of its distinctions came from one parent, shared with that parent, or
is fresh and so loose. No two round-t junctions share a distinction. So u and w are candidates exactly when they share a parent.

**(F2) Sharing a parent is overlap.** u and w share a parent exactly when |A ∩ gB| = t for some g ∈ Γ. That g is then unique by
(L2), and C′(u, w) = A ∪ gB is a cluster of t + 2 points, with A = C′ − (the point of gB not in A) and gB = C′ − (the point of A not
in gB).
- *Only if.* A shared parent p, with φ_{t−1}(p) = [W], gives A − a = W′ and B − b = hW′ for lifts with a ∈ R*(A) and b ∈ R*(B). Then
  |A ∩ h^{−1}B| ≥ t.
- *If.* By Lemma 0.5, W = A ∩ gB is a cluster.
  - It holds a knot. If t = 1 and W is a lone surplus point, both A and gB would be W with its knot, so u = w.
  - So the point a of A outside gB lies in R*(A), and gB's point outside A lies in R*(gB).
  - By (a), φ_{t−1}^{−1}[W] is a parent of both.

**(i) If |R*(C′)| ≥ 3, then G(C′) is a maximal valid set, with |R*(C′)| distinct members (L1).**
- *Pairwise candidates.* (C′ − v) ∩ (C′ − v′) has t points, so (F2) applies.
- *No common parent.* Suppose p, with φ_{t−1}(p) = [W], were a parent of every member.
  - For each v there is g_v with g_vW ⊆ C′ − v. All these lifts lie in C′, which has |W| + 2 points, so Lemma 2 makes all g_v equal
    to one g.
  - Then gW ⊆ C′ − R*(C′), which has at most t − 1 < |W| points. Contradiction.
- *Maximal.* Suppose u ∉ G(C′), with φ_t(u) = [U], is a candidate of every member.
  - For each v, (F2) gives h_v with |(C′ − v) ∩ h_vU| = t.
  - For two such v, D = C′ ∪ h_vU ∪ h_{v′}U is a cluster of at most t + 4 < |U| + 4 points holding two lifts of U. So all h_v equal
    one h.
  - If hU ⊆ C′, then hU = C′ − x for a removable x, and u ∈ G(C′).
  - Otherwise I = hU ∩ C′ has exactly t points and lies in every C′ − v, so I ⊆ C′ − R*(C′), which has fewer than t points.
    Contradiction.

**(ii) Each candidate pair {u, w} lies in exactly one G(C′), the orbit [C′(u, w)].**
- It lies in G(C′(u, w)) by (F2).
- Suppose it also lies in G(C″), through C″ − x = h1A and C″ − y = h2gB. Then |A ∩ h1^{−1}h2gB| = t, so h1^{−1}h2g = g by (L2).
  So h1 = h2, and h1^{−1}C″ = A ∪ gB = C′(u, w).

**(iii) Every valid set S lies in one G(C′) with |R*(C′)| ≥ 3.**
1. **Lifts.** Fix u_1 ∈ S with a lift A_1. By (F2) and (L2), each other member u_j has a unique lift A_j with |A_1 ∩ A_j| = t; write
   A_j = (A_1 − b_j) ∪ {c_j}.
2. **Not every b_j is the same.** If all b_j equal one b, then A_1 − b = A_1 ∩ A_j is a cluster holding a knot (Lemma 0.5). Its
   junction is then a parent of u_1 and of every u_j, by (a), so S is not valid.
3. **Different b's force equal c's.** Take b_i ≠ b_j and suppose c_i ≠ c_j.
   - Then A_i ∩ A_j = A_1 − {b_i, b_j} has t − 1 points.
   - Since u_i and u_j are candidates, (F2) gives g ≠ 1 with |A_i ∩ gA_j| = t.
   - Then D = A_1 ∪ A_i ∪ A_j ∪ gA_j is a cluster of at most (t + 3) + 1 = t + 4 < |A_j| + 4 points holding A_j and gA_j, against
     Lemma 2.
   - So c_i = c_j.
4. **All c's are equal.** Every b_l differs from b_i or from b_j, so every c_l equals the common value c.
5. **The cluster.** Put C′ = A_1 ∪ {c}. Every A_j = C′ − b_j and A_1 = C′ − c are clusters holding knots. So S ⊆ G(C′), and
   |R*(C′)| ≥ |S| ≥ 3.

**Conclusion.**
- By (i) and (iii), the maximal valid sets are exactly the G(C′) with |R*(C′)| ≥ 3.
- By (ii), the candidate pairs in no maximal valid set are exactly the G(C′) with |R*(C′)| = 2.
- By Lemma 0.4, every cluster of t + 2 ≥ 3 points has |R*(C′)| ≥ 2.
- By (ii), distinct orbits give distinct groups. ∎

## Proof of the theorem

By induction on t, carrying (a), (b) and "every junction of round t is live".

**Round 0.**
- φ_0 sends a knot k to the orbit of its lifts.
- By (S1), k holds sh_k + d_k + s_k distinctions, of which d_k + s_k are loose.
- By (S3), the round-1 groups are the candidate pairs. So d_k is the number of knots u having a common K-neighbour with k, each
  through exactly one block by (S4).
- The points adjacent to a lift k̃ are one lift of each such u and the s_k surplus points. So |∂{k̃}| = d_k + s_k, which gives (b).
- By Lemma 0.2, ∂{k̃} ≠ ∅, so every knot is live.

**Round 1.**
- The neighbours of a knot are its K-neighbours, so candidates are knots with a common K-neighbour: the knot pairs adjacent in X.
- By (S3), the groups are these pairs. Each knot gives one distinction to each of its d_k pairs, and its s_k surplus ones become
  offshoots.
- φ_1 sends a pair {u, v} to the orbit of an adjacent pair of lifts. It is one orbit, since the block holding u and v is unique by
  (S4). φ_1 sends the offshoot of a surplus distinction of k to [{k̃, z̃}].
- These are all the clusters of two points (Lemma 0.1), so φ_1 is a bijection onto O_2.
- (a) holds: R*({ũ, ṽ}) = {ũ, ṽ}, and R*({k̃, z̃}) = {z̃}, whose removal leaves the parent k.

**Step t → t + 1, for t ≥ 1.**
1. **The groups.** By Lemma 4, the groups formed from round t are the G(C′), one for each [C′] ∈ O_{t+2}. Put
   φ_{t+1}(junction of G(C′)) = [C′].
2. **(a) at t + 1.** It holds by construction, with the members distinct by (L1).
3. **No offshoots and no stall.** Let j be a junction of round t with φ_t(j) = [C].
   - j lies in G(C′) exactly when C′ ∈ [C ∪ {x}] for some x ∈ ∂C. Every such x is removable, since C is a cluster holding a knot.
   - The |∂C| orbits [C ∪ {x}] are distinct by (L3), and j occurs once in each by (L1). So j lies in exactly |∂C| groups.
   - By (b) at t, j holds exactly |∂C| loose distinctions. So it gives each away and leaves no offshoot, and the round does not
     stall. Every junction of round t + 1 is a group.
4. **(b) at t + 1.** A new junction with φ_{t+1} = [C′] has p = |R*(C′)| parents.
   - p ≥ 2 by Lemma 0.4 when t + 2 ≥ 3.
   - Its demand is the number of round-(t + 2) groups containing it, counted with every round-(t + 1) junction live. By Lemma 4 at
     t + 1, whose proof uses only (a) through round t + 1 and liveness, and by step 3, that number is |∂C′|.
   - By Lemma 0.2, d = |∂C′| ≥ 1. So max(d, 3 − p, 1) = d, and the implied rule gives d too.
   - For the round-1 offshoots {k̃, z̃}: p = 1 and d = d_k + s_k − 1 ≥ 2 by (S2), so again max(d, 3 − p, 1) = d.
   - So every junction of round t + 1 holds |∂C′| ≥ 1 loose distinctions and is live. ∎

## Proposition 5: (S5) cannot be dropped

Take K with knot 0 joined to knots 1, 2 and 3, and knot 3 joined to knots 4 and 5: two stars joined at their centres. No surplus.
- **It is in RING-PAIR's scope.**
  - Every knot has sh + d = 3 or 5.
  - K is a tree, so (S3) and (S4) hold.
  - `covermodel.in_scope` returns true.
- **X.** It has two components, the single blocks {1, 2, 3} and {0, 4, 5}.
- **Rounds 1 and 2.** Round 1 makes the six pairs, each holding one loose distinction.
- **Round 2.** It makes {1, 2, 3} and {0, 4, 5}, each from three parents, with demand 0.
  - Neither takes every loose distinction: each takes three of the six.
  - So the floor gives each one fresh distinction where the theorem would give |∂| = 0.
- **The counts.** The growth then runs 6, 6, 2, 2, 4, 6, 8, 10, … through offshoots: `CLUSTER-ALL-20261119-001`'s relays. Model H
  gives 6, 6, 2, 0.
- **The advisor's example.** It gave a seven-knot one: knot w joined to a and b, each with two leaves. Round 1's junction ab has
  demand 0 and is not implied.
- **The machine check.** Among RING-PAIR-scope starts on 3 to 7 knots (with and without one surplus distinction):
  - all 45 whose K has a cycle agree with the theorem's invariants;
  - 21 of the 43 trees do not.

## Where the next hypothesis is needed (the wider class)

`CLUSTER-ALL-20261119-001`'s rule is exact on a wider class. It adds the floor's endless chains, relays, and first-round groups of
three as blocks of their own. Each extension breaks a different step of this proof.

- **Relays (dropping S5).** This is Step t → t + 1, part 4: a junction with ∂C = ∅ that is not implied gets one fresh distinction.
  That distinction then starts a chain of offshoots (Proposition 5). The rule needs an extra pendant chain on each finished component.
- **The floor (dropping S1 or S2).** This is the same step: fresh > d leaves offshoots whose candidates are the junction's other
  children. They hang from a cluster, not from a point of X, so they are not a deck-invariant part of the complex. CLUSTER-ALL models
  them as endless chains.
- **Groups of three in round 1 (dropping S3).** This is Lemma 1: an incidence cycle of length 6 gives k = 3.
  - (L1), (L2) and "no common parent" survive, but the two maximality arguments in Lemma 4 do not, because their D has |U| + 3
    points.
  - The base fails too: a three-parent junction of round 1 is not a cluster of two points.
  - Adding the triple as its own block creates cycles of length 4 with the N(w) blocks, so the tree-of-blocks cover is the wrong
    object there.
  - CLUSTER-ALL's two breaks, the overlapping sunflowers and three blocks in a cycle, both sit in this class.

## Known results, and what this adds

- **Known, cited once.**
  - Hyperbolic automorphisms of trees and their axes (Serre, *Trees*, 1980).
  - Block graphs and their non-cut points (Harary 1963).
  - Site animals on Bethe lattices and Husimi trees (Fisher and Essam 1961; Harary and Uhlenbeck 1953).
  - "Remove a non-cut point" as reverse search over connected induced subgraphs (Avis and Fukuda 1996).
  - The neighbourhood hypergraph of a bipartite graph splitting into two halves (the halved graph).
- **What this adds.** For the cheapest parity growth, the identification is exact for every round, not only below the girth:
  - the junctions of round t are the deck orbits of clusters of t + 1 points of the unrolled candidate map;
  - their parents are the removable points, and their loose distinctions the boundary points;
  - this holds on RING-PAIR's scope with (S5).
- **What it corrects.** RING-PAIR claimed the rule on its scope without (S5). Proposition 5 shows that is too wide, and the correction
  is logged in `docs/CORRECTIONS.md`.

## Validation

- **The machine check.** `machine_check.py` is a separate algorithm in the same task. It enumerates clusters in balls of the cover
  around each point's lift, weighting each by 1/size, and its output is `machine_check.json`.
  - Girth at least 8, in fact at least 10, holds on all 88 RING-PAIR-scope starts on 3 to 7 knots.
  - The multiset of (parents, fresh distinctions) per round equals that of (|R*(C)|, |∂C|) over O_{t+1}, for t ≤ 6, on all 45
    starts with a cycle.
- **Earlier evidence.** RING-PAIR's frozen run (17 fresh starts, every one with a cycle in K) and its census gate (36 starts) are
  evidence for the counts.
- **The advisor** checked each step before the freeze (`research/RING-IDENT-20261119-001/advisor/`). Its remarks are folded in:
  - (S5);
  - the union lemma's wording, which needs no point of B at α;
  - the two details of Lemma 0.4.
