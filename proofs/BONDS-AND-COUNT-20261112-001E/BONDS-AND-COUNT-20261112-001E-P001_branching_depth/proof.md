# One branching pattern reads depth through its least bonds

**Theorem.** In the genuine limit-only family specified below, let \(L(s)\) be the minimum size of a bond containing any top port and any own distinction of the copy at depth \(s\) on the first recursive branch. Allow every finite support in the entire infinite pattern, including distinctions on other branches and beyond depth \(s\). For every \(s\ge1\),

\[
\lceil s/3\rceil+1 \;\le\; L(s) \;\le\; \lceil s/2\rceil+2 .
\]

In particular the least bond size is of order \(s\). The target is an own distinction on the specified first recursive branch. This is an all-depth result for one branching family. It does not say how frequently this happens, turn this pattern into a binary counter, or settle the finite-flip sources at an infinite solution.

## Family and prior work

The family is line 11064 of the accepted LIMIT-ONLY sample 5. Each call \(D(a,b,c)\) introduces fresh local distinctions \(x,y\), imposes \(\mathrm{NAE}(y,a,c)\), and makes the three calls \(D(c,a,x),D(x,c,a),D(y,x,b)\). The first is the chosen branch. Every port triple has an infinite extension. Within a copy take \(y=1-a\), choose \(x\) freely, and apply the same rule to its child copies. Distinct child copies share only their supplied port variables. The usual limit agrees with this semantics since no call passes through all three original ports. Leaves A and its accepted NEST-COUNT dependency establish those conventions and the finite-family death at depth four. [Exact depth-two example](../../../experiments/BONDS-AND-COUNT-20261112-001A/BONDS-AND-COUNT-20261112-001A-E001_side_branches/AGGREGATE_FINDINGS.md)

The classical formulation measures the least cardinality of a finite minimal non-shattered set in the admissible two-colourings of this fixed infinite recursively presented three-uniform hypergraph. The finite-state theorem about its ends quantifies fixed top windows. The earlier depth calculation restricts support to its ray. Neither supplies the quantified lower bound here. The general ingredients, Boolean relation composition and projection of a chain of constraints, are elementary. Field-level novelty has not been assessed.

## Lower bound for all side branches

Group the first-branch copies by their depth \(i=0,1,\ldots\). Group \(i\) consists of its own local constraint and its two complete off-branch child subtrees, stopping at the ports of its first child. These groups exhaust every individual copy. Give a newly introduced distinction to its unique group of introduction, and give the three top ports to group zero. This assignment also applies when that variable occurs again much farther down. The incoming and outgoing port triples are the only interfaces between adjacent groups. Any name used on opposite sides must be passed through the corresponding triples, since later calls only receive ports and introduce fresh locals.

Fix any finite candidate support and any values prescribed on it. Apply the prescription once per variable at its introduction group. For each group consider the relation it allows between its two interface triples subject to those prescriptions. Its witnesses, including all off-branch subtrees, can be chosen independently of other groups once these triples agree. The three entries of a given port triple are distinct in this family. If the group owns no selected variable the relation is exactly
\[
T:\quad (a,b,c)\longmapsto(c,a,x)\qquad(x=0\text{ or }1).
\]
Indeed \(y\) can satisfy the local rule and all three child-port triples extend. A variable previously observed and still used in such a group remains carried in the triples. Repeated composition therefore accounts for that identity, even when there is no fresh observation in the group.

The third power of \(T\) is the full relation on two triples. Starting with \((a,b,c)\), the three outgoing triples in order are \((c,a,u),(u,c,v),(v,u,w)\), with \(u,v,w\) arbitrary. After these three groups no original variable still occurs at the far interface.

Suppose a candidate bond has three consecutive empty groups strictly between its top endpoint and its endpoint at depth \(s\). The selected variables before the interval and those after it are both nonempty proper subsets. Each subset would be free by minimality. Take any assignments on the two subsets and an infinite realizing state for each separately. Keep the first state through the left boundary and the second from the right boundary onward. Full \(T^3\) connects their boundary triples. Realize the connecting three groups, including their off-branch subtrees, with their exact relation. All observations on both sides now hold in one state. This proves the entire support free, contradicting binding.

Groups 0 and \(s\) contain the required endpoints. The difference between consecutive occupied group indices from 0 to \(s\) is at most three. Hence at least \(1+\lceil s/3\rceil\) occupied groups are needed and each owns at least one distinct selected variable. Additional selected variables past depth \(s\) already belong to the right-hand part in the gluing argument. They cannot defeat the bound.

## An explicit bond at every depth

