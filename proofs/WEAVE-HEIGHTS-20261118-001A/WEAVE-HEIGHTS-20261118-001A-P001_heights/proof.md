# Heights on weave patches: the criterion for constrained sets and the lower bound

Ticket `WEAVE-HEIGHTS-20261118-001A`, 18 November 2026. Written before the frozen checks of ticket B
(`experiments/WEAVE-HEIGHTS-20261118-001B/WEAVE-HEIGHTS-20261118-001B-E001_checks/`). Referee pending. The statements of Proposition 3
and Lemma 6 and the outline of their proofs are the advisor's (claude-fable-5-2, in `DOUBLE-MEET-20261118-001`); the proofs below are
written out in full by the thread, with the bridged-graph step resting on cited theorems. The advisor then refereed this text before the
freeze; its fixes are folded in (definitions, the hypotheses of the cited theorems, a remark weakened).

## Setting

The weave's distinctions are the points (i, j) of Z²; its knots are u(i, j) = {(i, j), (i+1, j), (i, j+1)} and
d(i, j) = {(i+1, j), (i, j+1), (i+1, j+1)}, every one not-all-equal. A **patch** T is a finite set of knots; V is the set of its
distinctions and E the set of its **pairs** (two distinctions in a common knot of T); G = (V, E) is its pair graph. Values are 0 and 1.
For x ≠ y, **steps apart** s(x, y) is the number of knots of a least chain from x to y (consecutive knots sharing a distinction); since
two distinctions are co-knotted exactly when they form a pair, s(x, y) is the distance in G, and we set s(x, x) = 0. **Bond distance**
b(x, y), for x ≠ y, is the least size of a bond holding both, minus one, and infinite when none does. A **lone** distinction lies in
exactly one knot of T. T is a **disc** when its knots are connected through double
meetings, V − |E| + |T| = 1, and the knots around each distinction are connected through double meetings (no pinch).

**Lemma 0 (discs).** If T is a disc, the union of its knots is a closed topological disc, the 2-complex (V, E, T) is simply connected,
and every three pairwise co-knotted distinctions form a knot of T.

*Proof.* (V, E, T) is a subcomplex of the lattice's triangulation of the plane, and the union of its knots is its geometric
realisation. Each lattice pair lies in exactly two lattice knots, so in at most two knots of T. The six lattice knots at a distinction v
form a cycle in which consecutive knots share a pair through v, and two distinct knots at v that share a pair share one through v; so
"connected through double meetings" makes the knots of T at v a connected part of that 6-cycle: a fan or the full wheel. So the union
is a compact connected surface with boundary (connected because the knots are). It lies in the plane, so it is
orientable of genus 0, and its Euler characteristic 2 − (number of boundary curves) equals 1: it has one boundary curve and is a disc,
hence simply connected. Three pairwise adjacent lattice points are always the corners of a lattice knot k. If k ∉ T, each of its three pairs
lies in exactly one knot of T (the other lattice knot on it), so all three are boundary pairs, and they form a closed curve inside the
single boundary curve, which is simple; so the boundary curve is the boundary of k, and the disc is either k (not in T) or its
unbounded complement (T is finite): a contradiction. ∎

## 1. Orientation and residues

Call e₁ = (1, 0), e₂ = (−1, 1) and e₃ = (0, −1) the **forward** steps; every lattice pair is a forward step in exactly one direction.
Each knot is a forward 3-cycle: u(i, j) runs (i, j) → (i+1, j) → (i, j+1) → (i, j) by e₁, e₂, e₃, and d(i, j) runs
(i, j+1) → (i+1, j+1) → (i+1, j) → (i, j+1) by e₁, e₃, e₂. The class c(i, j) = (i + 2j) mod 3 rises by 1 along every forward step.

A **height function** on T is h : V → Z with h(v) ≡ c(v) (mod 3) and h(b) − h(a) ∈ {1, −2} for every forward step a → b of a pair.

**Lemma 1 (states are heights).** On a disc, an assignment σ of values to V is allowed exactly when σ ≡ h (mod 2) for some height
function h, and h is then unique up to adding a multiple of 6. (G is connected, as T is.)

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

