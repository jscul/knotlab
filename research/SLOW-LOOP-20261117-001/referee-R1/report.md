# Referee report SLOW-LOOP-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **Sound, and reproduced.** The moves keep the allowed states: a fresh brute force found no violation in 1.66 million ties and
  shadow knots, or in 19,741 rebuilds. The frozen verdict (reading 4, no charged win for G) stands, and so do GO's charged wins on
  both local cells at 3,200, CPU included. Every headline number recomputes.
- **One correction, a Narrowing.** Charged work (A91) leaves out part of the rebuild's cost: Python-side deduplication and set
  operations, O(m log m), never counted in `work`. With it counted:
  - GO's two charged local wins hold (0.15 → about 0.24 to 0.30; 0.23 → about 0.46 to 0.60);
  - GO's "work win" on `embed` 3,200 disappears (0.67 → about 1.1 to 1.35);
  - its work win on `local` w10 800 is uncertain (0.38 → 0.57 to 1.45);
  - G gets worse (0.84 → up to about 2.1), which only strengthens reading 4.

  The limitation line "Charged work does not depend on this" is not accurate.

## What holds (the referee's own checks)

- **The freeze and the order of the runs.** The pre-registration commit 8898f7117 is at 05:33:40 UTC. The runner then started each
  job in this order:

  | Job | Started (UTC) | What |
  | --- | --- | --- |
  | Re-tuning | 05:33:48 | after the freeze |
  | Grid extension | 05:49:45 | before the slow arms were tuned |
  | Policy tuning | 06:09:27 to 06:09:37 | `policies.json` written 06:09:57 |
  | Test | 06:10:09 | after the policies were fixed |
  | Stress | 06:10:32 | |
  | Post hoc tuning | 06:14:59 | after G came out lazy, before the test finished at 06:28 |
  | Post hoc runs | 06:15:23 | |

- **Seeds.** The ranges are disjoint (`job.py`): tuning 7,500,000+, policy 7,000,000+, oracle (GO) 7,600,000+, test 7,100,000+,
  stress 7,200,000+.
- **The engine's moves are sound by reading** (`slow_engine.c`):
  - *Propagation.* `propagate` is unit propagation for signed not-all-equal knots: two set members with equal effective values force
    the third. It is sound, and a probe stopped by its budget is never read as a refutation.
  - *Tie probe.* `tie_probe` tests one representative pattern per complement pair. The pattern set is closed under global flip, so
    this is enough. If "member d is the odd one" is refuted, then p and q differ in every allowed state, and the recorded parity
    1 ⊕ s_p ⊕ s_q is right.
  - *Shadow triple.* With exactly one representative refuted, `shadow_triple` writes a signed knot excluding exactly that pattern
    and its complement. With two or three refuted, it writes only the pair parities that every survivor shares.
  - *Reduction.* `sl_reduce` merges with parity-tracking union-find. Its cascade is right: two members in one class with equal
    effective signs force the third, by a tie with parity s_u ⊕ s_p ⊕ 1; with unequal signs the knot always holds. A knot is
    dropped only when it always holds or has become its tie, and canonical signs use the global flip.
- **The headline, recomputed with the referee's own code** (`referee_R_slow.py`, `.json`). The statistic is the median over
  instances of each instance's five-run geometric mean of `work`, against the better of NOV and PS, re-chosen in each of 10,000
  paired resamples, with 99% intervals. It matches the study in every cell:

  | Cell | G | GO | ST | GO R_CPU |
  | --- | --- | --- | --- | --- |
  | `local` w10 3200 (primary) | 0.838 [0.640, 1.069] | 0.150 [0.115, 0.186] | 0.521 | 0.33 |
  | `local` w40 3200 | 0.912 [0.770, 1.255] | 0.235 [0.187, 0.303] | 1.270 | 0.61 |
  | `local` w10 12800 | 0.745 [0.318, 1.082] | 0.116 [0.047, 0.162] | 0.363 | 0.28 |
  | `embed` 3200 | 0.982 | 0.671 [0.541, 0.816] | 0.898 | 1.33 |
  | `rand` 3200 / 800 / 12800 | 1.04 / 1.04 / 1.04 | 1.64 / 1.78 / 1.49 | ≈ 1.04 | 1.5 / 1.9 / 1.4 |
  | `block` 3200 / 800 | 1.03 / 0.99 | 1.88 / 2.14 | 1.61 / 2.28 | 5.4 / 6.2 |

  The ratios to static probing are GO/ST = 0.29 and 0.18 on the two local cells at 3,200, that is 3.4 and 5.5 times. At 12,800
  GO/ST is 0.32, or 3.1 times, slightly below the range quoted for 3,200.
