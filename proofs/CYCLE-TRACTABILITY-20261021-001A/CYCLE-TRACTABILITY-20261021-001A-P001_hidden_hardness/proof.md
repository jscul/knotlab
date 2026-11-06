# Tops can hide any constraint problem

Status: Proved

Ticket `CYCLE-TRACTABILITY-20261021-001A`, 2026-10-21. It uses:
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001`;
- `AFFINE-TOPS-20261021-001A-P001`: Corollary 6, the characterization of
  composing like cycles;
- `CYCLE-UTILITY-20261021-001A-P001` ("the utility proof"): Proposition 2. A
  law that still composes like cycles with all constants added has a
  polynomial-time constraint problem, and trivial tops give a Mal'tsev
  polymorphism.

It also cites:
- the CSP dichotomy theorem (Bulatov; Zhuk);
- the Siggers characterization: a finite structure has a polynomial-time
  constraint problem exactly when it has a Siggers polymorphism, given the
  dichotomy;
- the NP-completeness of 3-colouring (Hell and Nešetřil), and of not-all-equal
  and one-in-three satisfiability (Schaefer).

## Standard statement

**Two lifts.** Let H be a finite structure on a set S, and q ≥ 2.
- **The equal-top lift E_q(H)** has domain Z_q × S. Each relation R ⊆ S^k of
  H becomes

    R↑ = {((a, s₁), …, (a, s_k)) : a ∈ Z_q and (s₁, …, s_k) ∈ R}:

  all first coordinates in an atom are equal, and the second coordinates obey
  H.
- **The shifted lift F_q(H)** adds one binary relation,

    U = {((a, s), (a + 1, t)) : a ∈ Z_q and s, t ∈ S}:

  the first coordinate goes up by one, and the second coordinates are free.

**This proof shows the following.**
1. **Both lifts compose like cycles** (Theorems 1 and 3). In every system the
   free sets are exactly the sets with at most one visible variable in each
   component of the system's constraint hypergraph. That is a partition
   matroid.
2. **E_q(H) is homomorphically equivalent to H** (Theorem 1(b)). So it has
   H's constraint problem and H's core.
3. **The core question is settled** (Corollary 2), as the owner defined it, in
   both permitted ways:
   - **refuted:** the core of a law that composes like cycles need not compose
     like cycles. E₂(K₃) has core K₃, which does not.
   - **a non-Taylor core:** laws that compose like cycles can have non-Taylor
     cores (K₃; not-all-equal) and NP-complete constraint problems.
   - **Every finite structure** is homomorphically equivalent to a law that
     composes like cycles.
4. **Being a core does not help** (Theorem 3). When H is a core, F_q(H) is a
   core that composes like cycles, with H's constraint problem up to
   polynomial-time equivalence. It has a Siggers polymorphism only if H does.
5. **The positive remainder** (Proposition 4). A law that composes like cycles
   and is a core with no nontrivial automorphism pp-defines its constants. So
   its constraint problem is solvable in polynomial time.
   - **Both hypotheses are needed.** E_q(one-in-three) has a rigid core but is
     not a core. F_q(one-in-three) is a core whose only automorphisms are the
     q translations.
   - Both are NP-complete.

So, without constants, composing like cycles does not imply polynomial time
unless P = NP, even for cores.

## Nearest known results

- **Homomorphic equivalence and cores.** Homomorphically equivalent
  structures have the same constraint problem, and every structure has a
  unique core. This is standard in the algebraic theory of constraint
  satisfaction (Hell and Nešetřil; Bulatov, Jeavons and Krokhin).
- **The Taylor and Siggers characterizations,** and the dichotomy theorem
  ([Bulatov](https://arxiv.org/abs/1703.03021),
  [Zhuk](https://arxiv.org/abs/1704.01914)).
- **Height-1 identities transfer** along homomorphisms between structures.
  This is the minion-homomorphism step used in (c).

**Classification: elementary; new to the program.**
- **Both lifts are standard constructions:** a product with a trivial
  structure, and a product with a directed cycle on Z_q. Products like these
  preserve the constraint problem.
- **What is new here** is reading them against composing like cycles. The
  extra coordinate makes every two variables of a component dependent, so the
  matroid of free sets sees only components, whatever H is.

## Theorem 1 (equal-top lifts compose like cycles)

Let H be a finite structure on S, and q ≥ 2.
- **(a)** Let a system of E_q(H) have a nonempty solution set. Then a set Y of
  its visible variables is free exactly when Y has at most one variable in
  each component of the hypergraph on all its variables, with one edge per
  atom. So E_q(H) composes like cycles.
- **(b)** The maps π(a, s) = s and ι(s) = (0, s) are homomorphisms E_q(H) → H
  and H → E_q(H).

*Proof of (a).*
1. **Solutions.** An assignment ((a_v, s_v))_v is a solution exactly when:
   - a is constant on each component, since each atom requires equal first
     coordinates;
   - (s_v)_v is a solution of the same system over H.

   So the solution set is the product of two sets:
   - the functions from components to Z_q;
   - the solution set of the H-system, which is itself a product over the
     components.
2. **Ranges.** Every visible variable takes every first coordinate: change the
   constant on its component.
3. **One component.** Two visible variables x and y in one component have
   a_x = a_y in every solution. Both ranges contain every first coordinate,
   so the pair is constrained, and so is every set containing it.
4. **Different components.** If Y has at most one variable per component, its
   projection is the product, over those components, of the variables' own
   projections, which are their ranges. So Y is free.
5. **Elimination.** These free sets are the independent sets of a partition
   matroid: each component's visible variables form a rank-one parallel class.
   So elimination holds. Systems with no solution satisfy it trivially. ∎

*Proof of (b).*
- π maps each atom's tuple to the tuple of H it carries.
- ι maps a tuple of R to ((0, s₁), …, (0, s_k)) ∈ R↑. ∎

**Consequences of (b).**
- **The same problem.** An instance is satisfiable over E_q(H) exactly when it
  is satisfiable over H.
- **The same core.** The two structures have isomorphic cores.

## Corollary 2 (the core question)

1. **Refuted.** E₂(K₃), the lift of 3-colouring, composes like cycles by
   Theorem 1. Its core is K₃. In K₃, x ≠ e ∧ e ≠ z has the ties {x, e} and
   {e, z}, while {x, z} is free, so K₃ does not compose like cycles.
2. **Non-Taylor cores.** K₃ and not-all-equal have no Siggers polymorphism.
   The checks search exhaustively; classically, both problems are
   NP-complete.
   - So the lifts of 3-colouring and of not-all-equal satisfiability compose
     like cycles, have non-Taylor cores, and have NP-complete constraint
     problems.
3. **Any structure.** By Theorem 1, every finite structure is homomorphically
   equivalent to a law that composes like cycles. So every finite-template
   constraint problem is the constraint problem of such a law. ∎

**Why the earlier theory allows this.**
- **No knots.** The lift has no knots: every circuit is a pair inside one
  component.
- **Ties are bijections modulo the top.** For the lift of K₃, "same first
  coordinate" is pp-definable: two steps of the lifted relation give it. It is
  the top. A pp-definable relation between variables in different components
  is a product, so every other proper pp-definable equivalence lies inside it.
- **The characterization has nothing to act on.** Corollary 6 of the
  affine-tops proof is then satisfied with no knot to constrain. The matroid
  sees the components and nothing below them.

**Why constants matter.** Pin one element to (0, 0) in the lift of K₃.
- A component attached to it has its first coordinate fixed. 3-colouring then
  surfaces as a tie that is not a bijection.
- The checks give an explicit system with three visible variables. With the
  constant it fails elimination; without it, it does not.
- This is why the utility proof's tractability theorem must assume that the
  law composes like cycles with constants added.

## Theorem 3 (shifted lifts are cores)

Let H be a finite structure on S, and q ≥ 2.
- **(a)** F_q(H) composes like cycles. In every system with a solution, the
  free sets are exactly the sets with at most one visible variable in each
  component of the hypergraph of all its atoms.
- **(b)** The endomorphisms of F_q(H) are the maps (a, s) ↦ (a + c, h_a(s)),
  with c ∈ Z_q and each h_a an endomorphism of H. So if H is a core, F_q(H)
  is a core with q · |Aut H|^q automorphisms.
- **(c)** The constraint problems of F_q(H) and H are polynomial-time
  equivalent. F_q(H) has a Siggers polymorphism only if H has one.

*Proof of (a).*
1. **The coordinates separate.** Each atom constrains first and second
   coordinates separately. An atom of R↑ asks for equal first coordinates and
   an H-tuple; an atom of U asks for a step of +1 and nothing of the second
   coordinates.
2. **So the solution set is a product of two sets:**
   - the solutions A of the first-coordinate system. On each component,
     a_v = c + o_v, for fixed offsets o_v and a free c ∈ Z_q;
   - the solutions B of the H-system formed by the R↑ atoms alone. B is a
     product over its own components, which refine the components of all
     atoms.
3. **Ranges.** Every visible variable takes all q first coordinates.
4. **One component.** Two visible variables in one component have a fixed
   offset, so the pair is constrained.
5. **Different components.** A set with at most one visible variable per
   component projects onto a product of ranges. This holds in A (one variable
   per component) and in B (one variable per finer component).
6. **Elimination.** So the free sets again form a partition matroid. ∎

*Proof of (b).* Let f(a, s) = (g(a, s), h(a, s)) be an endomorphism.
- **U is preserved,** so g(a + 1, t) = g(a, s) + 1 for all a, s and t. So
  g(a, s) depends only on a, and g(a) = a + g(0).
- **R↑ is preserved.** The image of an atom in fibre a has first coordinate
  g(a) throughout, and its second coordinates form an H-tuple. So h(a, ·) is
  an endomorphism of H.
- **Conversely,** every such map is an endomorphism.
- **If H is a core,** each h(a, ·) is an automorphism. So f is a bijection,
  hence an automorphism. ∎

*Proof of (c).*
- **From H to F_q(H).** Read an H-instance with R↑ atoms. It is satisfiable
  over F_q(H) exactly when it is satisfiable over H, by Theorem 1(b) applied
  to the reduct E_q(H).
- **From F_q(H) to H.** By (a)'s proof, an instance is satisfiable exactly
  when two systems are:
  - the first-coordinate system, solved by propagating offsets in each
    component;
  - the H-system of its R↑ atoms.
- **Siggers.** A polymorphism s of F_q(H) preserves each R↑. So
  (x₁, …, x₄) ↦ π(s(ιx₁, …, ιx₄)) is a polymorphism of H. It satisfies every
  identity without nesting that s satisfies, Siggers's among them. ∎

**What this gives.**
- **Cores that compose like cycles.** F_q(K₃), F_q(not-all-equal) and
  F_q(one-in-three) are cores that compose like cycles. None of them is
  Taylor, and all have NP-complete constraint problems.
- **The smallest automorphism group.** The automorphisms of
  F_q(one-in-three) are just the q translations of the first coordinate,
  since one-in-three has no nontrivial endomorphism.
- **Again no knots.** Every circuit is a pair inside one component.

## Proposition 4 (rigid cores)

Let Γ compose like cycles, and be a core with no nontrivial automorphism. Then
its constraint problem is solvable in polynomial time.

*Proof.*
1. **The canonical system.** Take one variable for each element d₁, …, d_n,
   and every tuple of every relation as an atom. Its solutions are the
   endomorphisms of Γ, written as tuples.
2. **It is a single tuple.** In a core every endomorphism is an automorphism.
   Here the only automorphism is the identity, so the solution set is
   {(d₁, …, d_n)}.
3. **Constants are pp-definable.** Each singleton {d_i} is a projection of
   that system.
4. **The conclusion.** Γ with constants added has exactly Γ's systems, so it
   composes like cycles. The utility proof's Proposition 2 gives polynomial
   time. ∎

**Both hypotheses are needed.**
- **Dropping "a core".** E_q(one-in-three) composes like cycles, and its
  core, one-in-three, has no nontrivial endomorphism. Its constraint problem
  is NP-complete.
- **Dropping "no nontrivial automorphism".** F_q(one-in-three) is a core that
  composes like cycles, with only the q translations as automorphisms. Its
  constraint problem is NP-complete.
- **Why the proof stops there.** The automorphisms move every element, so no
  constant is pp-definable.

## What this does not show

- **No claim about P versus NP.** The NP-completeness of 3-colouring,
  not-all-equal and one-in-three is classical. This proof only places these
  problems inside laws that compose like cycles.
- **Only knot-free examples.** All the hard examples are knot-free. This proof
  does not treat laws with knots.
- **No protected structure.** No native recurrence, composed topology in the
  protected sense, path or distance is claimed.

## Checks

`check.py` writes `result.json` in under a second. All checks pass, and all
controls are rejected.

- **Theorem 1.** Lifts were built of six structures:
  - 3-colouring;
  - not-all-equal;
  - one-in-three;
  - three random structures on three values.

  For each, with q = 2 and 3, 120 random systems were sampled, with hidden
  variables. In every one of the 671 nonempty systems, the free sets are
  exactly the sets with at most one visible variable per component. There is
  no elimination failure. Both maps are homomorphisms in all twelve cases.
- **Corollary 2.**
  - The lifts of K₃ and not-all-equal (q = 2) have cores of 3 and 2 elements,
    which are K₃ and not-all-equal.
  - Exhaustive search finds no Siggers polymorphism for either. The same
    search finds one for the Z₃ law and for parity.
  - K₃ and not-all-equal violate elimination.
  - On 38 random graphs, the lifted instance is satisfiable exactly when the
    graph is 3-colourable.
- **Constants.** In the lift of K₃, a system with one pinned element violates
  elimination: the ties {x, e} and {e, z}, with {x, z} free. The same system
  unpinned satisfies it.
- **Theorem 3.** Shifted lifts of K₃, not-all-equal and one-in-three were
  checked, with q = 2 and 3.
  - **Endomorphisms.** All are bijective, and their numbers match
    q · |Aut H|^q: 72 and 648, 8 and 24, 2 and 3.
  - **Free sets.** In all 266 nonempty sampled systems, the free sets are
    exactly the sets with at most one visible variable per component. There
    is no elimination failure.
  - **Splitting.** 60 shifted 3-colouring instances mixed equal-top and
    step atoms. Each is satisfiable exactly when the graph is 3-colourable and
    the offsets are consistent:
    - 18 instances are colourable and consistent;
    - 29 are colourable but inconsistent;
    - 13 are not colourable.
  - **Not searched.** No Siggers search was run on the shifted lifts; it was
    too slow. Their non-Taylor status rests on (c).
- **Proposition 4.**
  - **The illustration.** x + y + z = 0 over Z₃, with the constants 0 and 1,
    has only the identity as an endomorphism and keeps x − y + z.
  - **Sharpness.** One-in-three has only the identity as an endomorphism. Its
    shifted lift has exactly q automorphisms.
- **Controls,** each rejected:
  - "composing like cycles implies tractability" (the lift of K₃);
  - "the core of a law composing like cycles composes like cycles" (K₃);
  - "the lift still composes like cycles with constants" (the pinned system);
  - "every core composing like cycles is tractable" (the shifted lift of K₃).
