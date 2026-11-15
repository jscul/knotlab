# Shared padding on two alternative implication branches

Status: Proved

## Standard statement

At stage $i$ the two branches are $x_{i-1}\to a_i\to x_i$ and $x_{i-1}\to b_i\to x_i$. All $2r$ middle names are distinct. The endpoints have units $x_0,\neg x_r$ for $r\ge1$. Each implication occurrence $D_e$ has two half-clauses $D_e\lor p_e$ and $D_e\lor\neg p_e$. The hidden Boolean pads $p_e$ may be arbitrarily identified with one another, including across stages. They are distinct from all original variables, endpoint padding, slot witnesses and visible guards. All visible guards and slot witnesses are occurrence-private. A minimal support is an inclusion-minimal set of visible guards whose ones already force unsatisfiability.

At a stage let $P_i$ be the pad names that occur on **both** branches, and let $m_i(p)$ count the occurrences of $p$ among its four implications. The polynomial whose coefficient of $z^k$ counts the inclusion-minimal $k$-guard obstructions to a local drop $x_{i-1}=1,x_i=0$ is

\[
 L_i(z)=2z^{12}+2\sum_{p\in P_i}z^{3(8-m_i(p))}.
\]

The first two supports activate both halves of both implications on either one branch. Each $p\in P_i$ contributes two further supports. On every $p$-occurrence of the first branch choose one sign, on every $p$-occurrence of the second choose the opposite sign, and on all other occurrences choose both halves. Include all three guards of each chosen half. At the global visible-guard projection the corresponding polynomial is

\[
 z^{24}\prod_{i=1}^r L_i(z).
\]

The original independent-implication scan decides every visible guard vector exactly when $P_i$ is empty at every stage. A pad reused solely between different stages can affect the projection if internal original variables are also observed.

## Nearest known result