**Lemma 2** (T a disc, so G is connected and D finite). (i) Every walk from s to t weighs ≡ c(t) − c(s) (mod 3). (ii) For every height function h, h(t) − h(s) ≤ D(s, t).
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
Lemma 1, σ occurs exactly when some height function h has h ≡ r (mod 6) on S, that is h(s) = r_s + 6k_s for integers k_s. By Lemma 2(ii)
such g = h|S satisfies g(t) − g(s) ≤ D(s, t) for all s ≠ t in S, and by Lemma 2(iii) any such g extends to a height function. So σ occurs
exactly when integers k_s satisfy k_t − k_s ≤ W(s, t) = ⌊(D(s, t) − r_t + r_s)/6⌋ for all s ≠ t. Integer difference constraints are
feasible exactly when the complete digraph on S (without loops) with weights W has no negative cycle, and a negative cycle can be taken
simple, so of m ≥ 2 distinct members. For a simple cycle s₁, …, s_m put a_i = D(sᵢ, sᵢ₊₁) − r_{i+1} + r_i. By Lemma 2(i) and r ≡ c,
a_i ≡ 0 (mod 3), so ⌊a_i/6⌋ = (a_i − 3εᵢ)/6 with εᵢ = 1 when a_i ≡ 3 (mod 6) and 0 when a_i ≡ 0 (also for negative a_i); the r's
telescope, so with L = Σᵢ D(sᵢ, sᵢ₊₁) the cycle's weight is

Σᵢ W(sᵢ, sᵢ₊₁) = (L − 3 Σᵢ εᵢ)/6.

L ≡ 0 (mod 3), and Σᵢ εᵢ ≡ L/3 (mod 2), since εᵢ is the parity of a_i/3. Changing σ(sᵢ) moves r_i by 3 and flips εᵢ and εᵢ₋₁ together;
so the vectors (εᵢ) reachable by changing σ on the cycle are exactly those with Σᵢ εᵢ of that fixed parity, and the largest reachable sum
is m when L/3 ≡ m (mod 2) and m − 1 otherwise.
- *If L ≤ 3(m − 2) for some cycle with m ≥ 3:* when L/3 ≡ m (mod 2), take Σεᵢ = m > L/3; otherwise L/3 ≡ m − 1 and L/3 ≤ m − 2 force
  L/3 ≤ m − 3, and take Σεᵢ = m − 1 > L/3. Either way the cycle is negative for that σ (values off the cycle chosen freely), so σ does
  not occur and S is constrained.
- *If S is constrained:* some σ gives a negative simple cycle, so L < 3 Σεᵢ with Σεᵢ ≡ L/3 (mod 2), hence L/3 ≤ Σεᵢ − 2 ≤ m − 2. For
  m = 2 this would need L ≤ 0, but D(s, t) + D(t, s) ≥ 3 for s ≠ t (a closed walk through t weighs ≡ 0 (mod 3) by (i) and is
  positive); so m ≥ 3 and L ≤ 3(m − 2). ∎

**Corollary 4.** On a disc every pair and every singleton is free, and a bond B of m members (m ≥ 3) has a cyclic order of all of its
members with D-sum at most 3(m − 2).

*Proof.* Proposition 3 requires three distinct members, so sets of at most two members are free. If B is a bond, some m′ ≥ 3 of its
members have a cyclic order with D-sum ≤ 3(m′ − 2); those members form a constrained set (Proposition 3). Every set of |B| − 1 members of a
bond is free, and subsets of free sets are free, so every proper subset of B is free; hence those members are all of B. ∎

## 4. D(x, y) + D(y, x) = 3 · steps apart

**Lemma 5 (no level knot).** On a disc, for every distinction x, the steps-apart distance δ = s(x, ·) is not constant on any knot of T.

