# Novelty and utility of the composition characterization

Epic `CYCLE-UTILITY-20261021-001`, closed 2026-10-21.

## The question

`AFFINE-TOPS-20261021-001` proved two things.
- **The characterization.** A law composes like cycles exactly when it is
  affine modulo the tops.
- **The matroids.** Such laws carry exactly the direct sums of matroids
  representable over finite fields.

The owner asked for a novelty check and, if the result proved novel, an
attempt to understand its utility.

**The evidence.**
- [The novelty scan](novelty_scan.md).
- [The utility proof](../../proofs/CYCLE-UTILITY-20261021-001A/CYCLE-UTILITY-20261021-001A-P001_utility/proof.md),
  with its [checks](../../proofs/CYCLE-UTILITY-20261021-001A/CYCLE-UTILITY-20261021-001A-P001_utility/result.json).

## Novelty

**`no-overlap-in-bounded-search`.** That is not a priority claim. About twenty
queries in seven families found no statement of the characterization.
- **The individual steps are classical:**
  - strong rectangularity ⇔ Mal'tsev ([Dyer and
    Richerby](https://arxiv.org/abs/1003.3879));
  - abelian ⇒ affine ([Herrmann's theorem, after Kearnes and
    Szendrei](https://arxiv.org/abs/math/9604246)).
- **The closest relatives work with single codes,** where the conclusion
  fails. [Almost affine codes and entropic
  matroids](https://arxiv.org/abs/1909.12175) carry the non-Pappus matroid at
  alphabet size 9. Linearity is known only for alphabets of size 2, 3 and
  [4](https://arxiv.org/abs/2608.20553).
- **Composition forces groups elsewhere, too,** with different hypotheses:
  - [Zaslavsky's biased expansions](https://arxiv.org/abs/math/0411268), on a
    fixed graph;
  - model-theoretic geometries.
- **What is the program's own:** the step into rectangularity (no overlapping
  circuits, then uniform fibres), and the hypothesis of closure under
  composition.

## What the result is good for

| Area | Use | Status | Evidence |
| --- | --- | --- | --- |
| Codes, entropic matroids, ideal secret sharing | **A composition test for linearity.** A code whose composition closure composes like cycles carries only matroids representable over finite fields, and with trivial tops it is a module code. The non-Pappus code has uniform fibres but fails, through an explicit three-copy system. | Proved. It reformulates the open p-entropic question but does not advance it. | Proposition 1 |
| Constraint complexity | **Tractability under constants.** A law that still composes like cycles with all constants added has a Taylor polymorphism algebra, so its constraint problem is in P. With trivial tops a genuine Mal'tsev polymorphism exists. One-in-three, not-all-equal and 3-colouring all fail. | Proved, given the dichotomy theorem. The general case is open, because constants can destroy composing like cycles. | Propositions 2 and 4 |
| Counting | **None.** The lifted Z₃ law and K₄ compose like cycles, yet counting their solutions is #P-complete. | Proved (Dyer and Richerby) | Proposition 3 |
| Matroid theory | **A description of 𝓡.** It is exactly the class of matroids carried by laws closed under composition that stay matroidal. Single codes go beyond it; closed laws never do. | Proved in AFFINE-TOPS B; here contrasted with the non-Pappus code | Proposition 1 |
| The contact-first program | **What cycle-like composition can be.** It is finite-field affine geometry modulo the tops. The program's hard substrates (one-in-three, not-all-equal, colourings) never compose like cycles. The tops hide structure that pinning a single value reveals. | Interpretation, grounded in the propositions above | Propositions 2 and 4 |

**The honest summary.**
- **The closest thing to a practical use** is the test for linearity of codes.
- **The cleanest theoretical link** is to tractability: composing like cycles
  with constants is a certificate of polynomial time.
- **Counting is outside its reach.**
- **A correction during the work.** My first sampling suggested that constants
  never break composing like cycles. That sampling mostly drew pinned, trivial
  systems. Correct sampling refutes it in parity beside J and in K₄, and the
  proof records the refutation.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| The non-Pappus failure | The novelty scan's nearest overlap, tested against the affine-tops theorem. The failure is the top lemma breaking at one pp-definable line equivalence. | New to the program; computation |
| Tractability with constants | A two-element projection quotient would create a tie that is not a bijection modulo the tops | New to the program; short, given the Taylor criterion and the dichotomy theorem |
| The counting limit | Dyer and Richerby's balance, applied to the census laws | Application of a classical theorem |
| Constants destroy composing like cycles | Correct sampling, then explicit systems | New to the program |

**Did the perspective do real work?** It did. Ties being bijections modulo the
tops is the whole argument for tractability. The top lemma's failure is what
the non-Pappus system exhibits.

**Ratio since the last checkpoint.**
- 1 artifact is substantive: the utility proof.
- 3 are administrative: the scan, this note and the ledger.

So the recommendation is substantive work.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — novelty and utility of the characterization | **Successful** | Novelty: no overlap in a bounded search. Utility: a linearity test for codes; tractability under constants; no use for counting; constants can break composing like cycles. |
| Local direction — characterizing composition like cycles | Practically complete | The characterization stands. Its utility is now mapped. |
| Broader exploration — composition (open question 3) | Known alternatives | (1) Whether composing like cycles alone implies polynomial time. (2) Conversion of the series into a reviewable note, now that the scan is clean (2/3). (3) The strong ("dressed") form of the matroid Conjecture 5 (1/3). (4) The deferred space directions (1/3). |
| Long-term goal — intrinsic structure from logic | Capability gained | Cycle-like composition is linear geometry modulo the tops. It is, at least with constants, a certificate of tractability, and the program's NP-hard substrates are exactly where it fails. |
| Next recommendation — does composing like cycles imply polynomial time? (fresh epic) | **Next step:** Continue. Two parts. (a) Cores. A law that composes like cycles and is itself a core with no nontrivial automorphisms pp-defines its constants, so Proposition 2 applies at once. The real question is whether the core of a law composing like cycles again composes like cycles; cores with automorphisms then go through the orbit relation. (b) Test laws composing like cycles that have no constant tuples (inhomogeneous and dressed laws) for Taylor cores, as a search for a counterexample. | Yes would make cycle-like composition a tractability certificate for every law. No would be a law composing like cycles whose tops hide an NP-hard problem. That would bear directly on the program's question of where hardness lives. |
| Interest — that next step | **2/3 — Promising** | Proposition 2 proves the constants case, and every known law composing like cycles is tractable. The uncertainty is real: constants can destroy composing like cycles, so tops do hide structure, and cores with nontrivial automorphisms are not covered. |
| Execution — that next step | Deferred | Not started: the owner's request covered this epic. Stop if the rigid case fails, or if no route through cores appears within one epic. The next step is the owner's decision. |
