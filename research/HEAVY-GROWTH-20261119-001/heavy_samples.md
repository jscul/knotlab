# Two erasures on starts 03 and 14

Both erasures preserve the giant age-ten birth on 03, with at least **2,174,695,764,692,054 parents**. Its candidate-step distance from the intact tip is exactly eight. Both starts also have a recurring seventeen-junction cohort at distances zero through five. Fifteen of these junctions count as heavy, including eleven births with at least three parents. Isolating those fifteen and recomputing their loose counts gives three steps, with live counts \(15\to11\to5\) and one closing birth.

## Exact changes after erasure

Let \(a\) be the unique unary tip, \(b\) its only candidate, and \(W\) the four other candidates of \(b\). At ages seven and eight the sole pendant path in each complete roster is the one step \(a,b\). Either erasure leaves one connected component, with no remaining pendant path or isolated junction. At age eight the full rosters have 28,065 and 162,336 junctions. Erasing \(a,b\) leaves 28,063 and 162,334, respectively. The restricted rosters also have a unique-degree junction, so neither has a transitive symmetry group on its junctions. [Literal checks](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/heavy_samples.json)

The isolated law restricts the old blocks to the retained roster and keeps the actual incoming parent arities. A *retuned* start uses the funded loose count \(\max(d,3-p,1)\) after the restriction. A second comparison uses the original loose counts at the surviving junctions for the first round and then applies the ordinary funding rule. Counting heavy junctions in a reached full roster instead takes the union of the marked births and drops each marked junction once. A two-tip control has two distinct unary births and one shared companion, for three marked births.

| Intervention at age seven | Next births on 03 | Next births on 14 |
|---|---:|---:|
| Intact | 28,065 | 162,336 |
| Erase tip, retune | 28,063 | 162,334 |
| Erase both, retune | 28,059 | 162,330 |
| Erase tip, keep first-round loose counts | 28,064 | 162,335 |
| Erase both, keep first-round loose counts | 28,063 | 162,334 |

The intact arity counts, in the order at least three, two, one, are \((28{,}008,56,1)\) and \((162{,}122,213,1)\). The sum of the intact loose counts used is 993,164 and 6,513,797. The literal parent rows of all 190,401 age-eight births check the openings and the first-round deletions. Direct enumeration from age four independently checks all four related erasures, crossing the same interface with both funding choices.

In the first round every unheld group of at least three survives with the same parents. Any candidate clique extendible by \(a\) lies in the held pair \(\{a,b\}\). Aside from that pair, a clique extendible by \(b\) lies in the held block \(\{b\}\cup W\). The pair block disappears under either erasure. When both junctions are erased the second block becomes the held four-set \(W\), still maximal because every outside junction compatible with any of \(W\) meets at most two of them. The other maximal held sets and the classifications of all surviving candidate pairs are unchanged. The retuned law loses the one unary birth and the residual pair \(\{a,b\}\). The double erasure also loses the four residual pairs \(\{b,w\}\) with \(w\in W\). The funded loose counts of \(a,b\) were two and five. Retuning removes three uses after tip erasure and eleven after double erasure, including the reassigned counts at survivors. Keeping the openings leaves one extra unary birth at \(b\) in the first arm or four unary births, one at each \(w\in W\), in the second.

The literal distance-three profiles consist of one site for each of the six pairs of indices in \(W\), with \(\sigma=3\) singleton profiles for 03 and \(\sigma=4\) for 14. The four demands at \(W\) are \((5,5,4,5)\) and \((5,6,4,5)\). Erasing both junctions drops each demand there by one. In the intact law the four interface pairs replace \(W\) at each step, and the six unheld triples through two elements of \(W\) replace the six two-index profiles. Every singleton profile gives a separate residual pair and is likewise replaced.

The restricted successor read from the intact law still contains the four interface pairs and their held block through \(b\). Retuning misses those four births. Keeping the openings makes four unaries with distinct sole parents, so the shared block is absent even when the birth count matches. This is the specific dependence of the restricted succession on the erased junctions.

| Intervention at age eight | Change in age-nine births | Change in age-ten births |
|---|---:|---:|
| Erase tip, retune | −2 | −6 |
| Erase both, retune | −6 | −15 on 03, −16 on 14 |
| Erase tip, keep first-round loose counts | −1 | −2 |
| Erase both, keep first-round loose counts | −2 | 0 |

For the age-ten differences, first consider retuning after double erasure. At age nine this removes exactly the next tip, its companion and the four new \(W\). The six unheld interface triples, the five pairs through the companion, the \(\sigma\) singleton-profile pairs and the one offshoot are the only lost births at age ten. Each of the six triples has just one surviving parent, so no retained pair loses coverage. All survivors remain connected. In the arm with original openings, the four added unaries have held neighborhoods of sizes \(3\) plus their respective singleton-profile counts. They contribute \(12+\sigma\) residual pairs and no surplus at the second step. This compensates the count of missing births, with six fewer large groups and seven more pairs than in the intact age-ten roster. Under tip-only erasure the retuned first successor removes the next tip and companion, so its next loss is six. Keeping the original openings adds a unary with four candidates and restores four pairs at the second step.

