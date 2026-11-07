# Open ends make a tower stretch

Status: Proved

Ticket `LOGIC-AXIS-20261107-001D`, 2026-11-07.

## Standard statement

Let G be a finite graph in which every vertex has degree 3, and let some edges be "half-edges": edges
whose other end is a common extra vertex ∞. Put a binary variable on each edge, and require the three
variables at every ordinary vertex to sum to 0 mod 2 (the Tseitin system of G with ∞ unconstrained).

- The implied parity checks are the cuts δ(U) for sets U of ordinary vertices.
- The minimal ones of size >= 3 are the bonds.

Replace one vertex v by a connected gadget whose three designated half-edges take over v's edges.

1. The old check (the three edges at v) is still implied exactly when the gadget has no other
   half-edges. In that case the replacement does not change any implied check among the old edges.
2. If G is a tree apart from ∞, the least bond containing two half-edges has exactly
   (number of vertices on the tree path between them) + 2 edges.

## Nearest known result

- **Cuts and cycles.** That the implied parity checks of a Tseitin system are the cuts, and the minimal
  ones the bonds, is classical: this is cycle/cut space duality.
- **Statement 1** is the observation that the sum of a gadget's vertex checks is its boundary.
- **Statement 2** is the edge count of a subtree.
- **Classification:** `known-with-delta`, at folklore level for the mathematics. The delta is the reading:
  - a substitution law keeps its old knot exactly when it adds no open end;
  - the ruler stretches only through open ends;
  - the exact bond distance on tree towers.

## Setting

- **Hub-free parity laws.** In a hub-free parity law every knot has three distinctions, and every
  distinction lies in at most two knots. Draw it as its knot graph:
  - knots are vertices;
  - a shared distinction is an edge;
  - a distinction held by one knot is an edge to the unconstrained outside vertex ∞. These are an
    original *leg*, or an *open end*: a distinction left free on one side, a loop's open distinction.
- **Knots of the law.** Implied checks are cuts δ(U) with ∞ ∉ U, so the law's knots (K1–K3) are the
  bonds with at least 3 edges.
- **Bond distance** is as in NATIVE-NETWORK-20261021-001.
- **Substitution.**
  1. A gadget Γ is a connected hub-free knot graph with three legs and possibly some open ends.
  2. Substituting Γ for a knot v removes v and inserts a copy of Γ, joining v's three distinctions to
     Γ's legs.
  3. A tower applies this to every knot, level after level.

## 1. The criterion

**Proposition 1.** Substitute a connected gadget Γ for a knot v of a hub-free law L, giving L′, and let
e_1, e_2, e_3 be v's distinctions. Then:

- (a) e_1 + e_2 + e_3 = 0 is implied in L′ iff Γ has no open end.
- (b) If Γ has no open end, then for every set S of distinctions of L, S supports an implied check of
  L′ iff it does in L. So L′ is a conservative extension of L, and every knot of L is a knot of L′.

*Proof.*
1. **Copies are all or nothing.** Write C for the copy of Γ's knots in L′. A cut δ′(U′) contains no
   internal edge of C exactly when U′ ∩ C is ∅ or all of C, because Γ is connected.
2. **(a), the direction "no open end".** With U′ = C, δ′(C) is the three legs plus Γ's open ends. With
   no open ends this is {e_1, e_2, e_3}.
3. **(a), the direction "an open end".** Suppose Γ has an open end and δ′(U′) = {e_1, e_2, e_3}.
   Then U′ ∩ C ∈ {∅, C}.
   - If U′ ⊇ C, the open ends of C lie in the cut, which is a contradiction.
   - If U′ ∩ C = ∅, then U′ is a set of knots of L other than v whose cut is exactly v's three
     edges, so δ_L(U′ ∪ {v}) = ∅. That makes U′ ∪ {v} a union of components of L avoiding ∞,
     impossible when every component of L meets ∞. In the towers, every level's graph is connected
     and has the original legs at ∞.
