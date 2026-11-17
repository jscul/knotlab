# Referee report SPEC-MERGE-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Frozen reading 5, no win anywhere, holds:
- Every number recomputes, every reported solution checks on the original knots, and the planted state never reached a decision.
- Gate D replicates in an independent engine, and against an activity-matched control too.
- No speculative arm beats even its own fast loop anywhere, so the verdict does not depend on the comparator.

The fixes concern what the losses are attributed to and how the undo is described:
- **What the random-cell losses measure.** On the random cells A and A0 almost never merged, so their losses there are the cost of
  watching, not of merging.
- **What the undo did.** The undo table merges two checks. The contradiction check caught most wrong rounds at once (61% and
  78%). The stall test on its own kept wrong rounds at least as often as right ones.
- **Where precision was high.** "The evidence reaches precision near 1 only where proofs already work" is contradicted by `rand`
  3.0: precision there was 0.98, and the proof-based loop changed nothing.
- **"The first signal."** It should say "in this program", since backbone-guided local search is such a signal in the literature.

## What holds

- **Order.** The UTC times come from the runner's own files:

  | Event | Time (UTC) |
  | --- | --- |
  | Gates S1–S5 output | 09:32:22 |
  | Freeze, 8147c8202 | 09:32:24 |
  | Gate D | 09:32:33 to 09:32:40 |
  | `gate_summary.json` | 09:33:38 |
  | Fixed-arm test launched | 09:33:51 |
  | Tuning | 09:32:37 to 09:50:50 |
  | `policies.json` | 09:50:59 |
  | Tuned-arm test | 09:51:10 to 10:06:05 |
  | Fixed-arm test ends | 10:29:12 |
  | Close, a5fa81d9e | 10:32:24 |

  - **The code that ran is the frozen code.** All three stages ran `job.py` with sha256 `e01054b4…`, the committed file. The only
    change after the freeze is `analyze.py` reading the test's two directories.
  - **Seeds are disjoint:** gate 8,700,000+, tuning 8,800,000+, test 8,900,000+, calibration 9,500,000+. NOVt's settings are
    EARN-BUDGET's re-tuned ones (`retuned.json`: (0.7, 0.005), (0.6, 0.02) and (0.8, 0.01)), chosen on its own tuning instances.
  - **The two-part test ran on the same instances and initial states.** The tuned arms' runs without a merge reproduce NOV's flips
    exactly; see below.
- **The planted state reached no decision.**
  - **Where it is read.** It is drawn in the generator, and read only after the loop ends (`spec_merge.run_spec`, the diagnostics
    block) and in `gate_d`. It does not appear in the C engine or in the fast- and slow-loop drivers.
  - **The tuning choice.** Recomputed by the referee from charged work and the least violated count alone, it matches
    `policies.json`: A is setting 12 (8n, ≥ 4, 0.5%, patience 1), Aloc is setting 16 (8n, ≥ 4, 10%, 1). The precision stored in
    the tuning runs played no part.
- **Every reported solution checks.**
  - **The stored flags.** Of the 11,050 test runs, 10,893 are solved, and none lacks `verified = true`.
  - **The referee's rerun** (`referee_verify.py`, `.json`). Every one of the 2,646 solved runs that made a speculative merge was
    rerun with the study's driver from the same seeds, across all four cells, the eight merging arms and controls. Each
    reproduced its stored flips, charged work and merge count exactly. Each state satisfies every original knot by the referee's
    own test, on freshly generated knots, and every planted state does too.
- **Gate S1–S5.** Rerun today, `check.py` passes all five, with the same counts as the output committed at the freeze (FAILS: 0).
- **Gate D, recomputed from `gate/results.jsonl`** (`referee_R_spec.json`). Every value matches the note:
  - **`rand` 2.1.** The differences are 0.113 [0.048, 0.175], 0.106 [0.050, 0.166] and 0.125 [0.073, 0.183] at 4, 8 and 16 epochs.
  - **`local` w10.** The tied shares are 0.38, 0.54 and 0.59 against 0.23, 0.23 and 0.22, a ratio of 1.64 to 2.68, and the lower
    end of every difference is at least 0.074.
  - Both frozen rules pass.
