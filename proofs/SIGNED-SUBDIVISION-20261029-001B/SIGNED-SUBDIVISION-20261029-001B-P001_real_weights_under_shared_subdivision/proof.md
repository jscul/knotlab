# Real weights under shared subdivision

Status: Proved

Ticket `SIGNED-SUBDIVISION-20261029-001B`, 2026-10-29.

## Standard statement

The setting is that of `SIGNED-SUBDIVISION-20261029-001A`, with arbitrary nonzero real weights.
- **The rules.** On the triangular-lattice torus a three-bit law sits on every up triangle (S2, 34 knots) or on every triangle, with
  one placement for up and one for down triangles of the same class (S1, 88 pairs): 122 rule shapes.
- **Weights.** A weighting puts a nonzero real number on each allowed tuple, independently on up and down triangles. F(x) is the
  sum, over fine assignments restricting to the coarse assignment x, of the product of the weights. W(x) is the coarse weight.
- **Exact and support-exact.** A weighting is *exact* at a scale when F = c·W with c ≠ 0 on the stated coarse tori, and
  *support-exact* when F and W have the same support there. Support-exactness is exactness of the allowed states under the
  interference reading adopted on 2026-10-29.
- **Affine shapes.** These are the 22 shapes that are exact with counts at scale 2: parity on up triangles (2), parity on all
  triangles (2), twelve three-excluded pairs and six twisted not-all-equal pairs. Their solution sets are affine
  (`SHARED-SUBDIVISION-20261029-001B`).

**Results.**
- **Lemma 1 (gauge slice).** Every nonzero real weighting is gauge-equivalent to a sign class times positive magnitudes that equal
  1 on a maximal gauge-independent set of tuples. There are 944 sign classes, the gauge orbits of ticket A. The free magnitudes
  number 1 (parity), 1 or 2 (three-excluded), 2 or 3 (not-all-equal type, two excluded at distance two) and 4 (atoms).
- **Theorem 2 (positivity).** With positive weights, F and W have exactly the supports of the counted rule. So positive weights can
  be exact, or support-exact, only on the counted support-exact shapes. These are exactly the 22 affine shapes at scale 2 (coarse
  sides 2, 3, 4) and the six twisted pairs at scale 3 (sides 2, 3).
- **Theorem 3 (sign-parity obstruction).**
  - *Statement.* Let x be coarse-forbidden with at least one fine extension. Suppose every fine extension of x uses each tuple
    equally often modulo 2. Then F(x) ≠ 0 for every nonzero real weighting, so no weighting is exact or support-exact.
  - *Census.* At scale 2 this excludes 54 of the 100 shapes that are not affine: 52 on the coarse 2-torus and 2 more on the
    3-torus. At scale 3 it excludes 34 shapes on the coarse 2-torus.
  - *Refinement.* Asking only for one sign-coherent forbidden state in each sign class excludes nothing more at these sizes.
  - *Open.* What is left at scale 2 is the 46 densest shapes: the atoms (8 on up triangles, 20 pairs) and the two-excluded laws at
    distance two (12 on up triangles, 6 pairs). At scale 3, 82 shapes are left.
- **Theorem 4 (the affine shapes).**
  - *Scale 2, coarse sides 2 to 6.* The exact real weightings are exactly the gauge images of the exact ±1 classes of ticket A:
    the unsigned law for parity and the three-excluded pairs, and two classes for each twisted pair.
  - *Scale 3, coarse sides 2 to 4.* They are the gauge images of the six exact ±1 classes of each twisted pair. The other sixteen
    affine shapes have none.
  - *The census sizes are not enough for real weights.* On coarse sides 2 to 4 alone, each parity law on up triangles has one more
    exact class, at an irrational magnitude. For odd parity it is the weight −2^(1/9) on 111, the other weights being 1. For even
    parity it is −2^(−1/9) on the three tuples of weight two. The coarse 6-torus removes both.
  - *Smaller tori admit more.* On the coarse 2-torus alone, the twisted pairs are exact at the golden ratio at scale 3 (one
    magnitude φ or 1/φ) and at the reciprocal of the tribonacci constant at scale 2 (the real root of x³ + x² + x − 1). Both fail on
    the 3-torus. These occur in every sign class of every twisted pair (the check lists each point and the torus that removes
    it).
  - *Side effect.* The exact classes of ticket A stay exact on coarse sides 5 and 6 at scale 2 and on side 4 at scale 3.
- **Theorem 5 (symmetric slices).** Take the atoms that exclude 000 or 111, on up triangles or on all triangles with the same law,
  and give them weights constant on Hamming classes (two free ratios). None of them is exact on the coarse 2-torus at scale 2.
