# Only parity is rebuilt by native gadgets of its own copies

Status: Proved

Ticket `GEOMETRY-LAW-20261029-001A`, 2026-10-29.

## Standard statement

Let K ⊆ {0, 1}³ be a relation in which every two coordinates are unconstrained (each projection onto two coordinates is all of
{0, 1}²), other than the full cube. Equivalently, the excluded set E = {0, 1}³ \ K is a nonempty independent set of the 3-cube;
there are 34 such relations. Build a *gadget* from m ≥ 2 copies of K, each with any order of its coordinates, by identifying
variables in pairs between distinct copies (no variable is shared by two places of one copy, and none by three places), so that
exactly three variables, the *legs*, stay single and the copies form a connected network; its relation is the projection onto the
legs.
- If K is a parity relation x + y + z = c over GF(2), every gadget gives back K.
- Otherwise every gadget excludes strictly fewer leg tuples than K, so K is never rebuilt, and substituting gadgets repeatedly
  reaches the full relation within three levels.
- No such K has a coordinate symmetry group inside the rotations of a cyclic order of its three coordinates; 96 of the 742
  analogous relations on four bits do.

## Nearest known result

- **Inside the repository (used here).**
  - `SURFACE-GLUING-20261024-001B-P001`: hub-free gluing keeps excluded tuples pairwise non-adjacent, an exact count for gluing,
    at most half of the tuples excluded, and no parity of dimension three or more without a parity knot.
  - `NATIVE-HARDNESS-20261024-001B-P001`: in an unsatisfiable connected closed hub-free network without parity knots, the graph
    is a cactus, every cycle is an odd wire cycle, and the two sides of every bridge force opposite values (Lemma 1, Corollary 3).
    Theorem 3 below is a consequence of that structure for networks with three legs.
- **Outside.**
  - Expressibility with two occurrences per variable: Feder, *Fanout limitations on constraint systems*, TCS 255 (2001);
    Dalmau and Ford (2003); Kazda, Kolmogorov and Rolinek, *Even delta-matroids and the complexity of planar Boolean CSPs*
    (2019); closures of signatures under such gadgets (Holant clones). These ask which relations gadgets define, not which
    relations are rebuilt by gadgets of their own copies.
  - Higuchi and Mézard, *Decimation flows in constraint satisfaction problems*, J. Stat. Mech. (2009) P12009: decimation of
    hard random constraint problems produces linear constraints over GF(2). Here, exact substitution (not decimation) keeps
    only linear relations.
  - Hierarchical-lattice renormalization (Migdal, Kadanoff; Berker and Ostlund) takes the substitution rule as given.
- **Classification.** No overlap found in a bounded scan of four queries (candidate local delta). Theorem 1 is classical (Tseitin).

## Setting

- **Knots.** The 34 relations of the standard statement. A *placement* of K is K with its coordinates permuted.
- **Gadgets.** A *native gadget* of K: a connected loopless network of m ≥ 2 copies of K, each in some placement, in which every
  internal variable lies in exactly two distinct copies and three variables (the legs) lie in one copy each. Counting places,
  3m = 2·(internal variables) + 3, so m is odd and the network has h = (m − 1)/2 ≥ 1 independent cycles. Its *relation* R_Γ is
  the set of leg tuples l that extend to an assignment of the internal variables satisfying every copy; E_Γ = {0, 1}³ \ R_Γ.
  Pinning the legs to l gives a closed network Γ_l, and l ∈ E_Γ exactly when Γ_l is unsatisfiable.
- **Wires and strong values.** A *wire* is a relation on two bits excluding exactly 01 and 10 (*equal*) or exactly 00 and 11
  (*unequal*). A value v is *strong* for coordinate k of K when the face x_k = v of K is a wire, that is, when two excluded tuples
  have x_k = v. The excluded set splits as |E| = |E^{k,0}| + |E^{k,1}|, and each part has at most two elements.
- **Types of non-parity knots.** Since |E| ≤ 3 when K is not parity, each coordinate has at most one strong value.
  - *No wire face* (12 knots): the 8 atoms (|E| = 1) and the 4 knots excluding an antipodal pair. No coordinate has a strong value.
  - *Two excluded at distance two* (12 knots): the two excluded tuples agree on one coordinate k*, and their common value v* there
    is the only strong value of K.
  - *Three excluded* (8 knots): E is three tuples of one parity class. Every coordinate has exactly one strong value.

## Theorem 1 (parity is rebuilt by every gadget)

If K = {x : x₁ + x₂ + x₃ = c}, then R_Γ = K for every native gadget Γ, in every placement.

*Proof.* Adding the m equations of the copies, every internal variable appears twice and cancels, so l₁ + l₂ + l₃ = m·c = c (m is
odd). Conversely the copies' equations form the vertex equations of a connected graph whose edges are the internal variables,
with right-hand sides fixed by c and the legs. Such a system is solvable exactly when the right-hand sides add up to 0, which is
the condition above. Placements do not matter, since K is symmetric. ∎

