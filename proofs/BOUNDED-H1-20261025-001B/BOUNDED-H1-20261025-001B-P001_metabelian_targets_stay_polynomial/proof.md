# Metabelian targets stay polynomial with bounded homology

Status: Proved

## Standard statement

**Theorem.** Let G be a finite group with an abelian normal subgroup N such that Q = G/N is nilpotent. Every metabelian group qualifies,
with N = G′. Fix an integer d. There is a polynomial-time algorithm for the following problem.

- **Input.**
  - A finite presentation ⟨X | R⟩ of a group P with dim H₁(P; F_p) ≤ d for every prime p dividing |Q|.
  - Optionally, one generator x₀ and a conjugacy class C of G.
- **Output.** The number of homomorphisms P → G, sending x₀ into C when that constraint is given.

**Corollary.** In particular, counting is polynomial for:
- closed orientable 3-manifolds with |H₁(M; Z)| bounded, given by triangulations;
- knot groups with the meridian sent to a fixed class, given by diagrams.

The second case holds because H₁ = Z and all meridians are conjugate. This includes S₃, every dihedral and dicyclic group, Q₈, A₄,
Z_ℓ ⋊ Z_p and every group of order p³.

**The contrast.** S₄ has no such decomposition. Its abelian normal subgroups are 1 and V₄, and S₄/V₄ ≅ S₃ is not nilpotent. On knot
groups it sums over the 3ⁿ homomorphisms into S₃ exhibited in `BOUNDED-H1-20261025-001A`, and that sum is #P-hard (Theorem 3 there).

## Nearest known result

- **Matei and Suciu (2005)** count epimorphisms onto finite solvable groups through twisted cohomology in degrees 1 and 2. Samperton
  and Weiß note that no complexity bounds were given there.
- **Samperton and Weiß (2026)**: class-2 targets on triangulated 3-manifolds are polynomial when |H²(M; Z(G))| is bounded.
- **Affine (Alexander) quandle colourings of knots** are counted by linear algebra; this is classical.
- **What is new here.** The explicit polynomial statement for abelian-by-nilpotent targets under bounded mod-p homology.
- **Novelty.** Folklore risk high: this is a direct use of twisted 1-cocycles. It is recorded so that the line is explicit.

## Proof

**1. Homomorphisms to Q are boundedly many and enumerable.**
- **A central series.** Q is nilpotent, so G has normal subgroups G = K₀ > K₁ > ⋯ > K_s = N such that each K_i/K_{i+1} is central in
  G/K_{i+1} and has prime order p_i. Pick z_i ∈ K_i \ K_{i+1}.
- **Lifting one level.** Suppose ρ: P → G/K_i is given by representatives g_x. Its lifts to G/K_{i+1} are g_x z_i^{a_x} with
  a ∈ F_{p_i}^X. Since z_i is central modulo K_{i+1}, each relator r gives one linear equation
  t_r + Σ_x ε_x(r) a_x = 0 over F_{p_i}. Here r(g) ≡ z_i^{t_r} modulo K_{i+1}, and ε_x(r) is the exponent sum of x in r.
- **The lifts are few.** The solutions form a translate of {a : Σ_x ε_x(r) a_x = 0 for all r} = Hom(H₁(P), F_{p_i}), of size at most
  p_i^d.
- **Conclusion.** |Hom(P, Q)| ≤ Π_i p_i^d = |Q|^d, and each level costs one F_p elimination of polynomial size.

**2. The lifts through N form an affine space.**
- **The unknowns.** Fix representatives g_x of a homomorphism P → G/N. Every lift has the form x ↦ g_x n_x with n_x ∈ N.
- **The relators become linear.** For a relator r, the value r(g) lies in N, and r(g)⁻¹ r(g n) is a sum of conjugates of the n_x^{±1}
  (Fox calculus). So it is a homomorphism N^X → N.
- **The system.** The lifts are the solutions of a linear system over the finite abelian group N, with coefficients in the action of
  Q on N.
- **Counting.** Decompose N into p-parts. For each part, count the solutions over Z/p^a by elimination with valuation pivots, which is a
  Smith form over a chain ring: a pivot p^v contributes p^v solutions if it divides the right-hand side and none otherwise, and each free
  column contributes p^a.
- **The class constraint on x₀.** Run over the |N| or fewer admissible values of n_{x₀}, fixing it in each run.

**3. Size.** The work is polynomial in |X| and |R| for fixed G and d:
- at most |Q|^d homomorphisms into Q;
- |N| runs per constrained generator;
- linear algebra over each run.

**4. Corollary.**
- **3-manifolds.** A triangulation gives a presentation of π₁ in polynomial time; this is standard and cited. dim H₁(M; F_p) is bounded
  by log₂|H₁(M; Z)| plus b₁.
- **Knots.** A Wirtinger presentation has H₁ = Z, so d = 1. Constraining one meridian constrains all of them. ∎

## Check

`check.py` uses the standard library only and runs in about 1 s. Its output is `result.json`.

1. **Decompositions.** Every test group has an abelian normal N with nilpotent quotient: S₃, D₈, Q₈, A₄, the dihedral group of order
   16, Z₃ ⋊ Z₄, Z₇ ⋊ Z₃, and the Heisenberg group of order 27. S₄ has none.
2. **Random presentations.** For each test group, 12 random presentations with dim H₁(P; F_p) ≤ 2:
   - the algorithm equals brute-force enumeration in all 96 cases;
   - |Hom(P, Q)| ≤ |Q|^d holds.
3. **Knot groups.** Wirtinger presentations of the trefoil, the cinquefoil, the figure-eight and 5₂, built as braid closures with
   signs, with the meridian sent into each conjugacy class of S₃, A₄, D₈, Q₈ and Z₃ ⋊ Z₄. The algorithm equals brute force in all 39
   cases small enough to enumerate.
4. **Scale.** The tripled alternating knots of the 2×3, 2×5 and 3×4 grids have 21, 39 and 51 Wirtinger generators. The algorithm
   returns their S₃ transposition counts 3⁶, 3¹⁰ and 3¹² in a few hundredths of a second, as `BOUNDED-H1-20261025-001A` predicts.
   These counts are exponential, but they are computed by linear algebra.
5. **Controls.**
   - Hom(Z₂⁶, Z₂) has 64 elements, so the bound needs bounded homology.
   - S₄ is not abelian-by-nilpotent.
   - Commuting pairs in S₃ are counted correctly (18).

## Scope

- **A sufficient condition, not a classification.** For example, SL(2,3) is not abelian-by-nilpotent: its only non-trivial abelian
  normal subgroup is the centre, and the quotient A₄ is not nilpotent. Whether it is polynomial with bounded homology is not settled
  here. Its lifting obstruction on closed 3-manifolds is quadratic, which suggests that it is.
- **Cited, not proved.** Polynomial-time conversion of triangulations into presentations.
- **No overclaim.** No claim about P versus NP.
