# Interference across the two/three boundary: one cancelling witness per knot

Status: Proved

Ticket `INTERFERENCE-20261029-001A`, 2026-10-29.

## Standard statement

A *gadget* on visible bits x₁, …, xₙ is a function

  g(x) = Σ_{h ∈ {0,1}^m} Π_f f(z_f),

where z = (x, h) and every factor f is a real-valued function of at most two of the variables. Its *support* is the set of x
with g(x) ≠ 0. A relation on three bits is a *knot* when it is nonempty, not the whole cube, and its projection onto every
pair of coordinates is all four pairs (K1–K3 on allowed states). There are 34 knots in 16 classes up to coordinate order.

- **Theorem 1 (nonnegative values).** If every factor is nonnegative, the support of g is the projection of the conjunction of
  the factors' supports. So it is definable from binary relations with existential quantifiers, hence majority-closed, and it is
  never a knot, whatever the number m of hidden bits.
- **Theorem 2 (no hidden bits).** With m = 0 the support is never a knot, whatever the signs.
- **Theorem 3 (one hidden bit per clause).** A clause ℓ₁ ∨ … ∨ ℓ_k of any width is the difference of two products of one-variable
  functions, 1 − Π(1 − ℓᵢ). So a k-CNF with m clauses is a signed gadget with one hidden bit per clause. More generally a
  relation that excludes z tuples is a signed gadget with z hidden bits.
- **Theorem 4 (census).** Every one of the 16 classes of three-bit knots is exactly a signed gadget with one hidden bit, and
  with no fewer.
  - For 14 classes the indicator itself has real tensor rank 2. Its Cayley hyperdeterminant is 1 for the atoms, 4 for the
    pairs excluded at distance two and for parity, and 5 for the three-excluded classes.
  - For not-all-equal and twisted not-all-equal the hyperdeterminant is −3 and the real rank is 3. Multiplying by one pairwise
    sign makes the hyperdeterminant 5.
  - Every such decomposition has a negative entry, as Theorem 1 requires.
  - The decompositions of the three-excluded and not-all-equal classes involve the golden ratio.

So the two/three boundary of the program, that no 2-CNF with witnesses defines a knot, is a boundary of positivity. Once
witnesses may cancel, every three-bit knot is one witness away from pairs, and every CNF is one witness per clause away.

## Nearest known result

- **In the repository.** `KNOT-FOUNDATION-20261019-001E` proves (with a Lean kernel) that no 2-CNF with witnesses defines a knot.
  Theorem 1 is the same fact for nonnegative weighted sums, whose supports are existential projections.
- **Outside.**
  - Majority closure of relations definable from binary ones is classical (Baker and Pixley 1975; Schaefer 1978).
  - The clause identity 1 − Π(1 − ℓᵢ) is inclusion–exclusion. It is the first step of both 2026 refutations of the Exponential
    Time Hypothesis: OpenAI's clause polynomial Φ_e, and Anthropic's Appendix D, which expands the condition that no clause is
    violated over sets of violated clauses.
  - That a parity is a Hadamard transform of an equality is the basis of holographic algorithms (Valiant 2008; Cai and Lu).
  - Real ranks of 2×2×2 tensors are decided by the sign of Cayley's hyperdeterminant (de Silva and Lim 2008).
- **Classification.** Theorems 1 to 3 are elementary or classical. The census of Theorem 4 is a small local delta: no overlap
  was found for the minimum number of cancelling witnesses of each three-bit knot class.

## Theorem 1 (nonnegative values)

Write φ(z) for the product of the factors. If all factors are nonnegative, then g(x) = Σ_h φ(x, h) is a sum of nonnegative terms.
It is nonzero exactly when some term is, that is, when some h makes every factor nonzero. So the support is
{x : ∃h ∧_f z_f ∈ supp(f)}, a primitive-positive definition from the binary relations supp(f). Coordinatewise majority
preserves every binary relation and is preserved by primitive-positive definitions, so the support is majority-closed.

