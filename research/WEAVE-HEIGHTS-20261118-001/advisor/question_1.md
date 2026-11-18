You are refereeing a written proof before it is frozen. Work only from what is written; no tools. Check every step; list gaps, wrong steps and unclear citations concretely, and say which statements you would weaken. Keep it focused.

Context: NAE ("not-all-equal") constraints on the triangles of patches of the triangular lattice. A set S is constrained if not every assignment of S extends to a satisfying assignment; a bond is a constrained set whose (|S|-1)-subsets are all free; bond distance b = least bond size - 1; steps apart = graph distance in the patch's edge graph. You earlier sketched the cyclic criterion and D + D = 3 steps; the thread has now written them out. The proof follows.

# Heights on weave patches: the criterion for constrained sets and the lower bound

Ticket `WEAVE-HEIGHTS-20261118-001A`, 18 November 2026. Written before the frozen checks of ticket B
(`experiments/WEAVE-HEIGHTS-20261118-001B/WEAVE-HEIGHTS-20261118-001B-E001_checks/`). Referee pending. The statements of Proposition 3
and Lemma 6 and the outline of their proofs are the advisor's (claude-fable-5-2, in `DOUBLE-MEET-20261118-001`); the proofs below are
written out in full by the thread, with the bridged-graph step resting on cited theorems.

## Setting

The weave's distinctions are the points (i, j) of Z²; its knots are u(i, j) = {(i, j), (i+1, j), (i, j+1)} and
d(i, j) = {(i+1, j), (i, j+1), (i+1, j+1)}, every one not-all-equal. A **patch** T is a finite set of knots; V is the set of its
distinctions and E the set of its **pairs** (two distinctions in a common knot of T); G = (V, E) is its pair graph. **Steps apart**
s(x, y) is the number of knots of a least chain from x to y (consecutive knots sharing a distinction); since two distinctions are
co-knotted exactly when they form a pair, s(x, y) is the distance in G. T is a **disc** when its knots are connected through double
meetings, V − |E| + |T| = 1, and the knots around each distinction are connected through double meetings (no pinch).

**Lemma 0 (discs).** If T is a disc, the union of its knots is a closed topological disc, the 2-complex (V, E, T) is simply connected,
and every three pairwise co-knotted distinctions form a knot of T.

*Proof.* Each lattice pair lies in exactly two lattice knots, so in at most two knots of T; with no pinch, the knots around each
distinction form a fan or a full wheel, so the union is a compact connected surface with boundary. It lies in the plane, so it is
orientable of genus 0, and its Euler characteristic 2 − (number of boundary curves) equals 1: it has one boundary curve and is a disc,
hence simply connected. Three pairwise co-knotted distinctions are the corners of a lattice knot k. If k ∉ T, each of its three pairs
lies in exactly one knot of T (the other lattice knot on it), so all three are boundary pairs, and they form a closed curve inside the
single boundary curve, which is simple; so the boundary curve is the boundary of k, and the disc is either k (not in T) or its
unbounded complement (T is finite): a contradiction. ∎

## 1. Orientation and residues

Call e₁ = (1, 0), e₂ = (−1, 1) and e₃ = (0, −1) the **forward** steps; every lattice pair is a forward step in exactly one direction.
Each knot is a forward 3-cycle: u(i, j) runs (i, j) → (i+1, j) → (i, j+1) → (i, j) by e₁, e₂, e₃, and d(i, j) runs
(i, j+1) → (i+1, j+1) → (i+1, j) → (i, j+1) by e₁, e₃, e₂. The class c(i, j) = (i + 2j) mod 3 rises by 1 along every forward step.

A **height function** on T is h : V → Z with h(v) ≡ c(v) (mod 3) and h(b) − h(a) ∈ {1, −2} for every forward step a → b of a pair.

**Lemma 1 (states are heights).** On a disc, an assignment σ of values to V is allowed exactly when σ ≡ h (mod 2) for some height
function h, and h is then unique up to adding a multiple of 6.

*Proof.* If h is a height function, the three increments around a knot lie in {1, −2} and sum to 0, so exactly one is −2: exactly
one pair of the knot has h of equal parity, so h mod 2 is not all equal on the knot. Conversely, let σ be allowed and put
ω(a → b) = 1 when σ(a) ≠ σ(b) and −2 when σ(a) = σ(b), for each forward step a → b (and ω(b → a) = −ω(a → b)). Each knot has exactly
one equal pair, so ω sums to 0 around each knot. By Lemma 0 the 2-complex is simply connected, so ω sums to 0 around every closed walk
and ω = h(b) − h(a) for some h : V → Z, unique up to a constant; choose h(v₀) with h(v₀) ≡ c(v₀) (mod 3) and ≡ σ(v₀) (mod 2). Every
increment is ≡ 1 (mod 3), so h ≡ c (mod 3) everywhere, and h changes parity exactly where σ changes value, so h ≡ σ (mod 2). Two height
functions with the same parity everywhere have the same increments (parity decides between 1 and −2), so they differ by a constant,
which is ≡ 0 (mod 2) and (mod 3). ∎

## 2. Heights as difference constraints

