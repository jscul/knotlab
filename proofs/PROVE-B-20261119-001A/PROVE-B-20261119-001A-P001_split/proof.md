# The split formula, offshoots, and a counterexample to Claim B for arrangements in general

## Standard statement

Take a graph G with a distinguished vertex o, and split o into new vertices N. Each n ∈ N takes over one o-edge from each vertex of
a set P(n), and gets f(n) ≥ 1 new parallel edges to o. Then every cocircuit of the split graph comes from a family of pairwise
disjoint, non-adjacent vertex sets with their cocircuits, plus a set of new vertices joining them, and its size is given by an
explicit discount formula. Pendant new vertices (|P(n)| = 1) never change the least cocircuit through two old edges. A
cocircuit-distance isometry that preserves the new vertices' attachment data need not extend to the split graphs.

## Nearest known result

`EXTEND-ROUND-20261119-001` (Lemma A, Claim B\*, Claim B unproved) and its referee; `PARENT-RULE-20261119-001` (Theorems 1 to 3,
the case T = ∅ here). [Design](../../../research/PROVE-B-20261119-001/preregistration.md).

## 0. Setting

- **Arrangements and tables.** As in EXTEND-ROUND: a connected arrangement a, its junction graph G = (J ∪ {o}, E), the table T,
  the live junctions L.
- **The round.** The law's round makes new junctions N with parent sets P(n) ⊆ L, k(n) = |P(n)|, taken loose edges x_{n,u} (one
  per parent, rerouted u–n) and f(n) fresh edges n–o, with f(n) ≥ 1, so that the next stage is open.
- **The new graph.** G′ is the new junction graph. δ(S) is the cut of S ⊆ J in G, and δ′ the cut in G′.

## 1. The split formula

**Lemma C.** The bonds of G′ are the cuts δ′(S ∪ T), with S ⊆ J and T ⊆ N, such that S ∪ T is non-empty and connected in G′ and
its complement together with o is connected in G′. For each of them:
1. |δ′(S ∪ T)| = |δ(S)| + Σ_{n ∈ T} (f(n) + |P(n) ∖ S| − |P(n) ∩ S|);
2. a shared old edge lies in δ′ exactly when it lies in δ(S), and a taken edge x_{n,u} lies in δ′ exactly when
   [u ∈ S] ≠ [n ∈ T];
3. S is the union of pairwise disjoint, non-adjacent sets S_1, …, S_m, each connected, and δ(S) = ∪ δ(S_i). The complement of
   each S_i together with o is connected in G, so each δ(S_i) is a bond of G.

*Proof.* A bond of a connected graph is a cut between a connected vertex set and its connected complement. Take o on the outer
side and write the inner side as S ∪ T.
- **Item 1** counts the cut's edges:
  - the old shared edges between S and J ∖ S;
  - the taken edges cut, those with exactly one of u ∈ S, n ∈ T;
  - the fresh edges of T;
  - the loose edges of junctions in S that no new junction takes. There are none: the round takes every loose distinction of the
    live junctions, and junctions that are not live have none.
  So |δ(S)| loses the taken edges of n ∈ T with u ∈ S and gains those with u ∉ S, plus f(n).
- **Item 2** is the same count.
- **Item 3.** New junctions meet only their parents and o, so the components of S in G are glued only through T. The complement
  of S ∪ T reaches o in G′. Contracting N ∪ {o} to o gives G, and keeps the complement of each S_i connected to o, because it
  contains the complement of S. ∎

With T = ∅ this is PARENT-RULE's Theorem 3 (old bonds survive, T′ ≤ T on old pairs).

## 2. Offshoots

**Lemma O.** Let n be an offshoot (k(n) = 1, parent u; under the fewest counts f(n) ≥ 2).
1. Removing n from T in any feasible (S, T) with u ∈ S gives a feasible (S, T ∖ {n}). It is cheaper by f(n) − 1 ≥ 1, and its cut
   holds every old edge the first held, except possibly x_{n,u}.
