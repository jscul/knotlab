# Recognizing a nested reading by swapping whole branches

Status: Proved

## Standard statement

A stage has two branches. Each branch has three positions, read as its middle name, its incoming pad name and its outgoing pad name. The two kinds of names have disjoint indexed namespaces. Each name occurs once or twice in the full $6r$ positions. A single pad position stands for the two signed half-clauses of one guarded implication. A legal reading chooses the order of the two entire branches independently at each stage, keeping the order of stages and the internal order of each branch. The raw guards travel with their branch.

For any layout, _zero_order(middles, pads)_ returns a vector of $r$ swap bits whose reading contains no alternating pair of names, or reports that every reading contains such a pair. It uses $O(r+1)$ indexed operations and words, including recognition of impossibility. In the returned vector, a zero reads the supplied upper branch first. In the input the two middle and four pad identifiers per stage follow the flat order of the predecessor. Each identifier in each separate namespace lies in $[0,6r)$ and has at most two occurrences. The empty layout returns the empty tuple. Reading or interning arbitrary strings additionally incurs their supplied input cost. [Solver](solver.py) · [Guarded-stage semantics](../../TWO-RELAY-PADDING-20261115-001D/TWO-RELAY-PADDING-20261115-001D-P001_nested_pair_grouping/proof.md)

Consequently, whenever any legal reading is nested, finding such a reading and then deciding SAT for **any supplied guards** takes $O(r+1)$ indexed operations. The predecessor can also recover a full assignment. Physically permuting the two triples and their four associated signed guard slots per branch takes linear work across stages. Both branches in a stage use the same ordered pair of boundaries. Interchanging the two conjunctive branch requirements preserves all assignments to the original names once positions are mapped back. The witness and endpoint conventions are those of the predecessor.

## How one swap changes alternation

Retain only the names $x\ne y$ that occur twice each. Let $a_{xy}$ be 1 when their occurrences alternate in the original order, and 0 otherwise. Equivalently it is the parity of the number of ordered endpoint pairs with a $y$ before an $x$. On $xxyy,xyxy,xyyx,yxxy,yxyx,yyxx$ these counts are $0,1,2,2,3,4$. Other names and singletons do not affect them.

In stage $i$ let $u_i(x),l_i(x)$ be the multiplicities of $x$ in its supplied first and second branches. A whole-branch swap reverses precisely the comparisons between one position in each branch. Its coefficient for this pair of names is

$$
c_i(x,y)=u_i(x)l_i(y)+l_i(x)u_i(y)\pmod 2.
$$

Different stage swaps concern disjoint comparisons. Thus bits $s_i$ eliminate the alternation between $x$ and $y$ precisely when

$$
\bigoplus_{i:\,c_i(x,y)=1}s_i=a_{xy}.
$$

This formula counts occurrences even when both ends of one or both names lie in a single stage.

- With one occurrence of each name there, the coefficient is one exactly when they occupy opposite branches.
- With three of the four endpoints there, one name occurs twice. The coefficient is one exactly when that name occurs in both branches. If both occurrences are in the same branch, their two potential reversals cancel.
- With all four endpoints there, each name has even total multiplicity, so $u_i(x)=l_i(x)$ and $u_i(y)=l_i(y)$ modulo two. The coefficient vanishes, including on invariant alternating orders.
- A nonzero coefficient requires both names to occur in its stage. Each name occurs only twice in all, so a pair yields at most two nonzero coefficients. A pair with no such coefficient has the same alternation status in every reading.

## A sparse construction and one verification

Record first and second positions for every typed identifier. In each stage examine its nine cross-branch position pairs. When both names are doubled and distinct, emit their two identifiers in increasing order together with the stage index. There are at most $9r$ records before cancellation. Sort by the two identifiers using two stable counting-sort passes on the dense namespace, secondary key first. Records arrive in stage order, which both passes preserve within one name pair. Count each distinct _pair, stage_ group modulo two. For a pair with one or two stages left, compute $a_{xy}$ by comparing its four stored positions. A unary equation is a pin. A binary equation specifies the XOR of two stage bits. Each identifier pass takes $O(r+1)$ time and storage. No table lists every pair among all names.

Make a graph with a vertex for each stage and one extra vertex fixed to zero. A pin joins its stage to zero, and each binary equation joins its two stages, with the required XOR on the link. Propagate values from the fixed vertex first, then from an arbitrary zero seed in each remaining component. An inconsistent revisit certifies that the original equations have no solution. Otherwise this produces a solution of all equations with nonzero coefficients, using linear work. When feasible, each component disjoint from the zero vertex contributes one free binary choice.

There may be quadratically many pairs whose coefficients all vanish. Check the entire reading under **one** propagated assignment using a stack. Ignore singleton names. Push a doubled name when it is first seen in that reading. At its second occurrence, it must be at the top. If $x$ closes underneath an open $y$, then $x,y,x,y$ occur in this order. Conversely a successful scan closes every pair inside its predecessor or outside it. The scan reads occurrences anew after the swaps, including the case when both occurrences of a name were in the same stage.

