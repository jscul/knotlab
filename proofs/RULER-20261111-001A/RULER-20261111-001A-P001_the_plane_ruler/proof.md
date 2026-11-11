# Bond distance is graph distance plus one in the plane

Status: Proved

Ticket `RULER-20261111-001A`, 2026-11-11. The statement was frozen in `research/RULER-20261111-001/preregistration.md` before this proof
was written.

## Standard statement

Let Λ be the triangular lattice and N the set of 2-colourings of its vertices with no monochromatic triangle (the ground states of the
triangular Ising antiferromagnet). Call a finite vertex set shattered when every 2-colouring of it extends to an element of N. Then
every pair is shattered, the minimal non-shattered triples are exactly the triangles, and for two vertices at graph distance d the
smallest non-shattered set containing both whose every co-1 subset is shattered has exactly d + 2 vertices. Every vertex can be
flipped by a finite change of the flat three-sublattice ground state.

## Nearest known result

The height mapping of the antiferromagnet's ground states (Blöte and Hilhorst 1982; Nienhuis, Hilhorst and Blöte 1984), and the
extension of height functions by difference constraints (as for lozenge tilings, Thurston 1990). These give the tools. No statement
about the minimal non-shattered sets of the ground-state space was found (bounded search). Classification: known-with-delta; the delta
is R1, R2 and R3 below. Folklore risk moderate.

## Setup

Sites are Z², neighbours ±(1, 0), ±(0, 1), ±(1, 1), knots (triangles) {x, x + (1,0), x + (1,1)} and {x, x + (0,1), x + (1,1)}. Orient
the edges by the **forward steps** (1, 0), (0, 1) and (−1, −1). Every triangle is then a directed 3-cycle: the first uses the three
steps forwards, the second (x → x + (1,1) → x + (0,1) → x) uses all three backwards. Let c(x) = (x₁ + x₂) mod 3; every forward step
raises c by 1 mod 3. Write δ(x, y) for graph distance: for d = y − x, δ = max(|d₁|, |d₂|) when d₁d₂ ≥ 0 and |d₁| + |d₂| otherwise.

Free, bond and bond distance refer to the projections of N onto finite sets (the canonical K1–K3 test with every other site
quantified away): a bond is a finite set of at least three sites, not free, whose co-1 subsets are free.

## Lemmas

**Lemma 1 (heights).** For σ ∈ N there is h: Z² → Z with h(y) − h(x) ∈ {1, −2} on every forward edge x → y, the step being 1 exactly
when σ(x) ≠ σ(y); then σ(x) ≡ h(x) + σ(0) − h(0) mod 2. Conversely every such h gives the state σ = h mod 2 in N.

*Proof.* Around a directed triangle the steps are 1, 1, −2 in some order, since exactly one edge of a non-monochromatic triangle joins
equal spins; they sum to 0. Triangles generate the cycles of the plane, so the steps integrate to h. Across a step of 1 the spin
changes and across −2 it does not, so σ ≡ h + const mod 2; choosing the free additive constant with h(0) ≡ σ(0) mod 2 makes σ = h mod 2, and adding 6 keeps that. Conversely, three steps from {1, −2} summing to 0 around a triangle are
1, 1, −2 in some order, so every triangle has exactly one equal pair. ∎

**Lemma 2 (the bound D).** Let D(x, y) be the least number of forward steps from x to y. Then D(x, y) = d₁ + d₂ + 3 max(0, −d₁, −d₂)
for d = y − x; D(x, y) ≡ c(y) − c(x) mod 3; D(x, y) + D(y, x) = 3δ(x, y); and δ(x, y) ≤ D(x, y). Every h of Lemma 1 has
h(y) − h(x) ≤ D(x, y).

*Proof.* With α, β, γ steps of (1,0), (0,1), (−1,−1): α − γ = d₁, β − γ = d₂, and α + β + γ = d₁ + d₂ + 3γ is least at
γ = max(0, −d₁, −d₂). Each forward step adds 1 to c mod 3. Summing the two formulas gives 3[max(0, −d₁, −d₂) + max(0, d₁, d₂)], which
is 3δ in each sign case. Each of D(x, y), D(y, x) is at most 2δ (two forward steps replace a backward one), so each is at least δ.
Along a forward walk h rises by at most 1 per step. ∎

