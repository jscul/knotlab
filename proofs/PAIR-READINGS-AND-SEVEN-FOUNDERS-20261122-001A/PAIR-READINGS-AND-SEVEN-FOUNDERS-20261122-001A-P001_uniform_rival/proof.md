# The 465 uniform pair readings determine the seven next births

**Theorem.** Consider the specified table on 31 named distinctions, giving each complete allowed current word equal weight. Among all positive-age presentations under the ordinary not-all-equal law with these readings, the next complete cut has the seven two-parent births listed below, with the stated fresh grants. This holds for any finite admissible founding source and any positive observed age, including disconnected sources and repeated meetings on distinct names. The identification concerns the next cut. The input and its scope are fixed in the [preregistration](../../../research/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001A/preregistration.md).

## Reduction to the one loose name

Write the values as signs and let \(C_{ij}=\mathbb E[s_i s_j]=1-2\Pr(s_i\ne s_j)\), with \(C_{ii}=1\). The prior proof uses only the named pair readings, the allowed projections and the complete-cut funding rule to list possible latest holdings. With uniform weights there are six possible latest holdings, 63 nonempty disjoint selections and 3,544 complete earlier assignments to screen. The previous grant counts exclude 3,491 and the previous paid groups exclude 41. Of twelve survivors, seven give the same seven next births and five give the same two next births. The latter all require the lone latest holding \(F=\{8,29,30\}\). The archived argument and its whole finite reduction were checked again against the sealed data. [Previous reduction and necessary conditions](../../../research/NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001A/weighting_comparison.md) · [Exact replay](../../../research/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001A/results.json)

If \(F\) alone formed, its paid name was 8 and its fresh names were 29 and 30. Each preceding word extends in precisely three ways. Thus the 406 old pairs on names 0 through 28 have the uniform law on the preceding relation. The other 59 equations are exactly \(C_{29,30}=-1/3\) and \(C_{fz}=-C_{8z}/3\) for \(f\in\{29,30\}\) and \(0\le z\le28\), including \(z=8\). The complete cut would consume every preceding loose name, so 8 was the only such name. Each of the other 28 names belonged to two distinct holders. Each holder is a subset of at least three distinct names, ruled by not-all-equal. Its entire allowed relation is the intersection of those holdings. This static description includes every possible earlier age. For an exclusion we may even admit redundant constraints and omit the source essentiality and projection requirements.

Here are the prior forced holdings on those 29 names.

| Holder | Physical names |
| --- | --- |
| \(H\) | 3, 5, 6, 7, 8 |
| \(P_3\) | 1, 2, 3, 14, 15 |
| \(D\) | 5, 13, 23, 24, 25 |
| \(E\) | 6, 16, 26, 27, 28 |
| \(P_7\) | 0, 4, 7, 10 |

For completeness, in a loose name's row its companions minimize the signed moment. If the companions are constant with probability \(q\), their moment with the loose name is \(-q\). On a mixed companion word the loose sign has conditional mean zero. On a constant one the loose sign opposes every companion, which also bounds every exterior correlation below by \(-q\). The minimum at 8 is \(-1332653/20039377\), with minimizers exactly 3, 5, 6, 7. Every two- or three-name subset of those four has constant mass greater than \(q=1332653/20039377\), forcing \(H\). Erasing \(H\) and 8 gives one old lift of a constant companion word and two of a mixed one. In particular the residual word count is \(N(1+q)/2\). For each companion \(a\) the residual row is
\[
 C'_{az}=(C_{az}-C_{8z})/(1+q),\qquad z\ne a,8 .
\]
Indeed, given any residual word, summing \((s_a-s_8)s_z\) over its legal lifts always gives \(2s_as_z\). Any residual event has probability at least its old probability divided by \(1+q\). Applying the same minimum test to the four newly loose names gives the other rows above. Dividing the old constant probabilities of each possible proper subset of two or three companions by \(1+q\) still exceeds the mass required by its new minimum in every case.

Complement symmetry determines every signed three-name pattern from the three pair readings. The reduced denominator least common multiple is 200,393,770. The five compulsory holdings alone allow \(30\cdot15^3\cdot7\cdot2^9=362,880,000\) words, by first choosing \(H\), then its four other holdings, which intersect only it in one assigned name each, then the remaining nine names. Thus a predecessor would have exactly 200,393,770 words and exactly 106,860,150 after erasure. All individually identified residual pair and triple counts are nonnegative integers. Indeed removing the final unary holding from the attained 31-name presentation gives a real 29-name system passing these count and erasure tests, with the same 406 pairs, but with **thirteen** loose names. The following exclusion uses the obligation that the other twelve too would have to be shared. [Forward and deletion controls](../../../research/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001A/controls.json)