Let D(s, t) be the least weight of a walk from s to t along pairs of T, a forward step weighing 1 and a backward step 2.

**Lemma 2.** (i) Every walk from s to t weighs ≡ c(t) − c(s) (mod 3). (ii) For every height function h, h(t) − h(s) ≤ D(s, t).
(iii) If S ⊆ V is nonempty and g : S → Z has g ≡ c (mod 3) and g(t) − g(s) ≤ D(s, t) for all s, t ∈ S, then
h(v) = min over s ∈ S of g(s) + D(s, v) is a height function equal to g on S.

*Proof.* (i) A forward step weighs 1 and raises c by 1; a backward step weighs 2 and lowers c by 1 ≡ 2. (ii) Along a forward step h
rises by at most 1 and falls by at most 2, so along any walk h changes by at most its weight. (iii) h = g on S by the hypothesis (and
D(s, s) = 0); h ≡ c (mod 3) by (i); and for a forward step a → b the shortest-walk inequalities give h(b) ≤ h(a) + 1 and
h(a) ≤ h(b) + 2, so h(b) − h(a) ∈ [−2, 1] and ≡ 1 (mod 3), hence ∈ {−2, 1}. ∎

## 3. The cyclic criterion

**Proposition 3.** On a disc, a set S of distinctions is constrained exactly when it holds m ≥ 3 distinct distinctions s₁, …, s_m with
Σᵢ D(sᵢ, sᵢ₊₁) ≤ 3(m − 2) (indices mod m).

*Proof.* Fix an assignment σ on S. For s ∈ S let r_s ∈ {0, …, 5} be the residue with r_s ≡ c(s) (mod 3) and r_s ≡ σ(s) (mod 2). By
Lemmas 1 and 2, σ occurs exactly when there are integers k_s with g(s) = r_s + 6k_s satisfying g(t) − g(s) ≤ D(s, t) for all s ≠ t in
S, that is k_t − k_s ≤ W(s, t) = ⌊(D(s, t) − r_t + r_s)/6⌋. Integer difference constraints are feasible exactly when the complete
digraph on S with weights W has no negative cycle, and a negative cycle can be taken simple. For a simple cycle s₁, …, s_m (m ≥ 2) put
a_i = D(sᵢ, sᵢ₊₁) − r_{i+1} + r_i. By Lemma 2(i) and r ≡ c, a_i ≡ 0 (mod 3), so ⌊a_i/6⌋ = (a_i − 3εᵢ)/6 with εᵢ = 1 when a_i ≡ 3
(mod 6) and 0 when a_i ≡ 0; the r's telescope, so with Σ = Σᵢ D(sᵢ, sᵢ₊₁),

Σᵢ W(sᵢ, sᵢ₊₁) = (Σ − 3 Σᵢ εᵢ)/6.

Σ ≡ 0 (mod 3), and Σᵢ εᵢ ≡ Σ/3 (mod 2), since εᵢ is the parity of a_i/3. Changing σ(sᵢ) moves r_i by 3 and flips εᵢ and εᵢ₋₁ together;
so the vectors (εᵢ) reachable by changing σ on the cycle are exactly those with Σᵢ εᵢ of that fixed parity, and the largest reachable sum
is m when Σ/3 ≡ m (mod 2) and m − 1 otherwise.
- *If Σ ≤ 3(m − 2) for some cycle with m ≥ 3:* when Σ/3 ≡ m (mod 2), take Σεᵢ = m > Σ/3; otherwise Σ/3 ≡ m − 1 and Σ/3 ≤ m − 2 force
  Σ/3 ≤ m − 3, and take Σεᵢ = m − 1 > Σ/3. Either way the cycle is negative for that σ (values off the cycle chosen freely), so σ does
  not occur and S is constrained.
- *If S is constrained:* some σ gives a negative simple cycle, so Σ < 3 Σεᵢ with Σεᵢ ≡ Σ/3 (mod 2), hence Σ/3 ≤ Σεᵢ − 2 ≤ m − 2. For
  m = 2 this would need Σ ≤ 0, but D(s, t) + D(t, s) ≥ 3 for s ≠ t (a closed walk through t weighs ≡ 0 (mod 3) by (i) and is
  positive); so m ≥ 3 and Σ ≤ 3(m − 2). ∎

**Corollary 4.** On a disc every pair and every singleton is free, and a bond B of m members (m ≥ 3) has a cyclic order of all of its
members with D-sum at most 3(m − 2).

*Proof.* Freeness of sets of at most two members is the case m ≤ 2 of Proposition 3. If B is a bond, some m′ ≥ 3 of its members have a
cyclic order with D-sum ≤ 3(m′ − 2); those members form a constrained set (Proposition 3), and every proper subset of a bond is free,
so they are all of B. ∎

## 4. D(x, y) + D(y, x) = 3 · steps apart

**Lemma 5 (no level knot).** On a disc, for every distinction x, the steps-apart distance δ = s(x, ·) is not constant on any knot of T.

