# Which substrates a law fails on, and whether globally

Status: Proved

Ticket `BEYOND-TWO-20261101-001C`, 2026-11-01.

## Question

- **What B found.** Blurring gives laws on three and four values that compose like cycles, fail recognisably and count hard. That is
  mutual selection in PINNING C's formal sense.
- **What the knot's selection means.** The knot's selection meant more:
  - its failures pick out a structural class of substrates, the knot's spaces;
  - every failure is global (no part of it can be removed);
  - on its failing spaces, counting becomes easy again.

  Parity, by contrast, fails locally (PARITY-CORRECTION).
- **The question here.** On which substrates do these laws fail, and are their failures global?

## Dependencies

- **`BEYOND-TWO-20261101-001B`.**
  - The blurring lemma.
  - Blurred parity and blurred Z3: Mal'tsev, cycle-like composition, #P-complete counts.
- **`THREEFOLD-SPACES-20261030-001A`.** Theorem 1: a connected cubic system is non-2-colourable iff it is minimally so, iff its
  incidence matrix is sign-nonsingular.
- **`NATIVE-PATHS-20261101-001`.**
  - A: the signed Seymour bound and minimality, for signed systems.
  - C: the twist criterion, which says the failing signings form one switching class.
- **`MUTUAL-SELECTION-20261031-001C`.** The census of all 60 connected cubic bipartite graphs with up to 8 points per side, read as
  substrates, together with their Pfaffian status.

## Setting

- **Substrates.** A substrate is a connected cubic system: n points and n lines, every line holding three points and every point on
  three lines. A is its n × n incidence matrix.
- **Signed laws on a substrate.** Each law reads every line with signs.
  - The knot: not-all-equal of the colours read through signs, as in A.
  - Parity: x + y + z = c over GF(2), one c per line.
  - Z3: x + y + z = c over Z3.
  - Blurred parity and blurred Z3 (B): their preimages.
- **Global failure.** A failure is *global* when removing any one line makes the system solvable. Otherwise it is local.

## Theorem

1. **The knot.**
   - It fails on a substrate (under some signing) iff the substrate is Pfaffian.
   - The failing signings form one switching class.
   - Every failure is global.
2. **Parity and blurred parity.**
   - They fail (for some right-hand side) iff the substrate has an even number of perfect matchings.
   - No failure is ever global.
3. **Z3 and blurred Z3.**
   - They fail on every substrate.
   - On a substrate of Z3-corank 1 every failure is global. On a substrate of corank 2 or more every failure is local.
4. **A law that both selects and composes, at four values: blurred Z3 on corank-1 substrates.**
   - **Global failures.** Its failures are global.
   - **Recognisable.** The class of failing systems is recognised in polynomial time: corank 1, and the right-hand sides do not sum to
     zero.
   - **Easy in return.** Removing any line leaves exactly three solutions of the image, so its count there is easy.
   - **Hard in general.** Its count in general is #P-complete (B).
   - **Composition.** It composes like cycles (B).

5. **Rigidity.** Remove any line from a failing Z3 system on a corank-1 substrate.
   - **The bridge's selected spaces are rigid.** Exactly three solutions remain: one degree of freedom. Every circuit is a tie of two
     variables and no knot survives. The same holds for blurred Z3, since blurring keeps circuits.
   - **The knot's are not rigid in general.** Of the 8 Pfaffian substrates, removing a line leaves a knot at every line on the Fano
     plane (10 colourings) and on four others. On one it leaves a knot at 3 of 7 lines. On two (K4^(3) and one 8-point substrate) it
     leaves only ties.
   - **So** the four-value bridge selects only rigid, pairwise spaces, while the knot can select spaces that keep a knot inside.

**Among the three-valued laws examined here, none does both.** Z3 fails globally but counts easily, and blurred parity counts hard but
never fails globally. The other Mal'tsev laws on three values are not classified (B).

## Proof

**Item 1.**
- **When the knot fails.**
  - Read through signs σ, the system is non-colourable iff its signed incidence matrix is sign-nonsingular. The argument is Seymour's,
    with signs: NATIVE-PATHS C, item 1, and THREEFOLD-SPACES Theorem 1 for plain signs.
  - Sign-nonsingular means all perfect matchings contribute to det with one sign, i.e. |det| = perm. So some signing fails iff the
    bipartite graph has a Pfaffian signing.
- **One class.** The failing signings form one switching class (NATIVE-PATHS C, item 1).
- **Global.** A connected cubic signed system that fails is minimally so (NATIVE-PATHS A). ∎

**Item 2.**
- **When parity fails.** Ax = c fails for some c iff A is singular over GF(2), iff det A ≡ 0 (mod 2). Since det ≡ perm (mod 2), that is
  iff perm A, the number of perfect matchings, is even.
- **The witness.** A failure has a witness y with yᵀA = 0 and yᵀc = 1, i.e. a set of lines covering every point an even number of
  times with an odd total right-hand side.
- **It never uses every line.** If y used every line, it would cover every point three times, an odd number.
- **So the failure is local.** Remove a line outside y: the witness survives.
- **Blurred parity.** By the blurring lemma it fails exactly when its image does. ∎

**Item 3.**
- **Always singular.** Every point lies on three lines, so the all-ones combination of rows is 3 · (all ones) = 0 over Z3. So A is
  singular, and Ax = c fails whenever Σc ≢ 0.
- **The kernel.** Let K be the left kernel, so dim K is the corank. A failing c gives a nonzero functional f(y) = yᵀc on K. Removing
  line L leaves the system failing iff f is nonzero on K_L = {y ∈ K : y_L = 0}.