2. Hence no least bond through two old edges other than x_{n,u} uses n.
3. T′(fresh of n, y) = T′(x_{n,u}, y) + f(n) − 1, for every y outside n's own edges.
4. If every new junction is an offshoot, T′ = T on old pairs, and the whole next table is a function of T and of the round's
   output (which taken edge each offshoot holds, and its f).

*Proof.*
1. In (S, T) with n ∈ T, n's only neighbour in S ∪ T is u, so removing it keeps S ∪ T connected. Its fresh edges then reach o
   directly, and the complement stays connected. The cost changes by −(f(n) + |P∖S| − |P∩S|) = −(f(n) − 1). Only n's own edges
   change membership.
2. Follows from item 1.
3. A bond through a fresh edge of n has n inside. If u ∉ S, then S ∪ T = T ∋ n is connected only if T = {n} and S = ∅, which is
   n's star. Otherwise u ∈ S, and item 1 gives the cost of the corresponding bond without n plus f(n) − 1.
4. Follows from items 1 to 3. ∎

**Corollary O.** If a table isometry carries each live junction's loose distinctions onto a live junction's, a round of offshoots
only extends it. In particular, offshoots made by hand never break a matching (HUNT-SHORTEN's H1, now proved).

## 3. A counterexample to Claim B for arrangements in general (Proposition X)

Take seven junctions, written as their distinctions:
- a = {p₁, p₂, q₁, q₂};
- b = {p₁, p₂, s₁, s₂, t₁, t₂};
- c = {q₁, q₂, s₁′, s₂′, t₁′, t₂′};
- u = {s₁, s₂, ℓ_u};
- v = {t₁, t₂, ℓ_v};
- u′ = {s₁′, s₂′, ℓ_u′};
- v′ = {t₁′, t₂′, ℓ_v′}.

So a shares two distinctions with each of b and c, and b and c each share two with each of their two children. This is the
advisor's construction, checked by computation in ticket B's control (`control.json`).
- **The renaming.** Let φ swap p₁ and q₁ and fix everything else.
  - It is an isometry of the table.
  - It keeps the round's reading: the live junctions are u, v, u′, v′ with one loose distinction each, and the family is
    {{u, v}, {u′, v′}}.
  - It does not carry the equations.
- **The round.** The law's round makes n = {ℓ_u, ℓ_v, one fresh} and n′ = {ℓ_u′, ℓ_v′, one fresh} (pairs, with f = 1).
- **The failure.** In the next table, T′(p₁, p₂) = 2, through the bond δ′({b, u, v, n}). But T′(q₁, p₂) = 3, since only a's star
  holds both. So the extension of φ is not an isometry, and Claim B fails for this connected arrangement.
- **What it needs.** The arrangement is a start, not a reached stage: its live junctions share two distinctions with their parent,
  which no reached stage of round ≥ 1 allows (PARENT-RULE Lemma 1: a new junction meets each parent once). So it does not decide
  Claim B for reached stages.

## 4. Where the proof stalls for reached stages

The next table reads, for each bond, which live junctions it holds (Lemma C), and the table records only the least bond through
each pair. Claim B for reached stages would follow from a tie lemma. Suppose a bond holding no live junction ties in size with a
bond holding more than (k + f)/2 of some parent set. Then no isometry keeping the reading trades a pair read by both for a pair
read only by one. That lemma is not proved here.

Proposition X's mechanism names the smallest configuration to hunt in reached stages:
- a junction with no loose distinction whose distinctions split evenly between two holders, giving a class-breaking swap that is
  a table symmetry;
- a tie between its star and a bond holding a full parent set with k > f.

In a reached stage the split needs knots sharing two or more, so start knots. Ticket B hunts it over every start of 3 or 4 knots
with shared multiplicities up to 4 (3 knots) or 3 (4 knots), grown up to three rounds.
