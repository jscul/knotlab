# Held-out lower-limit batch

The first sampling passes found that individual search outcomes can dominate
the overall mean. The follow-up fixes one sampling design before drawing new
streams. It targets a one-sided lower confidence limit for the count of all
maximal mutually joinable sets (the literature's maximal cliques). The 16
outputs also measure the spread of independent runs of the same design.

Use the most recent factored width-512 configuration, with degree ordering
and the same exact cutoff and branching rule. Order the representatives of
equal closed candidate neighborhoods by descending original degree, breaking
ties by original index. The pivot pool contains the first 32 excluded and
first 32 remaining junctions in that order. The child order is the same
degree order. Assign weight with the existing systematic resampling procedure.
Use one run for each seed from 202611199400 to 202611199415 inclusive, with
each stream restarted at its own seed. Four CPU workers run the commands
independently. Do not examine results until all 16 runs finish.

```bash
study=experiments/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate
result=artifacts/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate
stage=/var/tmp/wall-round9-20261119
g++ -std=c++20 -O3 -march=native -Wall -Wextra -Werror "$study/estimate_bk.cpp" -o "$stage/estimate_bk_heldout"
python3 -B "$study/estimate_heldout.py" "$stage/estimate_bk_heldout" "$stage/age8.txt" "$result/estimate_heldout.json"
```

For each seed the driver runs
`estimate_bk_heldout age8.txt 1 SEED 32 24 1 0 1 0 512 0.5 8192`.
In order, the settings after the seed give the pivot pool per set, exact
cutoff, quotient flag, shuffle flag, rank exponent, local ordering flag,
population width, resampling mass exponent, and largest candidate count
eligible for residual factorization.

The compiler is GCC 14.2.0 (Ubuntu 14.2.0-19ubuntu2). The SHA-256 digests are

| File | SHA-256 |
| --- | --- |
| `estimate_bk.cpp` | `dcc9cd474fd85a2edd6c309997dd7981538eef0b81caaa7b25ef0b1c34deac7f` |
| `estimate_heldout.py` | `df27beccd1b419632dab2161de07c36536ac7d1798f44e89de675f5ee6aef15f` |
| `estimate_bk_heldout` | `cf156427b267bf1c467a3be769e2408e7acee1261bb4b4d2f338b570d17684e9` |
| `age8.txt` (reconstructed by `export_stage.py`) | `049ad2aa85d55619a9e9c97dfd7ed33f6bb0d929d665af56f071b13f8fbd1102` |

For the four consecutive groups of seeds, let their means be
$g_1,g_2,g_3,g_4$, and let $\bar Y$ be the overall mean. Report
$\max\{0.005\bar Y,\,(0.005g_1g_2g_3g_4)^{1/4}\}$.
Every replicate is nonnegative with expected value equal to the count $M$
under the sampling design. The grouped means are independent, so the
expected product is $M^4$. Markov's inequality bounds the two
probabilities of overstating $M$ by 0.005 each. Their union gives at least
99% one-sided coverage under the design. Also report the observed minimum,
maximum, and max/min ratio across all 16 replicates.