- **Gate D, replicated in an independent engine** (`referee_gate.c`, `.py`, `.json`). The referee's own Novelty+ (0.7, 0.01) ran
  from its own initial states, with its own stability count and its own pair probe, on the same 30 gate instances per cell. It drew
  four controls (k = 1% of n each):

  | Cell, epoch | Top pairs | Uniform (the gate's control) | Active (the test's control) | Stability ≥ 1 | Top pairs' members re-paired |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | `rand` 2.1, 4 | 0.643 | 0.563 | 0.554 | 0.614 | 0.531 |
  | `rand` 2.1, 8 | 0.690 | 0.594 | 0.565 | 0.617 | 0.514 |
  | `rand` 2.1, 16 | 0.775 | 0.671 | 0.598 | 0.732 | 0.622 |
  | `local` w10, 4 / 8 / 16: tied share | 0.42 / 0.49 / 0.62 | 0.24 / 0.24 / 0.22 | 0.24 / 0.25 / 0.24 | 0.29 / 0.31 / 0.31 | — |

  - **Against the gate's own control.** On `rand` the difference is 0.080 [0.026, 0.130], 0.096 [0.027, 0.163] and 0.103
    [0.054, 0.154]. The study's 0.11 to 0.13 is the same signal from other runs. It passes the frozen rule (≥ 0.10, lower end above
    0) only at epoch 16, by 0.003.
  - **The gate's control was uniform, not activity-matched.** Activity matching was used for the test arms' controls. Against
    activity-matched pairs the difference is larger: 0.09, 0.13 and 0.18 on `rand`, and 0.18 to 0.38 in tied share on `local`.
    Pairs still moving agree less often. So the uniform control was the harder one, and fair.
  - **The signal is about pairs.** Re-pairing the top pairs' members at random drops agreement to 0.51 to 0.62, so the signal does
    not come from single well-placed distinctions.
  - **What the ranking adds.** Against pairs that moved together at least once (stability ≥ 1), the ranking by stability adds only
    0.03 to 0.07 on `rand`, and 0.13 to 0.31 in tied share on `local`.
- **The headline, recomputed with the referee's own code** (`referee_R_spec.py`, `.json`).
  - **The statistic.** Per instance, the geometric mean of five runs' charged work; per cell, the median; R against the better of
    NOV and NOVt, re-chosen in each of 10,000 paired resamples, with 99% intervals.
  - **Every R and ratio in the note's table recomputes.** The point values match exactly, and the intervals match within
    resampling noise. Examples:
    - A: 1.175 [1.13, 1.32] on the primary;
    - AE: 2.26 [1.70, 6.28];
    - Aloc: 1.41 [0.86, 1.96] on `local`;
    - Gpr: 0.154 [0.106, 0.192] on `local`, with CPU 0.138;
    - A/Arand: 0.32 [0.21, 0.59] on `local`;
    - Aloc/Arandloc: 0.78 [0.52, 1.17].
  - **The verdicts.** No speculative arm is a charged win in any cell, so the reading is 5, no random cell won, and no publication
    hold arose.
  - **The undo table** (from `round_log`) and the merge counts match.
- **The verdict does not depend on the comparator.** Against the arms' own fast loop, Novelty+ (0.7, 0.01), no speculative arm
  meets the frozen win tier anywhere. The best is Aloc on `local` w10, 0.89 [0.59, 1.21]; A is 0.99 there and 1.09 to 1.14 on the
  random cells.
- **The comparator on `rand` 3.0.**
  - **NOVt.** (0.6, 0.02) is EARN-BUDGET's choice, not at a grid edge.
  - **The fast loop's handicap.** NOV costs 2.06 [1.83, 2.70] times NOVt there, so most of the arms' 2.25 to 4.40 is the fast
    loop, as the note says.
  - **probSAT is left out.** F is the better of two Novelty+ settings only, without the probSAT the earlier studies included. A
    stronger comparator could only enlarge the losses.
  - **On `local` w10** NOV costs 1.58 [1.03, 2.18] times NOVt, so there too the frozen R carries a fast-loop handicap of about 1.6.
    The note gives Aloc's 0.89 against its own loop beside it.
- **Censored runs.**
  - **How they are counted.** An unsolved run counts its work at the cap, a lower bound. Cells with more than 5% censoring are
    flagged as bounds.
  - **Why they stalled.** Every censored run of AE and Arand had kept a wrong round: 26 of 26 for AE on `rand` 2.1, 37 of 37 for AE
    on `local`, and 45 of 45 for Arand on `local`.
  - **The direction of the bounds.** They make the arms' losses firmer. A/Arand's 0.32 on `local` is an upper bound, since Arand's
    18% censoring is in the denominator.
- **The proof-based loop changed nothing on the random cells.** Gpr's flips equal NOV's in every run: 250 of 250, 250 of 250 and
  100 of 100. Its losses there (1.59 to 6.20) are the cost of probing that found nothing usable.
- **Prior work.** `objects-gate` prints "prior-work line: ok". The three neighbours are named correctly: Walshaw 2002, multilevel
  refinement for SAT; Zhang 2004, backbone-guided local search; and survey-propagation decimation.
