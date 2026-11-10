# Boards of laws that name no relation

Status: Proved

Ticket `BOARD-DIST-20261110-001A`, 2026-11-10. Pre-registered in commit c3b6a0bde before the proof attempt and before ticket B's
census ran.

## Setting

- **Names.** The reduced words in x, y and their inverses X, Y: the free group F2. Each name u has four neighbour names ux, uX, uy
  and uY, the products reduced.
- **Distinctions.** A value s(u) in a finite alphabet Q for each name, and an identity distinction e(u, v) for each pair of names,
  read "u and v are one place".
- **Board axioms.** Transitivity e(u, v) ∧ e(v, w) → e(u, w); letter closure e(u, v) → e(ug, vg) for each letter g; constancy
  e(u, v) → s(u) = s(v). Identity is reflexive and symmetric by definition.
- **A law.** Finitely many clause templates. A template has base names u_1, …, u_k; its literals are value literals on s(u_i a) and
  identity literals e(u_i a, u_j b), for offsets a, b (reduced words). It is instantiated at every tuple of names, coincident ones
  included, so every clause names finitely many variables. The board axioms are templates. A **value law** has only value literals
  at one base name.
- **Names no relation.** Every identity literal relates the same offset of two base names, e(u_i a, u_j a). A literal relating two
  different offsets, such as e(u, uxyXY), names the relation between them: at coincident bases it says that a word acts trivially.
- **Allowed state.** An assignment satisfying every instance. Its board is the relation e.
- **Types.** Let r be the longest offset in the law. The type of a name u in a colouring s is the map g ↦ s(ug) on the ball B_r.

Every template is invariant under left translation u ↦ hu (offsets act on the right), so the allowed states are too.

## Theorem 1. Boards are Schreier graphs

**Statement.**
1. The boards of allowed states are exactly the right congruences of F2: equivalences with u ~ v ⇒ ug ~ vg.
2. These correspond to the subgroups H of F2, by u ~ v ⇔ uv⁻¹ ∈ H; the places are the cosets Hu and the letters act by Hu ↦ Hug,
   the Schreier graph of H.
3. On the ball B_L, the board states of the truncated CNF (transitivity among the names of the ball, letter closure whenever ug and
   vg lie in it) are exactly the restrictions to B_L of right congruences, and every one is the restriction of a finite-index one.

**Proof.**
1. Transitivity and letter closure say exactly this. Letter closure applied letter by letter gives u ~ v ⇒ uw ~ vw for every word
   w.
2. Let H be the class of 1. If u ~ v then uv⁻¹ ~ vv⁻¹ = 1; if uv⁻¹ ~ 1 then u = uv⁻¹v ~ v. H is a subgroup: if h ~ 1 and k ~ 1
   then hk ~ k ~ 1, and h⁻¹ = 1·h⁻¹ ~ hh⁻¹ = 1. Conversely uv⁻¹ ∈ H defines a right congruence for every subgroup H.
3. Restrictions of right congruences are board states. Conversely, let ~ be a board state on B_L.
   - Make a labelled graph on its classes, with an edge [u] → [ug] whenever u and ug lie in B_L. Letter closure makes it well
     defined, and also injective: if ug ~ vg, closure under g⁻¹ gives u ~ v.
   - So each letter is a partial injection of the finite set of classes. Extend each to a permutation of that set.
   - The result is a finite Schreier graph, connected because every name of the ball is read from [1] along its prefixes, which lie
     in the ball.
   - Reading a name u ∈ B_L from [1] follows edges of the partial graph, so it ends at [u]. The board's restriction to B_L is
     therefore ~. ∎

**Classical.** Schreier coset graphs; the folding of Stallings (1983).

## Theorem 2. Refinement

**Statement.** Suppose no clause has a positive identity literal other than those of the board axioms. If (s, ~) is allowed and ~′
is a finer right congruence, then (s, ~′) is allowed. So the tree (no two names one place) is allowed whenever any state is, and
the allowed boards are closed under covering.

