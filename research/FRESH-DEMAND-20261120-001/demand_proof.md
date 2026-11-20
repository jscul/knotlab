# What determines the number of fresh distinctions at a funded birth?

Fix a finite, connected physical presentation, the knot law, and a particular birth in a legal, funded complete round. Supply its marked parents, all the distinctions they hold, and which of those are loose. The number of fresh distinctions is determined by how the other children of these parents meet. Parity has one additional possibility when every parent holds exactly one loose distinction. The two laws agree whenever the raw demand is positive. The result applies both to lawful starts and to stages they reach. The lower bounds with complete bond readings are attained on lawful starts. A separate comparison fixes the physical parent holdings at positive age. [Frozen question](preregistration.md) · [Complete-round operator](../ORDINARY-DYNAMICS-20261120-001/end_operator.md)

## A calculation from incidence at every arity

Let \(P\) be the set of parents of the specified birth, \(p=|P|\), and \(h(u)\) the loose count at \(u\). Define

\[
 H=\sum_{u\in P}(h(u)-1),\qquad a_p=\max(1,3-p).
\]

The current witnessed groups determine the funded births, with a separate unary birth for each unused loose slot. In the lists of births at the parents in \(P\), strike the specified birth from each list. There are \(H\) remaining **occurrences**. Identify occurrences belonging to the same actual birth. Call the resulting set of siblings \(S\). For \(s\in S\), let \(I_s\subseteq P\) be the parents whose lists contain it. Thus \(I_s\ne\varnothing\) and \(\sum_s |I_s|=H\). Repeated unary births at a parent remain distinct.

Join siblings \(s,t\) in an auxiliary graph if their full parent sets overlap. This requires an outside test only when \(I_s\) and \(I_t\) are disjoint. Even then one needs only the existence of a common outside parent. Form the inclusion-maximal pairwise adjacent sets \(Q\subseteq S\) of size at least two for which \(\bigcap_{s\in Q}I_s=\varnothing\). Write \(\mathcal Q\) for these sets and \(U=\bigcup_{Q\in\mathcal Q}Q\). The structural answer is

\[
 D=|\mathcal Q|+|S\setminus U|
   =H-\sum_{s\in S}(|I_s|-1)-|U|+|\mathcal Q|. \tag{1}
\]

Indeed, a group of at least three through the specified birth can use only its siblings. Its members are pairwise candidates precisely when those siblings are pairwise adjacent. A parent holds the entire proposed group precisely when it belongs to every one of the traces \(I_s\). An empty intersection stays empty when a member is added, so maximality can be checked entirely inside \(S\). Each uncovered sibling supplies exactly one remaining pair. This proves (1) from witnessed incidence without being given the next groups. Two siblings with the same parent in \(P\) may still belong to a larger unheld group. A count of siblings alone would also miss the effect of one sibling appearing in several parent lists.

The output under not-all-equal is \(\max(a_p,D)\). Under parity the same formula applies except that the sole birth receives zero. Indeed the only nonempty parity equation supported entirely on current loose distinctions is their complete set. A sum of old knot equations with no shared distinction in its boundary includes both holders of every shared distinction or neither, and the ordinary presentation is connected. On a funded round all loose slots are consumed. Thus the specified input parity is already implied exactly when the specified birth is the only birth. Under not-all-equal the old distinction taken from each parent can have the same value in a permitted old state, so the keep clause still applies. [Fewest-count rule](../FRESH-COUNT-20261118-001/fresh_count.md) · [Not-all-equal implication proof](../NAE-GROWTH-20261119-001/nae_growth.md)

This gives the **coarsest partition of possible completions for the fixed display**. When \(H>0\), some sibling exists. It either belongs to a group counted in \(\mathcal Q\) or supplies a pair, so \(D>0\) and no closure flag is needed. All realizable values \(D\le a_p\) form one class, and each distinct realizable \(D>a_p\) forms its own class. When \(H=0\), there is no sibling and \(D=0\). Not-all-equal always gives \(a_p\). Parity gives zero if there is no birth elsewhere and \(a_p\) otherwise. Retain this one bit only when both alternatives are realizable on the given display. Equivalence now follows in both directions from the output formula. The lists and overlap tests above are a way to compute the equivalence class. Individual entries in those lists may contain more information than that class.