## What a second holder may share

No holder can have size three. For every one of the 3,654 triples its constant-word mass \((1+C_{ij}+C_{ik}+C_{jk})/4\) is positive. The smallest is \(2857630/20039377\). A not-all-equal holding on any such triple would forbid its constant words.

Call the rows of two names equal *outside the pair* when \(C_{xz}=C_{yz}\) for every \(z\notin\{x,y\}\). Two names with the same two holders may be exchanged without affecting any constraint. Uniform words then give them this row equality. Inspection of all 406 old pairs gives precisely the following nonsingleton classes.

\[
 \{1,2\},\quad\{17,18\},\quad\{19,20\},\quad\{21,22\},
 \quad T=\{23,24,25\},\quad S=\{26,27,28\}.
\]

Consequently two distinct holders can share at most three names. A shared triple must be \(T\) or \(S\). As the first is already in \(D\) and the second in \(E\), the two places per name force one of its holders to be that specific known five-place holder. Hence an additional holder meets any other holder in at most two names, except possibly in a triple of a five-place \(D\) or \(E\). In particular distinct additional holders meet in at most two names.

**Extension under prescribed values.** Let \(V\) be an additional holder. Remove \(V\) and any specified further holdings. Prescribe value 0 to any subset of \(V\); optionally prescribe 1 to one further name outside this subset. All remaining holdings can be satisfied simultaneously.

To prove this, drop remaining holders that already see both values. Any holder that has seen only zero has at least two unassigned names by the intersection bound just proved. A holder that has seen only one has at least three unassigned names because just one name was prescribed 1. An untouched holder has at least four. Make a temporary multigraph in the classical sense for the unassigned names. Its vertices are the unsatisfied holders, and each name belonging to two of them joins its two holders. Give a name belonging to just one a separate one-place dummy endpoint. A name occurring at neither can be chosen freely. This representation permits multiple meetings, and each component is treated separately.

In a component with odd-degree vertices, join every odd-degree vertex to one auxiliary vertex. Traverse the resulting Euler circuit from the auxiliary vertex and colour its successive names alternately. Remove the auxiliary names. At an original vertex of even degree at least two, an original arrival and departure have opposite colours. An original odd-degree vertex of degree at least three has at least two pairs of arrival/departure in the augmented traversal, and only one can use its auxiliary name. Thus every real holder of degree at least two sees both values. If all degrees are even and a degree at least four occurs, start at such a vertex. An internal visit there supplies both colours even when the circuit has odd length. All other real vertices have an ordinary paired visit. If all degrees are two, an even circuit alternates. In the remaining odd circuit every real holder has exactly two unassigned names and therefore, by the bounds above, already has a prescribed zero. Set every unassigned name in that circuit to one. This completes the asserted extension in every component.

## The pair readings force a common second holder

Suppose 8 is the sole loose name. Choose distinct \(x,y\in T\). They belong to \(D\) and each must have another holder. Assume their second holders \(V,W\) differ. Both are additional holdings. Put \(A=V\setminus\{x\}\) and \(B=W\setminus\{y\}\). Neither \(y\) belongs to \(A\) nor \(x\) to \(B\), because a name can occur at most twice. Erase only \(D\), retaining the uniform relation on all 29 names. Every newly admitted word has constant \(D\), hence \(s_x=s_y\). In the original relation equality of their exterior rows said \(\sum(s_x-s_y)s_z=0\) for every exterior \(z\). The same unnormalized equalities persist after erasing \(D\).

