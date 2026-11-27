# Tables under the recorded transfer law: what stands (as computed; referee pending)

Epic `TRANSFER-TABLES-20261126-001` (at the coordinator's go-ahead after the factoring study's referees), closed 26
November 2026. Computed; advisor consulted before the freeze; every frozen prediction held; refereed (R1, below).
[The note](README.md) · [preregistration](preregistration.md) · [advisor's question](advisor_question.md) and
[answer](advisor_answer.md)

> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, no Block.** Rebuilt: 13 reached states, 30
> splits, a knot in the whole joining every split, the model's reads peaking at exactly 2 under every registered
> counting, and 1 + √2 and ≈ 2.2159 with supplied coherence and rotated reads. **Narrowings:** "every counting" means
> each registered counting: a supplied positive weighting on the same 13 states gives the model's reads 67/31 ≈ 2.16;
> freely changing a read never signals, but changing the founder's preparation changes the far pair with certainty;
> correlation alone is not contact (two fresh distinctions under the minimum lift are correlated and share no knot), so
> the decision's intuition is too strong; "half the weight" is 1/2 under the start counting and 5/13 when every reached
> state counts once; the failing control's nine-distinction cap applied at the finish, and no sampled start qualified.
> **Not a block:** six splits per counting print zero for an empty value-read search; the code header's name for the
> 13-state counting. Logged in `docs/CORRECTIONS.md`.

## What stands

1. Under the transfer law, value reads never exceed 2 and never signal (entailed, checked).
2. With the model's reads (values, changes, combined products) on the coherent version, no table exceeds 2 on any of the
   30 splits, under either lift and every counting.
3. With rotated reads on the coherent version (both supplied), 15 splits exceed 2, up to 1 + √2 ≈ 2.414, quantum and
   without signalling; the minimum lift and the record's finish counting give none.
4. Every split is joined by a knot in the whole of the reached states: the readers whom no listed law joins are not
   separated in the program's sense.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a table above the classical limit under the transfer law | **Status:** Successful (a negative with its reason) | None with the model's reads; with supplied coherence and rotated reads, only between readers a knot in the whole joins |
| Local direction — the transfer law as a source of separated tables | **STOP** (obstruction learned) | Its non-factoring is over knots it makes, which join the readers |
| Long-term goal — G18 Comparing growth laws | Obstruction learned | The quantum line rests, as the coordinator said |

**Next step:** Research directions — the line rests until the owner and the coordinator take stock

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The divide-weight-over-several-births law (waits for the owner) | 2/3 | 2/3 | the owner's go | Waiting |
| 2 | The transfer law at more founders and rounds | 1/3 — more of the same kind | 3/3 | — | Proposed |

**Intuition (an exact link, not evidence).** A law that reads values as it grows makes its own correlations into new
relations among the distinctions it touched; here those relations are knots in the whole, so the readers it ties are
no longer separated *(R1: correlation alone is not contact; under the minimum lift two correlated fresh distinctions share
no knot)*.

**Corrections:** none in this study.
**Goals:** checkpoint row added (G18; obstruction learned).
**Assumptions:** A305 entered (scaffold: the declared start weighting, the coherent version, rotated reads, one founder).
**Scaffolds:** the start weighting (declared), the coherent version and rotated reads (supplied), the splits, one founder
and round; the no-excess-with-the-model's-reads result holds under every counting and lift.
**Advisor:** consulted before the freeze (its by-hand values were frozen and all held; it found the readers joined in the
whole and four code faults, fixed before the run).
