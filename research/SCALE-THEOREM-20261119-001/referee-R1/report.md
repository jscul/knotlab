# Referee report SCALE-THEOREM-001-R1 (own classification, reading, growth and relayed model on all 64,000 samples)

**Verdict: confirmed. No Block. P2's failure is a scorer label slip, as the note says. Two wording points, both Not a block.**
- **`scalelib.theorem_class` uses DOUBLE-IDENT's class and rule unchanged.** It loads `machine_check.classify` and `dims.predict` by
  path, without copying or editing them. It reads the class as `dims.py` does: "in", "one loose" and "none" together. That makes
  it DOUBLE-IDENT's class prediction exactly, including the edge case proved there: a start with one loose distinction closes at
  round 1.
- **The integrity check is sound, and an independent one agrees.**
  - **The study's P1** recomputes the cluster rule on the regenerated samples and compares it with SCALE-SHARE's record.
  - **The referee's check** does not use the cluster rule. It compares each regenerated sample's shared count and open places per
    knot with SCALE-SHARE's recorded features: they match on all 64,000. The referee's stall test also equals SCALE-SHARE's
    recorded stall on all 64,000.
- **The referee's own classification and reading reproduce every sample.** It uses DOUBLE-IDENT-R1's `classify`, `build` and
  `predict`, run on SCALE-SHARE's samples regenerated as data:
  - the theorem class matches on 64,000 of 64,000;
  - the growth class and the dimension-two mechanism match on 14,478 of 14,478 in the class.

  Every figure in the note's table reproduces at every size.
- **P2: the scorer's label slip, confirmed.**
  - **The labels.** `scale.classify` names every exponential growth class "ring (exponential)" (its only exponential label), and
    `scalelib.label` writes "exponential". `merge.py` compares the strings.
  - **The comparison.** With the labels as recorded, 14,474 of 14,478 agree. The 4 that differ are exactly the 4 the theorem reads
    as exponential. Read as one class, all 14,478 agree. No other label differs: no in-class sample carries a "[break shape]" tag
    or "out of scope".
  - **The growth.** The four do grow exponentially, by the referee's engine:
    - three keep a steady ratio of 1.16, 1.16 and 1.26 per round to round 30;
    - the fourth reaches 287 junctions at round 12, at a ratio near 1.36, and then fills the referee's 3 GB case cap.
  - **The note's handling is right:** "failed as scored", then shown to hold once the labels are matched, marked post hoc.
- **The referee's own regrowth sample agrees.** It covers all chains, not only chain 0: one in eight in-class growers by hash, plus
  every exponential one, 1,518 in all.
  - The referee's growth was compared with its relayed model, keys per round to round 6: all 1,518 agree.
  - All 685 in-class starts with at most one loose distinction close at round 1.

## The checks (`job_scale.py` and `job_expo.py` under `scripts/longrun.py`; 64 + 4 cases)

| Knots | Non-stalling | In the class | Out (S3) / (S4) | Class: closes / dim 1 / dim 2 | Dim 2 among the class's growers | SCALE-SHARE | Regrown, agree |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 5 | 4,413 | 82.9% | 4.7% / 12.4% | 22.0% / 11.6% / 66.4% | 85.1% | 82.4% | 365 / 365 |
| 6 | 3,724 | 81.0% | 6.8% / 12.2% | 18.9% / 10.2% / 70.9% | 87.4% | 85.2% | 311 / 311 |
| 7 | 3,035 | 78.1% | 8.4% / 13.5% | 15.3% / 9.2% / 75.6% | 89.2% | 87.0% | 243 / 243 |
| 8 | 2,634 | 76.5% | 10.0% / 13.6% | 13.0% / 7.7% / 79.3% | 91.2% | 88.7% | 209 / 209 |
| 10 | 1,764 | 75.2% | 10.6% / 14.2% | 8.5% / 5.1% / 86.4% | 94.5% | 92.9% | 155 / 155 |
| 12 | 1,405 | 74.6% | 11.0% / 14.4% | 6.1% / 4.6% / 89.2% | 95.0% | 93.6% | 108 / 108 |
| 16 | 851 | 76.0% | 10.6% / 13.4% | 3.9% / 2.3% / 93.8% | 97.6% | 97.2% | 88 / 88 |
| 20 | 544 | 73.3% | 9.9% / 16.7% | 1.5% / 2.3% / 96.2% | 97.7% | 98.1% | 39 / 39 |

- **Dimension three or more in the class: 0 of 12,270 growers.** The cluster rule's 43 three- and four-dimensional samples all lie
  outside the class (8, 8, 9, 8, 6, 2, 2 and 0 by size).
- **The mechanism of dimension two.** "Relay and two chains" rises from 34.6% to 57.6%, and "relay" alone falls from 21.5% to 8.6%,
  as stated.
- **Weighted to distinct arrangements** (|Aut| / n!, the recorded weights): the in-class share is 80.8% at five knots and 73.2% at
  twenty, and dimension two is 85.6% to 97.7% of the class's growers. The conclusions do not change. The pre-registration names
  the weighting, but every share in the note is labelled. The note says so under the table.

## Points for the owner (listed, not folded in)

1. **"The class (no first-round group of three, no two live knots with two common neighbours)"** leaves out two of its conditions.
   One is no stall, since the shares are of non-stalling starts. The other is that 685 of its 14,478 starts have at most one loose
   distinction. Those are outside Theorem 6's (S6′), but covered by DOUBLE-IDENT's proved edge case: they close at round 1, as the
   referee's growth confirms for all 685. **Not a block.**
2. **"Open places per knot fall like √(5/n)"** is the advisor's figure, and the measured constant is larger.
   - **Over all samples** the mean is about 1.23·√(5/n): 1.22 at five knots and 0.61 at twenty.
   - **Over the class**, which the argument is about, it is 1.07 at five and 0.38 at twenty. That falls faster than √(5/n), roughly
     as n^−0.74.

   The argument's direction holds, and more strongly. **Not a block.**

## How the work was split

- **The referee:**
  - read `scale_theorem.md`, the pre-registration, `scalelib.py`, `job.py`, `merge.py` and `results.json`, and DOUBLE-IDENT's
    `machine_check.classify` and `dims.predict` for the comparison;
  - wrote `job_scale.py`, `job_expo.py` and `scale_readout.py`. They use its own DOUBLE-IDENT-R1 classification and X⁺ reading,
    its RELAY-IDENT-R1 growth keys and relayed model, and its FIRST-KNOT-R1 engine with the program's rule.
- **Run only to regenerate the study's own data:** SCALE-SHARE's sampler, `scale.chain`.
- **Read as data:** the per-sample records in `runs/scale-share` and `runs/scale-theorem`.
- **No study reader was run.**
- **Where it ran.** Under `scripts/longrun.py` within the 16 GB cap (peak 139 MB). One exponential growth to round 30 reached the
  3 GB case cap, as noted above.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