Eliminating a shared Boolean variable can relate distinct clauses that carry its opposite literals. This is the resolution step in classical Davis–Putnam variable elimination. Earlier project results give reachability for shared middle variables with private pads, and exact continuation classes for already-active positive implications. Here the middle variables are distinct and the hidden padding variables may coincide. The result gives every minimal guard support introduced by this identification, its size, and the projection for which the stage product holds. [Davis and Putnam (1960)](https://web.stanford.edu/class/cs357/DP60.pdf) · [Joined-route proof](../../UNSIGNED-ROUTE-JOINS-20261115-001Z/UNSIGNED-ROUTE-JOINS-20261115-001Z-P001_synthesis/proof.md) · [Implication boundary proof](../../ROUTE-FRONTIER-MEMORY-20261115-001Z/ROUTE-FRONTIER-MEMORY-20261115-001Z-P001_synthesis/proof.md)

## One stage with a prescribed drop

Every strict ternary clause $L_1\lor L_2\lor L_3$ is represented by a private slot

\[
 (w_1\lor w_2\lor w_3)\ \land\
 \bigwedge_{h=1}^3(\neg e_h\lor\neg w_h\lor L_h).
\]

When a guard is off, choosing its witness alone satisfies the slot for all literal values. When all three guards are on, a witness exists exactly when the displayed clause holds. Hence an implication half is active precisely when its three guards are on. A unit uses four signed strict clauses on two fresh private pad names. If the unit is false, these four clauses each exclude a different pad assignment. Thus a unit is enforced exactly when all twelve of its guards are on.

With the stage endpoints fixed to $1,0$, the value of each middle selects exactly one failed implication in its branch. If the middle is false the incoming implication fails, and if true the outgoing one fails. On a failed occurrence, zero active halves allow either pad value, one active half requires its displayed literal, and two active halves allow no pad value. The local drop is feasible exactly when one can select one failed occurrence on each branch whose two pad requirements are simultaneously satisfiable.

If both occurrences of one branch have both halves active, the branch alone forbids the drop. Otherwise each branch has at least one available occurrence where at most one half is active. If any available occurrence has neither half active, it can pair with any available occurrence on the other branch. For all pairs to fail, every available occurrence must therefore require a single literal. Two single literals conflict only when they name the same pad with opposite signs. Fixing one available occurrence on each branch shows that *all* available occurrences on the first branch must demand the same sign of one $p$, and all on the other branch its opposite. Every non-$p$ occurrence then has both halves active. Every $p$ occurrence contains its branch's designated half. Thus every blocked local setting contains one of the displayed supports.

For a one-branch support, deleting any half leaves an available occurrence there and a completely free choice on the other branch. For a support indexed by $p$, deleting a designated $p$-half frees that occurrence entirely, so it can pair with an opposite-branch $p$ occurrence. Deleting a half on an occurrence of another pad $q$ leaves one $q$ literal. It can pair with an available $p$ occurrence since $q\ne p$. This proves minimality. Opposite orientations give different supports, and two distinct indexing pads have different sets of singly active occurrences. A $p$-support has $m_i(p)+2(4-m_i(p))=8-m_i(p)$ active halves. Three guards per half give $L_i$.

## The 15 local identifications

The four digits name pads in order on the first branch's incoming and outgoing implications and then the second branch's. Equal digits denote the same pad. The table gives every partition up to renaming the pads. The two right columns count the settings forbidding a drop, among $256$ half activations and among $2^{24}$ raw stage-guard vectors, respectively.

| Pad identifications | Number | Minimal local supports by guard count | Blocked half settings | Blocked raw settings |
| --- | ---: | --- | ---: | ---: |
| 0011, 0012, 0122, 0123 | 4 | 2 of size 12 | 31 | 8,191 |
| 0102, 0112, 0120, 0121 | 4 | 2 of size 12 and 2 of size 18 | 33 | 8,289 |
| 0001, 0010, 0100, 0111 | 4 | 2 of size 12 and 2 of size 15 | 37 | 9,073 |
| 0000 | 1 | 4 of size 12 | 49 | 16,129 |
| 0101, 0110 | 2 | 2 of size 12 and 4 of size 18 | 35 | 8,387 |

For the count, give each half $c$ possible inputs, exactly one of which activates it. An old complete branch occurs in $2c^4-1$ settings by inclusion and exclusion. Suppose $p$ occurs $a$ times on the first and $b$ times on the second branch. Under a prescribed orientation every designated half and every non-$p$ half is active. At least one partner half on each branch must be inactive to avoid the old obstruction. This gives $(c^a-1)(c^b-1)$ settings per orientation. The available occurrences determine both $p$ and its orientation uniquely, so these contributions are disjoint. Taking $c=2$ counts half activations, and $c=8$ counts the three-bit guards of a half.

## Why the visible-guard supports multiply

With both endpoint units enforced, every assignment to the originals has a stage with a drop from one to zero. Conversely, if some stage admits a drop, choose its witnessing middle and pad values. Set every earlier stage boundary and middle true, and every later stage boundary and middle false. Every implication outside the chosen stage is then true for *any* value of its pad. The chosen pad values are consistent throughout, including every reuse in other stages. If one endpoint unit is inactive, a constant assignment to all originals satisfies the remaining unit and every implication, and private endpoint pads can be extended.

Thus the whole system is contradictory exactly when both units are active and every stage forbids a drop. Every such setting contains the 24 endpoint guards and one minimal obstruction from each stage. The guard sets are disjoint. Dropping any single selected guard either frees an endpoint or restores a drop in its stage. These are exactly the minimal global positive supports. On the unpinned projection of any such support, all assignments except the all-one assignment extend by setting the outside guards off. Any constrained projection contains one such support, since the feasible guard vectors are closed under turning guards off. This proves the product, including arbitrary identifications between stages. If any $P_i$ is nonempty, put a new minimal support at that stage and an old minimal support at every other one. The old scan answers SAT on this explicit UNSAT setting.

Keeping internal originals can change the result even with just *one* interstage pad identification. In three stages, share only the pad on the incoming first-branch implication of stages one and three. At the first stage activate its positive half and both halves of its outgoing first-branch implication. At the third stage activate the negative half and both outgoing halves. Leave their second branches off and activate all halves of the middle stage. Use both endpoint units. Pinning $x_1=0$ forces a first-stage drop with $p=1$. Pinning $x_2=1$ forces a last-stage drop with $p=0$. Either single pin extends, as do the guards alone. Both pins together make the system unsatisfiable.

## Raw strict-CNF witness and finite checks

In one stage with all four pads identical, turn on only the two positive halves on the first branch and the two negative halves on the second. These half activations have mask 90, using the negative then positive half of each implication and starting with the least significant bit. Turn on both endpoints and all three guards of each chosen half, for 36 visible ones. With fresh pads this vector is satisfiable. Sharing all four pads makes it unsatisfiable, and deleting any one of the 36 guards restores satisfiability. Given the endpoint values, the four active half-clauses read $(a\lor p),(\neg a\lor p),(b\lor\neg p),(\neg b\lor\neg p)$.

Number guard bits from zero with the 24 endpoint guards first. Fix all but indices $27,33,36$ as in that vector. Direct solving of the guarded strict clauses gives seven permitted assignments on these three guards. The missing tuple is $111$, every single-coordinate forgetting is full, and the canonical K1–K3 checker accepts the observed relation with loop labels **AinPlus, AoutPlus** and contact label **BinMinus**. Freeing guard 42 as well gives 15 of 16 assignments, with the first three labels as loops and **BoutMinus** as contact. These are finite relations on named guards under the stated restrictions. The evidence concerns the relations and their forgetting tests.

Run the following command from this directory. The default replay uses the repository's PySAT environment for the guarded clauses and calls the canonical knotlab CLI on the observed restrictions.

~~~sh
python3 -B check.py
~~~

The checker enumerates original truth assignments, retains minimal sets of failed implications, and assigns the actual pad identities there. Supersets of failed implications impose at least the same literal restrictions for every fixed pad assignment, which justifies this reduction independently of the stage theorem. Downward closure gives the exact feasible half activations. It agrees with every claimed support and decision on all 3,840 local cases and all 271,319,040 two-stage cases. The latter cover all 4,140 partitions, including 3,915 with interstage sharing. An independent SAT solver receives the predecessor's fully expanded guarded strict clauses with the pad names literally identified. It checks 9,216 complete raw vectors, 77 minimal supports and all 3,336 individual deletions, with additional cases through six stages. The all-$r$ result follows from the single feasible drop construction. [Executable checker](check.py) · [Numerical evidence](checks.json)
