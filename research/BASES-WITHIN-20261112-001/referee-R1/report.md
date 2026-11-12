# Referee report BASES-WITHIN-R1: bases within bases

**Verdict: Confirmed with fixes.** Every lemma holds and every computed number the epic reports reproduces with new code. One
registered prediction rests on a sampled count that the exhaustive count changes: lagged stitches end a living outer pattern under
37 of the 45 harmonies, not 17, and P4 fails by 8 harmonies, not 28. Three wording fixes follow below. None of them changes a
conclusion. The words used here are the glossary's: unlagged stitch (the record's "stitch at one place"), lagged stitch and lags (its
"shifted stitch" and "shifts"), and steps apart.

Referee: the background referee thread, 2026-11-12, working from the brief in `brief.md`. All the code in this folder was written for
this job and none of it imports the author's `nest_lib.py` or `check.py`. The author's result files were read only to compare. The
methods differ from the author's:
- harmonies come from the pruned window graph, not from `harm_lib`;
- lagged stitches are decided by a C backtracking search over states with bit masks (`shifts.c`), not by SAT;
- ties use Glucose 4 instead of CaDiCaL, and the whole tie relation is computed, not only the origin's tie class;
- level counts come from backtracking over rows with column prefixes, with no SAT;
- the three-copy nesting is built from integer points.

Validation class: V2 (an independent reimplementation by a separate session). The advisor model was not used for this job.

## 1. The hand proofs

| Lemma | Verdict | Note |
| --- | --- | --- |
| L1 | holds | At each place a triple has 0 or 2 unequal pairs, so the sum of the three disagreement counts is 2L exactly when every place holds. |
| L2 | holds | Rows are I-states and columns are O-states, so every state repeats along both shifts. "Harmony" here means the two-shift sense. A70 defines it for one shift. |
| L3 | holds | (w, w, w') holds exactly when w' is w's mirror, so β(w') = β(w) for every w' other than w's mirror. With a third state w', β(w) = β(w') = β(mirror of w), a contradiction. |
| L4 | holds, both directions | "If": the mirror lift. "Only if": a column of a state of O[I] is a state of O, because an unlagged stitch is O's knot read on that column. The record writes out only the "if" direction; the converse needs one line. At every level the result follows by induction, since O[I] is again a not-all-equal base. The lemma uses only two facts: not-all-equal is unchanged when all three members flip, and the inner base lives. It does not use that I is a harmony. |
| L5, L6, L9 | hold | Each follows in a line from L4 and the shift and mirror symmetries. |
| L7 | holds | "If": chain coordinate by coordinate. "Only if": swap one coordinate's seed state in a mirror lift. |
| L8 | holds | This is the standard gauge argument: shift each row and each knot's place. It applies when the incidence graph of distinctions and knots is a forest. |

**Which lemmas are close to true by definition.** L2, L4, L5, L6 and L9 follow in one or two lines from the definition of an
unlagged stitch and two symmetries of not-all-equal: flipping all three members, and shifting a row. The headline "the level above is
the level below" is L4. So it is the mirror symmetry of not-all-equal restated, and it would hold for any living inner base, harmony
or not. The exactly-one control shows that the result depends on that symmetry. It is correct, but it says less than "the outer level
reads its own law" suggests: what the law reads of the inner states (L1, pairwise disagreement counts) is a separate matter, and it is
real. L3, L7 and L8 are genuine lemmas, if standard ones.

## 2. The computations

**The roster.** My window-graph enumeration gives the same 45 harmonies, in the same order, and the same 31 outer patterns. For every
harmony, the cyclic words of length P allowed by its kinds are exactly its states, so counting on Z_P^k is exact.

**E3, levels of finite seeds: confirmed exactly.** I computed the whole tie relation, not only the origins'. It equals the product
rule, pairs and relations, at every level from 1 to 4 for all five seeds. For the Fano plane less one knot there are 3, 60, 927 and
13,080 tied pairs; the other four seeds have none. For origins on the removed knot, the tie class is 3, 9, 27, 81 and the tie extent
is 2, 4, 6, 8 steps, which equals the farthest distinction. Other origins are tied to nothing.

**E4, the three-copy nesting: confirmed and strengthened.** It lives at levels 0 to 7, with 3, 6, 15, 42, 123, 366, 1,095 and 3,282
distinctions. No pair of distinctions is tied anywhere at any of these levels, which is stronger than the record's claim about two
corners. The farthest distinction from the corner is 2^n steps.

That it lives at every level is provable: colour (x, y) by x mod 2, so each cell's three corners read (b, 1 − b, b). That nothing is
forced "at every depth" is computed to level 7 only, and should be worded so (fix 2).

**The control: confirmed.** By brute force, the outer pattern has 2 states under exactly-one, and O[I] has none.

**E2, unlagged stitches: confirmed.** All 1,485 pairs live exactly when the outer pattern does, as L4 says.

**E2, the frozen sample of lags: reproduced exactly.** I regenerated the author's 60 assignments per pair from the pre-registered
seeding and decided each with my code. All 1,485 pairs agree in how many lived and how many ended. The totals:
- 46 endings, under 17 harmonies, all of them on the four-point pattern with all four triples knotted;
- the alternation ends that pattern in 8 of 256 assignments and revives the Fano plane in 16,320 of 16,384;
- all 2,640 sampled assignments of the other harmonies revive the Fano plane.

L9 holds on all 26,340 of the alternation's assignments: each matches signed not-all-equal by brute force. L8 holds. Only 2 of the 32
living outer patterns have no closed chain, so L8's check is thin, but the lemma is proved.

