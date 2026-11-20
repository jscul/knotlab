# Exact bond distances between old background distinctions

Write \(e_i\) for the original shared distinction between \(b_i\) and \(b_{i+1}\) on the 17-knot background. At the first completed layer of the singly attached source, loading its five-ring increases the bond distance on **33 of the 120** old path pairs by two. The other 87 agree. In particular \(e_2,e_5\) read 13 quiet and 15 loaded. A different old pair changes in the opposite direction later. The two distinctions immediately beside the attachment at \(b_4\), \(e_3,e_4\), have quiet distance **7 at every age**. Their loaded distance is **7 through age three and 4 at every age from four onward**. Each result compares the same pre-existing physical marks.

The law passes cold groups and vetoes hot multipart groups. The stored state is the five original ring meetings relative to the transported zero. All live groups after the first round are cold. The original arrangement, source openness and numerical law are fixed; in the following proofs the evaluator keeps the original names. A bond distance is one less than the least size of a bond containing both distinct marks. In the wired holder graph, a bond is a cut with two connected shores. The bookkeeping exterior stands for loose distinctions and is never used for an ordinary knot route. [Frozen definitions](definitions.md) · [Parity cut proof](../EDDY-WORLD-20261119-001/bending.md) · [State and growth locality](../STATE-FEEDS-GROWTH-20261119-001/locality.md)

Along any one of these histories, bond distance on retained marks can only decrease or stay fixed. Each birth has a fresh distinction private to its own equation at that layer, so every allowed old assignment extends and every old projection remains exactly the same. In particular a previous minimal nonfree support stays minimal on its own distinctions. Across sibling histories at the same age, either sign occurs. For \(e_2,e_5\) the common source distance is 15. The quiet first round lowers it to 13 and the loaded round leaves it at 15. For \(e_3,e_4\) the fall to 4 happens on the loaded history.

## First layer: remove the young knots exactly

Let \(S\) be the original holders on the shore away from the exterior, \(o_v\) the original open count of \(v\), and \(\delta_0S\) its old shared-distinction boundary, counting multiplicities. Begin with every child outside \(S\). The cut has size

\[
 |\delta_0S|+\sum_{v\in S}o_v .
\]

If a child has \(p\) parents, \(a\) of them in \(S\), and \(f\) fresh distinctions, moving it inside adds \(f+p-2a\). In the named first layers \(p\) is one or two and \(f\ge p\), including after any of the frozen vetoes. A child with one inside parent is a leaf on the inner shore. Moving it back outside preserves connectivity and weakly decreases cost. A child with no inside parent cannot be in that connected shore, which contains an endpoint of each old mark. Consequently the only young knots ever needed are binary children whose two parents are inside. Such a child can join two old components at cost \(f-2\). The outside remains connected: every outside old knot has its children outside, and every outside child has a fresh distinction to the exterior.

For **any two originally shared distinctions** in these arrangements this gives an exact formula. Minimize the displayed old cost over old subsets \(S\) crossed by both marks. Add the minimum sum of binary connection costs needed to connect the components of the old induced \(S\), using only children of two parents in \(S\). If they cannot be connected, that \(S\) is unavailable. A minimum spanning tree on the components gives this sum. Keeping only those children gives a genuine bond on the literal stage, also when zero-cost links are present.

For a surviving child of parents \(p,q\), its ordinary next demand is \(o_p+o_q-2\) minus the number of other parents \(r\) for which both \(pr,qr\) survive. Each such \(r\) replaces two candidate pairs with one unheld triple. These triples all lie in the unique source witness's neighbor block. A veto deletes possible connections and weakly increases the fresh cost of every surviving binary connection. Thus at the first layer *every* originally shared pair has loaded bond distance at least its quiet distance, including ring marks. This ordering does not extend to all later ages. [First-layer demand derivation](../STATE-FEEDS-GROWTH-20261119-001/locality.md)

## First-layer formula for every original path pair

Let \(I=[i+1,j]\) be the old path holders between marks \(e_i,e_j\), with \(i<j\). On an intact source define

\[
C(I)=2+\sum_{v\in I}\bigl(o_v+2\,{\bf1}_{v\text{ is an attachment}}\bigr).
\]

This is the bond **size** before growth. At age one its exact replacement for any subset of fully loaded rings is

\[
 K_1(e_i,e_j)= C(I)-2\,\#\{s:\text{ the ring at }s\text{ is quiet and }s-1,s+1\in I\}.
\]

Subtract one for bond distance. The formula applies to the bare background, the three single attachments and both two-ring placements, including the quiet control for each. The isolated growth factors of the rings do not enter. [Source formula](../EDDY-WORLD-20261119-001/source_bonds.md)

