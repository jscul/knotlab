# Exact counted fixed points: which knots, at which sizes, with which factors

Status: Proved

Ticket `EXACT-TOWERS-20261029-001A`, 2026-10-29.

## Standard statement

The 34 relations on three bits in which every two coordinates are unconstrained, other than the full cube (the *knots*), form 16
classes under permutations of the coordinates. A *hub gadget* of a knot K joins copies of K, each in any coordinate order (a
*placement*). Three variables, the *legs*, lie in one copy each. Every other variable lies in at least two distinct copies, no copy
repeats a variable, and the copies are connected. Its *relation* is the set of leg tuples that extend to all variables.
- **Exact.** A gadget is an *exact counted fixed point* of K when two things hold. Its relation is a placement of K. Every allowed leg
  tuple has the same number c of extensions, the *factor*. Substituting it for every copy of any network then multiplies the number
  of solutions by c per copy and leaves the law unchanged.
- **Irredundant.** No two copies impose the same constraint on the same three variables. A repeated constraint changes nothing.
- **Single-scale.** The three legs are pairwise at one distance s. Two variables are adjacent when they share a copy.

**Results.**
- **Theorem 1.** The factor is the gadget's number of solutions with free legs divided by |K|.
- **Theorem 2 (linear).** For the two parity classes every rebuilding gadget is exact, with a factor that is a power of two.
- **Theorem 3 (symmetric).** A gadget whose automorphisms act transitively on its relation is exact. The symmetries of K itself act
  transitively on K only for the two parity classes, not-all-equal and twisted not-all-equal.
- **Lemma 4 (leg copies).** Suppose the legs of an exact gadget lie on three distinct copies. Deleting the copy of a leg leaves
  exactly c extensions of each excluded tuple.
- **Theorem 5 (census, exhaustive up to six copies).**
  - *Which classes.* Besides not-all-equal, exactly five classes have exact counted fixed points:
    - the two parity classes, from three copies;
    - twisted not-all-equal, from four;
    - the three-excluded classes {000, 011, 101} and {001, 010, 111}, from five.
  - *Not exact.* The two "x or (y ≠ z)" classes are rebuilt but never exact up to six copies.
  - *Not-all-equal* is exact at seven copies, by the punctured Fano plane with factor 5 (`HUB-SURVIVORS-20261029-001B`).
  - *Mechanisms.* For the classes other than parity, every irredundant exact gadget has one of four features, except 22 at six
    copies:
    - a *pendant*, copies holding no leg that at most two variables cut off;
    - a hidden variable frozen to a constant;
    - a tied pair;
    - transitive automorphisms.
  - *Smallest single-scale gadgets.* The smallest single-scale exact gadgets give tower growth exponents log₂ 3 (parity), 2
    (twisted not-all-equal), log₂ 6 (three-excluded) and log₃ 7 (not-all-equal).

## Nearest known result

- **In the repository.**
  - `HUB-SURVIVORS-20261029-001A` found which classes are rebuilt by hub gadgets of at most six copies: seven classes, and not the
    other nine. This census reuses its enumeration.
  - `HUB-SURVIVORS-20261029-001B` proved that not-all-equal is rebuilt first at seven copies, only by the punctured Fano plane, with
    factor 5.
- **Outside.**
  - Renormalization on hierarchical lattices is exact because the lattice is built by substitution (Berker and Ostlund 1979;
    Kaufman and Griffiths 1981). Its fixed points are studied for given interactions.
  - Constants built from gadgets ("pinning") are standard in counting constraint problems.
  - That fibres of a linear map have equal size, and that a transitive symmetry group makes counts uniform, are elementary.
- **Not found.** A bounded search found no classification of which hard constraint laws are fixed points of substitution by their
  own copies, counts included.
- **Classification.** Theorems 1 to 3 and Lemma 4 are elementary. Theorem 5 has no overlap found (candidate local delta).

## Theorem 1 (the factor)

Let G be exact for K with factor c, and let N be its number of solutions when the legs are free. Then N = c·|K|. For any network of
copies of K, replacing every copy by G (aligned to the copy's placement, with fresh hidden variables) gives exactly c^(number of
copies) extensions of each solution of the network, and none of any other assignment of its variables.

*Proof.* Each allowed leg tuple has c extensions and each excluded tuple none, so N = c·|K|. In the substituted network, the hidden
variables of different copies are disjoint. Given the old variables, the extensions therefore multiply over copies: c for a satisfied
copy, 0 for a violated one. ∎

