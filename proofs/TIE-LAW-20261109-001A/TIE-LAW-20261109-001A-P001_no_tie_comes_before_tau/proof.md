# No two shortest routes tie before τ

Status: Proved by hand (Theorems 1 to 3, Lemmas 1 and 2); checks 2 to 4 of `check.py` are computations, check 1 is the proof's
arithmetic.

Ticket `TIE-LAW-20261109-001A`, 2026-11-09.

## Standard statement

- **The graph.** Let T be the regular tessellation {f, m} of the Euclidean or hyperbolic plane (1/m + 1/f ≤ 1/2): its faces are
  f-gons and m of them meet at each vertex. Its **directed medial graph** D has the edges of T as vertices, and one arc for each corner
  (vertex u, face Φ) of T, from the edge of the corner to the next edge about u, always turning the same way. Every vertex of D has two
  arcs in and two out; the arcs about a vertex u form a directed m-cycle (u's **ring cell**) and the arcs about a face Φ a directed
  f-cycle (Φ's **face cell**); every arc has its ring cell on its left and its face cell on its right. In the program's terms: rings are
  T's vertices with m contacts each, contacts are T's edges, faces are T's faces, and an arc is a contact reading the next contact
  about one of its two rings (rule 60).
- **Routes.** A route is a directed path; dist(x, y) is the least length of a route from x to y, and a route of that length is
  shortest. A route **turns on** (a V step) when its next arc is about the same ring, and **switches** (an F step) when it keeps to the
  same face and changes ring. A **ring run** is a maximal block of arcs about one ring, a **face run** one about one face.
- **The tie law.** τ(m, f) = L − L/m − L/f + 1, L = lcm(m, f). `PLAIN-TIME-20261108-001B` computed that the first contact reached by
  two shortest routes comes at τ on every cover it read; why no tie comes earlier was open.
- **Over GF(2).** With A the adjacency matrix of D over GF(2), (A^d)[x, y] is the number of routes of length d mod 2. A contact y at
  distance d < τ has a single shortest route, so (A^d)[x, y] = 1: the plain first need sees it on time. The first contacts with an even
  number of shortest routes, (A^d)[x, y] = 0 at d = dist(x, y), can come no earlier than τ.

**Theorem 1 (a Gauss–Bonnet count for two routes).** Let P and Q be routes from x to y that meet only at their ends, of lengths d_P
and d_Q, and let Δ be the closed disc they bound, named so that Δ lies on P's left. Let k and j be the numbers of ring cells and face
cells in Δ, I the number of arcs in its interior, n the number of vertices of D in its interior, p_F the number of F steps of P and
q_V the number of V steps of Q. Then

km = I + d_P,  jf = I + d_Q,  I = k + j − 1 + n,  n = k + j − 2 − p_F − q_V.

So when d_P = d_Q = d, K = km = jf is a common multiple of m and f and

d = K(1 − 1/m − 1/f) + 1 − n.

**Lemma 1 (one run per cell).** In Theorem 1, if P is a shortest route, P runs along each ring cell of Δ at most once; if Q is a
shortest route, Q runs along each face cell of Δ at most once.

**Lemma 2 (run bounds).** A ring run of a shortest route has at most ⌊m(f − 1)/f⌋ arcs, a face run at most ⌊f(m − 1)/m⌋.

**Theorem 2 (no tie before τ).** In the directed medial graph of every regular tessellation {f, m} of the Euclidean or hyperbolic
plane, two different shortest routes with the same ends have length at least τ(m, f). Every contact within distance τ − 1 of x is
reached by a single shortest route.

**Theorem 3 (closed routes, and the tie at τ when m = f).** Every closed route has length at least min(m, f). When m = f, the contact
y with an arc y → x is at distance m − 1 = τ from x and is reached by two shortest routes, the long way round the ring and the long
way round the face of that arc's corner: the first tie is exactly at τ.

**Computed.** On 42 hyperbolic covers (every type with a ball to τ + 2 of at most two million contacts, two primes each) the first tie
is at τ, two contacts of two routes each (check 2). On 33 of them, every pair of shortest routes that meet only at their ends bounds a
disc with no interior vertex, K = cL and length c(τ − 1) + 1, and the run bounds of Lemma 2 are attained (check 3).

**Open.** That a tie comes at τ when m ≠ f, in general: computed on every cover read, proved for m = f.

## Nearest known result

- **Combinatorial Gauss–Bonnet.** Theorem 1 is the combinatorial Gauss–Bonnet formula for a disc of a 4-valent plane cell complex, with
  the corners counted by the turns of the boundary; thin geodesic bigons are classical in small-cancellation theory (Lyndon and Schupp;
  Strebel's classification of bigons in C(p)–T(q) complexes). Here the routes are directed and the cells are themselves directed
  cycles, so the classical results do not apply as they stand.
- **Triangle groups.** D is a Schreier-type graph of the rotation group of {f, m}; geodesics and growth of triangle groups are classical,
  for undirected generating sets.
- **Classification.** New as far as found for the question asked (ties of directed shortest routes in the alternating medial digraph).

## Proof of Theorem 1

Draw D in the plane with each arc a segment inside its corner, so that the cells of D are the ring cells and face cells. P and Q meet
only at x and y, so P ∪ Q is a simple closed curve, and Δ is a union of cells. Every arc has its ring cell on its left and its face
cell on its right; Δ is on P's left and Q's right, so an arc of P has its ring cell in Δ and its face cell outside, an arc of Q the
reverse, and an interior arc has both inside. Counting arcs of the cells of Δ: km = I + d_P and jf = I + d_Q.

At a vertex v of D the four arcs alternate in, out, in, out, and the four regions between them are, in turn, the ring cells of the
edge's two ends and the face cells of its two sides. At an inner vertex of P where P turns on (V), the region on P's left is the
ring cell it turns about and the other two arcs at v lie outside Δ; where P switches (F), the region on P's right is a face cell
outside Δ, and the other two arcs and three regions (ring, face, ring) lie in Δ. For Q the same holds with left and right exchanged:
two arcs of Δ at its V steps, none at its F steps. At x and at y the two routes use opposite arcs, and one further arc lies in Δ. Each
interior arc has two ends among the vertices of Δ, so counting arc ends,

2I + 2(d_P + d_Q) = 4n + 2(d_P − 1) + 2p_F + 2(d_Q − 1) + 2q_V + 6,  i.e.  I = 2n + 1 + p_F + q_V.

Euler's formula for the disc, with n + d_P + d_Q vertices, I + d_P + d_Q edges and k + j faces, gives n − I + k + j = 1. The two
relations give I = k + j − 1 + n and n = k + j − 2 − p_F − q_V. When d_P = d_Q = d, K = km = jf and d = K − I = K − k − j + 1 − n with
k = K/m and j = K/f. ∎

## Proof of Lemma 1

A vertex of a ring cell R of Δ that lies on P is a vertex of a run of P along R: at an inner vertex of P where P turns on, the only
corner of Δ is the ring P turns about, and where P switches, the two ring corners of Δ are the rings of the runs before and after (and
at x and y the ring corner is that of P's first or last run). Suppose P runs along R twice, and let its first run along R end at
p_b. P switches there. Follow R's cycle forward from p_b: its first vertex on P is the start p_c of another run along R, with c > b
since the first run came first; the arcs of R from p_b to p_c form a route S that meets P only at its ends, and leaves p_b on P's
left. So Theorem 1 applies to P' = P[p_b, p_c] and S, with Δ' on P''s left. S turns on at every inner vertex (q_V = |S| − 1), and P' is
shortest, so |P'| ≤ |S|. From Theorem 1, I' = 2k' + 2j' − 2 − p_F' − |S|, and |S| = j'f − I' gives j'(f − 2) = 2k' − 2 − p_F'; then
|P'| = k'm − I' ≤ |S| gives 2j' ≥ k'(m − 2) + 2 + p_F'. Multiplying by f − 2 and substituting,

k'((m − 2)(f − 2) − 4) + 2f + f·p_F' ≤ 0,

which is impossible, since (m − 2)(f − 2) ≥ 4 whenever 1/m + 1/f ≤ 1/2. The statement for Q is the same argument with rings and
faces exchanged (the inequality becomes j'((m − 2)(f − 2) − 4) + 2m + m·q_V' ≤ 0). ∎

## Proof of Lemma 2

Let a route run r arcs about the ring of u, from the edge e_0 to e_r = e_(r − m) (edges about u, numbered in the turning sense). The
route that goes the other way round u, through the m − r faces between e_r and e_0 on the far side, leaves e_0 round the face just
behind it (f − 1 arcs to e_(−1)), then round the next (f − 1 arcs to e_(−2)), and so on: (m − r)(f − 1) arcs in all. A shortest route
therefore has r ≤ (m − r)(f − 1), that is r ≤ m(f − 1)/f. Faces are the same with m and f exchanged. ∎

## Proof of Theorem 2

Write g = gcd(m, f) and h = 1 − 2/m − 2/f ≥ 0. Let d be the least length of a tie anywhere in D; by the rotations of T, which act
transitively on contacts and keep the arcs, it is the same from every contact. Take a tie P ≠ Q of length d from x to y.

1. **P and Q meet only at their ends.** Both are shortest, so a vertex they share is at the same position on both. If they shared an
   inner vertex, a first divergence and the next meeting would give a tie shorter than d, from x or from a later contact.
2. **The count.** By Theorem 1 (Δ on P's left), d = K(1 − 1/m − 1/f) + 1 − n with K = km = jf = cL for an integer c ≥ 1.
3. **n counts the untouched cells.** By Lemma 1 the runs of P are along distinct ring cells, so P has p_F + 1 runs touching
   p_F + 1 ring cells, and Q touches q_V + 1 face cells. So n = k + j − 2 − p_F − q_V is the number of cells of Δ that their side's
   route does not run along: the **untouched** cells.
4. **Small discs are thin.** An untouched ring cell has all its m arcs inside Δ, across which lie m distinct face cells of Δ, so
   j ≥ m; an untouched face cell forces k ≥ f. Since j = cm/g and k = cf/g, if c < g there is no untouched cell: n = 0 and
   d = c(τ − 1) + 1 ≥ τ.
5. **The coprime disc of size L is thin.** Let g = 1 and c = 1, so k = f and j = m. Suppose a ring cell R, about u, is untouched. Its m
   neighbours are then all the face cells of Δ, the m faces about u (the **petals**). No other ring cell is untouched (its m faces would
   be the same, and two vertices share at most two faces); at most one petal is untouched (an untouched petal's f vertices would be all
   f ring cells of Δ, and two faces share at most two vertices). So Q runs along at least m − 1 petals, once each. Where Q passes from
   one petal to the next it turns on about the far end of their common edge at u, an edge of R, keeping Δ on its right: Q goes round u
   the opposite way to R's cycle, and between two such edges it uses all f − 1 non-u corners of each petal in between. R's cycle joins
   the same two edges the other way: if Q's runs touch r_Q ≥ 3 petals, the r_Q − 2 whole petals cost (r_Q − 2)(f − 1) arcs against
   m − (r_Q − 2) round R, so r_Q ≤ m/f + 2. With r_Q ≥ m − 1 this needs m(1 − 1/f) ≤ 3, false for every coprime hyperbolic type with
   m ≥ 4. For m = 3 (f ≥ 7) there are three petals; if all three were touched, r_Q = 3 > 3/f + 2; so one petal Φ₀ is untouched and its
   f vertices are the ring cells of Δ. Each other petal shares only u and one more vertex with Φ₀, so its other f − 2 corners border
   ring cells outside Δ and are arcs of Q: a face run of f − 2 arcs, more than the ⌊2f/3⌋ Lemma 2 allows once f ≥ 7. An untouched face
   cell is excluded the same way with rings and faces exchanged. So n = 0 and d = τ.
6. **Large discs are long.** Otherwise c ≥ 2. Two bounds hold for every tie: from n ≤ k + j − 2 (step 3),

   (a) d ≥ K·h + 3;

   and since each touched cell carries one run, of at most ρ_R = ⌊m(f − 1)/f⌋ or ρ_F = ⌊f(m − 1)/m⌋ arcs (Lemma 2), P has at least
   d/ρ_R runs and Q at least d/ρ_F, so n ≤ K/m + K/f − d/ρ_R − d/ρ_F and

   (b) d·(1 − 1/ρ_R − 1/ρ_F) ≥ K·h + 1.

   If 1/m + 1/f ≤ 1/3, (a) with K ≥ 2L gives d ≥ τ + L(1 − 3/m − 3/f) + 1 > τ. For m = 3 and f ≥ 7 not divisible by 3 (L = 3f,
   τ = 2f − 2, ρ_R = 2, q = ρ_F = ⌊2f/3⌋), (b) at c = 2 gives d ≥ (2f − 11)·2q/(q − 2), which is at least 2f − 2 (at f = 7 and 8
   directly, and for f ≥ 10 since 2q/(q − 2) > 2); for 3 | f (g = 3), step 4 covers c ≤ 2 and (a) at c ≥ 3 gives d ≥ f − 3 ≥ 2f/3.
   The case f = 3 is the same with m and f exchanged. The types left, (4, f) with 5 ≤ f ≤ 11, (5, 5), (5, 6), (5, 7), their duals and
   the three Euclidean types, are closed by (a) or (b) in exact arithmetic for every c (check 1, which runs the same case analysis for
   every type with m, f ≤ 40). Both bounds grow with K, so every c ≥ 2 follows from the least one.

So every tie has length at least τ. ∎

## Proof of Theorem 3

Let C be a simple closed route of length ℓ, bounding a disc Δ. If Δ is on C's left, every arc of C has its ring cell inside and its
face cell outside, and the counts of Theorem 1 give km = I + ℓ, jf = I, I = 2n + c_F (c_F the F steps of C) and n − I + k + j = 1;
eliminating, ℓ = m + n(m − 2 − 2m/f) + c_F(m − 1 − m/f) ≥ m, since m − 2 − 2m/f ≥ 0 when 1/m + 1/f ≤ 1/2. If Δ is on C's right, ℓ ≥ f
likewise. Every closed route contains a simple one, so it has length at least min(m, f), the length of a cell.

Let m = f, let y → x be an arc of D, in the corner (u, Φ). Any route from x to y followed by this arc is a closed route, so
dist(x, y) ≥ m − 1. Going on round u's ring cell from x reaches y after m − 1 arcs, and going round Φ's face cell after f − 1 = m − 1;
these two routes leave x by different arcs. So y is reached by two shortest routes at distance m − 1, which is τ(m, m). With Theorem 2,
the first tie is exactly at τ. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | `PLAIN-TIME-20261108-001B`'s manifest bound by hash | pass |
| 1 | Theorem 2, step 6: the case analysis closes for every type with m, f ≤ 40, Euclidean ones included (exact rational arithmetic) | pass |
| 2 | Computed: the first tie at τ, two contacts of two routes each, on 42 hyperbolic covers, two primes each | pass |
| 3 | Computed: every pair of shortest routes meeting only at their ends is thin, at length c(τ − 1) + 1, on 33 covers; the run bounds attained | pass |
| 4 | Theorem 3: the shortest closed route has length min(m, f) on 10 covers; at m = f the first tie is at m − 1 | pass |

## Nonclaims

- **Attainment for m ≠ f is computed**, on every cover read, not proved.
- **The covers are read in PSL(2, p)** for two large primes that agree; a ball is the cover's when the quotient identifies nothing
  within it.
- **Regular tessellations only**; irregular networks are not covered. No claim about the plain first need beyond the tie (the first
  late ring at τ + 1 or τ + 2 stays computed, `PLAIN-TIME-20261108-001B`).