- **Corollary (the one-parameter cyclic families).** Weights constant on rotation orbits, with two orbits, are parity or
  not-all-equal. Not-all-equal is excluded for every weighting (Theorem 3). Parity is exact only on the gauge orbit of the uniform
  law (Theorem 4).

## Nearest known result

- **In the repository.**
  - `SHARED-SUBDIVISION-20261029-001A` and `B`: with counts, exactly the 22 affine shapes are exact at scale 2 and the six twisted
    pairs at scale 3. Their solution sets are Newman–Moore, Baxter–Wu and line-constant.
  - `SIGNED-SUBDIVISION-20261029-001A`: with weights ±1, no new shape becomes exact or support-exact.
- **Outside.**
  - That positive weights cannot change supports is elementary; it is the reason sign problems are needed for cancellation.
  - Gauge freedom of vertex models (edge gauges, holographic transformations) is standard.
  - Exact real-space renormalization in two dimensions is rare. Spurious fixed points on small lattices are a known hazard of
    finite renormalization schemes.
  - No classification of real-weighted three-bit laws under shared subdivision was found.
- **Classification.** Theorem 2 is elementary given the counted census. Theorem 3 is an elementary obstruction with a new census.
  Theorems 4 and 5 are exact computations. No overlap was found (candidate local delta).

## Lemma 1 (gauge slice)

- **Real gauge.** The edge gauges of ticket A extend to nonzero real functions h_H, h_D, h_V of two bits. Multiply each up weight by
  h_H(a,b) h_D(b,c) h_V(a,c) and each down weight by 1 / (h_H(e,f) h_D(d,e) h_V(d,f)). Each edge lies in one up and one down
  triangle, so F and W are unchanged. For S2, use g₁(a) g₂(b) g₃(c) with g₁g₂g₃ ≡ 1.
- **Scales.** Scaling the up law (or the down law) by λ multiplies F and W by powers of λ, so it preserves exactness.
- **The slice.** The positive part of the gauge acts on log |w| by adding vectors from the column space of an integer matrix G. Fix
  magnitudes to 1 on a set of tuples whose rows of G are independent and of full rank; then the equations G_F g = −log |w|_F can be
  solved. Sign gauges do not touch magnitudes, and positive gauges do not touch signs. So the classes of sign patterns modulo the
  sign gauge, times the slice, meet every gauge orbit. The check counts 944 sign classes and lists the free magnitudes.

## Theorem 2 (positivity)

- **Supports.** With positive weights every term of F(x) is positive. So F(x) > 0 exactly when x has a fine extension, and W(x) > 0
  exactly when x is coarse-allowed. The weighted rule is support-exact iff the counted rule is.
- **Census.** The check decides counted support-exactness exactly (residues modulo three primes) for all 122 shapes. At scale 2, on
  coarse sides 2, 3, 4, the support-exact shapes are the 22 affine shapes, the same set as the counted-exact ones. At scale 3, on
  sides 2 and 3, they are the six twisted pairs.
- **Control.** Random positive weights on twelve shapes give the counted supports on the coarse 2-torus.

## Theorem 3 (sign-parity obstruction)

- **Proof.** F(x) = Σ_e Π_t w(t)^(n_e(t)), where n_e(t) counts the fine triangles of the extension e that use tuple t. The sign of a
  term is Π_t sign(w(t))^(n_e(t) mod 2). If n_e mod 2 is the same for all e, all terms have one sign and nonzero size, so F(x) ≠ 0.
  But W(x) = 0, so F ≠ c·W and the supports differ. ∎
- **Test.** For every tuple t, the parity n_e(t) mod 2 is constant over e exactly when |F(x)| keeps the value of the count after the
  sign of t alone is flipped. The check runs this exactly for every shape at scale 2 (coarse sides 2, then 3) and at scale 3 (side
  2). Every witness found is of this kind. No allowed assignment without an extension occurs.
- **Refinement.** A weaker requirement suffices for one sign class: some forbidden x whose extensions all have the same sign under
  that class. The check tests it for every class of every shape not yet excluded. No shape has a coherent witness in every class
  at these sizes.

## Theorem 4 (the affine shapes)

- **Solution sets.** The candidates are the explicit families of `SHARED-SUBDIVISION-20261029-001B`:
  - Newman–Moore rows;
  - patterns constant on the three colour classes;
  - configurations constant along one of the three lattice directions.
  
  The candidates that satisfy the rule are all the solutions: their number equals trace(T^L), computed exactly, on every torus used
  (L = 2 to 6, 8, 9, 10, 12). So F and W are explicit polynomials in the free magnitudes, for each sign class.