**Proof.**
- The board axioms hold for every right congruence.
- In every other clause, each identity literal is negative. A negative literal true under ~ is true under the finer ~′, and the
  value literals are unchanged, because s is a function on names and does not change.
- A cover of Sch(H) is Sch(H′) with H′ contained in a conjugate of H. By left translation the conjugate gives an allowed state, and
  H′ is finer. ∎

## Theorem 3. Unfolding

**Statement.** Let a law over a finite alphabet name no relation. If some allowed state has an infinite board, some allowed state
has the tree as its board. So no such law forces an infinite board (forcing a board means every allowed state has it). The boards it
can force are finite.

**Proof.**
1. **Reduction.** By letter closure in both directions, e(u_i a, u_j a) ⇔ e(u_i, u_j) in every allowed state, and on the tree
   too. So every identity literal may be taken as e(u_i, u_j). By constancy, two names of one place have the same type, so places
   have types. The literals of an instance at bases w_1, …, w_k are then fixed by:
   - the types of the w_i, for the value literals;
   - which w_i lie at one place, for the identity literals.
2. **A far region.** Let (s, ~) be allowed with an infinite board Γ, and call a type rare when only finitely many places of Γ have
   it.
   - There are finitely many types, so finitely many places R have rare types.
   - Γ is connected, locally finite and infinite, so for each n there is a place p_n at distance more than n from R.
   - Choose a name u_n of p_n and the translate s_n(g) = s(u_n g).
3. **Every instance near the root holds on the tree.** Take an instance with bases w_1, …, w_k in B_n, evaluated with the colouring
   s_n on the tree.
   - The bases' types are those of the places [u_n w_i], each within distance n of p_n, so none is rare.
   - Its identity literals form the pattern π: which w_i are equal.
   - Choose places q_i of Γ with the types of the w_i and with q_i = q_j exactly when w_i = w_j. This is possible because every
     type needed occurs at infinitely many places, so blocks of π that share a type can get distinct places.
   - The instance at names v_i ∈ q_i under (s, ~) has the same literal values, and it holds because (s, ~) is allowed. So the tree
     instance holds.
4. **Compactness.** Let K_n be the colourings of F2 under which every instance with bases in B_n holds on the tree.
   - K_n is closed: finitely many instances, each reading finitely many coordinates.
   - K_n is nonempty, since it contains s_n, and K_(n+1) ⊆ K_n.
   - Q^(F2) is compact (Tychonoff), so the K_n meet. A colouring in every K_n, with the tree as board, is an allowed state. ∎

**Where the hypothesis is used.** Step 1 needs the same offset on both sides. With different offsets, the instance at coincident
bases reads whether a word acts trivially at a place, and the far region need not look like the tree. Theorem 8 shows that the
conclusion then fails.

## Theorem 4. Finite boards can be forced

**Statement.** For every finite board Γ there is a law that names no relation whose allowed states all have board Γ (up to the base
point), and some state is allowed.

**Proof.**
- Take Q to be the places of Γ, with the value law s(ux) = σ_x(s(u)), s(uy) = σ_y(s(u)) (one base name), and identity of
  indiscernibles at radius 0: s(u) = s(v) = q → e(u, v) for each q (bases u and v, offset 1).
- The value law gives s(uX) = σ_x⁻¹(s(u)) and s(uY) = σ_y⁻¹(s(u)), so s(u) is s(1) moved by u, a surjection onto Γ because Γ is
  connected.
- Identity of indiscernibles and constancy give u ~ v ⇔ s(u) = s(v). The board is therefore Γ, pointed at s(1).
- Every s(1) gives an allowed state. ∎

## Theorem 5. Every change of board is infinite

**Statement.**
1. Two different boards differ in infinitely many identity distinctions.
2. Every place of a board other than the tree holds infinitely many names.
3. So at an allowed state whose board is not the tree, no change of finitely many variables reaches another allowed state. No
   distinction there is flipped by a finite change, and under the source-aware reading no knot is native at such a state.
