# Tables under the recorded transfer law for readers whom no listed law joins

Epic `TRANSFER-TABLES-20261126-001`, at the coordinator's go-ahead after the factoring study's referees found that the
transfer law of the ring-to-end study (`RING-TO-END-20261119-001`, a rival law that reads values as it grows: a newborn
on an odd input takes one of its fresh pair, on an even input both if its parent holds another occupied distinction and
none if the parent is quiet) makes a weighting that does not factor over its listed laws. The question: for freely set
readers whom no listed law joins, does any table exceed the classical limit, and does any signal? Computed; the advisor
consulted read-only in the repository ([question](advisor_question.md), [answer](advisor_answer.md)); **refereed (R1, below).** Every frozen prediction held ([preregistration](preregistration.md)).

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

## Setting ([`tables.py`](tables.py), [output](tables_out.jsonl.gz))

One founder (a three-place even knot), one round: 13 reached states, four listed laws (012, 034, 156, 278), and 30
splits into two readers and one or two unread distinctions such that no listed law meets both readers. Two lift rules:
the minimum lift, and the pair lift (the two pair modes are one rule here). Three countings: the start counting (starts
and lifts equally weighted, which the law does not prescribe: declared), every reached state once, and the record's
finish counting (every allowed word of the four laws once, which ignores the transfer).

## Results

| Lift, counting | Value reads, largest CHSH | Coherent version: entangled splits | Any reads, largest | The model's reads, largest |
|---|---:|---:|---:|---:|
| minimum, start | 2 | 0 of 30 | 2 | 2 |
| minimum, every reached state once | 2 | 0 of 30 | 2 | 2 |
| pair, start | 2 | 15 of 30 | **1 + √2 ≈ 2.4142** | 2 |
| pair, every reached state once | 2 | 15 of 30 | **≈ 2.2159** | 2 |
| pair, the record's finish counting (32 words) | 2 | 0 of 30 | 2 | 2 |

- **Value reads never exceed 2 and never signal**, under every lift and counting: the reached word is a list of values
  (entailed; checked on every split).
- **The coherent version** (the reached states related with equal phases, amplitude the square root of the weight;
  supplied) is entangled across 15 splits under the pair lift. **With any reads** it reaches 1 + √2 ≈ 2.414 (start
  counting) or 2.216 (every reached state once): above the classical 2, below the quantum limit 2√2, and quantum, so it
  signals nothing. **With the model's reads** (values, changes and their combined products) it never exceeds 2.
- Where the excess comes from: on the split with distinction 2 unread, half the weight is a pure state in which the
  ring reader's quiet start goes with 00 at the far pair and its active start with 11, and both readers can tell which
  half they are in (each holds the value of distinction 2 as a parity of its own). The far pair's lift reads the parent.
- **Controls.** A two-place even law read by the two readers it joins: any reads 2√2, the model's reads 2. Three words
  00, 01, 10 equally weighted: the model's reads 7/3, any reads 2√13/3 ≈ 2.404 (so the model's-reads test can exceed).
  The factoring study's failing control (dividing over the whole growth at once): no sampled start with at most nine
  distinctions fails, so it **did not exercise the test**.

## But the readers are joined in the whole ([`whole_knots.py`](whole_knots.py), [output](whole_knots_out.jsonl.gz))

On the 13 reached states, many sets of three distinctions pass the canonical test (constrained, every part free,
allowed), one of them confirmed with the repository's checker; **every one of the 30 splits is joined by such a knot in
the whole**. The transfer law's weighting factors over these knots, as the advisor showed by hand. So the readers whom
no listed law joins are joined by knots the law itself makes.

## So

Under the recorded transfer law no table exceeds the classical limit with the model's reads (values, changes, combined
products), under either lift, any counting, any split. An excess appears only with two supplied pieces, the coherent
version and rotated reads, and then between readers whom a knot in the whole joins. Nothing signals. The answer is the
same under the declared start counting and under every reached state once (the counting is a scaffold here only for the
size of the excess), and the minimum lift and the record's finish counting give none: it comes from the transfer law's
reading of values together with the supplied coherence and reads. The other knot rule could not be tested: the pair
transfer is defined for parity only (the nearest not-all-equal law that reads values, register entry A210's, is not a
transfer).

## What this does not say

- More founders, more rounds (a second round changes the structure by values), or other value-reading laws.
- That the coherent version is the model's: it is supplied, as are the rotated reads and the start weighting.

## Scaffolds

The declared start weighting; the coherent version (equal phases); rotated reads; the reader splits; one founder and
one round. The "no excess with the model's reads" result held under each counting and lift; the excess with any reads is
about the supplied coherence and reads.
