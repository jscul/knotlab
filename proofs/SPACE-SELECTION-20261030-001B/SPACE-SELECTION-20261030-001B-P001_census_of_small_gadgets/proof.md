# Census of small gadgets for the harmony

Status: Proved

Ticket `SPACE-SELECTION-20261030-001B`, 2026-10-30.

**What it uses:**
- `SPACE-SELECTION-20261030-001A`: the gadgets, the pencils, the criterion, the mechanisms, and its library (`gadget_lib.py`).
- `SIMPLEX-GASKETS-20261029-001A`: its elimination engine, copied here as `gasket_engine.py`. It is the second, independent contraction code.

## Standard statement

**Setting.**
- Gadgets, linear gadgets and exactness are as in ticket A.
- The standing wave is w_q = K + qM: q = 0 is the knot (signed not-all-equal), and q = 1 + 2cos 2θ.
- The *mechanism* of a generic gadget:
  - *locked*: every mixed sector assignment has a vanishing factor;
  - *balanced*: survivors cancel within classes of equal factors;
  - *algebraic*: otherwise.
- The *growth rate* ρ of a gadget's tower is the growth rate of the shortest corner chains (numbers of triangles).
  - With d_k the chain lengths of level k, d_(k+1) = F(d_k), where F takes, for each corner pair, the minimum over corner paths of the
    traversal counts times d_k.
  - ρ is the least spectral radius over choices of one minimal path per corner pair. It is certified by a positive vector x with
    F(x) = ρx.
  - The *growth exponent* is log n / log ρ, a combinatorial quantity of the gluing.

**Result 1 (the census).** All gadgets with at most five triangles, up to isomorphism.

| n | gadgets | linear | generic-exact (locked / balanced) | exact at the knot | knot only (locked at π/3) | generic, λ(0) = 0 |
| --- | ---: | ---: | --- | ---: | --- | ---: |
| 1 | 1 | 1 | 1 (1 / 0) | 1 | 0 | 0 |
| 2 | 0 | 0 | — | — | — | — |
| 3 | 30 | 8 | 14 (14 / 0) | 14 | 0 | 0 |
| 4 | 1,293 | 48 | 172 (92 / 80) | 206 | 34 (0) | 0 |
| 5 | 73,326 | 2,520 | 5,694 (3,078 / 2,616) | 8,584 | 3,082 (584) | 192 |

- **Mechanisms.** No generic gadget with at most five triangles needs algebraic cancellation.
- **Linear gadgets.** Generic-exact: 6, 4 and 520 at n = 3, 4, 5. 520 = 440 locked + 80 balanced.
- **The knot on linear gadgets.** It is exact on exactly the same linear gadgets: no knot-only gadget and no lost gadget.
- **Three triangles.**
  - All 14 exact gadgets have λ = q² − 1 (so λ(0) = −1) and growth rate 2.
  - The Sierpinski gadget is one of the 6 linear ones: a triangle cycle whose corner triangles are locked to T_A.

**Result 2 (special parameters).** For a non-generic gadget the exact parameters are roots of a polynomial. The counts below are gadgets exact
at that value only.

| value | angle | n = 3 | n = 4 | n = 5 |
| --- | --- | ---: | ---: | ---: |
| q = 0 | π/3, the knot | 0 | 34 | 3,082 |
| q = 1 | π/4 | 6 | 116 | 5,064 |
| q = 2 | π/6 | 0 | 17 | 1,524 |
| q = 1 ± √2 | π/8, 3π/8 | 0 | 0 | 244 |
| q = 1/3 | cos 2θ = −1/3 (not a rational angle) | 0 | 0 | 680 |
| q = 3/2, q = 1/2 | cos 2θ = 1/4, −1/4 | 0 | 0 | 280, 80 |
| q = −1, q = 3 | degenerate (θ = π/2, θ → 0) | 10, 2 | 236, 80 | 7,348, 3,800 |
| complex | e.g. q² − q + 2, q² + 3, q² + 1 | 0 | 44, 34, 0 | 2,000, 1,464, 1,072 |

- **The three crystallographic angles at n = 5.** The standing wave is exact on 8,584 gadgets at the knot angle π/3, 7,170 at π/6 and 6,846
  at π/4.
- **Where the extras come from.** The extra gadgets at π/4 come partly from locking at π/4 (2,192 of 5,064): even-base two-triangle
  contacts vanish when their sectors agree. At the knot, 584 of the 3,082 extras come from locking at π/3, where three in-phase triangles
  at an odd-base contact vanish.
- **The knot leads among real angles at n = 5.** Among the non-degenerate real angles the knot angle is exact on the most gadgets. The
  degenerate limit q = 3 is exact on more (9,494).

**Result 3 (cosine and plain pencils).**
- At n = 3 and 5 the cosine wave is generic-exact on exactly the standing wave's generic gadgets (14 and 5,694).
- At n = 4 the cosine wave is exact on none (Theorem 1 of ticket A).
- The cosine knot (−1)^a·NAE is exact on 14, 0 and 8,514 gadgets at n = 3, 4, 5.
- Plain not-all-equal is exact on no gadget with 2 ≤ n ≤ 5. The one-triangle gadget is exact for every law.

**Result 4 (growth).**
- Every exact gadget's growth rate is certified (8,996 gadgets).
- The rates are algebraic integers between 2 and n − 1.