**Eliminating excursions into a ring.** A retained old holder off the path can connect to the path only at \(s-1,s,s+1\), counting the available binary connections as well as the old meetings. If \(s\) is inside, its old meetings already connect every retained member of these three. Removing the other four ring holders cannot increase cost: a proper part of the ring already contributes at least two crossings, and removing a full ring except \(s\) saves more than two open distinctions. If \(s\) is outside, an excursion can at most connect \(s-1\) and \(s+1\). For a quiet ring the direct binary child between them costs two. Removing any used ring holder saves at least this amount, and the old ring boundary can only decrease. At a loaded ring no off-path holder can connect into such a shore. At separation four, the sets \(\{s-1,s,s+1\}\) for the different rings are disjoint. The shared intervening background knot gives no off-path connection between those rings. The removals can therefore be made separately.

The remaining connected shore has a path span \([L,R]\supseteq I\). Every gap is one single omitted holder \(g\), bridged by its surviving binary child on \(g-1,g+1\). No long gap can be bridged. Begin with the whole span inside. Its boundary is \(C([L,R])\) with the initial 2 replaced by \({\bf1}_{L>0}+{\bf1}_{R<16}\). Omitting an internal \(g\) creates two path crossings, saves its old opening contribution, and requires the new connection at cost \(f-2\). Thus the net change is

\[
 f-o_g-2\,{\bf1}_{g\text{ is an attachment}}.
\]

At a quiet attachment \(o_s=4\). Its two path neighbors both have four opens, and its four-member neighbor block gives their child four fresh distinctions. Omitting \(s\) saves two. At a loaded attachment precisely the path pair survives in that block. Its child now has six fresh distinctions, so omission saves zero. Gaps adjacent to a loaded attachment require a vetoed child. At every other surviving path gap the child has at least \(o_g\) fresh: away from attachments \(o_g=2\), and at a neighbor of an attachment its two parents include the four-open attachment and another parent with at least two opens. These facts still hold at the midpoint of the four-step placement, where the two parents of a prospective gap can both have four opens.

All savings available inside \(I\) are realized by omitting the eligible quiet attachment holders at once. They are at least four apart. Enlarging \(I\) to gain any further saving must add an immediate neighbor of the corresponding attachment, a four-open interior holder. These added neighbors are distinct for different new savings. Extending to a physical path end also adds at least two opens for the possible loss of one boundary crossing. No extension of \(I\) improves the stated minimum. This also accounts for shores taking the opposite endpoint of either marked distinction.

The funded cut control removes the meeting \(c_2c_3\) while keeping all opens. Its quiet path formula is identical. If \(s\) is inside, removing the whole of either off-path arm increases its old crossings by at most one and saves at least two opens on any removed holder. If \(s\) is outside, any used off-path connection still passes through \(c_1\) or \(c_4\), either of which pays for the direct two-cost connection. The background binary connections and their fresh counts are unchanged because the original neighbor block of \(s\) is unchanged.

| Loading change against quiet | Pairs with unchanged distance | Increase of 2 | Increase of 4 |
| --- | ---: | ---: | ---: |
| Single ring at \(b_4\) | 87 | 33 | 0 |
| Both rings, \(b_4,b_8\) | 59 | 40 | 21 |
| Both rings, \(b_4,b_{12}\) | 63 | 48 | 9 |

An individual attachment at \(s\) contributes two exactly when \(i\le s-2\) and \(j\ge s+1\). This includes the far outermost pair \(e_0,e_{15}\). Holding the other ring's load fixed leaves the same contribution, so the two-ring interaction contrast vanishes for every one of these first-layer bond distances. At \(e_2,e_5\) a quiet attaining shore consists of \(b_3,b_5\) and their common child, giving \(4+8+2=14\) crossings. Under load that child's connection costs four, giving 16. The old interval \(b_3,b_4,b_5\) also attains 16.

## Physical dose with five duplicated ring meetings

Keep the source open counts fixed while doubling the five old ring meetings as registered. Let \(m\) count which of the two ring neighbors \(c_1,c_4\) of \(s\) are active, so \(0\le m\le2\). The path interval cost \(C_{\rm double}(I)\) now includes four ring crossings at \(s\). For **all 64 allowed physical loadings** and all 120 background pairs the first bond size is

\[
 C_{\rm double}(I)-(4-m)\,{\bf1}_{s-1,s+1\in I}.
\]

The path parents \(s-1,s+1\) are always cold. Their common child survives, with \(4+m\) fresh distinctions because it loses one complete candidate triple per active \(c_1,c_4\). To justify erasing an excursion when \(s\) is outside, any such excursion includes \(c_1\) or \(c_4\), a four-open holder. Its removal pays for the direct connection, which costs at most four. With \(s\) inside, a proper piece of the doubled ring contributes at least four old crossings, and removing a complete ring except \(s\) saves more than four opens. All other path gaps have nonnegative net cost; an extra eligible gap obtained by enlarging \(I\) costs at least four before its saving. This establishes the formula even for a partially loaded ring.