- **Corank 1.** K is spanned by the all-ones vector and K_L = 0 for every L, so every failure is global.
- **Corank 2 or more.**
  - Each K_L is a hyperplane of K, since the all-ones vector is not in it. The failure is global only if every K_L equals ker f.
  - Then every coordinate functional on K would be proportional to f. The inclusion of K into Z3^lines would then have rank 1, which
    forces dim K = 1, a contradiction.
  - So some line can be removed while the system still fails.
- **Blurred Z3.** By the blurring lemma it fails as Z3 does. ∎

**Item 4.**
- **Recognition.** The corank and Σc are computable, and at corank 1 the system fails iff Σc ≢ 0.
- **Three solutions.** Removing a line from a corank-1 system leaves n − 1 independent rows, so the solutions form a line in Z3^n: three
  points.
- **The blurred count.** It is their weighted sum, with weight 2 for every 0.
- **The rest.** Composition and hardness are B. ∎

**Item 5.**
- **The solutions.** The three solutions form a line x₀ + tk (t ∈ Z3) in Z3^n. A variable with k_v ≠ 0 takes all three values, and any two
  such variables determine each other.
- **Ties.** So every pair of moving variables is constrained while each alone is not. Every circuit is such a pair, and no set of three
  or more is minimal.
- **The knot.** Its side is computed (check 7). ∎

## Checks

`check.py` (`result.json`, about 4 s), on all 60 connected cubic substrates with up to 8 points (1, 1, 2, 5, 13 and 38 of them):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved; the census bound by hash. | pass |
| 1 | The knot. Pfaffian is decided by a signing with \|det\| = number of perfect matchings, agreeing with the census. | 8 Pfaffian; each has exactly one failing switching class, and its failure is global; every class colourable on the other 52 |
| 2 | Parity. | fails on exactly the 38 substrates with an even number of perfect matchings; 0 global failures among all failing right-hand sides |
| 3 | Z3. | fails on all 60; coranks 1: 24, 2: 27, 3: 9; of 15855 failures tested, the 5173 global ones are exactly those on corank-1 substrates |
| 5 | Blurred Z3 is easy in return: corank-1 substrates with up to 7 points, every line removed. | 10 substrates, 63 removals; 3 solutions each; the brute-force count equals the weighted sum |
| 6 | The summary by size. | below |
| 7 | Rigidity. Z3 on corank-1 substrates, every line removed. The knot on the 8 Pfaffian substrates (failing signing), every line removed. | Z3: 175 removals, all ties. The knot keeps a knot at every line on 5 substrates (Fano: 10 colourings), at 3 of 7 on one, at none on two (4 and 8 colourings) |

| Points | Substrates | Pfaffian (the knot fails) | Even perfect matchings (parity fails) | Z3-corank 1 (Z3 fails globally) |
| --- | --- | --- | --- | --- |
| 3 | 1 | 0 | 1 | 0 |
| 4 | 1 | 1 | 0 | 1 |
| 5 | 2 | 0 | 1 | 1 |
| 6 | 5 | 1 | 4 | 2 |
| 7 | 13 | 2 | 9 | 6 |
| 8 | 38 | 4 | 23 | 14 |

## Reading

This section is interpretation, kept apart from the theorem.

- **Global failure needs cancellation of the right kind.**
  - On a cubic substrate every distinction sits in three lines.
  - A linear law fails globally only if the whole space cancels, which needs 3 = 0, so characteristic 3: Z3, not parity.
  - The knot fails globally for the opposite reason: nothing cancels. Its perfect matchings all agree in sign (sign-nonsingular).
  - This is the owner's "harmonies are incommensurables cancelling", met at the level of failure.
- **Linear selection is rigid; the knot's need not be.**
  - After removing a line, blurred Z3's selected spaces are one moving value seen everywhere, so they are pairwise.
  - The knot's selected spaces can keep emergence inside: a four-place knot survives the removal of any line of the Fano plane.
- **The bridge exists, at four values, and it is linear.**
  - Blurred Z3 on corank-1 substrates selects in the knot's full sense: global and recognisable failures, easy in return, hard in
    general. It also composes like cycles.
  - It needs characteristic 3 for its global failures, and a doubled value for its hard count.
  - Its selected substrates (corank 1 over Z3) are a linear-algebraic class. The knot's (Pfaffian) are a no-cancellation class, and
    the knot cannot compose like cycles.
- **So the knot stays apart.** On two values, selection and cycle-like composition exclude each other (SELECT-COUNT A). Beyond two
  values they can coexist, but only through linearity in characteristic 3 plus a hidden multiplicity, not through the knot's kind of
  failure.

## What this does not establish

- **Larger substrates.** Only substrates with up to 8 points were enumerated. The theorems hold for all.
- **Other three-valued laws.** The simple non-affine Mal'tsev laws on three values were not examined for global failures.
- **Arities other than three.** For a k-regular, k-uniform substrate, the same argument gives global linear failures exactly when the
  characteristic divides k. This is not checked here.

## Novelty

- **Classical.**
  - Pfaffian signings and sign-nonsingularity (Kasteleyn; Little; Robertson–Seymour–Thomas).
  - det ≡ perm (mod 2).
  - Linear algebra over Z3.
- **Ours.** Seymour's bound for the knot's spaces (THREEFOLD-SPACES, NATIVE-PATHS).
- **New here.**
  - The census comparing the three laws' failing substrates and their globality.
  - The corank dichotomy for Z3.
  - The bridge at four values.
- **Folklore risk.** Moderate for the corank dichotomy, low for the comparison as a whole.
