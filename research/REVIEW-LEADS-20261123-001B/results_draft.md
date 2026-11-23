# REVIEW-LEADS-20261123-001B: a learner whose examples are knots (draft result, referee pending)

Draft by the Sonnet implementation agent; the thread owns the verdict, the report format and the scope transitions. Exploratory study on one fresh panel; nothing here proves an all-size statement. The pre-registration (`preregistration.md`, a078a4f959) was not edited; the places where it left a choice are in `experiments/REVIEW-LEADS-20261123-001B/REVIEW-LEADS-20261123-001B-E001_example_knots/deviations.md` (read it before the verdicts, especially items 2, 5, 6 and 7).

In standard terms: learning a parity function over GF(2) by Gaussian elimination, answering only on the span of the examples. L1 = F0 only; L1+ = F0, then F0+F1, F0+F1+F2, F0+F1+F2+F3 until the knots allow a memory word (F0: 2x2 windows, 16 memory distinctions with the constant; F1 adds 1x3 and 3x1 (30); F2 adds 2x3 and 3x2 (156); F3 adds 3x3 (667)). C1 = the integer implementation of the recorded count reader of PIXEL-LETTERS-20261122-001 (the knot version was not run).

## Commands (from the repository root; each under ten minutes and 12 GB; each takes about two seconds)

```
timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001B/REVIEW-LEADS-20261123-001B-E001_example_knots/panel.py   # builds and hashes the panel (a rerun verifies it against a fresh build)
timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001B/REVIEW-LEADS-20261123-001B-E001_example_knots/run.py gates   # gates only; opens no scorer key
timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001B/REVIEW-LEADS-20261123-001B-E001_example_knots/run.py score   # every learner, arm and control once; refuses to run twice
```

Outputs: `artifacts/REVIEW-LEADS-20261123-001B/REVIEW-LEADS-20261123-001B-E001_example_knots/` (`panel/` with `manifest.json`, sha256 a6512c8bd43fd9cdfe7df368ba4221d29496eeb346f019992148ff2c2523376d; `gates.json`, `log_gates.txt`; `results/` with `tables.md`, `counts.csv` (every arm, labels, learner, condition, letter, turn), `verdicts.json`, `items_<arm>_<labels>.jsonl`, `gates.json`, `log.txt`). The panel was written and hashed before any learner code was run on it.

## The panel

32 fresh designs (16 L, 16 T; D1 to D32, alternating, the L and T of one pair sharing step lists), 8 seeded positions x 4 quarter-turns each = 1024 images, none equal to any of the 3264 bitmaps of the four earlier panels, none with the rotation class of an earlier design; all have 6 or 7 lit pixels. Narrow arm: D1 to D4, all 8 positions, turns 0 and 1 (64 images). Varied arm: D1 to D16, the first 2 positions, turns 0 and 1 (64 images). Test items: narrow a = 0 (every position is trained), b = 64, c = 512; varied a = 192, b = 256, c = 512. Shuffled arms: same images, labels permuted by seed 2026112303 (30 labels change in the narrow arm, 32 in the varied arm). No test file carries a label; only the scorer reads the keys.

**Denominators and independence.** The windows are blank-padded so that every feature is translation-invariant (deviations, item 6). All 8 positions of one design at one turn therefore give the identical feature vector, and every learner answered all 8 identically (checked on every unit). Every count below is a multiple of 8; the independent units are (design, turn) pairs: narrow b = 8 units, narrow c = 64; varied a = 32, b = 32, c = 64.

## Gates (all pass)

| Gate | Result |
| --- | --- |
| Second implementation of the forcing test agrees on every item | dense GF(2) rank test on 4608 item answers (L1 and L1+, both arms, true and shuffled labels): 0 mismatches; enumeration of all 65,536 F0 memory words on 3648 item answers and on the existence of an allowed word: 0 mismatches |
| Exchange of kept knots between learners trained with opposite label meanings reverses every answered guess; clearing leaves nothing answered | applies where a memory word exists: narrow L1 and L1+ (F0, 248 items answered), varied L1+ (F2, 192 answered): every answer reversed, same items answered, 0 answered after clearing |
| Planted parity rule over F0 from 20 random examples | planted word 0xaf2f; 20 examples reached rank 11, the rank of all 2020 random images (random images span 11 of the 16 F0 dimensions); 2000 of 2000 fresh random images answered, 2000 right, 0 wrong; 32 allowed words by enumeration |
| C1 totals equal the label-wise sums of window histograms | true in all four (arm, labels) cases |

