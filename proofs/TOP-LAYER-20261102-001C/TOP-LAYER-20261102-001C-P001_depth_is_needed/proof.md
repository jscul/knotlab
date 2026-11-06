# Depth is needed: simple abelian sections force rigid selection

Status: Proved

Ticket `TOP-LAYER-20261102-001C`, 2026-11-02.

## Question

- **What tickets A and B found.**
  - **A.** Every law on three values that composes like cycles is rigid.
  - **B.** Group laws keep their top rigid, and are rigid when every abelian section has prime order.
- **The question.** What is the common reason, and how far does it reach?

## Dependencies

- **`TOP-LAYER-20261102-001A` and `B`.** Their results are instances of the theorem.
- **Classical commutator theory** for congruence-modular varieties (Freese–McKenzie 1987; Herrmann 1979; Gumm). Every Mal'tsev
  algebra generates such a variety. The facts used:
  - [α, β] ≤ α ∧ β, and the commutator is monotone and distributes over joins.
  - [1, 1] is the least congruence with an abelian quotient.
  - Abelian algebras are affine: polynomially equivalent to modules over a ring, one ring for the whole variety. Their subuniverses
    are cosets of submodules.

## Setting

- **Mal'tsev laws.** A law is Mal'tsev when its relations have a Mal'tsev polymorphism. Its algebra has the polymorphisms as
  operations, and the relations of the law are subuniverses of its powers.
- **Sections.** A section is S/α, with S a subalgebra and α a congruence of S.
  - **Abelian.** The quotient is an abelian algebra.
  - **Simple.** Its only congruences are the two trivial ones. For a module, this means a single layer.
- **Systems with declared domains.** Every point v of a connected k-regular k-uniform substrate (k ≥ 3) carries a subalgebra D_v,
  its domain. Every line carries a knot of the law whose range at each of its points is exactly that point's domain. Removing a line
  then changes no domain.
- **Mixed domains.** A system in which some line confines a point further than its other lines do has mixed domains. The proof below
  does not cover it (see the last section).

## Theorem

1. **Knots are abelian.**
   - **Forks.** Let H ≤ R_1 × … × R_k (k ≥ 3) have every (k − 1)-projection full. Each fork relation ρ_i is a congruence of R_i, and
     H is a union of ρ_1 × … × ρ_k classes. Here ρ_i relates two values of coordinate i that complete the same values of the other
     coordinates.
   - **Quotients.** Every quotient R_i/ρ_i is abelian.
   - **One equation.** H is pulled back from one linear equation Σ f_i(x_i) = c, valued in a module Q ≅ R_i/ρ_i.
2. **Systems are linear over abelianizations.** For a system with declared domains, the solutions, and the solutions after any
   removal, are unions of classes of the derived congruences δ_v = [1, 1] of the domains D_v. They are pulled back from one linear
   system over the abelianizations M_v = D_v/δ_v, which are modules; removing a line deletes one of its equations.
3. **Simple sections force rigidity.** If every abelian section of the algebra is simple, every global failure of a system with
   declared domains on a substrate is rigid: after any removal only ties remain.

**Corollaries.** Rigid selection holds for:
- every Mal'tsev law on at most three values (ticket A);
- every non-affine Mal'tsev law on four values;
- every group law that composes like cycles and whose abelian sections have prime order, which includes those of squarefree order
  (ticket B).

**Depth is necessary, not sufficient.** The module F2² over the upper-triangular ring T2(F2) has two layers and composes like cycles,
yet it is rigid on every regular substrate.

## Proof

**Item 1, forks.** Write H ≤ P × R, with P the product of the other coordinates and R = R_k, both projections full.
- **ρ is a congruence.** ρ is reflexive and symmetric. It is the projection of the subalgebra {((p, r), (p, r′)) ∈ H²} onto R², so
  the operations respect it.
- **Saturation.** If (p, r) ∈ H and r ρ r′ through some (q, r), (q, r′) ∈ H, then m((p, r), (q, r), (q, r′)) = (p, r′) ∈ H.
- **Transitivity** follows the same way. ∎

**Item 1, abelian.**
- **Setup.** Let F: P → R/ρ send p to the class of its fibre, with kernel ψ. For complementary nonempty sets I and J of the other
  coordinates (possible since k ≥ 3), let η_I and η_J be the kernels of the projections of P onto them. Then η_I ∧ η_J = 0.
- **Joins with ψ.** The projection of H onto I ∪ {k} is full, so each η_J-class of P maps onto R/ρ, giving ψ ∘ η_J = 1. Likewise
  ψ ∘ η_I = 1.
- **The commutator.** [1, 1] = [ψ ∨ η_I, ψ ∨ η_J] ≤ ψ ∨ [η_I, η_J] ≤ ψ ∨ (η_I ∧ η_J) = ψ.
- **Conclusion.** P/ψ ≅ R/ρ is abelian, and by symmetry so is every R_i/ρ_i.
- **One equation.** The quotient relation H/Π ρ_i has trivial forks and full proper projections. In modules it is then the graph
  {x : Σ f_i(x_i) = c} with every f_i an isomorphism onto Q. ∎

