<!-- modelUsage: claude-fable-5-2 -->

I checked everything below by hand, not by running code. Citations are from memory, so verify them before freezing.

## Verdict

- **W1–W3** hold as worded, but the tolerances are too loose to test anything, and the cross-class ratio has a correction of relative order 1/r that the draft omits.
- **C**: the closed form is right in every direction and your numbers reproduce. C1 is borderline at l = 1.
- **G**: I expect both drafts to be wrong. Reading (c) fails at n = 4 for k and at n = 5 for λ, by an explicit collision. Reading (a) probably determines both at n ≤ 8.

## Arm W

**Leading form and amplitude.** C(r) ≈ a r^(-1/2) cos(Q·r) with isotropic a is correct. There are no logarithms: the dimer model is free-fermion, so there is no marginal operator.

Along a row the correlation is exactly an x-by-x Toeplitz determinant with symbol +1 on |θ| < π/3 and −1 elsewhere:

- Entries: φ₀ = −1/3, φ_k = 2 sin(πk/3)/(πk).
- Values: D₁ = −1/3, D₂ = 1/9 − 3/π² = −0.192853, D₃ = 0.358520, D₄ = −0.165613, D₅ = −0.133617.
- D₂ and D₃ match your −0.1929 and 0.3585, so this is a free independent gate out to any separation.

Fisher–Hartwig with two jumps (β = ±1/2, chord √3) then gives the amplitude:

- a = 2 · 3^(-1/4) · E₀² = **0.6322260804**, where E₀ = 2^(1/12) e^(3ζ′(−1)) = 0.6450024485.
- This equals Stephenson's ε₀ = √2 (E₀ᵀ)² (J. Math. Phys. 11, 413, 1970). Your glimpses 0.630, 0.621, 0.638 are consistent with it.

**Corrections you asked about.**

- **Cross-class, relative order 1/r.** The row expansion has the form cos(Qn) → cos(Qn) ∓ sin(Qn)/(4√3 n), from the known 1/n term 2iβ³ cot(k_F)/n of the two-jump expansion. So the cross-class amplitude is −(a/2) r^(-1/2) [1 ± 1/(4r)], with + for n ≡ 1 and − for n ≡ 2 (mod 3). My D₄ and D₅ give ratios 1.0478 and 0.9452 to the leading term, which fits ±1/(4n) plus a term of order −0.15/n².
- **Its angular form.** By symmetry (my inference, not checked off the row) the factor is cos 3θ: the term vanishes for same-class pairs and has opposite signs for the two other classes.
- **Same-class, relative order r⁻².** This comes with a cos 6θ part. Your three glimpses suggest A(30°)/A(row) − 1 ≈ +0.3/r², but that is a rough fit.
- **Uniform term.** A non-oscillating r^(-9/2) term also exists; it is negligible here.

**Consequences for the predictions.**

- **W1**: true, but at r ≈ 60 the same-class anisotropy is about 1e-4, so "within 1%" cannot fail. Freeze the form instead: deviation ∝ r⁻², with the ordering row < (4,1) < (5,2) < 30°.
- **W2**: fine if you use same-class points only.
- **W3**: passes (±0.4% at r = 60 along the row), but convergence is 1/r, not faster. A sharper version: the mean of the two cross-class amplitudes over same-class tends to −1/2 as r⁻², and their relative difference is cos 3θ/(2r).
- **Outlines**: the own-class set has about 0.1932 (1 − 2ρ/N)^(-4) members. The other classes' outlines sit at 1/4 the radius but carry a fixed three-lobed offset of ±½ cos 3θ spacings, so they are round only in the limit.
- **Gate to add**: confirm that same-class C > 0 and cross-class C < 0 at every separation, not only along the rays.

## Arm C

**Closed form.** It is right in every direction. The boundary of Q is the zero set of the Kac–Ward/Onsager symbol (1+t²)² − 2t(1−t²)(cos k₁ + cos k₂) at imaginary momentum, which is the one-particle mass shell. I reproduced:

- A = 25/12 at l = 1;
- axis rate ln(3/2) and diagonal rate 2 ln(4/3) per diagonal step;
- anisotropies 1.00340, 1.0686, 1.1419;
- Golab π at l = 1: a perturbative check gives π(1 + 11.5ε²) ≈ 3.14170. The definition (half the self-perimeter) is sensible.

