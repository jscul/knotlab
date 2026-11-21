# Reading the preceding holders and their mutual witnesses

With uniform weighting on the allowed states, **the named pair rates of the 28-name stage force four births among all stages reached by at least one funded ordinary not-all-equal step**. Write \(P_{ij}\) for the six live holdings identified below. For every three different indices \(i,j,k\) there is one birth with parents \(P_{ij},P_{ik},P_{jk}\) and one fresh distinction. The argument determines those parents from the table with the observation age and the founder withheld. Its use of a preceding funded step restricts the rival population. [Protocol](preregistration.md) · [Named table and alternatives](../../artifacts/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B-E001_pair_growth/witness_recovery.json)

## A pair reading for a spent holder

Represent a named distinction by its sign \(s_x\in\{-1,1\}\). The pair correlation \(C_{xz}=\mathbb E[s_xs_z]\) is one minus twice its measured disagreement rate. Suppose an observed live holder \(P\) has a loose name \(f\) and an inherited name \(u\). At a positive-age stage, \(u\) had exactly one holder \(H\) before this last step. It gained exactly one new holder, \(P\). The support of \(H\) is what must be recovered to tell which currently live knots have a common witness.

Under the uniform weighting, for \(z\notin\{u,f\}\) form
\[
             C_{uz}-C_{fz}=\mathbb E[(s_u-s_f)s_z].
\]
Whenever \(H\setminus\{u\}\) is mixed, exchanging the two bits \(u,f\) is a weight-preserving involution. The rule at \(H\) is already satisfied, the rule at \(P\) treats its places symmetrically, and every other rule is independent of both names. Thus the contribution of this event is zero. On the complementary event \(H\setminus\{u\}\) has one common sign \(s\), and \(s_u=-s\). Every name \(z\in H\setminus\{u\}\) therefore attains the same negative value
\[
 -\mathbb E\!\left[|s_u-s_f|\,{\bf1}_{H\setminus\{u\}\ {\rm constant}}\right].
\]
No other name gives a smaller value. This lower bound is strictly negative. Full old projection gives an old word whose only 1 at \(H\) is \(u\). Set \(f=0\) to satisfy \(P\). Every other new holder can be satisfied independently at its own loose position. This proof allows any number of inputs in \(P\) and any repeated meetings elsewhere.

