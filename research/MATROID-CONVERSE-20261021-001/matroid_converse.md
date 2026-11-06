# Which matroids can a law that composes like cycles carry?

Epic `MATROID-CONVERSE-20261021-001`, closed 2026-10-21.

## The question

`DIAGONAL-LEMMA-20261021-001` showed that composing knots like cycles sees only
which sets are constrained, so a law's fibres can hide anything. The
matroid-level converse asks the remaining question at the right level:

- Does every law that composes like cycles have, system by system, the
  constrained sets of a difference law?
- In particular, can such a law carry a matroid that no field represents, like
  the Vámos matroid?

The owner asked for a literature scan first, then a test of Vámos.

**The evidence.**
- [The census](../../experiments/MATROID-CONVERSE-20261021-001A/MATROID-CONVERSE-20261021-001A-E001_matroid_census/contract.json),
  with [result](../../artifacts/MATROID-CONVERSE-20261021-001A/MATROID-CONVERSE-20261021-001A-E001_matroid_census/result.json).
- [The proof](../../proofs/MATROID-CONVERSE-20261021-001B/MATROID-CONVERSE-20261021-001B-P001_top_quotients/proof.md).

## The literature

- **What it covers.** The classical work studies *uniform* representations,
  where a set of rank r has exactly q^r joint values:
  - ideal secret sharing (Brickell and Davenport 1991);
  - [Seymour (1992)](https://collaborate.princeton.edu/en/publications/on-secret-sharing-matroids/),
    who showed that the Vámos matroid is not a secret-sharing matroid;
  - partition representations ([Matúš 1999](https://dblp.uni-trier.de/pid/55/5647.html));
  - almost affine codes (Simonis and Ashikhmin 1998);
  - [p-entropic matroids](https://arxiv.org/abs/1909.12175), which are linear
    for p = 2, 3 but not for p = 9.
- **Why it doesn't apply directly.** The program's free sets ask only for a
  full projection. That is so weak that a single relation can carry any
  matroid.
- **The real question.** Does composing like cycles bring back enough
  uniformity to exclude Vámos?

## What was found

- **Single relations carry anything, and their laws fail.**
  - The Vámos matroid is exactly the free-set family of its support relation
    (158 tuples). It is also the free-set family of a union of two GF(7) codes
    whose independent sets cover Vámos's.
  - Both relations have circuit projections with a direct case, so their laws
    fail elimination at once.
- **Difference laws carry only field-representable matroids.**
  - **The top lemma.** A subdirect product of Mal'tsev algebras that each have
    a unique maximal congruence is the full product exactly when its image in
    the simple tops is full.
  - **Groups.** For group laws that compose like cycles, every system's matroid
    is a direct sum of one GF(p)-representable matroid per prime, plus parallel
    classes.
  - **Fields.** Field laws carry F-representable matroids.
  - **What never appears.** The Vámos, non-Pappus and Fano/non-Fano 2-sum
    matroids never appear in these laws, or in their shadows, lifts and
    disjoint unions.
- **Tops exist without any difference operation.** In every law that composes
  like cycles, every range has a unique maximal pp-definable equivalence.
  - The argument is a chain of ties; elimination keeps every alternating
    composite proper.
  - This generalizes half of the circuits epic's Theorem 1.
  - It lets the conjecture be sharpened to a top lemma for all such laws.
- **The census agrees on every count** (signal true, all five predictions and
  all four controls).
  - **Group laws.** 750 systems over random subgroup laws of Z₄, Z₉, S₃, D₅ and
    AGL(1,5) all matched their top images. No circuit mixed primes, and two
    primes appeared together in 80 systems.
  - **Perturbations.** Of 91 one-tuple perturbations of x + y + z ≡ 0 over Z₃
    and of its lift, 83 fail. The 8 survivors are exactly the removals from the
    lift's (2,2,2)-block, and all keep the Z₃ law's constrained sets.
- **A lead for the next step.**
  - **A Siggers operation.** K₄ has no difference operation, but lifts of
    Z₃'s linear operations preserve it. For example, s(x, y, z, w) = h(x̄ + ȳ),
    with h sending 2 to 3, preserves K₄ and satisfies the Siggers identity
    s(a, r, e, a) = s(r, a, r, e). It is not idempotent, so this is a hint
    rather than a Taylor term. Checked by brute force.
  - **No obstruction to n-permutability.** No reflexive non-symmetric relation
    appears among small derivations.
  - **Why it matters.** The top lemma's proof uses modularity for one half and
    permutability only for Fleischer's lemma.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Single relations carry any downset | Comparing the uniform notions in the literature with free sets | Trivial once seen; separates relations from laws |
| Vámos as a union of two codes | Covering Vámos's independent sets by two representable weak-map images | New to the program |
| Top lemma | Generalizing the Frattini argument with modularity and Fleischer's lemma | Classical tools; possibly folklore |
| Group laws give per-prime direct sums | Top lemma plus Goursat and Scott's lemma | New to the program |
| Tops exist in every law that composes like cycles | Chaining ties, without permutability | New to the program; generalizes the circuits proof |
| Dressed survivors near Z₃ | Census A | Observation |

**Did the perspective do real work?** It did. Reading free sets relative to
ranges is what separates single relations, which are unconstrained, from laws,
which composition forces back to linear structure one prime at a time.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the census and the proof.
- 2 are administrative: this note and the ledger.

The recommendation is therefore substantive work.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the matroid-level converse | **Partially successful** | Proved for difference laws (groups and fields) and for their shadows, lifts and disjoint unions. Every such system's matroid is in 𝓡, so Vámos never appears. Tops exist in every law that composes like cycles. Open: laws without a difference operation. |
| Local direction — composition through matroids | Continue | The converse now reduces to a top lemma for all laws that compose like cycles, plus a description of their simple tops. |
| Broader exploration — composition (open question 3) | Known alternatives | (1) Mal'tsev conditions of such laws, the route through tame congruence theory. (2) The three-value question for the diagonal lemma (1/3). (3) The deferred space directions. |
| Long-term goal — intrinsic structure from logic | Capability gained | Composing like cycles forces linear structure, one prime at a time, wherever a difference operation exists. Arbitrary matroids need arbitrary relations, and their laws fail. Logic's cycle-like topologies look algebraic. |
| Next recommendation — Mal'tsev conditions of laws that compose like cycles, as a fresh epic | **Next step:** Continue. Decide by polymorphism search whether K₄ and the other dressed survivors are congruence n-permutable (Hagemann–Mitschke terms) or modular (Gumm terms). Then try to prove that composing like cycles implies modularity. In a modular variety, the top lemma's Lemma A holds as is, and only Fleischer's lemma needs a substitute. | A positive answer would place cycle-like composition inside the modular part of the algebraic CSP landscape and make the top lemma for all such laws within reach. A negative one would show that cycle-like composition is a new kind of condition. |
| Interest — that next step | **2/3 — Promising** | The first discriminators are finite searches, and the payoff is a structural theorem. The risk is that such laws are not modular and the converse needs new tools. |
| Execution — that next step | Deferred | Not started: the owner's request covered this epic. Stop if K₄ is neither n-permutable nor modular, and reassess. The next step is the owner's decision. |