## Lemma 2 (legs beyond every bridge)

Let K be a non-parity knot and l ∈ E_Γ. Then both sides of every bridge of Γ_l contain a leg of Γ.

*Proof.* Let f be a bridge and S a side without legs. By Lemma 1 of `NATIVE-HARDNESS-20261024-001B-P001`, S allows exactly one
value of f, so S with f pinned to the other value is an unsatisfiable connected closed network with exactly one pin and no parity
knot. By Corollary 3 there, it is a cactus in which every cycle is an odd wire cycle. It has a cycle: a tree of copies with three
places each would have at least three free places, and it has one. Take a leaf of its block tree. A leaf block is a cycle (a
bridge to a copy of degree one would need two free places at that copy). Every copy of a leaf cycle other than its cut copy has
its third place free of the cycle and not on a bridge, so pinned: a cycle has at least two copies, so this uses at least one pin.
If the block tree has one block, every copy of the cycle is pinned, at least two pins. Otherwise it has at least two leaves, at
least two pins. Either way more than one pin is needed, a contradiction. ∎

## Theorem 3 (the other knots lose excluded tuples)

Let K be a non-parity knot and Γ a native gadget of K. Then
- E_Γ = ∅ if K has no wire face;
- |E_Γ| ≤ 1 if K excludes two tuples at distance two, and E_Γ ≠ ∅ only when Γ is the triangle of three copies with one leg each;
- |E_Γ| ≤ 2 if K excludes three tuples, and |E_Γ| ≤ 1 unless some copy carries two legs.

In particular |E_Γ| < |E| in every case.

*Proof.* Let l ∈ E_Γ. By Corollary 3 of `NATIVE-HARDNESS-20261024-001B-P001`, the graph of Γ is a cactus and every cycle of Γ_l is
an odd wire cycle: with each copy's third place at its forced value (its pin, or the value forced from beyond its bridge, Lemma
1 there), every copy's face on its two cycle places is a wire and an odd number of these wires are unequal. Γ has a cycle (h ≥ 1).
- **No wire face.** No face of K is a wire, so no cycle is a wire cycle, a contradiction. So E_Γ = ∅.
- **Legs on cycles are fixed.** A copy on a cycle has two cycle places, so it carries at most one leg, on its third place. Its face
  is a wire only if that leg takes the strong value of its coordinate: one choice.
- **A copy with one leg off the cycles.** Its other two places are bridges f₁, f₂. By Lemma 1 there the far sides force constants
  c₁, c₂, and the side through the copy must force ¬c₁ on f₁. So, with f₂ = c₂, the copy allows f₁ = ¬c₁ and excludes f₁ = c₁:
  (λ, c₁, c₂) ∈ E for its leg value λ (in its placement). Two tuples differing only in λ are adjacent, so at most one λ works:
  the leg is determined by (c₁, c₂).
- **Branches.** In a cactus the parts hanging from different copies of one cycle are disjoint. So, by Lemma 2, the copies of a
  cycle need legs in pairwise distinct branches (on their third places or beyond their bridges).
- **Case 1: a copy d carries two legs.** It is off the cycles, with one bridge f to the rest S, which holds the third leg. At most
  one copy carries two legs, since a copy with three would be the whole gadget.
  - *The shape of S.* A copy of S off the cycles would have at least two bridges inside S, and Lemma 2 would need a leg beyond each
    one other than the bridge toward d; S has a single leg, so there is no such copy. A cycle of S has legs available in at most
    two branches (toward d, and toward the third leg), so it is a digon. Hence S is a chain of digons joined by bridges, from the
    copy at f to the copy holding the third leg.
  - *The count.* The third leg takes its copy's strong value, so S, whose only pin is that leg, forces a fixed constant c on f.
    The copy d alone must then allow only ¬c, so (l_a, l_b, c) ∈ E in its placement: at most |E^{f, c}| ≤ 2 pairs. Hence
    |E_Γ| ≤ 2.
- **Case 2: the legs sit on three distinct copies.** Let u be a copy off the cycles carrying a leg. It has two bridges, and by Lemma 2
  each far side holds exactly one of the other two legs. Let w hold the leg beyond one of them. If w were off the cycles, it would
  have a second bridge leading away from u, with no leg beyond it, against Lemma 2. So w lies on a cycle and its leg is fixed, and
  so is the constant its side forces. Both constants at u are fixed, so u's leg is fixed. Every leg is fixed: |E_Γ| ≤ 1.
- **Three excluded.** Cases 1 and 2 give |E_Γ| ≤ 2 < 3.
- **Two excluded at distance two.** The only strong value is v* at k*, and the face x_{k*} = v* is the same wire W, equal or
  unequal, in every copy (swapping its two coordinates does not change a wire). So a wire cycle has every third place at
  coordinate k* with value v*, and it is odd exactly when its length is odd and W is unequal.
  - Digons are never odd, so Case 1, whose cycles are digons, gives E_Γ = ∅.
  - In Case 2 every cycle has length at least three, with legs in at least three distinct branches, so there is one cycle, of length
    three, with one leg in each branch. If one of its copies reached its leg through a bridge, the copy holding that leg would lie
    on a second cycle (as for w above), which would need three more branches with legs. So each copy holds its leg: Γ is the
    triangle, and then the legs are fixed.
  - So E_Γ ≠ ∅ only for the triangle with W unequal, and |E_Γ| ≤ 1 < 2. ∎

