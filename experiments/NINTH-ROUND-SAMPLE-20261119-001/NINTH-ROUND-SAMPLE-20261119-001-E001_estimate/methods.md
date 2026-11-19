# Sampling the maximal mutually joinable sets

The prespecified 16-run batch gives a 99% one-sided lower confidence limit of
734,650,722,639.96 maximal mutually joinable sets at age eight. With 203
held maximal sets and no isolated junctions, and nonnegative contributions
from residual pairs and offshoots, this gives a lower limit of 734,650,722,437
round-nine junctions, rounded to an integer. Individual replicate estimates
ran from $3.67\times10^{11}$ to $2.90\times10^{13}$, a factor of 78.90.
Their empirical central 95% range spans a factor of 58.90. The study's
factor-ten precision criterion fails. [Fixed design](heldout_design.md)
and [all 16 outputs](../../../artifacts/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/estimate_heldout.json).

## What was sampled

The program builds the candidate relation from the 365 maximal blocks at
age eight. It counts all maximal mutually joinable sets (the literature's
maximal cliques). Each set with at least three junctions that no block holds
gives one junction in the next round. Held sets, residual pairs and
offshoots are accounted for by the independent parts calculations.

Junctions with identical closed candidate neighborhoods (the literature's
true twins) must appear all together in any maximal set that contains one
of them. Keeping one representative from each class reduces 28,065
junctions to 25,654 and preserves the count of maximal sets by bijection.

The pivoted Bron–Kerbosch search keeps the junctions $P$ that can still be
selected and the previously excluded junctions $X$ that can still extend
the current set. A completion must include a candidate outside the pivot's
open candidate neighborhood. It belongs to the branch for the first such
candidate, including the pivot itself if selected. Earlier choices move to
$X$. When $P$ is empty, the search counts one maximal set exactly when
$X$ is also empty. This partitions the count without duplicate sets,
regardless of pivot or branch order.

At a search state, a junction in $P$ that is a candidate of all other
members of $P$ is required in every completion. The solver selects such
junctions deterministically. It also counts small residual components
exactly. For this purpose a noncandidate pair connects two junctions in
$P$, or a junction in $P$ to one in $X$. Every excluded junction must
have a noncandidate among the further selections, so an isolated junction
in $X$ precludes all completions. Completions in separate components
combine independently and their counts multiply. These reductions and
the exact enumeration when at most 24 selectable junctions remain were
enabled in the fixed batch.

## Weighting and uncertainty

Random descent chooses one branch per split. A path with sampling probability
$p$ and exact suffix count $k$ contributes $k/p$. Summing the
conditional contributions in expectation gives the full count. Rank-based
proposals keep 10% uniform and assign the other 90% in proportion to
$(j+1)^{-s}$, where $j$ is the branch's order from zero. Every branch
has positive probability.

Population runs list all children at a split and form a weighted list
from all retained parent states. When the list exceeds the width, each
child receives a positive score. The score is its parent's weight raised
to the configured mass exponent, times the square root of its parent's
branch count, times the rank-based proposal. The code permutes the list
and uses one uniform systematic sampling offset. For width $B$ the
child's expected multiplicity is $B$ times its score divided by the
total score. Its assigned weight is the parent weight times the observed
multiplicity divided by that expected multiplicity. The expected retained
weight equals the parent weight for each child. Repeating this argument
through all splits gives an unbiased nonnegative replicate under the
sampling model, even when the scores are poor. Each separate run uses a
distinct pseudorandom stream. Descendants inside a run reuse the
resampling offsets, so the independent units for uncertainty are complete
replicates.

The spread numbers are empirical descriptions of independent estimates.
The distribution-free lower limit uses Markov's inequality for the
arithmetic mean and for the product of four independent group means. It
gives coverage under the independent-randomization model for the recorded
streams. It supplies no upper confidence limit. Neither the sample mean nor
the largest observed inverse-probability weight is an established count.

## Replication and the tail

Independent NetworkX enumeration gives 134, 401, and 28,099 maximal sets
on ages five, six, and seven. All agree with the exact search. The age-seven
correction is $28{,}099-91+56+1=28{,}065$, using the exact held, pair,
and offshoot counts. The smaller control also passed 228 exact replays
across 76 graphs, including 31 replays that used component factorization.
A case requiring resampling returned mean 63.998 over 4,096 runs with
an exact count of 64. [Control outputs](../../../artifacts/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/estimate_checks.json).

Exploration changed the proposals and coverage in this order. Uniform
descent missed much of the count on age seven in 100,000 draws, returning
13,879 and 16,077. Prioritizing early branches improved the controls to
25,804 and 26,257. Widths 2,048 and 4,096 covered the entire age-seven
frontier, returning 28,099 in all 64 replicates for each width without a
resampling step. On age eight, widening the population still left widely
different outcomes because weighted deep branches dominate the sum in
some runs.

| Age-eight design | Runs | Empirical central 95% ratio | Largest run's share of their sum |
| --- | ---: | ---: | ---: |
| Population width 2,048, degree order | 16 | $3.80\times10^5$ | 99.52% |
| Population width 4,096, degree order | 16 | $2.01\times10^9$ | 99.996% |
| Population width 4,096, local degree order | 16 | $2.03\times10^5$ | 97.70% |
| Population width 8,192, degree order | 16 | $3.64\times10^9$ | 97.21% |
| Factored population width 512, fixed batch | 16 | 58.90 | 38.53% |

Every listed width covers all children at the first age-eight split.
The differences persist after that split, where repeated thinning assigns
very large inverse-probability weights to a few of the states that reach
maximal sets. Factoring residual components reduces a portion of that
work, while leaving between-run spread well above the decision threshold.
The width changes and trial scores were selected after seeing the pilot
results. They are observations of method sensitivity with configurations
and summaries in the [diagnostic record](../../../artifacts/NINTH-ROUND-SAMPLE-20261119-001/NINTH-ROUND-SAMPLE-20261119-001-E001_estimate/estimate_diagnostics.json).
The raw pilot outputs were generated in `/var/tmp/wall-round9-20261119`,
with digests and options in the diagnostic record. The fixed batch used
new seeds and was opened after all 16 runs finished. It took 18.7 seconds
with four CPU workers.