4. At a state on the tree, values may flip by finite changes (when the law has finite moves), but identity distinctions never do.

**Proof.**
1. Say u ~ v but not u ~′ v. For every word g, ug ~ vg, while ug ~′ vg would give u ~′ v. So the pairs {ug, vg} all differ between
   the two boards, and they are distinct for distinct g: {ug, vg} = {ug′, vg′} with g ≠ g′ forces (u⁻¹v)² = 1, which F2,
   torsion-free, allows only for u = v.
2. A place Hu has |H| names, and a nontrivial subgroup of the torsion-free F2 is infinite.
3. A finite change keeps the board by (1). Then it changes the values at finitely many names, but the values are constant on
   classes, which are infinite by (2).
4. A finite change cannot change the board, by (1). ∎

## Theorem 6. The collapse

**Statement.** For a value law, the collapse (all names one place) is allowed iff some constant colouring satisfies the law, iff
every board is allowed.

**Proof.**
- On the collapse a colouring is constant.
- A constant colouring satisfying the law satisfies constancy on every board, and a value law does not read the board.
- Every board allowed includes the collapse. ∎

For a value law the allowed boards are exactly the Schreier graphs that admit a colouring by allowed patterns.

## Theorem 7. Identity of indiscernibles

The rule IoI_r: two names of one type at radius r are one place. For each type t it is the template (τ(u) = t ∧ τ(v) = t) →
e(u, v), with bases u and v and offset 1, so it names no relation.

**Statement.**
1. **Finite boards.** Under IoI_r distinct places have distinct types, so every allowed board has at most |Q|^|B_r| places.
2. **Boards from view sets.** Take one bit and radius 1, where a type is a pattern (c; x, X, y, Y).
   - The connected allowed boards of a law L with IoI_1 are exactly the connected view boards: a set V ⊆ L of patterns with
     permutations σ_x and σ_y of V such that each σ_g(t) has centre t's g-value and gives its g⁻¹-neighbour t's centre.
   - Such permutations exist iff, for each letter g and each pair (a, b), the patterns of V with (centre, g-value) = (a, b) are as
     many as those with (g⁻¹-value, centre) = (a, b).
3. **The swap.** If a law has a plane-like abelian view board (every star has five distinct places, and σ_x σ_y = σ_y σ_x), it also
   has a non-abelian one.

**Proof.**
1. By IoI_r and constancy, two names are one place iff they have one type.
2. **The correspondence.** A board with an IoI_1 state gives its views and its letters. Conversely, from a view board colour each
   view by its centre: the recomputed view of t is t, because σ_x(t) has centre t's x-value and σ_x⁻¹(t) has centre t's X-value,
   and likewise for y. So the views are distinct allowed patterns, IoI_1 holds, and Theorem 1 gives the board.
   **The count.** The pattern t′ can be σ_g(t) exactly when its (g⁻¹-value, centre) equals t's (centre, g-value). A bijection then
   exists iff the classes have matching counts.
3. **Two patterns in one class.** A plane-like board has at least 5 views but only 4 classes (centre, x-value), so two views t_1 ≠
   t_2 share one. Their images t_1′ and t_2′ share a target class, so σ′_x = τσ_x, with τ exchanging t_1′ and t_2′, is again
   compatible.
   **The new board is not abelian.** If (σ′_x, σ_y) commuted, then τσ_xσ_y = σ_yτσ_x together with σ_xσ_y = σ_yσ_x would give
   τσ_y = σ_yτ. Then σ_y would fix {t_1′, t_2′}: it would fix t_1′, or it would exchange the two so that σ_y² fixes t_1′. Either
   contradicts the plane-like star at t_1′.
   **A connected example.** The component of a place where σ′_xσ_y ≠ σ_yσ′_x is a connected non-abelian view board of the same
   law. ∎

**Remark (any radius).**
- The same correspondence holds at radius r with q values. Compatibility is agreement on the overlap of a name's and its
  neighbour's balls, which has 3^r − 1 names in the tree.
