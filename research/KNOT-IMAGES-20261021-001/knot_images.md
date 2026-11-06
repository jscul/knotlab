# Can a knot overlap at the top, and must Latin knots be groups?

Epic `KNOT-IMAGES-20261021-001`, closed 2026-10-21.

## The question

`CYCLE-TOPS-20261021-001` proved the top lemma. It showed that, at each
variable, a knot's top image is functional or overlapping. The owner approved
a fresh epic with two steps:
- try to show that knot top images are functional (Latin hypercubes of the
  tops);
- test whether elimination forces Latin knots to be group-like (Reidemeister),
  which would give a Mal'tsev operation on knot tops.

**The evidence.**
- [The census](../../experiments/KNOT-IMAGES-20261021-001A/KNOT-IMAGES-20261021-001A-E001_latin_census/contract.json),
  with [result](../../artifacts/KNOT-IMAGES-20261021-001A/KNOT-IMAGES-20261021-001A-E001_latin_census/result.json).
- [The proof](../../proofs/KNOT-IMAGES-20261021-001B/KNOT-IMAGES-20261021-001B-P001_latin_circuits/proof.md).
- **Literature.**
  - Reidemeister's closure condition characterizes group isotopes
    ([Encyclopedia of Mathematics](https://encyclopediaofmath.org/wiki/Closure_condition)).
  - [Zaslavsky's biased expansions](https://arxiv.org/abs/math/0411268) shows
    that over 3-connected graphs every multiary quasigroup is a group in
    disguise.

## What was found

- **Latin circuits compose like cycles.** Suppose every circuit is functional
  modulo common proper pp-definable equivalences. Then the law composes like
  cycles.
  - So composing like cycles with no overlapping circuit is the same as having
    Latin circuits modulo the tops.
  - Only one question is left for the characterization: can a circuit overlap?
    The **Latin conjecture** says it cannot.
- **Every overlapping candidate failed.** These include:
  - the equality indicator y = [a ≠ b];
  - e = x + yH over Z₅ and Z₇.

  All 65,159 knot top images in the surviving laws were functional.
- **Latin squares.**
  - **Reidemeister.** A 2×2 subsquare's relation is functional exactly when
    the square is a group isotope.
  - **Non-group squares.** Their 4-cycle circuits are therefore not Latin.
    Every non-group square tested failed (seven on a 2×2 subsquare with a
    shared diagonal label) or collapsed its tops (one of order 6).
  - **Where they fail.** Only once labels were shared. With distinct labels,
    the order-5 non-group square even gives the graphic matroid on K₃,₃.
- **Abelian 3-nets.** The 3-net law of a finite abelian group composes like
  cycles exactly when the group is a p-group. Such laws carry
  GF(p)-representable matroids.
  - **The proof.** The polymorphisms are the End(G)-affine maps, and a unique
    maximal proper fully invariant subgroup exists exactly for p-groups.
  - **The census agrees.** It found the predicted tops for Z₄, Z₈ and Z₂×Z₄,
    and a collapse for Z₆.
- **Non-abelian groups.** Suppose the elements with u^m = 1 generate the group
  without exhausting it. Then its 3-net fails, which covers S₃, D₄ and Z₆.
- **Q₈ separates the two conjectures.**
  - Q₈'s only involution is −1, so the obstruction above does not apply.
  - Its 3-net survived the census with top Q₈/{±1} ≅ Z₂ × Z₂, and every knot
    image was Latin.
  - **But it has no polymorphism Mal'tsev modulo ±1.** The candidate on the
    tops is forced to be x + y + z, and its lifts reduce to sign equations over
    F₂. An explicit certificate of 416 of those equations is inconsistent.
  - **The consequence.** Either Q₈'s 3-net fails elimination in systems larger
    than any sampled, or the tops proof's Conjecture 7 (Mal'tsev on knot tops)
    is false. In the second case the Latin conjecture survives, and composing
    like cycles is strictly weaker than having a Mal'tsev operation on the tops.
  - **Scoping after the census (not evidence).** About 3,700 more Q₈ systems
    of up to 12 variables showed no failure. All 1,412 top images small enough
    to test were affine, consistent with the certificate needing a large
    configuration.
- **The census signal was false,** and only because of Q₈. Its frozen search
  timed out at 1,200 seconds (H5), and the proof then showed that no such
  operation exists. Every other prediction and every control held.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Latin circuits compose like cycles | Reversing the tops proof's dichotomy: a common equivalence makes fibres disjoint | New to the program; short |
| Reidemeister link | The 2×2 subsquare relation, read as a circuit | Classical theorem, restated |
| Abelian 3-nets compose like cycles exactly for p-groups | The circuits proof's Theorem 1 plus End(G)-affine polymorphisms and fully invariant subgroups | New to the program; an expert would derive it quickly |
| Small-element obstruction | The m-cycle gadget and Lemma 1 of the tops proof | New to the program |
| Q₈ has no Mal'tsev operation on its tops | Lifting x + y + z through the sign cocycle, decided over F₂ | New to the program |
| Non-group squares fail only with shared labels | Census A and scoping | Observation |

**Did the perspective do real work?** It did.
- **The program's own notions.** Range-relative circuits and the tops proof's
  dichotomy turned "is composing like cycles a Mal'tsev condition?" into a
  question about Latin circuits.
- **Classical tools did the rest.** Reidemeister's theorem, fully invariant
  subgroups, and the sign cocycle of Q₈.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the census and the proof.
- 2 are administrative: this note and the ledger.

The recommendation is therefore substantive work.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — knot top images | **Partially successful** | Proved: Latin circuits compose like cycles, the Reidemeister link, the abelian 3-net classification, the small-element obstruction, and that Q₈'s 3-net is not Mal'tsev on its tops. Open: the Latin conjecture, and whether Q₈'s 3-net composes like cycles. |
| Local direction — characterizing composition like cycles | Continue | The two candidate characterizations (Latin circuits; Mal'tsev on knot tops) now differ exactly on one explicit law. |
| Broader exploration — composition (open question 3) | Known alternatives | (1) The Q₈ question. (2) The Latin conjecture in general. (3) The three-value diagonal question (1/3). (4) The deferred space directions. (5) A write-up of the composition series once the characterization is settled. |
| Long-term goal — intrinsic structure from logic | Capability gained | For 3-nets the answer is now sharp: abelian p-groups compose like cycles, non-groups and groups generated by small elements do not, and Q₈ sits on the boundary. |
| Next recommendation — does the 3-net of Q₈ compose like cycles? (fresh epic) | **Next step:** Continue. Q₈'s 3-net is the Z₂² 3-net with a sign layer twisted by the cocycle f(a, b) = a₁b₁ + a₂b₂ + a₂b₁. Build the pp-definable relation behind the 416-equation certificate, whose top image cannot be affine, and test elimination and the Latin property in systems built from it. Then attempt a proof through Theorem 1: are all its circuits functional modulo ±1? | Yes refutes Conjecture 7: composing like cycles would mean Latin circuits, not Mal'tsev operations. No would locate the failure in a large configuration and support Mal'tsev on knot tops. |
| Interest — that next step | **3/3 — Hot** | One explicit 8-element law decides between the two characterizations. Its non-Mal'tsev property is proved, and it has survived about 4,000 systems. The uncertainty is that a proof of composition like cycles for it may need new structure. |
| Execution — that next step | Deferred | Not started: the owner's request covered this epic. Stop if the certificate's relation yields an elimination failure (then Conjecture 7 survives), or if a proof attempt stalls after one epic. The next step is the owner's decision. |
