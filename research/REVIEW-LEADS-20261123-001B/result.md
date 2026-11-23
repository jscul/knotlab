# A learner whose examples are knots: result

Ticket `REVIEW-LEADS-20261123-001B` (B311; G15 with G16), 2026-11-23. Computed; scientific referee pending.
[Pre-registration](preregistration.md) · [full tables and commands](results_draft.md) ·
[deviations](../../experiments/REVIEW-LEADS-20261123-001B/REVIEW-LEADS-20261123-001B-E001_example_knots/deviations.md)

**With the window wiring, the parity features and the answer rule supplied, the learner is never wrong on the designs
it trained on, answers almost nothing there, and on new designs is wrong more often than the recorded count reader on
the same images. What it has that the count reader lacks is a sign of its own: when no rule over its distinctions fits
the examples, its memory has no allowed word.**

## What was run

Thirty-two fresh letter designs (16 L, 16 T), 1,024 images, none of the 3,264 earlier bitmaps; the panel was hashed
before any learner ran on it. Two arms of 64 training images at two quarter-turns: narrow (four designs) and varied
(sixteen). Because the windows have a blank border every feature is the same at every position, so the eight positions
of a design at one turn always get the same answer. The independent units are (design, turn) pairs and every count
below is a multiple of eight.

## What happened

Counts are right / wrong / unanswered.

| Arm, condition | L1 (parity knots) | Count reader on the same items | Count reader, matched abstention | Count reader on all |
| --- | --- | --- | --- | --- |
| Narrow, trained designs at held turns (64) | 8 / 0 / 56 | 0 / 8 | 8 / 0 | — |
| Narrow, designs never trained (512) | 136 / 104 / 272 | 168 / 72 | 200 / 40 | 328 / 184 |
| Varied, any held item (768) | no allowed word: 0 answered | — | — | — |

- **Trained designs.** The eight right answers are one unit: design D1 at one held turn. Seven of eight units are
  unanswered.
- **New designs.** L1 is wrong on 104 of the 240 images it answers (43%). The count reader is wrong on 72 of those same
  240 (30%), and on 40 of the 240 it is most sure of. A forced answer is right only if one parity rule over the
  features gives the label on the new design too, and across designs none does.
- **Varied training.** Twenty-two of the 64 example knots contradict the ones before them: no memory word is allowed.
  Adding window families until some word is allowed took 156 memory distinctions, and the learner then answered none
  of the 768 held images. It had stored its examples and nothing else.
- **Shuffled labels.** In both arms the memory has no allowed word, through every family. The count reader answers
  everything at about one half (264 / 248 and 312 / 200) and gives no sign that the labels mean nothing.
- **Not-all-equal knots.** Nothing is answered, as settled by construction: such a knot leaves the label free unless
  its memory distinctions are all equal in every allowed word.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed | Second implementation agrees on 4,608 rank tests and 3,648 enumerations of the 65,536 words; exchanging the kept knots reverses every answer; a planted rule is recovered from 20 examples (2,000 of 2,000 fresh images right) |
| P1 | Held | No wrong answer on trained designs where a word was allowed (8 answers, one unit) |
| P2 | Held | Varied arm: no allowed word (rank 9 of 16, 22 contradicting knots) |
| P3 | Held in the narrow arm, failed in the varied arm | Narrow: 0 wrong of 8 against the count reader's 8 wrong of 8 on the same items. Varied: nothing answered |
| P4 | Held without content | Shuffled labels leave no allowed word, so there is nothing to score |

The thread recomputed the L1 counts of both arms and both label versions with separate code and got the same numbers.

## What this is about

The result is about this choice of features and this law for an example knot, not about knots in general. Supplied:
the two-by-two wiring with its border, the parities, the answer rule, the list of further window families, the
drawings and split, the comparator. The frozen design named no arm in P3, so both arms are reported. Ten of the 32
designs are mirror images of earlier designs (the generator could not give 16 pairs otherwise); every bitmap is new.

**Verdict.** As a way to recognize letters at turns never trained, this learner is retired: it trades wrong answers
for silence on trained designs and is worse than counting on new ones. One thing stands and is new to the learning
line: the learner's memory failing K3 is a native sign that the examples have no rule in its class, and it fires on
shuffled labels where a counting reader keeps answering. What a learner should add when that sign fires is still
open; adding every window of the next size is not it.