The partition simplifies further on actual fixed displays. For a unary, all siblings have the sole parent in their trace, so \(D=h(u)-1\), with a floor of two. A lawful connected parity source cannot have exactly one loose distinction, since its value would be fixed on a proper part of its holder. A nonclosing step has at least two births with fresh distinctions. Thus a closing unary never actually arises on this domain, and **a unary needs no outside information**. For every \(p\ge2\) with \(H>0\) the demand is already at least its floor of one. **Two completions of this display agree exactly when they have the same integer (1).** On a fixed display the floor can never identify distinct realizable positive demands. When \(p\ge2\) and \(H=0\) only the possible parity exhaustion bit remains. One may obtain this bit from an exact proposal reading on the loose inputs. Funding and legality are still required hypotheses. [Exact input test and small-arity conventions](../BOND-CLOSURE-20261120-001/criterion.md)

No fixed finite display supports an unbounded range. There are at most \(H\) siblings. Every group counted in (1) corresponds to a different nonempty subset of them, giving \(D\le 2^H-1\) for \(H>0\). If \(W\) is the sum of the physical widths of the marked parents, \(H\le W-p\). Information bounds below concern the length of a fixed-length message reporting the computed class, equivalently the worst-case number of unrestricted binary questions. They do not bound the number of queries available to a particular ruler. No probability weighting is needed.

## The class with an identified map

For a multipart birth in the proved identification class, choose any two parents \(u,v\). Their common witness has a block of \(t\) current live knots. On positive layers this is its full child roster. The established identity is

\[
 D=h(u)+h(v)-t.
\]

At a qualifying source the only multipart births are pairs. Each other member of the common block replaces two prospective pairs through the birth by one ternary. At positive age, after lifting the two parents, the boundary exposed by their joint extension has the sum of their individual boundaries minus that of their common predecessor. The identity also covers the finite-piece and relay cases. Thus, with the parent holdings fixed and \(H>0\), the exact outside datum is \(t\) itself on its realizable range. Its distinct values give distinct positive demands. A witnessed end step discloses \(t\). A numerical step distance of one only discloses adjacency. Since \(t\ge2\), \(D\le H\) at every multipart birth in this class. [Complete identified formula and hypotheses](../ORDINARY-DYNAMICS-20261120-001/end_operator.md) · [Identification with repeated meetings](../DOUBLE-IDENT-20261119-001/double_ident.md)

### Arbitrarily many answers with the same complete parent readings

Fix \(m\ge1\), put \(h=m+1\), and take the ordinary meetings

\[
 US,\ VS,\ SA,\ AZ,\quad SW_i,\ W_iB_i,\ B_iA\quad(1\le i\le m).
\]

Replace every meeting by \(M\) distinct shared distinctions. The marked \(U,V\) each hold \(h\) loose distinctions. In arm \(k\), \(0\le k\le m\), give the first \(k\) holders \(W_i\) exactly \(h\) loose distinctions apiece and the remaining \(W_i\) none. Give \(Z\) exactly \(2+(m-k)h\) loose distinctions. The other holders are spent. Take \(M>T\), where \(T=(m+2)h+2\) is the total loose count. The variable loose distinctions can retain their names when transferred. Both marked parent stars remain literally identical.

All physical parity stars are bonds. Deleting \(S\) leaves \(U,V\) connected to the auxiliary exterior by their own opens, and every \(W_i\) can reach \(Z\) through \(B_i,A\). Deleting \(A\) leaves \(Z\) wired by its own opens and every other ordinary holder attached to \(S\). Deleting \(B_i,W_i,U,V\), or \(Z\) leaves all remaining holders able to reach a remaining loose distinction. All stars have at least three distinctions. Under not-all-equal, every partially specified ordinary bundle can be made mixed whenever it is missing an assignment. These completions are independent across bundles. Every remaining incomplete star has only private loose variables left to assign and can be satisfied independently. Consequently a partial assignment extends exactly when it contains no fully specified monochromatic star. The stars are incomparable under inclusion, and each can be the whole minimal obstruction. Hence the only minimally constrained supports under this law are the declared physical stars. This proves lawfulness and identifies the actual not-all-equal bonds.

The live \(U,V,W_1,\ldots,W_k\) form one common block held at \(S\). Every pair in it has only that witness, and there are no unheld triples. Each member owes \(k+1\le h\) slots. \(Z\) is isolated in the growing end. This verifies the identification hypotheses, including funding, with at least two loose distinctions. Both end components produce children and stay apart because children are adjacent only through a shared parent. With at least two components a sole closing birth is impossible, and the output rule funds the following round. Thus both laws can continue indefinitely in every arm.