Write \(q_{-1}=c\) for the top port and \(q_i=x_i\) for the first-branch own distinction at depth \(i\). For \(i=1,\ldots,s\), the \(i\)-th local constraint is exactly \(\mathrm{NAE}(q_{i-2},q_{i-1},y_i)\). Consider the support
\[
W_s=\{c,y_1,\ldots,y_s,x_{s-1}\}.
\]
It contains the top port \(c\) and the depth-\(s\) own distinction \(y_s\). Its size is \(s+2\). To evaluate its projection, eliminate the internal \(q\)'s of the displayed chain. Every legal assignment of this chain extends to the whole pattern. The root constraint is satisfied by a free choice of \(y_0\), deeper first-branch calls extend from every triple and each off-branch child extends independently for the fixed values of its ports.

For completeness the exact chain relation excludes precisely two complementary assignments. One NAE triple excludes only the two constant words. Inductively leave its last \(q\) visible. If the other bits at this stage fail to match either complementary forbidden prefix, both values of the last \(q\) are available and the next NAE can always be met. Otherwise, for each of the two forbidden prefixes, exactly one value of \(q\) is allowed. The next NAE fails only if the new two bits both equal that forced value. These give two forbidden extended words, one for each prefix, still complementary. There are at least two prefix bits throughout, so the prefixes are distinct. Every deletion of one bit makes the remaining relation full, since the two forbidden words differ in all the retained coordinates. The relation is also nonempty. Thus \(W_s\) satisfies K1, K2 and K3 and bounds \(L(s)\) from above. Changing the last-bit position in the written tuple only permutes the relation.

## Shorter all-depth construction using side branches

Keep \(q_{-1}=c\), and also put \(q_{-2}=a,q_{-3}=b\). The ports at ray site \(i\) are \((q_{i-2},q_{i-3},q_{i-1})\). Its second child has ports \((q_i,q_{i-1},q_{i-2})\), and therefore supplies \(\mathrm{NAE}(z_i,q_i,q_{i-2})\), where \(z_i\) is that child’s own \(y\). The third child at site \(s\) has ports \((y_s,q_s,q_{s-3})\), giving \(\mathrm{NAE}(w_s,y_s,q_{s-3})\). Thus a selected \(z_i\) connects \(q_{i-2}\) to \(q_i\), and \(w_s\) completes the connection to the target \(y_s\).

- For even \(s\ge2\), start at \(q_{-1}=c\), use the second-child relations for \(i=1,3,\ldots,s-3\), and finish with the terminal relation. At \(s=2\) the terminal relation alone suffices.
- For odd \(s\ge3\), use the local relation at site one from \(c\) to \(q_0\) with \(y_1\), then the second-child relations at \(i=2,4,\ldots,s-3\), then the terminal relation. At \(s=1\) use the local relation at site one.

Observe the two endpoints and one witness per displayed relation. The chosen relations form a chain of \(\lceil s/2\rceil\) triples. Its projection is exactly the two-exclusion relation established above. To verify extension, fix the chosen internal chain values. The terminal ray relation uses \(q_{s-2}\) and \(q_{s-1}\), which are unselected and lie beyond every chain carrier (the last is \(q_{s-3}\)); choose them to satisfy that relation for the prescribed \(y_s\). Every other unselected ray \(y_i\) can now satisfy its local relation independently, since these values do not pass down the first recursive branch. Fill the remaining calls from their TOP port relation; siblings share only the port values already assigned. For \(s=1\) this is the direct local triple, whose port values always extend. This proves the stronger upper bound. The terminal witness \(w_s\) belongs to a side child at depth \(s+1\); unrestricted supports in the theorem allow this.

The choice of target branch is essential. If, instead, the observer may pick the target copy at depth \(s\) anywhere in the tree, alternating the second and first child can keep the top port \(a\) successively in the third and first port slots indefinitely. At every such copy its local NAE triple has this same top variable and its fresh \(y\). That triple is a bond: all port triples extend and its local bit has exactly the NAE restriction. The minimum in this different endpoint convention is therefore at most three at every depth.

## Scope of the conclusion

At depth two the exact comparison gives four when supports are restricted to the ray through that depth and three when a side copy is admitted. The factor-three lower bound holds at every depth even for the latter unrestricted minimum. The proof leaves the exact \(L(s)\) sequence and its slope open. The distinction that changes over the proof is nesting depth; it is supplied by this recursive presentation. The pattern's allowed states yield the bounds on bond size.

## Checks

Run `python3 -B proofs/BONDS-AND-COUNT-20261112-001E/BONDS-AND-COUNT-20261112-001E-P001_branching_depth/check.py` from the repository root. Direct enumeration checks all 64 pairs of three-bit interfaces, the two-step negative control, a side-child observation on either side of three empty groups, the exact chain tables through depth eight, and the counting bound on every occupancy pattern through depth twelve. The canonical knotlab CLI checks the exact chain relations at depths one, two and five. An additional scalar enumeration instantiates the whole mixed child selection through depth six in the original definition and compares its projected table with the proposed chain. The all-depth lower bound is the gluing argument.

Independent hand review checked the three-level interface separation including observations beyond the target, supplied the shorter second-child construction, and identified the counterexample for a freely chosen target copy.
