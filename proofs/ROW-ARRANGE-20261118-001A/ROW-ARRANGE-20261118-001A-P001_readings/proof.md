# What colour refinement and local views of the count table cannot see

Ticket `ROW-ARRANGE-20261118-001A`, 18 November 2026. Checked by ticket B's gates
(`experiments/ROW-ARRANGE-20261118-001B/ROW-ARRANGE-20261118-001B-E001_readings/checks.py`). Referee pending. Several statements
were proposed by the advisor (claude-fable-5-2) before the freeze; each was checked here, by hand and on instances.

Notation. A base's count table D gives, for two distinctions, the number of allowed states in which they differ; on a split base
D = 2 × (number of splits separating them). k is the least number of colours of the splits' crossing graph, λ Eppstein's lattice
dimension. A reading is a function of D invariant under renaming; the ones used are defined in `readings.py`: a (multiset of sorted
rows), N1 (each row with the rows of the start's nearest distinctions), W2 (two rounds of colour refinement, 1-WL, on the complete
count-weighted table), WL (1-WL to rest), BW4 (1-WL started from the views within count 4), B_r (the view within count r of each
start, start marked, up to renaming).

## R0. The ladder (by construction)

Each round of 1-WL keeps the previous colour, so a, read off round one, is a function of W2, and W2 of WL. N1 is a function of W2:
the round-two colour of x lists every (count, row) pair, from which the least count and the rows at it are read. B_r with r at least
the largest count is the full table, and for bases of complement-closed three-place constraints the full table with N determines
the base (`DISTANCE-ORDER-20261117-001A`, statement 1: a betweenness knot holds exactly when its counts add), hence k and λ. ∎ (Checked on the 101 classes at n = 6.)

## R1. Every partial cube is a base (the advisor's lemma)

Let G be a partial cube (a connected bipartite graph whose distance embeds isometrically in a hypercube), with distance d. Take
the betweenness constraints B(x, y, z) for every y on a shortest path from x to z; a 0/1 assignment satisfies them exactly when the
set A of its 1s and its complement are both closed under lying on a shortest path. Let A be such a set, neither empty nor
everything. G is connected, so some pair ab of neighbours has a ∈ A, b ∉ A. If d(x, a) < d(x, b) then a lies on a shortest path from
x to b (G bipartite, so d(x, b) = d(x, a) + 1); were x ∉ A, the complement would contain x and b but not a, which it may not. So
W_ab = {x : d(x, a) < d(x, b)} ⊆ A, and likewise W_ba ⊆ complement. In a bipartite graph W_ab ∪ W_ba is everything, so A = W_ab.
Conversely every W_ab and its complement are closed (G is a partial cube). So the solution set is the two all-equal states and the
halfspaces, and D = 2d. ∎ (Checked by brute force: F(2, 4), F(3, 3), κ(C₄), κ(C₆).)

## R2. No reading that sees each start only within a fixed count determines k

F(a, b) is two rings of 2a and 2b points sharing one point p, a partial cube, so a base by R1. Each ring's splits are its a pairs of
opposite halves. Two splits of one ring cross. A split of ring 1 puts ring 2 wholly on the side of p, so it nests with every split
of ring 2. The crossing graph is a clique of a and a clique of b: k = max(a, b).

Fix r (in count units; the view of x is every point within r/2 steps). Let a, b, c, d ≥ r with a + b = c + d. A point at more than
r/2 steps from p sees a run of r + 1 consecutive points of one ring, the same table in all four rings. A point at t ≤ r/2 steps
from p sees p and four runs leaving it, one of t + r/2 points and three of r/2 − t (corrected after the referee), the same table whatever the rings' lengths, and depending
only on t. There is one point with t = 0 and four with each t = 1, …, r/2, in both bases, and the rest are runs. So F(a, b) and
F(c, d) have the same n = 2(a + b) − 1, the same N, and the same multiset of views within count r, and k = max(a, b) against
max(c, d). For every r, F(r, 3r) and F(2r, 2r) (n = 8r − 1) differ in k (3r against 2r) with equal views. This is Hanf's and
Gaifman's locality in the program's setting. ∎ (Checked: F(2, 4) against F(3, 3), n = 11, N = 14, equal B_2, k = 4 against 3,
λ = 4 against 3.)

## R3. Colour refinement does not determine k

For a graph H without triangles, the simplex graph κ(H) has a point for the empty set, for each vertex and for each pair of
adjacent vertices of H, a set joined to each set with one more vertex. It is a median graph (Bandelt and van de Vel), so a base by
R1. Its splits are H's vertices v (sets containing v against the rest); two cross exactly when some set contains both, which needs
the pair uv in H. So the crossing graph is H and k = χ(H).

Take H = C₁₀ and H = C₅ ⊔ C₅ (n = 21 each). In both, the points fall in three kinds: the empty set, ten vertices, ten pairs. The
counts depend only on the kinds and on incidence: empty set to vertex 2, to pair 4; vertex to vertex 4; vertex to pair 2 when
incident, 6 otherwise; pair to pair 4 when they share a vertex, 8 otherwise. Each vertex lies in two pairs and each pair meets two
others, in both graphs, so the partition by kind is equitable with the same numbers. 1-WL therefore stops at the same three colours
with the same rows, and a, N1, W2 and WL all agree, while k = 2 against 3 (λ = 5 for both). The view within count 4 of the
empty-set point is the whole table, so B_4 tells them apart: local views and colour refinement are incomparable. ∎ (Checked.)

## R4. Computing k from the table is NP-hard (classical)

k is the least number of trees whose product holds a median graph (Bandelt and van de Vel 1989), and deciding three is
NP-complete. Directly: three-colouring graphs without triangles is NP-complete, and H ↦ κ(H) is computed in polynomial time with
k(κ(H)) = χ(H) (R3); the count table of κ(H) is twice its graph distance. So k cannot be computed from the table in polynomial time
unless P = NP (the table does determine k, R0; narrowed after the referee). λ, by contrast, is a maximum matching (Eppstein 2005). ∎ (A hardness statement only.)

## R5. Distinct rows suffice for W2 (the advisor's remark)

If the sorted rows of a base are pairwise distinct, each start is named by its row, and W2 gives, for each start, its count to
every named start, which is the table. ∎

## R6. Remark: rings of arcs

On a ring of L points take as splits all arcs of w consecutive points. Two arcs cross exactly when they overlap, so the crossing
graph is the (w − 1)-th power of a cycle of length L; the count at ring distance d is 4·min(d, w), and between two rings of a
disjoint pair it is 4w. One ring of 2M and two of M (w = 2, M odd; or w even, M ≡ w/2 mod w) have equal views within any count below
4w and equal 1-WL colourings, with k = w against w + 1 (Prowse and Woodall's chromatic numbers of cycle powers). Checked at 10
against 5 + 5 (w = 2) and 20 against 10 + 10 (w = 4). These are split systems but not bases: their betweenness constraints allow
more states. R2 and R3 are the bases that do the same work.
