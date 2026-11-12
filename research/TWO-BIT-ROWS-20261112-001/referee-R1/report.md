# Referee report TWO-BIT-ROWS-R1 (lean, as asked)

**Verdict: Confirmed with fixes: one Narrowing, two Not a block.**
- **The run reproduces.** My own builder reproduces all 1,596 hop rules with one or two knots exactly, and every harmony and
  unexplained rule I reread.
- **The cheap hop harmony is a product of the halving map's fixed point.** At position 0, old ⌊0/2⌋ is old 0 itself, so the rule
  reads one old position through both reaches. Drop only the knots at position 0 and both 2-knot harmonies vanish (0 of 1,596), as
  do 16 of the 21 hop harmonies in all.
- **Without that collision:**
  - **Fewest knots.** Hop needs 6 knots against flat's 10.
  - **Weight share.** Hop's falls from 0.12% to about 0.028%, against flat's 0.011%. That is roughly 2.5 times, not 11.
- **The post-run reading is wrong for one rule.** The rule said to settle into period 2 from depth 35 dies at depth 41 and stays dead
  to depth 80.

Referee: the background referee thread, 2026-11-12.
- **Code.** `ref_two.py`, my own builder and classifier.
- **Advisor.** The advisor model was not consulted.

## 1. What reproduces

| Item | Census | Referee |
| --- | --- | --- |
| Hop rules with one or two knots, alive(t) and first-generation relation at depths 1..40 | 1,596 | 1,596 of 1,596 equal |
| Hop harmonies among them | 2 (period 2) | the same |
| The 5 unexplained and 6 smallest sampled harmonies, depths 1..40 | — | all equal |

**The construction matches the pre-registration.**
- **Generations.** Position p of generation r holds two distinctions, and generation r has 2 + r positions.
- **The rule.** At new position i it reads old i, old ⌊i/2⌋, new i − 1 and new i. A knot is dropped when a position is missing or two
  of its distinctions coincide.
- **Closing.** The last generation is closed on consecutive triples, in order of position and then of its two distinctions. A
  closing knot can therefore span two positions, which is a fair analogue of ROW-NEST's closing row.

## 2. Is the 2-knot hop harmony forced by the halving reach?

**Yes, at its fixed point, not by the far reach.**

**The rule.** The two knots are on (old i first, old ⌊i/2⌋ second, new i second) and (old i second, old ⌊i/2⌋ first, new i first).
- **At position 0** they become NAE(old 0 first, old 0 second, new 0 second) and NAE(old 0 second, old 0 first, new 0 first). When
  the old pair is equal, both new distinctions are forced to its complement. So position 0 carries "my pair is equal", flipped every
  generation.
- **At position 1** the rule reads old 0, not old 1, so the two columns evolve differently. The parity of the depth then shows in the
  first generation's relation.

**Test: knots at position 0 only, where old i and old ⌊i/2⌋ are the same position, dropped.**

| Hop harmonies | As frozen | Position 0's collision dropped |
| --- | --- | --- |
| One or two knots (exhaustive, 1,596) | 2 | 0 |
| All 21 (exhaustive and drawn) | 21 | 5 (with 6 to 10 knots) |
| Fewest knots | 2 | 6 |
| Weight share (the census's formula) | 0.124% | about 0.028% |

So "hopping makes harmonies with two knots and ten times more often" comes from the halving map's fixed point at 0, a self-reading
column that flat reach does not have.

## 3. Is the flat against hop comparison fair?

**In weighting, yes.**
- **Equal mass.** The code gives each number of knots the same mass in both variants, normalised by C(R, m).
- **Equal coverage.** Rules with one or two knots are exhaustive in both, and the drawn samples are the same size (4,000).

**In construction, no.** Hop alone has the collision at position 0. Without it the comparison is 6 knots against 10, and about 0.028%
against 0.011%. Hop reach still helps, but by a factor of about 2.5.

## 4. The five late rules, to depth 80

| Rule (knots) | Census, depths 1..40 | Referee, depths 1..80 |
| --- | --- | --- |
| 4 | unexplained | dies at 21, dead to 80 |
| 5 | unexplained | dies at 21, dead to 80 |
| 5 | first generation unexplained | changes at 2 and 31, then constant to 80 |
| 5 | unexplained | dies at 31 (first generation changes at 5 and 31), dead to 80 |
| 7 | first generation unexplained | changes to depth 11, alternates at 35 to 40, **dies at 41**, dead to 80 |

**The post-run reading needs one correction.** The note's "one settles into period 2 from depth 35" is the 7-knot rule, which
alternates only from 35 to 40 and then dies.

**None changes again between 42 and 80.** So these are long transients that end in a constant, each measuring depth once, up to a
fixed threshold. They are not counters on this evidence.

**Without position 0's collision,** the two 21-death rules stay unexplained within 40. The 31 and 41 cases become constant or
eventually constant, so the late deaths are not all from the collision.

## 5. Context

**Harmonies are not new to two distinctions.** The nested language with three-distinction ends already keeps time.
- **The count.** In LIMIT-ONLY's W, the self-holding relations cycle with period 2 (222 families), 3 (35) or 4 (7), out of 223,261.
- **What that means.** So "two distinctions per position are enough to keep time" is true, but one distinction per position with
  three-distinction ends already does. It is ROW-NEST's one-bit rows that do not.

## Fixes for the thread

1. **Conclusion 1 and the Answer.**
   - Say that the 2-knot hop harmonies, and 16 of the 21 hop harmonies, come from the collision at position 0. There ⌊0/2⌋ = 0, so
     the rule reads one old position through both reaches. Without it hop needs 6 knots, and its weight share is about 0.028%
     against flat's 0.011%.
   - Reword "hopping makes them with two knots and ten times more often" accordingly.

   **Narrowing** (by construction).
2. **The late rules.** The 7-knot rule dies at depth 41 and does not settle into period 2. All five are constant from depth 42 to
   80. **Not a block.**
3. **Context.** Harmonies already exist in the three-distinction nested language (264 families of LIMIT-ONLY's W with period 2 to
   4), so keeping time is not what two distinctions add. **Not a block.**

## Files

| Command | Output | What it does |
| --- | --- | --- |
| `ref_two.py hop W 10` | `result_hop_*.jsonl` | the 1,596 hop rules, as frozen and without position 0's collision |
| `ref_two.py late` | `result_late.json` | the unexplained and smallest harmonies to depth 80 |
| scratch `hop_harm.py` (run once) | `result_hop_harmonies_no_collision.json` | every hop harmony without the collision |
| `ref_two.py summary` | `result_summary.json` | the counts |