If the stack succeeds, the returned reading is nested. If it fails, every equation having a nonzero coefficient was satisfied, so a violating pair has zero coefficients in **all** stages. It therefore violates every possible reading. Searching other solutions of the graph would give the same verdict. This proves completeness and the claimed time and space bounds. It also shows that the set of valid readings is either empty or exactly the entire affine solution set of the graph. Its nonzero cardinality is a power of two.

Two stages illustrate why propagation alone is insufficient. Give the first stage the branches $(A,P,Q)$ and $(B,P,Q)$, and the second $(A,u,v)$ and $(C,w,z)$, with fresh lowercase pads. Eliminating the alternations of $A$ with $P,Q$ requires the first stage to keep its order. Those requirements are consistent. The pair $P,Q$ alternates under every choice, so the final scan correctly rejects. The four readings have respectively one, one, three and three alternating pairs.

A different failure needs three pairs but no invariant alternation. Use fresh middle names and put the pads in the order $(A,B\mid C,u)$ at stage 1 and $(v,A\mid B,C)$ at stage 2, where the bar separates branches. Initially the repeated names read $A,B,C,A,B,C$. Nesting $A,B$ requires $s_2=1$, nesting $B,C$ requires $s_1=1$, and nesting $A,C$ requires $s_1\oplus s_2=1$. Each pair can be repaired separately. The three requirements contradict each other.

## How many names cease to need conditioning

For $t\ge1$, use $r=2t$ stages. In consecutive stages $2j-1$ and $2j$ put the same pair of distinct positive middles $(A_j,B_j)$ in the same order, with distinct names between gadgets and fresh pads everywhere. The original word spells $A_j,B_j,A_j,B_j$ within each gadget. Each gadget contributes exactly one conflicting pair, and the gadgets are disjoint. Precisely $t$ names must be conditioned to make the original reading nested. Swap the second stage of each gadget. The new word spells $A_j,B_j,B_j,A_j$ and needs zero conditioned names. The returned bits obey $s_{2j-1}\oplus s_{2j}=1$ separately for each gadget.

Thus the nested verifier can handle every guard vector on this family in linear indexed work after recognition. For example, activating both endpoints and every implication gives an unsatisfiable instance. Disabling the negative endpoint while keeping all implications active allows the all-true boundary-and-middle assignment. The number $t$ lower-bounds the number of names that this particular conditioning method must omit when restricted to the supplied reading. Other SAT algorithms may use a different method.

## Nearest known result

The existence of a linear zero-alternation decision also follows from the linear algorithm of Angelini, Di Battista, Frati, Jelínek, Kratochvíl, Patrignani and Rutter for extending a partial planar embedding. Here is a direct reduction, using ordinary graph-theoretic terminology. Take an ordered root star with one distinguished leaf marking the beginning, and its other children the stages in fixed order. Each stage vertex has two children, one for each branch. Each branch vertex has three ordered leaf children for its three positions. Add a matching link between the two occurrence leaves of every doubled name.

In a plane embedding of the rooted tree, the order of the occurrence leaves around its boundary is exactly a legal reading if the root and branch rotations are prescribed and the stage rotations are free. A small closed neighborhood of a plane tree is a disk. The matching links can be drawn in the complementary disk exactly when their endpoints do not alternate. An arc joining one pair separates the two arcs of the boundary that it determines. Conversely, nested and disjoint pairs can be drawn recursively. Hence existence of a nested legal reading is equivalent to extendibility of the prescribed rotations.

To encode those rotations in a partially embedded graph, subdivide tree links sufficiently to give each fixed vertex its own incident stubs. Pre-embed the disjoint stars of stubs around the root and each branch vertex in the chosen circular orders. All other segments and all matching links are free. Since the prescribed graph is a forest with only one face, this partial embedding imposes precisely these rotations and no cycle-containment restrictions. A planar extension supplies the desired stage rotations, and an embedding respecting the rotations restricts to the prescribed forest embedding. The graph has $O(r+1)$ vertices and links. This is a literature comparison. The local algorithm derives its parity equations from the six physical positions and implements them directly. [Angelini et al., *Testing Planarity of Partially Embedded Graphs*](https://doi.org/10.1137/1.9781611973075.19)

## Validation and limits

The finite checker independently generates partitions into singleton and doubled names in each role, literally permutes triples for each candidate and compares endpoints of every doubled pair. At two stages there are 10 middle partitions and 764 pad partitions. Of the 7,640 layouts, 965 work in supplied order, another 1,106 acquire a nested reading by swaps, and 5,569 admit none. The counts with exactly $0,1,2,4$ successful orientations are $5{,}569,908,850,313$. The reference also exhausts the 18,144 readings of 216 larger layouts through eight stages. The indexed implementation returns an exception-free reading of the 8,192-stage family whose supplied order requires conditioning on 4,096 names and rejects a 4,800-stage input with 2,878,800 invariant alternating pairs. A separate same-task reviewer checked the multiplicity cases and supplied the invariant with two consistent pins. These are V1 finite corroborations of the argument. This theorem concerns finding a zero-exception reading and the inherited SAT method on its domain. [Checker](check.py) · [Counts and controls](checks.json)