- **Unsolved runs.** Four runs on one `embed` 800 instance stopped at the cap (NOV, G, Gx and GO), as the note says.
- **CDCL** (P9, P10). The 60 s interrupt never fired. From the wall times:
  - `local` w10 3,200: 50 of 50 within 60 s, median CPU 0.057 s (P9).
  - `rand` 3,200: 3 of 20 within 60 s, median 85.8 s CPU, 87.5 s wall (P10).

  Every model checks. The reading is right.
- **"P6 held only by its letter"** is a fair statement. On the primary cell, RND rebuilt the pattern 88.5 times (median) against
  G's 57. Its rebuild work was 1.33·10^7 incidences against 8.8·10^6, which is most of the gap in total work (2.39·10^7 against
  1.91·10^7). So P6's letter (G/RND ≤ 0.9) holds, but it holds because random targets found more ties that each cost a rebuild,
  not because attention chose better targets. At the eager policy attention is worse than random (GO/RNDO 1.18, post hoc).
- **Post hoc labels.** RNDO, the static probing tuned on `local` w10 and the attention diagnostic are labelled post hoc in the
  note, the decision and the objects row.

## The helper's fresh checks (`NOTES.md`)

One Claude helper wrote a brute-force oracle and an instrumented rerun, and called the study's code only as the thing under test.

**1. Soundness: no violation.**
- **Probes and rebuilds.** 8,000 small planted instances, n = 10 to 20, every family scaled down
  (`referee_task1_soundness.*`):
  - all 945,168 ties and 716,604 shadow knots written by `sl_probe` hold in every brute-forced allowed state;
  - all 19,741 rebuilds lift one for one onto the original allowed states;
  - every dropped knot always holds, and there are no contradictions;
  - mutant controls (wrong tie parity, flipped shadow sign) are caught.
- **Full `run_slow`.** 59,160 runs on 1,479 instances, with GO, RNDO, GO with shadows, ST and an extreme eager policy
  (`referee_task1c_runslow.*`). Every reported state checks, and the final patterns lift exactly.
- **At n = 800.** CaDiCaL as a third-party oracle confirms all 29,544 ties and 21,872 shadow knots (`referee_task1d_atsize.*`).
- **The stored runs.** 0 contradictions in 21,000.

**2. Identity until the first move: matches** (`referee_task2_identity.*`). All 4,752 stored runs without a rebuild equal NOV
exactly in flips, solved flag and fast work. In 1,391 fresh runs the state at the first rebuild equals NOV capped at the same flips.

**3. Charging (A91): differs in size** (`referee_task3_charging.*`).
- **The rebuild's C side** is charged fairly, at 5.7 ns per charged incidence against 5.3 for the fast loop.
- **What `work` does not count.** The Python side of `reduce_pattern` and `build` does real O(m log m) work that is never counted:
  - `np.unique` for deduplication;
  - `np.isin` for the probed flags;
  - `np.union1d` on a probed-key set that grows over the run;
  - `np.unique` of the roots.

  The guided order's `qsort` is also charged as if it were linear.
- **The size, for GO on `local` w10 3,200.** 200 instrumented reruns reproduce the stored runs bit for bit. The uncharged sorting
  alone is 1.89·10^6 operations per run, which is 1.2 times `work_rebuild` and 0.58 times the total.
- **Corrected R.** The low end counts one unit per sort operation; the high end counts rebuild CPU at the fast loop's rate.

  | GO, cell | Reported R_work | Corrected R | R_CPU (the whole run) |
  | --- | ---: | ---: | ---: |
  | `local` w10 3,200 | 0.15 | 0.24 to 0.30 | 0.33 |
  | `local` w40 3,200 | 0.23 | 0.46 to 0.60 | 0.61 |
  | `embed` 3,200 | 0.67 | 1.09 to 1.35 | 1.33 |
  | `local` w10 800 | 0.38 | 0.57 to 1.45 | 1.63 |