## Verdicts

| # | Prediction | Verdict | Exact counts (right / wrong / unanswered) |
| --- | --- | --- | --- |
| G | Gates | holds | as above |
| P1 | Where training allowed a memory word, L1 gives no wrong answer on its trained designs (a and b) | holds where it applies: narrow arm only; varied arm not applicable (L1 allows no word) | narrow, L1 at F0: a 0/0/0 (empty); b 8/0/56. The 8 right answers are one unit: D1 (L) at turn 2, all 8 positions |
| P2 | In the varied arm the training knots of L1 allow no memory word | holds | no word at F0: rank 9 of 16, 22 of the 64 knots contradict those before them; also none at F1 (rank 13 of 30); L1+ gets a word at F2 (rank 32 of 156) |
| P3 | At held turns L1+ answers at least one item and is wrong on a smaller share than C1 on those same items | holds in the narrow arm (one unit); fails in the varied arm (nothing answered) | narrow, L1+ (F0) b: 8/0/56 (0 of 8 wrong); C1 on the same 8 items: 0/8 (8 of 8 wrong); C1 with matched abstention (8 answered): 8/0/56. Varied, L1+ (F2) b: 0/0/256; C1 on the same items: none |
| P4 | Shuffled labels: L1 has no allowed word, or is right on 35 to 65% of what it answers | holds (no allowed word in either arm; nothing to answer) | narrow: rank 8 of 16, no word; varied: rank 9 of 16, no word. L1+ also reaches no word through F3 in either arm (narrow rank 8 at every level; varied rank 32 of 667 at F3) |

L2 (not-all-equal) answers nothing in all four (arm, labels) cases, as settled by construction (allowed memory words of 65,536: narrow true 63,880, narrow shuffled 62,878, varied true 56,380, varied shuffled 52,984). Not a finding.

Example knots with fewer than three memory distinctions: 0 of 64 in each arm at every family level (smallest knot 7 distinctions in the narrow arm and 5 in the varied arm at F0, constant included; 6 and 4 without it).

## Readings the counts support (and one they do not)

- Where L1 answers on its trained designs the answers are right, but few are held out: the only answers of L1 and L1+ at held turns on trained designs (condition b) are 8 items (one unit) in the narrow arm; the 192 right answers of L1+ in the varied arm's condition a are the trained feature vectors at new positions, right by construction of the translation-invariant features, not a held-out result.
- At held turns on the varied arm L1+ (F2, 156 memory distinctions, 32 independent knots) answers nothing in conditions b and c: the new turns and new designs are not in the span of the 32 training knots.
- Narrow arm, condition c (new designs): L1 answers 240 of 512 (47%): 136 right, 104 wrong (43% of its answers wrong; 30 units answered, 17 right, 13 wrong). C1 on those same 240 items: 168 right, 72 wrong; C1 with matched abstention (240 answered): 200 right, 40 wrong; C1 answering all 512: 328 right, 184 wrong. A forced answer on a new design is therefore not reliable here, and the count reader is more often right on the same items.
- Shuffled labels: L1 and L1+ detect that no memory word exists (L1+ through F3); C1 trained on the shuffled labels still answers everything: narrow c 264 right / 248 wrong (52%), varied c 312 right / 200 wrong (61%, on 64 units).

Not done: the knot version of C1; any further window family beyond F3; a held-out-position condition in the narrow arm (condition a is empty under the pre-registered 8 positions); any rerun with another seed.

---

# Generated tables (`results/tables.md`; "right/wrong/unanswered (coverage)")


### Counts right / wrong / unanswered (coverage), labels: true


Arm **narrow**; test items per condition: a=0, b=64, c=512

