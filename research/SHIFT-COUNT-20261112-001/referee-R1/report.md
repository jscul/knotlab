# Referee report SHIFT-COUNT-R1: one unlengthened shift against two

**Verdict: Confirmed with fixes.**
- **Ticket A reproduces, and one more base is certified.** With my own window and certificates, all 146 certified rank-2 bases are
  confirmed. Sample 97 at r = 3 has the two certified directions (1, 0) and (−1, −1). The one forced-but-uncertified base (137/4) is
  certified by a two-way eventually periodic state, which makes 147 of 169.
- **Ticket C's base-16 refutation is fair and reproduces.** No lattice up to 24 × 24 carries either of base 16's two patterns: 7,200
  lattices, 7,067 of them with states. A two-way eventually periodic state carries both.
- **The fixes are wording.**
  - The line-count criterion is weak beyond the lattices with one line per direction.
  - b(27) = b(23) = 6 is a plateau of certified upper bounds over one step, on three laws.
  - A3's overturn is best worded as "growth sits on a side no certified cone covers", as the note already does.

Referee: the background referee thread, 2026-11-12.
- **Code.** `ref_shiftcount.py` rechecks ticket A's certified directions; `ref_137.py` handles the uncertified base; `ref_lattices.py`
  is ticket C on base 16. They build on my COMMON-FOLD-R1 `ref_fold.py` (the draw, the window, the tori) and on the two-way eventually
  periodic certificate derived for FAR-BOUND-R1. They import no `census.py`.
- **Not recomputed:** ticket B, and ticket C on the other bases. Section 4 reads both from their rows.
- **Solvers and validation.** CaDiCaL and Glucose 4. Validation: V2 for A and for C on base 16. The advisor model was not consulted
  for this job.

## 1. Ticket A: certified directions (coordinator's i and ii)

**How each base was checked.** For every base the census calls certified rank 2, I took its first certified direction and the first
one independent of it, with the census's travelling pattern (A, p, k, σ) for each. I then checked, with my own code:
- **Forced.** In a 61 × 61 window, p on A is satisfiable and forces σ(p) on A + k·d.
- **Carried.** p with σ(p) is carried, and every pattern on A is carried. The certificates are my tori (199 of them) or a two-way
  eventually periodic state. That state has tails of two blocks each side in both directions, periods from the kinds' spans upward,
  and is built in the direction's frame or in the standard axes.

**Result: 146 of 146 confirmed.**
- **Certificates used.** 288 of the 292 checked patterns-with-image are carried by tori, and 4 by eventually periodic states. In 37
  of the 292 freeness checks, some pattern on A needed an eventually periodic state.
- **A first pass failed.** With periods up to 16 only, 12 bases were not confirmed. Directions like (−6, −5) have large across-spans
  in their frame, and periods sized from the spans, or the standard axes, settle them.

**Sample 97 at r = 3, confirmed (i).**

| Direction | Travelling pattern | Forced | Certificate |
| --- | --- | --- | --- |
| (1, 0) | 00 on {(0, 0), (1, 1)} forces 11 on its translate by (1, 0) | yes | tori |
| (−1, −1) | 011 on {(0, 0), (0, 1), (1, 1)} forces 100 on its translate by (−1, −1) | yes | tori; one pattern on A by an eventually periodic state |

Both directions are certified, so A3 failed as reported.

**Why my TRAVEL-READ-R1 search missed (−1, −1).** It took shifts (a, b) with 0 ≤ a ≤ 4, so it covered one sense of each line, and
forcing along t does not give forcing along −t. My "at least 130" was a lower bound for that reason too.

**Safe wording for A3.** "Growing across does not exclude a second certified shift." On 97/3, by the note's reading (I checked the
directions, not the cone's position), the cone of (1, 0) and (−1, −1) covers the side where its one-cross-section bonds were absent,
and it grows on the other side, like base 16. What goes with growth is a side
no certified cone covers, as the note's revised Reading says. The count of shifts alone does not decide it. FAR-BOUND's "the growing
bases travel in one direction only" is overturned, already logged.

**(ii) 146 against my 130.**
- **My earlier search is contained.** It covered only the 66 bases of rank 1 in TRAVEL-READ and found a second direction on 27. All 27
  are among the census's 43.
- **Where the census's 16 extra directions come from:** both senses of each shift (as on 97/3), shifts up to 6, multiples up to 4, and
  sets of 4 cells. The other 23 bases have no second direction in either family.
- **So 146 = 103 + 43, consistent with my 130 = 103 + 27.**

**The forced-but-uncertified base (137/4) is certified.**
- **The census's position.** It forces (0, ±1) but certified only the line of (2, −1).
- **What my search found.** In ticket A's family, the pattern 0101 on {(0, 0), (0, 1), (0, 2), (2, 0)} forces its complement one step
  along (0, 1).
- **The certificate.** The pattern and its image, and every pattern on A, are carried by two-way eventually periodic states in the
  frame of (0, 1), with periods (4, 4) and (6, 6), and by tori.
- **So** the base has certified rank 2: 147 of 169. A2's "1 uncertified" is a limit of the census's certificates (strips periodic
  across), not of the family.

**Base 16 has the single direction (1, −1),** as in the census's rows. I did not rerun its full family; the control matches the
earlier work.