- **Not overstated in its title and limits.**
  - The title, the headline and the "Retire in this form" row are scoped to this evidence and this undo rule.
  - The limitations name one evidence rule, one undo rule and the permanence of kept rounds.

## 1. On the random cells A and A0 paid for watching, not for merging (Narrowing, attribution)

- **How rarely they merged.** On the three random cells A, A0 and Aloc merged in 3 to 6% of runs.
- **The runs without a merge.** In every one, the arm followed Novelty+'s trajectory exactly: the same flips in 235 of 235, 236 of
  236, 241 of 241 and 96 or 97 of 96 or 97 runs. It cost 1.11 to 1.14 times NOV's work (A, epochs of 8n) and 1.23 to 1.26 (A0,
  epochs of 4n) for the counters alone.
- **So the frozen losses of A and A0 on random cells are the cost of watching.** On `rand` 2.1 and at 12,800 they are 1.17 to
  1.34. Against NOV, on all three random cells, they are 1.09 to 1.26.
- **Only AE merged in most runs:** 76% on `rand` 2.1 and 70% at 12,800, against 44% on `rand` 3.0.

The decision's "at a precision of about 0.7, unproved merges cost 1.17 to 2.26 times Novelty+" therefore reads A's watching cost
as a merge cost.

**The evidence bought nothing at the point of use on random patterns.**
- **The note's sentence.** "On `rand` the arms rarely merged at all" overlooks AE, which did merge.
- **AE against its control.** AE was not better than its activity-matched random control: AE/AErand is 1.17 [0.85, 3.04] on `rand`
  2.1, 1.14 [0.95, 1.33] on `rand` 3.0 and 1.00 [0.89, 1.32] at 12,800.
- **Precision against cost.** Its precision was higher (0.70 against 0.60 on `rand` 2.1; 0.66 against 0.56 at 12,800), but that did
  not lower the cost.

**A fair wording.**
- *Random cells.* "Watching alone cost 1.1 to 1.3 (A and A0 merged in at most 6% of runs). AE, the one arm that merged in most runs,
  at precision 0.70, cost 2.26 (a bound; 2.19 against its own fast loop), and was no better than merging random active pairs."
- *The intuition entry.* "The search paid for every one" should give way to the same split.

## 2. The undo table merges two checks; the stall test alone was no better than blind (Narrowing, a number)

The note's "kept 449 of its 4,829 rounds with a wrong merge (9%)" counts every undone wrong round as the stall test's work. But a
round whose merges contradict each other or the knots is undone at once by the contradiction check, before the stall test reads
it. Once a wrong round has been kept, a later round consistent with the planted state can also contradict. The stored runs count
the two kinds of undo per run but not per round.

So the referee reran the merging arms (`referee_undo.py`, `.json`, 1,264 runs) with the study's driver unchanged and a wrapper on
`reduce_pattern` that records each rebuild's contradiction flag. Every rerun reproduced its stored flips, work and round log
exactly:

| Arm, cell | Wrong rounds | Undone by contradiction | Reached the stall test | Stall test kept: wrong | Stall test kept: right |
| --- | ---: | ---: | ---: | ---: | ---: |
| AE, `local` w10 | 4,829 | 2,957 (61%) | 1,872 | 449 (24.0%) | 375 of 2,116 (17.7%) |
| A0, `local` w10 | 151 | 3 | 148 | 30 (20.3%) | 289 of 2,430 (11.9%) |
| Aloc, `local` w10 | 876 | 159 | 717 | 187 (26.1%) | 163 of 828 (19.7%) |
| A, `local` w10 | 200 | 7 | 193 | 27 (14.0%) | 328 of 2,427 (13.5%) |
| AE, `rand` 2.1 | 2,879 | 2,243 (78%) | 636 | 85 (13.4%) | none were right |

- **The stall test is no better than blind.** In every `local` arm it kept the wrong rounds it judged at least as often as the
  right ones: 1.04 to 1.7 times as often.
- **The contradiction check did the useful filtering.** It undid 61% of AE's wrong rounds on `local` and 78% on `rand` 2.1.
- **It also undid right rounds.** AE's 2,071 undone right rounds on `local` are 1,741 stall undos and 330 contradictions, which
  arose only because an earlier wrong round had been kept.