The common birth \(P=\{U,V\}\) receives \(2h-(k+2)=2m-k\) distinctions. Equivalently, the \(k\) other members of its block each replace two sibling pairs by one ternary, with the remaining sibling pairs unchanged. The \(m+1\) different answers at **one fixed display** require \(\lceil\log_2(m+1)\rceil\) bits. Together with the preceding upper bound, the worst-case bit requirement in the identified class grows as \(\Theta(\log(H+1))\) for growing \(H\), already at two parents.

The same comparison survives supplying the least common bond size on **every nonempty subset of the two whole marked stars**. Let \(B_U,B_V\) be their ordinary bundles and \(L_U,L_V\) their loose sets. Under parity, specifying any member of one of these four classes requires its whole class to cross. The following are all possibilities, up to exchanging the marks at \(U,V\).

| Required ordinary bundles | Required loose sets | Least bond size |
|---|---|---:|
| None | Any nonempty selection | \(T\) |
| \(B_U\) | None, or \(L_U\) only | \(M+h\) |
| \(B_U\) | \(L_V\) only | \(M+T-h\) |
| \(B_U\) | Both | No bond |
| Both | None | \(2M+T-2h\) |
| Both | At least one | No bond |

A parity bond is a cut with both sides connected after wiring loose distinctions to the exterior. The only nonempty cut avoiding ordinary bundles cuts exactly all \(T\) loose distinctions. With a required \(B_U\), the shore away from the exterior either isolates \(U\), or, at cost less than a second bundle, contains all ordinary holders except \(U\). Including both loose sets requires both leaves inside and hence \(S\) inside, preventing either leaf bundle from crossing. When both bundles cross, put all ordinary holders except \(U,V\) inside. Its opposite shore is connected through the leaves' opens, and any further ordinary crossing costs more. These arguments give every minimum and absence in the table. The only not-all-equal bonds meeting marks lie at \(U,V,S\). Their complete supports and sizes are identical across arms, so all exact readings under that law agree as well. Under either law the relation projected onto the two marked stars is the product of their two local relations. For parity this follows by removing the marked distinctions, after which \(U,V\) are isolated and the remainder is connected to the exterior at \(Z\). For not-all-equal it follows from the completion proof.

Given any numerical bond-distance radius \(R\), one can also increase the fixed two opens at \(Z\) to a common larger reserve and then choose \(M>T>R+1\). Under parity every nonempty bond has size at least \(T\). Under not-all-equal every physical star has size at least \(M\). The bounded balls then show no other distinction under either law. The exact parent-star comparisons above still agree at this larger \(T\). These are readings on one physical stage. Supplying the complete witnessed roster at \(S\) explicitly gives \(k+2\) and decides the answer. [Earlier seven-knot comparison](../BOND-CLOSURE-20261120-001/bond_radius.md)

### A separate positive-age comparison

The range for physical parent holdings alone is unbounded even if the observer requires a reached layer at positive age. Fix \(h\ge2\). Double every ordinary meeting on the five-knot path \(a,W_a,s,W_b,b\). Give \(s\) exactly \(k\) loose distinctions and \(a,b\) exactly \(h+2-k\) each, for \(2\le k\le h+1\). Both witnesses \(W_a,W_b\) are spent. After deleting any holder every remaining ordinary component reaches a live holder, and the bundle completion argument applies under not-all-equal. The two initial pairs \(U=\{a,s\}, V=\{s,b\}\) are funded and have two-member witness blocks. Each receives \(h\) fresh distinctions. All other births are unary. On this first reached layer the complete stars of \(U,V\) therefore agree literally up to naming their two incoming and \(h\) loose distinctions. A sibling meeting both would either have \(s\) as a parent or take both \(a,b\). No birth took both \(a,b\). Every prospective larger group containing \(U,V\) is consequently held at \(s\), leaving the pair. Its common witness \(s\) has exactly \(k\) children. Its fresh count is \(2h-k\), with \(h\) different values under each law. Even the projection onto the two stars is the product of their local relations. Their four incoming distinctions are a proper subset of the source loose distinctions and are jointly free under parity. Under not-all-equal a mixed value assignment to each source bundle makes any values on those four possible. Every other birth has its own fresh distinctions for completing the extension. The all-order bond-deck comparison above uses the separately specified starts.