Thus \(e_2,e_5\) read \(13+m\), while \(e_3,e_4\) read 9 in every first-layer loading on the doubled source. In the even sector an arbitrary subset of meetings has both copies on. Two meetings touch \(c_1\), two different meetings touch \(c_4\), and the last touches neither. The number with \(j\) doubled meetings selected and \(m\) active neighbors is the coefficient of \(z^ju^m\) in

\[
 (1+z)\,[1+u(2z+z^2)]^2 .
\]

The remaining 32 assignments turn on precisely one copy per meeting, have weight five and \(m=2\). Weighting each physical assignment of the stated weight equally, the mean distance increments for each of the 33 affected pairs are \(0, 4/5, 7/5, 2, 9/5, 2, 2\) at weights \(0,2,4,5,6,8,10\) respectively. From weight five to six the mean falls. All 87 other path pairs stay fixed at this age.

Every first-layer path formula above agrees entry by entry with the independent connected-shore tables. These cover 3,960 pair comparisons over 33 distinct source/activity settings across the eight fixtures, or 9,600 pair comparisons when every allowed physical loading receives its own row. The latter includes all 7,680 path-pair/loading combinations of the doubled source. [Independent first-layer tables and physical loading map](../../artifacts/OLD-MARK-GEOMETRY-20261119-001/OLD-MARK-GEOMETRY-20261119-001-E001_marks/bond_first.json)

## The two original path distinctions at an attachment, every age

For one attachment at \(s\), mark \(e_{s-1},e_s\). The result also holds at either attachment on both doubles while the other ring's load is held at either setting.

| Target ring | Age 0 | Age 1 | Age 2 | Age 3 | Every age \(t\ge4\) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Quiet | 7 | 7 | 7 | 7 | 7 |
| Loaded | 7 | 7 | 7 | 7 | 4 |

These are bond distances. In the proof below, count crossings before subtracting one. Use the shore omitting the wired exterior. If both marks cross, either \(s\) is inside or both of its path neighbors are inside. An additional route from the indicated inside holder to the exterior has to contribute another crossing if it uses neither mark. Pairwise distinction-disjoint routes add their lower bounds; they may meet at ordinary knots. An upper bound always uses a cut with both shores connected.

**Four continuing routes to the path ends.** At ages \(t\ge1\) the original spare at each of \(b_0,b_1,b_{15},b_{16}\) has a unary child with two loose distinctions. Its parent had two opens, so that child has one other sibling, one binary proposal and another unary child. Induction gives a separate unary chain all the way to the current loose exterior for each of the four original holders. The near-end binary proposal is cold in every loading considered. These chains ensure at least two births in every next round. Cold P supplies full demand, so all finite ages exist and there is no globally implied closing top.

Here and below a jump \([u,w]\) means the two *actual* distinct shared inputs \(u\)–\(Q\)–\(w\) of their unique first binary child, and all other steps use individual old shared distinctions. Starting respectively at \(s-2,s-1,s+2,s+1\), use these four ways to arrive at four distinct continuing chains:

- From \(s-2\), take the original path to \(b_1\) and the chain at \(b_1\).
- From \(s-1\), take consecutive two-place jumps between odd path indices down to \(b_1\), then the original \(b_1,b_0\) distinction and the chain at \(b_0\).
- From \(s+2\), take the original path to \(b_{15}\) and the chain there.
- From \(s+1\), take consecutive two-place jumps between odd indices up to \(b_{15}\), then the original \(b_{15},b_{16}\) distinction and the chain at \(b_{16}\).

All attachment indices are even. The jumps survive veto even if their middle old knot is loaded, because both actual parents are cold. The four routes use disjoint distinctions. This remains so when a jump and a plain route visit the same holder.

**Quiet lower and upper bounds.** If \(s\) is inside, start the four routes above by leaving \(s\) through \([s,s-2]\), through the old ring meeting to \(c_1\) and then \([c_1,s-1]\), through \([s,s+2]\), and through the old ring meeting to \(c_4\) and then \([c_4,s+1]\), respectively. Two more routes leave \(s\) into the first pure-ring children \([s,c_2]\), \([s,c_3]\); here each route stops at the middle child of its displayed jump and continues along growing pure-ring descendants. If \(s\) is outside, begin the four end routes at the two inside holders \(s-1,s+1\). For the plain path on either side first take the outward old meeting to \(s-2\) or \(s+2\). The other two routes enter the ring via \([s-1,c_1]\) and \([s+1,c_4]\), then enter the pure-ring children on \(\{c_1,c_3\}\) and \(\{c_4,c_2\}\).