**Lemma 3 (extension).** Let S ⊆ Z² (finite or not) and g: S → Z with g(x) ≡ c(x) + k mod 3 for a fixed k and g(y) − g(x) ≤ D(x, y)
for all x, y ∈ S, and suppose inf over x ∈ S of g(x) + D(x, z) is finite for every z. Then g extends to an h of Lemma 1.

*Proof.* Put h(z) = min over x ∈ S of g(x) + D(x, z) (a minimum of integers bounded below). On S it equals g, by the pairwise condition
and D(z, z) = 0. D obeys the triangle inequality, so h(z′) − h(z) ≤ D(z, z′) for all z, z′. Every candidate is ≡ k + c(z) mod 3, so h
is. On a forward edge z → z′ this gives h(z′) − h(z) ≤ 1, h(z) − h(z′) ≤ D(z′, z) = 2, and h(z′) − h(z) ≡ 1 mod 3, so the step is
1 or −2. ∎

**Lemma 4 (the criterion).** For a finite set S and a pattern p: S → {0, 1}, let r(x) ∈ {0, …, 5} be the residue with r(x) ≡ c(x)
mod 3 and r(x) ≡ p(x) mod 2, and on the complete digraph on S put
w(x, y) = ⌊(D(x, y) − r(y) + r(x)) / 6⌋. Then p extends to a state of N if and only if this digraph has no negative cycle.

*Proof.* With h normalized so that σ = h mod 2 (Lemma 1), adding 2 to h keeps σ and shifts h mod 3 by 2, so we may take k = 0: p extends exactly when there are integers m(x) with
g = r + 6m satisfying Lemma 3's pairwise condition (necessity by Lemma 2, sufficiency by Lemma 3; S is finite, so the infimum is
finite). The pairwise condition reads m(y) − m(x) ≤ w(x, y), a system of difference constraints, solvable in integers exactly when
there is no negative cycle. ∎

The numerator N(x, y) = D(x, y) − r(y) + r(x) is ≡ 0 mod 3 (Lemma 2 and r ≡ c), so N = 6w + e with **e ∈ {0, 3}**.

**Lemma 5 (counting).** If a pattern on S has a negative cycle, it has one on distinct sites x₁, …, x_k with
3k ≥ Σᵢ D(xᵢ, xᵢ₊₁) + 6 ≥ 3 diam_δ{x₁, …, x_k} + 6.

*Proof.* A negative closed walk contains a negative simple cycle. Around it Σ (r(xᵢ₊₁) − r(xᵢ)) = 0, so Σ w = (Σ D − Σ e)/6 ≤ −1, and
Σ e ≤ 3k. Splitting the cycle at the two sites a, b of largest distance and using the triangle inequality, Σ D ≥ D(a, b) + D(b, a)
= 3δ(a, b) (Lemma 2). ∎

**Lemma 6 (bonds are spread).** If S is a bond, then |S| ≥ diam_δ(S) + 2.

*Proof.* Some pattern p on S does not extend, so by Lemma 4 it has a negative cycle. If one missed a site s, the same weights make
p restricted to S ∖ {s} non-extendable, and S ∖ {s} would not be free. So every negative simple cycle of p passes through all of S,
and Lemma 5 gives 3|S| ≥ 3 diam(S) + 6. ∎

## Theorems

**R1.** Every pair of sites is free, and the non-free triples are exactly the triangles.

*Proof.* A negative cycle on two sites would need 6 ≥ 3δ + 6 (Lemma 5), impossible for distinct sites. A non-free triple has a
negative cycle, not on two of its sites, so on all three: 9 ≥ 3 diam + 6, so its sites are pairwise adjacent, and in Λ every three
pairwise adjacent sites form a triangle. A triangle is not free (its monochromatic patterns do not occur). ∎

So in the plane the three-place bonds are exactly the knots, with no tie and nothing frozen: Λ is read faithfully.

**R2.** For sites u ≠ v, β(u, v) = δ(u, v) + 1.

*Lower bound.* A bond containing u and v has at least diam + 2 ≥ δ(u, v) + 2 sites (Lemma 6).

*Upper bound.* Let d = δ(u, v). The twelve automorphisms of Λ fixing a site preserve N and so map bonds to bonds, and they carry
every displacement of length d to one of the form (d, j), 0 ≤ j ≤ d. So take u = (0, 0), v = (d, j), and let

S = {(0, y) : j − d ≤ y ≤ j} ∪ {v},

the side of the triangle with corners a = (0, j − d), b = (0, j), v, together with the opposite corner v: d + 2 sites, u among them.

