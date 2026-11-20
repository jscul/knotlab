# A seven-knot minimum for a witnessed part with two independent cycles

The exploratory atlas screen found no eligible live part with two independent cycles through six original knots. At seven there is one ordinary meeting graph, with two equivalent choices of live members. Its least lawful funded realization has **25 distinctions** under either knot law. The particular rule that recognizes the whole source by repeated meetings first becomes available at **28 distinctions**. This checks a structural prerequisite for the identified generator. The recurring-release proof has further recognition and ancestry obligations. [Identified construction and obstruction](source.md)

## Exhausted structural panel

Take the connected ordinary simple graph underlying the physical holdings. Use every graph up to isomorphism from the NetworkX graph atlas, and test every literal subset of its holders as live. This counts two subsets separately even when a graph symmetry exchanges them. For each holder, including a spent holder, form the set of its live neighbours. A set of size at least two supplies a witness role, joined in the incidence graph to its live members. An ordinary holder can play both a live role and a witness role, which remain distinct nodes in this calculation.

Reject a pair of live holders with two different witnessing holders. Among the remainder, reject every unheld complete triple. This is sufficient to enforce the corresponding restriction on larger complete groups. If all triples of a larger group are held, fix a pair in that group. The triples extending this pair must all belong to its unique witness, which therefore holds the entire group. Once both gates pass, each part is scored by the number of its incidence relations minus the number of its roles plus one. For example, a single witness holding three live members has cycle rank zero.

| Original knots | Connected graphs | Live subsets including empty | Pass both witness gates | Passing subsets with a candidate pair | Candidate pair occurrences in passing subsets | Parts of rank two or more |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 2 | 2 | 0 | 0 | 0 |
| 2 | 1 | 4 | 4 | 0 | 0 | 0 |
| 3 | 2 | 16 | 15 | 5 | 5 | 0 |
| 4 | 6 | 96 | 69 | 27 | 36 | 0 |
| 5 | 21 | 672 | 392 | 212 | 354 | 0 |
| 6 | 112 | 7,168 | 2,910 | 1,716 | 3,098 | 0 |
| 7 | 853 | 109,184 | 28,841 | 18,137 | 34,526 | 2 |
| **Total** | **996** | **117,142** | **32,233** | **20,097** | **38,019** | **2** |

The two successes have one rank-two part each. Both use atlas graph 443, with ordinary meetings $01,04,14,24,26,34,35,56$. Take holder 1 to be spent. The other mask is its image under the exchange of 0 and 1. Its witness rosters are
\[
\{0,4\},\quad \{4,6\},\quad \{4,5\},\quad
\{0,2,3\},\quad \{3,6\},\quad \{2,5\}.
\]
There are six live and six witness roles with thirteen incidence relations in one connected part. This gives rank two. The held three-member roster contributes three distinct candidate pairs but no unheld triple.

## Distinction budgets at seven knots

Eight distinct ordinary meetings require at least eight shared distinctions. The eight candidate pairs require a total of sixteen loose distinctions at their endpoints. With holder 1 spent, the minimal open counts at $0,2,3,4,5,6$ are $3,3,3,3,2,2$. Those supplies already meet the three-place floor at every live holder. Holder 1 has two distinct neighbours, so at least one of its meetings must carry a second shared distinction to make its star a three-place knot. This gives the lower bound $8+16+1=25$. Doubling $01$ attains it. The parity star supports pass the wired connectivity test on removing any one holder. For not-all-equal, each unpinned live knot can put opposite values on its two own loose distinctions. When the spent holder is unpinned it has at least one unpinned shared distinction, since it meets two different live holders. It can see both values regardless of the pinned legal star. The literal representative was checked by satisfiability as well.

The source can also carry a mark on every original holder. That specific mark asks that every original participate in a repeated meeting. At least four extra shared distinctions are needed to cover seven holders in pairs, so the width is at least 28. Doubling $01,24,26,35$ attains the bound and leaves no nontrivial permutation of the original holders preserving meeting multiplicities and open counts. The repeated meetings recover the original subset in all later ordinary stages because a birth attaches just one distinction to each parent. Given the original subset, the smallest width at which all original holder roles are fixed by that weighted source is **26**, attained by doubling $01,24$. At width 25 the reflection of the five-member ordinary cycle remains a symmetry whichever meeting at the spent holder is doubled. The 26 result presumes that the subset has already been recovered. It gives no width bound for other physical rules that might recognize originals.

The bounded weight enumeration includes both successful masks, all allocations of at most four extra shared distinctions, and the minimum opens for each resulting graph. Extra loose distinctions cannot lower a minimum. The exact counts are:

| Distinctions | Repeat allocations tested | Lawful, funded | Original holders rigid given their subset | Every original incident to a repeat | Both rigidity and coverage |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | 2 | 0 | 0 | 0 | 0 |
| 25 | 16 | 4 | 0 | 0 | 0 |
| 26 | 72 | 30 | 16 | 0 | 0 |
| 27 | 240 | 128 | 88 | 0 | 0 |
| 28 | 660 | 408 | 320 | 16 | 8 |

Each minimum representative gives eight births in the first ordinary layer and twelve in the second, with the same counts under parity and not-all-equal. The exact finite result applies to the identified rank-two requirement, independently of loose counts and physical meeting multiplicities in the structural screen. Sources outside the identification class and other ways to recognize or release products require different tests. [Checker](../../experiments/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators/minima.py) · [Exact receipt](../../artifacts/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators/minima.json)