**Citations.** Add Cheng and Wu (Phys. Rev. 164, 719, 1967) for the general-direction asymptotics, and Holzer 1990 / Akutsu and Akutsu 1990 for "Wulff shape = Kac–Ward zero locus". Yours are appropriate.

**Sign and classes.** Two corrections:

- The spine (grid points plus chain interiors) is bipartite for every l, not only odd l. Grid points alone split in two only for odd l.
- Loose ends do not join a fixed class. Exactly, C(0, c) = −[C(0, a) + C(0, b)]/2 for a loose end c on a knot with spine members a and b. Its sign depends on which neighbour is nearer the start, and its magnitude is reduced (a factor of about 1/6 along an axis at l = 1). Use this identity as a gate.

**C1.** The successive-ratio estimator has error c₁/r² with c₁ ≈ −1/(8m). At l = 1 and r ≈ 30 that is about 8.5e-4 relative, right at your 1e-3 line. Use a three-point estimator or go to r ≈ 60. At l = 2, 3 the correlations are about 1e-26 and 1e-42, so make sure the "1e-15 agreement" is relative, not absolute.

**C2.** The 3x3 wrap is frustrated, so compare against t = −1/3 directly, not a gauged +1/3.

## Arm G

**A structural fact.** If census bases are exactly the solution sets of their betweenness knots, then b is between a and c iff count(a,c) = count(a,b) + count(b,c). So the count matrix, up to relabeling, determines the base, and hence k, λ and N. Reading (a) loses information only through row sorting.

**Reading (c) is blind to a symmetry.** XOR-ing every state with one allowed state preserves all Hamming distances but moves the all-equal state, and can change the crossing graph. Coordinates below are (o, a, b, c):

| Base | Knots | States (plus complements) | k | λ |
|---|---|---|---|---|
| Star | (a,o,b), (a,o,c), (b,o,c) | 0000, 0100, 0010, 0001 | 1 | 2 |
| Translate | (o,b,a), (o,c,a), (b,o,c) | 0000, 0100, 0110, 0101 | 2 | 2 |

- Both have N = 8 and the same state-side profile: two rows (1,1,1,3,3,3,4) and six rows (1,2,2,2,2,3,4).
- In the translate, ob|ac crosses oc|ab.
- Reading (a) separates them: the star has rows (2,2,2) and three of (2,4,4); the translate has (2,2,6), (4,4,6) and two of (2,4,4).

With four leaves (n = 5) the same construction gives k = 1, λ = 2 against k = 3, λ = 3:

- The translate has knots (o,b,a), (o,c,a), (o,d,a), (b,o,c), (b,o,d), (c,o,d).
- It is buildable with at most three knots per step.

So G2 fails if these classes are admitted; I could not check your admission rule.

**Reading (a).** I found no collision among the n = 4 systems I enumerated. For bases whose distinctions fill their median graph, k is forced by n and the number of nearest pairs up to n ≈ 9. I expect (a) to determine k at n ≤ 8 (about 75%) and λ slightly less surely.

**Fix.** Root the state-side reading at the all-equal state, which is name-free. Split sizes plus Hamming distances then give all quadrant sizes, hence the crossing graph.

## Your three extra questions

**(i) State-side on large-entropy bases.** It reads only local flips.

- On weave wraps the count within r is roughly binom(F, r), with F the number of free flips. F varies by state and is zero for striped states.
- On parity bases every state has the same profile, namely the weight enumerator.
- On a full box the state side is 2d strands joining the two all-equal states, so growth is linear and d appears as half the number of nearest states to the all-equal state.

**(ii) Most valuable change.** Add an outline exponent to W. Define the outline as ball members with a nearest-count partner outside. Then ball ~ u^(-d/η) and outline ~ u^(-(d−1)/η) with u = 1 − 2ρ/N, so the ratio of logs gives (d−1)/d and separates d from η. As drafted, W reads only d/η = 4. In τ the W ball grows like 81^τ while the C ball grows like τ², so the two arms are not yet comparable. The matching cut is G1/G2 as "determines at n ≤ 8": the census is too small to test that.

**(iii) Words.** "Outline" is fine. "Round" presupposes an embedding; state it as the Golab number, or "self-measured half-girth 3.14159". Your drafts also use "ball", "radius", "row", "direction", "30 degrees" and "hexagon" for the program's own objects, which are worse offenders than "outline".
