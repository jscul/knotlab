# Four-bit pair readings exclude the proposed equation

Write \(K(e,f)=D(e,f)+1\) for the least cardinality of a bond through two named distinctions. A binary equation space means any binary linear space of supports on the names. Its bonds are its minimal nonempty supports. The source below uses the ordinary wired incidence graph to calculate these readings.

Take a four-place site \(t\) born on one earlier parent, and two four-place sites \(p,q\) born on \(t\). Each makes three outputs. A four-place site \(w\) takes \(p,q\) and makes two outputs. Site \(b\) takes \(p,q\), and site \(c\) takes \(t,w\). Either \(b\) or \(c\) may take a lawful third parent and may make two or three outputs. All six sites are distinct. Allow any reachable prefix, any intervening lawful additions preserving these incidences and any finite mixed continuation. Let \(ut\) be the input of \(t\), and write \(p_0,q_0,w_0\) for the remaining outputs of \(p,q,w\), even after they have been used elsewhere. Concatenated site names denote their shared distinction.

**Theorem.** If a bijection from this source to any binary equation space preserves the pair readings through \(K=4\), the image of

\[
               W=\{tc,wc,pb,qb,tp,wq\}
\]

is absent from its equation space. The same readings force the entire four-place support of each of \(t,p,q,w\). The source's own fifteen pairs in \(W\) nevertheless all have \(K\le6\). Pairs at one holder use its star of arity at most six. For each remaining pair take two adjacent central four-place holders, one at each bit. Their combined six-bit boundary is a bond because deleting the two ordinary holders leaves all remaining sites connected to the wired exterior. [Two-site deletion](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/inverse.md#two-elementary-source-restrictions)

## The four-bit certificate