## Theorem 2 (the linear mechanism)

If K is one of the two parity classes, every gadget whose relation is a placement of K is exact. Its factor is |S|/4, a power of two,
where S is its solution set.

*Proof.* Each copy is an affine equation over the two-element field, so S is an affine subspace. The restriction to the legs is an
affine map on S. Its image is the relation, of size 4, and every non-empty fibre is a coset of its kernel. So every allowed tuple has
|S|/4 extensions, a power of two. ∎

## Theorem 3 (the symmetric mechanism)

An *automorphism* of a gadget is a permutation π of its variables, together with a set of variables to complement, such that:
- π maps legs to legs;
- every copy, transported by π and the complementations, is a copy of the gadget, with multiplicities.

Every automorphism maps solutions to solutions and acts on leg tuples. If the automorphisms act transitively on the relation, the
gadget is exact.
- An automorphism induces a symmetry of the relation, a permutation of its coordinates with complementations.
- The symmetries of K act transitively on K exactly for:
  - the two parity classes (24 symmetries);
  - not-all-equal and twisted not-all-equal (12 symmetries each).
- For the other twelve classes, no exact gadget is explained by its automorphisms.

*Proof.* An automorphism is a bijection of the solution set. It carries the extensions of a leg tuple t onto those of its image, so
the counts are constant on orbits. A transitive action makes them constant on the relation. The orbit sizes are computed in check 1.
For example, "x or (y ≠ z)" has 4 symmetries with three orbits of size 2. The three-excluded classes have 6 symmetries, with orbits
of sizes 1, 1 and 3 on their 5 allowed tuples. ∎

## Lemma 4 (the copies of the legs)

Let G be exact for K with factor c, with its legs a, b, c′ on three distinct copies. Let t be an excluded tuple, i a leg and C_i its
copy. The extensions of t in G − C_i are exactly the extensions of t ⊕ e_i in G, so there are exactly c of them. Hence t has at
least 3c extensions that violate exactly one copy.

*Proof.*
- **The neighbours are allowed.** The excluded tuples of a knot are pairwise at Hamming distance at least 2, so t ⊕ e_i is allowed.
- **G − C_i does not see leg i.** Leg i lies only in C_i. So h extends t in G − C_i exactly when h extends t ⊕ e_i in G − C_i.
- **One direction.** Suppose h extends t ⊕ e_i in G. Then h extends t ⊕ e_i in G − C_i, hence t in G − C_i.
- **The other direction.** Suppose h extends t in G − C_i.
  - Since t is excluded, h violates C_i at t.
  - C_i's tuple at t is then excluded, so at t ⊕ e_i it moves to a neighbour. That neighbour is allowed.
  - So h extends t ⊕ e_i in G.
- **The count.** The c extensions obtained through different legs are distinct: each violates a different copy, and no other. ∎

`EXACT-TOWERS-20261029-001B` uses this lemma to show that softening an exact law is unstable.

## Theorem 5 (the census; computation)

Exhaustive over hub gadgets of three to six copies, every shape (3, 11, 104, 1065) and every placement (check 3). Below, "exact"
counts irredundant exact gadgets (shape and placements).

| class | 3 copies | 4 copies | 5 copies | 6 copies | factors |
| --- | --- | --- | --- | --- | --- |
| parity, even tuples allowed | 2 / 2 / 2 | 2 / 1 / 1 | 30 / 22 / 13 | 186 / 116 / 71 | 1, 2, 4 |
| parity, odd tuples allowed | 2 / 2 / 2 | 2 / 1 / 1 | 30 / 22 / 13 | 186 / 116 / 71 | 1, 2, 4 |
| twisted not-all-equal {001, 110} | – | 2 / 2 / 1 | 16 / 10 / 2 | 179 / 115 / 29 | 1, 2, 3, 4, 5, 6 |
| three excluded {000, 011, 101} | – | 1 / 0 / 0 | 10 / 3 / 1 | 93 / 54 / 23 | 1, 2, 3, 4, 5 |
| three excluded {001, 010, 111} | – | 1 / 0 / 0 | 10 / 3 / 1 | 93 / 54 / 23 | 1, 2, 3, 4, 5 |
| x or (y ≠ z) {000, 011} | – | 1 / 0 / 0 | 8 / 0 / 0 | 77 / 0 / 0 | none |
| ¬x or (y ≠ z) {001, 111} | – | 1 / 0 / 0 | 8 / 0 / 0 | 77 / 0 / 0 | none |