- *S is not free.* Give the side the value 0 and v the value d + 1 mod 2, and take the cycle a → (0, j − d + 1) → … → b → v → a. Its
  D values are 1 on each of the d side steps, D(b, v) = D((0,0), (d,0)) = d and D(v, a) = D((0,0), (−d, −d)) = d, so Σ D = 3d. On a
  side step the spins agree and c rises by 1, so r rises by 4 mod 6 and N = 1 − 4 ≡ 3 mod 6; on b → v and v → a, N ≡ d − (d + 1)
  and N ≡ d + (d + 1) mod 2 respectively, both odd multiples of 3. So every e = 3, Σ w = (3d − 3(d + 2))/6 = −1, and the pattern does
  not extend.
- *Every co-1 subset is free.* Every column site (0, y) is at distance d from v, since v − (0, y) = (d, j − y) with 0 ≤ j − y ≤ d,
  and column sites are at distance |y − y′| from each other. Let T ⊊ S. A negative cycle on sites T′ ⊆ T would need
  |T′| ≥ diam(T′) + 2 (Lemma 5). If v ∉ T′, T′ is a set of column sites at distinct integer positions, so diam(T′) ≥ |T′| − 1. If
  v ∈ T′ and |T′| ≥ 2, diam(T′) ≥ d ≥ |T′| − 1, since |T′| ≤ |T| = d + 1. Either way no negative cycle exists, and T is free.

So S is a bond of d + 2 sites containing u and v. ∎

**R3.** Let σ₀(x) = 1 when c(x) = 1 and 0 otherwise (the flat three-class state; each triangle reads 0, 1, 0). Every site b is flipped
by a change of σ₀ inside the disc of radius 4 around b, so every bond is native at σ₀.

*Proof.* σ₀ has height h₀ = c ∈ {0, 1, 2}: steps from class 0 to 1 and 1 to 2 join different spins (+1), from 2 to 0 equal spins (−2).
Let O be the sites at distance at least 5 from b, and set g = h₀ on O and g(b) = h₀(b) + 3. Pairs within O satisfy the pairwise
condition (Lemma 2). For x ∈ O, g(b) − g(x) ≤ 2 + 3 = 5 ≤ δ(x, b) ≤ D(x, b), and g(x) − g(b) < 0 ≤ D(b, x). The congruence holds, and
g(x) + D(x, z) ≥ 0, so Lemma 3 extends g to a height function that agrees with h₀ outside the disc and changes the parity at b. Its
state agrees with σ₀ outside the disc and flips b. ∎

## Scope and nonclaims

- The theorems are about the infinite triangular lattice. On flat tori and Klein bottles a state lifts to a periodic state of Λ, so a
  set whose lift is not free in Λ is not free in the quotient when the covering is injective on its sites; freeness of co-1 subsets
  and the lower bound do not transfer. There the result stays computed (`LONG-LOOP-20261111-001`): faithfulness on tori and Klein
  bottles of edge-width at least 5, and the equality to distance 3 on tori of edge-width at least 6, with shortcuts on tori of
  edge-width 4 and 5; the equality was not computed on Klein bottles.
- Bond distance here is a counted size (A40), not a drawn length.

## Checks

`check.py` (result in `result.json`): C1 the criterion against SAT on a disc of radius 8 for 71,002 patterns; C2 the side-and-apex
bonds for every distance 1 to 8 and direction (44 cases; SAT for d ≤ 4); C3 no smaller bond in a box to distance 4; C4 R1 in a box; C5
R3 by SAT for a site of each class; C6 the criterion with D replaced by graph distance disagrees with SAT (3,900 patterns), so C1 can
fail. A disc's SAT verdict is the plane's because every state of a hex disc extends to the plane (shortest forward walks between two
sites of a hex disc stay in it, so a disc state meets Lemma 3's pairwise condition); C3 uses the criterion, on sites within distance
d of both u and v.

## Review

An independent referee, a fresh agent, checked every lemma and theorem with its own oracles (SAT on a disc of radius 11 for
non-extension, SAT on the 24 × 24 torus for extension, neither using D) and found the statement fully proved: the criterion matched on
55,756 random patterns; the side-and-apex sets are bonds in all 6d directions for d ≤ 6; no smaller bond in boxes to d = 4 (398,504
sets at d = 4); R3's flip needs radius 0 or 1, not 4. It asked for the normalization in Lemma 1 (made), a sentence on why disc SAT
speaks for the plane (added), and a narrower scope note: the flat-world equality was computed on tori only (corrected; logged).
