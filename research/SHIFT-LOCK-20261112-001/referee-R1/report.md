# Referee report SHIFT-LOCK-R1: locks across two shifts

**Verdict: Confirmed with fixes.**

My own code reproduces the census of 2,880 mixed-knot cells exactly:
- 323 cells lock, and the same 78 cells (10 harmonies, not 11) unlock with no non-constant state along a short step.
- The 376 cells the census left unsettled all have a short-step state, so the 78 are complete on the range.
- Every check on the 78 holds: copy 0 is tied to nothing in all of them.

The fix concerns how "two-way" the 78 are, which rests on A77's cut at steps of length 2:
- **42 of the 78** also open through states that repeat along a step of length 3 or 4. These are often a smaller repeat's state laid
  twice.
- **21** have a side of 3.
- **17 cells** stay two-way under any step and with both sides at least 4: the 5 × 7, 5 × 9 and 7 × 9 families.

Two further checks:
- **The largest harmony** has no symmetry beyond its shifts and flip. That closes half of the automorphism gap.
- **The other uncovered harmony** has more than 200 extra symmetries. Its 14 cells stay unchecked.

The 0011 rule and the 0011 + 01 lock set reproduce to 16 × 16. The Ledrappier sizes reproduce to 32, and G1's proof holds.

Referee: the background referee thread, 2026-11-12. Code: `ref_shift.py` (the census, the squares, the Ledrappier control) and
`ref_shift_extra.py` (the 78 cells). They build on the referee's `ref_lib.py`, `ref_endless.py` and `ref_ties.py`, and import none of
`shift_lib.py`, `loop_lib.py` or `endless_lib.py`. I used Glucose 4 with no conflict budget and networkx for the automorphisms.
Validation: V2. The advisor model was not consulted for this job.

## 1. The census of mixed knots (the owning thread's risk 1): reproduced

| Census category | Cells | Referee |
| --- | --- | --- |
| locked | 323 | locked: 323 |
| every state invariant along a short step | 1,303 | a short-step state: all 1,303 |
| a state invariant along no short step | 878 | short-step state: 800; none: **78** |
| not settled | 376 | a short-step state: all 376 |

