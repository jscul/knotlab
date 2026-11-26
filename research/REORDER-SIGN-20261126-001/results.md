# The sign as the cost of reordering

> **Referee report R1 and a frozen confirmation, 26 November 2026: the numbers stand; two readings are narrowed.** The
> [referee](referee-R1/codex/report.md) rebuilt all five claims with its own code (confirmed with fixes), and
> [the confirmation](../REORDER-CONFIRM-20261126-001/results.md) (frozen, every prediction held) tested the account at three
> to six readers. Read this record with these changes.
> - **"An even order" is the three-reader case.** The contradiction appears exactly when the commit order is one of the n
>   cyclic shifts of the parents' creation order (3 of 6, 4 of 24, 5 of 120, 6 of 720); at three readers the shifts are the
>   even orders, at four two of them are odd. First created, first born is exact at every size checked.
> - **The reference is supplied, not free.** The parents' creation order acts only through the start's relative signs, which
>   the parity rule does not fix, and the commit order must match it; "the reference that reading R1 had to supply is not
>   extra … every history already has" is withdrawn. Under the swap rule the sign is a property of the supplied schedule of
>   creations and births, read against real readings held fixed: with a complex flip the other schedules carry it.
> - **Why P7 failed.** A commit order is an order of operations: two births commute up to −1 exactly when both parents hold 1.
>   The listing is a convention; the commit order is not. The P7 convention matches the sequential births on fresh inputs
>   only; its tables do not single out a birth operator elsewhere.
> - **Smaller fixes.** The F1 flip's *primed* factor sits on the old distinction (both factors are odd); with the child's pair
>   written in the other order the other flip works. "Orders unknown to the readers give 7/6" holds for the fixed readings:
>   with other real readings the mixtures score above 2 (at least 168/(25√10) and 308/(25√37)), without the full
>   contradiction. The coherent sum's surviving word is the parents' word 000, with eight completions. The births mix fermion
>   parity, so they are not local operations of physical fermions.

**With one added rule, that swapping the order of two distinctions that both hold 1 costs −1, a growth round's own commit order
supplies the sign of the three-detector experiment, and the reference it is measured against is the parents' own creation
order.** Read with the two real readings, the grown parity knot carries the full contradiction exactly when its children are
committed in an even order relative to the order their parents were created; committed first-created-first-served, it gives
all 64 outcome probabilities exactly. This needs the readers' flip to be the real flip whose odd factor sits on the reader's old
distinction; with the other real flip no order carries it. The finding came after the frozen prediction P7 failed and is
exploratory. [Design frozen before the code](preregistration.md) · [Signed benchmark](../WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/results.md)

The rule is the literature's exchange sign of fermions (Jordan and Wigner, 1928), and a swap of two adjacent distinctions under
it is the same as one CZ per crossing, so nothing here separates exchange statistics from that. What the program adds is the
link to its own growth: the law already leaves a round's commit order free, and the sign the experiment needs is the cost of
that order.

## What the frozen predictions found

| # | Prediction | Result |
| --- | --- | --- |
| G | Gate | **Held.** A direct count of inverted pairs over every listing equals the block formula on every word of fixtures with up to 4,096 grown words and on 256 words sampled with seed 20261126 beyond, for every order up to 720 and 120 sampled orders at seven knots. `+---` with X and `++++` with Y each give 64/64. The s = +1 mutant gives 44/64 (scored win 5/8). |
| P1 | Reversal sign is a quarter turn per occupied distinction, n = 3 to 8 | **Held** at every n, with the full contradiction. |
| P2 | At n = 4 to 6 the contradiction comes from exactly the n orders that reverse a prefix and its suffix separately, not from odd orders | **Held.** 4 of 24, 5 of 120, 6 of 720 orders. The full reversal carries it at n = 4 and 5 though it is even there; a single swap does not. Parity predicts exactly only at n = 3. Every carrying order has a nonvanishing polar form, but the form alone does not decide it: at n = 4, 20 of 24 orders have one and 4 carry the contradiction. The s = +1 control carries it nowhere. |
| P3 | Grown ternary with block readers, relative to the production listing | **Held.** The three odd orders give ⟨ZZZ⟩⟨XXZ⟩⟨XZX⟩⟨ZXX⟩ = −1; the reversal matches the target exactly and the two single swaps up to relabelling. Even orders give mixed correlations 0. Under every one of the six reference listings, the orders carrying it are exactly those odd relative to it. Reading the old distinction alone gives 5/8, and s = +1 gives 5/8 in every order. |
| P4 | Orders unknown to the readers | **Held.** Mermin score 4/3 over the odd orders and 7/6 over all six, against the local bound 2 and the quantum 4. |
| P5 | Orders not recorded: the coherent sum | **Held.** Only words with at most one odd child survive. On the ternary only the blank word survives, so the knot is lost; weighting the orders by their sign leaves three of the four words, so it is lost too. s = +1 keeps every word. |
| P6 | Readers' records born in the same round | **Held.** Every order gives the positive class (mixed correlations 0). |
| P7 | Rule applied to the readings too: order becomes gauge | **Failed.** The tables differ across orders. |

