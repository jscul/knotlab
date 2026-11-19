# Three readings distinguish an internal six-bit bond from a junction

The six-bit bond below occurs after a legal seven-to-six step at nine ordinary sites. Four more binary additions make every one of its bits shared. Three pair readings already exclude that support as a physical six-place junction in any reachable presentation with those readings. The certificate survives every further legal addition. The same ordinary two-connected part can contain arbitrarily many different eligible triples at once.

## An input and an output read the whole arity

**Lemma.** At a nonseed site \(v\) with \(p\) parents and \(h\) fresh distinctions, take any input \(e\) and any output \(f\), including an output that has since been used. Then

\[
                         K(e,f)=p+h.
\]

Here \(K=D+1\) is the least size of a bond containing both bits. The growth law permits \(1\le p\le3\) and \(2\le h\le3\). The lemma allows further ternary sites anywhere. Write \(e=a\to v\). Give the outside endpoint to any loose bit when measuring a cut. The star at \(v\) is a bond and gives the upper bound. [Cut representation](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/separator.md)

Let \(U\) be any ordinary shore whose boundary contains \(e,f\). If \(v\in U\), the chosen input enters and the chosen output leaves. A shore of one or two sites containing \(v\) costs at least \(p+h\), since a second site of arity at least three can cancel at most one ordinary meeting. In a larger shore, consider its last three sites in birth order. At most two of their outputs can be used within the shore, by ordinary simplicity and bipartiteness. If those three include \(v\), they make at least \(h+4\) outputs and export at least \(h+2\). The incoming \(e\) gives at least \(h+3\ge p+h\). If \(v\) is earlier, its chosen output and input are additional to at least four exports from the last three, giving at least six.

If \(v\notin U\), then \(a\in U\), and \(f=v\to b\) must already have a later ordinary holder \(b\in U\). At the birth of \(v\) there were \(p\) edge-disjoint ordinary paths from \(a\) to \(v\). One is \(e\). For each other parent \(c\), use the path from \(a\) through its earlier common witness with \(c\), then through \(c\) to \(v\). With three parents the two witnesses are distinct, since a joint witness would forbid the addition. Each of the \(p\) paths contributes a distinct crossing. The bit \(f\) is later, and the latest site of \(U\) is at least as late as \(b\). It sends at least two outputs out of \(U\), distinct from all the preceding crossings. This gives \(p+3\ge p+h\).

**Six-place test.** A true six-place support admits a partition into three inputs and three outputs, with all nine cross readings equal to six. In particular, three mutually disjoint pairs with \(K\le5\) exclude a six-place support. Each whole pair would have to lie on one side, while each side has odd size. The reader needs no orientation and no entries outside the six proposed bits. Two disjoint small pairs alone still allow such a partition as a counting test. The exclusion concerns every table bijection carrying the proposed support, without any assumption on the rival's birth order or number of ternary sites.

## The six-bit bond and its four-step internalization

In the following histories a site makes two fresh bits unless three are specified. Each parent supplies one physically loose bit. Bits loose at the same holder may be interchanged. Let the ternary seed be \(T\).

| New site | Parents | Fresh bits | Pair witnesses where needed |
|---|---|---:|---|
| \(a,b\), separately | \(T\) each | 3 each | Unary |
| \(u\) | \(a,b\) | 2 | \(T\) |
| \(c\) | \(T,u\) | 2 | \(a\) or \(b\) |
| \(P_{ab},P_{ac},P_{bc}\), separately | The indicated pair of \(a,b,c\) | 2 each | \(T\) or \(u\) |
| \(z\) | \(P_{ab},P_{ac},P_{bc}\) | 2 | The three separate sites \(a,b,c\) |

Before \(z\), the frontier has one bit at \(u\) and two at each \(P\). The three parent sites of \(z\) have no common neighbor since each meets exactly its named pair. After \(z\), the frontier \(W\) has one bit at each of \(u,P_{ab},P_{ac},P_{bc}\) and both fresh bits at \(z\). This is a six-bit equation, the sum of the nine site stars. It is a bond. A nonminimal six-bit equation would split into two disjoint three-bit bonds, and the seed is the only ternary site. Every three-bit bond is a ternary star. Equivalently the selected ordinary shore is connected and its complement is the single outside vertex.

Use four binary two-output additions, with the indicated old bits.

| New site | Parents | Earlier common witness | Bits of \(W\) used |
|---|---|---|---|
| \(E\) | \(u,P_{ab}\) | \(a\) | Both inputs |
| \(F\) | \(P_{ac},P_{bc}\) | \(c\) | Both inputs |
| \(G\) | \(z,E\) | \(P_{ab}\) | One old output of \(z\) |
| \(H\) | \(z,F\) | \(P_{ac}\) | The other old output of \(z\) |