**Item 2.**
- **δ_v sits under every fork.** For every line L′ through v, the range is D_v and D_v/ρ_(L′,v) is abelian, so δ_v ≤ ρ_(L′,v).
- **Saturation.** Changing a solution's coordinates within δ-classes keeps every line satisfied, by item 1.
- **Pull-back.** Conversely, a point whose image satisfies every abelianized line has a preimage that satisfies every line. So the
  solution set is exactly the pull-back of the abelianized solutions. ∎

**Item 3.**
- **Simple pieces.** Every M_v and every line's Q is a simple module, or trivial.
- **One type.** A line's equation joins only variables whose modules are isomorphic to its Q, since homomorphisms between
  non-isomorphic simple modules vanish. Removing a line of another type leaves a failing type failing, so all n lines of a global
  failure have one type S.
- **Scalars.** The coefficients lie in F = End(S), a finite field by Wedderburn's theorem. As an F-space S ≅ F^d, so the system is d
  copies of one n × n_S scalar system over F, with n_S ≤ n.
- **One dependency.** Global failure gives a one-dimensional, fully supported left kernel, by the hyperplane argument of
  RIGID-SELECTION A, item 1. So after any removal the rank is n − 1.
- **One line.** The solutions are x° + τ ⊗ t with t ∈ S, and moving variables are pairwise tied (x_w − x°_w = (τ_w/τ_v)(x_v − x°_v)).
- **Everything else is free.** Variables of other types, or with trivial abelianization, are unconstrained.
- **Back to the solutions.** Pulling back along coordinatewise surjections keeps exactly the constrained sets (the blurring lemma of
  BEYOND-TWO B, which allows fibres of different sizes). ∎

**Corollaries.**
- **Three values.** An abelian section has 2 or 3 elements, so it is a module of prime order, hence simple.
- **Four values, non-affine.** An abelian section with four elements would be the whole algebra, which is not abelian. So every
  abelian section has prime order.
- **Groups.** For a group that composes like cycles, every abelian section is a quotient of a subgroup's abelianization, a cyclic
  p-group (ticket B). It is simple when it has prime order, which squarefree order guarantees.
- **The hypothesis is needed.** Without it the conclusion fails. A C6 section splits into a C2 part and a C3 part. Z4 keeps knots
  (RIGID-SELECTION B).

**Depth is necessary, not sufficient.**
- **The relations.** Over T2(F2), the relations of F2² are U ⊕ V with V ⊆ U: subspaces on the bottom and top bits. A knot must have
  V = parity and U = parity or everything, and every range is all of F2².
- **The top system.** It is therefore the plain incidence system N over F2.
- **When it can fail globally.** That needs a fully supported left-kernel vector, the all-ones vector, so k must be even. Then
  N · 1 = 0, and after any removal the top's free direction is the all-ones vector.
- **Conclusion.** Every two variables are tied at the top, so no circuit has three or more elements. This holds whichever layer fails.
  ∎

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Item 1 on 26 random Mal'tsev algebras on four values, every three-place knot enumerated (subuniverses of A³). | 1518 knots, 4554 forks: every fork a congruence with an abelian quotient, every knot saturated |
| 2 | Random systems (mixed domains: knots placed at random) on cubic (up to 7 points, both readings) and 4-regular substrates. | 98 global failures, every one saturated by the derived congruences of its ambient ranges and rigid |
| 2b | Systems with declared domains on cubic substrates and on 4-regular substrates with 5 and 6 points. | 475 global failures, all rigid and saturated |
| 3 | Controls: Z4 and T2(F2). | Z4 has a two-layer section and keeps knots after all 6 removals; T2(F2) has one and is rigid in all 195 global failures (none on cubic substrates) |

## Mixed domains

- **Why the proof stops.** When a line confines a point further than its other lines do, removing that line enlarges the point's
  range. Then:
  - the abelianization after the removal is not the full abelianization minus one equation;
  - the hyperplane argument has nothing to act on.
- **The mechanism, in the smallest case.** Take a three-value law. A variable that one line reads by its block bit, and the others
  by its top bit, enters the other lines with coefficient zero while that one line is present.
- **The evidence.** Every mixed-domain global failure met in the checks was rigid:
  - ticket A: 443, with knots placed at random;
  - ticket B: 108;
  - check 2 here: 98.
- **Status.** The extension is a conjecture with that support, not a theorem.

## What this does not establish

- **Where kept knots sit.** With two-layer sections, the theorem says nothing about where kept knots sit. That is ticket D.
- **The converse.** It fails in general (T2(F2)). Which multi-layer sections allow kept knots is open: Z4, F2[t]/(t²), Z8, Z9, Z25 and
  Z27 do (RIGID-SELECTION B and D).
- **Substrates.** Regular ones only, as throughout.

## Novelty

- **Classical.** The commutator facts used, Fleischer-style fork arguments, and Wedderburn's theorem.
- **New here.**
  - The statement that selection is rigid whenever every abelian section is simple.
  - Its corollaries.
  - The T2(F2) example.
- **Folklore risk** is moderate.
