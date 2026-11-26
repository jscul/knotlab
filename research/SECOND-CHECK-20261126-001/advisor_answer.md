# The advisor's answer (26 November 2026), read-only in the repository

# Advisor answer: the second kind of check (`SECOND-CHECK-20261126-001`)

I read the hivemind, `dual.py`, `rings_dual.jsonl`, `classes.py`, `classes2.py`, the two-class README and `motion.md`. I cannot run code, so everything marked "by hand" is `unverified` until you run it.

## 1. Errors and counterexamples in the computation

**a. The commuting test never ran.** `checked` by reading the file and the code.
- No row of `rings_dual.jsonl` has the key `growth commutes with the exchange`.
- The cause is `dual.py:43`: `if dS == dH: return out` returns before `_exchanged` is set (line 63). Every ring start has one class, so `ex0` is `None` and line 77 skips the test.
- Your "one n-place knot, grown gives n + 1 knots of n places" is therefore not in the record. If you ran it by hand, record that run.
- Even when it runs, line 79 only compares knot counts and sorted sizes. That is enough for a "no" but not for a "yes".

**b. With loose values free, the least class change has 5 distinctions, not n.** `checked` in the file: `d_change` is 5 at n = 5 and at n = 7 (also 5 at n = 4 and 6).
- By hand: flip one old ring distinction, one parent-to-child distinction at each of its two holders, and one loose distinction at each of the two children reached.
- This is allowed, meets the old ring once, and so changes the class on any odd ring.
- So "changing the class takes at least n distinctions" is true only under pinning.

**c. Pinning exchanges which side is short; neither setting has both long.**

| Setting | Least class label (d_read) | Least class change (d_change) |
|---|---|---|
| Loose free | n (file: 5 at n = 5, 7 at n = 7) | 5 (file) |
| Loose pinned | 3 (file, n = 5 only; "not run" for n ≥ 7) | n (file, n = 5, 7, 8, 9, 10) |

- By hand, the pinned label of 3 holds for every n ≥ 5: one old ring distinction plus one parent-to-child distinction at each of its two holders has even overlap with every move and odd overlap with the old ring.
- Two such labels at neighbouring positions differ by exactly one old knot's row, so they agree.
- This is a repetition code in one reading or the other, not the literature's toric code, where both distances grow.
- Check: run `d_read` pinned at n = 7 to 10 with a weight-bounded search instead of enumerating H-perp.

**d. On even rings the pinned classes are not the free classes.**
- The hivemind's `checked` note says that for n = 8, 10, 12 with loose free, dim (S0+H)/H = 0: the old ring lies in the free moves' span.
- Yet pinned n = 8 and 10 show two classes, parted by the old ring.
- So those two classes are made by the pinning, which removes moves. Only on odd rings is the pinned sign the free sign restricted.
- Your list "n = 5, 7, 8, 9, 10" mixes the two.

**e. "Lawful" is a local proxy.**
- `dual.py:51` tests "three or more places, at most two holders". It is not the record's knot test.
- `motion.md` (line 28) says of the pinned preparation: "on the first grown stage the old holders pass while the new loose holders fail K2".
- So the preparation under the "lawful" finding already fails the record's own test. Run the canonical projection check on the exchanged pattern if "lawful" is to be claimed.

**f. The pinned exchanged pattern is the start ring.** By hand, `unverified`.
- Each move holds two consecutive old ring distinctions and two parent-to-child distinctions held by no other move.
- That is `classes.ring(n, 2)` up to renaming. On these rings the exchange after growth returns the start; it undoes growth and does not commute with it.
- Check: compare `_exchanged` with `classes.ring(n, 2)` up to renaming.

**g. Smaller points.**
- Line 40 is dead code (`... if False else None`).
- "Loose free, not lawful" is recorded only for n = 4 to 7; n ≥ 8 is "not run". The loose pairs do give two-place pieces at every n by `motion.md`'s description.
- "Held by up to eight moves" is the n = 6 value; n = 5 and 7 give 5.
- The flag "a least class change is allowed in the exchanged pattern" is `any(...)`. Pinned, it holds for the old ring; with loose free it is false at n = 7.

## 2. Second check, or scaffold?

Two readings are mixed, and neither gives a new check.

- **Exchanged knot as a parity law on values** (what `dual.py` computes, H-perp):
  - By hand, neighbouring moves share exactly one distinction, so the moves break the exchanged knots' parity.
  - Together with the original law it leaves, on an odd pinned ring, four states.
  - It is a further restriction of values, not the dual's check.
- **Exchanged knot as invariance of the weighting under the move** (what your argument uses):
  - This is `motion.md`'s "a weighting fixed by a group H of changes is exactly a constant on each set x + H", with its supplied signs.
  - It is already recorded and leaves both signs free. The exchange adds nothing to it.
- **Pinning:** by 1c, 1d and 1e it decides which distance is long, creates the classes on even rings, and fails K2 in the record. I would call the pinned lawfulness a scaffold.

## 3. Counterexamples to the argument

All three use `motion.md`'s supplied change read; none is native. All `unverified`.

**a. Loose free, one reader.** The 5-distinction class change of 1b, read as a change, gives +1 with certainty on one sign and −1 on the other. This is the last section of `motion.md` at a ring. The holdings lie in four neighbouring knots.

**b. Pinned, two readers, each holding fewer than n.**
- Split the old ring into two parts, one per reader, and let each read the change of its own part.
- Each part alone leaves the allowed set, so each reader's record is ±1 at one half under either sign. The product is the long change, so it is the sign.
- Joint statistics depend on the sign, marginals do not, settings are free, nothing signals.
- So "a reader holding fewer cannot tell" is right for one reader's own record and wrong for the joint record: n is a total across readers.
- A shared hidden value reproduces this, so there is no excess from it.

**c. The sign is not the resource, and no contact between rings is needed.**
- `motion.md` already records, under the plain positive weighting, that readers splitting one knot have "a joint fixed read ... and joint fixed change ... which anticommute locally".
- On a pinned ring a knot's row lies across the split of 3b and meets each reader's part of the old ring once, so the two readers hold one such pair under either sign.
- With reads and changes as the only settings, one pair gives CHSH 2.
- Two rings, each split between the same two readers, with a product weighting and no contact between the rings, would give two pairs. That is the setting of the literature's Mermin–Peres square, which uses only reads, changes and their products.
- So "a joint state of two rings needs a contact" does not close the argument; what does the work is a holder that meets both readers. The cheapest test is to compute the square on two five-knot pinned rings with `motion.py`'s rule.

**Not opened:** the contact study behind "every contact signals", and `forbid.grown`. The "n + 1 knots of n places" claim is unchecked by me.

**What a referee would press first:** 1a (a claimed result with no record), then 1b and 1c (the distance claim depends on pinning), then 3c.

The hivemind has one new entry for this consultation, marked `unverified` except the two file readings.