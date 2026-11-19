# Referee report JOIN-GROWTH-001-R1 (fresh growth code; the study's case list and knot sizes read as data)

**Verdict: confirmed with two Narrowings, a scorer fault that changes no verdict, and one count to fix. No Block.**
- **The single-ring product law stands as frozen.** Every predicted annihilator re-scores "holds" under the frozen rule.
  - **An independent regrowth reproduces the study's counts.** The referee regrew 85 starts with its own engine, and every round of
    every start equals the study's count. On the referee's shorter horizon, 68 of the 74 predicted annihilators "hold" and 6 are
    "unsettled"; none fails.
  - **The listed P1 start that job.py never ran** (ring 9, s = 3) was grown by the referee, and its predicted annihilator holds from
    round 0, tested on 29 rounds.
- **The two-ring reading t^(−3/2) is pre-asymptotic.**
  - **The data agree with the exact model.** The referee grew the 5–9 join one round past the study's horizon, to round 17, and
    every round equals the exact cluster count that RING-PAIR-20261119-001 proposes (checked with the referee's own code).
  - **That count's exponent is −5/2.** Its local exponent is −1.42 at round 16, −2.00 at 50 and −2.46 at 700.
  - **So two rings grow like C λ^t t^(−5/2), with higher rates than the α = −3/2 fits.** For example 2.24, not 2.19, for 5–9.
  - **This also corrects the referee's own early read.** A thread message said one round past the horizon "favours the t^(−3/2)
    reading". That was the same pre-asymptotic local exponent.
- **The memory amendments are clean.**
- **The post hoc section is labelled and scored correctly.** Its eight chain, tree and fork starts regrow exactly, and their stated
  relations hold. One of the three law-2 "unsettled" cases, grown one round past, now holds (Section 5).

## 1. The exact-annihilator scoring in merge.py (the owner's first point)

**The frozen rule** (pre-registration, "Decision rules"):
- **holds:** the predicted annihilator annihilates the grown counts from some t₀ ≤ 12, with at least three rounds tested past its
  order;
- **unsettled:** the horizon gives fewer than three such rounds;
- **fails:** otherwise.

**merge.py's `verdict`** first takes `annihilated_from`. That value is job.py's least t₀ with at least three rounds tested. If it is
≤ 12, the verdict is "holds", which is correct. Otherwise it falls into a short-horizon branch: when fewer than three rounds remain
past the order from round 12, it returns "unsettled" if there is no violation or the last violation starts after round 12, and
"fails" otherwise. **That branch inverts the frozen rule:**
- **A late violation becomes "unsettled".** A violation after round 12 means the relation cannot hold from any t₀ ≤ 12. The frozen
  rule says "fails"; merge.py says "unsettled".
- **An early hold becomes "fails".** A relation that holds from t₀ ≤ 12 with only one or two rounds tested should be "unsettled";
  merge.py says "fails".

`posthoc.py`'s `score` implements the frozen rule correctly.

**No verdict changes.** The referee re-scored every predicted annihilator with the frozen rule. On the recorded counts all 74 (26 in
A1–A6 and 48 in P7) are "holds", the same as merge.py, with t₀ ≤ 4 and at least 3 rounds tested; the three tightest are D-D starts
with exactly 3. The short-horizon branch was never reached. **Not a block**, but merge.py should be fixed before it is reused.

## 2. The memory amendments (the owner's second point)

- **The same code.** `job_mem.py` yields the same cases from `job.py` and calls the same `job.run`, with the same caps: 80 rounds,
  250,000 junctions, 900 s.
- **The reruns hit the cap that was frozen.** Every rerun stopped on the junction cap, well inside the time cap (45 to 304 s), so
  only the memory limit differs.
- **Overlapping cases are identical.** Four two-ring cases ran in both the main run and `runs/join-growth-mem` (C-5-5-K, C-5-5-P1,
  C-5-7-D, C-5-9-D). They give identical outcomes, rounds, junction counts and per-round counts.
- **merge.py uses a rerun only when needed.** It takes a rerun's record only when the main record is not ok, which matches the
  amendment.
- **No selection by result.** The cases were rerun because of memory, not because of anything in their results.
- **The amendments are clean.**

## 3. Independent regrowth

The referee's lean engine (`lean.py`) is a copy of its own complete-round growth with the GF(2) basis dropped. On six starts of four
families its counts equal the full engine's.

`referee_join_regrow.json` covers A1 to A6, B (except chord-02), E, and the D starts on D and K. Each start was grown to 60,000
junctions or 80 rounds (the study's cap: 250,000). The frozen rule was applied to the referee's own counts.

| Family | Starts | Equal to the study's counts on every common round | Frozen rule on the referee's counts | Rounds reached |
| --- | --- | --- | --- | --- |
| A1 | 6 | 6 | 6 hold | 21 to 58 |
| A2 | 8 | 8 | 8 hold | 19 to 28 |
| A3 | 3 | 3 | 3 hold | 27 to 40 |
| A4 | 2 | 2 | 2 hold | 27 to 31 |
| A5 | 5 | 5 | 5 hold | 18 to 26 |
| A6 | 2 | 2 | 2 hold | 19 |
| B | 5 | 5 | (no annihilator predicted) | 18 to 80 |
| D on D | 36 | 36 | 30 hold, 6 unsettled | 16 to 24 |
| D on K | 12 | 12 | 12 hold | 23 to 56 |
| E | 6 | 6 | (no annihilator predicted) | 80 |

- **The six "unsettled" are a horizon effect of the referee's smaller cap,** not a disagreement. They are the D-D starts with b = 2
  (at r, r1 and r2, with a = 1 and 2). Their relations start at t₀ = 4, and the referee's runs reach only 0 or 2 rounds past the
  order. On the study's longer runs, the same rule gives "holds" with exactly 3 rounds (Section 1).
- **Six starts have a junction of demand zero** (B-chord-01 and five E starts). There the lean engine is not exact in general, yet
  their counts still equal the study's on every round.

**The pre-registered P1 start that was never run.** P1 lists seven starts: rings of 7 and 9 with s = 1, 2, 3, and s = 4 on the ring
of five. job.py runs six; ring 9 with s = 3 is missing. The referee grew it (`referee_join_n9s3.json`): **it holds as predicted** (`referee_join_n9s3.json`).
- **The annihilator x¹³ − x⁴ − (1 + x)³** (that is x^(n+s+1) = x^(s+1) + (1 + x)^s with n = 9, s = 3) annihilates the counts from
  t₀ = 0, tested on 29 rounds. This is "holds" under the frozen rule.
- **The growth.** It reached 272,214 junctions at round 41. The predicted rate is 1.2191; the last ratio is 1.1598, still
  approaching it, as the relation implies.

**A count.** "All 27 sharp, medium and risky tests" should read **26**: A1 to A6 hold 6 + 8 + 3 + 2 + 5 + 2. That is also
"74 = 26 + 48" in the results.

## 4. The two-ring joins and t^(−3/2) (with RING-PAIR-20261119-001)

**Grown past the study's horizon.** The referee grew the 5–9 join with its own engine to round 17. The study stopped at 16 (348,021
junctions); round 17 has 344,740 new junctions (692,761 in all). The run was stopped during round 18, which would need about 1.4
million junctions, beyond the memory cap.
- **The rounds the study also grew** (0 to 16) equal the study's counts.
- **Every round 0 to 17 equals the exact cover-model count**, computed by the referee's own code (RING-PAIR referee report).

**What the exponent is.** Fits on rounds 8 to 17 leave α free at −1.10. A fit on rounds 10 to 17 gives −1.18. Local exponents from
three consecutive rounds rise in size:
- −1.07 at 10, −1.24 at 14, −1.39 at 15, −1.42 at 16;
- in the exact count beyond the growth: −1.54 at 20, −1.75 at 30, −2.00 at 50, −2.23 at 100, −2.36 at 200, −2.43 at 400 and −2.46
  at 700.

**The limit is −5/2, the rooted-to-unrooted exponent of lattice animals on a tree-like map, not −3/2.** Every two-ring join the
study grew shows the same thing in the exact count (5–5–K, 5–5–P1, 5–7, 7–7, 5–9: −2.44 to −2.46 at t = 499).

**Why the −3/2 forecasts worked.** At these rounds the one-step forecast is insensitive to the exponent. From rounds 14 to 16, round
17 is forecast within +0.06% with α = −3/2, within −0.28% with α = −1, and within +0.24% with α = −1.75.

**The rates.** They are therefore higher than the α = −3/2 fits. With α = −5/2 the exact counts give 2.868 (5–5–K), 2.427 (5–5–P1),
2.382 (5–7), 2.241 (5–9) and 2.186 (7–7), against 2.79, 2.36, 2.32, 2.19 and 2.14.

**The fitted P9 still holds as frozen.** No short recurrence; fitted λ above 1.5; λ falling with ring length; fitted α in [−2, −1].
Only the reading changes.

## 5. The post hoc section (the owner's third point)

- **Labelled as post hoc, and scored correctly.**
  - The law 1 / law 2 split (28 holds, 14 unsettled and 5 fails under law 1; 44 holds and 3 unsettled under law 2) reproduces from
    the recorded counts with the frozen rule.
  - The refinement (a knot of demand 1 with one surplus distinction renews) was found on those same 47 cases, as the note says.
- **The timing of the written predictions is self-attested.** `prediction_chain4.txt` and `prediction_2.txt` carry timestamps
  (23:53 and 00:01 UTC) inside the files. They were committed in the same commit as the runs, so their order cannot be checked from
  the record.
- **The post hoc chains, trees and fork, regrown** (`referee_join_posthoc_chains.jsonl`, `referee_join_posthoc_fork.jsonl`).
  The referee regrew the eight post hoc starts with its own engine: five chains (5–3, 7–3, 9–3, 5–4, 7–4), two tree chains (depths 5
  and 6) and the fork.
  - **Every count equals the study's on every common round**, over 24 to 36 rounds. The fork was regrown at a cap of 100,000
    junctions, to round 26 of the study's 29.
  - **Every stated annihilator holds under the frozen rule:** from t₀ = 1 on the chains, and t₀ = 2 on the trees and the fork,
    with 14 to 25 rounds tested.
- **The three law-2 "unsettled" cases: one grown one round past** (addendum, 2026-11-19, `referee_join_posthoc_dp1.jsonl`).
  D-P1-at-r-a2-b2 was grown to round 20 under a 24 GB cap, after a wait for memory.
  - **Every count equals the study's on its 19 rounds.**
  - **The stated law-2 relation now scores "holds" under the frozen rule:** from t₀ = 4, with 3 rounds tested.
  - **The other two, D-P1-at-r1-a2-b2 and D-P1-at-r2-a2-b2,** are the study's symmetric variants of the same start. They were not
    grown and stay "unsettled".

## 6. Other claims

- **P8.** All 93 D starts grow faster than the bare ring, at 1.1347 (D-K-none-b0) to 1.6851 (D-D-at-r2-a2-b2). The chord on ring
  knots 0 and 1 closes in five rounds. The chord on 0 and 2 is unread (over 6 GB).
- **P10.** Six of six no-ring starts have dimension 1 or 2.

## Corrections for the owner (listed, not folded in)

1. **The two-ring exponent.** "They fit λ^t · t^(−3/2) closely, the mark of a menu that contains itself", with rates 2.14 to 2.79.
   - At these horizons it is a pre-asymptotic fit.
   - The exact cluster count, which the growth matches round for round through round 17 on 5–9, has exponent −5/2 and rates 2.19
     to 2.87.
   - RING-PAIR-20261119-001 already narrows this. **Narrowing; not a block.**
2. **merge.py's short-horizon branch** inverts "unsettled" and "fails". It changes no frozen verdict. Fix it before reuse. **Not a
   block.**
3. **"27 frozen single-ring tests" should be 26**, and **P1's run omitted one listed start** (ring 9, s = 3). The referee's run of it
   is above. **Narrowing (count); not a block.**
4. **The referee's own thread message** saying one round past the horizon "favours the t^(−3/2) reading" was the pre-asymptotic
   local exponent. This report replaces it.

## How the work was split

- **The referee:**
  - read the decision note, the pre-registration, `merge.py`, `posthoc.py`, `job.py`, `job_mem.py` and `contract.json`;
  - wrote `lean.py` and `referee_join.py` (validate, regrow, n9s3, posthoc, tworing, fit).
- **Runs.** The first background chain was killed partway for memory. The post hoc cases were rerun in parts with streamed output:
  the chains, then the fork alone at a smaller cap after the chains' hour ran out on it.
- **The study's case list** (`job.cases()`) and its computed knot sizes were read as data. The post hoc law-2 factors (`posthoc.predicted`) were imported as
  the prediction under test.
- **No growth, recurrence or scoring code of the study was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
