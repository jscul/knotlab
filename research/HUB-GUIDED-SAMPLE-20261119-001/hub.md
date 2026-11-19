# Exact path weights for groups drawn from old blocks

On start-03, the 24 fixed replicates had a 5,245-fold empirical central spread.
They drew 1,408 actual large joins, from four to 18,291 junctions. The reversed
order gave a 55.8-fold spread. Even adding every candidate pair to each mean
leaves it below the earlier one-sided lower confidence limit on births. The
fixed weights have an exact expectation, while these batches miss the requested
precision.
[Plan and seeds](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/hub_plan.json) ·
[Weighted draws and literal group names](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/hub_results.json) ·
[Earlier lower limit](../NINTH-ROUND-SAMPLE-20261119-001/decision.md)

## Why the weights are exact

At each residual set \(R\), choose the largest intersection \(B\) with one
of the eight largest supplied blocks. This is a set of mutually candidate
junctions. Each name outside \(B\) receives 32 equally likely tickets. One
ticket proposes finishing with all of \(B\). Finishing with an extendible
set contributes zero. An outside choice retains the chosen name and restricts
the following names to its candidates. An exact shortcut takes a whole
residual set once it is a set of mutually candidate junctions.

When at most eight names remain outside \(B\), enumerate their compatible
subsets. Each subset forces precisely the remaining members of \(B\) that
can join all of it. Test maximality with respect to every omitted outside
name. The proposal chooses uniformly among these exact completions.

Fix an actual maximal group \(C\). A reference path chooses only tickets
consistent with \(C\). At an outside choice this leaves 32 tickets per
available outside member of \(C\). If no member of the remainder of \(C\)
is outside, maximality forces the remainder to be exactly \(B\), and the
finish ticket is its sole choice. At an exact suffix the reference selects
its required completion. This reference process ends at \(C\) with
probability one. The ratio of its path probability to the proposal path
probability therefore has expectation one per maximal group. The same
identity with an indicator gives its count for any recorded mark. The
artifact retains the integer factors of both probabilities and weights.

The shape marks record how many actual blocks meet the group, the largest
number of its members in one block, whether a cover needs at least three
blocks, and how many pairs of a fixed partnered set the group meets. The
start-03 marks use the literal 24-pair witness. For other stages, a
deterministic search tries at most 64 names per selected pair and certifies
the resulting partnered set directly. These are coverage marks for the
declared references. Raw fractions are proportions of the proposal draws.
Ratios of weighted sums describe the finite weighted sample.

## Controls and reached groups

Exhaustion of every proposal path on 75 small candidate graphs verified
the exact unit contribution of every group in 600 settings. Literal samples
also reproduce the single-block birth counts 304,590 and 36, and the last
two start-00 controls of one and zero births. The small partnered controls
check both free and held transversals.

The age-seven start-03 control had mean 10,434 births against 28,065 exact,
despite a 3.20-fold central spread. The larger order-five partnered control
had mean 23,701 against 65,526 exact, with a 1.74-fold spread. These fixed
controls show why central spread alone cannot establish accuracy for a
given finite sample.

For start-03, 1,037 of the 1,408 genuine large joins needed at least three
blocks. A largest block met at least 90% of the members in 340 draws, and
38 drew a group meeting all 24 marked pairs. The largest replicate
supplied 74.9% of the weighted total. The weighted large-join means were
\(4.816\times10^9\) and \(1.692\times10^9\) in the two orders.

| Start | Age | Large joins drawn | Observed sizes | Draws needing at least three blocks | Reference pairs met |
|---|---:|---:|---:|---:|---:|
| 01 | 10 | 0 | — | — | — |
| 02 | 9 | 60 | 51,495–60,949 | 60 | 0–2 of 2 |
| 03 | 8 | 1,408 | 4–18,291 | 1,037 | 0–24 of 24 |
| 05 | 9 | 61 | 51,499–60,990 | 61 | 0–2 of 2 |
| 06 | 7 | 64 | 205–6,532 | 63 | 0 of 3 |
| 07 | 7 | 58 | 80–20,327 | 25 | 0–1 of 1 |
| 08 | 9 | 60 | 51,495–60,963 | 59 | 1–3 of 3 |
| 09 | 6 | 54 | 25–1,525 | 32 | 0 of 3 |
| 10 | 7 | 56 | 81–2,858 | 41 | 0–3 of 3 |
| 11 | 7 | 62 | 97–2,651 | 44 | 0–1 of 1 |
| 12 | 7 | 52 | 24–21,230 | 25 | 0 of 3 |
| 13 | 7 | 59 | 36–22,500 | 24 | 0–3 of 5 |
| 14 | 8 | 63 | 2,401–61,567 | 58 | 0–4 of 6 |
| 15 | 8 | 59 | 2,433–17,161 | 37 | 0–5 of 9 |

Start-03 used 1,536 draws in the main order. Each other unread stage used
64. The 64 start-01 draws all gave held maximal sets with 12 observed
fingerprints. All other unread stages yielded at least 12 genuine large
joins with full membership bitsets saved. The size and cover columns concern
the observed draws. For birth totals, the exact controls add the known
residual pairs and offshoots to the marked large-join estimate. The unread
stages retain their exact offshoot counts alongside the unknown residual
pair corrections.

The original equal-ticket pilot rarely reached a genuine group on
start-03. The locked revision used 32 tickets per outside name and checked
for a whole compatible residual set after eight choices with no lost
candidate other than the chosen name. In its 96-draw exploratory panel,
89 draws gave actual large joins in about three seconds. The fixed panels
used fresh seeds. For the 162,336-name start-14 case, the four prespecified
replicates ran in separate processes. Its conditional neighborhood backend
subtracts the identical union of old block memberships while skipping
covered words. The two backends gave byte-identical traces on a 12-draw
start-03 control. The archived full group bitsets use zero-based literal
roster names, little-endian bytes, zlib and Base64.
[Estimator](../../experiments/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/hub_greedy.py)
