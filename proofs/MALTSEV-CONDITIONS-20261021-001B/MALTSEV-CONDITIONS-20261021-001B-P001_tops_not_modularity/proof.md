# Composing like cycles is a condition on tops, not a classical Mal'tsev condition

Status: Proved

Ticket `MALTSEV-CONDITIONS-20261021-001B`, 2026-10-21. It uses:
- the shadow and lift theorems of `DIAGONAL-LEMMA-20261021-001B-P001` ("the
  shadow proof");
- Proposition 6 of `MATROID-CONVERSE-20261021-001B-P001` ("the matroid proof"):
  in a law that composes like cycles, every range has a unique maximal
  pp-definable equivalence, its top;
- the census `MALTSEV-CONDITIONS-20261021-001A-E001` ("A").

## Standard statement

**Mal'tsev conditions.** A law's polymorphisms form an algebra on its domain,
and that algebra generates a variety. Three classical conditions are tested
here:
- **congruence permutability:** a Mal'tsev operation, p(x,y,y) = x and
  p(x,x,y) = y;
- **congruence n-permutability:** Hagemann–Mitschke terms p₁, …, p_{n−1} with
  p₁(x,y,y) = x, pᵢ(x,x,y) = pᵢ₊₁(x,y,y) and p_{n−1}(x,x,y) = y;
- **congruence modularity:** Day terms, or equivalently Gumm terms. In the
  form of Theorem 4.1 of [On the number of terms witnessing congruence
  modularity](https://arxiv.org/abs/1709.06023), Gumm terms are ternary p,
  j₁, …, j_{n+1} with j_i(x,y,x) = x, p(x,z,z) = x, p(x,x,z) = j₁(x,x,z),
  j_i(x,z,z) = j_{i+1}(x,z,z) for odd i, j_i(x,x,z) = j_{i+1}(x,x,z) for even
  i, and j_{n+1}(x,y,z) = z.

The matroid proof recommended testing whether composing like cycles implies
modularity, since half of its top lemma uses only modularity.

**The laws.**
- **K₄** = g⁻¹(x + y + z ≡ 0 over Z₃) − {(2,2,2)} on {0,1,2,3}, with
  g = (0,1,2,2), so 3 is read as 2.
- **K₆** = (x + y + z ≡ 0 over Z₃) × (not exactly two ones), with pairs
  encoded as 2a + b.

Both compose like cycles, by the shadow proof.

**This proof shows the following.**
1. **K₄ is 3-permutable and congruence modular** (Theorem 1), with explicit
   terms, but it has no Mal'tsev polymorphism.
2. **A restriction lemma** (Theorem 2). Linear identities of a shadow's
   polymorphisms hold in its dominated factor's clone, fibre by fibre.
   Idempotent identities hold on congruence classes.
3. **K₆ is neither congruence modular nor n-permutable for any n** (Theorem 3),
   although its law composes like cycles. Its fibres carry the clone of
   conjunctions and constants.
4. **So composing like cycles is incomparable** with congruence
   permutability, n-permutability and modularity (Corollary 4). It is not one
   of these classical conditions, and the top lemma cannot go through
   modularity.
5. **What the known examples share** (Theorem 5).
   - Every difference law that composes like cycles is Mal'tsev on its tops:
     some polymorphism is a Mal'tsev operation modulo each range's maximal
     congruence.
   - So is every lift of one, and every shadow of one in which equality of
     first components is pp-definable. This covers K₄, K₆, K₄ₓ₄ and the
     GF(4) lift, and census A found such operations for L₂₂₃ and L₂₃₃.
   - Conjecture 6 says this is forced.

## Nearest known results

- **The characterizations used.**
  - Hagemann and Mitschke (1973): a variety is n-permutable exactly when it
    has Hagemann–Mitschke terms (stated, for example, in [n-permutability and
    linear Datalog implies symmetric Datalog](https://arxiv.org/abs/1508.05766)).
  - Day (1969): it is congruence modular exactly when it has Day terms.
  - Gumm (1981, 1983) gave an equivalent family of terms, in the form above.
- **Tame congruence theory** (Hobby and McKenzie 1988) explains the shape of
  the result. Modularity and n-permutability rule out the semilattice type
  everywhere in a variety. Composing like cycles, as found here, rules things
  out only on the tops.
- **Two-element clones.** The two-element clones that appear are small and are
  decided here by exhaustive enumeration.

**Classification: new to the program; elementary.** The restriction lemma is
routine. The incomparability and the "Mal'tsev on tops" picture are the
results.

## Theorem 1 (K₄ is 3-permutable and modular)

Write lift(r) = r for r ∈ {0, 1} and lift(2) = 3, and v(x, y) = x if x = y,
else lift(2x̄ + 2ȳ).
- **Hagemann–Mitschke terms.**
  - p₁(x,y,z) = x if y = z; v(x, z) if x = y; otherwise lift(x̄ + ȳ − z̄).
  - p₂(x,y,z) = z if x = y; v(x, y) if y = z; otherwise lift(2x̄ + ȳ + z̄).
- **Gumm terms** (n = 1, with j₂ the third projection).
  - p(x,y,z) = x if y = z; otherwise lift(x̄ − ȳ + z̄).
  - j₁(x,y,z) = z if z = x or z = y; otherwise lift(z̄).

  The required identities are j₁(x,y,x) = x, p(x,z,z) = x,
  p(x,x,z) = j₁(x,x,z) and j₁(x,z,z) = z.

Each term is a polymorphism of K₄ and satisfies its identities. So K₄
generates a variety that is congruence 3-permutable and congruence modular.
K₄ has no Mal'tsev polymorphism.

*Proof.*
1. **Residues are linear.** In every case each term's residue mod 3 is a fixed
   linear form:
   - x̄ + ȳ − z̄ for p₁;
   - 2x̄ + ȳ + z̄ for p₂;
   - x̄ − ȳ + z̄ for p;
   - z̄ for j₁.

   Linear forms preserve x + y + z ≡ 0.
2. **A value 2 is always forced by an identity.** Each term outputs the value
   2, rather than 3, only in a case forced by an identity, where it copies an
   argument equal to 2:
   - p₁ only when y = z and x = 2;
   - p₂ only when x = y and z = 2;
   - p only when y = z and x = 2;
   - j₁ only when z = 2 and (z = x or z = y).
3. **No all-2 output.** An output tuple (2,2,2) would therefore need one input
   tuple equal to (2,2,2): the first for p₁ and p, the third for p₂ and j₁.
   K₄ excludes that tuple.
4. **The identities** hold case by case, including on the overlaps where two
   cases meet.
5. **No Mal'tsev polymorphism.** A Mal'tsev polymorphism makes every
   pp-definable relation rectangular, and K₄ is not rectangular: the fibres
   {3} and {2, 3} meet without being equal. ∎

## Theorem 2 (the restriction lemma)

**(a) Shadows.**
- **Setting.** Let M ⊆ A^k contain every constant tuple, let h: A → B be
  surjective with h(M) ⊆ K ⊆ B^k, and let F be an n-ary polymorphism of
  M × K.
- **The fibre restriction.** For a ∈ A, let g_a(b₁, …, b_n) be the second
  component of F((a, b₁), …, (a, b_n)). Then g_a is a polymorphism of K.
- **Identities pass down.** If polymorphisms F₁, …, F_m of M × K satisfy a set
  Σ of linear identities, their restrictions g_a satisfy Σ for each a. In a
  linear identity each side is a single operation applied to variables, or a
  variable.

**(b) Congruence classes.**
- **Setting.** Let θ be a pp-definable equivalence and C a θ-class. Suppose
  polymorphisms F₁, …, F_m satisfy Σ and are idempotent: Fⱼ(x, …, x) = x.
- **The restriction.** Each Fⱼ maps Cⁿ into C, and its restriction preserves
  R ∩ C^k for every relation R of the law.
- **Identities pass down.** The restrictions satisfy Σ.
- **When idempotence holds.** Hagemann–Mitschke, Day and Gumm terms are
  idempotent, since setting all variables equal in their identities gives
  F(x, …, x) = x.

*Proof.*
- **(a), g_a is a polymorphism.** Take K-tuples β¹, …, βⁿ and form the
  M × K-tuples with first components (a, …, a), which lie in M. Applying F
  gives a tuple of M × K, whose second component is g_a applied to the βʲ.
- **(a), identities.** Restrict every variable to the fibre {a} × B. Equal
  values have equal second components, and a variable's second component is
  itself.
- **(b), staying in C.** If all inputs lie in C, the output is θ-related to
  Fⱼ(c, …, c) = c.
- **(b), the rest.** Polymorphisms preserve R, and the identities restrict
  verbatim. ∎

## Theorem 3 (K₆ is neither modular nor permutable)

K₆'s law composes like cycles, but the variety its polymorphisms generate is
not congruence modular and not congruence n-permutable for any n.

*Proof.*
1. **K₆ composes like cycles.** Take M the Z₃ law (it contains the constants)
   and h = (0, 0, 1). Then h(M) is exactly "not exactly two ones". The shadow
   theorem applies.
2. **The fibre clone.** By Theorem 2(a), any Day or Hagemann–Mitschke terms
   for K₆ restrict to such terms among the polymorphisms of N₂, "not exactly
   two ones" on {0, 1}.
   - Exhaustive enumeration shows that N₂'s ternary and 4-ary polymorphisms
     are exactly the conjunctions of some of their arguments and the two
     constants: 9 and 17 of them.
   - Day terms are 4-ary, and Hagemann–Mitschke terms are ternary.
3. **No Day terms.** The identity mᵢ(x,y,y,x) = x forces each mᵢ to be the
   conjunction of a nonempty subset Sᵢ of {1, 4}.
   - The three choices x₁, x₄ and x₁ ∧ x₄ are distinct functions, both of
     (x,x,u,u) and of (x,y,y,u).
   - So each linking identity forces Sᵢ = Sᵢ₊₁.
   - But S₀ = {1} and S_n = {4}. By Day's theorem the variety is not modular.
4. **No Hagemann–Mitschke terms.** Conjunctions and constants are monotone.
   - The chain gives 1 = p₁(1,0,0) ≤ p₁(1,1,0) = p₂(1,0,0) ≤ … ≤
     p_{n−1}(1,1,0) = 0, a contradiction.
   - By Hagemann and Mitschke the variety is not n-permutable for any n. ∎

**Census A agrees.**
- Its exhaustive two-element search (H3) finds no Day and no Hagemann–Mitschke
  chain in N₂'s clone, and none for the block clones of the lifts L₂₂₃ and
  L₂₃₃ (H2).
- **Dressings (H5).** Seven of the eight Boolean dressings K ⊇ N₂ give the
  same verdict. Only the full relation, which adds no decoration, has chains.
  So under these Z₃ tops, any genuine decoration costs modularity and
  permutability.

## Corollary 4 (incomparability)

Composing like cycles is incomparable with congruence permutability,
n-permutability and congruence modularity.
- **Permutability does not imply it.** Both of these laws have the Mal'tsev
  polymorphism x − y + z, yet fail elimination (the circuits proof; explicit
  systems in the checks):
  - x + y + z ≡ 0 over Z₆;
  - the Z₂ × Z₂ law that also contains the two line congruences
    x ⊕ y ∈ {0, 1} and x ⊕ y ∈ {0, 2}.
- **A correction to census A's contract.** Its control description called
  x ⊕ y ⊕ z = 0 over Z₂ × Z₂ a law that fails. On its own that relation does
  compose like cycles.
  - It is binary parity on both bits at once, so its systems have parity's
    free sets.
  - Its automorphisms move every line, so no line congruence is
    pp-definable.

  The census tested only the Mal'tsev polymorphism, so its results stand.
- **It does not imply modularity or n-permutability:** K₆ (Theorem 3).
- **It does not exclude them either:** K₄ is 3-permutable and modular
  (Theorem 1).

So composing like cycles is not one of the classical Mal'tsev conditions. The
top lemma for all such laws cannot rest on modularity.

## Theorem 5 (Mal'tsev on the tops)

**Definition.** A law that composes like cycles is **Mal'tsev on its tops**
when it has a ternary polymorphism F with these properties. Take any range B
of any system, with μ_B its unique maximal pp-definable equivalence (the
matroid proof, Proposition 6). Then for all x, y ∈ B, F(x,y,y) μ_B x and
F(x,x,y) μ_B y.

**The theorem.** Let M be a difference law, with Mal'tsev polymorphism m,
that composes like cycles. Then each of these laws is Mal'tsev on its tops:
1. M itself;
2. every lift L = g⁻¹(M) − {(a, …, a)} under the lift theorem's hypotheses
   (constants, no free identifications);
3. every shadow M × K in which equality of first components is pp-definable,
   such as K₆ and K₄ₓ₄.

*Proof.*
- **M itself.** Take F = m.
- **Lifts.**
  - Take F = h′ ∘ m ∘ g, where h′ sends a to its copy a′ and fixes the rest.
  - F preserves L. Since g ∘ F = m ∘ g, images under g stay in M. F never
    outputs a, so it never outputs (a, …, a).
  - The ranges are D and, at pinned variables, D − {a} (the lift theorem).
  - On D − {a}, F is exactly Mal'tsev, since h′ ∘ g is the identity there.
  - On D, F(x,y,y) has the same image under g as x, and F(x,x,y) as y.
- **The kernel of g lies below μ_D.**
  - Let Ψ relate two values of A that have a common extension in M:
    (x, z̄) ∈ M and (y, z̄) ∈ M for one tuple z̄.
  - The formula ∃z̄ (L(x, z̄) ∧ L(y, z̄)) defines g⁻¹(Ψ). Lift z̄ with a′ in
    place of a, so that neither tuple is (a, …, a).
  - Ψ is an equivalence: if z̄ links x to y and z̄′ links y to w, then
    m((x, z̄), (y, z̄), (y, z̄′)) = (x, z̄′) links x to w.
  - Ψ is proper. Otherwise, for all x and y, a common extension z̄ gives
    m((x, z̄), (y, z̄), (y, …, y)) = (x, y, …, y) ∈ M. Identifying all
    positions but the first would leave the full relation, a free
    identification.
  - So the kernel of g lies in the proper pp-definable equivalence g⁻¹(Ψ), and
    hence below μ_D.
- **Shadows M × K.**
  - Take F = (m, h ∘ m): the first component is m on the first components, and
    the second component is h of that value.
  - F preserves M × K, because h(M) ⊆ K.
  - Every range is all of A × B (the shadow theorem).
  - F(x,y,y) has the same first component as x, and F(x,x,y) as y. Equality
    of first components is a proper pp-definable equivalence by hypothesis, so
    it lies below μ. ∎

**The hypothesis on shadows is needed for this F.**
- Take K = M and h the identity. One pp-formula then defines the same
  equivalence E on both components, so every pp-definable equivalence is
  E × E.
- So μ = E × E for a proper E, and F(x,y,y) = (x_A, x_A) is not μ-related to
  x = (x_A, x_B) when x_B is not E-related to x_A.
- That law is still Mal'tsev on its tops, through (m, m). Other shadows are
  open.

**The checks.** They verify:
- the operations for K₄ (exact on its pinned range {0,1,3}), the GF(4) lift,
  K₆ and the 4-variable product K₄ₓ₄;
- the pp-definitions used, for each of these laws R: the formula
  ∃z̄ (R(x, z̄) ∧ R(y, z̄)) defines the kernel of g for the two lifts, and
  equality of first components for the two shadows;
- for the Z₃ law paired with itself, that the shadow operation fails modulo
  E × E for every proper E.

**Census A (H4).** The census found such operations by search for K₄, K₆,
K₄ₓ₄ and the two non-constant removals L₂₂₃ and L₂₃₃. These two are observed,
not proved, to compose like cycles. In each case the top used is the largest
derived equivalence.

## Conjecture 6 (cycles are decided on the tops)

Every law that composes like cycles is Mal'tsev on its tops. Below the tops it
can carry clones far from Mal'tsev:
- semilattice fibres in K₆;
- the clone of "all but 001" on L₂₂₃'s block.

Composition does not see that structure.

**The combined picture.** Together with the matroid proof's top lemma
conjecture, this predicts the following. A law composes like cycles exactly
when:
- each range has one maximal congruence;
- the law is Mal'tsev on its tops;
- the free sets can be read modulo the tops (the top lemma).

Theorem 1 of the circuits proof is the case where F is a Mal'tsev operation
outright.

## What this does not show

- **Conjecture 6** is not proved.
- **Shadows in general.** Theorem 5 covers shadows in which equality of first
  components is pp-definable. For the others, the operation (m, h ∘ m) can
  fail, and whether some other operation works is open.
- **L₂₂₃ and L₂₃₃** are observed to compose like cycles (census
  `MATROID-CONVERSE-20261021-001A-E001`) but not proved to.
- **Taylor terms.** Whether composing like cycles forces a Taylor term, or any
  other condition without bare variables, is not decided.
- **Knots only.** The variant for laws that compose only their knots like
  cycles is not addressed.
- **No protected structure.** No native recurrence, composed topology in the
  protected sense, path or distance is claimed.

## Checks

`check.py` writes `result.json`. All checks pass, and all controls are
rejected.

- **Theorem 1.** The explicit Hagemann–Mitschke and Gumm terms for K₄ are
  polymorphisms and satisfy their identities. K₄ is not rectangular.
- **Theorem 2.**
  - Every fibre restriction of 20 random ternary polymorphisms of K₆ is a
    polymorphism of N₂.
  - K₄'s terms map the class {2, 3} into itself and preserve the block
    relation there.
- **Theorem 3.**
  - N₂'s 9 ternary and 17 quaternary polymorphisms are exactly the
    conjunctions and constants, with no Day and no Hagemann–Mitschke chain.
  - K₆ has the Z₃ law's constrained sets in 300 random systems.
- **Corollary 4.**
  - Z₆, and Z₂ × Z₂ with its line congruences, have x − y + z as a
    polymorphism, and each has a failing system.
  - x ⊕ y ⊕ z = 0 over Z₂ × Z₂ alone has parity's free sets in 200 random
    systems.
- **Theorem 5.**
  - The explicit operations for K₄, the GF(4) lift, K₆ and K₄ₓ₄ are Mal'tsev
    on their tops.
  - The pp-definitions of the kernel of g and of equal first components hold.
  - The shadow operation fails for the Z₃ law paired with itself.
  - The census's search witnesses for L₂₂₃ and L₂₃₃ re-verify.
- **Census agreement.** A's predictions H1–H5 hold.
- **Controls:**
  - "composing like cycles implies modularity" and "implies n-permutability",
    both rejected by K₆;
  - "a Mal'tsev polymorphism implies composing like cycles", rejected by Z₆
    and by Z₂ × Z₂ with its line congruences;
  - "every law is Mal'tsev on its tops", rejected by the Boolean neither-knot,
    which is simple and has no Mal'tsev polymorphism.
