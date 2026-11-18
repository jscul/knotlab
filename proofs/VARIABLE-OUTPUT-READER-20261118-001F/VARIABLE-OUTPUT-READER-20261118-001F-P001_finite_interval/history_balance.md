# Independent check that the reachable population is complete

Forget the names of the distinctions and keep junctions in the order in which they are born. One history records a subset of earlier junctions at each addition and the new output count. Different loose outputs at a single parent play identical roles in this count. For each width the audit counts these histories in two directions. The two counts agree from the initial seed through width 26. At width 26 there are 8,585,343,953 such histories and 4,131,343 ordinary incidence types. [Exact counts](histories.json)

## Count the ways a given arrangement could have grown

For a presented graph \(G\), write \(a_v\) for the total number of distinctions at \(v\), including its loose ones. For \(U\) a set of junctions, let \(R(U)\) be the number of possible birth orders on this set with the induced meetings and the same prescribed total arities \(a_v\). The seed condition is \(R(\{v\})=1\) if \(a_v=3\), and zero otherwise.

Try each \(v\) in \(U\) as the last junction. Its parents must be precisely its neighbors in \(U\setminus\{v\}\). Test the permitted parent counts, their common neighbors in that earlier set, the exclusion of a witness common to three parents, and \(a_v-\#\mathrm{parents}\in\{2,3\}\). If the test passes, add \(R(U\setminus\{v\})\). A parent has the required input available when \(v\) joins. The distinction at that meeting has not appeared in a previous join, and the parent's final arity holds all its eventual ordinary meetings. Conversely each admissible last join appears precisely once in this recurrence.

Let \(A_G\) be the group of ordinary graph automorphisms preserving loose counts. Its action on total orders of distinct junctions is free. For a valid order the earlier neighbor subset and output count at each step are forced. Two such orders give the same chronological sequence of parent subsets and fresh counts exactly when a member of \(A_G\) carries one to the other. Thus the number \(H(G)\) of different chronological histories ending at this unlabelled type is \(R(G)/|A_G|\).

The checker counts \(|A_G|\) by an independent ordinary-vertex bijection search preserving colors and every previously matched adjacency. For interchangeable unused vertices it explores one choice and multiplies by the number of equal choices. Their transpositions fix the partial assignment. The reverse count must be positive and divisible by this exact group order for every type. [Reverse calculation](histories.cpp)

## Balance each width against the two that enter it

Let \(P(G)\) be the number of legal ordinary parent subsets, including their one-, two-, and three-parent possibilities, without choosing a fresh count. Write \(J_w=\sum H(G)\) and \(L_w=\sum H(G)P(G)\) over the delivered arrangements of width \(w\). The audit checks
\[
     J_w=\mathbf{1}_{w=3}+L_{w-2}+L_{w-3}.
\]
Missing lower-width terms count as zero. Each history has either two or three new distinctions in its last step. Each shorter history and parent set supplies exactly one history of each of these widths. This proves the identity for the true reachable population independently of the generator. The computed ordinary graph keys already establish that the delivered types are distinct. Since every delivered \(H(G)\) is positive, the identity would fail at the first width missing a type. An intentionally omitted two-site type triggers exactly this failure. [Balance and deletion control](check_histories.py)

The history numbers prove population coverage. The separate marked matrix comparison determines whether any two of these histories differ on a three-parent permission at identical distances.
