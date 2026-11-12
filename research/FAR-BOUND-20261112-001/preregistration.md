# Bounded at every distance? Pre-registration

Epic `FAR-BOUND-20261112-001` (`TRAVEL-READ-20261112-001` direction 1; G1 with G17, question 9; program topology, group spacing),
2026-11-12, at the coordinator's go-ahead, in the order it set: the recheck first, then far away, then a proof on one base. Committed
before any registered run. The canonical K1–K3 test is unchanged. The advisor model was consulted on the design before freezing.

## Words

As in `TRAVEL-READ-20261112-001`: frame, along-count, across-count, rank, window bond, cross profile, bounded across, growing across.
New here: an **eventually periodic strip**, a state periodic across with period Q and, along, repeating with period P on each side of
a finite stretch; and a **certified bond**, a set refuted in a window every proper part of which is carried in every pattern by a
doubly periodic state or an eventually periodic strip.

## The question

TRAVEL-READ found 56 of 66 rank-1 travelling bases bounded across (the least window bond to a far distinction about 4 at every
across-count to 6), but only 46% of its bonds certified. Are those bonds real? Do they stay bounded much farther away, including at
across-counts where Ledrappier-type growth would show? Can boundedness be proved on one base?

## Prior work

As in TRAVEL-READ; and Ledrappier's shift, where bonds of three reach (2^n, 0), so bond size tracks binary weight rather than
distance (the advisor's point): targets of low binary weight can hide slow growth.

## What is settled by definition or by proof (checks)

- **The certificate is sound.** An eventually periodic strip solution, with two copies of each tail block constrained equal and P at
  least the largest along-span of the kinds, extends to a state of ℤ² by repeating the tails; every knot of the extension is a
  translate of one inside the window. Complement symmetry halves the patterns.
- **Refutations in a larger window remain refutations**, so the recheck can only remove bonds (a proper part refuted in the larger
  window) or certify them; it can raise b, never lower it below a certified value.
- **The control.** Base 16's profile must be certified exactly: 4, 5, 5, 6, 6 at y = 2 to 6, 5 at 14 along and 3 across, nothing
  downward in one cross-section, class "growing across". Checked before freezing: it is (the patterns doubly periodic states missed are
  carried by eventually periodic strips with Q = 8, P = 2).

## Disclosed before freezing

On four unregistered travelling bases (seeds 912, 922, 936, 938 of the COMMON-FOLD weighting, r = 4, 5) with the frozen code: three
stay bounded across with certified bonds of 4 at every near target (one with uncertified ones on one side), one becomes unresolved
(its bonds certified on one side only); at the first far targets (7 along, 7 to 13 across) certified bonds of 4 or 5 where defined.
Runtime 3 to 14 s per base for the recheck, about a minute for the far targets.

## Ticket A (frozen in `experiments/FAR-BOUND-20261112-001A/`)

**Parts.** `recheck` (the 66 rank-1 bases of TRAVEL-READ's cross.jsonl, its twelve one-cross-section targets, |S| ≤ 5, the same
strips, window twice as large, certificates as above); `far` (the bases bounded across after the recheck: along 7, 10, 15 and across
±7, ±11, ±13, ±14, ±15, ±19, ±20, ±23, of high binary weight, |S| ≤ 5); `rings` (the 103 rank-2 bases: rings of radius 10 and 15,
|S| ≤ 4 in the 3 × 3 cells around the origin). Classes and numbers as in the census's docstring: "bounded across" needs certified bonds
(b_cert) defined at 10 along at |y| = 2 and 6 on some side, a difference at most 1 wherever both are defined, and every defined near
b_cert at most 5; "no certified bond within the cap" counts as unresolved, never as unbounded.

**Predictions.**
- **F1, the recheck.** At least 40 of the 66 rank-1 bases are bounded across on certified bonds.
- **F2, far away.** On at least two thirds of the bases bounded after the recheck, every far target with a certified bond has b_cert at
  most the base's largest near b_cert + 1, and at least 80% of the far targets have one.
- **F3, rings.** On at least two thirds of the rank-2 bases, at least 80% of the ring-15 targets have a bond (certified or window-only)
  of at most 5, and the largest is at most the base's largest ring-3 value in TRAVEL-READ + 1.
- **Validity.** The control holds; at most 20% of bases dropped at the 1,800-second cap.

**Failure criteria, and what each does to the published claim.** The headline of TRAVEL-READ ("56 of 66 bounded across") is
corrected (a Narrowing, logged and reported to the coordinator) if fewer than 56 bases are bounded across on certified bonds, and
overturned (a Block for that reading) if fewer than 33 are. Any base whose class changes is listed. F2 fails if fewer than two
thirds stay bounded far away, or if certified bonds are missing at more than 20% of far targets (then the far range is unresolved, not
unbounded). F3 fails likewise.

## Ticket B (proof on one base)

**Selection, fixed now.** The first base, in the order r ascending and then COMMON-FOLD sample index ascending, that ticket A's recheck
classes bounded across. Nothing about its proof's difficulty enters the choice.

**Goal.** For that base, a constant c and α₀ such that for every across-count y and every along-count α ≥ α₀ the bond distance from
the origin to (α, y) is at most c. **Plan** (the advisor's): S free and a pattern p on S forcing a region H; prove a seed (p forces the
configuration c_p on a finite W₀) and a growth lemma (agreement with c_p on W + h forces it on W + h + g for generators g), each a
finite set of window refutations because c_p is periodic across and eventually periodic along; minimality of S ∪ {x} for all x from
eventually periodic certificates of the residues (α mod P, y mod Q). **Failure.** If no bounded W supports a growth lemma, the attempt
reports an obstruction (evidence against boundedness on that base); the proof is checked by its own exact finite checks and handed to
the referee.

## Decision rules

- **F1 to F3 hold:** the bounded bonds are real and stay bounded to 23 across and radius 15 on most bases: global influence at
  bounded bond distance is the typical reading, now on certified bonds.
- **F1 fails:** TRAVEL-READ's headline narrows or falls, as above.
- **F2 or F3 fails:** boundedness is a near-range effect; slow growth is the next question.

## Runtime

Recheck about 5 minutes, far about an hour, rings about an hour, on 6 and 4 workers; registered in `docs/LONG_RUNNING.md`, each base
saved as it finishes.

## Workspace assumptions

- **Relied on.** A64, A67, A71, A74, A76.