## Corollary 4 (patterns of patterns)

- **Only parity is rebuilt.** A non-parity knot K is never the relation of a native gadget of its copies, in any placement, since
  |E_Γ| < |E|. Parity is rebuilt by every native gadget (Theorem 1).
- **Towers die within three levels.** Replace each copy in a network by a native gadget of the knot, then each copy of the new
  knot by a gadget of that knot, and so on. Co-independence is kept (`SURFACE-GLUING-20261024-001B-P001`, Lemmas 2 and 3), so every
  level carries a knot or the full relation. The excluded count drops at every level that is not parity, from at most 3, so after
  at most three constrained levels the relation is full.
- **The census (check 3).** The bounds are attained: two for three excluded tuples (only with a copy carrying two legs), one for
  two excluded at distance two (only by the triangle). The longest chain of constrained levels has three knots.

## Proposition 5 (no orientation at three places)

- **Three bits.** Every knot's coordinate symmetry group contains a transposition.
  - |E| = 1: two coordinates of the excluded tuple are equal; swapping them fixes it.
  - Two excluded at distance two: they agree on k* and differ on the other two coordinates, and swapping those fixes or exchanges
    the two tuples.
  - An antipodal pair: two coordinates of one tuple are equal; swapping them fixes both tuples.
  - Three excluded: E is a parity class minus one tuple w; swapping two equal coordinates of w fixes w, the class and E.
  - Parity is symmetric.
  The rotations of a cyclic order of three coordinates are the identity and the two 3-cycles, which contain no transposition.
  So no placement can orient a vertex: a native network of three-place knots carries no rotation system.
- **Four bits.** Of the 742 relations on four bits with every three coordinates unconstrained, 96 have their symmetry group
  inside the rotations of some cyclic order of the coordinates (48 with trivial symmetry). Orientation first appears at four places.

## Consequence for geometry from a law

A set-level law of three-place Boolean knots, glued natively, fixes the topology of its network (a surface,
`SURFACE-GLUING-20261024-001A-P001`) and nothing finer of this kind:
- no orientation at any knot (Proposition 5);
- no scale: no non-parity law survives being rebuilt from its own copies. Parity survives in every shape, so it prefers none
  (Corollary 4).

Self-gluing (one copy glued to itself, making one loop play two roles) and hubs change this: with self-gluing some non-parity knots
are rebuilt, and the hub relation all-equal is rebuilt by native gadgets (check 6).

## Checks

`check.py` (standard library), with `result.json`:
- **0.** The four dependency artifacts are bound by hash.
- **1.** The 34 knots, their types (12, 12, 8, 2) and their strong values.
- **2.** Symmetry: three-bit stabilizer sizes 6 (7 knots) and 2 (27), each with a transposition; none orients a vertex. Four bits:
  742 knots, 96 orient a vertex, 48 of them with trivial symmetry.
- **3.** Exhaustive census of native gadgets with 3 copies (2 shapes) and 5 copies (9 shapes), every placement. Parity is rebuilt
  by every gadget, no other knot is rebuilt, the bounds hold and are attained as stated, and every arrow of the flow decreases the
  excluded count. The longest chain of constrained levels is 3.
- **4.** For all 798 excluded leg tuples of the census, the pinned network is a cactus, every cycle is an odd wire cycle under the
  forced values, and both sides of every bridge contain a leg.
- **5.** 180 random native gadgets of 7, 9 and 11 copies, each with every knot in random placements (6120 evaluations): the
  bounds hold.
- **6.** Controls that must fire:
  - with self-gluing, non-parity knots are rebuilt by gadgets of three copies;
  - all-equal, which is not co-independent, is rebuilt by both native shapes of three copies;
  - the mutated bound "at most one for three excluded tuples" is violated by the census.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Theorem 1 | Linear algebra over GF(2) (Tseitin) | Classical |
| Lemma 2, Theorem 3, Corollary 4 | The cactus structure of native contradictions (`NATIVE-HARDNESS-20261024-001B`), applied to networks with three legs; the question (which laws survive being rebuilt from their own copies) came from the program's patterns of patterns | Candidate local delta; no overlap found in a bounded scan |
| Proposition 5 | Orbits of coordinate permutations on the 3-cube and the 4-cube | Elementary; the four-bit count is computed |

## What this does not show

- Nothing about counts (numbers of hidden witnesses): the statements are about which leg tuples are allowed. Weighted versions can
  differ.
- Nothing about gadgets with hubs or self-gluing, beyond the controls.
- Nothing about four-place knots beyond the orientation count (ticket B).
