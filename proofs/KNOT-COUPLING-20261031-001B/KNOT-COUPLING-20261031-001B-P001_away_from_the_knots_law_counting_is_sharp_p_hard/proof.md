# Away from the knot's law, counting on the knot's spaces is #P-hard

Status: Proved

Ticket `KNOT-COUPLING-20261031-001B`, 2026-10-31.

## Dependencies

- **`KNOT-COUPLING-20261031-001A`.** Lemma 1 (the even-subgraph form), Lemma 3 (decoration and chains), Lemma 4 (at λ = 0 an atom is a
  negation; which decorated systems are knot's spaces), Proposition 6 (real couplings) and Proposition 8 (the dimer coupling).
- **`PLAIN-COUNT-20261031-001A`, Theorem 4** (the note's Theorem D). Counting the proper 2-colourings of cubic triple systems whose
  incidence graphs are Pfaffian is #P-hard under Turing reductions.
- **`COUNT-NOTE-20261031-001`.** Theorem 1: #col(H − L) is polynomial for knot's spaces. Lemma 6: the dictionary.
- **External, not replayed.**
  - A Pfaffian signing of a Pfaffian bipartite graph can be found in polynomial time (Robertson–Seymour–Thomas 1999; McCuaig 2004).
  - Kasteleyn's theorem.
  - Counting perfect matchings of cubic bipartite graphs is #P-complete (Dagum–Luby 1992).
  - The algorithm in `hard_lib.py` for exponential sums of quadratic polynomials over GF(2) is self-contained.

## The problem

- **Setting.** As in ticket A: M(H; λ) sums λ^{mono(c)} over the 2-colourings c, a *knot's space* is a connected cubic triple system that
  is not 2-colourable, and u = (λ − 1)/(λ + 3).
- **#KNOT(λ₀).** Given a knot's space H, compute M(H; λ₀).
- **λ₀ = ∞.** This means the leading coefficient, the number of colourings in which every line is monochromatic.

## Theorem 1 (one good atom makes the knot's spaces hard)

- **Statement.** Let λ₀ ∈ ℂ ∖ {1, −3}. Suppose some atom H*⟨e₀⟩, with H* a knot's space, has α + β ≠ 0 at λ₀ and ρ = (α − β)/(α + β) with
  ρ² of infinite multiplicative order. Then #KNOT(λ₀) is #P-hard under polynomial-time Turing reductions.
- **Proof.**
  1. **Source.** Let G be a cubic triple system with Pfaffian incidence graph, n points and 3n incidences. Computing #col(G) is #P-hard
     (Theorem 4 of `PLAIN-COUNT-20261031-001A`); the source instances there are connected. Find a Pfaffian signing of B(G) (RST) and let
     O be its negation set.
  2. **Instances.** For 0 ≤ i ≤ Dₐ and 0 ≤ j ≤ D_b, let G_ij carry a chain of 2i atoms on every incidence outside O and 2j + 1 atoms on
     every incidence of O. Here Dₐ and D_b bound |χ ∖ O| and |χ ∩ O| over the even subgraphs χ of B(G); Dₐ = 3n − |O| and D_b = |O|
     always suffice.
     - By ticket A, Lemma 4, every G_ij is a knot's space: its odd chains sit exactly on a Pfaffian negation set, and it is connected.
     - Its size is O(n²) atoms.
  3. **The oracle identity.** By ticket A, Lemma 3 (chains act multilinearly) and Lemma 1 (applied to the signed systems G^S):

     M(G_ij; λ₀) = 2ⁿ ((λ₀ + 3)/4)ⁿ (α + β)^{Σ k_e} · Q(ρ^{2i}, ρ^{2j}),

     where Q(a, b) = Σ_χ u₀^{|χ|/2} ρ^{|χ ∩ O|} a^{|χ ∖ O|} b^{|χ ∩ O|}.
     - Expanding Σ_S Π_e c_e(±) M(G^S) and summing over S gives Π_e (c_e(+) + (−1)^{[e ∈ χ]} c_e(−)) = (α + β)^{k_e} or (α − β)^{k_e}
       for each e.
     - The prefactor is not zero, since λ₀ ≠ −3 and α + β ≠ 0.
  4. **Interpolation.** The nodes ρ^{2i} (i ≤ Dₐ) are distinct, and so are the ρ^{2j} (j ≤ D_b). So the tensor-product Vandermonde
     system determines every coefficient q_rs of Q (interpolate in b, then in a).
  5. **Evaluation.** By Lemma 1 at λ = 0 (where u = −1/3 and (λ + 3)/4 = 3/4),

     #col(G) = 2ⁿ (3/4)ⁿ Σ_{r,s} q_rs ρ^{−s} (−1/(3u₀))^{(r+s)/2}.

     - r + s = |χ| is even (B(G) is bipartite), so no square root is chosen.
     - u₀ ≠ 0, since λ₀ ≠ 1.
  6. **Count.** There are (Dₐ + 1)(D_b + 1) ≤ (3n + 1)² oracle calls. ∎

## Corollary 2 (every real coupling but four)

- **Statement.** For every real λ₀ ∉ {0, 1, −1, −3}, #KNOT(λ₀) is #P-hard.
- **Proof.** By ticket A, Proposition 6, one of the Fano and splice atoms has α + β ≠ 0 and a real ratio ρ ∉ {0, ±1}. Then |ρ| ≠ 1 and ρ²
  has infinite order. Apply Theorem 1. ∎

## Proposition 3 (the five easy couplings)

On knot's spaces M(H; λ) is polynomial-time computable at λ ∈ {0, 1, −1, ∞, −3}:

| λ | value | why |
| --- | --- | --- |
| 0 | M = #col = 0 | by definition |
| 1 | M = 2ⁿ | every line weighs 1 |
| −1 | M = Σ_c (−1)^{Q(c)} for a quadratic Q over GF(2) | [line monochromatic] = 1 + e₁ + e₂ (mod 2) in its three signed bits; eliminating one variable either kills the sum or substitutes a linear relation |
| ∞ | the number of colourings with every line monochromatic, 2^{nullity} or 0 | Gaussian elimination over GF(2) |
| −3 | M = (−2)ⁿ #PM(B(H)) = (−2)ⁿ \|det B(H)\| | ticket A, Proposition 8 |

- **Easy for every system.** λ ∈ {1, −1, ∞}.
- **Easy only on the knot's spaces.** λ = 0 and λ = −3 are #P-hard on general cubic systems: the not-all-equal count (Fan–Cai; the note's
  Theorems C and D), and the permanent of cubic bipartite graphs (Dagum–Luby).

## Theorem 4 (deficiency one)

- **Statement.** For every real λ₀ ∉ {0, 1, −1, −3}, computing M(H − L; λ₀) for knot's spaces H and lines L is #P-hard. At λ₀ = 0 it is
  polynomial (the note's Theorem 1), and at λ₀ ∈ {1, −1, ∞} the algorithms of Proposition 3 apply to any system.
- **Proof.** As in Theorem 1, with a third parameter.
  - **The extra incidence.** Choose an incidence e* ∉ O. On it put a chain of 2k + 2 atoms (k ∈ {0, 1}) whose first atom is a Fano atom
    with one further line L′ ≠ l₀ deleted. Before the deletion the system is a knot's space (even chain), and the deleted line is a line
    of it.
  - **The modified atom.** Lemmas 2 and 3 of ticket A hold for any system, so the modified first atom acts by [[α′, β′], [β′, α′]], with
    α′, β′ the half-counts of Fano − L′ with e₀ restored or negated. Chains of mixed atoms commute, since all their edge functions have
    the form [[a, b], [b, a]].
  - **The values.** M(H′ − L′; λ₀) = (prefactor) · (Q₀(a, b) + ρ^{2k+1}ρ′ Q₁(a, b)). Two values of k separate Q₀ and Q₁. Then
    Q = Q₀ + a Q₁ weights e* like every other incidence outside O, and the proof ends as before.
  - **The condition.** This needs α′ + β′ ≠ 0 and ρ′ ≠ 0 at λ₀ for some L′. The degeneracy polynomials (α′ + β′)(α′ − β′) of the six
    line-deleted Fano atoms have no common real root outside {0, ±1, −3} (check 6).
  - **Mixing atoms.** The chain atoms are chosen by Corollary 2; atoms of different types may be mixed, because Lemma 4 of ticket A holds
    atom by atom. ∎

## Remark 5 (deficiency one at the dimer coupling is open)

- **The structure.** At λ = −3 every surviving line uses exactly two of its incidences, so exactly one point p is unused. Hence

  M(H − L; −3) = 2ⁿ Σ_p #PM(B(H) − N[L] − N[p]).

  This is checked on the Fano plane (1792 = 2⁷·14) and the splice (1015808 = 2¹³·124).
- **Why it stays open.** For both, some of the subgraphs B(H) − N[L] − N[p] have #PM ≠ |det|. So the dimer argument does not apply
  directly, and Theorem 4's interpolation needs λ₀ ≠ −3 (the coupling u = ∞ cannot be moved by edge weights).

## End-to-end evidence (checks 3 and 6)

The colouring counts of three sources are recovered exactly from counts of knot's spaces, all computed by `hard_lib.count`. That counter
shares no code with ticket A.

| Source (#col) | Atom | λ₀ | Oracle calls | Largest instance (lines) |
| --- | --- | --- | --- | --- |
| K₄⁽³⁾ (6) | Fano | 2 | 32 | 1033 |
| K₄⁽³⁾ (6) | Fano | −1/2 | 32 | 1033 |
| K₄⁽³⁾ (6) | Fano | 1 + i | 32 | 1033 |
| K₄⁽³⁾ (6) | 13-point splice | 2 | 32 | 1915 |
| 6-prism system (20) | Fano | 2 | 52 | 2673 |
| K₄⁽³⁾ with a Fano atom (30, not planar) | Fano | 2 | 69 | 9629 |
| K₄⁽³⁾ (6), deficiency one | Fano, line deleted | 2 | 64 | 962 |

- **The oracle identity** is checked separately against a direct sum over even subgraphs (check 2).
- **Every instance used is a connected cubic knot's space** (check 1).

## Controls (check 7)

The reduction degenerates exactly at the special couplings:
- at λ₀ = 0 every oracle value is 0;
- at λ₀ = −3 the prefactor vanishes;
- at λ₀ = 1 every ratio is 0.

## What this does not establish

- Complex couplings beyond Theorem 1's hypothesis (ticket C).
- Deficiency one at λ = −3 (Remark 5).
- Approximate counting.

## Novelty

- **Standard.** The reduction is a gadget-and-interpolation argument (Valiant; Dyer and Greenhill; Cai, Lu and Xia). The source hardness is
  the counting arc's (Fan–Cai, `SOFT-CROSS-20261031-001B`, `PLAIN-COUNT-20261031-001A`).
- **New here (no overlap found yet).** The dichotomy restricted to the knot's spaces, the non-2-colourable cubic triple systems. On them
  exactly two couplings beyond the affine ones are easy, λ = 0 and λ = −3. Both come from the Pfaffian structure: the dictionary
  (non-colourable ⇔ Pfaffian) and Kasteleyn (#PM = |det|).
- **Literature check.** At closure.
