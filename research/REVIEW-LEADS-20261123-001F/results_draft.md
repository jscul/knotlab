# A rule that is both parity and not-all-equal: results draft

Ticket `REVIEW-LEADS-20261123-001F`, experiment `REVIEW-LEADS-20261123-001F-E001_both_laws`. Draft by a Claude Sonnet sub-agent from the frozen pre-registration ([preregistration.md](preregistration.md), sha256 `59cb60d8f25af312545849616b7a7928e60bb9ab1879089effe9350d2e62ba3f`, unchanged). Exploratory; referee pending; the verdict and the report to the owner are the thread's. Every reading and deviation is in `experiments/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/deviations.md` (D1 to D11); the hand null is `counting_null.md` in the same folder.

In words: on the five-founder clock, the seven-knot source and the nine-knot source, every lawful valued start survives to the horizon in every arm, so nothing is removed. The rule forces one whole history, and a signal fraction of 0, only for the 16 of 4,009 lawful clock starts whose founders carry 0 or 10 ones among their ten loose distinctions. Every other lawful clock start has at least 2.6 x 10^16 whole histories and every one of the seven signal fractions 0/6 through 6/6. The rule is not itself a knot (it fails K2), so these are statements about a counting constraint.

## Commands (repo root, each under `timeout 600 prlimit --as=12884901888 .venv/bin/python -B`)

```text
sha256sum experiments/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/counting_null.md   # before any run
timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/gate.py   > artifacts/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/gate.log
timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/clock.py  > artifacts/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/clock.log
timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/seven.py  > artifacts/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/seven.log
timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/nine.py   > artifacts/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/nine.log
.venv/bin/python -B experiments/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/make_tables.py   # writes artifacts/.../tables.md
```

`counting_null.md` sha256 `ba0c4aaf441ebcda4e7321262ea48eedbb384282127a52df82359e25330576d0`, recorded in `artifacts/.../counting_null.sha256` at 2026-11-23T20:17:08Z, before the gate was run. The gate, clock, seven-knot and nine-knot scripts ran in the last pass at 74 s, 133 s, 217 s and 10 s on one process each, all under 12 GB; the seven-knot and nine-knot scripts were run once more after adding two recorded fields (D9). Sources imported read-only: `GENERATORS-20261120-001A` `fixtures.py` and `CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B` `phase_clocks.py` (sha256 in every result file).

## Gate row G: passed

