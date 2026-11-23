# A learner whose examples are knots: pre-registration

Ticket `REVIEW-LEADS-20261123-001B` of epic `REVIEW-LEADS-20261123-001` (takes B311; G15, with G16), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Sonnet sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test and the ordinary growth law are unchanged.

## The question

In the letter and feeder studies an ordinary program learned and the knots stored its numbers. Here the rewarded examples are the knots: the memory is a set of two-valued distinctions, each rewarded image adds one knot over them, and a new image is answered only when the knots force its answer. Does such a learner answer correctly where it answers, does it know when its distinctions are not enough, and does the knot law matter?

## In standard terms

Learning a parity function over GF(2) by Gaussian elimination, answering only on the span of the examples (the consistent-hypothesis or version-space learner with abstention). Inconsistency of the linear system is the test that the hypothesis class is too small. Quantities: right, wrong and unanswered counts on held-out items; coverage.

## Prior work in the program

`python3 -B scripts/track.py objects "learner whose rewarded examples add parity knots answered only when forced" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "learning a parity function by elimination version space abstention" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`python3 -B scripts/track.py objects "8x8 L and T letter images two-by-two window pattern counts" --until 2026-11-23 --exclude REVIEW-LEADS-20261123-001`

`PLUS-ONE-20261118-001` — unrelated object.
`SEARCH-AUDIT-20261112-001` — a relative: the earlier learning line searched over laws; no example was a knot.
`NATIVE-GRADE-20261112-001` — a relative: a learner made of knot rules on counts; not on images and not answered by forcing.
`GROWTH-STATISTICS-20261121-001` — unrelated object.
`HUNT-SHORTEN-20261119-001` — unrelated object.
`FEEDER-PAYOFF-REVERSAL-20261121-001` — a relative: reward wrote a preference into knot memory; the learner was an ordinary program.
`TWO-ENDS-20261117-001` — unrelated object.
`ADDR-KNOTS-20261113-001` — unrelated object.
`PERIODIC-READ-20261111-001` — unrelated object.

Seen before this freeze, by the thread's own abstract checks of 2026-11-23 (`docs/prompts/missed_leads_checks/`, private): the three older, unblinded letter panels (no wrong answer on two; 49 wrong of 143 answered on blind designs; contradiction on the varied training set), with unbordered windows. The panel of this study does not exist yet.

## Prior work outside the program

Learning parities by elimination (Helmbold, Sloan and Warmuth 1992); version spaces (Mitchell 1982); learners that may abstain (Rivest and Sloan 1988). Not found: the examples read as knots of a growing system, with the system's having no allowed state as the learner's own sign.

## Settled by construction (stated, not tested)

If one parity rule over the features gives every label in a population, a forced answer on that population is right. The not-all-equal learner L2 answers nothing: its example knot leaves the label free unless the memory distinctions on it are all equal in every allowed word, which a not-all-equal system never forces. L2 is run once to confirm this and is not a finding.

## What is supplied

The two-by-two window wiring shared across positions, with a blank border of one cell so that counts do not depend on position; the parity features; the parity law of an example knot; the answer rule; the frozen list of further window families; the drawing generator, seed and split; the comparator and its matched abstention. No orientation, letter template or three-lit-pixel clue is supplied. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Panel.** Thirty-two fresh letter designs (16 L, 16 T) from the drawing generator of the relative-pixel study with seed 2026112302, excluding every design that occurs in an earlier panel at any position or quarter-turn. Designs are numbered D1 to D32 in generator order, alternating letters. Each design has 8 positions drawn by the seed and 4 quarter-turns. The panel and its hashes are written before any learner is run on it.
- **Arms.** Narrow: train on D1 to D4, 16 images each (8 positions, turns 0 and 1). Varied: train on D1 to D16, 4 images each (2 positions, turns 0 and 1). Both: 64 images, each seen once.
- **Test conditions.** (a) trained designs at turns 0 and 1 at positions not trained; (b) trained designs at the held turns 2 and 3; (c) D17 to D32, never trained, at all four turns. Identical bitmaps never sit on both sides.
- **Features.** Family F0: the parity of the count of each of the 15 non-blank two-by-two window patterns over the 81 windows of the bordered image, and one constant. Further families, added in this order when needed: F1 the 1×3 and 3×1 windows, F2 the 2×3 and 3×2 windows, F3 the 3×3 windows, each as parities of non-blank pattern counts.
- **L1.** One memory distinction per feature. Each rewarded training image adds one parity knot over the memory distinctions of its odd features, with sign its label. A test image is answered when the kept knots force its label and is unanswered otherwise.
- **L1+.** As L1; when the training knots allow no memory word, add the next family and rebuild, until some word is allowed. The family reached is recorded.
- **L2.** As L1 on F0 with not-all-equal knots (the memory distinctions of the odd features and the label value not all equal), by enumeration of the 65,536 memory words.
- **Comparator C1.** The recorded count reader of the first letter study, trained on the same 64 images. C1 on the same items: its score on exactly the items a learner answers. C1 with matched abstention: C1 leaving unanswered the items of smallest margin until its answered count equals the learner's in each condition.
- **Shuffled arm.** The same training images with labels permuted by seed 2026112303.
- **Checks.** The number of example knots with fewer than three memory distinctions (below the canonical arity) is reported. Exchanging the kept knots between learners trained with opposite label meanings reverses every answered guess; clearing them leaves nothing answered. A second implementation of the forcing test agrees on every item.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gates: the second implementation agrees; the exchange and clearing checks hold; on a planted parity rule over F0 the learner recovers it from 20 random examples. | any fails |
| P1 | Where training allowed a memory word, L1 gives no wrong answer on its trained designs (conditions a and b). | one wrong answer |
| P2 | In the varied arm the training knots of L1 allow no memory word. | a word is allowed |
| P3 | At held turns (condition b) L1+ answers at least one item and is wrong on a smaller share of its answers than C1 on those same items. | nothing answered, or the share is not smaller |
| P4 | With shuffled labels L1 either has no allowed memory word or is right on between 35% and 65% of what it answers. | outside that range with a word allowed |

## Runs and stop rule

One script builds and hashes the panel; one runs every learner and arm once and writes right, wrong and unanswered counts by arm, learner, condition, letter and turn, with coverage. The study stops when every arm is scored once. Every run stays under ten minutes and under 12 GB; a longer run is not started, the partial result is reported instead. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed the six designs cold before this freeze (`research/REVIEW-LEADS-20261123-001/advisor/`, question and answer kept). Its strongest objection here and the change made: The headline compared a learner that abstains with a comparator that answers everything, L1+ may answer almost nothing once features outnumber examples, unpadded windows are not position-invariant at the border, and the not-all-equal learner answers nothing by construction. Changes: the comparator is scored on the same items and with matched abstention, a shuffled-label arm was added, the windows have a blank border, coverage is reported everywhere, and L2 moved to what is settled by construction.