A knot is never majority-closed. Its pairs are all free, so majority closure would force it to contain every tuple, the whole
cube. (This is the program's `KNOT-FOUNDATION-20261019-001E`.)

The check confirms on 20,000 random nonnegative gadgets (three visible bits, up to three hidden bits, values 0, 1, 2) that the
support equals the projection and is majority-closed, and that none is a knot.

## Theorem 2 (no hidden bits)

With no hidden bits, g is a product. A product is nonzero exactly when every factor is, so its support is the intersection of the
factors' supports, a relation definable by binary relations without quantifiers. By Theorem 1 it is not a knot. The check runs
over all 16³ triples of supports on the three pairs of a three-bit system.

## Theorem 3 (one hidden bit per clause)

For a clause C = ℓ₁ ∨ … ∨ ℓ_k on Boolean inputs, [C] = 1 − Π_i [ℓᵢ false]. Take one hidden bit h with u(0) = 1, u(1) = −1,
k_i(0, ·) = 1 and k_i(1, x) = [ℓᵢ false at x]. Then Σ_h u(h) Π_i k_i(h, x_i) = [C](x). Every factor is binary.

For a CNF F = C₁ ∧ … ∧ C_m, the product of these one-bit sums is a sum over m hidden bits:

  F(x) = Σ_{h ∈ {0,1}^m} (−1)^{|h|} Π_{e : h_e = 1} Π_{i ∈ e} [ℓ_{e,i} false].

Summing over x gives the inclusion–exclusion formula for the number of satisfying assignments, the starting point of both
refutations.

For a relation R excluding a set Z, [R](x) = Π_{b ∈ Z} (1 − [x = b]), with one hidden bit per excluded tuple. The check covers
every clause of width 1 to 8 with every sign pattern, 300 random 3-CNFs, and all 256 relations on three bits.

## Theorem 4 (census)

By Theorem 2 no knot has a gadget with zero hidden bits. A gadget with one hidden bit h has the form

  g(x) = W(x) · Σ_{h=0,1} u(h) k₁(h, x₁) k₂(h, x₂) k₃(h, x₃),

with W a product of functions of two visible bits.

**W is nowhere zero.** If g = [K] for a knot K, W vanishes off K at most. The zero set of a pair factor is a union of
cylinders {x_i = α, x_j = β}, and each cylinder meets K because every pair is free in K. So W has no zeros.

**The criterion.** Hence [K]/W must have real tensor rank at most 2. A 2×2×2 tensor has real rank 2 when its Cayley
hyperdeterminant is positive and real rank 3 when it is negative. A decomposition into two products is exactly a gadget with one
hidden bit: k₁(h, ·), k₂(h, ·) and k₃(h, ·) are the three vectors of the h-th product.

The check computes the hyperdeterminant of each indicator. Where it is negative, the check searches the 2¹² pairwise sign
functions for one that makes it positive. It then decomposes exactly with sympy, using the eigenvectors of the pencil of the
two slices, and verifies the gadget on all eight inputs symbolically.

| Class (excluded tuples) | Hyperdeterminant | One hidden bit | Numbers in the decomposition |
| --- | --- | --- | --- |
| atoms (one tuple), four classes | 1 | yes | rational |
| two excluded at distance two, four classes | 4 | yes | rational |
| parity (even or odd), two classes | 4 | yes | rational: ½((1,1)^⊗3 ± (1,−1)^⊗3) |
| three excluded, four classes, incl. "no lone one" {001, 010, 100} | 5 | yes | golden ratio (1 ± √5)/2 |
| not-all-equal {000, 111} and twisted {011, 100} | −3 (real rank 3) | yes, after one pairwise sign | golden ratio |

Every decomposition has a negative entry. A nonnegative one would be a nonnegative gadget whose support is a knot, which
Theorem 1 excludes. Replacing every factor by its absolute value (control) gives a support strictly larger than the knot in
all 16 classes.

**Parity of any length.** Σ_{h=0,1} Π_i (−1)^{h xᵢ} = 2[x₁ + … + xₙ even], one hidden bit with Hadamard edges, checked for
n ≤ 10. The knot that hides the most (one full bit) is the cheapest to build by cancellation.

## Reading

- **The boundary is positivity.** The program's two/three boundary is a theorem about allowed states, where witnesses are read
  existentially. It is equally a theorem about counts, because counts are nonnegative. Once witnesses may cancel, the boundary
  disappears. Every three-bit knot is one witness away from pairs, and every 3-CNF is one witness per clause away. This
  reading does not change K1–K3: a signed sum is a second reading of "allowed" (allowed when the signed witness sum is
  nonzero), and the canonical reading is untouched.
- **This is where the ETH refutations start.** OpenAI's algorithm writes each clause as 1 − Π(1 − ℓ) before doing anything else.
  That moves every three-place knot of the formula into the signed pairwise form of Theorem 3. Anthropic's bound in n starts
  from the same inclusion–exclusion over violated clauses. Its main recursion instead keeps each clause as a node weight and
  cancels at the crossings of equality edges.
- **The golden ratio.** The three-excluded knots include the Fibonacci fusion rule ("no lone one"), and their one cancelling
  witness carries the golden ratio. This matches the Fibonacci rates of `SURFACE-GLUING-20261024-001`, and the sign that the
  Fibonacci rule needs in three dimensions (`HUB-DIMENSION-20261024-001`).

## Nonclaims

- No change to the canonical knot test, and no claim that the signed reading is the right one; that decision belongs to the
  owner (the epic's decision note records the request).
- No complexity claim: a signed gadget with one witness per clause is the inclusion–exclusion formula, which takes 2^m terms.
- The census is for three-bit knots only. Minimum witness counts for larger knots are not computed.
