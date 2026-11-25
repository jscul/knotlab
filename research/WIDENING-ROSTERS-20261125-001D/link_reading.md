# Does a recorded first meeting bind the two sides?

## Claim and selection before measurement

The question concerns the actual distinctions of the structure at the first meeting of two previously selected parts. At each eligible event, test every pair of distinct private places of its two holders against the same shared distinction. On a specified smaller selection, also test **all the holders' private places jointly**. The outcomes are open. A high holder count identifies a candidate. Only the allowed states determine whether the candidate binds.

For the joint test, take the unbarred run under the most-held taking rule in each case in the registered case order. Work separately by case, knot law, meeting route (a common older knot or a cross take), and origin of the candidate distinction (held by a start knot or entirely made). The following selection implements the [frozen experiment contract](../../experiments/WIDENING-ROSTERS-20261125-001D/WIDENING-ROSTERS-20261125-001D-E001_links/contract.json).

1. Keep occurrences with an actual shared identity $c$ and two distinct, oppositely descended holders $u,v$ as defined below. **First select** the lexicographically first occurrence in the group by $(s,t,X,Y,w,u,v,c)$, with each ordered side represented by its sorted member list. A cross take uses the supplying holder as $w$. Preserve phase and take orientation. If multiple archived tests contain the same physical target, keep their source references. The IDs select a repeatable sample, so coverage claims apply to that sample. A relabelling check on a selected occurrence transports the same physical roles.
2. **Then** set $A=P(u)\setminus P(v)$ and $B=P(v)\setminus P(u)$, where $P$ is the list of places as a set. If $|A|+|B|+1>14$, mark that representative **not run** without substituting a smaller one. The one counts $c$. All other shared places are hidden. Record any empty arm, over-width representative, and group with no actual shared-identity occurrence. An empty private record has one value and cannot have a proper attachment.
3. On every selected occurrence determine exactly whether the complete private records are independent given $c$, and which of their two attachments to $c$ constrain them. An untested occurrence receives no verdict. This selection and width cap apply to the full-record check. The separate all-private-literal test keeps its registered population.

The criteria here can be applied by independent programs given the recovered event records and the incidence of the complete stage. The original compressed summaries retain the origin and class of a link, but omit its holder and distinction lists. Those summaries alone cannot determine a ternary relation. [Earlier probe](../WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further/README.md) · [Archived link summarizer](../WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further/links.py)

## Which physical objects are being tested

Fix one unbarred run, a split after round $s$, an ordered pair of distinct parts $X,Y$ at that split, and their first meeting at round $t>s$. Reconstruct each knot's descent from the recorded parents. A holder on the $X$ side descends from $X$ and does not descend from $Y$. Define the $Y$ side in reverse. Retain any additional part-of-origin bits and report them. A mixed holder descended from both cannot stand for two independent roles. The two sides' member lists and the meeting round belong to the run under its own knot law. A parity reading of a fixed not-all-equal structure is a law swap on that incidence unless its actual parity growth is also shown to reach the same structure.

The earlier study counted two kinds of route. Both must keep their original event evidence. [Definition of the linking set, §5](../WHAT-A-BIRTH-CARRIES-20261125-001/definitions_b.md) · [Descent and link reader](../../experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot/read.py)

* **Common older knot.** In the particular recorded roster or demand roster, a linking knot $w$ meets a holder $u$ of the first side and a holder $v$ of the other. Test every $c\in P(w)\cap P(u)\cap P(v)$. If this intersection is empty the recorded meeting uses distinct places on its two sides. Retain its two sets of places and report **no single shared identity on this route**. A third place arbitrarily chosen on $w$ would answer another question.
* **Cross take.** A birth on one side takes a distinction $c$ that a holder on the other side already held. Keep the precise take record and its pre-take holder list. The new holder and the supplying holder are $u,v$, ordered by $X,Y$ regardless of take direction. Check the same $c$ on both after the round. A common place inherited by both through a different route is separate from this take.

The original link reader listed places of $w$ held by **either** descent. The identity check above asks for **both** in one recorded occurrence. It can therefore legitimately return no shared identity for a recorded linking knot. A shared identity in an unrelated part of the same snapshot does not repair that failure. For each tested $c$, retain its physical ID, first holder or fresh maker, complete holder list with rounds and descents, start-held flag, phase and route. Distinct holders of the same high-count distinction, repeated archived tests and two distinct shared identities have different meanings and should be counted separately.