## Stronger bound on unrestricted lawful starts

Here is a different construction in which the \(O(H)\) general bit upper bound is sharp in order of growth, even at two marked parents. The loose counts at these parents and the full widths of their stars both grow linearly in \(H\). At each width all physical meetings are fixed across the compared starts. Only the locations of unmarked loose distinctions change. Each comparison refers to a legal event on its first complete round.

### Realizing any set of row–column overlaps

Fix \(n\ge2\) and a zero–one matrix \(B\) of order \(n\). Give the marked parents \(u,v\) exactly \(n+1\) loose distinctions apiece. Give each private holder \(r_i,c_j\) one loose distinction. Supply a holder \(z_{ij}\) for every matrix position, including its zeroes. A one puts two loose distinctions at \(z_{ij}\), a zero puts the same two named distinctions at the common holder \(z_0\). Keep two extra loose distinctions permanently at \(z_0\). The total loose count \(T=2(n+1)+2n+2n^2+2\) is fixed.

Create the following spent holders. Each line specifies exactly its ordinary neighbors at this point. Use two shared distinctions per ordinary meeting.

| Spent holder | Its neighbors |
|---|---|
| \(R_i\), one per row | \(u,v\), and all \(z_{ij}\) in row \(i\) |
| \(C_j\), one per column | \(u,v\), and all \(z_{ij}\) in column \(j\) |
| One private witness per \(i\) | \(u,r_i\) |
| One private witness per \(j\) | \(v,c_j\) |
| One private witness per cell | \(r_i,z_{ij}\) |
| A different private witness per cell | \(c_j,z_{ij}\) |

Extra spent holders specified below ensure physical lawfulness and preserve all exact marked bond readings. None adds a candidate pair among live holders. The complete multipart roster is

\[
 P=\{u,v\},\quad
 X_i=\{u,r_i\}\cup\{z_{ij}:B_{ij}=1\},\quad
 Y_j=\{v,c_j\}\cup\{z_{ij}:B_{ij}=1\}.
\]

To verify it, a pairwise candidate set containing \(r_i\) can use only \(u\) and the live cells of its row. When that row is nonempty, the listed whole set is unheld, since the only witness of \(u,r_i\) misses all cells. When the row is empty the pair remains. The same argument works for each column. A set with no private holder, other than the isolated \(z_0\), uses only \(u,v\) and cells. Pairwise adjacent cells are all in one row or one column. Indeed, two distinct cells in the same row with different columns admit no cell outside that row adjacent to both, and the column argument is the same. The corresponding \(R_i\) or \(C_j\) holds that set, including any \(u,v\) in it. Of its pairs, only \(uv\) escapes coverage by an \(X_i\) or \(Y_j\). This proves the displayed roster and funding. Each one-cell participates twice, each private holder once, and \(u,v\) participate \(n+1\) times each. All \(z_0\) slots make unary births in a separate end component. Both laws continue.

Through the common birth \(P\) the \(n\) row siblings share \(u\) and the \(n\) column siblings share \(v\). A row and column sibling share a parent precisely at a one of \(B\). A set through \(P\) is unheld when it contains at least one sibling of each kind. Its maximal possibilities correspond exactly to the inclusion-maximal all-one rectangles of \(B\) having both a nonempty row set and a nonempty column set. Each row or column with no ones instead contributes a residual pair. In the terminology of the bipartite graph of \(B\), these rectangles are its maximal nonempty bicliques. This is the exact demand from (1) for every matrix.

### Fixed physical parent stars and equal bond data

The following attachments depend on \(n\) but not the matrix entries. Let the *base* consist of all the described old holders except \(u,v\). It includes the reservoir \(z_0\) and every spent witness.

1. Add two spent holders \(L_0,L_1\). For each base holder \(x\) and each \(t=0,1\), join \(x\) to \(L_t\) through its own new spent intermediary, with two distinctions on each meeting. Neither \(u\) nor \(v\) gets such a link. Write \(C\) for the total number of distinctions so far, including all loose ones.
2. Add one spent holder \(K\). For each variable holder \(z\), comprising \(z_0\) and every \(z_{ij}\), join \(z\) to \(K\) through its own new spent intermediary with \(M>C\) parallel distinctions on each of the two meetings. For a prescribed finite radius \(R\) one may take \(M>\max(C,R+1)\).

