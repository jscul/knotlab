# Should witnesses be allowed to cancel? (the interference reading)

Status: adopted on 2026-10-29 by the repository owner's standing rule (take the reading that gives more interesting results): the signed reading, recorded beside the existential one, reopenable
Raised: 2026-10-29
Commitment: Allowed states are read with existential witnesses (a state is allowed when some witness assignment satisfies every constraint), so counts of witnesses are nonnegative; on that reading "no 2-CNF, even with witnesses, defines a knot" (KNOT-FOUNDATION-20261019-001E), and native patterns of patterns keep only parity (GEOMETRY-LAW-20261029-001A).
Implementation: docs/KNOT_INTUITION.md (open question 2, Witnesses); every later result records the verdict under both readings
Reopen: set Status back to open and rebuild the program views; both verdicts are kept, so nothing has to be re-derived
Decision: Whether to admit a second reading, tested side by side with the canonical one as the competition reading was, in which witnesses carry signs and a state is allowed when its signed witness sum is nonzero, or to admit signed laws as a declared substrate as hub laws were on 2026-10-29, or neither.

## Adoption

On 2026-10-29 the owner answered that questions like this need no explicit answer: the answer is whichever reading gives more
interesting results. The signed reading does:
- under it, every three-bit knot is one cancelling witness away from pairs;
- 14 of 16 classes are rebuilt by their own native copies, and 10 reproduce exactly on the native triangle;
- under the existential reading, only parity survives.

So the signed reading is adopted as a working reading, with three safeguards:
- the canonical K1–K3 test is unchanged, since it is a test on relations, and the signed reading only changes which states count as
  allowed (a nonzero signed witness sum) where a result declares it;
- every result records its verdict under both readings;
- reopening is the Status change above.

## Why this comes up now

Both October 2026 refutations of the Exponential Time Hypothesis get their speed from cancellation. They write every clause as
1 − Π(1 − ℓ), carry signed intermediate sums that count nothing, and recover the count by interpolation (OpenAI) or by an
identity whose terms carry signs, the octonion eight-square identity (Anthropic). The program's canonical reading has no
cancellation. Three earlier epics recommended "signed witnesses" and none took it up (`HUB-DIMENSION-20261024-001`,
`NATIVE-COUNTING-20261024-001`, `TWIST-3D-20261025-001`).

## The evidence (INTERFERENCE-20261029-001)

- **The two/three boundary is a boundary of positivity** (`INTERFERENCE-20261029-001A-P001`).
  - With nonnegative weights, no sum over hidden bits of products of two-variable functions has a knot as its support.
  - With signs, every three-bit knot is exactly such a sum with one hidden bit. A clause of any width is one hidden bit, and a
    3-CNF is one hidden bit per clause.
- **Patterns of patterns** (`INTERFERENCE-20261029-001B-P001`).
  - With weights ±1, native gadgets of three and five copies rebuild 14 of the 16 knot classes, and 12 of them exactly, where
    counting rebuilds only parity.
  - Signed not-all-equal (−1 on one tuple) is reproduced exactly by the native triangle, so the Sierpinski gasket carries it at
    every level.
  - The shared-boundary (triangular-lattice) substitution still keeps only parity, on the first three closed surfaces, for signed
    laws constant on rotation orbits.

## Proposed wording (for docs/KNOT_INTUITION.md, open question 2, Witnesses)

> **Interference (a second reading, 2026-10-29).** If witnesses may carry signs, so that a state is allowed when its signed witness
> sum is nonzero, the two/three boundary disappears: every three-bit knot is one cancelling witness away from pairs, and native
> patterns of patterns keep most knots instead of only parity. The canonical reading stays existential; the signed reading is
> recorded beside it, as the competition reading is.

## Consequences

- **If the signed reading is admitted beside the canonical one.**
  - Every result is reported under both readings.
  - The 2-vs-3 thesis is stated as a positivity statement: positive witnesses cannot make emergence from pairs, while cancelling
    ones can.
  - Question 9 gains signed towers.
- **If signed laws are admitted as a declared substrate (as hubs were).**
  - Signed laws are studied as a resource, like hubs, and never counted as native contact.
- **If neither.**
  - The program stays positive.
  - The ETH algorithms' mechanism is then outside it by construction, and this epic stands as a map of what that excludes.