| ρ | minimal polynomial | n = 4 (generic / knot only) | n = 5 (generic / knot only) | exponent at n = 5 |
| --- | --- | --- | --- | ---: |
| 2 | x − 2 | 144 / 28 | 4,416 / 2,346 | 2.32 |
| 1 + √2 | x² − 2x − 1 | 4 / 0 | 230 / 44 | 1.83 |
| φ² = (3 + √5)/2 | x² − 3x + 1 | 0 / 0 | 116 / 24 | 1.67 |
| (1 + √13)/2 | x² − x − 3 | 16 / 0 | 92 / 0 | 1.93 |
| 1 + 2cos(2π/7) | x³ − 2x² − x + 1 | 4 / 0 | 48 / 0 | 1.99 |
| 3 | x − 3 | 4 / 6 | 528 / 604 | 1.46 |
| 4 | x − 4 | — | 4 / 8 | 1.16 |

- Twenty further cubic and quadratic rates occur at n = 5; `census.json` has all of them.
- The exponents at n = 5 run from log 5 / log 4 ≈ 1.16 to log 5 / log 2 ≈ 2.32.

**Result 5 (beyond five triangles, exact examples).** The regularities of Results 1 and 3 do not persist:
- a linear 6-triangle gadget exact at the knot only (λ = (q − 1)(q + 1)²(2q² − 3q − 1));
- a linear 6-triangle generic gadget whose factor vanishes at the knot (λ = q(q + 1)²(q² − 2q + 5));
- a linear 7-triangle gadget generic for the standing wave but not for the cosine wave;
- a 5-triangle gadget exact at q = 1/3 with λ = 64/81.

## Nearest known result

- **In the repository.** Ticket A gives the criterion and mechanisms. `SIGNED-GASKETS-20261029-001` and `SIMPLEX-GASKETS-20261029-001` fix
  the Sierpinski gluing.
- **Outside.**
  - Censuses of fixed points of decimation on families of finitely ramified gluings exist for resistance forms (harmonic structures), not
    for signed three-bit laws.
  - Growth rates of min-plus recursions with independent row choices are spectral radii of a best stationary policy (Rothblum–Whittle 1982;
    Blondel–Nesterov 2009). Here each rate is certified directly.
- **Classification.** No overlap found (candidate local delta).

## Proof

- **Enumeration.**
  - Gadgets are generated as set partitions of the non-corner slots into blocks of at least two slots from distinct triangles. Triangle 0
    holds A, and the placements of B and C are reduced by symmetry.
  - Keys are canonical under every relabeling of the other triangles. This is a complete invariant: a gadget is determined by its corner
    placements and blocks.
  - An independent enumerator gives the same isomorphism classes for n ≤ 4. It uses all corner placements, restricted-growth labelings and a
    canonical form over all triangle permutations.
  - For n = 5, 3,000 random labelled gadgets all land in the census.
- **Exact corner relations.**
  - For every gadget and each of the three pencils, the corner relation is computed at nine integer parameter values by two independent
    codes: direct summation over the inner spins, and the gasket engine's elimination. That is 223,950 gadget–pencil pairs, all agreeing.
  - Each entry is interpolated exactly. Its degree is at most n, checked at the remaining points.
- **Classification.**
  - Generic exactness is the identical vanishing of the proportionality defects, with λ ≢ 0.
  - Special values are the irreducible factors of the defects' gcd that do not divide λ.
  - Mechanisms follow ticket A's definitions.
  - Angle locking at π/k uses ticket A, Theorem 3(a).
- **Growth.**
  - For every exact gadget, take the policy of least spectral radius and its eigenvector x. The check confirms x > 0 and F(x) = ρx.
  - Monotonicity of F then gives c·ρ^k x ≤ d_k for some c > 0, and the policy itself gives d_k ≤ C·k²·ρ^k.
  - So the growth rate is ρ. The minimal polynomial is the irreducible factor of the policy's characteristic polynomial vanishing at ρ.
- **Result 5.** Exact relation polynomials for the four examples. ∎

## What the computation checks

`check.py` (about three minutes) writes `census.json` with every table:
- **Enumeration and its replay.** The census counts, the independent enumerator and the random completeness probe.
- **Two codes.** The two contraction codes agree on every gadget and pencil.
- **The tables.** The standing-wave table, the special factors, angle locking, the cosine and plain pencils, and the certified growth rates.
- **Result 5.** The examples beyond five triangles.
- **Controls:**
  - a perturbed pencil is not generic-exact on the Sierpinski gadget;
  - flipping one sign of the law changes the n = 3 count;
  - the growth certificate rejects every non-optimal policy.

## Reading

- **The harmony builds many spaces.** Generic-exact gadgets number 14, 172 and 5,694 at three, four and five triangles. The knot builds more
  than the harmony: 8,584 at five triangles, a third of them its own.
- **Phase locking and mirror cancellation are the whole story up to five triangles.** Algebraic cancellations appear only later.
- **The knot leads at five triangles, but no angle is selected.**
  - Among real angles the knot builds the most spaces at five triangles.
  - Special angles proliferate: the quarter and sixth waves, π/8, and angles with cos 2θ = −1/3, ±1/4 that are not rational multiples
    of π.
  - The knot is not singled out by the gluings it admits.
- **No growth exponent is selected.** Exact towers grow with many algebraic rates. Exponents range over [1.16, 2.32] at five triangles and,
  by ticket A's tadpoles, without bound.

## Nonclaims

- **Size.** The census stops at five triangles. Rates or patterns at six or more triangles are not claimed, beyond the exact examples of
  Result 5.
- **Growth.** Growth rates and exponents are counts of triangles in corner chains of the substitution tower, not a metric or a dimension.
- **Mechanisms.** "Locked" and "balanced" are sufficient mechanisms by definition (ticket A). The census shows they exhaust n ≤ 5, not that
  they exhaust any larger size.
