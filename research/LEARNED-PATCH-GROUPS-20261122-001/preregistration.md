# Can reward teach a letter distinction that survives an unseen turn?

Single G15 study `LEARNED-PATCH-GROUPS-20261122-001`, proposed on 2026-11-22. Astra Max reviews the complete proposed contract before the detached freeze. Both parity and not-all-equal go to the same blind test under every outcome.

## Question and existing evidence

The earlier reader learned class-dependent frequencies from raw pixels but called every held-turn T an L. An inspection after scoring showed that one particular sum of local frequencies separated its old drawings. That observation motivated testing whether a learner can select a sum. It is known to the study designers. None of its pattern identities, coefficients, transformations or target frequencies are built into the learner, its candidate ordering, its tie rule, or the scoring criterion. The same fresh training and test sets are used for every comparison. [Earlier frozen study and post-score observation](../PIXEL-LETTERS-20261122-001/decision.md)

## Prior work in the program

`python3 -B scripts/track.py objects "learning a group of pixel patterns from reward" --until 2026-11-22 --exclude LEARNED-PATCH-GROUPS-20261122-001`

`python3 -B scripts/track.py objects "subset sums pixel histograms" --until 2026-11-22 --exclude LEARNED-PATCH-GROUPS-20261122-001`

`python3 -B scripts/track.py objects "8x8 glyphs" --until 2026-11-22 --exclude LEARNED-PATCH-GROUPS-20261122-001`

The directly relevant `PIXEL-LETTERS-20261122-001` is a closed standalone ticket. Its 400 bitmaps, 16 normalized drawings, old readout and post-score finding were available before this study. `SECOND-FEEDER-CUE-20261121-001` asked whether credit selected a supplied cue. `FEEDER-PAYOFF-REVERSAL-20261121-001` used reciprocal learned words to change the choice at a feeder. `AGENT-LOOP-20261117-001` and `WHERE-NEXT-20261116-001` investigated learned search rules on formulas. `WHICH-SEQUENCES-20261112-001`, `LAW-RIGIDITY-20261112-001` and `TERNARY-REPORT-JOINS-20261115-001` studied other kinds of sums or exact counting. The population search had no index rows.

