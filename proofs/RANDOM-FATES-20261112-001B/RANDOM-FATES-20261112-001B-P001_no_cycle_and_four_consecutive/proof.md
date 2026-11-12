# Knots with no cycle, and growth among the newest four

Status: Partial

Ticket `RANDOM-FATES-20261112-001B`, 2026-11-12. Statements T1 to T4 were stated in
`research/RANDOM-FATES-20261112-001/preregistration.md` before the census of ticket A ran. The canonical K1–K3 test is unchanged.

## Words

The guide's glossary (`publication/knotlab/INTUITIONS.md`): knot pattern, base, free, constrained, bond, bond distance, steps apart,
faithful, contradiction. All knots here are three-place and carry the not-all-equal law (NAE), with no signs. In this record:

- A pattern has **no cycle of knots** when no two knots share two distinctions and there is no cyclic sequence of three or more
  distinct knots K1, …, Kℓ with distinct distinctions c_i ∈ K_i ∩ K_{i+1} (indices mod ℓ). The literature calls it Berge-acyclic,
  and a connected one a hypertree: its incidence graph (distinctions and knots, joined by membership) is a forest.
- For a set S of distinctions in one component, the **span** T(S) is the smallest set of knots that is connected (through shared
  distinctions) and contains S: the union of the knot paths between members of S. The **span-degree** of a distinction is the
  number of knots of T(S) containing it.
- A **tie** and the **ruler at d** are as in the pre-registration: a constrained pair; two distinctions d steps apart whose least
  bond has d + 2 distinctions.

## Standard statement

- **T1 (no cycle of knots).** Let H be a 3-uniform Berge-acyclic hypergraph, finite. Under proper 2-colouring (NAE): H is
  2-colourable; no pair of vertices is restricted; the restricted triples whose pairs are unrestricted are exactly the edges (so H is
  read faithfully); and for two vertices u, v at hypergraph distance d (in the same component) the least restricted vertex set
  containing both whose proper subsets are all unrestricted has exactly d + 2 vertices. Vertices in different components lie in no
  such set.
