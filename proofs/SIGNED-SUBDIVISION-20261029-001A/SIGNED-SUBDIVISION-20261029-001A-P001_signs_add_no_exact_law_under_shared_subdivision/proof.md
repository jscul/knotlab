# Signs add no exact law under shared subdivision

Status: Proved

Ticket `SIGNED-SUBDIVISION-20261029-001A`, 2026-10-29.

## Standard statement

This uses the setting of `SHARED-SUBDIVISION-20261029-001A`.
- **The torus and the rules.** On the triangular-lattice torus a three-bit law sits on every up triangle (S2, 34 knots) or on
  every triangle, with one placement for up triangles and one for down triangles of the same class (S1, 88 pairs). That gives 122
  rule shapes.
- **Shared subdivision at scale k.** Every triangle is cut into k², with the new vertices shared between neighbours, so the coarse
  sites are the fine sites (k i, k j).
- **Signed rules.** The law now carries weights ±1 on its allowed tuples, independently on up and down triangles, up to one
  global sign per law: 135,440 signed rules. For a coarse assignment x, F(x) is the sum over fine assignments restricting to x of
  the product of the weights. W(x) is the product of the coarse weights.
- **Exact and support-exact.** A signed rule is *exact* at a scale when F = c·W for one c ≠ 0, on coarse tori of side 2, 3 and 4
  (scale 2) or 2 and 3 (scale 3). It is *support-exact* when F and W have the same support on those tori. Support-exactness is
  exactness of the allowed states under the interference reading adopted on 2026-10-29.

**Results.**
- **Lemma 1 (gauge).** Multiplying the up and down weights by one sign function on each class of edges leaves F and W unchanged on
  every torus, because each edge lies in exactly one up and one down triangle. For S2, so do sign functions of the three corners
  whose product is 1, because each site has each corner role exactly once. The 135,440 signed rules fall into 944 gauge orbits.
- **Theorem 2 (census).** Decided exactly on one representative per orbit:
  - **No new shape.** At scale 2 a signed rule is support-exact only when its shape is one of the 22 counted-exact shapes. At
    scale 3 it is support-exact only when its shape is one of the six twisted not-all-equal pairs. So no other shape becomes
    exact, or even support-exact, with signs.
  - **Scale 2.** Every sign pattern of the 22 counted-exact shapes is support-exact: all 80 of their gauge orbits. Exactness is
    finer: 28 orbits (3,144 signed rules) are exact. For parity on up triangles, parity on all triangles and the twelve
    three-excluded pairs, the exact orbit is the orbit of the unsigned law, one of two. For each twisted not-all-equal pair, two
    of its eight orbits are exact, the unsigned one included.
  - **Scale 3.** For each twisted pair, six of the eight orbits are support-exact, and all six are exact (36 orbits, 4,608 signed
    rules). The two orbits that are only support-exact at scale 2 lose even support-exactness at scale 3. Every orbit exact at
    scale 2 stays exact at scale 3.
  - **The coarse 2-torus alone misleads.** Two orbits each of the two symmetric three-excluded laws on up triangles (no lone one,
    no lone zero) are support-exact on the coarse 2-torus and fail on the 3-torus.
- **Corollary.** Under shared subdivision of the triangular lattice, ±1 interference creates no new exact or support-exact shape.
  It keeps every counted-exact shape exact in its unsigned class, and at scale 2 it keeps the allowed states of every sign
  pattern of those shapes. The exact signed laws are signed versions of the affine laws of `SHARED-SUBDIVISION-20261029-001`:
  parity, the frozen three-excluded laws and the line-collapsing twisted not-all-equal.

**Correction to the planned claim.** The plan expected every sign pattern of a counted-exact shape to stay exact. The census
refutes that: signs split each such shape into classes that reproduce their weights and classes that reproduce only their
allowed states. The claim above is the corrected one.

## Nearest known result

- **In the repository.**
  - `SHARED-SUBDIVISION-20261029-001A`: with counts, 22 of the 122 shapes are exact at scale 2 and 6 at scale 3, all with affine
    solution sets and zero entropy density. Not-all-equal never is.
  - `INTERFERENCE-20261029-001B`: with signs, most knots survive native coarse-graining, a finitely ramified substitution. On
    closed spheres, signed laws constant on rotation orbits stay parity-only under shared subdivision.