- **What this changes.**
  - The conclusion that the undo is blind and A93 is overturned stands, and is firmer for the stall test itself.
  - The figure "kept 9% of wrong ones" (note part 4, decision headline, A93's Challenge and the final report) should give the split.
  - The lesson "a mutation needs a check of its own" is supported directly. The one check of its own in the loop, the
    contradiction check, did most of the filtering, which bears on direction #3.

**Not a block** for the theory under test, since it strengthens the result, but it corrects a published number.

## 3. High precision was reached where proofs find nothing (Narrowing, wording)

- **What the summaries say.**
  - The decision's position table: "Unproved merges need precision near 1, which the evidence reaches only where proofs already
    work".
  - The note's part 3, of `rand` 3.0 and `local` w10: "Proof-based probing gets the same structure far more cheaply and
    completely".
- **`rand` 3.0 contradicts both.**
  - AE's median merge precision there was 0.98.
  - The proof-based loop changed nothing: Gpr's flips equal Novelty+'s in all 250 runs, and its R is 6.20.
- **What failed there instead.**
  - Rounds of 320 merges were almost never wholly right: 27 of 556.
  - The search was rarely stuck: Novelty+ (0.7, 0.01) solves in about 10 flips per distinction, 1.2 of A's epochs.
- **A fair wording.** "Rounds of 16 to 320 unproved merges need precision near 1. On `rand` 3.0 the evidence was 0.98 right per
  merge where proofs found nothing, but rounds of 320 were still wrong, and smaller rounds with the search stuck were not reached."
  The G15 row's "acting on it without proof fails" should read "failed here".

## 4. "The first signal": in this program (Narrowing, wording)

- **The claim.** "The first signal from the fast loop's history that predicts structure" appears in the decision, the note and the
  goals checkpoint.
- **Why it needs scoping.** It should say "in this program". Backbone-guided local search (Zhang 2004), a neighbour the note itself
  names, estimates pseudo-backbones from the search's own local minima: a signal of the same kind in the literature. The
  intuition entry already says "in this line".
- **The size of the signal.**
  - The number beside each use, 0.66 to 0.75 against 0.55 to 0.63, is right.
  - The replication puts the difference at 0.08 to 0.10 against the same control.
  - So "predicts the planted relations about 0.1 more often than random pairs" is the claim the data carry on random patterns.
  - On the local pattern it is the provable tie share, 2.5 times random, which replicates (1.8 to 2.8 times).

## 5. Smaller points (Not a block)

- **CPU.** "R_CPU within about 15% of R_W" is closer to 25%: AE at 12,800 is 1.85 against 1.43, and A on `local` 1.56 against
  1.88.
- **Dr (context).** Its flips are 0.71 to 1.52 times the better Novelty+'s, not 0.80 to 1.53: Dr seed 1 on `local` is 0.71.
- **The frozen S1 line.** It says 783,040 merges and 17,182 undos at n = 800, but the gate output committed with it says 544,573
  and 11,378, and the note quotes the latter. The referee's rerun gives 544,573 and 11,378 again, so the pre-registration's figure
  is from an earlier run before the freeze.
- **Words.** No spatial word is used for the program's objects.

## Fixes for the thread (listed for the owner, not folded in)

1. **The random cells' losses.** Attribute A's and A0's losses on random cells to watching (no merge in 94% or more of runs; the
   same flips as Novelty+). Say that AE, the one arm that merged there, was no better than its random control (decision headline,
   note "The evidence matters only in one arm", goals checkpoint, intuition entry). **Narrowing.**
2. **The undo numbers.** Split the undo numbers into the contradiction check and the stall test. The stall test kept 24% of the
   wrong rounds it judged against 18% of the right ones (AE, `local`), so "kept 9% of wrong ones" should not stand alone (note part
   4, decision, A93's Challenge, final report). **Not a block** (it strengthens the result).
3. **Precision and proofs.** Withdraw "the evidence reaches [precision near 1] only where proofs already work" and "proof-based
   probing gets the same structure" for `rand` 3.0 (precision 0.98; Gpr changed nothing). Scope "needs precision near 1" to the
   round sizes tried, and the G15 row's "fails" to "failed here". **Narrowing.**
4. **"The first signal."** Add "in this program" to "the first signal from the fast loop's history that predicts structure"
   (decision, note, goals checkpoint), with Zhang 2004 as the literature's instance. **Narrowing** (wording).
5. **Small figures.** The CPU tolerance, Dr's flips range and the frozen S1 figure. **Not a block.**

## How the work was split

- **The referee:**
  - read the pre-registration, the note, the decision, A93 and the code (`spec_merge.py`, `job.py`, `choose.py`, `analyze.py`);
  - recomputed gate D, the tuning choice, every test ratio and the undo split from the raw results;
  - replicated gate D in an independent engine with three more controls;
  - reran every solved merging run and checked its state;
  - reran the merging arms to split the undos by check;
  - reran the gates and the objects gate.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_R_spec.py` and `.json`: the recomputation from the raw results.
- `referee_gate.c`, `referee_gate.py` and `referee_gate.json`: gate D in the referee's own engine.
- `referee_verify.py` and `.json`: every solved merging run rerun, with its state checked.
- `referee_undo.py` and `.json`: which check undid each round.