The rings of four-place knots carry relative signs that no relabelling removes in almost every order: 20 of 24 orders at three
knots, 115 of 120 at five, 5,033 of 5,040 at seven, with 6, 24 and 720 distinct polar forms. Under the coherent sum 8 of 64,
64 of 1,024 and 256 of 16,384 old words survive (counting allowed words equally; seven knots by the closed formula, which brute
force confirms at three and five). The two ternaries sharing two distinctions carry
none, and the three-ternary ring has no fresh distinctions to order. [Exact receipt](../../artifacts/REORDER-SIGN-20261126-001/REORDER-SIGN-20261126-001-E001_reorder_signs/results.json)

## Why P7 failed, and what replaced the reference

The frozen check of P7 represented the readings with their ordering strings in a listing that puts the earliest-created
distinction first. A births-in-sequence model acts the other way: each later birth multiplies on the left. An independent
calculation built the nine-distinction system as fermionic operators (Fock space of dimension 512, Jordan–Wigner matrices,
nothing shared with the main checker). The start is the positive parity knot, its parents created in a stated order; each birth
is the operator that creates the child's fresh pair with the parity of its parent, applied in commit order; readers use the
ordinary reading (−1)^n and one of the two real Hermitian pair flips, F1 = −iγ′_x γ_y or F2 = iγ_x γ′_y (γ = c + c†,
γ′ = i(c† − c)). Both flips are local even operators on the reader's own distinctions, and they commute across readers.
[Independent check](verify_fock.py) · [Its output](verify_fock.json)

| Parents created | Flip | Orders with the full contradiction | Exact 64/64 with fixed labels |
| --- | --- | --- | --- |
| c, b, a | F1 | acb, bac, cba: exactly the even orders relative to the parents | cba |
| a, b, c | F1 | abc, bca, cab: exactly the even orders relative to the parents | abc |
| either | F2 | none | none |

In both cases the exact table comes from committing the children in the order their parents were created. With orders unknown
to the readers the best Mermin score is 7/6; with the order not recorded only the blank word survives. The frozen check's P7
convention corresponds to births that carry a string over all earlier distinctions, which are not local to the parent; its
"even orders relative to production" is the same statement with the listing reversed. Either way order is not gauge: the
advisor's prediction, adopted as P7, is refuted.

So the reference that reading R1 had to supply is not extra. In the fermionic reading it is the order in which the parents were
created, which every history already has. What remains supplied is the rule s = −1, the block readers, the choice of F1 over F2,
squared weights, and a commit order of the right class, which the growth law leaves free.

## Reproduce

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
a=artifacts/REORDER-SIGN-20261126-001/REORDER-SIGN-20261126-001-E001_reorder_signs
.venv/bin/python -B "$a/check.py" --check
.venv/bin/python -B research/REORDER-SIGN-20261126-001/verify_fock.py
```

The main check takes about 8 seconds and the Fock check about 4. The s = +1 control of the coherent sum was misreported in the
first run (the closed formula of s = −1 was applied to it); it was fixed before this record and the receipt regenerated.

## Research position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the sign as the cost of reordering | **Status: Partially successful** | The growth's own commit order, measured against its parents' creation order, carries the sign with the dressed real flip; exact for first-created-first-served. Post hoc, after P7 failed. |
| Local direction: order as the source of the sign | Continue, as a frozen confirmation | The F1/F2 split and the parents' order were found after the freeze; one size past and a second growth round are untested. |
| Broader exploration: native phase | Known alternatives | The swap rule is one CZ per crossing; parity superselection makes the odd local births a modelling choice; R1b, R2 and R3 give no contradiction. |
| G5 Dynamics, G9 Witnesses | Capability gained, conditionally | One added rule makes a round's free order carry the sign, with no reader-supplied reference. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Freeze and confirm: parents' order as the reference | 2/3 — Substantial | 3/3 — Ready | Pre-register "even relative order with F1 carries the contradiction; FIFO is exact" for four readers and a second growth round, then replay in the Fock model → stop at a pass or a counterexample | Proposed |
| 2 | What fixes the commit order | 3/3 — Barrier | 1/3 — Stated | Ask whether any native record of the program selects the FIFO class → stop when one is found or the record has none | Alternative · deferred |
| 3 | Must a knot be built from two-sided pieces? | 2/3 — Substantial | 2/3 — Testable | The owner's ruling on the hidden distinction as a hub | Needs the owner's call |

**Corrections:** One, logged before the freeze: the idle-exchange study fixed z² = i and did not leave +1 and −1 (Narrowing).
P7's failure is a failed prediction, not a correction.

**Goals:** G5 Dynamics and G9 Witnesses.

**Assumptions:** A275 (the swap rule) and A276 (the block readers and the F1 flip) are added as scaffolds; squared weights stay
A144. Independent referee pending.

**Scaffolds:** The rule (control s = +1), the reference listing (all six orders), the readers (block against old distinction
alone), the flip (F1 against F2), the parents' creation order (both directions), outcome relabellings.
