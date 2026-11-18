[claude-code:unrecognized_model] {"model":"claude-fable-5-2","query_source":"sdk"}
I ran independent checks on all three arms. W2 and the C closed form hold; W3 is ill-posed as worded; G1 is likely false and G2 fragile. Scripts are in `/tmp/adv_b195/` (`w_row.py`, `c_arm.py`, `g_census.py`).

## W (weave)

**New exact gate.** Along a row the dimer determinant collapses to a Toeplitz determinant with a sine kernel (my derivation from the honeycomb kernel):

C(r) = (−1)^r det[δ_jk − 2g(j−k)], with g(0) = 1/3 and g(n) = (−1)^n sin(nπ/3)/(πn).

It gives −1/3 at r = 1, −0.192852 at r = 2 and 0.358520 at r = 3, matching your values, and runs to r = 482 in seconds.

**Amplitude.** a = 2·3^(−1/4)·E0² = 0.6322260813, with E0 = 2^(1/12) e^(3ζ′(−1)) = 0.645002448. This agrees with Stephenson's ε0 = √2 (E0^T)² = 0.632226080 (J. Math. Phys. 11, 413 (1970), from memory; check the reference).

**Form and corrections.** C ~ a r^(−1/2) cos(Q·r) is correct. There is no log (free-fermion point, no marginal operator) and no competing r^(−2) term; the next harmonic is uniform at r^(−9/2). Measured along the row:

| Class | √r·C relative to leading term | At r ≈ 60 |
|---|---|---|
| Same class (r = 3k) | 1 − 3/(16r²) | −5.2e-5 |
| Cross class, r ≡ 1 mod 3 | 1 + 1/(4r) | +0.40% |
| Cross class, r ≡ 2 mod 3 | 1 − 1/(4r) | −0.41% |

- **W1:** correct but far too loose. Along the row the deviation is 5e-5 at r = 60, so "moving toward 1" is unresolvable unless your quadrature is good to about 1e-6. Tighten to 1e-3 and drop the trend clause. I did not compute off-row rays; isotropy of a rests on the height-field argument (three-fold symmetry forces an isotropic stiffness).
- **W2:** correct. The slope is −0.49958 at r = 30 and −0.49990 at r = 60, using same-class centred differences. Specify same-class only.
- **W3:** "at equal r" is impossible. Same-class sites have r² ≡ 0 mod 3 and cross-class r² ≡ 1 mod 3, so they never share a separation. Restate as √r·C_cross → −a/2. It passes 2% at r ≈ 60 but converges only as 1/r, with the alternating sign above. The symmetry argument suggests this term carries a cos 3θ factor off-row (conjecture, unchecked), so freeze the 1/(4r) pattern for the row only.
- **Consequence:** correct. The own-class ball holds about (2πa⁴/(3√3))·g^(−4) ≈ 0.193 g^(−4) distinctions, with g = 1 − 2ρ/N. The 1/4 radius for other classes is right, so they hold 1/8 as many. In tau the ball grows like 3^(4τ), exponentially, so tau gives no growth exponent here.

## C (chain grid)

- **Closed form:** right in every direction. The zero set of Onsager's cosh²2K − sinh 2K (cos k1 + cos k2) at imaginary k is your curve, and its support function is the decay rate.
- **Numbers:** all reproduced: 0.369070, 0.523719, anisotropy 1.003400 / 1.068608 / 1.141877, and Golab pi 3.141701 / 3.182439 / 3.297933 / 3.418832 / 3.589389. Your Golab definition is sensible.
- **Citations (from memory, check volumes):**
  - Cheng and Wu, Phys. Rev. 164, 719 (1967), for general-direction asymptotics.
  - McCoy and Wu's book.
  - Rottman and Wortis (1981); Avron, van Beijeren, Schulman and Zia, J. Phys. A 15, L81 (1982); Zia and Avron (1982), for the dual Wulff shape.
  - Campanino, Ioffe and Velenik (2003), for OZ with analytic strictly convex rate.
- **C1 is marginal at l = 1.** The on-axis estimator's relative residual is about −0.1/(mr)²: −1.4e-3 at r = 20, −6.5e-4 at r = 30, −3.8e-4 at r = 40. Use r ≥ 40 or a 3e-3 tolerance. I checked the axis only. At l = 3, r = 30 the correlations are near 1e-42; confirm your formulas stay multiplicatively stable there.
- **Sign:** the gauge is right for grid nodes, but two things need fixing.
  - A 3×3 torus has odd cycles, so C2 tests the reduction on a frustrated system and not the two-class split. Add an open 3×3 patch (21 bits) for that.
  - A knot is symmetric in its three members, so loose ends and chain interiors are ordinary distinctions at one knot-step. The subdivided structure is bipartite for every l, so two classes always exist once those are counted. State which distinctions the ball counts.

## G (growth against orders)

I took a census of all partial cubes up to 10 vertices (1068, of which 857 are median), with states being both sides of every split. Your admitted-extension census may be a subset, so check that each collision member is reachable.

| Reading | Fails on k | Fails on lambda |
|---|---|---|
| (a), (b) | Not through n = 9; at n = 10 only with a non-median member; never on median through 10 | First at n = 9 |
| (c) | Median: first at n = 10. All partial cubes: n = 7 | First at n = 6 |

- **G1:** expect it to be false. Below n = 10 reading (a) is nearly a complete invariant (one non-singleton class), so "determines k" is close to vacuous. Reading (b) adds nothing.
- **G2:** true through n = 9 only if your census is median-only.
- **Hand-checkable (c) collision, n = 6:** the star with five leaves (lambda 3) and the double star 0–1 with leaves 4, 5 on 0 and 2, 3 on 1 (lambda 2). Every state's row is [2,2,2,2,4,4,4,4,6] in both.
- **(a) collision on lambda, n = 9, both median, k = 2:**
  - lambda 3: {01, 05, 06, 12, 13, 14, 27, 28, 37, 48}
  - lambda 2: {01, 05, 07, 12, 13, 14, 26, 28, 37, 48}
- **(c) collision on k, n = 7:**
  - k = 3, not median: {01, 04, 12, 13, 26, 45, 56}
  - k = 2, median: {01, 04, 06, 12, 13, 26, 45, 56}

I would freeze: (a) determines k through n = 9 and fails lambda at n = 9; (c) fails lambda at n = 6.

## Your three side questions

**(i) State side on large-entropy bases.** I expect it to read only local freedom, not orders (reasoning, not computed). On parity bases the profile is the code's weight distribution, identical from every state. On weave tori the number of states within r grows like (number of flippable distinctions)^r / r!, which scales with the base's size. It is informative only on split bases, where states are few and nest into chains.

**(ii) Most valuable change.** Add a second reading of the same weave with a different exponent: the derived distinctions "two adjacent distinctions agree". Their correlations decay as r^(−2) and come from 2×2 determinants of your existing kernel. The law then predicts growth exponent 1 instead of 4 on the same base, which makes "the count reads 2/eta" falsifiable. Those distinctions are biased (mean 1/3), so use the raw count against its 4N/9 baseline, not tau. The cut: C1 at l = 2, 3 out to r ≈ 30, which tests nothing the closed form does not already settle.

**(iii) Words.** "Outline" is fine. "Round" is a shape word; I would replace it with a defined quantity such as "even: largest-to-smallest reach ratio tends to 1". By the same rule your drafts also use radius, polygonal, diamond, cross-polytope, box, grid, row, diagonal, hexagon, direction, degrees, and arguably "ball" and "dimension".
DONE
