# The advisor's answer (26 November 2026), read-only in the repository

# Advisor answer: `SIGNED-COUNT-20261126-001`

Your conclusion (the signed form shows a reader nothing the counts do not) survives, but two of the four points fail as worded and the example cannot support any of them. I had no shell, so everything below is either read from the files or worked by hand; each item says which.

## What I found in the files (checked by reading)

- **The split 288 − 162 is made by the code, not by the structure.** `signed.py` lines 21–24 keep the constant `1` and the empty-subset term `−2^(1−k)` as two separate terms on the same empty set.
  - Merged, a three-place knot is 3/4 − (1/4)(three pair products) and a four-place knot is 7/8 − (1/8)(…).
  - Distinctions 3, 4, 5, 6, 7 each sit in one knot only, so every non-constant choice vanishes. The count is then one positive term, 256·(7/8)(3/4)(3/4) = 126, with no negative part.
  - The same holds at the other settings: 512·(7/8)(3/4)(7/8) = 294 and 1024·(7/8)(7/8)(7/8) = 686.
  - So the positive and negative parts are not functions of the structure. This is the strongest form of your point (1), and it means the file shows no cancellation at all.
- **The example has no loop.** The start `((0,1,2,7),(0,3,4),(1,5,6))` has no cycle of shared distinctions, so the loop expansion has only its trivial term. "The product" is a single term, (−1/8)(−1/4)(−1/4)·256 = −2, matching the file's "positive part 0".
- **Point (3) is false as worded.** The record has readings that square a signed sum over unread distinctions:
  - `SIDE-SIGN-20261126-001/sides.py` lines 281–285, reading R2 (README lines 149–150: "every unread distinction summed before squaring").
  - `WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001/verify_laws.py` lines 94 and 115. Its `results.md` line 38 has two source words giving 1 + 1 (chance 1/4) or 1 − 1 (chance 0); line 62 has an untouched reader's chance moving with the other settings under two of three prescriptions.
  - Scoped to "under the count weighting" the point is true, but only by definition.
- **Lemma 2 has no reader.** In the proof (`proofs/THREEFOLD-AMPLITUDE-20261030-001C/.../proof.md`, not under `research/`), the signed ε_e(y) enter only R(L), inside an identity between counts, and R(L) = 0 in the non-colourable case. Its nonclaims say "The complex weight is used only to count." I found no place where the coefficients enter a statistic; I read that one file only.
- **`signed.py` cites a `README.md` that is not in the study folder.** The folder holds only `signed.py`, `signed_out.jsonl` and `advisor_question.md`.

## 1. Counterexamples (by hand, unverified)

- **Points (1) and (2) are tautologies inside the count weighting.** A referee will press that first. They cannot fail, and they say nothing about whether a far dependence exists.
- **A far dependence does exist under the count weighting.** Take a ring of four three-place knots:
  - A = (0, 1, a), M1 = (0, 2, m), M2 = (1, 3, m′), B = (2, 3, b), with a, m, m′, b loose.
  - A and B share no distinction.
  - Alice's own statistic is the mean of s0·s1, both held by her knot.
  - With no edit: N = 82 (checked two ways by hand) and the mean is −30/82 = −15/41.
  - With Bob's edit (one more loose distinction on B): N = 190 and the mean is −66/190 = −33/95.
- **In the signed form, the far setting changes how much a loop term contributes.** The loop term through B is 1/9 of the direct term before the edit and 1/21 after. On a ring of three knots the loop term has the opposite sign and cancels 1/3, then 1/7, of the direct term (mean −3/13 → −9/31; the readers' knots share a distinction there).
- **The same table is a nonnegative mixture.** For an edit on a not-all-equal knot, the completions number 2 − [others all equal] = (1 − [all equal]) + 1. So for every event on the old distinctions, N′(event) = N(event) + N(event with B's knot deleted).
  - In your file: 294 = 126 + 168 and 686 = 126 + 168 + 168 + 224.
  - On the ring of four: 190 = 82 + 108 and −66 = −30 − 36.

So the accurate statement is not "nothing depends on the far setting". The dependence exists, the signed form writes it as a halving of loops through the far knot, and the count writes it as mixing in the structure without that knot. The two give the same table.

## 2. Is point (4) right?

Partly; three corrections, all by hand and unverified.

- **Signed parity knots.** The character sum is 0 or ± the size, not "0 or its size". The 11-knot structure has signed parity knots.
- **Empty allowed space.** There the expansion cancels completely, half the terms +, half −. "No cancellation" needs "on a nonempty allowed space"; then all nonzero terms of one character share a sign.
- **Events that are not characters.** For the complete record equal to a given word, the indicator is a signed sum of characters, and those do cancel. Example: with x + y = 0 forced, P(x = 0, y = 1) = ¼(1 + 0 − 0 − 1) = 0. The total is still all-or-nothing, uniform on an affine set, so it is harmless, but "no partial cancellation exists at all" is wrong for these.

Two limits on scope:

- Under parity an edit setting deletes the knot's law outright (N′ = N with the knot deleted, not a mixture). A far dependence is then a jump in the affine set.
- Point (4) does not cover mixed structures; `SETTING-AS-REREAD`'s decision note says its newborns are not-all-equal.

## 3. A cheap frozen test

The argument is enough for "same table", since it is an identity. A test is worth running only for the parts with content:

1. **Representation.** Run `expand` with merged constants. Predict the totals unchanged, and the parts changed to 126 − 0, 294 − 0 and 686 − 0.
2. **A start with a loop.** Use the ring of four above (and the ring of three). Predict the four numbers above and N′(event) = N(event) + N(event, knot deleted) for every event on the old distinctions.
3. **Criterion.** Predict that a near statistic is unchanged by the far edit exactly when its value is the same with the far knot deleted. Test on the census starts `forbid.py` already enumerates.
4. **Contrast row.** Run the same starts under R2. That is the only reading in the record where the signed sum is not a count, so only there can the two readings differ. Report whether its no-signalling gate fails where the count's does not.

Hivemind entry added (`unverified` except the file readings). Nothing here touches the publication hold.