Each cell gives rebuilding shapes / shapes with an irredundant exact gadget / shapes with a pendant-free one. A *pendant* is a
group of copies, holding no leg, that at most two variables cut off from the rest. No other class is rebuilt up to six copies
(`HUB-SURVIVORS-20261029-001A`), so none is exact there.

**Mechanisms (checks 4 to 6).**

- **Parity.** Every exact gadget is linear: 440 rebuilding gadgets, all exact, all affine (check 4).
- **The other classes.** Each irredundant exact gadget is assigned the first of these that applies (check 6):
  - a *pendant*;
  - a *frozen* hidden variable, constant on all solutions;
  - a *tied* pair, two variables always equal or always opposite;
  - automorphisms transitive on its relation.

  Counts of gadgets, three to six copies:

| class | pendant | frozen hidden variable | tied pair | transitive automorphisms | none of these |
| --- | --- | --- | --- | --- | --- |
| twisted not-all-equal {001, 110} | 1698 | 0 | 411 | 6 | 18 |
| three excluded {000, 011, 101} | 698 | 213 | 49 | 0 | 2 |
| three excluded {001, 010, 111} | 698 | 213 | 49 | 0 | 2 |

The 22 gadgets with none of these are all at six copies:

| class | shape | factor | leg distances | automorphisms | orbit sizes on the relation | gadgets |
| --- | --- | --- | --- | --- | --- | --- |
| each three-excluded class | ade, bdf, cef, deg, efh, fgh | 2 | 2, 2, 2 | 1 | 1, 1, 1, 1, 1 | 2 + 2 |
| twisted not-all-equal | ade, bdf, ceg, dfh, efg, efh | 3 | 2, 2, 3 | 2 | 2, 2, 2 | 9 |
| twisted not-all-equal | ade, bdf, ceg, dfh, egh, fgh | 3 | 2, 2, 3 | 4 | 2, 4 | 9 |

Their counts are uniform although their automorphisms leave several orbits. The first has no automorphism at all.

**"x or (y ≠ z)".**
- **Scope.** Check 6b covers its 1120 rebuilding gadgets of three to six copies, none of them exact. Two of its allowed tuples lie at
  distance 2 from both excluded tuples, 101 and 110 for {000, 011}.
- **The far tuples lead.**
  - In every one of the 1120, these two *far* tuples have more extensions on average than the other four.
  - In 1112 of them, each far tuple has at least as many as each of the others.

**Single-scale exact gadgets and their dimensions.** A single-scale gadget with m copies and legs at distance s generates a tower
whose growth exponent is log m / log s (`EXACT-TOWERS-20261029-001B`). Up to six copies, and at seven for not-all-equal.

Pendant-free single-scale exact gadgets (check 5):

| class | copies m | distance s | factor c | log m / log s | mechanism |
| --- | --- | --- | --- | --- | --- |
| parity (each class) | 3 | 2 | 2 | log₂ 3 ≈ 1.585 | linear |
| parity (each class) | 4 | 2 | 1 | 2 | linear |
| parity (each class) | 5 | 2 | 2 | log₂ 5 ≈ 2.322 | linear |
| parity (each class) | 5 | 3 | 4 | log₃ 5 ≈ 1.465 | linear |
| parity (each class) | 6 | 2 | 1 and 2 | log₂ 6 ≈ 2.585 | linear |
| parity (each class) | 6 | 3 | 2 | log₃ 6 ≈ 1.631 | linear |
| twisted not-all-equal | 4 | 2 | 2 | 2 | transitive automorphisms |
| twisted not-all-equal | 6 | 2 | 2 | log₂ 6 | tied pair |
| each three-excluded class | 6 | 2 | 1 | log₂ 6 | tied pair |
| each three-excluded class | 6 | 2 | 2 | log₂ 6 | none of these |
| not-all-equal | 7 | 3 | 5 | log₃ 7 ≈ 1.771 | transitive automorphisms (`HUB-SURVIVORS-20261029-001B`) |

The smallest single-scale exact gadget of each class:
- **Parity.** The triangle: three copies, one on each corner of a subdivided triangle with no middle copy, factor 2, dimension
  log₂ 3. This is the Sierpinski gasket.
- **Twisted not-all-equal.** The punctured tetrahedron: four copies on the faces of a tetrahedron, one vertex split into the three
  legs, factor 2, dimension 2. It is unique up to symmetry, and transitive.