4. **(b).** A cut of L′ that uses only old distinctions has U′ ∩ C ∈ {∅, C}.
   - Setting U = (U′ ∖ C) ∪ ({v} if C ⊆ U′) gives δ_L(U) = δ′(U′), since δ′(C) = δ_L({v}) when Γ
     has no open end.
   - Conversely, every δ_L(U) arises this way.
   - For parity laws, X_S is fixed by the implied checks supported in S, so projections to old
     distinctions agree, and knots of L stay knots. ∎

**Corollary (collapse without open ends).** In a tower of a gadget without open ends:
- every step is conservative, so by LOGIC-AXIS A, Proposition 6, bond distances between existing
  distinctions never increase;
- the original legs stay a knot, at bond distance 2, at every level;
- each leg lies in a new three-place knot at every level (the copy of the knot holding it), so its
  bond-2 neighbours number at least 2(k + 1) at level k and grow without bound.

The 2026-10-20 parity refinement is such a gadget (the corner triangle G0). This explains its failure:
it adds open bits as closed cycles of knots, never as open ends, and its coarse knots never dissolve.

## 2. Trees

**Proposition 2.** Suppose the knot graph of a hub-free law is a tree apart from ∞. Let e and f be
outside edges at knots u and v, and let P be the set of knots on the tree path from u to v. Then
δ(e, f) = |P| + 1, attained by the cut δ(P).

*Proof.*
1. A bond δ(U) contains e and f iff u, v ∈ U. Its side U is connected, so U ⊇ P.
2. A connected set U of knots in a tree spans |U| − 1 internal edges. So
   |δ(U)| = 3|U| − 2(|U| − 1) = |U| + 2, which is least for U = P.
3. δ(P) is a bond: P is connected, and every subtree hanging off P has a leaf with an outside edge,
   so the complement is connected through ∞. ∎

**Corollary (the star tower).** Take the star gadget G1: a centre knot joined to three corner knots,
each corner holding one leg and one open end.
- Its towers are trees.
- Each knot on the path between legs a and b becomes three knots on the next level's path
  (corner, centre, corner).
- So the path has 3^k knots and δ_k(a, b) = 3^k + 1.
- With four copies per level, the self-similarity ratio is log 4 / log 3.

## Reading

**Interpretation, not a theorem.**
- **Growth by substitution.** A tower grows its system and adds open bits at every level. Its ruler
  stretches only if those bits are open ends: distinctions held by one knot, left free on one side.
- **Closed cycles are not enough.** Bits added as closed cycles of knots leave the old knot in place.
  The original distinctions then stay bonded, a collapse like that of Ledrappier's frozen law
  (ticket B).
- **What stretching means.** In this sense, space expands between existing distinctions exactly where
  growth adds open ends. Ticket C measured the resulting stretch factors.

## Checks

`check.py` runs four checks, each with a rejected control (`result.json`):
- **The criterion.** All 304 gadgets agree: the 4 named ones and 300 random connected cubic gadgets
  with 0–3 open ends.
- **Conservativity.** 1,560 random comparisons of implied checks across a step, for 26 gadgets without
  open ends.
- **The G0 tower, levels 0–4.** The corners stay a knot, and leg a's bond-2 neighbours are 2, 4, 6, 8
  and 10.
- **Trees.** 150 random cubic trees by exhaustive search, and the star tower. Exhaustive values at
  levels 0–2 are 2, 4 and 10; path cuts at levels 3–5 have 27, 81 and 243 knots. The control is the
  prism, a non-tree where the path formula gives 5 against the true 4.

## Nonclaims

- Statement 1 concerns hub-free gadgets. With hubs (a distinction in three knots) the old knot can
  survive for other reasons. Ticket C's G6 keeps it, and Proposition 1 says nothing about such
  gadgets.
- Statement 2 needs a tree. The prism tower is not one.
