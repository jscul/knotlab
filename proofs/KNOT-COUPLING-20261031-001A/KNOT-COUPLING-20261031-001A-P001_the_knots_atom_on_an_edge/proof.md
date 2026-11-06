# The knot's atom on an edge

Status: Proved

Ticket `KNOT-COUPLING-20261031-001A`, 2026-10-31.

## Dependencies

- **`COUNT-NOTE-20261031-001`, Lemma 6 (the dictionary).** A connected cubic signed system is not 2-colourable iff its signing is Pfaffian.
  For plain systems this is Seymour (1974) with Robertson–Seymour–Thomas (1999). The signed form is `THREEFOLD-AMPLITUDE-20261030-001C`,
  Lemma 4.
- **`THREEFOLD-SPACES-20261030-001A`.** The point splice. The 13-point Fano splice is a knot's space; check.py re-verifies this by
  enumeration.
- **`NEXT-DIRECTION-SCAN-20261031-001B`.** Lane B's script is re-examined in Correction 9.
- **External, not replayed.** Kasteleyn's theorem (a Pfaffian signing gives |det| = #PM). The #P-completeness of counting perfect matchings
  of cubic bipartite graphs (Dagum–Luby 1992).

## Setting

- **Systems.** A *cubic triple system* H has lines of three distinct points, every point on three lines, and n points and n lines. A
  *signing* σ is a set of negated incidences. B(H) is the cubic bipartite incidence graph. A *knot's space* is a connected cubic triple system
  that is not 2-colourable.
- **The coupling.** For λ ∈ ℂ, M(H, σ; λ) = Σ_c λ^{mono(c)}. The sum runs over 2-colourings c of the points, and mono(c) counts the lines
  whose three colours, flipped on negated incidences, agree. So a monochromatic line weighs λ and any other line weighs 1, and M(H, σ; 0)
  is the number of proper colourings #col.
- **The scan's notation.** u = (λ − 1)/(λ + 3) is the weight of a line of degree 2 in the even-subgraph form, and x² = u.
- **Special couplings.**

| λ | u | name |
| --- | --- | --- |
| 0 | −1/3 | not-all-equal, the knot's law |
| 1 | 0 | constant weights |
| −1 | −1 | quadratic phases (affine) |
| ∞ | 1 | each line forces equality (linear over GF(2)) |
| −3 | ∞ | the dimer coupling (Proposition 8) |

## Lemma 1 (the even-subgraph form)

M(H, σ; λ) = 2ⁿ ((λ + 3)/4)ⁿ Σ_χ u^{|χ|/2} (−1)^{|σ ∩ χ|}, the sum over the even subgraphs χ of B(H).

*Proof.* The line weight f(s) = λ for s ∈ {000, 111}, and 1 otherwise, has Hadamard transform (2λ + 6, 0, 2λ − 2, 0) by weight. Expand
every line and sum over the point colours: each point forces even degree. ∎ (Check 1.)

## Lemma 2 (the atom's edge function)

- **Statement.** Let e₀ = (l₀, p₀) be an incidence of H. Let g(a, b) sum λ^{mono} over the colourings with c(p₀) = b, evaluating l₀ with
  colour a in p₀'s place. Then g(0,0) = g(1,1) = α := M(H)/2 and g(0,1) = g(1,0) = β := M(H^{e₀})/2, where H^{e₀} negates e₀.
- **Proof.**
  - Complementing every colour preserves mono, so g(a, b) = g(1 − a, 1 − b).
  - g(0,0) + g(1,1) is M(H), because l₀ then sees p₀'s own colour.
  - g(0,1) + g(1,0) is M(H^{e₀}). ∎
- **Checked** on every incidence of the Fano plane, the 13-point splice and K₄⁽³⁾ (check 2).

## Lemma 3 (decoration and chains)

- **Decoration.** Let e = (l, p) be an incidence of a signed system G. The *decorated* system G ⊕_e H⟨e₀⟩ is formed as follows:
  - p takes p₀'s place in l₀;
  - p₀ takes p's place in l;
  - H's other points are fresh.

  It is a cubic triple system, and it is connected when G and H are. Then

  M(G ⊕_e H⟨e₀⟩) = α M(G) + β M(G^e).

  *Proof.* Group the colourings by a = c(p) and b = c(p₀). The line l₀ sees a in p₀'s place, so the part in H contributes g(a, b). The part
  in G sees b in p's place in l: a G-term when b = a, and a G^e-term when b ≠ a. ∎
