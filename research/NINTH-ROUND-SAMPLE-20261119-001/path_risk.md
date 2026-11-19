# One exact rare path in uniform-child descent

The actual age-eight stage has an unheld maximal clique of 16,531 named junctions. For the plain literal Bron–Kerbosch descent with a pivot pool of 128 and exact finishing at ten candidates, the probability of reaching its exact suffix is about \(1/(2.180\times10^{371})\). That suffix has eight candidates and exactly one counted completion. The same literal clique gives rare paths under both tested true-twin quotient configurations. [Full paths and exact integers](../../artifacts/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/path_risk.json)

| Graph used by descent | Pivot pool | Branches with a random choice | Inverse prefix probability |
|---|---:|---:|---:|
| True-twin quotient | 24 | 298 | \(9.396\times10^{351}\) |
| True-twin quotient | 64 | 315 | \(2.194\times10^{370}\) |
| Literal | 128 | 312 | \(2.180\times10^{371}\) |

## What the path proves

The proposal picks uniformly among the children at every visited branching state. Let \(b_i\) be the number of children at step \(i\) on a particular prefix. Set \(W=\prod_i b_i\). The prefix is visited with probability \(1/W\). If the suffix holds \(L\) counted leaves, the conditional mean contribution to the full estimator is \(WL\). Even with subsequent random descent, the prefix contributes at least \(W L^2\) to the second moment by Jensen's inequality. The archived configurations count the suffix exactly and have \(L=1\), so the prefix contributes exactly \(W\).

For a mean of \(M\) independent one-path estimates of a count \(T\), its relative RMS is therefore at least

\[
\sqrt{\max(0,W/T^2-1)/M}.
\]

For the literal configuration, if \(T\le10^{18}\), more than \(10^{333}\) independent draws are required even for relative RMS at most nine. If \(T\le10^{150}\), the bound is still more than \(10^{69}\) draws. After a million draws the relative RMS exceeds \(10^{32}\) throughout the second range. Each statement is conditional on its indicated count ceiling. The probability of ever seeing this prefix in a million draws is below \(5\times10^{-366}\). Empirical dispersion from such draws can miss this contribution. The certificate concerns RMS for these uniform-child estimators. Factor-ten coverage probabilities, rank-biased descent, population sampling, and other decompositions require their own analysis.

The target is unheld, so the same event contributes even when the traversal counts only unheld leaves. For the raw maximal-clique count, subtracting the deterministic held contribution changes the mean by a constant and leaves the variance unchanged. A birth count also needs its candidate-pair and offshoot terms. [Absolute block and correction counts](../../artifacts/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/parts8.json)

Starting exact counting earlier still admits the corresponding shorter prefix. On the literal graph that prefix has inverse probability above \(10^{370}\) with an exact cutoff of 128 candidates and above \(10^{334}\) with a cutoff of 8,192 candidates. These bounds use the retained factors before the first smaller state and the same named completion.

## Replay and controls

Candidates meet when a recorded parent block contains both. The construction greedily adds junctions in the same fixed original degree order used by the estimator, and checks pairwise candidacy and maximality on the resulting clique by intersecting closed neighborhoods. It verifies that no original block holds it. Grouping equal closed neighborhoods gives the true-twin quotient. Its maximal cliques lift uniquely by including each entire selected class.

At every pivot the script routes the target through the first branch containing a member of the target. It puts earlier siblings into the excluded set, just as in the estimator. The path records the exact child fanout before each decision and includes deterministic forced reductions. The archived estimator's own child and forced-reduction functions independently reproduce the sequence, including the cut-off state. A subset sweep checks every suffix completion. On a five-vertex cycle, a direct subset sweep finds five maximal cliques. An independent full probability tree gives mean five and second moment 27 with either a zero-candidate or a two-candidate exact cutoff. The age-seven source also gives an unheld path with inverse probability above \(2.16\times10^{18}\). [Path checker](../../experiments/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/path_risk.py) · [Exported stage sizes](../../artifacts/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/stage.json)

Run the checker on the directory containing `age7.txt` and `age8.txt`, written by the study's stage export. The result binds both input files and the estimator source by SHA-256.

```bash
family=experiments/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate
.venv/bin/python -B "$family/path_risk.py" /var/tmp/wall-round9-20261119
```
