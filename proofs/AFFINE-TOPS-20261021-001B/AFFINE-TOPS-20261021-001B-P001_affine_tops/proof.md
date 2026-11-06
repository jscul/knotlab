# Affine tops and representable matroids

Status: Proved

Ticket `AFFINE-TOPS-20261021-001B`, 2026-10-21. It uses:
- `AFFINE-TOPS-20261021-001A-P001` ("the rectangularity proof"): Theorem 3 and
  Corollary 5, a polymorphism Mal'tsev modulo the top of every knot range;
- `THOMSEN-KNOTS-20261021-001A-P001` ("the overlap proof"): Theorem 2, every
  circuit's top image is a Latin hypercube;
- `CYCLE-TOPS-20261021-001B-P001` ("the tops proof"): the top lemma;
- `MATROID-CONVERSE-20261021-001B-P001` ("the matroid proof"): the class 𝓡,
  its Theorem 3(b) and its Conjecture 5;
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001`;
- classical algebra:
  - the Galois connection between polymorphisms and pp-definable relations of
    a finite structure;
  - Wedderburn's little theorem;
  - the density theorem;
  - Rado's theorem on representations over finite fields.

## Standard statement

**Definitions.** They are those of the rectangularity proof.
- **Knot tops.** For a knot range B, write B̄ = B/μ_B. F is a polymorphism
  that is Mal'tsev modulo the top of every knot range (the rectangularity
  proof's Corollary 5). F̄ is the operation it induces on each B̄, which is well
  defined because F preserves μ_B.
- **Parallelogram relations.** Let K be the blur by the tops of a knot's
  relation. Take e a variable of range B, i another variable, and w the
  remaining variables (at least one). Then
  P(t₁, t₂, t₃, t₄) = ∃u, u′, w, w′: K(u, w, t₁) ∧ K(u′, w, t₂) ∧ K(u, w′, t₃) ∧ K(u′, w′, t₄).
  This is a two-by-two square whose rows are values of i and whose columns are
  values of the rest.
- **𝓡** is the matroid proof's class: direct sums of matroids, each
  representable over some field.

**This proof shows the following,** for every law that composes like cycles.
1. **The tops of knot ranges are affine** (Theorem 1).
   - Every knot's parallelogram relation is the graph of F̄. So F̄ does not
     depend on the knot or on F, and its graph is pp-definable.
   - F̄ is x − y + z for an elementary abelian p-group on the top.
   - Every polymorphism acts on the top by affine maps.
   - Every top image, restricted to the variables with knot ranges, is a coset
     of a subgroup.
2. **Three-variable circuits** (Corollary 2). Modulo the tops and after
   relabelling, each is the addition table of an elementary abelian p-group.
   This was the first step of the owner-approved plan.
3. **Matroids** (Theorem 3). Every system's matroid is a direct sum of rank-one
   parallel classes and matroids representable over finite fields.
   - A component's field is the endomorphism field of its tops, as modules over
     the ring of the polymorphisms' linear parts.
   - This proves the weak form of the matroid proof's Conjecture 5.
   - Conversely, every direct sum of matroids representable over finite fields
     occurs. By Rado's theorem this is all of 𝓡.

## Nearest known results

- **Abelian Mal'tsev algebras are affine.** This is Herrmann's theorem, a
  cornerstone of commutator theory; see [Kearnes and Szendrei's
  extension](https://arxiv.org/abs/math/9604246). Theorem 1 takes a direct
  route: the parallelogram relation makes the Mal'tsev operation commute with
  itself.
- **Model theory.** In model theory, geometries of independence that are
  modular or locally modular are coordinatized by groups.
  - For ω-categorical structures, the building blocks are affine or projective
    spaces over finite fields (Zilber; Hrushovski; Cherlin, Hrushovski and
    Lachlan).
  - Theorems 1 and 3 are a finite, pp-definable analogue: when the free sets of
    every pp-definable relation form a matroid, the tops are affine over finite
    fields.
  - The proofs here do not use that theory.
- **Rado's theorem.** A matroid representable over a field is representable
  over a finite field. See [Bell, Funk, Kim and Mayhew, Effective versions of
  two theorems of Rado](https://arxiv.org/abs/1802.10262).

**Classification: new to the program; built from classical algebra.**
- I found no source for Theorem 1 or Theorem 3 in this setting.
- Experts in universal algebra or model theory may know close analogues, so
  the folklore risk is moderate.
- Corollary 2 is immediate from Theorem 1.

## Theorem 1 (affine tops)

Let the law compose like cycles. Let B be a knot range with top B̄, and F as
above.
- **(a)** For every knot through B, every parallelogram relation P at a
  variable of range B has top image {(t₁, t₂, t₃, t₄) : t₄ = F̄(t₂, t₁, t₃)}.
  So F̄ on B̄ is the same for every polymorphism Mal'tsev modulo the tops of the
  knot ranges, and its graph is pp-definable.
- **(b)** Every polymorphism G commutes with F̄ on B̄. Fix o ∈ B̄ and put
  x + y = F̄(x, o, y). Then (B̄, +) is an abelian group, F̄(x, y, z) = x − y + z,
  and every polymorphism acts on B̄ by affine maps.
- **(c)** (B̄, +) is an elementary abelian p-group for some prime p.
- **(d)** For every system, the top image restricted to its variables with knot
  ranges is a coset of a subgroup of the product of the groups (B̄_v, +).

*Proof.*
1. **(a), the inclusion.** Take witnesses u, u′, w, w′, and apply F̄
   coordinatewise to the tuples (u′, w, t₂), (u, w, t₁) and (u, w′, t₃) of K̄.
   - F̄ is Mal'tsev on every coordinate, since every variable of the knot has a
     knot range.
   - So the result is (F̄(u′, u, u), F̄(w, w, w′), F̄(t₂, t₁, t₃)) =
     (u′, w′, F̄(t₂, t₁, t₃)), which lies in K̄.
   - So does (u′, w′, t₄). K̄ is functional at e (the overlap proof's
     Theorem 2), so t₄ = F̄(t₂, t₁, t₃).
2. **(a), every triple occurs.** Let t₁, t₂ and t₃ be any classes.
   - K̄ is a Latin hypercube. Choose w freely, then u from (w, t₁) and u′ from
     (w, t₂).
   - Choose all but one variable of w′ freely; the last is fixed by (u, t₃).
   - Then t₄ exists.
   - **Consequences.** The relation P is pp-definable and a union of top
     classes, and its top image is the graph of F̄. Hence that graph is
     pp-definable, and F̄ is determined by K alone.
3. **(b), commuting.** A polymorphism G preserves P, so its induced operation
   Ḡ preserves the graph of F̄.
   - Apply Ḡ to the tuples (yⱼ, xⱼ, zⱼ, F̄(xⱼ, yⱼ, zⱼ)), j = 1, …, n.
   - This gives Ḡ(F̄(x₁, y₁, z₁), …, F̄(xₙ, yₙ, zₙ)) = F̄(Ḡ(x⃗), Ḡ(ȳ), Ḡ(z⃗)).
4. **(b), the group.** Taking G = F, F̄ commutes with itself.
   - **Additivity.** With rows (xⱼ, o, yⱼ), self-commuting gives
     F̄(x⃗ + ȳ) = F̄(x⃗) + F̄(ȳ), because F̄(o, o, o) = o.
   - **Identity.** x + o = F̄(x, o, o) = x and o + y = F̄(o, o, y) = y.
   - **Commutative.** The rows (o, o, x), (o, o, o) and (y, o, o) give
     x + y = y + x.
   - **Associative.** The rows (x, o, y), (o, o, o) and (o, o, z) give
     (x + y) + z = x + (y + z).
   - **The formula.** By additivity, F̄(x, y, z) = x + F̄(o, y, o) + z.
     F̄(y, y, o) = o gives y + F̄(o, y, o) = o, so F̄(o, y, o) is the inverse of
     y, and F̄(x, y, z) = x − y + z.
   - **Affine maps.** A map commuting with x − y + z satisfies
     Ḡ(x⃗ + ȳ) = Ḡ(x⃗) − Ḡ(o⃗) + Ḡ(ȳ), so it is affine.
5. **(c).** Let p divide |B̄|.
   - The relation x − y ∈ pB̄ says x = y + p(u − v) for some u and v. That is a
     chain of p atoms of the graph of F̄, so it is pp-definable.
   - Its preimage is an equivalence on B containing μ_B, so it is μ_B or
     total. Hence pB̄ = 0 or pB̄ = B̄.
   - Multiplication by p is not onto, because B̄ has an element of order p.
     So pB̄ = 0, and B̄ is elementary abelian.
6. **(d).** F preserves every system and every top, and F̄ is Mal'tsev on each
   coordinate with a knot range. So the restricted top image is closed under
   coordinatewise x − y + z. A nonempty subset of an abelian group closed under
   x − y + z is a coset of a subgroup. ∎

## Corollary 2 (three-variable circuits)

Let the law compose like cycles. Every three-variable circuit's top image, after
relabelling each of its three tops, is the addition table {(x, y, x + y)} of an
elementary abelian p-group.

*Proof.* Let x, y and z be the circuit's variables. By Theorem 1(d) its top
image is a coset c + H, with H a subgroup of B̄_x ⊕ B̄_y ⊕ B̄_z.
- **H is a graph.** H projects onto all pairs, and it is functional at z. So H
  is the graph of a homomorphism (x, y) ↦ φ(x) + ψ(y).
- **φ and ψ are bijective,** because the top image is functional at x and at
  y.
- **The relabelling.** Translate by c, and relabel x by φ and y by ψ. ∎

Modulo the tops, for example, the 3-net of Z₄ becomes the addition table of Z₂,
and that of Z₂×Z₂ stays itself.

## Theorem 3 (matroids)

Let the law compose like cycles, and S a system.
- **Rank one.** The components of S's matroid of rank one are parallel classes,
  including coloops.
- **Higher rank.** In each component of rank two or more:
  - every variable has a knot range;
  - all their tops are isomorphic simple modules M over the ring R defined
    below;
  - the component is representable over the finite field D_M = End_R(M).

So every system's matroid lies in 𝓡, which proves the weak form of the matroid
proof's Conjecture 5. Conversely, every direct sum of matroids representable
over finite fields is carried by a system of some law that composes like
cycles. By Rado's theorem, that is all of 𝓡.

*Proof.*
1. **Components.** A connected matroid of rank two or more has a circuit C with
   three or more elements, and every element v lies in one.
   - If v and some c ∈ C lie in a common circuit of two elements, then v is
     parallel to c, and (C − c) ∪ {v} is a circuit through v.
   - So every variable of such a component lies in a knot of S and has a knot
     range.
   - The other components have rank one and are representable over every
     field.
2. **The ring.** By Theorem 1(b), a polymorphism G acts on each knot top B̄ as
   Ḡ(x⃗) = Σᵢ L_{G,i,B}(xᵢ) + c_{G,B}.
   - Let R be the ring of tuples (L_B)_B generated by the tuples
     (L_{G,i,B})_B. It acts on each B̄ through the B-component.
   - **It is a ring.** It contains:
     - the identity, from a projection;
     - sums, from identifying two arguments of G;
     - the negative of the identity, from F's middle argument;
     - products, from composition.
3. **Each knot top is a simple R-module.** Let N be an R-submodule of B̄.
   - The equivalence x − y ∈ N is preserved by every polymorphism, since their
     linear parts lie in R. By the Galois connection, it is pp-definable.
   - Its preimage contains μ_B, so it is μ_B or total. Hence N = 0 or N = B̄.
4. **Invariance.** Let V_K be S's variables with knot ranges, and c + H its
   restricted top image (Theorem 1(d)). For s ∈ c + H and h ∈ H:
   - applying Ḡ to the tuples s, …, s + h, …, s (with s + h in position i)
     gives Ḡ(s, …, s) + L_{G,i}(h), which lies in c + H;
   - Ḡ(s, …, s) also lies in c + H, so L_{G,i}(h) ∈ H.

   So H is an R-submodule of ⊕_{v∈V_K} B̄_v.
5. **Splitting by type.** The module ⊕ B̄_v is semisimple. There are no nonzero
   homomorphisms between non-isomorphic simple modules.
   - So H is the direct sum of its parts H_M, one for each isomorphism type M.
   - The matroid on V_K is the direct sum of theirs. A component of rank two or
     more therefore has a single type.
6. **One type.** Identify each B̄_v of type M with M by an R-isomorphism.
   - D = End_R(M) is a finite division ring, hence a field (Wedderburn).
   - By the density theorem, R acts on M through all of End_D(M). So the
     R-submodules of M^V are exactly M ⊗_D U for subspaces U of D^V.
   - Since M is a nonzero D-vector space, the projection of M ⊗ U onto Y is all
     of M^Y exactly when U's projection is all of D^Y.
   - So the component's free sets are those of U. That is the column matroid,
     over D, of a generator matrix of U.
7. **Converse.**
   - **One field.** Take a finite field F_q and the law of the relations
     z = x + y and y = λx, for λ ∈ F_q. It composes like cycles by the matroid
     proof's Theorem 3(b). Hiding coordinates, its systems carry the row space
     of any matrix over F_q, so every F_q-representable matroid occurs.
   - **Several fields.** A disjoint union of such laws, one sort per field,
     composes like cycles, because its systems split by sorts. It carries the
     direct sums.
   - **All of 𝓡.** By Rado's theorem, every matroid representable over a field
     is representable over a finite field. ∎

**The field is not the size of the top.**
- **The 3-net of Z₂×Z₂.** Its tops have four elements, but End(Z₂×Z₂) acts as
  all 2×2 matrices over F₂. So D = F₂, and its matroids are binary, as the
  images proof's Theorem 4 already showed.
- **The GF(4) law** {(x, y, x + ωy)}. Its top also has four elements, but
  multiplication by ω is a polymorphism. So D = GF(4).
  - It carries U(2,4): x + ωy = z and x + ωz = u give u = ω²(x + y), and every
    two of x, y, z and u are free.

## What this does not show

- **Tie ranges.** Ranges met only by ties are not covered. Theorem 3 does not
  need them: their variables form rank-one components.
- **The strong form of Conjecture 5.** It asks whether every such law is
  "dressed" by a group or field law relation by relation. It is not addressed.
  Theorem 1 gives affine structure on the top images of systems, not on the
  law's own relations.
- **No protected structure.** No native recurrence, composed topology in the
  protected sense, path or distance is claimed.

## Checks

`check.py` writes `result.json` in about five seconds. All checks pass, and all
controls are rejected.

- **Laws used:**
  - the fourteen laws of the rectangularity proof's checks, with their
    census-certified tops;
  - the GF(4) law. Its top on GF(4) is equality: all 13 coarser proper
    equivalences are broken by x + y + z or by multiplication by ω or ω².
- **Theorem 1.** For each law, 80 random systems were sampled. At all 3,116
  knot variables found:
  - the parallelogram relation is the graph of an operation;
  - that operation is Mal'tsev, and the same for every knot through the range.
  - For every range, the operation commutes with itself, by exhaustive check.
  - x + y = F̄(x, o, y) is an abelian group with F̄ = x − y + z, of prime
    exponent: 2 or 3.
  - Every sampled top image, restricted to knot-range variables, is closed
    under it.
- **Theorem 1 with polymorphisms.** In six small laws, four polymorphisms
  Mal'tsev modulo the knot-range tops were found by randomized search.
  - Each induces exactly the parallelogram operation.
  - Four random binary polymorphisms each commute with it.
- **Corollary 2.** All 892 three-variable circuits found are addition tables
  after relabelling.
- **Theorem 3.**
  - In all 1,200 sampled systems, components of rank two or more consist of
    knot-range variables.
  - For laws whose knot tops have prime order, the matroid is the column
    matroid over GF(p) of a generator matrix read off the top image, in all
    980 systems with such variables.
  - For the 3-net of Z₂×Z₂, all 80 matroids are binary.
  - For the GF(4) law, all 67 matroids with a nonconstant variable are
    represented by a generator matrix over GF(4).
  - The explicit system above carries U(2,4), represented over GF(4) and not
    over GF(2).
- **Controls,** each rejected:
  - "every top image is closed under the parallelogram operation". Thomsen's
    configuration in the 3-net of Q₈ is not closed under x + y + z modulo ±1.
  - "every law composing like cycles carries only binary matroids". U(2,4)
    occurs in the GF(4) law.
  - "the field is fixed by the size of the tops". The Z₂×Z₂ 3-net and the
    GF(4) law both have four-element tops; the first gives binary matroids in
    every sampled system, the second U(2,4).
  - "knot relations are closed under a Mal'tsev operation below the tops". K₄
    is not rectangular at its first variable.