**E2, every lag assignment (new, exhaustive).** Lags matter only up to the gauge of shifting each row and each knot's place. Every
gauge class has the same size, so a share of classes is a share of assignments. I decided every gauge class of every harmony against
every living outer pattern: the 31 connected ones and the Fano plane less one knot. The results:
- **37 of the 45 harmonies end a living outer pattern under some lags, not 17.** The 60-assignment sample missed 20 of them because
  their ending share is small. On the four-point pattern it runs from 0.03% (the ten-orbit harmony of period 14) to 5.5% (the
  one-orbit harmonies of period 16).
- **Endings happen only on the four-point pattern with all four triples knotted, now exhaustively.** No other living pattern of the
  range, the Fano plane less one knot included, ends under any lags for any harmony.
- **8 harmonies never end any of them:** 0011 + 01, 00001111 + 0011, 000111 + 0011 + 01, 00101101 + 0011,
  000000111111 + 0011 + 01, 00001111 + 00101101 + 01, the five-orbit harmony of period 8 (with 0011), and the seven-orbit harmony of
  period 12 (with 0011 and 01). I found no simple rule for which harmonies these are: 0011 alone, 000111 + 01 and
  000000111111 + 0011 all do end the four-point pattern.
- **So P4 still fails, but by 8 harmonies, not 28.** The record's "for 28 harmonies none of 60 did" is true of the sample and should
  not be read as a property of those harmonies.
- **Every lagged stitch keeps the Fano plane dead in only a small share of assignments.** I ran this exhaustively for every harmony of
  period at most 8; periods 10 and 12 were still running when this report was written. The dead share is 1 class in 256 (0.4%) for
  the alternation, which is its unsigned switching class (the 64 of 16,384 assignments). It is 0.07% or less for every other harmony.
  It is never zero, since the unlagged class always stays dead (L4). "In every sampled assignment of every other harmony" is accurate
  as a sample; the exhaustive count makes "almost always, never always" plain.

**The E1 follow-up after the run (descriptive): confirmed by a method without SAT.** All 45 level-2 counts under the 20,000 cap
match: 2, 16, 102, 528, 528, 2,470, 2,470, 11,016, 11,016 and the rest, with 26 harmonies over the cap. So do the linear and mirror-lift
counts, rigidity (only the alternation is rigid) and the level-2 tie products. Level 3 of 0011 has 256 states.

The labels are right in the proof and in the decision note: "follow-up after the run (descriptive, not frozen)", and P1 to P3 "not
tested by the frozen run". One slip is in the owner report (fix 3).

## 3. Fixes for the thread (to log in docs/CORRECTIONS.md if the thread agrees)

1. **Lagged stitches: replace the sampled counts with the exhaustive ones.** In the decision note's answer, its table against the
   pre-registration and section 5 of the proof:
   - "for 17 of 45 harmonies" becomes 37 of 45;
   - "for 28 harmonies none of 60 did" becomes "for 8 harmonies no lags at all end one (exhaustive)";
   - P4 failed, by 8 harmonies on the frozen range;
   - endings happen only on the four-point pattern, proved by exhaustion on the range.

   Suggested verdict: **Not a block** (Wrong count; the direction of P4 and of the conclusion stands). The entry of 2026-11-12 that
   says "Stands. Every lemma and count of BASES-WITHIN-20261112-001" should then point here.
2. **"At every depth" for the three-copy nesting.** "Fixing a corner ... forces nothing, at every depth" (proof, section 4) and
   "Influence stays local, at zero, at every depth" (decision note) are computed to level 7. Living at every level is proved by the
   x mod 2 colouring. **Not a block** (wording).
3. **The owner report's first bullet** puts "0011 gives 4, 16 and 256 states at levels 1 to 3" under "(proved)". These counts come
   from the descriptive follow-up. **Not a block** (labelling).
4. *(Not a correction)* L4's written proof should add the converse line. Its statement should say that it uses only the mirror
   symmetry of not-all-equal and that the inner base lives.

## 4. The coordinator's three questions

- **Does L4 give "lives iff O lives" at every level, or only one direction?** Both directions, at every level. The mirror lift gives
  "if". "Only if" comes from the definition: every column of a state is a state of the outer base. Induction then carries both
  directions to every level, because each level is again a not-all-equal base.
- **Is "Fano revived" stated with the sampled/exhaustive split plain?** Yes in the decision note and the proof: all assignments for
  the alternation, 60 sampled for the others. The owner report's "almost every time" is fair. The exhaustive count (section 2) shows
  that for every harmony a small share of lags keeps the Fano plane dead, so "every sampled assignment" must not be read as "always".
- **Is any lemma true by definition, so that it says less than it sounds?** L2, L4, L5, L6 and L9 are one- or two-line consequences
  of the definitions and the mirror and shift symmetries. The headline "the level above is the level below" is the mirror symmetry of
  not-all-equal and holds for any living inner base. L1, L3, L7 and L8 carry content.

## Files

`brief.md`; `ref_lib.py` (harmonies, patterns, slow cross-check); `shifts.c` and `ref_shifts.py` (lagged stitches); `run_shifts.py`
(`result_sample.json`, `result_exhaustive.json`, `result_fano8.json`, `result_fano.json` when it finishes); `check_signs.py`
(`result_signs.json`); `ref_ties.py` (`result_seeds.json`, `result_gasket.json`, `result_control.json`); `ref_levels.py`
(`result_levels.json`). Before the exhaustive run, `shifts.c` was cross-checked against brute force on 1,760 random cases and on
every assignment of the four-point pattern with the alternation, with no mismatch.
