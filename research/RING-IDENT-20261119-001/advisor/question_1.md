# Question for the advisor (RING-IDENT-20261119-001, before freezing the statement)

You have no tools. Answer only from this text; check the argument and say exactly where it fails, if it does.

**The growth (complete rounds).** A junction is a set of bits; a bit lies in one junction (loose) or two (shared). Round 0: the knots
of a start. Two junctions are neighbours when they share a bit. Each round: the live junctions (those born last round with loose
bits) form *candidates* (two live junctions with a common neighbour); a *valid set* is a set of at least three pairwise candidates with
no neighbour common to all; the *groups* are the maximal valid sets and the candidate pairs in no maximal valid set. Each live junction
gives one loose bit to each group containing it; each leftover loose bit becomes a one-parent junction (offshoot). A new junction with
p parents and demand d (the number of next-round groups containing it, computed with all new junctions live) gets fresh bits
max(d, 3 − p, 1), or d if it takes every loose bit of the presentation (implied).

**The start and its complex.** Knots k with shared distinctions to other knots (a simple graph K on the knots, one distinction per edge),
d_k = number of round-1 groups containing k, and s_k surplus distinctions; knot k has sh_k + d_k + s_k places. The candidate complex X:
vertices = knots plus one surplus vertex per surplus distinction; blocks = N_K(w) for each knot w with |N_K(w)| ≥ 2 (its neighbours
in K, as a full simplex), plus a block {k, z} per surplus vertex z of k. X̃ = the universal cover (the tree of blocks covering X's
vertex–block incidence graph I(X)); a *cluster* is a finite set of X̃'s vertices connected through common blocks.

**Scope (RING-PAIR's four conditions):** (S1) sh_k + d_k ≥ 3 for every knot; (S2) surplus only at knots with d_k ≥ 2; (S3) round 1 has
no group of three or more; (S4) no two knots of K have two common neighbours. Start connected.

**Claimed theorem.** In scope, for every t ≥ 0 there is a bijection φ_t from the junctions born in round t to the deck orbits of
clusters of size t + 1 containing a knot, with: parents(j) = {φ_{t−1}^{-1}[C − v] : v ∈ R*(C)} (R* = the points v with C − v
connected and containing a knot), all distinct; and loose bits of j after its birth = |∂C| (the vertices outside C adjacent to C).

**Proof plan.**
1. *Girth.* (S4) excludes incidence 4-cycles in I(X) (two blocks sharing two vertices); (S3) excludes incidence 6-cycles (three knots
   pairwise in a common block, no common neighbour, would be a valid triple in round 1). Surplus blocks are pendant. So every deck
   element f ≠ 1 translates its axis in the tree by 2k with k ≥ 4.
2. *Union lemma.* For a cluster B and a deck element f ≠ 1, every cluster D ⊇ B ∪ fB has |D| ≥ |B| + k ≥ |B| + 4. (Proof: the span
   of a cluster in the tree has no vertex-nodes outside the cluster; project to f's axis; if B's projection starts at axis node α,
   D's span contains the axis path from α to α + 2k; its vertex-nodes strictly inside, plus B's point at α, are k vertices of D not in
   fB, since fB projects to [α + 2k, …].)
3. *Consequences.* (L1) distinct v ∈ R*(C) give distinct orbits [C − v]; (L2) for clusters A, B of size m ≥ 2, at most one g with
   |A ∩ gB| ≥ m − 1; both from the union lemma, with D = C and D = A ∪ gB ∪ g'B (size ≤ m + 2).
4. *Groups, t ≥ 1.* Neighbours of a round-t junction are its parents only (fresh bits are loose and round-t junctions share no bit).
   For a cluster C' of size t + 2, G(C') = {C' − v : v ∈ R*(C')}. Show: (i) if |R*| ≥ 3, G(C') is a maximal valid set (no common parent:
   two lifts of a common parent inside C' would contradict the union lemma, and one lift cannot fit in C' − R*; maximal: an outside
   member U meeting each C' − v in t points has one lift for all v by the union lemma, so U ∩ C' ⊆ C' − R*, too small); (ii) every
   candidate pair lies in exactly one G(C') (L2); (iii) every valid set S lies in one G(C'): fix a lift A1 of one member and the unique
   lifts A_j = (A1 − b_j) ∪ c_j of the others; not all b_j equal (else a common parent); if b_i ≠ b_j then c_i = c_j (else the union
   A1 ∪ A_i ∪ A_j ∪ gA_j has at most t + 4 points and contains A_j and gA_j, against the union lemma), so all c_j equal. Hence groups =
   {G(C')}; removing v from C' keeps it a block graph, so C' − {v, v'} is connected and members share parents.
5. *Counts.* A round-t junction lies in exactly |∂C| groups (one per extension C ∪ {x}, distinct orbits by L2), so it uses all its loose
   bits: no offshoot after round 1, no stall. Its demand is |∂C'|. Clusters of size ≥ 3 have |R*| ≥ 2, so p ≥ 2 and fresh = max(d, 1) =
   d when d ≥ 1; d = 0 only for C' = X̃ finite, where the junction takes every loose bit (implied), so fresh = 0. Round 1: by (S3)
   groups are the candidate pairs = adjacent knot pairs of X, one block each (S4); offshoots = {k, z}; by (S1) a knot's loose bits are
   d_k + s_k = |∂{k}|; an offshoot {k, z} has p = 1 and d = d_k + s_k − 1 ≥ 2 by (S2), so the floor never binds.

**Questions.**
1. Is each step sound? In particular: the union lemma's proof (including when α is a block node, and when B's span does not meet the
   axis); the girth claim from (S3); and step 4(iii)'s size count (A1 ∪ A_i ∪ A_j ∪ gA_j ≤ t + 4).
2. Is anything used that the scope does not give (for example, connectivity, the structural implied test, or the code's pruning in
   group enumeration)?
3. The coordinator asked for the in-scope class where CLUSTER-ALL found its wider rule exact (with the floor's endless chains and
   first-round groups of three as their own blocks). Which step is the first to need a hypothesis that class does not give?
4. Is this known (lattice animals of a tree-like cover; equivalence of some growth process with animals)? Name the nearest result.
