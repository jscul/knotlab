# Lane B: is the knot's class a free fermion at every coupling?

Ticket `NEXT-DIRECTION-SCAN-20261031-001B`, 2026-10-31. Scouting pass (documentation); no theorem is activated.

## Question

- **The Ising reading.** The number of 2-colourings of a signed cubic triple system is an even-subgraph (Ising high-temperature) sum on
  its incidence graph. Points carry [1,0,1,0] and lines [1,0,x²,0]. A negated incidence contributes −1 when its edge is used.
- **The colour basis.** The same sum is a *three-body Ising model*: a line weighs 1 + 3x² when its three points agree (after the signs) and
  1 − x² otherwise, and Z_col = 2^#points · Z_even.
- **The counting point** is x² = −1/3, where the weights become 0 and 4/3 (not-all-equal). Three other couplings are easy for every system:
  - x = 0 (constant weights);
  - x² = 1 (each line forces its points equal: linear algebra over GF(2));
  - x² = −1 (a quadratic phase, affine).
- **The algorithm under test.** The note counts the knot's class, the glued Kasteleyn signing on a Pfaffian incidence graph, at the counting
  point. It does so through trisum junctions, which are matchgate signatures there (TWIST-COUNT-20261030-001A, Theorem 4, the
  similitude).
- **The question.** Do these junctions stay matchgate signatures at every coupling x, so that the knot's class is a free fermion along the
  whole line? Or is the counting point special?

## Method

`fermion.py` works in the y-basis, where every planar page is a matchgate at every x.
- It computes the tensor of each closed branch at its square exactly, as a polynomial in x, by enumerating the even subgraphs of the
  branch.
- It contracts two branches into the junction seen by the host and tests the matchgate identity (MGI) as a polynomial in x.
- Signs: the glued Kasteleyn signing of `twist_lib.kasteleyn_tree_signing`. MGI is covariant under switching, so the verdicts do not depend
  on this gauge.
- Section 5 checks the tensors against brute-force sums over colourings of the glued systems, as polynomials in x, for systems up to
  22 points.

## Results

1. **Single pages: free at every coupling.** Junctions of two knot-class pages satisfy MGI identically in x, for all six pairs of cube,
   6-prism and truncated-octahedron pages.
2. **Why single pages work.**
   - Every knot-class page tensor lies in a two-parameter family: F(1010) = F(0101) = 0, F(1100) = −F(0011), F(1001) = F(0110).
   - The family is closed under junctions at every x (checked with symbolic members).
   - Theorem 4's similitude holds at every x: MGI(W) = c_Q(x) MGI(F_R) for a fully symbolic F_R. For the cube page,
     c_Q(x) = −x⁴(x² − 1)³(4x⁴ + 3x² + 1), which is 256/2187 at the counting point.
3. **Twists at depth one.**
   - With one twisted page, MGI(x) ≡ 0 at every x, so Theorem 6's unbranched-twist mechanism extends here.
   - With two twisted pages, MGI(x) is nonzero at the counting point and at generic x. It vanishes at the affine couplings x = 0, ±1, ±i,
     and only there for cube and 6-prism pages. Truncated-octahedron pairs have further isolated zeros, some real (x ≈ ±0.523, ±0.849).
4. **Depth two: the counting point is singled out.**
   - A closed branch made of a page that carries a junction at a second square leaves the two-parameter family.
     - In every tested branch, its defect F(1001) − F(0110) contains the factor 3x² + 1, times a factor that depends on the branch:
       2x⁴ + x² + 1 or 2x⁸ + x⁶ + 2x⁴ + 2x² + 1.
     - At the counting point the branch returns to the family, as Lemma 3 of TWIST-COUNT A proves there.
   - Junctions of two such deep branches break MGI in 5 of the 6 tested pairs. Example (two 6-prism branches, each carrying two cubes):
     MGI(x) = −16 x²² (x − 1)¹² (x + 1)¹² (x² + 1)² (3x² + 1)² (2x⁴ + x² + 1)².
   - **The factors common to all five are exactly x, x − 1, x + 1, x² + 1 and 3x² + 1**: the affine couplings and the counting point. The
     branch-specific factors (2x⁴ + x² + 1, 2x⁸ + x⁶ + 2x⁴ + 2x² + 1, 2x² + 1) differ between pairs and drop out.
   - **The exception.** Two truncated-octahedron branches keep MGI identically. Both lie in one rotated two-parameter family:
     F(1111) = 0, F(1100) = −F(0110), F(0011) = F(1001).
5. **Consistency.** The junction network reproduces the brute-force three-body Ising sum as a polynomial in x on six systems: four at depth
   one, in the knot's class and doubly twisted, and two at depth two with 20 and 22 points. In the knot's class #col = 0 at the counting
   point, as the dictionary requires.
6. **Control.** Junctions of generic matchgate pages break MGI in 20 of 20 random pairs, so results 1–4 are not automatic.

## Reading

- **Reading (b) is affirmed in its point form, and sharpened.**
  - The knot's signs are free-fermion along the whole coupling line only on single pages.
  - Once the trisum tree has depth two, the matchgate mechanism survives only at the counting point and the affine couplings, on every
    tested tree except one.
  - Among the non-affine couplings, the knot's signs single out the knot's own law, not-all-equal.
- **In the program's words.** On the knot's spaces, the knot's signs and the knot's law fit each other, and only each other. Unlike lane A,
  this is a native selection: nothing is imposed except the coupling. The space's Pfaffian signs decide at which law counting stays planar.
- **Caveats.**
  - Failure of MGI in the y-basis is not hardness. Another holographic basis, or another algorithm, could still count at other couplings.
  - The evidence is six depth-two pairs over three page types, and one pair is an exception.
  - Whether the truncated-octahedron exception extends to other special families, giving other tractable couplings on special spaces, is
    open.
- **Literature (brief check).**
  - Planar Ising is free-fermion at every coupling (Kasteleyn, Fisher).
  - A graph of genus g needs 4^g Pfaffians, and a single real Pfaffian needs planarity; Gobron's single Pfaffian uses multicomplex
    coefficients.
  - Turner relaxes the planarity of Pfaffian circuits only up to one crossing.
  - No source was found on the three-body Ising model on Pfaffian triple systems, or on a coupling singled out by Pfaffian signs. Folklore
    risk: moderate (the ingredients are classical); the statement appears new.
  - Sources: arXiv 1312.7289 (Gobron), arXiv 2003.02967 (Pham), arXiv 1510.01541 (Turner), arXiv 1307.7430 (Cai–Guo–Williams).

## The question it opens

**A coupling dichotomy in the knot's class.** On non-colourable cubic triple systems with the knot's signs, is the three-body Ising model
#P-hard at every coupling except the counting point and the affine ones?
- If yes, the knot's law is the only non-trivial law at which the knot's spaces count easily.
- The cheapest discriminator: a deep-branch junction that breaks MGI at generic x is a non-matchgate signature *inside* the knot's class.
  Test whether planar gadgets around it interpolate to a crossing, as PLAIN-BRACE's cube-junction ladder did at the counting point for
  twisted braces.

## Interest

**3/3 — Hot.**
- The evidence is concrete: single pages free everywhere, depth two pinned to the counting point, factors shared across five pairs, a brute
  force cross-check and a control.
- The payoff would be a native selection theorem: the space's signs select the knot's law.
- Main uncertainty: the hardness step inside the knot's class at generic couplings, and the special families (like the truncated
  octahedron's) that keep the identity.

## Files

- `fermion.py`: the computation (run with `--write`).
- `results.json`: all sections, including tensors, factorizations and zero sets.
- `fermion.log`: the run log.