No new holder meets two live holders. The new ordinary graph stays connected after deletion of any one holder. The routes \(L_0\)–intermediary–\(x\)–intermediary–\(L_1\) have pairwise disjoint interiors across all base holders \(x\). Removing an interior holder of one route leaves its remaining parts connected through the other routes, and deleting a terminal leaves all parts attached to the other terminal. Each of \(u,v\) has at least two distinct ordinary neighbors in this base. Finally \(K\) has separate routes to at least two different variable holders. Deleting one intermediary or its variable holder leaves \(K\) attached through another route. Deleting \(K\) leaves its intermediaries attached to their own variable holders. This proves the assertion. A remaining loose distinction still wires the ordinary graph to the exterior. Thus every parity star is a bond. Every star is at least ternary and has at least two ordinary neighbors. The preceding mixed-bundle completion proves that the only not-all-equal bonds are the physical stars. In either law these are lawful original knots.

The literal marked star at \(u\) has \(3n\) fixed ordinary neighbors, each met twice, and \(n+1\) loose distinctions. Its width is \(7n+1\), the same as at \(v\). The ordinary neighbors directly met by the parents are all spent witnesses whose supports are fixed. Under not-all-equal this already proves equality of all exact bond readings on the parent stars. Even the projected relation on their union contains just the two local requirements. Under parity the projection has just the span of the two local equations, since removing the marked distinctions isolates \(u,v\) and leaves all other holders connected to the exterior.

For parity, a stronger argument is needed to compare the sizes of bonds reaching *outside* those marked supports. Consider a nonempty query on any subset of the two stars. If a bond contains the query, take its two connected sides, with the exterior outside. Retain the sides of the parents and their immediate ordinary neighbors. If an inside parent has no inside ordinary neighbor, it is the entire inside shore. Its own star is a bond of size at most \(C\) that contains the query. Otherwise construct a replacement as follows.

- Put \(L_1\) inside, \(L_0\) outside, and every variable holder, \(K\), and the intermediaries of all \(M\)-fold meetings outside. Assign other base holders outside unless their side has already been retained. No variable holder is an immediate ordinary neighbor of a marked parent.
- Set each intermediary between a base holder \(x\) and \(L_t\) on the side of \(x\). Every base holder reaches its same-side \(L_t\). Each inside parent reaches \(L_1\) through a retained inside neighbor. Each outside parent reaches the exterior through its own loose distinctions. The outside \(L_0\) reaches the exterior through \(z_0\), which has permanent loose distinctions.

Every vertex on each side is now connected to the others there, including the added heavy intermediaries through \(K\) and their variable holders. At least one inside base holder exists unless the singleton case applied. To see this, a required loose distinction needs an inside parent, and a required ordinary distinction needs either an inside parent or an inside ordinary neighbor. In the remaining case any inside parent has an inside neighbor. All queried distinctions still cross. No \(M\)-fold meeting crosses, so the new bond costs at most \(C\). This proves that **every finite marked minimum is below \(M\)**.

Every cut below \(M\) puts all variable holders and their connecting intermediaries on a common side. Their mobile loose distinctions then have the same crossing labels in every arm. Ordinary connectivity on each side is fixed. If the variable holders are outside, the whole variable part reaches the exterior through \(z_0\)'s two permanent opens, regardless of how the mobile ones are distributed. If they are inside, no variable loose distinction can change outside connectivity. Thus a low-cost cut is a bond with the same full support in every arm. Both directions, together with the replacement construction, establish equal exact minima including absences for every marked-star query. For the global table clipped at a prescribed finite radius the same cut argument works directly. Under not-all-equal every physical star whose loose support can change contains an \(M\)-fold meeting. All low-cost bond supports therefore agree globally under that law as well. Untruncated remote queries on the entire physical arrangement are outside this equality.

### Counting distinct outputs at one display

Take a finite partially ordered set on \(n\) elements with neither a greatest nor a least element, and set \(B_{ij}=1\) exactly when \(j\not\le i\). No row or column is isolated, and neither is universal because its diagonal entry is zero. Intersections of sets of neighboring columns, taken over all possible collections of rows including the empty one, are exactly the complements of order ideals. Indeed the missing columns in row \(i\) form the set of elements at most \(i\), and unions of these sets are precisely the ideals.