For the two pure continuations, the identified pure old-ring meeting pattern unrolls into a line with five original knot types per turn. The initial two-point clusters above are distinct consecutive intervals. Fix one of the two directions on that line for constructing the certificate. Appending one point at that end at every age gives actual parent-to-child routes and keeps their other ends at distinct residues modulo five. Hence they remain distinct at each age, including after a full turn. Every terminal interval has a loose continuation. These pure chains avoid all four path-end routes. An independent load at the other ring leaves these pure birth terms and their parent sets unchanged by the remote-pure theorem. [Ring-confined cluster and parent identification](../EDDY-WORLD-20261119-001/theory_fate.md) · [Induction for the remote pure part](../STATE-FEEDS-GROWTH-20261119-001/locality.md)

In both orientations the two marked crossings and six additional disjoint routes force at least eight. The eight-place original star of \(s\) attains eight. Its complement is connected: every other old source knot and every new knot has an outward route to a present loose distinction, avoiding \(s\). At the source every original knot has its own loose route. This proves the quiet row.

**The closed part made by a loaded source holder.** At a hot original holder \(p\), every multipart group through \(p\) is vetoed. All its open distinctions go to separate unary children. These children have no parent other than \(p\). No later knot of this branch can acquire a parent from another branch: the two would need a shared earlier holder. The branch meets the rest only through \(p\) and the wired exterior. Every first and later parity equation is physically retained.

At \(s\) there are four such children. Their next layers are precisely the pairs, triples and full set of these four open positions. The pairs have a common singleton when they meet; their unheld maximal triples are the three pairs of a three-member subset. The four resulting three-member subsets are mutually eligible for the unique full-set child. The respective cohort counts are \(4,6,4,1\), and their fresh counts per child are \(3,2,1,1\). The last one follows from the floor and the continuing path ends. At any age 1 through 3, four routes run from \(s\) to the exterior using only this branch. Starting at successive positions on an auxiliary cyclic listing of the four, take the intervals of lengths 1 through \(t\) and then a loose distinction. The four intervals of each length below four are distinct. From age four onward the single fresh distinction of the full set separates the whole first part from later descendants, and one route through it always exists. [Underlying subset growth under the fewest-count rule](../FRESH-COUNT-20261118-001/fresh_count.md)

If \(s\) is inside, add to those routes the old ring meeting to \(c_1\) and the old ring meeting to \(c_4\), each followed through that hot holder's own descendants to a current loose distinction. The two branches are disjoint from each other and from the branch of \(s\). Together with the marks this forces at least eight crossings through age three and at least five thereafter.

If \(s\) is outside, its two path neighbors inside still support the four end routes above. This already gives six crossings including the marks. At the first three positive ages take one additional route from each such neighbor \(v\). The veto of its two pairs with \(c_1,c_4\) supplies two distinct unary children \(U_v,V_v\). At age one use a loose distinction of \(U_v\). At age two continue to the compulsory binary child \(\{U_v,V_v\}\), whose two parents have no common knot except \(v\) and only meet other candidates at \(v\). At age three continue to any child of that binary knot. The two choices on opposite sides cannot reach the same age-three knot because the two binary knots have disjoint parent sets. They cannot meet a pure path-end chain either. This proves the required eight before the full-set child appears.

The eight-place star still gives the early loaded upper bound. From age four on, take exactly \(s\) and its \(4+6+4+1\) descendants just described. Its boundary consists of the four old meetings of \(s\) and the full-set child's single onward distinction, giving a five-cut forever. The inner part is connected by its parent links. The outer part is connected to the exterior: all other source holders and all their descendants can follow an outward chain, and all descendants beyond the full set have their own outward continuation. This proves that it is a bond. The age-zero value follows from the source formula for both preparations. Loading the other ring has no effect on any step of this comparison.

**Literal lower and upper checks.** On both source loadings of the single one-spare attachment and all four loadings of each double, the two-mark result was checked separately at each attachment through age five, giving 108 physical source/loading/attachment/age cells. For each cell, use the actual distinct names of the retained stage. Delete the two marked links and find \(K-2\) units of integral flow to the exterior, first from \(s\), then from the two original path neighbors supplied together, where \(K\) is the claimed bond size. Each physical link has unit capacity, including every member of a parallel bundle. Cancel opposing flows before extracting disjoint routes. This application of flow gives a lower certificate for either possible shore orientation and requires no assumption that an unconstrained minimum cut is a bond. For the upper certificate, take the star shore \(\{s\}\) or the 16-knot shore specified above, count literal crossings, verify both marks present, and traverse both induced shores to check connectivity. All 216 flow tests and all 108 upper-shore checks attained the claimed bounds. These finite checks reach one age past the loaded change. The persistent result uses the explicit continuing routes and retained five-cut, independent of finite confirmation.