**When the minima identify the whole old holder.** Suppose \(H\) met each other preceding holder on at most one name. For an older \(z\notin H\), fix \(u=z=1\) and all of \(H\setminus\{u\}\) to zero. After \(H\) is satisfied, each surviving rule sees at most one fixed zero from \(H\). A rule also seeing \(z=1\) is already mixed. Every unresolved rule with a fixed value retains at least two free names, and each untouched rule retains at least three. The finite completion lemma extends these pins. Choose \(f=0\) at the new holder and complete the other new rules as above. This positive-weight word makes \(z\) strictly exceed the lower bound. Thus the older names attaining the minimum are exactly \(H\setminus\{u\}\). [Completion proof, including the odd two-place case](../THREE-READERS-AND-GROWTH-20261120-001B/recovery_argument.md#completing-a-partly-specified-state)

At observation age at least two the single-meeting hypothesis on every active predecessor is automatic. Each such \(H\) was newly born at the preceding step, took one name per distinct parent and shared no name with a simultaneous sibling. The conclusion also holds at the first cut for every participating source holder that meets each other holder at most once. Once the current live holdings and their loose places have been identified, apply the reading to every inherited name. The witnesses of a group of current live holders are precisely their common preceding holders. Listing those incidences and all loose counts determines every next parent set and fresh count by the supplied ordinary rule. Recovering the rest of the old holdings is unnecessary. This conditional theorem covers arbitrarily large reached stages.

At a first cut the qualification can matter. A built eight-name source with \(01234,125,346,567\) has two loose names, 0 and 7. Either middle holder witnesses their parents together, so the sole birth is \(078\), with one fresh name. Making 0 the only 1 of \(01234\) forces 5 and 6 to be 1 and then forces 7 to be 0. In its 160 reached words the corrected minimum for \(u=0,f=8\) is \(-1/40\), attained at \(1,2,3,4,7\). Distinction 7 lies outside the preceding holder. All source and reached rules satisfy the local projection and erasure checks. This example concerns strictness of the individual reading. Its two known inputs still identify 7 as belonging to the other parent.

**The recursively split weighting.** Forget the current loose names once their identities have been established. The marginal on the remaining names equals their entire preceding-stage weighting because a predecessor word distributes all of its mass among its extensions. A consumed older \(u\) was loose at that stage. Its two values have equal weights at a fixed exterior whenever both are allowed. At the supplied starting stage this follows from uniformity. At a later preceding stage the ancestor weight and every extension denominator depend only on the inputs to that step's births. Its fresh \(u\) changes neither. Thus the older correlation \(C_{uz}\) on its own has minimum
\(-\Pr(H\setminus\{u\}\ {\rm constant})\) at all \(z\in H\setminus\{u\}\). The same pin completion gives strictness at every exterior older name under the single-meeting hypothesis. This proves the same predecessor recovery for this weighting after the current loose names have been identified. It uses preservation of the older marginal. A swap between a current fresh name and an inherited name need not preserve recursive weights.

## The unmarked 28-name table under uniform weighting

The first loose-name tests in the [exact 28-name table](../../artifacts/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B-E001_pair_growth/target.json) limit the possible current live supports to the six below. Each pair of proposed loose names has identical correlations to all other names.

| Indices | Possible live support \(P_{ij}\) | Possible loose names |
| --- | --- | --- |
| 01 | 4, 7, 16, 17 | 16, 17 |
| 02 | 5, 10, 18, 19 | 18, 19 |
| 03 | 6, 13, 20, 21 | 20, 21 |
| 12 | 8, 11, 22, 23 | 22, 23 |
| 13 | 9, 14, 24, 25 | 24, 25 |
| 23 | 12, 15, 26, 27 | 26, 27 |

If one of a listed pair \(f,g\) is loose, both must be loose. Otherwise \(g\) has another holder \(H\), and \(C_{gz}-C_{fz}\) is strictly negative at every \(z\in H\setminus\{g\}\) by the preceding proof. Its measured value is zero at every such \(z\). The other two places of a live \(P_{ij}\) are inherited. A positive-age not-all-equal stage reached by a funded birth has at least one live holder because every birth under this law has a fresh distinction.

For each inherited input \(u\) of a possible \(P_{ij}\), the minimum of \(C_{uz}-C_{fz}\) over **all** other names is \(-627437/3872140\) for either loose \(f\). Its three minimizers are precisely the other three names of the following indicated \(H_i\) or \(H_j\).

| Index \(i\) | Preceding support \(H_i\) |
| --- | --- |
| 0 | 0, 4, 5, 6 |
| 1 | 1, 7, 8, 9 |
| 2 | 2, 10, 11, 12 |
| 3 | 3, 13, 14, 15 |

The old holder cannot be smaller than these four. The minimum probability of a constant word over all 3,276 named triples is \(4406513/30977120>0\). For each triple this probability is \((1+C_{ab}+C_{ac}+C_{bc})/4\), so the table itself excludes every possible three-place rule. Its entire support is therefore forced whenever a selected \(P_{ij}\) uses its \(u\). This conclusion holds even if the actual preceding cut was a supplied source containing repeated meetings.

Let \(F\) be the nonempty selection of pairs \(ij\) that actually correspond to live \(P_{ij}\). Its endpoint indices represent precisely the live holders of the preceding cut. Every such holder had at least one loose distinction and the funded round spent every one on these births. Hence \(H_i\) had exactly \(d_i\) loose places, with \(d_i\) the number of selected pairs containing \(i\). Its other \(4-d_i\) places were already shared. Write \(t_{ij}\) for the number of indices \(k\) for which both \(ik\) and \(jk\) are also selected.

The next witnessed sets on the selected \(P\)'s collect all pairs \(ij\) with a given endpoint \(i\). Three or more selected pairs that pairwise intersect but do not share one endpoint must be the three pairs of a triple of indices. A fourth cannot intersect all three without coinciding with one of them. Consequently the provisional demand for \(P_{ij}\) was
\[
             (d_i-1)+(d_j-1)-t_{ij}.
\]
Each common third index replaces two two-parent groups through \(P_{ij}\) by one three-parent group. Since \(P_{ij}\) has two inherited names and two fresh names, its fresh floor is one and its demand must be exactly two. Of the 63 nonempty selections, exactly 14 pass this equality at every selected pair. They are the four three-pair selections with one index common to all, the three cycles of four pairs, the six selections missing exactly one pair and the full selection. All use four indices. [All 14 selections](../../artifacts/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B-E001_pair_growth/witness_recovery.json)

The previous witnessed pairs on the four \(H\)'s must be exactly \(F\). Any witnessed pair gives a birth or belongs to a larger birth. All the births at that cut were the selected two-parent births. In particular, each triple of pairwise witnessed predecessors has a joint witness, since otherwise it would be contained in a birth of at least three parents.

- Where three selected pairs share index \(i\), the three other indices must be witnessed separately with \(i\). The corresponding \(H_i\) has only \(4-3=1\) previously shared place. It cannot meet those three distinct witnesses.
- With just \(ab\) absent, each of the two other indices has degree three. The triple with \(a\) and the triple with \(b\) both require witnesses at that index. A single witness would also witness the missing \(ab\). Again there is only one shared place.
- With four pairs in a cycle, each \(H_i\) needs two distinct witnesses and has exactly two previously shared places. There must be a different \(J_{ij}\) witnessing each selected pair since every meeting by a third \(H\) would witness an absent pair. The four \(H_i\) are mutually disjoint, so none of them can serve as one of the four witnesses.

In the four-cycle case, there are eight current loose names. The total number of physical incidences is \(2(28)-8=48\). Four live \(P\)'s and four forced \(H\)'s account for 32 of these. Each of the four required witnesses must use at least four places, exhausting all 16 remaining incidences. Each witness holds one place from each of its two specified \(H\)'s. Exactly four names occur in neither the known \(H\)'s nor the selected \(P\)'s. Each has two distinct holders, so their meetings among the four witnesses have degree two at each witness. The six possible meeting multisets consist of the three cycles through all four and the three ways to form two double meetings. Assignment of the two unused names in an \(H_i\) to its two witnesses only renames those two distinctions. Assignment of the four entirely unused names to their specified meetings also only renames them. Total state count is therefore decided by these six cases for any of the three selected four-cycles.

The measured disagreement fractions require the total number of uniformly weighted words to be divisible by **15,488,560**, their common least denominator. Inclusion–exclusion on the twelve physical rules gives the six totals 55,707,884, 53,502,474, 53,913,902, 55,707,884, 53,913,902 and 56,329,350. None satisfies that divisibility requirement. For a set of simultaneously violated rules the state count is \(2^b\), where \(b\) is the number of independent name classes after identifying the names in each of those constant rules. This integer calculation does not require enumerating all words of width 28. [Exact count replay](../../experiments/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B-E001_pair_growth/witness_recovery.py)

Thus all six \(P_{ij}\) are current live holders and all four \(H_i\) are known. The twelve current loose places, the ten known four-place supports and the four remaining singleton incidences at names 0, 1, 2, 3 leave precisely one further four-place holder on those four names. This gives the complete named current presentation as a consequence. Each choice \(i,j,k\) now gives the actual unheld triple \(P_{ij},P_{ik},P_{jk}\). Each \(P_{ij}\) belongs to two such triples and uses both loose names. The four prospective births pairwise share a parent, and no parent holds all four, so their unique maximal unheld group gives demand one to each. Their parent count is three. The prescribed fresh count is one in all four births.

The age restriction used at the start of the argument is material. An unconstrained comparison against every supplied, possibly closed start need not supply any current loose name or any previous demand to invert. The all-size witness result applies once the live holdings and their loose places are readable. The separate [inherited comparison](../../artifacts/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B/STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B-E001_pair_growth/inherited_inversion.json) uses the older marginal and its own exclusion of four-cycle competitors. Independent program referee pending.