| learner | condition a | condition b | condition c |
| --- | --- | --- | --- |
| L1 | 0/0/0 | 8/0/56 (12% answered) | 136/104/272 (47% answered) |
| L1+ | 0/0/0 | 8/0/56 (12% answered) | 136/104/272 (47% answered) |
| L2 | 0/0/0 | 0/0/64 (0% answered) | 0/0/512 (0% answered) |
| C1 | 0/0/0 | 32/32/0 (100% answered) | 328/184/0 (100% answered) |
| C1@L1 | 0/0/0 | 0/8/56 (12% answered) | 168/72/272 (47% answered) |
| C1m@L1 | 0/0/0 | 8/0/56 (12% answered) | 200/40/272 (47% answered) |
| C1@L1+ | 0/0/0 | 0/8/56 (12% answered) | 168/72/272 (47% answered) |
| C1m@L1+ | 0/0/0 | 8/0/56 (12% answered) | 200/40/272 (47% answered) |

Arm **varied**; test items per condition: a=192, b=256, c=512

| learner | condition a | condition b | condition c |
| --- | --- | --- | --- |
| L1 | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| L1+ | 192/0/0 (100% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| L2 | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| C1 | 144/48/0 (100% answered) | 152/104/0 (100% answered) | 272/240/0 (100% answered) |
| C1@L1 | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| C1m@L1 | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| C1@L1+ | 144/48/0 (100% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| C1m@L1+ | 144/48/0 (100% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |

### Counts right / wrong / unanswered (coverage), labels: shuffled


Arm **narrow**; test items per condition: a=0, b=64, c=512

| learner | condition a | condition b | condition c |
| --- | --- | --- | --- |
| L1 | 0/0/0 | 0/0/64 (0% answered) | 0/0/512 (0% answered) |
| L1+ | 0/0/0 | 0/0/64 (0% answered) | 0/0/512 (0% answered) |
| L2 | 0/0/0 | 0/0/64 (0% answered) | 0/0/512 (0% answered) |
| C1 | 0/0/0 | 32/32/0 (100% answered) | 264/248/0 (100% answered) |
| C1@L1 | 0/0/0 | 0/0/64 (0% answered) | 0/0/512 (0% answered) |
| C1m@L1 | 0/0/0 | 0/0/64 (0% answered) | 0/0/512 (0% answered) |
| C1@L1+ | 0/0/0 | 0/0/64 (0% answered) | 0/0/512 (0% answered) |
| C1m@L1+ | 0/0/0 | 0/0/64 (0% answered) | 0/0/512 (0% answered) |

Arm **varied**; test items per condition: a=192, b=256, c=512

| learner | condition a | condition b | condition c |
| --- | --- | --- | --- |
| L1 | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| L1+ | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| L2 | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| C1 | 90/102/0 (100% answered) | 128/128/0 (100% answered) | 312/200/0 (100% answered) |
| C1@L1 | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| C1m@L1 | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| C1@L1+ | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |
| C1m@L1+ | 0/0/192 (0% answered) | 0/0/256 (0% answered) | 0/0/512 (0% answered) |

### By condition, letter and turn (true labels; right/wrong/unanswered)


Arm **narrow**, condition b

| learner | L q0 | L q1 | L q2 | L q3 | T q0 | T q1 | T q2 | T q3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | - | - | 8/0/8 (50% answered) | 0/0/16 (0% answered) | - | - | 0/0/16 (0% answered) | 0/0/16 (0% answered) |
| L1+ | - | - | 8/0/8 (50% answered) | 0/0/16 (0% answered) | - | - | 0/0/16 (0% answered) | 0/0/16 (0% answered) |
| C1@L1+ | - | - | 0/8/8 (50% answered) | 0/0/16 (0% answered) | - | - | 0/0/16 (0% answered) | 0/0/16 (0% answered) |
| C1m@L1+ | - | - | 0/0/16 (0% answered) | 0/0/16 (0% answered) | - | - | 0/0/16 (0% answered) | 8/0/8 (50% answered) |
| C1 | - | - | 8/8/0 (100% answered) | 0/16/0 (100% answered) | - | - | 16/0/0 (100% answered) | 8/8/0 (100% answered) |

Arm **narrow**, condition c

| learner | L q0 | L q1 | L q2 | L q3 | T q0 | T q1 | T q2 | T q3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | 24/8/32 (50% answered) | 16/0/48 (25% answered) | 0/16/48 (25% answered) | 32/8/24 (62% answered) | 32/8/24 (62% answered) | 8/24/32 (50% answered) | 8/16/40 (38% answered) | 16/24/24 (62% answered) |
| L1+ | 24/8/32 (50% answered) | 16/0/48 (25% answered) | 0/16/48 (25% answered) | 32/8/24 (62% answered) | 32/8/24 (62% answered) | 8/24/32 (50% answered) | 8/16/40 (38% answered) | 16/24/24 (62% answered) |
| C1@L1+ | 32/0/32 (50% answered) | 16/0/48 (25% answered) | 8/8/48 (25% answered) | 24/16/24 (62% answered) | 32/8/24 (62% answered) | 24/8/32 (50% answered) | 16/8/40 (38% answered) | 16/24/24 (62% answered) |
| C1m@L1+ | 56/0/8 (88% answered) | 48/0/16 (75% answered) | 8/8/48 (25% answered) | 24/0/40 (38% answered) | 16/0/48 (25% answered) | 32/0/32 (50% answered) | 8/8/48 (25% answered) | 8/24/32 (50% answered) |
| C1 | 64/0/0 (100% answered) | 56/8/0 (100% answered) | 24/40/0 (100% answered) | 40/24/0 (100% answered) | 40/24/0 (100% answered) | 48/16/0 (100% answered) | 32/32/0 (100% answered) | 24/40/0 (100% answered) |

Arm **varied**, condition a

| learner | L q0 | L q1 | L q2 | L q3 | T q0 | T q1 | T q2 | T q3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | 0/0/48 (0% answered) | 0/0/48 (0% answered) | - | - | 0/0/48 (0% answered) | 0/0/48 (0% answered) | - | - |
| L1+ | 48/0/0 (100% answered) | 48/0/0 (100% answered) | - | - | 48/0/0 (100% answered) | 48/0/0 (100% answered) | - | - |
| C1@L1+ | 30/18/0 (100% answered) | 42/6/0 (100% answered) | - | - | 36/12/0 (100% answered) | 36/12/0 (100% answered) | - | - |
| C1m@L1+ | 30/18/0 (100% answered) | 42/6/0 (100% answered) | - | - | 36/12/0 (100% answered) | 36/12/0 (100% answered) | - | - |
| C1 | 30/18/0 (100% answered) | 42/6/0 (100% answered) | - | - | 36/12/0 (100% answered) | 36/12/0 (100% answered) | - | - |

Arm **varied**, condition b

| learner | L q0 | L q1 | L q2 | L q3 | T q0 | T q1 | T q2 | T q3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | - | - | 0/0/64 (0% answered) | 0/0/64 (0% answered) | - | - | 0/0/64 (0% answered) | 0/0/64 (0% answered) |
| L1+ | - | - | 0/0/64 (0% answered) | 0/0/64 (0% answered) | - | - | 0/0/64 (0% answered) | 0/0/64 (0% answered) |
| C1@L1+ | - | - | 0/0/64 (0% answered) | 0/0/64 (0% answered) | - | - | 0/0/64 (0% answered) | 0/0/64 (0% answered) |
| C1m@L1+ | - | - | 0/0/64 (0% answered) | 0/0/64 (0% answered) | - | - | 0/0/64 (0% answered) | 0/0/64 (0% answered) |
| C1 | - | - | 32/32/0 (100% answered) | 24/40/0 (100% answered) | - | - | 48/16/0 (100% answered) | 48/16/0 (100% answered) |

Arm **varied**, condition c

| learner | L q0 | L q1 | L q2 | L q3 | T q0 | T q1 | T q2 | T q3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) |
| L1+ | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) |
| C1@L1+ | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) |
| C1m@L1+ | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) | 0/0/64 (0% answered) |
| C1 | 24/40/0 (100% answered) | 40/24/0 (100% answered) | 8/56/0 (100% answered) | 0/64/0 (100% answered) | 48/16/0 (100% answered) | 56/8/0 (100% answered) | 56/8/0 (100% answered) | 40/24/0 (100% answered) |