- **Outside.**
  - Gauge invariance of lattice partition functions under local sign changes is standard.
  - Signed weights on affine supports with quadratic signs are stabilizer states.
  - Exact real-space renormalization on two-dimensional lattices is rare.
  - No classification of signed three-bit laws under shared subdivision was found.
- **Classification.** Lemma 1 is elementary. Theorem 2: no overlap found (candidate local delta).

## Lemma 1 (gauge)

- **Edges.** An up triangle at (i, j) has corners a = (i, j), b = (i+1, j), c = (i, j+1). A down triangle at (i, j) has corners
  d = (i+1, j), e = (i, j+1), f = (i+1, j+1). A horizontal edge is (a, b) of one up triangle and (e, f) of one down triangle. A
  diagonal edge is (b, c) of an up triangle and (d, e) of a down triangle. A vertical edge is (a, c) of an up triangle and (d, f)
  of a down triangle.
- **S1.** Take sign functions h_H, h_D, h_V of two bits. Multiply each up weight by h_H(a,b) h_D(b,c) h_V(a,c) and each down weight
  by h_H(e,f) h_D(d,e) h_V(d,f). Then every edge's sign appears twice in the product over all triangles of any torus and cancels.
  This holds on every fine and every coarse torus, so F and W are unchanged.
- **S2.** Each site is the a-corner, the b-corner and the c-corner of exactly one up triangle each. Multiplying by g₁(a)g₂(b)g₃(c)
  with g₁g₂g₃ ≡ 1 multiplies every configuration by 1.
- **Orbits.** Exactness and support-exactness are therefore constant on gauge orbits. The check confirms invariance on 200 random
  (rule, gauge) pairs at coarse sides 2 and 3, and counts the orbits (944, with sizes summing to 135,440).

## Theorem 2 (census)

- **Method.** For each orbit representative, F and W are computed exactly, modulo three to six primes below 2^18 (ss_lib.py). The
  primes suffice because every |F(x) W(y)| is below half their product.
- **Filter.** Exactness on all tori needs exactness on the smallest ones. So every representative is decided on the coarse 2-torus
  at scales 2 and 3. Survivors go on to side 3 and side 4 (scale 2) and side 3 (scale 3).
- **Baseline.** Without signs, the check reproduces the counted census (22 shapes at scale 2, 6 at scale 3).

| Shapes | Gauge orbits | Support-exact, scale 2 | Exact, scale 2 | Support-exact, scale 3 | Exact, scale 3 |
|---|---|---|---|---|---|
| Parity on up triangles (2) | 4 | 4 | 2 | 0 | 0 |
| Parity on all triangles (2) | 4 | 4 | 2 | 0 | 0 |
| Three-excluded pairs (12) | 24 | 24 | 12 | 0 | 0 |
| Twisted not-all-equal pairs (6) | 48 | 48 | 12 | 36 | 36 |
| Every other shape (100) | 864 | 0 | 0 | 0 | 0 |
| All 122 shapes | 944 | 80 | 28 | 36 | 36 |

- **Signed rules.** The 28 exact orbits at scale 2 hold 3,144 of the 135,440 signed rules, and the 36 at scale 3 hold 4,608.
- **Per twisted pair.** Of the eight orbits, two are exact at both scales (the unsigned one among them), four are exact at
  scale 3 only, and two are support-exact at scale 2 only.

## Reading

- **The answer on genuine space does not change.** On genuine two-dimensional space, interference with weights ±1 creates no new
  law that reproduces itself, not even at the level of allowed states. The laws that were exact stay exact in their unsigned
  class.
- **Signs sort the old exact laws.** At scale 2 every sign pattern of an exact shape keeps its allowed states, but only some
  sign classes keep their weights. For parity and the frozen three-excluded laws only the unsigned class survives. Twisted
  not-all-equal keeps more classes at scale 3 than at scale 2.
- **A contrast with hierarchical space.** In finitely ramified towers (`INTERFERENCE-20261029-001B`), signs revived most knots.
  The difference is the substitution: shared midpoints couple neighbouring triangles. The cancellations that rebuild a knot inside
  one gadget then cannot be arranged consistently across the whole lattice.

## Nonclaims

- Weights are ±1. Real weights are ticket B.
- Exactness is decided on coarse tori up to side 4 (scale 2) and side 3 (scale 3), and these sizes are where survival is
  established.
- Other subdivisions, lattices and mixed classes are not covered.
