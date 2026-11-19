# An auxiliary integer-weighted count

## Fixed design

This panel uses a binary partition of maximal mutually joinable sets
(the literature's maximal cliques). It is an independent numerical check
on methods that sample pivoted subtrees, individual groups, or cores
of the full stage. The stage-\(t\) output is the count \(C_t\) of all
maximal mutually joinable sets, including held maxima and isolated
singletons. Subtract these terms and add residual pairs and offshoots
when converting the count to round \(t+1\) births.

The final auxiliary kernel is [kernel.cpp](../../experiments/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/kernel.cpp). The
[shared-runner job](../../experiments/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/kernel_job.py) reads only block files. It
uses the `partner` policy with `coverage` order. It sorts junctions
by the size of their largest block and then the sum of their block
sizes, breaking ties by the original index. Each run samples from its
own seed and returns an arbitrary-precision integer. Verify inputs and
budget before drawing, and use all completed draws for descriptive
statistics. If any scheduled run reaches a cap, distinguish the
completed subset from a complete unbiased panel. An empirical central
95% range describes repeat estimates. It gives no two-sided coverage for
the true count.

On the target start-03, take 24 independent runs from seeds
202611205000 through 202611205023. Use a frontier of 32, a pivot
inspection pool of 32, a 160 MiB row cache, and 150,000 prepared
states per run. Each exact local count may have at most 22 selectable
junctions. Residual component checks may take place with up to 1,024
selectable junctions. Enable the nonempty block-affiliation quotient.

On each of the other 13 currently unread stages, use eight independent
runs with index \(i=0,\dots,7\), from seed \(202611206000+100s+i\)
for start number \(s\). Local and factoring limits carry over.

| Live junctions | Frontier | Pivot pool | Row cache in MiB | Prepared states |
| ---: | ---: | ---: | ---: | ---: |
| At most 40,000 | 16 | 16 | 192 | 100,000 |
| 40,001–120,000 | 8 | 16 | 384 | 60,000 |
| More than 120,000 | 2 | 8 | 768 | 40,000 |

The shared runner uses a 120-second wall cap and 2 GiB memory cap per
case. Use four workers for the main target and six for the scale
applications. If an application returns zero completed runs, the
prespecified fallback uses four more seeds starting at
\(202611206050+100s\), a pool of eight, at most 40,000 prepared states,
and frontier two, or one for more than 120,000 junctions. Report the
fallback as its own design, without pooling it with the original.

GCC 14.2.0 builds the executable using
`g++ -std=c++20 -O3 -march=native -Wall -Wextra -Werror kernel.cpp -o kernel_frozen`.
This design was fixed before any of the above seeds was used. All
pilot seeds precede the earlier reserved validation range.

| Locked file | SHA-256 |
| --- | --- |
| `kernel.cpp` | `eeae81b0222e750dc014b861872aba86f58f475574d99be0ae8f746b4fc38a03` |
| `kernel_job.py` | `60f474e9524c8046fa632668a0b5176d723a5865d5bbbd14cb2965f2d91ea64d` |
| `kernel_frozen` | `a94d5fb2af05f375722d99c6c610dbb44afdce9168a0f306451f59df0f9bece3` |
| `start-03-age08.txt` | `049ad2aa85d55619a9e9c97dfd7ed33f6bb0d929d665af56f071b13f8fbd1102` |

## Counting and weighting

The noncandidate relation joins any two junctions that share no block.
A maximal mutually joinable set selects mutually nonconflicting
junctions and supplies a conflict for every junction left out. This
is the literature's maximal independent set of the noncandidate graph.
In a search state \(P\) holds the selectable junctions compatible with
the choices made so far. \(X\) holds previously excluded junctions
that still require a conflict among the further choices.

Selecting \(v\) removes it and all its conflicts from \(P\).
Those conflicts now meet the maximality requirement. It also removes
the excluded junctions in \(X\) whose requirement \(v\) satisfies.
Excluding \(v\) moves it from \(P\) to \(X\). These actions partition
all completions by whether they select \(v\). If \(v\) in \(P\)
has exactly one conflict \(u\) in \(P\), it is enough to partition
into selecting \(v\) and selecting \(u\). At least one must be
selected and they cannot both be selected. A junction with no
remaining conflict is mandatory. An excluded junction in \(X\) with
one possible conflict forces that choice, and one with zero makes
the state impossible.

The solver factors a residual by candidate conflicts and by the
incidence of \(X\) with its possible conflicts in \(P\). A small
independent component contributes an exact factor, since its
completions combine freely with completions from the other
components. The local solver also detects identical choice
neighborhoods, duplicate or redundant domination requirements, trees,
and bipartite cases with a small enough side for exact enumeration.
The global quotient only merges equal nonempty block affiliations;
the local solver recognizes paired alternatives from the actual
residual relation. Bitsets for closed candidate neighborhoods are
generated from block membership and reused in a bounded cache.

Each unresolved state has integer mass \(w\). When a split produces
two hard children, each inherits \(w\). Exact outcomes contribute
their weighted count before any population trimming. The remaining
states are paired by their selectable and excluded counts when the
frontier exceeds its width. Given a pair with masses \(w_a,w_b\),
an integer drawn uniformly below \(w_a+w_b\) keeps the first state
with probability \(w_a/(w_a+w_b)\), otherwise the second. It then
carries the sum as its mass. This operation leaves the expected
weighted sum of both continuation counts unchanged. Recursion and
conditioning therefore preserve an unbiased count under independent
randomization. Bit lengths, arithmetic and the comparison against
the sampling threshold use integers throughout.

If the two remaining counts are \(M_a,M_b\), the conditional variance
introduced by this merge is \(w_aw_b(M_a-M_b)^2\). Similar numbers
of candidates and exclusions can leave very different numbers of
completions, so this pairing can still introduce large tails. A
run that never merges is an exhaustive computation. The code reports
merges, largest terminal mass and largest terminal contribution per
run to distinguish these cases.

## Start-03 outcome

All 24 runs completed. The arithmetic mean was \(4.2660\times10^{19}\).
Independent estimates ran from \(1.6330\times10^{10}\) to
\(9.9380\times10^{20}\). Their empirical central 95% interval was
\([4.6076\times10^{11},4.3521\times10^{20}]\), a factor of
\(9.4454\times10^8\). The largest estimate accounted for 97.07%
of the sum. That run included an individual weighted contribution
of \(3.8648\times10^{20}\). The factor-ten precision gate fails
for this estimator. [All 24 runs](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/kernel_primary.json)

The age-seven exact frontier calculation gave 28,099, the independently
known count. Before fixing the panel, 16 width-256 hub-policy runs on
that control were between 24,810 and 34,910. On age eight the hub
pilot was stopped with no completed draw after more than three minutes
per process. Reverse-order partner pilots and a policy prioritizing
choices outside a dominant block also produced unstable weights.
These exploratory results guided the choice of the faster partner
policy and the fixed width. They are method comparisons on the stated
budgets. [Pilot configurations and outcomes](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/kernel_pilots.json)

Independent subset counts matched in 400 exact replays on 100 small
inputs. The controls exercised twin, component, forest and bipartite
reductions and the block continuation rule. A larger synthetic case
of 140 partner pairs gave \(2^{140}\) through exact components and
by repeated merging at width one with the exact components disabled.
This tests merge masses beyond a machine word. A smaller weighted
sampling control also exercised stochastic merges against an explicit
count. [Locked program checks](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/kernel_locked_checks.json)

## Scale applications

These estimates describe \(C_t\). Held maximal sets, isolated
singletons, residual pairs and offshoots enter the conversion to
round-\(t+1\) births. The rows marked censored contain descriptive
statistics of the completed subset. [All scale draws](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/kernel_applications.json)

| Stage | Completed | Mean | Empirical central 95% ratio |
| --- | ---: | ---: | ---: |
| Start-01 age 10 | 8/8 | \(1.42\times10^5\) | 11.9 |
| Start-02 age 9 | 8/8 | \(2.95\times10^6\) | 923 |
| Start-05 age 9 | 8/8 | \(5.07\times10^5\) | 27.6 |
| Start-06 age 7 | 8/8 | \(3.97\times10^{12}\) | \(2.02\times10^6\) |
| Start-07 age 7 | 2/8 | \(2.78\times10^7\), censored | 26.1 |
| Start-08 age 9 | 8/8 | \(3.94\times10^5\) | 64.5 |
| Start-09 age 6 | 8/8 | \(1.48\times10^6\) | 3.34 |
| Start-10 age 7 | 8/8 | \(3.46\times10^5\) | 6.39 |
| Start-11 age 7 | 8/8 | \(4.84\times10^4\) | 39.6 |
| Start-12 age 7 | 6/8 | \(9.27\times10^7\), censored | 138 |
| Start-13 age 7 | 0/8 | — | — |
| Start-14 age 8 | 8/8 | All zero | Undefined |
| Start-15 age 8 | 8/8 | \(6.59\times10^{18}\) | \(1.15\times10^{11}\) |

All 104 scheduled scale cases returned a final status. The eight
start-13 caps triggered the independent width-two fallback, which
returned 393,216, 4,463,360, 0 and 0. All eight start-14 draws completed
but reached no positive contribution, while an exploratory width-eight
run at that stage returned 30,638,080. The zero spread at width two
reflects undersampling, since a nonempty stage has at least one
maximal set. Start-09 and start-10 offer narrower empirical spreads
from eight independent draws each. The other results establish
feasibility of finite weighted draws and expose remaining uncertainty
across scopes. [Fallback draws](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/kernel_fallback.json)

The shared runner finished the start-03 panel in 35.5 seconds with
four workers and peak aggregate memory about 439 MiB. The scale panel
took 73.6 seconds with six workers and peak aggregate memory about
2.41 GiB. The caps arose from prepared-state counts, with no runner
timeouts or memory errors.