Using the prior bound on age nine of 03, the observed heavy count is at least 2,174,695,764,693,285. The isolated double-erasure law with retuning gives at least 2,174,695,764,693,281. The exact residual-pair counts before and after tip-only and double erasure are 1,241, 1,240 and 1,236. [Prior count](../HUB-GUIDED-SAMPLE-20261119-001/structure.md)

## One continuing cohort and one distant birth

Index \(W\) by \(i=0,1,2,3\). At candidate distance three, \(P_{ij}\) is the unique junction whose candidates in \(W\) have indices \(i,j\). At distance four, for each three-index set \(T\), write \(H_T\) for the unique junction compatible with its three \(P_{ij}\). At distance five write \(F\) for the unique junction compatible with all four \(H_T\). These definitions can be read from the rooted candidate graph. The literal parent rows from ages six through eight show the following transition in both starts. A primed label denotes a child.

\[
\begin{aligned}
P_{ij}'&:\quad W_i,W_j,P_{ij},\\
H_T'&:\quad H_T,\ \{P_{ij}:\{i,j\}\subset T\},\\
F'&:\quad F,\ \{H_T: |T|=3\}.
\end{aligned}
\]

The labels \(F\) at ages six, seven and eight are (88,71,10425) on 03 and (69,350,121267) on 14. Each \(F'\) has exactly five parents. Together with the tip, companion and four \(W\), all seventeen births have all their parents within the preceding cohort during the intact evolution. The independently checked stationary five-step restriction carries the exact parent rows forward from age seven. In particular the four-parent and five-parent births are recurring continuations with their previous selves among their parents. They stay at candidate-step distances four and five, respectively. The four \(H_T\) share one \(P_{ij}\) per pair and no parent across the whole four-set. [Stationary restriction](interface.md)

The \(H_T\) and \(F\) births also match for both isolated erasures through two further steps, and \(F\) still matches at the third step. In the most extensive retuned arm the first successor misses the full roster's vertices at distances zero to two. The second misses precisely its vertices at distances zero to three, by the minimum-parent distance formula. This leaves \(H_T,F\) at distances four and five from the reference tip, with their full parent rows through those two steps. Keeping the original openings adds first-generation unaries whose sole parent is \(b\) or one \(W_i\). None meets the three pair profiles of any one \(H_T\) group or any parent of the \(F\) group. Every added second-generation pair uses an added unary and a real junction that was within three steps of the reference tip at the first successor. Such a pair has no shared parent with the second-generation \(F\), whose parents were at distances four and five. It cannot enlarge the five-parent group. The early direct replay checks this exact matched parent row at the third step for all four funded comparison arms.

The selected fifteen heavy cohort members, considered as a separate induced restriction with loose counts recomputed, give \(15,11,5\) live junctions and one closing child. Its last group contains all five remaining junctions and uses their one loose distinction each. The actual large isolated bodies contain other junctions. The induced cohort's closure establishes a finite control for occurrence of the displayed recurrence while connected to a feeder. It supplies no indefinite growing subsystem detached from that feeder.

For the giant on 03, let \(C_1,\ldots,C_9\) be the nine literal compulsory age-nine parents certified in the previous study. Each \(C_i\) is represented by its complete support in the age-eight roster. For any age-nine parent of the giant, each of its own age-eight parents belongs to the union of the closed candidate neighborhoods of \(C_i\), for every \(i\). This follows from complete mutual compatibility of its own parents and its required meeting with the support of \(C_i\). The nine-fold intersection contains exactly 4,095 sites at distance six and 23,494 at distance seven from the age-eight tip. Each \(C_i\) has a parent at distance six. The minimum-parent formula therefore gives a minimum distance of seven among parents of the giant and exactly eight for the giant itself. [Literal giant supports and population counts](../GROWTH-CONTINUES-20261119-001/witnesses.md)

Every age-nine parent of the giant survives either erasure applied at age eight. The possible added unary children in the retained-openings arms use the old \(b\) or \(W\) and share no old parent with a parent of the giant. The complete giant group retains both maximality and its unheld status in all four arms. Its age-nine parents are disjoint from the age-nine parents of the local five-parent birth, so both incompatible children are present at age ten in the whole isolated body on 03. Long-term bounds on the width and eventual closure of either whole isolated body remain unresolved by these calculations. The unknown age-nine roster on 03 already requires over two quadrillion junctions. The age-ten group has a support at that scale by itself. The measurements use archived supports and exact cuts through the two steps, without listing entire rosters at those sizes.

Run the checker in the repository environment with `.venv/bin/python -B` followed by the checker path and the optional directory of archived stage files. It checks the published stage hashes, replays ages two through six from the literal starts, verifies candidate-step distances through age eight, and emits the table and finite controls as JSON. [Checker](../../experiments/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/heavy_samples.py) · [Exact output](../../artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/heavy_samples.json)