### Feature family reached by L1+, coverage, and the memory

| arm | labels | L1 (F0) has an allowed word | L1 rank of 16 | L1+ family | features | rank | families tried (name, allowed word, rank, features) | L2 allowed words of 65,536 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| narrow | true | True | 8 | F0 | 16 | 8 | [('F0', True, 8, 16)] | 63880 |
| narrow | shuffled | False | 8 | None | None | None | [('F0', False, 8, 16), ('F1', False, 8, 30), ('F2', False, 8, 156), ('F3', False, 8, 667)] | 62878 |
| varied | true | False | 9 | F2 | 156 | 32 | [('F0', False, 9, 16), ('F1', False, 13, 30), ('F2', True, 32, 156)] | 56380 |
| varied | shuffled | False | 9 | None | None | None | [('F0', False, 9, 16), ('F1', False, 13, 30), ('F2', False, 32, 156), ('F3', False, 32, 667)] | 52984 |

### Example knots with fewer than three memory distinctions (training knots; the constant counts as one distinction)

| arm | family level | knots | below three | below three without the constant | of size 1 | of size 2 | smallest size | largest size | distinct knots (by odd-feature set) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| narrow | up to F0 | 64 | 0 | 0 | 0 | 0 | 7 | 10 | 8 |
| narrow | up to F1 | 64 | 0 | 0 | 0 | 0 | 15 | 15 | 8 |
| narrow | up to F2 | 64 | 0 | 0 | 0 | 0 | 40 | 47 | 8 |
| narrow | up to F3 | 64 | 0 | 0 | 0 | 0 | 60 | 71 | 8 |
| varied | up to F0 | 64 | 0 | 0 | 0 | 0 | 5 | 11 | 31 |
| varied | up to F1 | 64 | 0 | 0 | 0 | 0 | 9 | 18 | 31 |
| varied | up to F2 | 64 | 0 | 0 | 0 | 0 | 32 | 47 | 32 |
| varied | up to F3 | 64 | 0 | 0 | 0 | 0 | 50 | 71 | 32 |