## Literal distinctions and the ternary relation

Enumerate $a\in A$, $b\in B$. These are literal variables of the respective holders. The coordinates $a,b,c$ are intrinsically different IDs. Preserve the fresh maker of each place when there is one, and its holders at the split and the meeting. A place can be private to these two holders and still have been borrowed from another descent. Distinguish a fresh place arising on its side, a place already carried by that side at the split, and an external or mixed origin. An original start distinction has no fresh maker in the growth record. Its actual start holders supply its provenance.

Let $S_t$ be all the constraints in the stage after the meeting round. For each $a,b,c$ calculate

$$
R=\{(i,j,k)\in\{0,1\}^3:\text{some full state of }S_t
\text{ has }a=i,\ b=j,\ c=k\}.
$$

Check all eight existential extensions, preserving all older knots, barred distinctions, and fresh distinctions. A bar prevents a growth action. It does not fix a Boolean value. For parity the constraints are linear equations over two elements. For not-all-equal each list excludes its two constant assignments. Record the eight-state mask and the three pair projections; check the mask by the canonical forgetting test. Encode a projected mask in the knot checker with one clause forbidding each excluded assignment. The checker then tests that mask; an independent reconstruction of the mask still tests the projection itself. [Canonical test](../../docs/FOUNDATIONAL_THESIS.md#canonical-knot-test) · [Knot checker](../../tools/knotlab/README.md)

A coordinate is open when its unary projection contains both bits. The four assignments in $\pi_{ab}R$ witness independent choices of the two visible side distinctions in the actual stage. The other two pair projections measure the other two erasures. When $a,b$ both existed at the end of round $t-1$, project that pre-meeting stage onto them too. Record whether they were already present at the split. For later births record their actual sources, without assigning a post-meeting place to a structure in which it did not exist. Record failed openness as a finding. Do not prefilter on $\pi_{ab}R$ being full, since a genuine conditional product through $c$ can leave $a,b$ tied when $c$ is forgotten.

Use the following tests to classify $R$. Here a join of two projections is the set of assignments agreeing on their common coordinate. Keep a separate flag for each fixed coordinate alongside the class.

| Verdict | Exact test |
| --- | --- |
| Incoherent | $R$ is empty. |
| Fully free | Eight states. K1 fails. Its two projections through $c$ are both free. |
| Ternary knot | Fewer than eight states, nonempty, and all three pair projections are full. K1–K3 hold. |
| Proper two-sided common hub | $R=\pi_{ac}R\bowtie\pi_{bc}R$. Each pair restricts its two open coordinates. |
| One-sided attachment | The same equality holds with exactly one restrictive pair relative to its unary supports. |
| Other constraint | Any remaining constrained relation. Report the fixed-coordinate flags, pair shadows and whether joining all three pair shadows reconstructs $R$. |

“Proper” requires an actual dependence, which in general is $\pi_{ac}R\subsetneq\pi_aR\times\pi_cR$, and likewise on the other side. The free relation satisfies the product equality trivially. It gives no evidence of a restrictive hub. A tie between $a$ and $b$ with $c$ free belongs under other constraint. Under even parity with no constants every projection is linear. In particular the only possible three-variable K1–K3 knot in such a projection is even parity on the three distinct variables, a consequence of all pair projections having rank two.

A K1–K3 pass answers the allowed-state question for these recorded variables. Identifying the two *parts* as native recurrences additionally requires independent evidence of the two continuing recurrence laws and how each supplies its displayed distinction. A part label or an effect of barring a part supplies neither recurrence by itself. If the aim is to credit the take with causing the binding, even an identified pre-existing knot requires a separate matched source-preserving comparison. Canonical erasure forgets a coordinate in $R$. Barring a part and regrowing answers a different, dynamical question. [Foundational recurrence and contact conditions](../../docs/FOUNDATIONS.md#first-emergence)

## Full private records and what they settle

For the selected holders project the same complete $S_t$ onto the disjoint place sets $A,B$ and the single actual $c$. Call this relation $G$. For each attainable bit $k$ let $G_k$ be its pairs of private records and let $A_k,B_k$ be their respective projections. Each $G_k\subseteq A_k\times B_k$. Thus the exact full-record product condition is

$$
 G=\pi_{Ac}G\bowtie\pi_{Bc}G
 \quad\Longleftrightarrow\quad
 |G_k|=|A_k|\,|B_k|\text{ for every attainable }k .
$$

The $A$ attachment is restrictive precisely when $\pi_{Ac}G\subsetneq\pi_AG\times\pi_cG$, and similarly for $B$. When $c$ is open, this is equivalent to $A_0\ne A_1$. Restrictions *within* either record do not by themselves bind that record to $c$. Preserve the fiber sizes, the two proper-attachment flags and the number of absent joint records. If a product fails, retain a witness consisting of two separately admissible records with the same $c$ whose combination has no extension. Check the result against a separate exact projection. A full test can use projected table counts; for parity a separate dimension check is

$$
 \dim G = \dim\pi_{Ac}G + \dim\pi_{Bc}G - \dim\pi_cG .
$$

The right side is the dimension of the joined projections, since the two linear maps onto their common projection on $c$ are surjective. Equality of dimensions decides equality by inclusion. For not-all-equal the extension test uses all the original constraints. Validating all admitted rows alone cannot show that a claimed absent combination is impossible.

If the full-record product holds, every separate reading $a=f(A)$, $b=g(B)$ still satisfies a product conditional on $c$. For fixed $k$, its allowed pairs are exactly $f(A_k)\times g(B_k)$. Such readings cannot give a K1–K3 knot over $a,b,c$. If both erasures through $c$ were full, that product would contain all eight states. A proper product therefore rules out an undiscovered side-local binary knot on **these two private records**, even when no individual place shows a restrictive attachment. A failed product exhibits dependence that survives conditioning on $c$. It does not by itself produce a binary knot or establish its native sources. Other common places were hidden in $G$, so unrepresented side variables and paths outside these holders lie beyond either conclusion.

## Controls on the choice of a side distinction

* Two parity holders with places $(a,p,c)$ and $(b,q,c)$ give a free projection on $(a,b,c)$. Their full private records do factor through $c$, with both attachments proper. Both statements also hold when the two holders use not-all-equal. Thus a free literal triple and a proper product of records are compatible.
* A four-place parity rule on $(a_1,a_2,b,c)$ gives a free triple on each $(a_i,b,c)$, but the side-local parity $a_1\mathbin\oplus a_2$ gives a ternary parity knot with $b,c$. A four-place not-all-equal rule likewise gives both free triples. Reading the first side as “both of its bits are one” excludes just $(1,1,1)$ on that reading, $b$, and $c$. Consequently free literal projections alone cannot justify a claim about every named pattern on one side. These are logical controls, independent of whether either aggregate is supplied by the growth.
* The distinction persists with two actual holders sharing only $c$. Give $u$ the places $(c,x_1,x_2,z)$, give $v$ the places $(c,y_1,y_2,w_1,w_2)$, and add a third rule on $(z,y_1,y_2)$. Every single private place of $u$ and single private place of $v$ have full projection with $c$ under either law. Under parity one can solve for the unassigned member of each needed pair. Under not-all-equal one can choose $x_1\ne x_2$ and $y_1\ne y_2$ even after fixing one private place on each side. Yet under parity $A'=x_1\oplus x_2$, $B'=y_1\oplus y_2$ satisfy exactly $A'\oplus B'\oplus c=0$. Under not-all-equal let $A'=x_1\lor x_2$ and let $B'=1$ when all four private places of $v$ agree. When $B'=1$ their common bit must be $1-c$, hence $z=c$. When $B'=0$ choose $y_1\ne y_2$ and $z=1-c$. The only excluded triple is $(A',B',c)=(0,1,0)$.
* An aggregate can manufacture a verdict. If $x=y$ while $c$ is independent, setting $a=x\mathbin\oplus c$ and $b=y$ gives a ternary parity knot by its definition. Conversely, on a parity holder the parity of every place except $c$ equals $c$ identically. Reading this parity on both sides forces $a=b=c$ for every shared $c$ under that knot law. Neither construction identifies side distinctions independently of the putative coupling. A proposed aggregate needs its own side-local source and a reason for choosing it before its verdict is known.

Direct enumeration of the 256 assignments in the two-holder control gave full masks on all twelve private-place pairs under each law. The canonical knot checker accepted the two stated aggregate masks. These checks concern the explicit control.

The source-preserving comparison is therefore between the actual shared-place literal test and the bounded complete-private-record test. The latter quantifies over separate readings by the product argument, without choosing one to meet a desired target. Through either test, keep an incidence link, a free relation, a proved two-sided product, and a K1–K3 pass at their own evidence levels.