- **The three-excluded classes.** Six copies, dimension log₂ 6. One has a tied pair. The other, with factor 2, has no automorphism.
- **Not-all-equal.** The punctured Fano plane: seven copies, factor 5, dimension log₃ 7. It is unique.

## Reading

- **What exactness is.** An exact counted fixed point is a law that looks the same at every scale, counts included. Each level adds
  log₂ c hidden bits per copy, and the visible law never changes.
- **How exactness arises.** Four ways were found, and a remainder.
  - *Linearity.* For parity every rebuild is exact.
  - *Symmetry.* Only the classes whose own symmetries are transitive can use it. In this range only the punctured tetrahedron does,
    and the punctured Fano plane at seven copies.
  - *Collapse.* A tied pair makes an equality, typically from parallel copies. A frozen hidden variable makes a constant.
  - *Decoration.* A pendant hangs on the rest through one or two variables and acts as a weight on them. A constant weight is a
    padding. A weight that vanishes somewhere is a constraint, which can remove tuples the rest allows and so even out the counts.
  - *The remainder.* Twenty-two gadgets at six copies are exact with none of these. One shape has no automorphism at all.
- **What fails.**
  - "x or (y ≠ z)" is rebuilt from four copies, but its counts are never uniform up to six copies. Its symmetries have three orbits,
    so symmetry cannot make it exact.
  - In its rebuilding gadgets the two tuples far from both excluded tuples, x = 1 with y ≠ z, lead. Ticket B follows a tower in
    which they take over the counted law, a decomposable relation.
  - Decoration might still make it exact at larger sizes. The census does not decide this.
- **The law does not fix the dimension.**
  - Parity alone has pendant-free single-scale exact gadgets with six growth exponents within six copies, from log₃ 5 ≈ 1.465 to
    log₂ 6 ≈ 2.585.
  - At its smallest size, each other law has one exponent: 2 for twisted not-all-equal (the punctured tetrahedron), log₂ 6 for the
    three-excluded classes, and log₃ 7 for not-all-equal, where the Fano plane is forced.

## Checks

`check.py` (numpy) on the library `exact_lib.py`, with `result.json`:
- **0.** The dependency artifacts are bound by hash.
- **1.** 34 knots in 16 classes. The symmetries of each class and their orbits; transitive exactly for the four classes named.
- **2.** The enumeration matches a full canonical enumeration at three, four and five copies (3, 11, 104). The size-first ordering
  misses shapes (control).
- **3.** The census and the factor formula for every exact gadget.
- **4.** Linear mechanism: every parity rebuild is exact, with an affine solution set and factor |S|/4, a power of two.
- **5.** The single-scale irredundant exact gadgets: mechanisms, and the pendant-free ones with their growth exponents.
- **6.** The mechanism of every irredundant exact gadget of the classes other than parity: pendant, frozen hidden variable, tied pair,
  transitive automorphisms (signed permutations of the variables fixing the leg set), or none, with orbit sizes for the last.
- **6b.** The far tuples of "x or (y ≠ z)" in all 1120 of its rebuilding gadgets.
- **7.** Lemma 4 on all 458 irredundant exact gadgets with their legs on distinct copies. In only 54 of them do all copies, not just
  the legs' copies, leave exactly c extensions.
- **8.** The punctured Fano gadget: exact, factor 5, legs at distance 3.
- **9.** Controls:
  - a rebuilding gadget with non-uniform counts is detected;
  - a doubled copy is flagged redundant and leaves the counts unchanged;
  - brute-force counts agree with the contraction on a random sample.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Theorems 1 to 3, Lemma 4 | Fibre counting, linear algebra, orbit counting, the isolation of a knot's excluded tuples | Elementary |
| Theorem 5 | Exhaustive census on the enumeration of `HUB-SURVIVORS-20261029-001A` | Candidate local delta |
| The question | Which laws reproduce themselves with their counts (`HUB-SURVIVORS-20261029-001`, recommendation) | From the program |

## What this does not show

- **Larger sizes.** Whether "x or (y ≠ z)" is exact at larger sizes. Not-all-equal shows that a bounded census decides nothing
  about larger sizes, and decoration can tune counts.
- **The remainder.** Why the 22 gadgets of the remainder are exact. The mechanisms are a description, assigned in a fixed order, not
  a proof that each one causes exactness.
- **Beyond six copies.** Anything about the classes that are not rebuilt up to six copies, beyond that they are not exact there.
- **The set-level reading.** Counts are a branch-internal measure. The canonical knot test reads only the set of allowed states,
  and for it every rebuilding gadget reproduces the knot.
