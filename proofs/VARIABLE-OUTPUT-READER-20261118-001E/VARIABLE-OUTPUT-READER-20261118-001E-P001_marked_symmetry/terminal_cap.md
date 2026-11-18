# A live input and an input consumed by a terminal junction have different distances

Write \(K(a,b)=D(a,b)+1\). An ordinary neighbor of a junction shares a distinction with it. The exterior is joined to each loose distinction in the classical wired-graph description.

**Terminal-junction theorem.** Let \(v\) be a junction with \(p\) parents and \(h\in\{2,3\}\) outputs, all still loose. It consumed an input \(e\) from an older junction \(u\). Suppose a remaining loose distinction \(l\) at \(u\) is in a legal triple in the current arrangement. For *every* fresh output \(f\) at \(v\),
\[
                  K(e,f)\le p+h < K(l,f).
\]
In particular exchanging \(l,e\) while fixing \(f\) cannot preserve the full table. This covers all mixed counts and arbitrary widths.

A site with no ordinary children can be deferred until the last addition. Any parent pair that relied on it for a witness was already a parent pair of that site and had an earlier witness. Removing a witness cannot create a forbidden common neighbor. If the deferred site took three parents, no later site can have become their first alternative common witness. Such a site would have had to join on the same three after they already had the deferred one in common. We may consequently regard \(v\) as last. Let \(P\) be the set of its \(p\) consumed loose bits in the prefix and \(F\) its fresh outputs. Its star is a bond, proving the upper bound on \(K(e,f)\). [Source graph and cut facts](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/separator.md)

Write \(b,c\) for the other two marked holders and \(l_b,l_c\) for their loose bits. All three holders lie on one ordinary bipartition side, so neither \(b\) nor \(c\) is the neighbor \(v\) of \(u\). The pair witnesses can all be chosen in the prefix. If \(v\) witnessed a pair after the join, those two parents had an earlier witness. No old witness was common to all three. Choose one witness for each pair to obtain the simple six-cycle on \(u,b,c\) and their witnesses.

Suppose a bond through \(l,f\) had size at most \(p+h\). Any equation containing \(f\) uses the last star. It has support \(F\cup(C\mathbin{\triangle}P)\), where \(C\) is the cut of a set \(U\) of old ordinary vertices. Since \(l\notin P\) is loose, \(u\in U\). Write \(j=|C\cap P|\). The size bound gives
\[
            |C|\le 2j.
\]
In the prefix use the two paths from \(u\) through its respective pair witnesses to \(b,c\), followed by their marked loose bits to the exterior. Both paths cross \(C\). Their edges are disjoint, and neither path meets \(P\) or \(l\). Hence
\[
            |C|\ge j+3.
\]
As \(j\le p\le3\), this forces \(j=p=3\) and \(|C|=6\). All three old parents of \(v\) are inside \(U\). Exactly two crossings remain after counting \(P\) and \(l\).

If both \(b,c\) are inside, their loose bits use the two remaining positions. There is no ordinary crossing. Ordinary connectivity gives the whole prefix for \(U\). Its six loose distinctions split into the two legal, complementary triples \(P\) and \(\{l,l_b,l_c\}\). The common-prefix theorem says that after adding a gate on either triple the old triple cannot remain legal, contradicting the hypothesis. If exactly one of \(b,c\) is inside, its loose mark leaves only one position for ordinary crossings. The six-cycle meets both sides and needs at least two. [Complementary-cap theorem](../../VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/complementary.md)

Both \(b,c\) must therefore be outside. The entire ordinary boundary of \(U\) consists of two edges, one on each of the two-step arms from \(u\) to \(b,c\).

Every ordinary cycle is a binary sum of four-cycles. In a cycle take its latest site. Its two old neighbors on the cycle were already linked through an earlier common neighbor when it joined. Adding the resulting four-cycle removes the latest site and leaves an even edge set of older sites. Decompose that set into cycles and induct. Thus a four-cycle uses the first of the two crossing edges, and necessarily uses the second one as well. If the two crossing edges have four distinct endpoints, both their inner endpoints and their outer endpoints must be neighbors in the square. They cannot both cross at the ends nearer \(b,c\), since their inner endpoints would be two distinct witnesses on the same bipartition side. If one crosses at \(u\) and the other at an outer marked holder, the outer adjacency makes the first arm's witness adjacent to the other marked holder as well. That gives an ordinary neighbor common to \(u,b,c\). The two outer endpoints cannot coincide because the arms have distinct marked holders, distinct witnesses and disjoint bipartition roles. The only case left has both crossing edges incident to \(u\).

In that case \(u\) retains \(l\) and supplies \(e\) to \(v\), so at most one of its outputs can be among the two crossings into the marked side. At least one ordinary site outside \(U\) precedes \(u\). Every nonempty prefix before \(u\) is connected and cannot pass from outside \(U\) into \(U\) without \(u\). Hence all other sites of \(U\) are younger than \(u\). To join with the other two parents in \(U\), the three-parent site \(v\) used two different earlier witnesses with \(u\). Both witnesses are in \(U\), since no other old site in \(U\) meets the exterior of \(U\) in the ordinary graph. The two edges to these witnesses, the edge \(e\), and the loose bit \(l\) would give \(u\) at least four outputs. This contradicts the growth law and proves the strict inequality.

The proof uses an orientation from some realizing history solely to certify the impossibility. The distinguishing entries themselves belong to the current matrix. The argument covers a last addition with all its outputs loose. Additional attachments using those outputs can alter which short bonds witness a pair. The theorem also allows a more general isometry to move the distinguishing output along with the marked bits.
