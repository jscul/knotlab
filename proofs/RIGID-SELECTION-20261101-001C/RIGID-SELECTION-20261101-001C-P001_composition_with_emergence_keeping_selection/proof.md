# A law that composes like cycles and selects spaces that keep a knot

Status: Proved

Ticket `RIGID-SELECTION-20261101-001C`, 2026-11-01.

## Question

- **What ticket B found.** Signed Z4 fails globally on substrates and keeps knots inside the spaces it selects.
- **What it lacks.** Z4's coset law counts easily: it is strongly balanced (BEYOND-TWO A). So it has no hard count in return for its
  failures.
- **What blurring does.** It keeps failures and circuits and makes counts hard (BEYOND-TWO B).
- **The question.** Does blurred signed Z4 have all four properties at once?
  1. It composes like cycles.
  2. It selects spaces globally and recognisably.
  3. Counting it is hard.
  4. It keeps a knot inside the spaces it selects.

## Dependencies

- **`RIGID-SELECTION-20261101-001B`.** The two spaces. **`RIGID-SELECTION-20261101-001D`.** The top-layer theorem.
  **`RIGID-SELECTION-20261101-001A`.** `zlocal.py`.
- **`BEYOND-TWO-20261101-001B`.** The blurring lemma and the count-matrix test; through it, KNOT-CIRCUITS Theorems 1 and 2.

## The law

- **The blur.** φ: {0, 1, 2, 3, 4} → Z4 sends 0 and 1 to 0, and 2, 3, 4 to 1, 2, 3. So the value 0 is doubled, and the preimage sizes
  are w = (2, 1, 1, 1).
- **The relations.** Every relation R_(s,c) = {x : Σ s_i x_i = c (mod 4)} of signed Z4, at three or four places, is replaced by
  φ^(−1)(R_(s,c)).

## Theorem

1. **It composes like cycles.**
   - **Same constrained sets.** Its systems have exactly the constrained sets of their images.
   - **Why that suffices.** The images are systems of Z4's coset law, which composes like cycles.
   - **A Mal'tsev lift.** A lift of x − y + z preserves every relation of the law.
2. **It selects recognisably and globally.**
   - **Where it fails.** A blurred system fails exactly when its image fails, which linear algebra over Z4 decides.
   - **On ticket B's spaces.** It fails globally on both of them.
3. **It keeps knots.**
   - **Four places.** On the 6-point space, after any line is removed: 6 knots each time.
   - **Three places.** On the 9-point cubic space, after line 0 is removed: 10 knots.
4. **Counting it is #P-complete.**
   - **The test.** Each three-place relation has a count matrix (pairs of values against the number of completions) of rank 4, while
     signed Z4's have rank 1.
   - **The consequence.** The law is not strongly balanced, so counting it is #P-complete (Dyer–Richerby).
5. **Its count is a short sum.** After a removal, the count on these spaces sums over the 8 solutions of the image. Each solution is
   weighted by 2 to the number of its zeros.
6. **What it keeps lies below the top layer.** Each kept knot is pulled back from a knot of Z4 (ticket D).
   - **One full-range variable at most.** At most one of its variables has an image taking all four values.
   - **One digit at most.** The knot hides at most one digit of Z4.

**Consequences.**
- **Composing like cycles does not force rigid selection.** At five values one law has all four properties:
  - it composes natively;
  - it selects globally and recognisably;
  - counting it is hard;
  - it keeps emergence inside the spaces it selects.

  What it keeps lies below its top layer.
- **At two values the two properties exclude each other.**
  - **Composing like cycles forces rigidity.** A two-valued law with knots that composes like cycles is affine (KNOT-CIRCUITS
    Theorem 2), so it is rigid (ticket D with k = 1).
  - **The knot is not rigid.** It keeps knots inside its selected spaces, at every line on 5 of the 8 Pfaffian census substrates
    (BEYOND-TWO C).

## Proof

**Item 1.**
- **Solutions are preimages.** The solution set of a blurred system is S′ = φ^(−1)(S), where S is the image's solution set.
- **Projections and ranges.** Since the fibres of φ^(−1) are products, each projection and each range of S′ is the preimage of the
  image's.
- **Same constrained sets.** |φ^(−1)(T)| = Σ_(t∈T) Π w(t_i) is strictly increasing in T. So a set of variables is constrained in S′
  iff it is constrained in S. This is the blurring lemma of BEYOND-TWO B.