- **Algebra.**
  - *Solved sides.* The exactness equations are F(x₀) W(y) − F(y) W(x₀) for coarse solutions y, and F(y) for forbidden y. For each
    sign class they are solved exactly on the smallest initial run of coarse sides whose system has finitely many solutions. One
    magnitude: the gcd and its real roots. Two magnitudes: a lexicographic Gröbner basis. Points with F(x₀) = 0 are discarded.
  - *Substituted sides.* Each point found is substituted exactly into the equations of the remaining sides (up to 6 at scale 2, up
    to 4 at scale 3). The test of vanishing uses the minimal polynomial of the value when it is irrational.
- **Result.**
  - Every exact point has all free magnitudes equal to 1, so it is a ±1 weighting.
  - The exact classes are those of ticket A: at scale 2, one per parity and three-excluded shape and two per twisted pair; at
    scale 3, six per twisted pair and none for the other shapes.
  - *Parity on up triangles.* Take the sign class whose four signs multiply to −1. The gcd on the coarse 3-torus has the factor
    m⁹ − 2 for odd parity (slice magnitude m on 111), or 2m³ − 1 for even parity (slice magnitude m on 110). Sides 2 and 4 have one
    coarse solution each and add nothing. So a second exact class survives sides 2 to 4. On the 6-torus it fails.

## Theorem 5 (symmetric slices)

- **System.** Weights 1, a, b on the three Hamming classes of the atom, with the same law on up and down triangles for S1. The
  equations are those of exactness on the coarse 2-torus at scale 2, from all 65,536 fine assignments.
- **Elimination.** Let G be the gcd of the equations. Every common zero with a, b ≠ 0 is a zero of G or of all the cofactors.
  - The check finds G a monomial in a, so it has no zero with a ≠ 0.
  - For the cofactors, the resultants with respect to b have a gcd whose only real root is a = 0.
  - So no nonzero a, b satisfy the system.

## Census

| Shapes | Scale 2 | Scale 3 |
|---|---|---|
| Affine (22): parity on up triangles (2), parity on all triangles (2), three-excluded pairs (12), twisted pairs (6) | Exact real weightings: the gauge images of the 28 exact ±1 classes (coarse sides 2–6) | The 36 exact ±1 classes of the twisted pairs (sides 2–4); none for the other 16 |
| Excluded for every real weighting by the sign-parity obstruction | 54 (52 on the coarse 2-torus, 2 on the 3-torus) | 34 (coarse 2-torus) |
| Open (no exact weighting proved impossible) | 46: atoms (8 on up triangles, 20 pairs), two excluded at distance two (12 on up triangles, 6 pairs) | 82, none of them affine |
| Symmetric slices of the open atoms excluding 000 or 111 (Theorem 5) | No exact weighting on the coarse 2-torus | Not computed |

- **Totals.** At scale 2 the rows give 22 + 54 + 46 = 122 shapes. At scale 3 they give 6 + 34 + 82 = 122: the six twisted pairs,
  34 excluded shapes (among them the 16 affine shapes that are not twisted pairs) and 82 open shapes.
- **Free magnitudes in the slice:** atoms 4; two excluded at distance two 3 (S2) or 2–3 (S1); not-all-equal type 3 (S2) or 2–3
  (S1); three-excluded 2 (S2) or 1–2 (S1); parity 1.

## Reading

- **Interference adds nothing where it can be decided.**
  - *Positive weights* see only the allowed states, and those are the counted ones.
  - *Signs* can cancel in principle, but the parity obstruction blocks cancellation on more than half of the shapes that are not
    exact.
  - *Real magnitudes* on the affine shapes add nothing beyond gauge copies of the ±1 exact laws.
- **The dense laws are what is left.** The 46 shapes open at scale 2 are the densest laws: atoms and two-excluded laws, with up to
  four free magnitudes. Ticket C searches them.
- **A lesson about proxies.** Exactness is checked on finitely many tori. Sides 2 to 4 are blind for parity on up triangles: sides 2
  and 4 carry a single coarse solution, so only side 3 constrains. That lets an irrational weight pass. With ±1 weights this never
  mattered. With real weights, the census needs a side where the solution space is large (6 or 7).

## Nonclaims

- The open shapes (46 at scale 2, 82 at scale 3) are not decided here. Ticket C searches them, as evidence only.
- Exactness is decided on the stated coarse tori only.
- Other subdivisions, lattices and mixed classes are not covered.