- **Chains.** A chain of k atoms in series on e has edge function g^k = (α + β)^k P₊ + (α − β)^k P₋, where
  P± = ½[[1, ±1], [±1, 1]]. So

  M = ½[(α + β)^k + (α − β)^k] M(G) + ½[(α + β)^k − (α − β)^k] M(G^e),

  and chains on several incidences combine multilinearly.
- **The even-subgraph form.** P₊ and P₋ become "e unused" and "e used". So a chain multiplies every even subgraph by (α + β)^k, and those
  through e by ρ^k, with ρ := (α − β)/(α + β).
- **Checked** in 32 cases: 16 decorated systems at two values of λ each, built from K₄⁽³⁾ and the 6-prism system with Fano and splice
  atoms in chains on one or two incidences, compared as exact values (check 3).

## Lemma 4 (at the knot's law an atom is a negation)

- **Statement.** Let H be a knot's space and e₀ any incidence. At λ = 0:
  - α = 0 and β ≠ 0, so the atom acts on its edge as β times a negation;
  - a chain of k atoms acts as β^k times the identity (k even) or a negation (k odd);
  - let G be connected and decorated with chains of lengths k_e; with O the set of incidences carrying odd chains,
    #col(G′) = β^{Σ k_e} #col(G^O).

  So G′ is a knot's space iff O is the negation set of a Pfaffian signing of B(G).
- **Proof.**
  - α = #col(H)/2 = 0.
  - β = #col(H^{e₀})/2. B(H) is cubic and bipartite, so it has no bridge: a one-edge cut δ(X) would need 3(|X ∩ P| − |X ∩ L|) = ±1. So
    the one-edge signing {e₀} is not a cut, differs from the Pfaffian empty signing, is not Pfaffian, and H^{e₀} is colourable (dictionary).
  - The rest is Lemma 3 at λ = 0 together with the dictionary for G. ∎