### Prediction verdicts (computed from the counts above)

```json
{
 "P1": {
  "narrow": {
   "applicable": true,
   "a": [
    0,
    0,
    0
   ],
   "b": [
    8,
    0,
    56
   ],
   "wrong_in_a_and_b": 0,
   "answered_in_a_and_b": 8
  },
  "varied": {
   "applicable": false,
   "note": "no allowed memory word for L1 at F0"
  }
 },
 "P3": {
  "narrow": {
   "L1+_family": "F0",
   "L1+_b": [
    8,
    0,
    56
   ],
   "C1_same_items_b": [
    0,
    8,
    56
   ],
   "C1_matched_b": [
    8,
    0,
    56
   ],
   "answered": 8,
   "L1+_wrong_share": 0.0,
   "C1_same_items_wrong_share": 1.0,
   "holds": true
  },
  "varied": {
   "L1+_family": "F2",
   "L1+_b": [
    0,
    0,
    256
   ],
   "C1_same_items_b": [
    0,
    0,
    256
   ],
   "C1_matched_b": [
    0,
    0,
    256
   ],
   "answered": 0,
   "L1+_wrong_share": null,
   "C1_same_items_wrong_share": null,
   "holds": false
  }
 },
 "P4": {
  "narrow": {
   "word_allowed": false,
   "holds": true,
   "note": "no allowed memory word with shuffled labels"
  },
  "varied": {
   "word_allowed": false,
   "holds": true,
   "note": "no allowed memory word with shuffled labels"
  }
 },
 "P2": {
  "L1_allows_no_word_in_varied_arm": true,
  "holds": true,
  "L1_rank": 9,
  "knots_contradicting_on_arrival": 22
 }
}
```