- **G's targets.** G's attention reading costs 21 to 33 ns per charged incidence, against 5 to 7 for RND and GO, so its selection
  cost is understated too. Counting rebuild CPU, G on the primary cell goes from 0.84 to about 2.1.
- **The frozen verdicts are safe.** The pre-registration's decision rule uses the whole-run CPU as well ("The verdicts use the
  total"), and R_CPU includes everything. So the frozen charged-win verdicts do not change: GO's two local cells are charged wins
  in CPU too, and `embed` 3,200 was already only a "work win".
- **What changes.** The work-only figures and the sentence "Charged work does not depend on this". **Narrowing.**

**4. Comparator: matches** (`referee_task4_comparator.*`). The helper's own Novelty+ (5 runs on 20 test instances) gives median
flips of 1.09 [0.70, 1.90] times the study's NOV arm on `local` w10 3,200 and 0.92 [0.76, 1.25] on `rand` 3,200.

**A side finding, not a soundness issue.** `planted_embed` has no retry guard. A tiny sub-pattern whose hidden values are all equal
loops forever while its memory grows: 14 GB before the helper stopped it. This cannot happen at the study's sizes, but it should be
guarded.

## GO's oracle tuning, flagged?

- **Where it is flagged.** GO was tuned on `local` w10 at n = 800, the same family as the primary cell, on disjoint seeds. The note
  says "GO, tuned on `local` window 10", the decision says "the policy tuned on `local` window 10 (GO)", the objects row says "the
  oracle-tuned eager GO", and the position table calls it "a charged win for the oracle-tuned policy".
- **Where it is only implied.** The final report and the intuition entry ("total work fell to 0.15 and 0.23 … on two local
  patterns, one of them never seen") imply it, without saying the eagerness was tuned on the first one.
- **Suggestion.** "with its eagerness tuned on the first". **Not a block.**

## Prior work and words

- **The objects gate passes.** `track.py objects-gate research/SLOW-LOOP-20261117-001/preregistration.md` prints "prior-work line:
  ok".
- **The literature named is the right one.** Failed-literal probing, equivalent-literal substitution, learned implied clauses and
  inprocessing are the standard names for these moves. The note's own "known inference" framing and "CaDiCaL solves local in
  0.06 s" are accurate.
- **What was not checked.** The referee did not run a separate literature search for this study; the framing claims no novelty
  beyond the test of the owner's attention signal.
- **Words.** The glossary's words are used (tie class, shadow, distinction, knot, meeting pattern).

## Fixes for the thread (listed for the owner, not folded in)

1. **Charging (A91).**
   - Say that `work` omits the Python-side rebuild operations: deduplication, probed-key sets, root unique, and qsort charged
     linearly. Drop "Charged work does not depend on this".
   - Qualify GO's "work win" on `embed` 3,200 (which does not survive the omitted cost) and on `local` w10 800 (uncertain).
   - GO's charged wins on both local 3,200 cells stand, CPU included.
   - Fold into A91's history that the measure under-counts rebuilds.
   - **Narrowing**, a correction for docs/CORRECTIONS.md.
2. **G's reading.** Note that counting rebuild CPU makes G worse on the primary cell (about 2.1), which only strengthens reading 4.
   **Not a block.**
3. **Flag GO's tuning family** in the final report and intuition entry ("eagerness tuned on `local` w10"). **Not a block.**
4. **Guard `planted_embed`** against an all-equal hidden sub-state (an infinite loop at tiny n). **Not a block.**
5. **For direction #1.** The lazy policy pays mostly in rebuilds: G's rebuild work is about 46% of its total on the primary cell,
   from 57 rebuilds, against GO's 10. A loop that earns its budget should batch finds before rebuilding. A design note, not a
   correction.

## How the work was split

- **The referee.** Read the pre-registration, the note, the decision and the engine. Recomputed every ratio, checked the job order
  and seeds, read the CDCL wall times, checked the P6 rebuild counts, and checked the labels and the objects gate.
- **One Claude helper.** Brute-force soundness, identity, an instrumented charging audit and its own Novelty+.
- **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_R_slow.py` and `.json`: the referee's recomputation.
- `NOTES.md` and the `referee_task*` scripts with their JSON: the helper's checks.