- **Circuit elimination.** The images are cosets of subgroups of Z4^n, that is, systems of Z4's coset law. That law composes like
  cycles by KNOT-CIRCUITS Theorem 1, since every subgroup of Z4 has a unique maximal subgroup. So circuit elimination holds for the
  blurred systems too.
- **The Mal'tsev lift (check 1).** Let m′(x, y, z) be z if x = y, x if y = z, and otherwise the least preimage of
  φx − φy + φz.
  - **It is Mal'tsev.** The first two cases give the identities, and they agree when x = y = z.
  - **It lifts x − y + z.** In every case φ(m′(x, y, z)) = φx − φy + φz, so it preserves every preimage of a coset.
  - **Four places.** Each four-place relation is pp-defined by two three-place ones: (x ± y − u = 0) and (u ± z ± w = c), with u
    existential. Checked for all 64.

**Item 2.**
- **Decision.** S′ is empty iff S is empty. That is decided by the Smith form over Z4 in polynomial time, and check 5 confirms it on
  300 random systems.
- **Global failure.** On ticket B's spaces the image fails globally, so the blurred system does too. Brute force over 5^6 and 5^9
  confirms this (checks 2 and 3).

**Item 3.** By item 1 the knots are the image's, which ticket B found. Brute force confirms them.

**Item 4.**
- **The count matrix.** For a three-place relation, the entry at (x′, y′) is the number of z′ completing it: 2 when the needed image
  value is 0, otherwise 1.
- **Its rank.** All entries are positive, so the matrix is a single block. Its rank is 4, while for signed Z4 every entry is 1 and the
  rank is 1.
- **Hardness.** By Dyer and Richerby, #CSP is in FP iff the language is strongly balanced, and #P-complete otherwise. A relation
  whose count matrix is one block of rank above 1 is not balanced, so counting is #P-complete.

**Item 5.** |S′| = Σ_(x∈S) Π w(x_i) = Σ_(x∈S) 2^(number of zeros of x), confirmed by brute force.

**Item 6.**
- **Theorem D applies.** The images on the spaces are square systems over Z4 that fail globally, so ticket D applies.
- **What the variables see.** A blurred variable's image takes all four values iff the image variable has full range.
- **Confirmed by brute force.** Checks 2 and 3 confirm that every kept knot has at most one such variable.

**Consequences.**
- **Five values.** This follows from items 1–5.
- **Two values.**
  - **Composing like cycles.** It needs an affine law (Theorem 2), whose global failures are rigid at every arity (ticket A, item 1;
    ticket D with k = 1).
  - **The knot.** The 5 of 8 is BEYOND-TWO C's census statement. All 8 Pfaffian incidence graphs are isomorphic to their duals (ticket
    B, check 3a), so it holds under both readings. ∎

## Checks

`check.py` (`result.json`, about 2 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | The Mal'tsev lift. | identities hold; it lifts x − y + z; preserves all 32 three-place relations; all 64 four-place relations pp-defined |
| 2 | The 6-point space, brute force over 5^6. | global; knots after every removal; constrained sets equal the image's; counts = weighted image solutions (93, 54, 16, …) |
| 3 | The 9-point cubic space, brute force over 5^9. | global; 10 knots after removing line 0 (600 solutions); constrained sets equal the image's at every removal |
| 4 | Count matrices. | rank 4 for all 32 blurred relations; rank 1 for signed Z4 |
| 5 | 300 random blurred systems. | recognition by Z4 linear algebra agrees with brute force (116 failing); 864 circuit pairs, no elimination failure |

**Correction during the ticket.** The Partial manifest said the count matrices have rank 2, by analogy with blurred parity. Check 4
found rank 4. The rank grows with the image: 2 for parity, 3 for Z3, 4 for Z4. The conclusion, rank above 1, is unchanged.

## What this does not establish

- **Two spaces only.** The law's selected spaces are exactly signed Z4's (item 2). Only the two spaces of ticket B are verified to
  keep knots.
- **Fewer values.** Blurring a field gives rigid laws (ticket A, item 3), so blurring needs Z4 underneath, which means five values.
  Whether a law on three or four values composes like cycles, counts hard and keeps knots inside its selected spaces is open.
- **Hubs.** Composition through hubs or a declared substrate is not considered.

## Novelty

- **Classical ingredients.** Blurring (preimage under a surjection), Dyer–Richerby's dichotomy, and the Smith form.
- **New here.** The construction and the five-value bridge.
