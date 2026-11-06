# The complex couplings

Status: Proved

Ticket `KNOT-COUPLING-20261031-001C`, 2026-10-31.

## Dependencies

- **`KNOT-COUPLING-20261031-001A`.** The atom ratios (Proposition 5) and their independence (Proposition 7).
- **`KNOT-COUPLING-20261031-001B`.** Theorem 1 (one good atom makes #KNOT(λ₀) hard), Proposition 3 (the easy couplings) and Theorem 4 (its
  deficiency-one variant).
- **External, not replayed.**
  - Lang's theorem (Ihara, Serre and Tate): a curve in 𝔾ₘ² with infinitely many torsion points is a torsion coset of a subtorus.
  - Beukers and Smyth, *Cyclotomic points on curves* (2002), Lemma 1: a torsion point of f(X, Y) = 0, with f over ℚ, is also a zero of one
    of f(−X, Y), f(X, −Y), f(−X, −Y), f(±X², ±Y²). It follows by applying the Galois automorphisms ζ ↦ ζ², ζ ↦ ζ^{M+2} and ζ ↦ ζ^{1+N/2}.

## The statement

**Theorem 1 (the coupling dichotomy on the knot's spaces).** For λ₀ ∈ ℂ ∪ {∞}, counting M(H; λ₀) for knot's spaces H is
- polynomial if λ₀ ∈ {0, 1, −1, −3, ∞};
- #P-hard (Turing) otherwise.

With one line deleted (deficiency one) the same holds, except that λ₀ = −3 is left open.

## Proof

- **What must be shown.** By ticket B (Theorem 1 and Proposition 3), it suffices that at every λ₀ ∉ {0, 1, −1, −3, ∞} one of two atoms has
  a finite, nonzero ratio of infinite multiplicative order (then ρ² has infinite order too). The two atoms are the Fano atom (ratio ρ_F) and
  an atom of the 13-point splice from its class of 12 incidences (ratio ρ_S):
  - ρ_F = (λ−1)³(λ+1)(λ³+λ²+λ+5) / (λ⁷+λ⁶+λ⁵+9λ⁴+9λ³+41λ²+61λ+5);
  - ρ_S = (λ−1)³(λ+1)(λ⁹+λ⁸+λ⁷+11λ⁶+6λ⁵+24λ⁴+61λ³+51λ²+75λ+25) / (λ¹³+λ¹²+λ¹¹+17λ¹⁰+21λ⁹+83λ⁸+246λ⁷+310λ⁶+783λ⁵+1547λ⁴+2241λ³+2241λ²+675λ+25).

  They agree with ticket A (check 1).
- **Step 1 (the curve).**
  - f(X, Y) = Res_λ(X d_F − n_F, Y d_S − n_S) is irreducible over ℚ, of bidegree (13, 7) with 102 terms (check 2).
  - The points (ρ_F(λ), ρ_S(λ)) lie on f = 0.
  - By ticket A, Proposition 7, no relation ρ_F^a ρ_S^b = constant holds, so f = 0 is not a torsion coset and has finitely many torsion
    points (Lang).
- **Step 2 (Beukers–Smyth).**
  - For each of the seven substitutions g, the resultants Res_Y(f, g) and Res_X(f, g) are nonzero, so f does not divide g. Their degrees
    are 169 to 364.
  - Their cyclotomic factors are only Φ₁ and Φ₂. Every m with φ(m) ≤ deg was tested (φ(m) ≥ √(m/2), so m ≤ 2·deg² suffices): by
    evaluation at a primitive m-th root of unity in two prime fields F_p with p ≡ 1 (mod m), confirmed by exact division (check 3).
  - So a torsion point of f has coordinates in {±1}. Testing the four candidates exactly leaves (1, 1) and (−1, −1) (check 4).
- **Step 3 (back to λ).**
  - ρ = −1 means M = 0, and gcd(M_F, M_S) = 2λ, so (−1, −1) is reached only at λ = 0.
  - ρ = 1 means M^{e₀} = 0, and gcd(M_F^{e₀}, M_S^{e₀}) = 2, so (1, 1) is reached by no finite λ. It is the limit at λ = ∞ (check 5).
- **Step 4 (zeros and poles).** For each irreducible factor φ of n_F, d_F, n_S, d_S:
  - the values of the other ratio at the roots of φ are the roots of Res_λ(φ, Y d − n);
  - none is 0, infinite or a root of unity (no cyclotomic factor), except for φ = λ ∓ 1, where both ratios are 0 (check 6);
  - by Galois conjugacy the test is all-or-nothing for each φ.
- **Conclusion.** At every λ₀ ∉ {0, 1, −1, −3, ∞}, at least one ratio is finite, nonzero and not a root of unity. λ₀ = −3 is excluded
  separately: there u₀ = ∞, and it is easy (ticket B, Proposition 3). Ticket B, Theorem 1 then gives hardness.
- **Deficiency one.** Ticket B, Theorem 4 also needs one line-deleted Fano atom with α′ ± β′ ≠ 0. The gcd of the six line-deleted atoms'
  degeneracy polynomials is (λ − 1)³ (check 7). So for every λ₀ ∉ {0, 1, −1, −3}, some line-deleted atom is non-degenerate, and the chain
  atom comes from the conclusion above. ∎

## Controls (check 8)

- The dependent pair (ρ_F, ρ_F²) gives the curve Y = X², a subtorus with infinitely many torsion points. Independence is what the argument
  uses.
- The known torsion point (−1, −1) at λ = 0 is found.

## Reading

- On the knot's spaces exactly two non-trivial laws are easy:
  - **the knot's own law, λ = 0** (not-all-equal). The count vanishes (non-colourability), and with one line deleted it is a product of
    determinants (the note's Theorem 1);
  - **the dimer law, λ = −3.** The count is (−2)ⁿ |det| of the incidence matrix.
- Both are faces of one fact, that the knot's spaces are exactly the cubic systems with a Pfaffian incidence graph whose plain signing is
  Pfaffian.
- At every other coupling, real or complex, the knot's spaces are as hard as general systems.

## What this does not establish

- Deficiency one at λ = −3 (ticket B, Remark 5).
- Approximate counting.
- Signed systems in the knot's class: the plain knot's spaces are a subclass, so hardness transfers to the signed class. The signed class's
  easy points are the same five by the same algorithms; at λ = −3 the count is (−2)ⁿ det of the plain incidence matrix up to sign (ticket A,
  Proposition 8).

## Novelty

- **Classical.** Torsion points on curves (Lang; Ihara, Serre and Tate; Beukers and Smyth). Algebraic-independence closures of
  interpolation arguments are common in Holant dichotomies.
- **No overlap found yet.** The dichotomy for the knot's spaces. The literature check comes at closure.