- **The 78 are the census's own 78, cell for cell, in 10 harmonies:**
  - 000111
  - 0011 + 01
  - 0000011111
  - 00001111 + 01
  - 0010011011
  - 00001111 + 0011
  - 000000111111 + 01
  - 00001111 + 00101101 + 01
  - the five-orbit harmony of period 8
  - the seven-orbit harmony of period 12

  So **10** is right (coordinator's point i).
- **No cell moved category with an unbounded solver.**

## 2. The 78 cells (new checks)

- **Ties.** In every cell, no place of copy (0, 0) is tied to any distinction of another copy. "Copy 0 tied to nothing" holds in all
  78.
- **Steps longer than 2.** In 42 of the 78 cells, some non-constant state repeats along a step of length 3 or 4, up to the harmony's
  shifts and flip. Usually it is a pure repeat: for example, the 7 × 6 cell of 00001111 + 0011 opens through a state repeating along
  (0, 3), the 7 × 3 cell's state laid twice. In 21 cells one side is 3, so every state is a ring of rows of three copies with a finite
  transfer. Only 17 cells have both sides at least 4 and no non-constant state repeating along any step at all:

  | Cells | Harmonies |
  | --- | --- |
  | 5 × 7 and 7 × 5 (12) | both for 0011 + 01, 00001111 + 0011, 00001111 + 00101101 + 01 and the two largest; 7 × 5 only for 000111 and 000000111111 + 01 |
  | 7 × 9 and 9 × 7 (3) | both for 00001111 + 00101101 + 01; 9 × 7 for 0010011011 |
  | 5 × 9 and 9 × 5 (2) | 00001111 + 00101101 + 01 |
- **Other symmetries.** I computed Aut(R), the permutations of states that preserve the one-knot relation, for the 10 harmonies:
  - for 8 of them it is just the shifts and flip;
  - for 00001111 + 0011 it has 16 extra elements, none giving a short-step state in its cells (as the census found);
  - for the largest harmony, of seven orbits (66 states), it is just the shifts and flip (24), so its 14 cells are covered too;
  - for the five-orbit harmony of period 8 (36 states), it has more than 200 elements against 16 shifts and flips. That harmony's
    14 cells remain unchecked against those extra symmetries, as in the census.

**What this means for A77 (risk 5).** "A walk around one cycle" is read as "repeats along a step of length at most 2". At that cut,
the 78 are exact. At a cut of 3 or 4, 42 cells open through cyclic states, often repeats of a smaller cell's state, and 21 more are
rings of 3-copy rows. The robust core is 17 cells, all of them 5 × 7, 5 × 9 or 7 × 9.

The two-way states exist. The phenomenon is real and does not depend on the cut in those 17 cells. But "in 78 cells they are the only
way the arrangement opens" is a statement relative to A77, and should say so.

## 3. After-run claims (risk 2)

- **0011.** I computed the locks to 16 × 16 with my own code: 147 cells, exactly "4 ∤ m and gcd(n, m) ≤ 3". This is confirmed on the
  range, not proved.
- **0011 + 01.** My lock set to 16 × 16 is the census's, cell for cell:

  | n | Locks at m |
  | --- | --- |
  | 2 | every m from 2 to 15 that is not a multiple of 4 (11 values) |
  | 3, 6, 7, 9, 10, 11, 13, 14, 15 | 2 only |
  | 5 | 2 and 5 |
  | 4, 8, 12, 16 | none |

  The slope-polygon model that predicts it was not rebuilt here, so it stays the thread's model, checked against a lock set I
  confirm.
- **"Locks at every size of a family come only from strips and short-step arithmetic"** (to 16 × 16). I did not rebuild the wedge
  census beyond the two harmonies above. It stays after-run and computed.

## 4. G1, ring ties, the Ledrappier control (risk 3)

- **G1 holds by a four-line proof.** If either ring unlocks, its state laid along one shift and repeated along the other is a state,
  because every knot along the other shift reads three equal copies. If both rings lock, every row and every column is constant. The
  945 cells follow and were not recomputed.
- **Ring ties (403 of 405) were not recomputed.** The ring arithmetic is LOOP-LOCK-R1's.
- **The Ledrappier control reproduces.** By my own rank computation over GF(2) on the n × n torus, the law unlocks at exactly 3, 6, 7,
  9, 12, 14, 15, 18, 21, 24, 27, 28, 30 and 31 for n ≤ 32. It does not unlock at 32. The note's "31 to 32" should read "to 32".

## 5. The coordinator's questions

- **(i)** 10 harmonies, as in section 1.
- **(ii) Built in, or known?** The two-way states are not built in by definition. Whether a cell opens only through them is computed,
  and depends on the cut A77 makes. The mechanisms are known:
  - torus states with no translation symmetry are the primitive periodic points of a two-dimensional shift of finite type, whose
    period sets can be any NE set (Jeandel and Vanier);
  - Ledrappier's shift and the periodic points of algebraic ℤ² actions (Kitchens and Schmidt);
  - height functions of tilings (Thurston) and the slope polygon of the dimer model (Kenyon, Okounkov and Sheffield) for 0011 + 01.

  What is new is data only: which harmonies and sizes, the 0011 rule, and the 0011 + 01 lock set. The note claims no novelty for
  mechanisms, which is right.
- **(iii) Frozen against after-run.**
  - Frozen: G1 and G2, the 2,880-cell census (H0 and H0'), squares to 16, the Ledrappier control, ring ties.
  - After the run, labelled so: the witness verification, the automorphism check (50 cells), the wedge census with the 0011 rule,
    and the 0011 + 01 tilings and slope rule.
- **(iv) Proved against computed.**
  - Proved: G1, G2, and the post-freeze lemma credited to LOOP-LOCK-R1.
  - Computed: everything else. The 0011 rule and the slope rule are computed to 16 × 16, not proved, as the note says.

## 6. Fixes for the thread

1. **The 78 cells and A77.** Say that "the arrangement opens only through two-way states" holds at A77's cut (steps up to 2, shifts
   and flip). 42 of the 78 open also through states repeating along a step of 3 or 4, and 21 have a side of 3. The robust core is 17
   cells (5 × 7, 5 × 9, 7 × 9). **Narrowing** (Overreading: relative to an assumption, stated as if absolute).
2. **The automorphism coverage.** The largest harmony has no symmetries beyond shifts and flip, so its 14 cells are covered. The
   five-orbit harmony of period 8 has more than 200 extra automorphisms, and its 14 cells remain unchecked. **Not a block.**
3. **"Two-way states carry no influence."** State it as "tie copy 0 to nothing (all 78 cells)". "Influence still travels around
   cycles" is a range statement and should say so. **Not a block.**
4. **The Ledrappier sizes.** "31 to 32" should read "up to 32 (32 does not unlock)". **Not a block.**

## Files

`brief.md`. `ref_shift.py`, with outputs `result_mixed.jsonl`, `result_square.json` and `result_ledrappier.json`.
`ref_shift_extra.py`, with output `result_extra.json`.
