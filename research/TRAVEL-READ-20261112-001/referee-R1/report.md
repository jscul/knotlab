# Referee report TRAVEL-READ-R1: what the law reads on travelling bases

**Verdict: Confirmed with fixes, and the headline narrowed.** The census's numbers reproduce. But "the law usually reads zero
dimensions on travelling bases" does not hold on certified bonds:
- **Few bases stay bounded across on certified bonds.** Of the 66 bases with one travelling direction in the census's family, 22
  stay bounded across with TRAVEL-READ's own doubly periodic certificates. FAR-BOUND's sound eventually periodic certificate raises
  this to 34. "Most" (56) holds only at window level.
- **"Rank 1" depends on the search family.** In a wider family, 27 of those 66 bases travel along a second certified direction. So
  at least 130 of the 169 travelling bases have two independent unlengthened shifts.
- **A second direction explains part of the boundedness.** It accounts for half of the certified bounded bases (17 of 34).

So boundedness across is often a consequence of a second fold, not a separate reading.

Referee: the background referee thread, 2026-11-12. The coordinator asked for a method independent of the owning thread's
larger-window recheck (FAR-BOUND-20261112-001). I used two:
1. **Certified-only aggregation.** I re-read the census's own records using only certified bonds.
2. **A second-direction search.** For each rank-1 base I searched a wider family for a second certified travelling direction: every
   shift (a, b) with 0 ≤ a ≤ 4 and |b| ≤ 4, sets of 2 or 3 cells of [0, 2] × [0, 2] holding the origin, and a 23 × 25 window. The
   torus certificates were as in the census.

The code (`ref_travel.py`) is built on the referee's `ref_fold.py` from COMMON-FOLD-R1. It imports neither census. Validation: V2. The
advisor model was not consulted for this job.

## 1. What reproduces

- **T1, recounted from `dirs.jsonl`.** At r = 4 and 5, 70 of 108 bases have rank 2 and 65 of those share a common pattern. In all,
  103 of 169 have rank 2, and 35 travel along all ten shifts.
- **T2 at window level, recounted from `cross.jsonl` with my own implementation of the frozen rule.** 56 bounded across, 2 growing
  across, 8 undecided.
- **The thresholds were frozen** (coordinator's ii). The T2 rule ("b(10, ±6) − b(10, ±2) ≤ 1 wherever both are defined, with one
  side defined to ±6; growing when some difference is ≥ 2") is in the pre-registration word for word.
- **FAR-BOUND's recheck, recounted from its `recheck.jsonl` with my own aggregation.** 34 bounded across, 3 growing, 29 unresolved.
  My classification agrees with the record on every one of the 66 bases.
- **Not recomputed:** T3 and T4.

## 2. The headline on certified bonds (coordinator's i)

| T2 reading | Bounded across | Growing across | Undecided or unresolved |
| --- | --- | --- | --- |
| window bonds (frozen) | 56 | 2 | 8 |
| TRAVEL-READ's doubly periodic certificates only | 22 | 1 | 43 |
| FAR-BOUND's eventually periodic certificates, window twice as large | 34 | 3 | 29 |

The upper-bound reading is the safe one. A certified bond is a true bond, so a certified b bounds the least bond from above. Read that
way, 36 bases have a certified bond of at most five distinctions to a target six across. The window-level 56 is not a certified count.

So "most rank-1 bases are bounded across" becomes "about half (34 of 66) on certified bonds". "The law usually reads zero dimensions"
should be narrowed to the certified statement:
- At least 130 of the 169 travelling bases travel along two independent certified directions, so bond distance is bounded along
  both. This follows from the census's lemma.
- 65 of the 70 rank-2 bases at r = 4 and 5 share one pattern, so bond distance is bounded on a cone and its mirror.
- Of the rest, about half are bounded across within six across on certified bonds.
- Zero dimensions in every direction is not shown. T4's rings use window bonds and need the same certified restatement.

## 3. Is "bounded across" forced by a second unlengthened shift? (coordinator's iii)

It is not settled by definition, but it often comes with a second fold.

**The second-direction search** finds a second certified direction for 27 of the 66 bases. In each case a pattern on 2 or 3
cells forces its own translate, or the translate's mirror, along a shift the census did not search: mostly shifts of length 3 or 4,
once (2, 2), and twice a listed shift with a set reaching outside the census's box. For
example, sample 24 at r = 3 travels along (0, 4), which FAR-BOUND's own proof found too. My first-direction search re-found the
census's direction on the bases tried.

**By class:**

| Class | Bases | With a second certified direction |
| --- | --- | --- |
| bounded across at window level | 56 | 26 |
| growing across (lines) | 2 | 0 |
| undecided | 8 | 1 |
| FAR-BOUND's certified bounded across | 34 | 17 |

So the census's "rank 1" means "one direction in the searched family". The rank-2 share in T1 is a lower bound.

**What the lemma gives.** Travel along t₂ bounds bond distance along t₂. Bond distance at (10, y) follows only with a common pattern,
which I did not test. So these bases are not proved bounded across by this alone, but their reading across is not a second,
independent fact about the base.

**The other half.** The 17 certified bounded bases with no second direction found in the wider family are the clearer cases of a
boundedness the search does not explain. The growing bases, base 16's kind, have no second direction, as base 16 has none.

## 4. FAR-BOUND's new certificate and proof (the coordinator's update)

**The eventually periodic certificate is sound.** I read the construction in its `census.py` (`Eventual`).
- **The certificate.** A window holds the cells from X₀ − 2P to X₁ + 2P along, periodic across with period Q in the frame. Knots are
  imposed where all members fall inside. The two tail blocks on each side are constrained equal, with P at least the kinds' span
  along.
- **Why a solution extends.** Repeat the left block to −∞ and the right block to +∞. Any knot of the extension lies wholly in a
  periodic tail or wholly inside the window. A tail knot is a translate, by a multiple of P, of a knot inside the window, because
  P ≥ span: if its first member is in the tail, all its members are. So every knot of the extension holds.
- **Unimodular frames.** These make the across period well defined.
- **Unrepresented cells.** A pattern with a cell outside the window is never counted as carried, which is conservative.

**The proof on one base** (FAR-BOUND ticket B, sample 24 at r = 3): the logic is sound.
- The travel along t′ and 4u comes from window refutations, which are sound. The induction gives forcing on the quadrant classes.
- T_j is free by eventually periodic strips.
- Each pair with x is free by a state family that repeats outside a finite box in both directions. That reduces it to 1,620
  representative cases.
- The four-set is then a bond, since every proper subset lies in T_j or in some π ∪ {x}.

I did not rerun the 1,620 cases. That belongs to FAR-BOUND's own referee job when it closes.

## 5. Fixes for the thread

1. **The Answer and conclusion 2.** "The law usually reads zero dimensions … 56 of 66 bounded across" should become the certified
   statement: 34 of 66 bounded across on certified bonds (FAR-BOUND), 22 with doubly periodic certificates alone. Also, at least 130
   of 169 travel along two certified directions. **Narrowing** (Overreading: window bonds reported as bonds).
2. **Rank 1 depends on the family.** 27 of the 66 bases travel along a second certified direction among shifts of length up to 4.
   Say that T1's rank-2 share is a lower bound, and that half the certified bounded-across bases have a second direction. **Narrowing**.
3. **T4 (rings)** rests on window bonds. Restate it at the certified level, or label it window-level. **Not a block**.

## Files

`brief.md`; `ref_travel.py` → `result_certified.json` (the classes on certified bonds), `result_second.jsonl` (second directions for
the 66 bases).