Every such intersection \(V\) determines a unique largest row set \(A_V\) whose rows contain \(V\). Its common columns are exactly \(V\), because the original rows producing the intersection are included in \(A_V\). This gives one maximal all-one rectangle for each intersection except the full column set (\(A_V\) empty) and the empty column set. Conversely every maximal all-one rectangle arises this way. With \(I\) the number of ideals, the common birth therefore takes exactly \(I-2\) fresh distinctions.

To obtain many different *numbers* of fresh distinctions, take \(m\ge2\) and \(j=\lfloor m/2\rfloor\). Starting from the empty order with one ideal, read any length-\(m\) binary string having exactly \(j\) ones. For every digit append one element incomparable to all preceding elements. This doubles the ideal count. For a digit one then append a new greatest element. Exactly one ideal includes that element, adding one to the count. The resulting count is the integer \(N\) with leading digit one followed by the given string. Add one last incomparable element. This gives \(2N\) ideals and ensures neither a greatest nor a least element exists. The number of elements is always \(n=m+j+1\) and \(H=2n\). Thus at precisely the same marked display one obtains \(\binom mj\) distinct fresh counts \(2N-2\). An exact reader needs at least

\[
 \left\lceil\log_2\binom m{\lfloor m/2\rfloor}\right\rceil
 \ \ge\ m-\log_2(m+1)
\]

worst-case bits, since the largest of the \(m+1\) binomial coefficients is at least their average. With \(H=3m+O(1)\), this is \(\Omega(H)\). The first section gives \(O(H)\) in general. These two bounds concern the information needed to distinguish different answers, irrespective of the time required to calculate one. They also scale linearly in the marked physical widths in this construction. The comparisons are made separately with true parity and true not-all-equal readings.

If an exact intermediate value of \(H\) is wanted, add the same number of spare loose distinctions at \(u\) in every arm before choosing \(M\). Each yields a distinct unary sibling through \(u\) that meets no column sibling. Any larger pairwise candidate set containing it and \(P\) is held at \(u\), so their residual pair survives. Each added spare increases every answer by one and preserves the number of different answers. Consecutive constructed values of \(H\) differ by at most four. The marked-cut proof uses the existence of loose distinctions at \(u,v\) and also applies with these extra spares.

A small instance has \(n=4\). If the only strict comparisons are \(1<3\) and \(2<3\), there are ten ideals. If the only strict comparison is \(1<2\), there are twelve. The two common births on the same five loose distinctions at each marked parent receive eight and ten fresh distinctions, respectively. Each physical marked parent has width 29.

The sibling calculation (1) itself needs no two-parent assumption. The strong lower construction also admits a fixed larger arity \(p\). Add \(p-2\) further marked parents, each with one loose distinction, and give each pair of marked parents with at least one new member its own private spent common witness with two distinctions per meeting. Include these witnesses in the base and omit all marked parents from the attachments at \(L_0,L_1\). Every new parent can be a candidate only with other marked parents. The full marked set is a maximal unheld group, and replaces the single residual pair \(uv\). Its new parents have no siblings, so its row and column siblings and their demands do not change. Every marked parent still has at least two distinct base neighbors and its own loose distinction. The preceding lawfulness and marked-cut replacement proofs hold verbatim, with an inside singleton treated as before. This extends the lower bound to each fixed \(p\ge2\); the binary case alone gives the general worst-case lower bound. These unrestricted examples use multiple common witnesses at the source. The logarithmic bound above applies in the identified class.

## Finite cross-checks

For \(m=1,2,3,4\) in the identified family, direct enumeration of the two connected sides of every cut checked all 15 nonempty marked-class selections in every arm. All 210 minima or absences agreed with the table. In the five-knot reached-layer comparison, two literal steps of the archived end operator gave \(h\) on each first-layer parent and \(2h-k\) on their pair in all 70 cases at \(2\le h\le8\), \(2\le k\le h+1\), and both laws. For the unrestricted coding construction, starting with the full column set, repeatedly retain both each existing set and its intersection with the next row. Subtracting two from the final number of distinct sets gave \(2N-2\) for all 146 fixed-weight strings at \(m=2,\ldots,8\). At \(m=8\) the 70 different outputs ranged from 540 to 990. The all-size results above follow from the incidence and counting proofs. [Archived end operator](../../experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py)