The supplied objective has a conventional antecedent in discriminant analysis. This study restricts coefficients to membership in a group of anonymous categories, keeps all equally best smallest groups, and tests transfer and physical storage of the fitted choice. [Fisher's original paper](https://onlinelibrary.wiley.com/doi/10.1111/j.1469-1809.1936.tb02137.x)

## Population and genuine holdouts

Every example is an 8×8 binary bitmap. The upright L consists of its left and bottom strokes. The upright T consists of the full top stroke and a vertical stem through its indicated interior column (zero-based). Width, height and ink count are matched within every L/T pair. Only the generator knows the shape parameters. The table gives (width, height, T stem column) separately for every design.

| Shape design | Dimensions and stem | Lit pixels | Available during fitting |
| --- | --- | ---: | --- |
| A | (3,4,1) | 6 | Yes |
| B | (4,3,2) | 6 | Yes |
| C | (3,5,1) | 7 | Yes |
| D | (5,3,2) | 7 | Yes |
| E | (5,2,1) | 6 | No |
| F | (4,4,1) | 7 | No |

Rotate in clockwise quarter-turns inside the glyph's bounding box and translate its top left to each row/column pair in 0 through 3. No clipping or noise occurs. Fit only at 0° and 90° and at the eight positions where row plus column is odd. At a seen position and familiar turn q, train one six-pixel style from A/B by `(row+q)%2` and one seven-pixel style from C/D by `(row//2+q)%2`. For each selected style present both letters individually. This yields 64 presentations, 32 per class. The training order is a salted hash of raw pixels independent of class and pose. The remaining 704 images have a separate order and answer key. Pose and shape checks can inspect the generator and verify equality and coverage before freezing. No observed fresh label–feature association or prediction is available for design selection. The old 400 bitmaps and their normalized shapes must be disjoint from the new corpus. Neither primary blind shape occurs under any turn or translation of the training shapes. [Exact generator, ordering and panel](../../experiments/LEARNED-PATCH-GROUPS-20261122-001/LEARNED-PATCH-GROUPS-20261122-001-E001_groups/panel/manifest.json)

The **primary** analysis is exclusively on E and F, held out across *all* training positions and turns. It has 64 images per condition (other style at familiar pose, new position, new orientation, both), each split evenly by class and then by its two turns. The **secondary** analysis covers new bitmaps of fit-visible A–D on the same four conditions (64, 128, 128, 128). There are no inter-split bitmap duplicates. The same named angle always denotes a clockwise turn relative to the upright generator. Turns 180° and 270° never enter training or tuning. There is no tuning partition or hyperparameter search over these designs.

## What the learner receives and retains

Deliver only 64 bits in row-major order. The unchanged padded sensor counts the 81 overlapping two-by-two patches at the 16 raw bit patterns in order 0000 through 1111. Translation sharing is supplied. The group learner knows categorical counts and conditional reward, with no contact between its group search and the spatial interpretation of the category numbers. Every nontrivial division of these categories into two groups is eligible. No angle, coordinate field, template, rotated copy, rotation table, corner/line feature, number of lit pixels per category, class string, pose, sample ID or external encoder enters the model.

Each presentation first receives one guess. Acquisition uses the majority of past earned actions, with bit zero on a tie. Correctness gives the chosen bit if correct and the other bit otherwise. Each earned bit and the counts observed on that image are written into ternary knots. After exactly 64 receipts the learner computes its group selection using temporary arithmetic on the stored words. It erases the acquisition records, sets the deployment marking, writes the two class sizes and count totals for each of the 16 bins, and marks the selected partitions. The prior classifier instead updates and predicts online through its original interface. Each arm receives one correctness bit for each of the same 64 bitmaps; with a binary action this reveals the target equally well for any issued guess.

Each new physical reader has 40,494 three-place holdings in a fixed layout. There is one phase bit, 7,296 receipt bits, 14 bits for class counts, 416 bits for the class totals and 32,767 membership flags. A held triple has order mark, dock, read. Zero is 110 under both laws. One is 011 under even parity or 001 under not-all-equal. The read must be forced under the open relation from the other two distinctions. The open law, all prepared alternatives and rejects are checked in each new storage region. The two-state preparation alone fails K2. The adapter supplies addressing, summation, ranking, physical writing and voting. Retained training-dependent state lives in the holdings. The only physical checkpoint content outside the marked words is fixed schema, law and training capacity. The ordinary twin stores ordinary integers and independently implements the rank. [Learner and new holding checks](../../experiments/LEARNED-PATCH-GROUPS-20261122-001/LEARNED-PATCH-GROUPS-20261122-001-E001_groups/learner.py) · [Ordinary comparator](../../experiments/LEARNED-PATCH-GROUPS-20261122-001/LEARNED-PATCH-GROUPS-20261122-001-E001_groups/ordinary.py)

## Frozen grouping rule

For a subset S and image histogram h, its reading z is the sum of h over S. There are 32,767 unordered nontrivial partitions. Complementing S gives 81−z, preserving every group vote when its class means are also complemented. The code stores the side excluding bin 15 only to designate one representative.

1. Use each actual training presentation once. Compute the class means and population variances of each proposed sum. Ignore candidates with equal class means. Rank all others by squared difference of means divided by the sum of the two class variances, with a positive difference and zero summed variance ranking above every finite value.
2. If several candidates tie at the highest rank, retain those whose smaller side contains the fewest categories. Every remaining tied partition gets one vote. No ID order or geometric preference breaks that tie. No informative partition gives an empty committee.
3. On a new bitmap each marked partition votes for the class with nearer mean on its sum. An exact midpoint abstains. A tied vote, including an empty committee, issues bit zero. An untrained reader also issues zero. Ordinary bit zero means L. A separate fitted opposite convention reverses those meanings for the writer only. Where a tie is present, two donors need not give opposite guesses.
4. Label reversal preserves a label-symmetric group's membership and exchanges its class calibration. Test whether *which bins get grouped* actually depends on the association between pixels and reward by shifting the teaching bits cyclically by 17 presentations on the same 64-image stream. Each shifted arm also learns from its own guess/correctness. Record the changed teaching bits, the class-specific multiset of observed histograms, the selected partitions for all three schedules and the predictions. This is one predetermined pairing control.

## Blind scoring, controls and stopping judgment

Freeze the reviewed algorithm, weightings, primary gate, source files, images, and separate training and test keys before fitting. Each phase runs in its own process and directory, with overwrite refusal. Hash the fitted states before evaluating any queries, then hash all blind guesses before the scorer opens the test key. The private keys are accessible to their respective environment or scorer; the model receives no key or row handle. Record each release hash outside the runner before the next phase. Use both laws even if a training diagnostic or the other law appears unsuccessful. Fit the six physical group readers, three independent integer twins and two ordinary-convention predecessor readers under the same precommitted exposure budget. Compare chance by exact 50% expectation; balanced always-one behavior gives one perfectly correct class and one entirely wrong.

- Report true L and true T correct/total separately at 180° and 270°, for both seen and new positions. Report familiar orientations and held positions separately, for blind and fit-visible styles. The primary success criterion under each law is **strictly above half for every true class, held turn, position condition and each blind shape E/F**. There are 16 such cells per law, each with eight translations. Because translation sharing preserves histograms, those cells contain just eight shape–turn–class combinations before feature coincidences. Scores are finite coverage counts with one vote per distinct bitmap. The comparison to the previous approach is a separate observed gain or loss.
- In identical recipients and on fixed pixels, exchange the *entire learned word* in both directions between the separately trained ordinary and opposite conventions. Keep the recipient's label meaning fixed. Count original disagreements and ties, reciprocal donor agreement, sham, clear and exact restore. For normal-fit selection alone, erase just the membership flags, leaving class counts and calibration intact. Then mark every partition of the fitted smaller-side size, allowing each candidate to use its calibrated means from the same unchanged totals. The latter is a control for how much the supervised selection adds beyond all similarly sized groups. The two selection controls may reuse the actual read for a repeated histogram, with no test reward. All primary and previous readers issue a guess separately for every raw bitmap.
- Save complete fitted memberships, class totals, individual votes per distinct blind histogram, blind disagreements among tied best rules, and output ties. Count training-signature overlaps and report whether training-equivalent group choices diverge on the held shapes. Choose examples by the smallest bitmap digest per stratum, label, turn, condition and correctness. Use reconstructed reads from physical marks to explain both correct and wrong guesses, when present.
- Check the matched integer reader against each physical law on all three teaching schedules. Independently replay the fit, votes and scores. Check that permuting anonymous category identities transports fitted partitions and votes, including cases where the stored side becomes its complement. The earlier post-score clue may only be compared descriptively with the fitted membership after release. Similar decisions do not identify a unique rule. Performance on E/F cannot establish general font or rotation recognition.

Stop after the two laws reach the sealed evaluation. Preserve partial transfer, a failure, a tie with controls, or different outcomes by law. Do not refit, add turns, choose new variants, alter candidate families or relax the criterion in response to scores. This is a CPU-only finite census in standard-library Python, with exact integer ranking, one fixed architecture and no parameter sweep. Record wall time and high-water memory separately per stage.

## Design and referee sequence

Astra Max reviewed the grouping, complement equivalence, blind shape ancestry, causal tests and per-class success rule before the freeze. A second auditor reviews the execution path and checks the raw results. Formal scientific referee handoff follows the released comparison. [Prospective Astra advice](design_review/pre_freeze_advice.md) · [Advisor record](advisor.json)