## 2. Ticket C on base 16 (coordinator's iv)

**The setting.** Base 16's kinds in the sheared frame are {0, (0, 1), (1, 0)} and {0, (0, 2), (1, 2)}. The part is {(0, 0), (0, −1),
(0, 1), (0, 5), (8, 5)}, with the patterns 00001 and 00010. I took every lattice ⟨(n, 0), (k, m)⟩ of the frame with n, m ≤ 24 and
0 ≤ k < n.

| Result | Value |
| --- | --- |
| Lattices | 7,200 |
| With some state of the base | 7,067 |
| Carrying 00001 | 0 |
| Carrying 00010 | 0 |
| Two-way eventually periodic state (frame of (1, −1), periods 2 along and 4 across) | carries both |

So C is empty to 24 × 24, and an empty base does not explain it, since nearly every lattice has states. A state that repeats along
no step carries the patterns. The note's "no repeat up to 24 × 24 carries them, while eventually periodic strips do" is confirmed.

**Is the refutation fair?** It is fair to the frozen criteria, with three remarks.
- **The base-16 refutation.** The frozen test (in LINE-LOCK's pre-registration) names base 16 and its three criteria. "C empty to
  24 × 24" is the first criterion, met for both patterns. So "the reading is refuted for base 16's patterns" is the frozen verdict,
  correctly computed.
- **The other bases.** Applying the test to the 19 unresolved bases was frozen in SHIFT-COUNT's own pre-registration, so the 13 of 21
  is a frozen extension. The 4 refuted "past a threshold" were not recomputed here.
- **The line-count criterion is weaker than the note says.** "Refuted if every line count varies between parallel lines within one
  state" can never fire on a direction with a single line on the lattice. But equality across parallel lines also holds whenever a
  state is invariant, up to the flip, under a translation that moves those lines onto each other: the count of equal neighbours is
  unchanged by translation and by the flip. The census's surviving states sit on lattices such as 11 × 8, which has 8 lines along and
  11 across. There the counts are equal but not automatic, so their equality is evidence for nothing in particular.

  So the 8 "survive weakly" are mostly survivals of a weak criterion. That holds the more strongly because the best divisibility
  fit is the trivial one (d₁ = d₂ = 1) with a share of 1 to 3%. The note says "weakly", which fits.
- **A caution on reading C empty.** A tiling reading with a slope fitting no lattice up to 24 × 24 is not excluded by C empty. The
  frozen criterion accepted that risk. The eventually periodic carriers, which change once and repeat outside a finite stretch, point
  to a line-like defect rather than a slope, as the note says, but that is an interpretation.

## 3. (iii) b(27) = b(23) = 6

**Weak evidence for a bound.** The weaknesses:
- **Only upper bounds.** b_cert is the least certified bond in the family, an upper bound on the least bond. No lower bound is computed.
- **One more step.** 23 to 27 across is a single step.
- **Three laws, not four bases.** 17/4 and 17/5 have identical far profiles (FAR-BOUND-R1).
- **One window value is lower.** On 109/3 the window value at 27 is 5 (b_win), below the certified 6.

So the plateau says the certified upper bound did not rise between 23 and 27. It does not separate a bound of 6 from slow growth. The
pre-registration itself says no finite computation does.

**The structural tests do more.**
- **B1.** No relay was found, so the growth mechanism the design named is absent.
- **B2.** The far cluster translates on 11/5 only, so that one base has some evidence of boundedness along that progression.

## 4. Ticket B and the rest of C: read, not recomputed

**B1 and B2, from the rows.**
- **Creeping bases.** 17/4, 17/5 and 109/3 are "between": largest gap 10 to 11 at 23 across, so not relays and not two clusters.
  112/4's least far bond is two clusters.
- **Bounded bases.** Three of 5 are two clusters (11/5, 133/4, 137/4).
- **Translation.** It works only on 11/5, with s = 1.

All of this matches the note. The classification uses the census's own thresholds (a gap of 6, |y|/2).

**183/4 was dropped at the 3,600-second cap.** In FAR-BOUND its window bonds were 4 everywhere (FAR-BOUND-R1), so it is the least
likely of the five to be growing.

## 5. Fixes for the thread

1. **Ticket A.** Add that the forced-but-uncertified base 137/4 is certified by a two-way eventually periodic state: certified rank 2
   on 147 of 169. A2's limit is the census's certificate family. **Not a block.**
2. **"The creep stops at 6, so far".** Say "the certified upper bound is 6 at both 23 and 27 across on three laws (17/4 and 17/5
   identical); 109/3's window value at 27 is 5; no lower bound". **Not a block.**
3. **Ticket C's line-count criterion.** Equality across parallel lines is automatic with one line per direction, and also follows from
   any translation symmetry of the state up to the flip. So the 8 survivors are weak survivals of a weak criterion. **Not a block.**

## Files

`brief.md`.

| Script | Output | What it does |
| --- | --- | --- |
| `ref_shiftcount.py` | `result_shiftcount.jsonl`, `result_shiftcount_summary.json` | ticket A's directions rechecked |
| `ref_137.py` | `result_137.json` | sample 137's second direction, certified |
| `ref_lattices.py` | `result_lattices.json` | ticket C on base 16 |
