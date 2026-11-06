# Does the 3-net of Q₈ compose like cycles?

Epic `THOMSEN-KNOTS-20261021-001`, closed 2026-10-21.

## The question

`KNOT-IMAGES-20261021-001` left one law deciding between two characterizations
of composing like cycles.
- **The law.** The 3-net law of the quaternion group Q₈ survived its census
  with Latin knot images.
- **The obstruction.** A 416-equation certificate showed that no polymorphism of
  that law is Mal'tsev modulo its top, ±1.
- **The dichotomy.** Either the law fails in systems larger than any sampled,
  or Conjecture 7 of the tops proof (Mal'tsev on knot tops) is false.

The owner approved deciding it. The plan was to build the relation behind the
certificate, test elimination and the Latin property on systems built from it,
and then attempt a proof through the Latin-circuits theorem.

**The evidence.**
- [The proof](../../proofs/THOMSEN-KNOTS-20261021-001A/THOMSEN-KNOTS-20261021-001A-P001_no_overlap/proof.md),
  with its [checks](../../proofs/THOMSEN-KNOTS-20261021-001A/THOMSEN-KNOTS-20261021-001A-P001_no_overlap/result.json).
- **Literature.** Thomsen's closure condition characterizes the quasigroups
  isotopic to abelian groups. See the [Encyclopedia of Mathematics entry on
  closure conditions](https://encyclopediaofmath.org/wiki/Closure_condition).

## What was found

- **The relation behind the certificate is Thomsen's configuration.**
  - For a group it says that x₂⁻¹x₁ and x₃⁻¹x₁ commute.
  - Over Q₈ its top image is ω(c₁ + c₂, c₁ + c₃) = 0, where ω is the
    symplectic form on F₂². That relation is not affine.
  - Three of its tuples replace the 416 equations.
- **Q₈'s 3-net does not compose like cycles.**
  - The configuration T is a knot, and it allows x₂ = x₁ for every x₃. So its
    fibres overlap.
  - Two copies, T(x₁, x₂, x₃) ∧ T(x₁, x₂, x₃′), violate elimination: dropping
    x₁ (or x₂) leaves {x₂, x₃, x₃′} free.
  - The failing system has 16 variables and 12 atoms. The census sampled at
    most six atoms and eight variables.
- **No circuit overlaps in any law that composes like cycles.**
  - Doubling an overlapping knot and applying elimination produces a circuit
    on which e′ = e is always allowed. Two copies of that circuit fail.
  - So the Latin conjecture is true: modulo the tops, every circuit is a Latin
    hypercube.
  - Composing like cycles is therefore exactly having Latin circuits modulo
    some proper pp-definable equivalences.
- **Which 3-nets compose like cycles.** Exactly the isotopes of abelian
  p-groups.
  - Every non-abelian group fails through T.
  - Non-group squares fail through T. When T is full, they fail through its
    four-variable form T′, with one column visible; this happened for 23 of 60
    random squares of order 6.
- **Conjecture 7 survives.** No law is known that composes like cycles without
  a Mal'tsev operation on its knot tops.

## Provenance

| Result | Where the idea came from | Novelty |
| --- | --- | --- |
| Thomsen's configuration is behind the certificate | The certificate's obstruction is the commutator form ω of Q₈'s sign cocycle, and Thomsen's configuration defines commuting differences | Classical configuration; its role here is new to the program |
| Q₈'s 3-net fails | Thomsen's configuration contains every tuple with two equal rows, a selector in the converse proof's sense | New to the program |
| No circuit overlaps (the Latin conjecture) | Generalizing the Q₈ failure: in two copies of an overlapping knot, elimination produces a circuit with a selector | New to the program; elementary |
| Which 3-nets compose like cycles | The no-overlap theorem, Thomsen's theorem and the images proof's abelian classification | New to the program; built on classical closure theory |

**Did the perspective do real work?** It did.
- **The program's own notions.** Range-relative circuits, the tops, and the
  converse proof's selector lemma carry every step.
- **Classical input.** Thomsen's theorem enters only to name the surviving
  3-nets.
- **Folklore risk.** "Latin circuits modulo the tops" resembles abelian
  structure in universal algebra, which a literature check should compare
  before any write-up.

**Ratio since the last checkpoint.**
- 1 artifact is substantive: the proof.
- 2 are administrative: this note and the ledger.

The recommendation is therefore substantive work.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — does Q₈'s 3-net compose like cycles? | **Successful** | Decided: no, through an explicit 16-variable system. Also proved: no circuit overlaps (the Latin conjecture), the characterization by Latin circuits, and which 3-nets compose like cycles. Open: Conjecture 7. |
| Local direction — characterizing composition like cycles | Continue | Composing like cycles is now exactly Latin circuits modulo the tops. The open question is whether that forces a Mal'tsev operation there (Conjecture 7). |
| Broader exploration — composition (open question 3) | Known alternatives | (1) Mal'tsev structure on the tops. (2) A write-up of the composition series, from the circuits proof to this one. (3) The three-value diagonal question (1/3). (4) The deferred space directions. |
| Long-term goal — intrinsic structure from logic | Capability gained | Composing like cycles has an intrinsic description: every circuit, read modulo the tops, is a multiary quasigroup. For 3-nets that pins the laws to abelian p-groups. |
| Next recommendation — Mal'tsev structure on the tops (fresh epic) | **Next step:** Continue. In a law that composes like cycles, every three-variable circuit's top image should be isotopic to an abelian p-group: the 3-net law of that image is a law of top images, so Theorem 4 applies. That argument was sketched in scoping and is not yet checked. Then show that knots through one range induce the same parallelogram operation (the tops proof's Lemma 1, applied to the relation comparing two of them). Extend to circuits of four or more variables, and test whether every top image is closed under that operation. | Yes would prove Conjecture 7 for the top images and describe composing like cycles as abelian structure modulo the tops. A counterexample would be a law with Latin circuits modulo its tops whose top images have no common Mal'tsev operation. |
| Interest — that next step | **3/3 — Hot** | The Latin characterization and the 3-net classification make the abelian structure concrete, and no candidate counterexample remains. The uncertainty is gluing: different circuits through one range must induce compatible operations. Lifting to a polymorphism of the original law, as Conjecture 7 is stated, may need more than the top images. |
| Execution — that next step | Deferred | Not started: the owner's request covered this epic. Stop if gluing fails on an explicit law (that law becomes the subject), or if the attempt stalls after one epic. The next step is the owner's decision. |