*Proof.* By Lemma 0 the clique complex of G is the 2-complex (V, E, T); it is simply connected, and the link of each distinction is a
path or a 6-cycle, which has no induced 4- or 5-cycle. So G is a **bridged graph** (Chepoi 2000, "Graphs of some CAT(0) complexes",
the characterisation of bridged graphs by their clique complexes). In a bridged graph every ball is convex (Soltan and Chepoi 1983;
Farber and Jamison 1987), and the triangle condition holds: two adjacent distinctions at the same distance t ≥ 1 from x have a common
neighbour at distance t − 1 (bridged graphs are weakly modular; Chepoi 1989). Suppose a knot {a, b, c} has δ = t on all three; t ≥ 1.
By the triangle condition a and b have a common neighbour at distance t − 1; the common neighbours of a and b in G are the far
distinctions of the lattice knots on {a, b} that lie in T, and c is at distance t, so it is the far distinction c′ of the other knot
on {a, b}. Likewise the far distinctions a′ across {b, c} and b′ across {c, a} are in V at distance t − 1. Now a′ and b′ are not a
lattice pair, so not adjacent in G, and c is adjacent to both: c lies on a geodesic of length 2 between two members of the ball of
radius t − 1 about x. By convexity c is in that ball, against δ(c) = t. ∎

**Lemma 6.** On a disc, D(x, y) + D(y, x) = 3 s(x, y) for all distinctions x, y.

*Proof.* "≤": walk a least chain's pairs from x to y and back; each pair is used once in each direction, weighing 1 + 2.
"≥": let δ = s(x, ·). Along each forward step δ changes by −1, 0 or 1; around each knot (a forward 3-cycle) the three changes sum to
0 and are not all 0 (Lemma 5), so exactly one is −1, one is 0 and one is +1. Let ω₁ be −2 on the forward steps where δ falls and +1
on the others, and ω₂ be −2 where δ rises and +1 on the others. Each has exactly one −2 around each knot, so each sums to 0 around
every knot, and by Lemma 0 integrates to h₁, h₂ with h(x) ≡ c(x) (mod 3); every increment is ≡ 1 (mod 3) and in {1, −2}, so h₁ and h₂
are height functions. On each forward step h₁ − h₂ changes by −3, 0 or +3 exactly as δ changes by −1, 0 or +1, so h₁ − h₂ = 3δ + const.
By Lemma 2(ii), D(x, y) + D(y, x) ≥ (h₁(y) − h₁(x)) + (h₂(x) − h₂(y)) = 3(δ(y) − δ(x)) = 3 s(x, y). ∎

## 5. The lower bound

**Theorem 7.** On a disc, b(x, y) ≥ s(x, y) + 1 for every two distinctions held by a bond.

*Proof.* Let B be a least bond holding x and y, with m = |B| ≥ 3 members (Corollary 4). Some cyclic order of B has D-sum at most
3(m − 2). That cyclic walk goes from x to y and back to x through the other members, so by the triangle inequality for D its D-sum is
at least D(x, y) + D(y, x) = 3 s(x, y) (Lemma 6). So m − 2 ≥ s(x, y), that is b(x, y) = m − 1 ≥ s(x, y) + 1. ∎

## 6. Lone distinctions

**Lemma 8.** If x is a lone distinction of a disc, in the knot whose forward 3-cycle is x → u → v → x, then D(s, x) = D(s, v) + 1 and
D(x, t) = 1 + D(u, t) for all s, t ≠ x.

*Proof.* The only pairs at x are {x, u} and {x, v}. A walk enters x from v by a forward step (weight 1) or from u by a backward step
(weight 2); since u → v is forward, D(s, v) ≤ D(s, u) + 1, so entering from v is never worse: D(s, x) = D(s, v) + 1. A walk leaves x to
u forward (1) or to v backward (2); since D(u, t) ≤ 1 + D(v, t), D(x, t) = 1 + D(u, t). ∎

So in the cyclic order of any bond through a lone distinction x, x sits between v and u, and contributes D(v, x) + D(x, u) = 2 = D(v, u):
the bond's walk passes x exactly as it would pass the backward step v → u.

## What is proved and what is not

Proved: Lemmas 0 to 2, 5, 6 and 8, Proposition 3, Corollary 4 and Theorem 7, the bridged-graph step resting on the cited theorems.
Not proved here: the upper bound b ≤ s + 1 (false on 64 bonded pairs of `DOUBLE-MEET-20261118-001`'s census), and which facing pairs of
lone distinctions are bonded.

Specific questions:
1. Lemma 0: is the topological argument complete (fan or wheel around each vertex, one boundary curve, flagness)?
2. Lemma 1 and Lemma 2: any gap (e.g. the cochain argument, the residue bookkeeping)?
3. Proposition 3: check the parity bookkeeping and the m = 2 exclusion carefully.
4. Lemma 5: are the cited facts right (Chepoi 2000 characterisation of bridged graphs via simply connected clique complexes with links free of induced 4- and 5-cycles; convex balls in bridged graphs; the triangle condition / weak modularity of bridged graphs)? Give the most reliable references you know, or a self-contained proof of "no level knot" for lattice discs that avoids them.
5. Lemma 6, Theorem 7, Lemma 8: any gap?
6. What would you require changed before this is refereeable?
