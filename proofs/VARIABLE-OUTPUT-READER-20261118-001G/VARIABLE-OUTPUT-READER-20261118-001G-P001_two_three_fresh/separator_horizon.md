# The scalar separator test needs only small entries

**Lemma.** Let \(L\) be five or six and suppose every ordinary junction in a reachable presentation has at most \(L\) distinctions. For a distinguished bit \(t\), the entire ordinary partition after deleting \(t\) is determined by the pair minima through \(K=L\), where \(K=D+1\). Each larger minimum can be replaced by the same “larger” symbol.

For distinct \(x,y\ne t\), draw a link only if \(K(x,y)\le L\) and
\[
              K(x,y)-2\ne (K(x,t)-2)+(K(t,y)-2).
\]
If either entry on the right exceeds \(L\), the inequality holds because the other entry is at least three. Otherwise all three entries are known. The components of this shorter list of links are the claimed parts.

Here is the reduction to the published [all-size separator proof](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/separator.md). Bits on opposite sides of a genuine separation satisfy equality by the one-distinction attachment law, so the new list never links those sides. It remains to prove that all surviving bits of any one ordinary site lie in the same component of the shorter list. This is the step where restricting a general connectivity test could have removed essential links.

Write \(w(x)=K(x,t)-2\) in the proof, giving each leg its true value. On a single site of degree \(d\), every pair \(x,y\) has \(K(x,y)\le d\le L\). If two such bits are in different components, their absent link thus implies
\[
                  w(x)+w(y)=K(x,y)-2\le d-2.
\]
This is exactly inequality (1) in the cited proof. The star-degree argument uses only that inequality and the physical classification of cuts of size three and four. It puts the bits of every site of size at most four in one component and does the same for every site containing \(t\). Any remaining site with bits in different components has degree five or six and three parents. Its exceptional bit \(x\) meets a trivalent endpoint of \(t\). All other bits \(y\) of that site lie in a common component and satisfy \(K(t,y)\le4\) at a five-place site or \(K(t,y)\le5\) at a six-place site.

The original argument also needs the exceptional bit to lie outside a shortest bond through \(t,y\). For exactly these \(y\), such a bond has size at most five. For every other \(z\ne t,y\) in it, \(K(y,z)\le K(t,y)\le L\), and \(K(y,z)-2\le w(y)<w(y)+w(z)\). The retained list therefore links \(y,z\). The exceptional bit, which is in a different component, cannot belong to that bond. The rest of the original proof excludes the two possible orientations of the exceptional bit by counting crossings of that short bond and following ordinary four-cycles through sites that each already lie in a single component. It requires no comparison at a larger minimum. This proves that each site belongs to one component. Ordinary incidence paths avoiding \(t\) stay in that component, proving the claimed partition. [Mixed-site cases and both orientations](../../VARIABLE-OUTPUT-READER-20261118-001D/VARIABLE-OUTPUT-READER-20261118-001D-P001_separator_inverse/separator.md#the-only-local-form-a-false-separation-could-take)

**Application.** In comparing a source of maximum arity four with any reachable rival, \(L=6\) bounds both maximum arities. In the [incidence proof](extension.md) the small equations use \(K\le4\), the disputed boundary of a putative missing four-place site uses just the separator partition, and the final five- and six-place exclusions distinguish \(K\le5\) from \(K\ge6\), or \(K\le6\) from \(K\ge7\). Thus entries through six force the entire incidence. The width-26 paired histories in the [six-place control](six_check.json) have opposite three-parent verdicts while every entry through five agrees. The horizon of six is sharp for the unrestricted number of additions in this source class, and already for exactly three three-fresh additions. In distance units the sharp horizon is \(D=5\).

For exactly two three-fresh additions, an equal-rank rival must already have the same equations, and hence the same entire table. A strict rival can only have one greater rank, exclusively two-fresh additions and maximum arity five. Apply the separator lemma with \(L=5\) in both presentations and then the five-place exclusion. Thus the horizon of five in that case follows from the symbolic argument alone. The [independent finite-state proof and lower-bound controls](cutoff.md) give the same sharp bound by a different route.

The [separation control](checks.json) compares all 66 single-distinction deletions on two reachable inputs of widths 32 and 34 whose maximum arity is five. Reading through \(K=5\) gives every physical partition. Lowering the cutoff to three or four fails on every deletion in these two inputs.
