# Fixed parent supports with arbitrarily many fresh counts

**Gate 1, referee pending.** Fix \(m\ge2\). The same two parent supports, with \(m\) loose distinctions each, admit \(m\) different fresh counts in funded, continuing histories. Every exact bond-size reading on the union of those supports is fixed within each knot law. One shared-parent step, with witnesses and loose counts, distinguishes the cases. The construction extends the earlier two-outcome demand comparison. [Seven-knot parity comparison](../BOND-CLOSURE-20261120-001/bond_radius.md) · [Genuine not-all-equal bonds on that source](../BOND-CLOSURE-20261120-001/scaffolds.md#the-continuing-demand-obstruction-also-holds-under-not-all-equal)

## Construction and full range

Use ordinary knots \(U,V,S,A,Z\) and \(q=m-1\) pairs \(W_i,B_i\). The ordinary meetings are \(US,VS,SA,AZ\) and the three meetings along each route \(S,W_i,B_i,A\). Each meeting has \(M\) parallel shared distinctions. Give \(U,V\) exactly \(m\) loose distinctions each and \(Z\) at least \(h\ge2\) permanent loose distinctions. Each \(W_i\) has a fixed set of \(m\) further loose names. In the arm with \(t\) live leaves for \(S\), put \(t-2\) of these sets at their respective \(W_i\), and the others at \(Z\). Use every \(t=2,\ldots,m+1\). The literal supports and loose identities of \(U,V\) never change. A fixed loose input at each can supply the marked pair birth \(P\), since all loose slots at a holder are interchangeable. The total number of loose distinctions is \(T=(q+2)m+h\), and the total width is \((4+3q)M+T\), independent of \(t\).

Every live pair in the \(t\)-member set has the unique witness \(S\), which also holds the entire set. The live knot \(Z\) has no witness in common with any of these live leaves. Every first group in the set is a pair, and each participant owes \(t-1\le m\) distinctions. Each remaining loose distinction makes a unary birth. At the next end, the births from this part are adjacent exactly when their parent sets intersect.

For \(P=\{U,V\}\), the unheld groups are exactly the triples of births with parent sets \(UV,UW_i,VW_i\) for live \(W_i\). In a pairwise-intersecting family through \(UV\), a unary parent set makes the family held. If there is no common parent, there must be one pair \(UW_i\) and one \(VW_j\). Their intersection forces \(i=j\), and no fourth distinct pair intersects all three. Thus these are maximal unheld triples. Each uses up the two candidate pairs from \(P\) to its companions. The remaining groups through \(P\) are its pairs with the \(m-t+1\) unary births of \(U\) and the same number from \(V\). Its demand and fresh count are therefore

\[
D(P)=(t-2)+2(m-t+1)=2m-t,\qquad f(P)=\max(1,D(P))=2m-t .
\]

The two end components have disjoint parents and remain separate. Each nonempty component makes a birth in a funded round. This precludes the sole implied parity birth and gives both components fresh distinctions. Those counts fund the next round. Induction gives continuation in all arms. For not-all-equal, assigning a mixed word on every ordinary meeting makes all source loose values free, including constant inputs to any proposed birth. The proposal keeps its fresh distinction for the keep clause. The inherited non-implication result covers its later funded steps. [Full-end operator](../ORDINARY-DYNAMICS-20261120-001/end_operator.md) · [Not-all-equal growth theorem](../NAE-GROWTH-20261119-001/nae_growth.md)

The family realizes all counts \(m-1,\ldots,2m-2\). This is the entire feasible interval at a funded identified first step with equal parent counts \(m\). Its unique witness block has \(2\le t\le m+1\) by funding and the all-pairs first roster, and the identified formula gives \(2m-t\). Even with the marked parents' entire bond deck, a fixed-length sufficient code therefore needs at least \(\lceil\log_2m\rceil\) bits on this display. Sending which witness size occurred attains that bound for the interval. [Identified fresh-count formula](../ORDINARY-DYNAMICS-20261120-001/end_operator.md#where-the-finite-radius-rule-holds)

## The two exact bond decks

For parity, wire loose distinctions to the auxiliary exterior. Deleting \(S\) leaves \(U,V\) separately wired to the exterior and a connected remainder at \(A,Z\). Deleting \(A\) leaves \(Z\) wired and the rest attached to \(U,V\) through \(S\). Deleting \(W_i\) or \(B_i\) leaves its remaining route holder attached to \(A\) or \(S\). Deleting an ordinary leaf leaves the rest connected with other loose distinctions. Thus every literal star is a connected-shore bond and its full projection is even parity. The funding, unique pair witness, initial binary groups and loose-total conditions verify the identified class.

Choose \(M>T\). A parity cut crosses each shared bundle in full or misses it, and a cut that crosses no ordinary meeting is the whole loose set. In the parent supports write \(B_U,B_V\) for their respective shared bundles and \(L_U,L_V\) for their loose sets. Each nonempty query specifies only which of these four classes it touches. The exact minimum \(b\) is as follows.

| Marked shared classes | Marked loose classes | Parity \(b\) |
|---|---|---:|
| None | Any nonempty choice | \(T\) |
| \(B_U\) only | None, or \(L_U\) only | \(M+m\) |
| \(B_U\) only | \(L_V\) only | \(M+T-m\) |
| \(B_U\) only | Both | \(\infty\) |
| Both bundles | None | \(2M+T-2m\) |
| Both bundles | At least one | \(\infty\) |

Exchange \(U,V\) for the rows with \(B_V\) alone. A connected shore away from the exterior that contains \(U\) and excludes \(S\) must be \(\{U\}\), since \(U\) has only the neighbor \(S\). Crossing \(B_U\) and taking loose from \(V\) instead puts \(S,V\) on that shore and \(U\) outside. Taking every ordinary knot except \(U\) attains the bound. To cross both bundles, a connected shore must contain \(S\) and omit both parents. Taking all other knots attains the last finite bound. In the finite cases, an additional bundle costs more than every loose distinction combined. These facts give the minima and all of the impossibilities in the table.

For not-all-equal, an incompletely pinned ordinary bundle can always be completed mixed, satisfying both holders. At a still-unsatisfied knot all shared values were pinned, so choose an unpinned loose value to differ if one exists. A partial assignment fails exactly when it pins a whole star monochromatically. Every \(U,V,Z\) support has a private loose name and every other knot meets at least two different neighbors. The stars are incomparable, so pinning a nonconstant word on any one of them extends. They are exactly the primitive nonfull projections. Only \(U,V,S\) supply bonds that meet either marked parent support.

| Query on the two complete parent supports | Not-all-equal \(b\) |
|---|---:|
| Contained in one parent's support | \(M+m\) |
| Meets both supports using shared names only | \((q+3)M\) |
| Meets both supports and includes any loose name | \(\infty\) |

Every pair reading is \(b-1\), so the two marked loose inputs have exact cross-root bond distance \(T-1\) under parity and \(\infty\) under not-all-equal in every arm. For a prescribed finite bond radius \(R\), choose \(h\) with \(T>R+1\) and \(M>T\). The least parity bond has size \(T\) and every not-all-equal bond has size at least \(M+2\). All radius-\(R\) bond balls centred at any supplied name are singletons. The comparison concerns the parent deck and its bounded balls. The complete unmarked global bond table supplies a different observation.

In the shared-parent reading, radius one at \(U\) shows the whole \(t\)-member live set and its witness \(S\). Ordinary holder radius two reaches every \(W_i\), whose loose count determines whether it participates. At ordinary radius one around \(U,V\), the displayed holders \(U,V,S\) and their loose counts agree. Across the two marked parents themselves, the ordinary holder and distinction readings are two and three steps respectively.

## The two-open displacement control

Use \(m=2\), \(M=9\) and two permanent openings at \(Z\). Send the extra pair of loose distinctions to \(W\), \(Z\) or \(B\), or erase that pair. Both knot laws give the same result for the marked birth in each row.

| Location of the extra loose pair | Holder steps from either parent | Distinction steps from either input | Shared-parent end steps | Demand | Fresh | Total arity |
|---|---:|---:|---:|---:|---:|---:|
| At \(W\) | 2 | 3 | 1 | 1 | 1 | 3 |
| At \(Z\) | 3 | 4 | \(\infty\) | 2 | 2 | 4 |
| At \(B\) | 3 | 4 | \(\infty\) | 2 | 2 | 4 |
| Erased | — | — | — | 2 | 2 | 4 |

With the loose pair at \(B\), \(A\) witnesses the new binary group \(BZ\) in the other component. Both holders have two openings, each owes one, and each has one unary completion. Their pair birth has demand and fresh count two, hence arity four. Moving the packet to \(B\) or \(Z\) preserves the two parent decks and total width. The exact bond distance from a proposed input to a packet distinction is seven under parity and \(\infty\) under not-all-equal at all three locations. Erasing the packet changes the parity deck through \(T=6\) in place of eight. The not-all-equal parent deck still agrees. With \(U,V\) each having only \(S\) as ordinary neighbor, every holder at ordinary holder distance two from either also meets \(S\). Such a holder enters the common witness set whenever it is live. \(B\) and \(Z\) are matched at distance three.

## Replay

The checker exhausts all 14 constructed sources for \(m=2,\ldots,5\) and every \(t\), using \(R=32\) with \(T=34,M=35\), and the four displacement controls. It enumerates connected parity cuts and all 15 nonempty parent query classes per source under each law. The four classes account for every actual subset of the supplied names. For seven separate small sources with twofold meetings, it independently enumerates literal not-all-equal projections. Pinned SAT queries check all 55 local stars and bonds and 304 maximal proper subsets summed across the sources. The end replay grades all successor groups through the marked pair under each knot law. The demand and both parent decks pass a relabeling. An underfunded source fails both funded-update checks, and a smaller support contained inside a written source star fails the lawfulness controls. The source families have no prevalence weighting.

~~~sh
.venv/bin/python -B experiments/FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders/scaffolds.py
~~~

[Checker](../../experiments/FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders/scaffolds.py) · [Machine receipt](../../artifacts/FRESH-DEMAND-20261120-001A/FRESH-DEMAND-20261120-001A-E001_orders/scaffolds.json)