A bond of size at most four with at least three ordinary sites on its shore can contain only bits born at sites making two outputs. Indeed, the latest three sites of that shore make at least six outputs, at most two of which can meet another of the three, by bipartiteness. None can feed an earlier ordinary site. The bound of four forces equality throughout. Those four outputs of the three two-output sites exhaust the boundary. Bonds on one site are stars. On two sites a bond of size at most four must be the sum of two adjacent ternary stars. In particular a shared bit born at a three-output site, whose endpoints both have arity at least four, can occur in a bond of size at most four only at one of its four-place endpoints. These statements use the full current presentation and continue to hold after further sites are added. [Small-shore proof](../../VARIABLE-OUTPUT-READER-20261118-001G/VARIABLE-OUTPUT-READER-20261118-001G-P001_two_three_fresh/extension.md#four-bit-shores-with-at-least-three-sites)

Let \(N_4(e)\) contain \(e\) and every other bit with \(K(e,f)\le4\). Write \(T,P,Q,A\) for the four-place supports at \(t,p,q,w\). Since \(tp,tq\) were born at \(t\), their neighborhoods are \(T\cup P\) and \(T\cup Q\). The two sites \(p,q\) are distinct and of the same ordinary color, so their stars do not meet. The common neighborhood is exactly \(T\), and \(K(tp,tq)=4\). Any rival bond realizing this value must use four bits from their common neighborhood. Hence \(T\) is a rival equation, after matching the names. The pair \(qw,qb\) similarly forces \(Q\). Both bits were born at \(q\), and the other endpoints \(w,b\) have the same color, so even when \(b\) has arity four the common neighborhood is exactly \(Q\). The pair \(pw,pb\) similarly forces \(P\). Finally \(N_4(pw)=P\cup A\) and \(N_4(qw)=Q\cup A\), forcing \(A\).

Only \(T,Q\) are needed to exclude \(W\). If \(W\) were a rival equation, the symmetric difference

\[
                  W\mathbin{\triangle}T\mathbin{\triangle}Q
                        =\{wc,pb,ut,q_0\}
\]

would also be an equation. Each of these four bits occurs in an observed bond of size at most four with a different bit, so none can be a singleton equation in the rival. A two-bit bond among them would contradict the observed absence of a pair minimum of two. Every binary word decomposes into disjoint bonds by repeatedly removing a minimal subword. The displayed four-bit word would therefore be a bond. Yet \(K(pb,wc)>4\). The bit \(pb\) was born at \(p\) and can belong to a bond of size at most four only at \(p\) or \(b\), neither of which holds \(wc\). This contradiction uses two forced four-bit equations and one excluded pair. All steps commute with an arbitrary bijection of the names.

## The whole binary space can be enlarged at the preceding cutoff

For **every** presentation covered by the theorem, adjoin the single extra parity equation \(W\) to its true equation space \(C\). The least weight in \(W+C\) is exactly four, and \(W\) becomes a bond. This gives the same full table through \(K=3\) on identical names.

Let \(E_0\) be the eight internal meetings from \(t,w\) to \(p,q,c\) and from \(b\) to \(p,q\). Every true cut has even intersection with every ordinary cycle. The set \(W\) selects three meetings in each of the four ordinary cycles

\[
 (t,p,w,c),\qquad(t,q,w,c),\qquad(t,p,b,q),\qquad(w,p,b,q).
\]

No bit belongs to all four cycles. Thus any word \(W\mathbin{\triangle}\partial U\) contains at least two members of \(E_0\). Suppose its weight were at most three. Then at most one cut crossing lies outside \(E_0\).

Neither \(b\) nor \(c\) can be in the ordinary shore \(U\). If one were inside, take the latest site reachable from it by following outputs within \(U\), including the starting site. Its two or more outputs leave \(U\). All are outside \(E_0\), since none of the four sites \(t,p,q,w\) can be a descendant of \(b\) or \(c\). The same argument applies if a private output \(p_0,q_0,w_0\) goes from its site inside \(U\) to another site inside. Its child and its subsequent descendants cannot return to the four central sites. Indeed the earlier inputs of \(p,q,w\) are fixed above and \(t\) precedes all three.

Consequently each of \(p,q,w\) contributes a different bit to \(W\mathbin{\triangle}\partial U\). If the site is inside, its private output crosses. If it is outside, its selected spoke \(pb,qb,wc\), respectively, appears since \(b,c\) are outside too. These exhaust the three proposed positions. The bit \(tc\) then forces \(t\) inside. Avoiding any additional bits on \(tp,tq,pw\) forces \(p\) outside, \(q\) inside, and \(w\) outside. The only crossing outside \(E_0\) is now \(q_0\). The earlier parent \(u\) must belong to \(U\), as otherwise \(ut\) gives another crossing. The nonempty set \(U\setminus\{t,q\}\) would have at most the single boundary bit \(ut\). All its sites are outside the six named ones, all eight internal meetings avoid it, and \(q_0\) runs from \(q\) to the complement of \(U\). This contradicts the two outgoing bits of its latest site. The four-bit word in the preceding section attains the lower bound.

There is no nonempty true subword of \(W\). A cut supported there has no crossings outside \(E_0\). The same forward-path argument puts \(b,c,p,q,w\) outside its shore. Then \(tq\), which is absent from \(W\), puts \(t\) outside as well. Every bit in \(W\) has both endpoints outside. It follows that \(W\) is a bond of the strict extension, since any proper subword in its new coset would differ from \(W\) by a nonempty true subword. The added space has exactly the original equations of size at most three, hence precisely the same bonds and pair readings through three.

Every pair in this enlarged binary space still has a finite reading. The four displayed odd cycles have no common site. For each ordinary site, one of the cycles therefore avoids its entire star. No added word can be contained in that star, since its intersection with the cycle is odd. All ordinary stars remain bonds and form a connected family covering the names. Here is a direct binary justification that any two names in such a family lie on one bond. Put a generator matrix in systematic form and join each pivot column to every nonpivot column marked in its row. Each bond is confined to one connected component of this incidence graph because the row space separates across components. Thus the graph is connected. On a shortest path between the two names add the rows corresponding to the pivot columns of the path. This word contains both ends. A subword can select only the path's pivot rows, as all other pivot positions are zero. Each internal nonpivot position on the path also sums to zero and has exactly two neighbors among those rows, so their selection flags agree. Hence every nonzero subword uses the entire word, which is a bond.

For the seven-site fixture with seed \(u=s\) and two-parent, three-output sites \(b,c\), this enlarged binary space has **no graph cut representation**. Let \(S,T,P',Q',A',B',C'\) denote the coefficients of the seven site equations, with \(H\) the coefficient of \(W\). Shorten on the five bits \(st\), one unused seed bit, \(tc,pw,qb\). Requiring zero at these bits gives

\[
             S=T=0,\qquad C'=H,\qquad A'=P',\qquad B'=Q'+H .
\]

Keep just \(tp,tq,pb,p_0,wq\), one loose bit at \(b\), and one at \(c\). Their seven respective values are

\[
         P'+H,\quad Q',\quad P'+Q',\quad P',\quad
         P'+Q'+H,\quad Q'+H,\quad H .
\]

These are all seven nonzero forms on three free coefficients. In a graph cut representation, shortening an edge identifies its endpoint potentials, and dropping coordinates deletes their edges. Both operations again yield graph cut spaces. At rank three such a space has at most six different nonzero column forms. A component of rank \(r\) has \(r+1\) vertices and supplies at most \(\binom{r+1}{2}\) different endpoint pairs, with the maximum attained when the whole rank lies in one component. This contradiction is the classical Fano minor. For every chronological continuation of this fixture, shorten first on every later fresh bit. The latest selected added site would contribute its own fresh bit, so shortening gives exactly the seven-site enlarged space. The same obstruction persists.

## A reachable permutation at three changes a named legal triple

Use the ternary seed for \(u\), and take \(b,c\) on their indicated two parents with three fresh bits each. Append a three-output site \(r\) on \(c,q\), whose common witness is \(t\) or \(w\). Append a three-output site \(y\) on \(b,r\), whose common witness is \(q\). The resulting width is 26. A loose bit \(l_c\) at \(c\) and a fresh bit \(l_y\) at \(y\) give a legal triple \(\{p_0,l_c,l_y\}\). The common witnesses for \(p,c\) include \(t,w\), for \(p,y\) there is \(b\), and for \(c,y\) there is \(r\). Neither of the only two neighbors \(b,r\) of \(y\) meets both \(p,c\).

In this same reachable presentation exchange \(tc\) with \(p_0\) and \(qb\) with \(w_0\), fixing every other name. The seed is the only ternary star, and every ternary bond is a ternary star, so fixing its three bits preserves the entire table through \(K=3\). The permutation sends \(W\) to \(P\mathbin{\triangle}A=\{tp,pb,p_0,wq,wc,w_0\}\). This is a genuine six-bit bond around the two adjacent sites \(p,w\). The displayed legal triple is sent to one containing the already shared bit \(tc\), which is forbidden. Thus three is insufficient even with a reachable rival, a genuine replacement bond, and opposing named verdicts. Four excludes this proposed replacement by the theorem.