The two inputs of \(E\), the two inputs of \(F\), and the two outputs of \(z\) give the three disjoint pairs on \(W\). Their stars bound the three readings by \(4,4,5\), respectively. Thus the six-place test already applies after \(F\). After \(H\) all six original bits are ordinary shared distinctions. Four additions are necessary to consume them all when only binary joins are allowed. Three would have to consume exactly two members of \(W\) per join. The two bits at \(z\) cannot join one another, and every other original loose holder is on the opposite ordinary color from \(z\).

Every further addition preserves the three short upper bounds, since the same three site stars remain bonds. It also preserves the bond \(W\). Each old state extends across a legal new parity star by assigning its fresh bits, so no proper nonempty subset of \(W\) can acquire an equation. This permanence allows arbitrary continuations under the original rule, including continuations that change the number of ternary sites or the total amount of free output. The source before this extension had just one ternary site.

For a literal naming, assign consecutive bits starting at zero, and at each parent use its least loose bit. At width 21 the six bits are \(10,14,16,18,19,20\). At width 29 all are shared. In order, the three pairs above are \((10,14),(16,18),(19,20)\). The [literal growth replay](../../VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/check_gluing.py) verifies both histories. Enumerating the 511 nonempty star sums on the nine-site history finds no proper nonempty subset of its six-bit word.

## Arbitrarily many live choices in the same ordinary part

After the four joins above, \(G,H\) each have two loose bits and share \(z\). Make a binary site \(K\) with three fresh bits on \(G,H\). On each of its outputs grow a different unary three-output site \(r,s,t\). Make three binary three-output sites \(Q_{rs},Q_{rt},Q_{st}\) on the indicated pairs. Their pairs have witnesses \(r,s,t\) and they have no common witness, so there is a legal triple choosing one loose bit at each \(Q\). Finally make a binary two-output join on \(G,r\), using the spare bit at \(G\) and the third output of \(r\). Its witness is \(K\).

The entire ordinary graph stays connected after deleting any one site. For the initial fixture, start with the complete bipartite graph on \(T,u\) and \(a,b,c\). Deleting any vertex leaves it connected. Adding a vertex on two or more distinct old neighbors preserves this property. This gives the nine-site graph after adding the three \(P\)'s and \(z\), and also covers \(E,F,G,H,K\). The six vertices \(r,s,t,Q_{rs},Q_{rt},Q_{st}\) form a cycle. Its three connections to \(K\) and the additional path from \(r\) to \(G\) through their binary join keep it connected to the old part after any one deletion. In particular, the live choices and the six internal bits belong to the same ordinary two-connected part.

Repeat with \(Q_{rs},Q_{rt}\) as the older pair in place of \(G,H\). They have their pair witness \(r\). One supplies an input to the next \(K\) and to the next additional path, using two of its three available outputs. The other uses only one. Each of the three older \(Q\)'s retains a loose bit. None of these additions meets all three older holders, so their triple stays eligible. Each repetition adds another such triple in the same two-connected part. Every later join in this construction has at least as many outputs as inputs. The example with four repetitions has 45 sites, 121 bits, and four simultaneously eligible triples on disjoint groups of holders. A literal replay checked the parent rule, the loose bits of every marked group and connectivity after each possible one-site deletion.

## Arbitrarily many internal six-bit bonds with a test through four

There is also a family with many different six-bit supports in one finite source. Return to \(G,H\). On their two pairs of outputs form two separate binary two-output joins \(k,l\) on those same parents. Then form \(m\) on \(E,k\) and \(n\) on \(F,k\), both with two outputs. The first pair shares \(G\) and the second shares \(H\). Exactly \(l,m,n\) now have loose bits, two apiece. The six bits form the entire frontier, a bond. They have three disjoint pairs already at \(K\le4\) because each of the holders has arity four.

The holders \(m,n\) share \(k\). On the two loose bits of each, form two separate binary two-output children on \(m,n\). The new pair of children have a common parent and can play the same role again. At each complete pair of joins the frontier consists of the unchanged two bits at \(l\) and four entirely new bits. Each frontier is a bond with the three-pair exclusion at threshold four. Its shore is the complete prefix at that stage. The shores are nested, and two different recorded supports meet in exactly the two bits at \(l\).

