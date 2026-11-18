# When a shared bit can mimic a loose bit in a legal triple

Consider the full finite serial parity presentation. Let \(l\) be a loose bit at \(u\) that belongs to a legal three-parent choice, and \(e=uv\) a shared bit at the same junction. Write \(L(t)\) for the number of loose bits at \(t\), \(d_G(t)\) for its number of ordinary meeting neighbors, and \(a(t)=L(t)+d_G(t)\) for its junction arity. If the transposition of \(e,l\) preserves the full scalar table, the following restrictions hold.

1. If \(v\) has a loose bit, then \(d_G(v)\ge L(u)+2\). In particular \(v\) must have at least three ordinary neighbors, since a site of ordinary degree at most two has a loose bit.
2. The arity of \(v\) is at least four. If it is four, both \(u\) and \(v\) introduced exactly two fresh bits. In this case \(v\) had two parents. If \(v\) also has a loose bit, then \(L(u)=L(v)=1\) and \(d_G(v)=3\).

Write \(o\) for the exterior of the wired graph. A bond is the edge boundary of a nonempty ordinary vertex set \(U\) with both sides connected. The star of a junction is a bond because deleting one ordinary vertex leaves every other vertex connected to \(o\). For distinct bits \(i,j\), \(D(i,j)+1\) is the least size of a bond containing them. [Wired graph and connectivity](inverse.md#two-elementary-source-restrictions)

**The two extra crossings.** Let the other two loose marks be held by \(b,c\). All three holders are distinct and lie in one ordinary bipartition class. The pairs \(u,b\) and \(u,c\) have distinct ordinary witnesses \(p,q\), since one witness for both pairs would neighbor all three parents. Use the paths \(u,p,b,o\) and \(u,q,c,o\), ending in the actual marked loose bits. They have disjoint edge sets. The neighbor \(v\) cannot be \(b\) or \(c\). It may equal \(p\) or \(q\).

Take any loose bit \(z\) at \(v\). A bond through \(l,z\) puts \(u,v\) together away from \(o\). It therefore contains all \(L(u)+L(v)\) loose bits there. Each of the two paths must cross, supplying two more distinct bits. Neither path uses a loose bit of \(u\) or \(v\). If \(v=p\) or \(v=q\), its incident first path edge \(uv\) is simply internal to \(U\). Thus

\[
D(l,z)+1\ \ge\ L(u)+L(v)+2,\qquad
D(e,z)+1\ \le\ a(v)=L(v)+d_G(v).
\]

The upper bound uses the star of \(v\). Equality of the two table entries gives the first restriction.

**Bonds of size three and four.** If \(U\) has two vertices, its connectedness gives one ordinary meeting, and its boundary size is the sum of the two star arities minus two. This is at least four. If \(U\) has at least three vertices, consider its three latest sites in creation order. Together they introduced at least six outputs. At most two of those outputs can have been consumed inside \(U\), since their only possible later holders there are among the same three and the ordinary graph is bipartite and simple. Thus at least four outputs cross. Every three-bit bond is consequently one junction's star. If \(a(v)=3\), choose any \(x\ne e\) at \(v\). Then \(D(e,x)=2\). No single star contains \(l,x\), since \(l\) belongs only to \(u\) and \(e\) is the unique ordinary meeting between \(u,v\). Hence \(D(l,x)>2\).

Suppose \(a(v)=4\). Choose any fresh output \(x\ne e\) of \(v\), whether still loose or subsequently consumed. The star of \(v\) gives \(D(e,x)\le3\). For a transposition to preserve the table there must be a bond of size at most four through \(l,x\). Its ordinary side \(U\) contains \(u\). It cannot be a singleton, since \(x\) is not incident to \(u\). For a two-site cut of size at most four, both sites would have to be ternary. This excludes \(v\). If \(x\) is now shared, its other endpoint is a neighbor of \(v\) different from \(u\), hence on the same bipartition side as \(u\). The two cannot form a connected \(U\).

For \(|U|\ge3\), the preceding four-output bound must be attained exactly. The three latest sites of \(U\) each made exactly two outputs, and every boundary bit is an outward output of one of them. No input from outside can enter \(U\). In particular \(l\) puts \(u\) among those three. Since \(x\) was made by \(v\), it also puts \(v\) among them. This proves the arity-four restriction for either orientation of \(e\). If \(L(v)>0\), the first inequality now gives \(L(u)+L(v)\le2\), proving the stated exact counts.

**Remaining cases.** At arity four the two-output cases above remain possible under these bounds. At arity five or six the degree inequality still applies when \(v\) has a loose distinction. Without a loose bit at \(v\), take another meeting \(x=vw\). Every bond through \(l,x\) separates either \(\{u,v\}\) from \(\{o,w\}\) or \(\{u,w\}\) from \(\{o,v\}\). If the two edge-cut minima in the wired graph between these prescribed sets both exceed \(a(v)\), the star bound on \(D(e,x)\) rules out the transposition. This last test is sufficient for exclusion. The bounds do not decide the remaining transpositions or arbitrary scalar isometries.