*Proof.* We first check the hypotheses of the characterisation of bridged graphs. G has no four pairwise adjacent distinctions (the
lattice has none), so by Lemma 0 the clique complex of G is exactly the 2-complex (V, E, T), which is simply connected. The link of a
distinction v in the clique complex is the graph induced on its neighbours, and two neighbours of v are adjacent in G only if, with v,
they form a knot of T (Lemma 0); so the link is the path or 6-cycle of the fan or wheel at v. (Flagness is what excludes a fan of five
knots whose two end neighbours would otherwise be adjacent through the sixth lattice knot.) A path or a 6-cycle has no induced 4- or
5-cycle. So G is a **bridged graph**: bridged graphs are exactly the graphs whose clique complexes are simply connected and whose vertex
links have no induced 4- or 5-cycles (Chepoi, "Graphs of some CAT(0) complexes", Adv. Appl. Math. 24 (2000), 125–179; the same class as
the 1-skeleta of systolic complexes, Januszkiewicz and Świątkowski, Publ. Math. IHÉS 104 (2006)). In a bridged graph every ball is
convex (Soltan and Chepoi 1983; Farber and Jamison, Discrete Math. 66 (1987)), and the triangle condition holds: two adjacent
distinctions at the same distance t ≥ 1 from x have a common neighbour at distance t − 1, since bridged graphs are weakly modular
(Chalopin, Chepoi, Hirai and Osajda, "Weakly modular graphs and nonpositive curvature", Mem. AMS 268 (2020)). (Theorem numbers are to be
checked against the sources; ticket B checks convex balls, the triangle condition and the conclusion itself on every disc to twelve
knots.) Suppose a knot {a, b, c} has δ = t on all three; t ≥ 1.
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

**Theorem 7.** On a disc, every bond holding two distinctions x ≠ y has at least s(x, y) + 2 members; so b(x, y) ≥ s(x, y) + 1 whenever
some bond holds them (and b is infinite otherwise).

*Proof.* Let B be a bond holding x and y, with m = |B| ≥ 3 members (Corollary 4). Some cyclic order of B has D-sum at most
3(m − 2). That cyclic walk goes from x to y and back to x through the other members, so by the triangle inequality for D its D-sum is
at least D(x, y) + D(y, x) = 3 s(x, y) (Lemma 6). So m − 2 ≥ s(x, y). ∎

## 6. Lone distinctions

**Lemma 8.** If x is a lone distinction of a disc, in the knot whose forward 3-cycle is x → u → v → x, then D(s, x) = D(s, v) + 1 and
D(x, t) = 1 + D(u, t) for all s, t ≠ x.

*Proof.* The only pairs at x are {x, u} and {x, v}, and for s ≠ x, D(s, x) is the least over the neighbours n of x of D(s, n) plus the
weight of the step n → x (and likewise for leaving x). A walk enters x from v by a forward step (weight 1) or from u by a backward step
(weight 2); since u → v is forward, D(s, v) ≤ D(s, u) + 1, so entering from v is never worse: D(s, x) = D(s, v) + 1. A walk leaves x to
u forward (1) or to v backward (2); since D(u, t) ≤ 1 + D(v, t), D(x, t) = 1 + D(u, t). ∎

So if x sits between s and t in a cyclic order (as in Proposition 3), it contributes D(s, x) + D(x, t) = D(s, v) + 2 + D(u, t): the cost
of routing s → v, then the backward step v → u (D(v, u) = 2: it is ≡ 2 (mod 3) and positive, and the step itself weighs 2), then u → t.
(A bond through x need not contain u or v.)

## What is proved and what is not

Proved: Lemmas 0 to 2, 5, 6 and 8, Proposition 3, Corollary 4 and Theorem 7, the bridged-graph step resting on the cited theorems.
The upper bound b ≤ s + 1 is refuted by `DOUBLE-MEET-20261118-001`'s census (64 bonded pairs at s + 2). Not proved here: which facing
pairs of lone distinctions are bonded.

## Checked in ticket B (frozen)

On every disc of the weave to twelve knots (59,564): Lemma 0's flagness, convex balls and the triangle condition (the ingredients of
Lemma 5), no level knot, Lemma 6's identity and Lemma 8's identities, with no exception; on every disc to eight knots (1,080): Lemma 1's
count and Proposition 3 set by set (833,536 sets); on every disc of twelve knots (37,901), Theorem 7 on all 3,365,574 bonded pairs.

## The upper side

Theorem 7 is a lower bound only. The excess of bond distance over steps apart + 1 grows at the rim: 64 bonded pairs at steps + 2 from
ten knots (`DOUBLE-MEET-20261118-001`), and lone pairs of opposite classes facing each other at steps + 3 from twelve knots, where they
break the triangle inequality while bonded (its referee). By Proposition 3 and minimality, b(x, y) + 1 is the least size of a set holding
x and y that has a cyclic order of D-sum at most 3(m − 2) and no such sub-collection; a closed form for it at the rim is not found here.