After recording any finite number of frontiers, run one more pair of joins to consume the last four recorded bits away from \(l\). On the two old bits of \(l\) grow separate unary three-output sites, then join those two sites by a binary two-output junction. They share \(l\). Now every bit of every recorded support is shared and lies on an ordinary cycle. For the two persistent bits the cycle passes through the two unary additions and their common child. Every other recorded bit was used in one of the complete bipartite two-by-two layers. The supports and their three-entry exclusions survive all further continuations. Literal replay at five recorded frontiers gave 30 sites and 65 bits. It checked that the five supports meet pairwise in two bits and that deleting any one of their distinctions preserves ordinary connectivity.

## A bound when the shore has at most four sites of one color

**Claim.** In a source with a single ternary seed, any ordinary shore of at least three sites and boundary at most six either has four sites of one ordinary color and five of the other, or has at least five of each. This bound allows all omitted vertices, input crossings and external witnesses.

For any selected sites the latest vertex has at most three neighbors inside their induced graph. If it has three, no other vertex of the same side can meet all three, since that vertex would already have been a forbidden common witness. This test is hereditary under further vertex deletions. In particular a complete three-by-three bipartite graph cannot occur. A four-by-four complete bipartite graph minus three disjoint edges cannot occur either. Each side has a full vertex, and each degree-three vertex would have all its earlier neighbors witnessed by that full vertex on its side. No vertex could be latest. More generally any four-by-four induced graph with at least 13 edges is impossible. Among at most three missing pairs, those contained in the union of one row and one column leave a complete three-by-three. Three missing pairs that have a shared endpoint admit this cover, as do any one or two missing pairs. The remaining case is the three disjoint pairs just excluded.

Let \(n\) be the number of selected sites. With at most three sites on the smaller side, there are at most \(2n-4\) internal meetings. With three rows, at most two columns can meet all three, and every other column contributes at most two. One or two rows give the same bound directly for \(n\ge3\). The boundary is at least \(4n-1-2(2n-4)=7\). A four-by-four split has at most 12 meetings, again giving seven. These arguments in particular settle every shore of size three through eight.

For four rows and \(b\ge5\) columns, say a column with three neighbors has type \(i\) if it misses row \(i\). With one full column there can be at most two three-neighbor columns. Two of the same type would give a complete three-by-three. Three different types with the full column would give the excluded four-by-four graph. With two full columns no three-neighbor column is possible. Without full columns each type occurs at most twice, and at most two types can occur twice. In fact, taking six columns from three doubled types would leave each of the four rows with at least four meetings. Each three-neighbor column has a twin, so none of these ten sites could be latest. In all cases the number of internal meetings satisfies \(e\le2b+6\).

Write \(s=1\) if the seed is present and zero otherwise, and \(h\) for the sum over nonseed sites of their arities minus four. The boundary bound gives \(2e\ge 4b+10+h-s\), so \(h\le s+2\). The four rows together have arity at most \(16+h\), and must hold all \(e\) meetings. Thus \(4b\le22+h+s\le26\), leaving \(b\le6\).

It remains to rule out \(b=6\). Some site in the shore must take three parents and make two outputs. Otherwise chronological insertion within the shore cannot decrease the boundary below that of its first three sites, which is at least seven. Indeed a site with \(p\) inputs, \(f\) outputs and \(j\le p\) earlier selected neighbors adds \(p+f-2j\). Thus \(h\ge1\), and the bounds leave \(e=17,18\). Both cases have no full column, since the presence of one or two full columns bounds \(e\) by \(2b+4=16\).

If \(e=17\), then \(h=s=1\). Every one of the 17 places allowed at the rows must be internal, so the seed is a column and the one high vertex is a row. Five columns have three internal neighbors and one has two. The five three-neighbor columns have arity at most four and could not have taken three parents. No row can be latest since all its outputs are consumed inside. Delete the only possible latest site, the two-neighbor column. Each row loses at most one meeting, leaving more neighbors than its possible number of inputs because every site makes at least two outputs. The other columns still have three earlier neighbors if chosen latest. Thus the remaining graph has no possible latest site.

If \(e=18\), then the six columns each have three neighbors and their type multiplicities must be \(2,2,1,1\). The rows missed by just one column each have five internal neighbors, contributing at least two to \(h\). Every row has at least four neighbors, and each doubled column has a twin. A singleton-type column must therefore be latest and take three parents. Remove it. The type counts are now \(2,2,1,0\), with a full row that witnesses all neighbors of each remaining degree-three row. Doubled columns still cannot be latest, and higher-degree rows cannot be latest. The other singleton-type column must also have taken three parents. These two columns and two rows now give \(h\ge4\), contrary to \(h\le s+2\le3\). The nine-site construction attains the surviving four-by-five split.

[Runnable history, connectivity and pair checks](structural_replay.py) · [Exact control values](structural_replay.json)