- So every plane-like abelian IoI_r board with more than q^(3^r − 1) places has a non-abelian sibling.
- Smaller boards are not covered. There a law may be rigid and force a torus; Theorem 4 does so with |Γ| values.

## Theorem 8. One named relation suffices

**Statement.** The commutator rule e(u, u x y X Y) at every name, together with an aperiodic Wang-tile value law (Q the tiles, a
pattern allowed when colours match on all four sides), allows exactly one board: the plane Z².

**Proof.**
1. **The boards are quotients of the plane.** u ~ ucu⁻¹·u for c = xyXY means uc⁻¹u⁻¹ ∈ H for every u, so H contains the normal
   closure of c, the commutator subgroup. The boards are therefore the quotients Z²/Λ of the plane.
2. **Colourings are periodic tilings.** On Z²/Λ an allowed colouring is a Λ-periodic tiling of Z².
3. **Only Λ = 0 survives.**
   - An aperiodic tile set tiles the plane but admits no doubly periodic tiling (Berger 1966; Robinson 1971; eleven tiles, Jeandel
     and Rao 2015).
   - It also admits no tiling with a single period v ≠ 0. A tiling with period v gives, after a change of basis taking v to (d, 0),
     rows determined by d symbols, hence a finite graph of strips. A cycle in that graph is a doubly periodic tiling.
   - So Λ = 0, and the plane is allowed. ∎

The commutator rule names one relation, a face of size four: exactly what A51's challenge excluded.

## What the theorems say together

- **A law that names no relation never chooses an infinite board.** Whenever such a law allows one, it allows the tree, so the plane
  is never forced (Theorem 3). It can force finite boards (Theorem 4), and identity of indiscernibles, the natural rule that names no
  relation and says which names are one place, always does (Theorem 7).
- **One named relation is enough.** The square, with an aperiodic law, forces exactly the plane (Theorem 8). The line between a
  board drawn and a board chosen therefore runs through naming a relation, a face.
- **Nativeness.** Boards made of names are frozen to finite changes off the tree, and identity distinctions are frozen everywhere
  (Theorem 5). Under the source-aware reading, any knot involving the board is opened only by infinity.

## Checks

`check.py` (result in `result.json`) calibrates, and proves nothing:
- every one of the 20 board states on B_1, and 2,000 and 300 random ones on B_2 and B_3, is the restriction of the finite board
  built in Theorem 1;
- 40 pairs of different finite boards differ on more pairs of names as L grows to 4;
- the balance criterion agrees with bipartite matching in all 137,070 tests;
- the swap turns all 748 plane-like abelian view boards of ticket B's laws into non-abelian ones;
- Theorem 4's law allows exactly its own board among the 758 finite boards with at most 6 places, for each of the 37 boards with at
  most 4;
- the commutator rule holds at every place exactly on the 33 abelian finite boards with at most 6 places.

## Scope and what is not proved

- **The setting.** Names from the free group on two letters, so the naming supplies four neighbour names per name. Finite
  alphabets, finitely many templates, finitary clauses.
- **Laws that relate different offsets.** These are not covered beyond Theorem 8.
- **An infinite alphabet.** It escapes Theorem 3's type count, but a law that requires a value among infinitely many needs an
  infinitary clause.
- **Abstract names.** Names with neighbour distinctions instead of letters are not treated here.
- **Whether a law can force the tree itself** is not decided.

## Sources

Schreier graphs and Stallings foldings (Stallings 1983); compactness (Tychonoff; König); aperiodic tilings (Berger 1966, Robinson
1971, Jeandel and Rao 2015); Leibniz's identity of indiscernibles as a rule; shifts on free groups (Piantadosi 2008; Aubrun and
Béal on tree shifts). Novelty: the theorems' ingredients are classical; the unfolding statement and its reading as an obstruction
for boards made of distinctions are new as far as found (bounded search, not a priority claim). Folklore risk: moderate for
Theorems 1, 2, 6 and 8; low to moderate for 3, 5 and 7.