- **T2 (four consecutive).** If the vertices of a 3-uniform hypergraph are indexed by an interval of the integers (finite, the
  natural numbers or all integers) so that every edge lies within four consecutive vertices (the literature's bandwidth at most 3),
  it is 2-colourable; when the interval has a least element, every proper colouring of an initial segment extends to the whole.
- **T3 (five consecutive).** The complete 3-uniform hypergraph on five vertices (ten edges, bandwidth 4) is not 2-colourable.
- **T4 (the growth processes).** (a) A knot with a distinction in no other knot never makes a pattern a contradiction; so O global
  (0) and T never end. (b) Newest-four growth never ends, whatever its moves. (c) Newest-w growth with w ≥ 5 and closing probability
  q > 0 ends with probability one, and the number of moves before it ends has a geometric tail: from any history it ends within the
  next C(w, 3) moves with probability at least q^C(w,3).
- **By definition (C1).** If knot {a, b, c} makes a pattern a contradiction, the pattern before it allows only 000 and 111 on {a, b,
  c}, so a, b, c are pairwise tied equal.

## Proofs

**Lemma A (a distinction in one knot).** Let K be a knot of a finite pattern P containing a distinction x that lies in no other knot
of P, and let σ be a pattern on a set S of distinctions with x ∉ S. Then σ extends to a state of P if and only if it extends to a
state of P − K. *Proof.* A state of P is a state of P − K. Conversely, take a state of P − K extending σ and reset x: if the other two
distinctions of K are equal, give x the other value, otherwise either value. K is then satisfied, and no other knot contains x. ∎

T4(a) is Lemma A with S empty, applied to the knot just added: every move of O global (0) and of T adds a knot with a new
distinction, so each pattern they reach allows a state.

**Lemma B (the span decides).** Let H be finite with no cycle of knots, S a set of distinctions in one component, σ a pattern on S.
Then σ extends to H if and only if it extends to T(S). *Proof.* Only if: restriction. If: remove the knots of T(S); since the
incidence graph is a forest, each remaining component meets V(T(S)) in at most one distinction. In a component with at least one
knot, take a knot K at greatest distance in the incidence graph from the meeting distinction (or any knot if there is none): K
shares at most one distinction with the rest of H, so it has two distinctions in no other knot, and neither is in S (S ⊂ V(T(S)) and
the component meets V(T(S)) in at most the meeting distinction, which K shares with the rest unless K is the component's only knot,
in which case it still has two other distinctions outside V(T(S))). By Lemma A, σ extends to H iff it extends to H − K. Repeat until
only T(S) and the components of H without S are left; a component without S is a pattern with no cycle of knots, which allows a state
by repeated Lemma A, independently. ∎

**Lemma C (bonds use every leaf).** Let H be finite with no cycle of knots and S a bond of H with |S| ≥ 2. Then S lies in one
component, and in T = T(S) every distinction of span-degree 1 belongs to S. *Proof.* If S met two components, its shadow would be the
product of the shadows of its parts in each, which are free, so S would be free. Now suppose a knot K of T has a distinction x ∉ S of
span-degree 1. Let σ be a pattern on S that does not extend (S is constrained); by Lemma B it does not extend to T, so by Lemma A it
does not extend to T − K. Write K = {x, y, z}.
- If K is a leaf of T, sharing one distinction, say y, with the other knots of T, then z has span-degree 1, and z ∈ S, since
  otherwise K could be dropped from T(S) (both x and z would be outside S), contradicting minimality. In T − K the distinction z is
  in no knot, so σ restricted to S − {z} does not extend to T − K. Since T(S − {z}) ⊆ T − K, Lemma B (applied to H and to the
  pattern T − K, each with no cycle of knots) shows S − {z} constrained in H, against S being a bond.
- Otherwise K is internal and T − K falls into two parts T1 ∋ y and T2 ∋ z with no distinction in common (removing a knot from a
  hypertree whose other two distinctions are both shared). Both parts contain members of S, by minimality of T(S). The states of
  T − K are pairs of states of T1 and T2, so σ fails on T1 or on T2, and S ∩ T1 or S ∩ T2, a proper subset of S, is constrained, by
  Lemma B again. Contradiction.
If T is a single knot (|S| ≤ 3), the same argument applies to its distinctions outside S: each lies in one knot, so a constrained S
contains the whole knot. ∎

**T1.** States exist by repeated Lemma A (T4(a)). Let S be a bond with |S| ≥ 2 and let T = T(S) have t knots. T is a hypertree, so it
has 2t + 1 distinctions, and counting incidences, Σ (span-degree − 1) over its distinctions is 3t − (2t + 1) = t − 1. So at most t − 1
distinctions have span-degree at least 2, at least t + 2 have span-degree 1, and by Lemma C all of those lie in S: |S| ≥ t + 2.
- *No tie.* Nothing is frozen (NAE is complement-closed), so a constrained pair would be a bond of 2 ≥ t + 2 with t ≥ 1 (one
  component, two distinctions): impossible.
- *Faithful.* A constrained triple with free pairs is a bond, so t + 2 ≤ 3, t = 1, and S, which then contains the three span-degree-1
  distinctions of the single knot, is that knot. Every knot is constrained (it forbids 000 and 111) with free pairs (no tie). So the
  hollow triples are exactly the knots.
- *At least d + 2.* If u and v are d steps apart, the knot path between them, unique in a hypertree, has d knots and lies in T, so
  t ≥ d and |S| ≥ d + 2.
- *A bond of exactly d + 2: the alternating chain.* Let the knot path be K1 = {u, a, c1}, K_i = {c_{i−1}, x_i, c_i} for 1 < i < d,
  and K_d = {c_{d−1}, b, v} (for d = 1, S = K1). Put S = {u, a, x_2, …, x_{d−1}, b, v}, of d + 2 distinct distinctions. Take the
  pattern u = a = 0, x_i = (i − 1) mod 2 for 1 < i < d, and b = v = (d − 1) mod 2. It does not extend: u = a = 0 forces c_1 = 1, and
  if c_{i−1} = (i − 1) mod 2 then x_i = c_{i−1} forces c_i = i mod 2; so c_{d−1} = (d − 1) mod 2 = b = v, and K_d is all equal. So S
  is constrained. Remove any one y ∈ S, and let K_i be the
  knot of the path containing y. Any pattern on S − {y} extends: propagate from u along K1, …, K_{i−1} (each knot has one undetermined
  link, which can always be chosen so that the knot is satisfied), from v back along K_d, …, K_{i+1} likewise, then choose y to
  satisfy K_i, which now has only y undetermined; extend to the rest of H by Lemma B. So every proper part of S is free and S is a
  bond. Hence the least bond containing u and v has exactly d + 2 distinctions: bond distance is steps apart plus one at every d. ∎

**T2.** Colour the vertices in order. When vertex i is coloured, the edges whose last vertex is i have their other two vertices among
the three before it, which are already coloured. A colour c is forbidden for i only if some such edge {a, b, i} has a and b both
coloured c. Among three coloured vertices at most one colour occurs twice, so at most one colour is forbidden, and i can be coloured.
Starting from any proper colouring of an initial segment, the same step continues it, by induction. For an index set with no least
element (all integers), every finite set of edges is 2-colourable by the above, so the whole is, by compactness (König's lemma). ∎

**T3.** Any colouring of five vertices with two colours gives one colour to at least three of them, and those three form an edge. ∎

**T4(b).** In newest-four growth a closing knot lies on the four newest distinctions, which are consecutive in order of arrival, and
a knot with a new distinction n has its other two among the three before it. So every pattern it reaches has every knot within four
consecutive distinctions, and allows a state by T2.

**T4(c).** While no new distinction arrives, the w newest distinctions stay the same, and each closing move adds a missing knot on
them. So C(w, 3) consecutive closing moves (or fewer, if knots there are already present) make all knots on the w newest
distinctions present; these contain the ten knots on five of them, so by T3 the pattern is a contradiction. Each move is a closing
with probability q independently of the past, so from any history the growth ends within the next C(w, 3) moves with probability at
least ε = q^C(w,3) > 0. Hence it is still a base after m·C(w, 3) moves with probability at most (1 − ε)^m, which tends to 0. ∎

**C1.** Adding {a, b, c} removes exactly the states with a = b = c. If no state remains, every state before had a = b = c. ∎

## Checks

`check.py` (results in `result.json`):
- **K1** T1 by brute force: on random patterns with no cycle of knots up to 13 distinctions, every allowed state enumerated, no
  tie, hollow triples exactly the knots, and the least bond of every pair (searched over all sets) of size d + 2.
- **K2** T2 exhaustively: every set of knots within four consecutive of 8 distinctions (2^16 sets) allows a state.
- **K3** T3: the ten knots on five distinctions allow no state; the least number of knots of a contradiction with every knot within
  five consecutive distinctions, on 5 to 8 distinctions, recorded.

## Remaining obligations

- Referee pass on T1 to T4.

## Literature

- Berge-acyclic hypergraphs and their 2-colourability are classical; the least-bond statement of T1 and the alternating chain were
  not found stated (bounded search). T2 is an elementary greedy argument; T3 is the pigeonhole principle (the literature's K5^(3)
  is not 2-colourable). T4 applies them to processes defined in this epic.
