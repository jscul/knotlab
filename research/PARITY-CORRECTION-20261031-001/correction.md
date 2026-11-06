# Parity's weighted family: decision at closure

Epic `PARITY-CORRECTION-20261031-001`, closed 2026-10-31. Program: foundations.

## The request

- **The error.** A peer session, acting on the owner's request, reported an error in `MUTUAL-SELECTION-20261031-001B`. That lane claimed
  parity's whole coupling family [1, λ, 1, λ] is "a generalized equality, affine and polynomial on every graph". Fan and Cai (2020,
  Theorem 2.2) contradict it.
- **The four tasks.**
  1. Verify that theorem's applicability and correct the parity analysis.
  2. Reassess mutual selection on parity's failing systems, keeping apart parity's decision and count, its weighted family, and
     tractability restricted to the failing systems.
  3. Correct or supersede the dependent conclusions, preserving the history.
  4. State what survives, what is withdrawn, and whether the four-place continuation keeps a justified target.

## What was found

| # | Result | Status | Evidence |
| --- | --- | --- | --- |
| 1 | The error. The Hadamard change of basis makes each line a generalized equality but each point an even-parity check, so the count is a code weight enumerator, M = Σ_{s ∈ ker N} (−1)^{b·s}(1 + λ)^{n−|s|}(1 − λ)^{|s|}, not a product of equalities. | proved; checked on 240 signed systems | A, Lemma 1 |
| 2 | Fan–Cai's Theorem 2.2 applies to M(H, 0; λ) = Holant([1, λ, 1, λ] \| =3): #P-hard for every real λ > 0, λ ≠ 1. Their gadget G4 is the theta substitution. | verified (PDF pp. 5, 8) | A, Lemma 2 |
| 3 | Theta substitution: M_par(θH; λ) = (2λ(1 + λ))ⁿ M_nae(H; λ + 1/λ − 1). In even-form variables the knot's u is the square of parity's Hadamard ratio. | proved; exact on 144 cases | A, Theorem 3 |
| 4 | Dichotomy: counting parity's coupling on connected simple cubic systems is polynomial exactly at λ ∈ {0, 1, −1, i, −i, ∞} and #P-hard at every other complex λ. | proved (from KNOT-COUPLING and PLAIN-COUNT) | A, Theorem 4 |
| 5 | Parity's failing systems carry every hard instance: a certificate avoiding the port line survives grafting, and two calls recover any count. So parity's coupling is #P-hard where parity fails, for every λ outside the six points. | proved; 72/72 end to end | B |
| 6 | Every dependent statement is located (17 places) and marked withdrawn, reason-withdrawn or surviving. | documentation | R |

## Answers to the request

1. **Applicability.**
   - Fan–Cai's problem on the incidence graph is exactly parity's plain coupling. For λ ≥ 0, their exceptions are λ = 1 (degenerate)
     and λ = 0 (affine).
   - Their proof treats [1, a, 1, a] explicitly, through G4.
   - Their graphs may have parallel edges. Our dichotomy covers simple systems without that caveat, and extends to complex λ.
2. **Mutual selection, three readings.**
   - **Decision and count.** Parity's decision and solution count are polynomial (Gaussian elimination), so parity fails (M2). This was
     never in doubt.
   - **The weighted family.** It is #P-hard except at six points. The scan's reason ("the whole family is easy, so selection is vacuous")
     is false.
   - **Restricted to the failing systems.** The family stays #P-hard there (B). So parity's failures make nothing easy, and the verdict
     "parity has no mutual selection" survives with a correct reason.
3. **Dependents.**
   - Withdrawn: the family claim in lane B's report, docstring and manifest.
   - Reason withdrawn, conclusion kept: the lane B ticket, the scan's status, decision note and ledger, PINNING C's table entry and its
     dependency bullet.
   - Surviving: PINNING D002, PINNING C's table row on solution counts, the knot-intuition conclusions.
   - Ticket R has the full table. A dated note is added to the knot-intuition document.
4. **What survives, and the continuation.**
   - The uniqueness theorem (PINNING C) stands as stated. Under the broader reading the knot is still the only law with mutual selection,
     now with a proof for parity.
   - All knot results are unaffected: the coupling dichotomy, the counting note, the pinning theorem, the five classes.
   - The four-place continuation keeps its target, with two guards:
     - never infer an easy family from a one-sided transform;
     - test whether each candidate's failures are local, since local failures cannot select.

## Reading

- **Failures that select are global.** The knot's recognisable failures constrain the whole space: a connected system fails exactly
  when its plain signing is Pfaffian, and that makes the dimer law a determinant. Parity's recognisable failures are local: a certificate
  lives in a small piece and survives any host, so the failing class contains every hard instance. This sharpens mutual selection
  without changing which law has it.
- **The two families are one.** Through the theta substitution the knot's coupling sits inside parity's, and their even forms are
  related by squaring. Parity's decision is easy because it is linear algebra. Its weighting is as hard as the knot's.
- **In the owner's terms.** The error came from transforming one side of a two-sided relation. A basis change acts on every incidence
  at once.

## Literature (checked 2026-10-31)

- **Fan and Cai (2020, arXiv 2011.09110).** Holant(f | =3) for nonnegative symmetric ternary f. Theorem 2.2; [1, a, 1, a] is in
  Lemma 4.2, case 3.
- **Cai, Fan and Liu (2021, arXiv 2110.01173).** Integer and rational values, mixed signs.
- **The complex case.** Neither abstract covers complex values. For this family it follows here from the knot's coupling dichotomy.
  Folklore risk is moderate.
- **The splice and interpolation (B).** Standard.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — correcting the parity analysis | **Status:** Successful | The false claim is withdrawn; parity's family is classified over C; its failing class is proved hard; the uniqueness theorem stands. |
| Local direction — mutual selection at three places | Complete | The only open item is lane B's sketch for other laws on parity's failing systems. It is low value, since B already shows those systems carry no structure. |
| Broader exploration — the two/three boundary | Known alternatives | (a) value-free four-place laws (approved by the owner); (b) rigidity of the knot's pieces at every size; (c) a short note on native selection. |
| Long-term goal — the two/three boundary as emergence | Capability gained | A sharper criterion: recognisable failures select back only when global. Also a native link: the knot's coupling sits inside parity's. Missing bridge: whether any arity other than three has a law with global, recognisable failures and a hard count. |
| Next recommendation — value-free laws on four places | **Next step:** Continue. A fresh epic depending on PINNING and this correction: classify the value-free four-place knots on signed 4-regular systems by failures, recognisability (with the locality test) and count. | First discriminator: a census of failures on small 4-regular 4-uniform systems, a graft test for locality, and a search for equality-building pieces. Stop when every value-free four-place knot is shown never to fail, to fail locally, or to have coNP-hard failures (then three is special), or when one has global, recognisable failures with a hard count (then it is not). |
| Interest — that recommendation | **2/3 — Promising** | It bears directly on the two/three thesis. The main uncertainty is whether signed four-place laws admit Pfaffian-like global failures at all. |
| Execution — that action | Approved by the owner before the correction; resumes now | Bounded by the four-place catalogue (30 value-free knots, 4 classes). |