Given a permitted exterior word in the erased relation, the signs \(s_x,s_y\) have independent uniform allowed choices, one constrained only by \(A\) and the other only by \(B\). If \(u\) is the average sign on \(A\), the conditional mean for \(x\) is \(m(u)\), where \(m(-1)=1\), \(m(1)=-1\), and \(m(u)=0\) for \(|u|<1\). Define \(v\) from \(B\) in the same way. The exterior row equalities, averaged across \(A\) and \(B\), yield
\[
 0=\mathbb E[(s_x-s_y)(u-v)]
   =\mathbb E[(m(u)-m(v))(u-v)] .
\]
The expression inside the last expectation is nonpositive pointwise. It is strictly negative when \(A\) is all zero (sign \(-1\)) and \(B\) contains a one. Such an exterior occurs. Indeed \(|B|\ge3\), while \(|V\cap W|\le2\), so choose \(z\in B\setminus V\). Prescribe \(A=0\) and \(z=1\) and erase \(D,V,W\). The extension just proved satisfies all other holders. Then \(x,y\) have legal choices for restoring \(V,W\) to the relation without \(D\). That exterior has positive weight. This contradicts the equality. Therefore each pair of names in \(T\) has the same second holder, and a single additional holder \(V\) contains all of \(T\).

## The measured sign excludes that common holder

Write \(V=T\cup B\), where \(B\ne\varnothing\) by the size-three exclusion. Consider all assignments outside \(T\) that satisfy every holder other than \(D,V\). No remaining holder contains any name of \(T\). Over each such exterior, first allow all eight assignments of \(T\), then restore \(D,V\). They can remove only constant \(T\) assignments. Write \(s\) for the common sign of a removed assignment. For distinct \(x,y\in T\) and \(d\in\{5,13\}\), both \(s_xs_d\) and \(s_xs_y\) summed to zero over the original eight. Thus their difference, summed over restored legal words, is exactly
\[
 \sum_{\mathrm{legal}}(s_xs_d-s_xs_y)
       =\sum_{(\mathrm{exterior},s)\ \mathrm{removed}} (1-s\,s_d).
\]
Every summand on the right is nonnegative. The measured correlations at \(x=23\) give
\[
 C_{23,5}=C_{23,13}=C_{23,24}=C_{23,25}
       =-6671467/100196885 .
\]
The left side is zero. Every removed assignment must therefore agree with both 5 and 13 on its constant sign.

But 5 already belongs to \(H,D\), so it cannot belong to \(V\). Drop \(D,V\), prescribe every member of \(B\) to be zero and 5 to be one, then extend by the lemma. Set \(T\) all zero. This word satisfies every remaining holder and also \(D\), because 5 is one. Restoring \(V\) removes it. It contributes two to the right side for \(d=5\). This is the contradiction. It rules out even a physically redundant extra holder in the enlarged static class. Arbitrary ages, wide holdings, disconnected parts and repeated meetings were all included.

A separate numerical identity cross-checks the same last step. For each \(t\in T\) and every exterior \(z\) the measured table gives \(14 C_{tz}+C_{5z}+C_{13z}=0\), including diagonal moments when \(z=5,13\). Over a fixed exterior with only \(D\) imposed, the sum of \(14s_t+s_5+s_{13}\) over its legal \(T\) words vanishes. Opposite companion signs leave eight words; agreeing companions leave seven and exclude exactly their own constant sign. Any additional removal by \(V\) has constant sign \(s\) on all of \(B\). For a fixed \(z\in B\), its removed term \((14s_t+s_5+s_{13})s_z\) is at least 12. The constructed word makes the removal strict. This contradicts the measured identity independently of the single equal-moment subtraction.

## The attained next cut

The one-latest-holder branch would have required the excluded predecessor, so every possible positive-age history in the named comparison has the six latest holdings below. The prior complete-cut calculation agrees on the next roster for every surviving earlier assignment. Direct ordinary growth on an admissible 17-name, five-knot founder witnesses this branch. [Independent forward counts and funded groups](../../../research/PAIR-READINGS-AND-SEVEN-FOUNDERS-20261122-001A/controls.json)

| Latest holder | Named holding |
| --- | --- |
| \(A\) | 0, 9, 17, 18 |
| \(B\) | 4, 14, 19, 20 |
| \(C\) | 12, 15, 21, 22 |
| \(D\) | 5, 13, 23, 24, 25 |
| \(E\) | 6, 16, 26, 27, 28 |
| \(F\) | 8, 29, 30 |

| Next parent pair | Fresh grant per birth |
| --- | ---: |
| \(AB,BC,DF,EF\) | 2 |
| \(AE,CD,DE\) | 3 |

Thus seven actual two-parent births receive seventeen fresh distinctions. This identifies the named parent groups and their prices from the exact uniform table. Further historic reconstruction, readings at age zero, incomplete or unnamed readings, and general identification from pair tables lie outside the theorem.