| Part | Result |
| --- | --- |
| G1, rule, 3 places and 4 places | the canonical checker (Python API and `knotlab check`, same verdicts): K1 true, K2 false, K3 true, so not a knot. Also false at 5, 6 and 7 places. |
| G1, controls | parity alone and not-all-equal alone: K1, K2, K3 all true at 3 and 4 places (and at 5, 6, 7) |
| G2, parity alone, from the quiet start | 64 of 64 six-bit patterns of signals, signal counts 0/6 through 6/6 |
| G2, not-all-equal alone, from the quiet start | 64 of 64 patterns, counts 0/6 through 6/6 |
| G3, rule, from the quiet start | exactly 1 whole history; the signal is 0 at all six returns (cuts 5, 10, ..., 30, read from the actual births and the founders' physical order); the carried count alternates 0, 10, 0, 10, ...; the engine's own count at depth 4 is also 1 |

The tooling checks are also in `gate.json` and all pass: the history counts against explicit enumeration with named distinctions (clock, depths 1 and 2, 15 starts, all three arms; value-flow and labelled-founder counts both agree); the abstract five-phase clock against the engine's real births (90 comparisons, depths 1, 2, 3, 5, 6); the SAT survival test against the exact counts (clock, seven-knot) and against two stricter rules that do remove starts (2,303 and 1,233 of 2,304 carried-count vectors removed, SAT and counts agree).

## Hand null (written before any run), against the run

Facts derived by hand and confirmed: no start is ever removed on the clock (H1); a return signals exactly when the receiver carries exactly one one among its two loose distinctions (H2); the carried count alternates C0, 10 - C0 on every history under the rule (H3, also checked over all 243 carried-count vectors: 0 exceptions); a start has exactly one history exactly when C0 is 0 or 10 (H5, H6). Predicted by hand but not proved, and confirmed on every lawful start: every other start has every signal count 0 through 6. The case C0 = 1 or 9 (H7, 2^30 histories) is confirmed as pure counting but no lawful start has it: the five founders' weights sum to twice the number of ones on shared distinctions plus C0, and each is even, so C0 is always even (D8).

## Five-founder clock (30 parent steps, six returns, 155 knots; every cut has 5 births, 2 parents, 2 fresh distinctions, 4 places)

Founder arities 7, 5, 4, 4, 6 (one each of 7, 5, 6; two of 4); all 150 newborns have 4 places. Allowed numbers of ones: rule: 4 places {2}, 5 {2, 4}, 6 {2, 4}, 7 {2, 4, 6}; parity alone: all even numbers; not-all-equal alone: all except 0 and all. No stall.

| Arm | lawful valued starts | used | survivors at step 0, each step to 30 | histories per start, min / median / max (value flow) | starts with exactly one history | signal fractions over the histories of a start |
| --- | --- | --- | --- | --- | --- | --- |
| rule | 4,009 | 4,009 (all) | 4,009 at every step | 1 / 1.92e27 / 4.61e27 (11 distinct values) | 16 | 16 starts: {0/6}; 3,993 starts: all seven, 0/6 to 6/6 |
| parity alone | 8,192 | 1,024 drawn | 1,024 at every step | 3.40e44 / 1.36e45 / 5.44e45 | 0 | 1,024 starts: all seven |
| not-all-equal alone | 179,878 | 1,024 drawn | 1,024 at every step | 6.41e80 / 5.49e81 / 2.62e82 | 0 | 1,024 starts: all seven |

Labelled-founder counts (D3) are the value-flow counts times the product of c!(2-c)! over the five founders; for the rule they run from 32 to 1.80e28. No carried-count vector, reachable or not, is without a lawful next step (0 of 243 in each arm).

### Rule arm by carried count of the start, with the hand null

| C0 (ones among the 10 loose distinctions) | starts | with one history | histories, min .. max | fractions with a history | mean share of a start's histories with signal count 0, 1, 2, 3, 4, 5, 6 | hand null |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 8 | 8 | 1 | {0/6} | 1, 0, 0, 0, 0, 0, 0 | forced: 1 history, fraction 0 |
| 2 | 302 | 0 | 2.60e16 .. 1.37e17 | all seven | 0.0507, 0.2014, 0.3240, 0.2698, 0.1226, 0.0289, 0.0028 | at least 2 histories, all seven (unproved) |
| 4 | 1,623 | 0 | 9.86e25 .. 4.61e27 | all seven | 0.0020, 0.0224, 0.1019, 0.2453, 0.3288, 0.2322, 0.0673 | same |
| 6 | 1,723 | 0 | 9.86e25 .. 4.61e27 | all seven | 0.0020, 0.0224, 0.1020, 0.2454, 0.3288, 0.2321, 0.0673 | same |
| 8 | 345 | 0 | 2.60e16 .. 1.37e17 | all seven | 0.0509, 0.2019, 0.3242, 0.2694, 0.1221, 0.0287, 0.0027 | same |
| 10 | 8 | 8 | 1 | {0/6} | 1, 0, 0, 0, 0, 0, 0 | forced: 1 history, fraction 0 |

Weighting of the shares: each lawful start counted once, and within a start each whole history counted once (no other weighting is implied). The null's 16 forced starts are the 16 observed ones; its 3,993 others all have at least two histories and all seven fractions. The signal-count totals pooled with each whole history counted once are in `clock.json` (`by_C0`).

### Carried count by stage (clock)

Rule: on every history of every start, C(t) = C0 at even t and 10 - C0 at odd t (universal over all 243 vectors); so stages 0 to 30 show only {0, 2, 4, 6, 8, 10} over the 4,009 starts. Parity alone: stage 0 {2, ..., 10} (drawn starts), stages 1 to 30 {0, 2, ..., 10}. Not-all-equal alone: stage 0 {1, ..., 9}, stages 1 to 30 {0, 1, ..., 10}. (Carried counts are even under the rule and under parity alone, because every founder's word is even.)

## Seven-knot source (25 distinctions, 9 shared; loose 3, 0, 3, 3, 3, 2, 2)

Horizon 6 parent steps (knots 7, 15, 27, 46, 78, 134, 235; step 7 would give 420); no stall; both laws give the same births. Births per step 8, 12, 19, 32, 56, 101. Arities met: founders 3 (one), 4 (two), 5 (two), 6, 7; newborns 5 (13), 6 (35), 7 (87), 8 (78), 9 (15). Allowed numbers of ones by arity for each arm are in `seven.json` (`allowed_ones_by_arity`).

| Arm | lawful valued starts | used | survivors at steps 0..6 | lawful starts with no survivor at step 6 | at step 6: no history / one / two or more (drawn) | counted exactly through | histories per start at that depth, min / median / max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule | 92,312 | 1,024 drawn | 1,024 at every step; all 92,312 lawful starts at every step | 0 | 0 / 0 / 1,024 (all 92,312 lawful starts have two or more) | 2 parent steps | 2.05e8 / 1.38e10 / 5.89e10 |
| parity alone | 262,144 | 1,024 drawn | 1,024 at every step; all 262,144 | 0 | 0 / 0 / 1,024 | 2 | 2.05e9 / 1.11e11 / 6.64e11 |
| not-all-equal alone | 16,316,976 | 1,024 drawn | 1,024 at every step; all 16,316,976 | 0 | 0 / 0 / 1,024 | 2 | 3.20e14 / 2.03e16 / 1.11e17 |

At depth 1 the rule arm has 48 to 46,208 histories per start (median 7,680). No old word of parent step 1 is removed later in any arm: of all 81,920 vectors of ones that the eight newborns of step 1 could carry, none has no lawful continuation to step 6. Carried count under the rule at stage 1: values 2 to 24 (even), stage 2: values 0 to 42 (even); stage 0 values of the drawn starts 2 to 14.

## Nine-knot source (39 distinctions, 10 shared; loose 5, 2, 4, 3, 3, 4, 3, 3, 2)

Horizon 4 parent steps (knots 9, 24, 54, 117, 259; step 5 would give 597); no stall; both laws give the same births. Births per step 15, 30, 63, 142. Arities met: founders 3 (one), 4 (one), 5 (four), 7 (two), 8 (one); newborns 4 (2), 5 (2), 6 (20), 7 (42), 8 (50), 9 (74), 10 (44), 11 (14), 12 (2).

| Arm | lawful valued starts | used | survivors at steps 0..4 | lawful starts with no survivor at step 4 | at step 4: no history / one / two or more (drawn) | counted exactly through | histories per start at that depth, min / median / max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule | 449,885,231 | 1,024 drawn | 1,024 at every step; all 449,885,231 lawful starts at every step | 0 | 0 / 0 / 1,024 (all 449,885,231 lawful starts have two or more) | 1 parent step | 2,645,248 / 7.92e8 / 1.00e10 |
| parity alone | 1,073,741,824 | 1,024 drawn | 1,024 at every step; all 1,073,741,824 | 0 | 0 / 0 / 1,024 | 1 | 2.18e7 / 9.14e9 / 1.52e11 |
| not-all-equal alone | 267,940,964,814 | 1,024 drawn | 1,024 at every step; all 267,940,964,814 | 0 | 0 / 0 / 1,024 | 1 | 3.74e11 / 7.76e13 / 8.91e14 |

Carried count under the rule at stage 1: values 8 to 60 (even); stage 0 of the drawn starts 6 to 22. Prefix-level removal beyond the starts was not enumerated for this source (space of newborn carried counts 4.2e10; D5).

## Predictions

| # | Verdict | Exact numbers |
| --- | --- | --- |
| G | holds | see the gate table: rule fails K2 at 3 and 4 places; parity alone and not-all-equal alone give 64 of 64 patterns and counts 0/6 to 6/6; quiet start stays quiet (1 history, 0 signals at 6 of 6 returns) |
| P1 | fails (every start survives on every structure) | clock: 4,009 of 4,009 lawful starts survive 30 parent steps (rule), 0 removed; seven-knot: 92,312 of 92,312 survive 6 parent steps, 0 removed; nine-knot: 449,885,231 of 449,885,231 survive 4 parent steps, 0 removed; the same for parity alone and not-all-equal alone; no stall |
| P2 | fails | clock, rule arm: 3,993 of 4,009 starts have histories at all seven fractions 0/6 to 6/6; only the 16 starts with C0 in {0, 10} have one fraction (0/6, one history) |
| P3 | fails | union over all histories of all starts: seven values (0/6 through 6/6); the values of the starts that have one fraction: {0/6} |

## Scaffolds used

The rule (even parity and not-all-equal, so exactly two ones at 3 and 4 places); the reading that an old word without a lawful fresh completion is removed (D5); the three sources, the enrolled receiver and the signal; the horizons and their reading (D2); the draw of starts (D4); the identification of histories up to renaming (D3); the depth to which histories were counted (D1). The statements are about these structures and arms, not about the model in general.

## Not done

- Exact whole-history counts beyond 2 parent steps (seven-knot) and 1 parent step (nine-knot); survival and one-or-several histories to the full horizon were decided by SAT instead (D1).
- Prefix-level removal for the nine-knot source and beyond parent step 1 for the seven-knot source.
- No test of a changed rule at higher arities, of a different receiver on the seven-knot or nine-knot source, or of a start outside the lawful ones.
- No second implementation of the clock count independent of the shared engine beyond the checks in `gate.json`.

## Files

- `experiments/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/`: `counting_null.md`, `deviations.md`, `both_laws.py` (engine), `structure_run.py`, `gate.py`, `clock.py`, `seven.py`, `nine.py`, `make_tables.py`.
- `artifacts/REVIEW-LEADS-20261123-001F/REVIEW-LEADS-20261123-001F-E001_both_laws/`: `counting_null.sha256`, `counting_null.recorded_utc`, `gate.json`, `clock.json`, `seven.json`, `nine.json`, the per-start files `clock_starts.jsonl`, `seven_starts.jsonl`, `nine_starts.jsonl`, `tables.md`, and the four logs.
- this note.