- **Checked (check 5).**
  - β(0) = 5 for the Fano atom (#col(Fano^{e₀}) = 10) and 25 for every splice class (#col = 50).
  - K₄⁽³⁾ decorated on a Pfaffian negation set of three incidences is not 2-colourable.
  - K₄⁽³⁾ decorated on one incidence has 30 = β #col(K₄⁽³⁾^e) colourings.

## Proposition 5 (the ratios)

Exact ratios, with M and M^{e₀} in check 4:

| Atom (incidences) | ρ(λ) |
| --- | --- |
| Fano (21) | (λ−1)³(λ+1)(λ³+λ²+λ+5) / (λ⁷+λ⁶+λ⁵+9λ⁴+9λ³+41λ²+61λ+5) |
| splice, class 1 (3) | (λ−1)⁵(λ+1)²(λ³+λ²+λ+5)² / (λ¹³+λ¹²+2λ¹¹+18λ¹⁰+23λ⁹+103λ⁸+228λ⁷+308λ⁶+783λ⁵+1423λ⁴+2346λ³+2346λ²+585λ+25) |
| splice, class 2 (12) | (λ−1)³(λ+1)(λ⁹+λ⁸+λ⁷+11λ⁶+6λ⁵+24λ⁴+61λ³+51λ²+75λ+25) / (λ¹³+λ¹²+λ¹¹+17λ¹⁰+21λ⁹+83λ⁸+246λ⁷+310λ⁶+783λ⁵+1547λ⁴+2241λ³+2241λ²+675λ+25) |
| splice, class 3 (24) | (λ−1)³(λ¹⁰+2λ⁹+2λ⁸+13λ⁷+21λ⁶+40λ⁵+121λ⁴+177λ³+206λ²+160λ+25) / (λ¹³+λ¹²+λ¹¹+16λ¹⁰+20λ⁹+82λ⁸+229λ⁷+327λ⁶+800λ⁵+1568λ⁴+2246λ³+2141λ²+735λ+25) |

Values at the special couplings:

| λ | every atom | reading |
| --- | --- | --- |
| 0 | ρ = −1 | an exact negation |
| 1 | ρ = 0 | the atom blocks its edge |
| −1 | ρ = 0, or 1 for splice class 3 | blocks or is transparent |
| ∞ | ρ = 1 | transparent |
| −3 | ρ = 2 | finite, yet it cannot move the coupling, since u = ∞ is fixed by edge weights (Proposition 8) |

For example, ρ_Fano(1/2) = −141/6079.

## Proposition 6 (real couplings)

- **Degeneracy.** For real λ every ρ is real, so an atom *degenerates* (ρ ∈ {0, ±1} or α + β = 0) exactly at the real roots of
  M · M^{e₀} · (M − M^{e₀}) · (M + M^{e₀}).
- **Statement.** For every real λ ∉ {0, 1, −1}, at least one of the four atoms has α + β ≠ 0 and |ρ| ∉ {0, 1}.
- **Proof** (check 6).
  - Over ℚ, the Fano atom degenerates on λ, λ ± 1 and four other irreducible factors:
    - λ³+λ²+λ+5, where ρ = 0;
    - λ⁶+7λ³+21λ+35, where M = 0 and ρ = −1;
    - λ⁶+λ⁵+2λ⁴+9λ³+20λ²+26λ+5, where ρ = 1;
    - λ⁷+λ⁶+λ⁵+9λ⁴+9λ³+41λ²+61λ+5, where ρ = ∞.
    These have 1, 2, 2 and 3 real roots.
  - None of these factors divides the degeneracy polynomial of splice class 2 or 3. Since each is irreducible, those classes do not
    degenerate at its roots.
  - The factors common to all four atoms are λ, λ − 1 and λ + 1. ∎

## Proposition 7 (independence)

- **Statement.** For each splice class, no relation ρ_Fano^a ρ_splice^b = constant holds with (a, b) ≠ (0, 0).
- **Proof.** The divisors of the ratios (orders at the irreducible factors and at ∞) have rank 2 (check 7). ∎
- **Use.** This is needed for complex couplings (ticket C).

## Proposition 8 (the dimer coupling λ = −3)

- **Statement.** For every plain cubic triple system H, M(H; −3) = (−2)ⁿ #PM(B(H)).
  - **On a knot's space** this is (−2)ⁿ |det B(H)| (Kasteleyn, since the empty signing is Pfaffian), and so polynomial-time computable.
  - **On general systems** it is the permanent of a 0/1 matrix with three ones per row and column, which is #P-complete (Dagum–Luby).
  - **With a Pfaffian signing σ**, M(H, σ; −3) = ±(−2)ⁿ det of the plain incidence matrix.
- **Proof.**
  - At λ = −3 the line transform is (0, 0, −8, 0), so only even subgraphs in which every line has degree exactly 2 survive.
  - That is 2n used incidences, every point even and n points, so every point has degree 2: χ is a 2-factor, the complement of a perfect
    matching. Its weight is (1/8)ⁿ 2ⁿ (−8)ⁿ (−1)^{|σ ∩ χ|}.
  - For Pfaffian σ, sgn(π_M)(−1)^{|σ ∩ M|} is constant over perfect matchings M. ∎
- **Checked (check 8).** The Fano plane gives −3072 = (−2)⁷·24 and the splice −1572864 = (−2)¹³·192, with |det| = #PM. The colourable
  controls have #PM ≠ |det| (K₄⁽³⁾: 9 against 3; 6-prism system: 20 against 0).

## Correction 9 (to `NEXT-DIRECTION-SCAN-20261031-001B`)

- **The scan's claim.** The couplings common to every deep-branch junction that breaks the matchgate identity are exactly the finite factors
  x, x ± 1, x² + 1, 3x² + 1.
- **What it missed.** In each of the five breaking pairs, the identity's polynomial has degree below twice the entries' degree (62 < 64,
  74 < 76, 86 < 88, 86 < 88, 98 < 100). So the identity also holds at x = ∞, which is u = ∞, the dimer coupling λ = −3.
- **Corrected statement.** The common couplings are the counting point, the affine couplings and the dimer coupling. The scan's artifacts
  are left unchanged (check 9).

## Controls (check 10)

- A colourable atom (K₄⁽³⁾ minus an incidence) is not a negation at λ = 0.
- An even chain on a negation-set edge gives a colourable system.
- ρ_Fano(1/2) ∉ {0, ±1}.

## What this does not establish

- **No hardness.** That is ticket B, which uses Lemmas 3 and 4 and Proposition 6.
- **Complex couplings.** At a complex λ every atom might have a root of unity as its ratio; that is not excluded here (ticket C).

## Novelty

- **Standard.** Gadget edge functions and interpolation (Valiant; Cai, Lu and Xia; Dyer, Goldberg and Jerrum).
- **Classical.** The dimer statement restates the SNS/Pfaffian dictionary (Seymour; Robertson, Seymour and Thomas).
- **Ours.** The atom as an exact negation at the knot's law, and the dimer coupling read as a second coupling singled out by the knot's
  spaces. No overlap has been found yet; the literature check comes at closure.
