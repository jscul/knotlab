# When joining middle names changes the two-route decision

Status: Proved

## Standard statement

Fix $r\ge1$. At stage $i$ the source implications are

$$
  x_{i-1}\longrightarrow a_i\longrightarrow x_i,\qquad
  x_{i-1}\longrightarrow b_i\longrightarrow x_i .
$$

There are also units $x_0$ and $\neg x_r$. Identify any of the $2r$ middle names by an equivalence relation, preserving the value of a name wherever it occurs. Keep the $r+1$ boundary variables distinct from each other and from every middle. Each implication occurrence and each endpoint unit retains its private padding, witnesses and public switches. The later input specifies all switch bits.

The original scan, which declares a contradiction when both endpoints are on and each stage has a complete original branch, is correct on **every** switch vector if and only if all middle names remain distinct. For every equivalence relation the actual strict CNF is contradictory exactly when both units are on and there is a directed route of live implication occurrences from $x_0$ to $x_r$ through the identified names. This decides a supplied vector in $O(r)$ operations on indexed names. Its inclusion-minimal switch obstructions are exactly the two endpoint groups together with the groups of one vertex-simple directed path, with parallel occurrences distinguished.

## From strict ternary switches to implication occurrences

The fixed encoding comes from the terminal two-route construction. A binary source clause $D$ becomes $(D\lor u)\land(D\lor\neg u)$ with private $u$. An endpoint literal receives four ternary clauses with all sign choices on two private padding bits. Only a complete padding group enforces its source clause. When a clause of the group is inactive, its missing forbidden padding assignment satisfies all remaining clauses even if the source clause is false. [Source construction](../../SIGNED-KNOT-OVERLAP-20261114-001C/SIGNED-KNOT-OVERLAP-20261114-001C-P001_many_easy_obstructions/proof.md)

Each padded ternary clause has one three-witness disjunction and three guards $\neg e_j\lor\neg w_j\lor L_j$. With all three switches on, some true literal must witness the disjunction, and any true literal suffices. With a switch off, its witness may alone be set true. Thus a source implication is live precisely when all its six switches are on. Each endpoint unit needs its twelve switches. This elimination works for *every assignment* of the source variables. It therefore still works when two middle names denote one variable. Every source pair still consists of a boundary and a middle, every padded clause still uses three distinct names, and the private completions in different groups remain independent.

Form the ordinary directed multigraph with the boundary variables and middle equivalence classes as vertices. The occurrence at a stage supplies its two separately enabled arcs $x_{i-1}\to[m]$ and $[m]\to x_i$. If either endpoint unit is missing, assigning all source variables false when the positive unit is absent, or all true when the negative unit is absent, satisfies all live constraints. With both endpoints on, each reachable vertex must be true. Conversely, assigning true to exactly the vertices reachable from $x_0$ satisfies every live implication and, when $x_r$ is unreached, both units. The private completions just described give a model of the strict CNF.

Scan the $24r+24$ switch bits to find the live clauses, then traverse the quotient by its outgoing occurrences. There are at most $3r+1$ vertices and $4r$ implication occurrences. Each is processed a constant number of times. This gives $O(r)$ time and $O(r)$ working words given indexed class labels, and it can return the satisfying assignment. Encoding long external names or computing equivalence classes from a separately supplied unprocessed list of identifications has its own input cost.

## Exact boundary of the original scan

With distinct middles a route must take both halves of the same original branch at every stage. That is exactly what the scan tests. After arbitrary identifications, any sequence of complete original branches still yields a directed walk to $x_r$, so the scan can miss a contradiction only in the other direction.

Suppose first that $a_i=b_i$. Turn both endpoints on. Use one full branch in each other stage. At $i$ use only $x_{i-1}\to a_i$ and $b_i\to x_i$. The identified rule system has a route, although neither original branch at $i$ is complete.

If middles at stages $i<j$ coincide, use one full branch in each stage before $i$ and after $j$. From stage $i$ use only the incoming half to the common middle, and from stage $j$ only the outgoing half from it. Leave all other implications off and both endpoints on. The walk reaches $x_r$ using $2(i-1)+2+2(r-j)$ live implication occurrences. Both exceptional stages are incomplete. Each of these counterexamples remains valid with additional middle identifications, since identifying vertices preserves the displayed walk. Each occurrence can be switched independently. This proves necessity for all equivalence relations.

Processing cuts in stage order can also miss walks that use middle identifications in both directions. At $r=3$, let $J=a_1=a_2$, $K=b_1=b_3$, $H=b_2=a_3$. Turn on only the two endpoint units and the six occurrences

$$x_0\to J\to x_2\to K\to x_1\to H\to x_3.$$

These live arcs form the indicated simple path. Its boundary order is $x_0,x_2,x_1,x_3$, so a rule allowing only increasing boundary indices loses the sole obstruction.

## Minimal switch obstructions

For each vertex-simple directed path $P$ from $x_0$ to $x_r$ in the quotient with all arcs available, let $R(P)$ contain all 24 endpoint switches and the six switches of every occurrence used by $P$. Activating just $R(P)$ contradicts the units. Removing any switch disables an endpoint or breaks the sole path in this set of occurrences. Conversely, in any contradictory setting the live subgraph contains a walk reaching $x_r$. Removing closed portions yields a simple directed path made of live occurrences, so its $R(P)$ is contained in that setting. This characterizes every minimal obstruction and gives $|R(P)|=24+6|P|$. Distinct paths give distinct supports, including paths that use different parallel occurrences. Keeping just the ordered variable pairs would undercount.

For a projection onto a set $U$ of switch names, every unobserved switch may be turned off. Hence the projection is constrained exactly when $U$ contains some $R(P)$ and minimally constrained exactly when $U=R(P)$. On that support the only forbidden vector is all ones, which is the canonical forgetting test. Its state count is $2^{|R(P)|}-1$. This statement concerns allowed switch assignments and uses the graph as a representation of the implications. [K1–K3 definition](../../../docs/FOUNDATIONAL_THESIS.md#canonical-knot-test)

As a control, retain distinct middle variables and identify **only** public switch names. The original stage scan can still be evaluated by using the supplied switch value at every place with that name. Every consistent input then expands to an input for the original correct scan. Under this change the minimal supports are the inclusion-minimal images of the original route supports on the public names. A setting contradicts exactly when it contains one of those images. Images can coincide or contain other images, which explains the minimality qualification.

## What can be carried in one bit between successive stages

Consider deterministic scans in increasing stage order. Each transition sees the entire current four-occurrence activation block, the stage number and the fixed identification pattern, and has at most one bit of state to pass to its successor. Computation within a block is free in this model. Test the endpoint units separately and take them both on below. Write $f(B_1,\ldots,B_r)=1$ when the resulting graph has a source-to-target path.

There is an exact criterion in terms of the paths. At every cut after stage $i$, $1\le i<r$, take **any two** simple occurrence paths $P,Q$ in the all-on graph. Keep from $P$ only its occurrences belonging to stages at most $i$ and from $Q$ only its occurrences belonging to later stages. A one-bit scan exists if and only if every such combined set contains a source-to-target path. The division uses the stage printed on each occurrence, including for a path that visits boundaries out of order.

For proof, the residual of an input prefix is its Boolean answer as a function of the unread suffix. Distinct residuals require distinct states, since two different answers to the same future input cannot be returned from one state. Conversely, residuals suffice as states: appending a block restricts the current residual. At every proper cut the all-off prefix has zero residual because all ways to leave $x_0$ were in the first stage. With one bit there can be at most one nonzero residual. Conversely, if there is at most one nonzero residual at each cut, the zero/nonzero distinction suffices between stages. The first and last transitions and the case $r=1$ require no extra state.

The combined-path condition is precisely the condition of a single nonzero residual. If it fails, the prefix from $P$ works with its own suffix and the prefix from $Q$ works with the suffix from $Q$. Only the latter evaluation is one on that suffix, so these nonzero residuals differ. If it holds, take any prefix with some accepting completion and any suffix with some accepting prefix. In the first completion choose path $P$, and in the second choose $Q$. The proposed combined input contains the indicated combination of occurrences and thus a path. Therefore every extendible prefix accepts exactly the same feasible suffixes.

Allowing every switch vector matters. For example, suppose a separate promise permits exactly one of $s\to u,s\to v$ in the first block and exactly one of $u\to t,v\to t$ in the second. The two accepting paths fail the splicing condition. One bit still suffices to remember which middle was reached, because the prefix that reaches neither middle has been excluded by the promise.

Equivalently, let $h_i(B_i)$ ask whether this one block permits a path when all other blocks are fully on. A one-bit scan exists exactly when $f=\bigwedge_i h_i$. Indeed, if the cut condition holds, any individually feasible blocks may be concatenated. Starting with a feasible prefix, splice it to a complete accepting input containing the next desired block. This yields another feasible prefix. Conversely the conjunction gives a one-bit scan directly. The criterion characterizes the model and makes no assertion that recognizing all suitable identifications is a linear-time preprocessing task.

If all identifications stay within their stages, use at each stage an incoming and an outgoing live half incident to the same actual middle class. If *all* middles across the system coincide, it is enough that some incoming half at stage 1 and some outgoing half at stage $r$ are live. These examples have a one-bit scan even where the original scan fails.

One interstage identification can already require four states. At $r=2$ let $a_1=a_2=C$ and keep $b_1,b_2$ distinct. Consider stage-one inputs that enable neither, either, or both of the disjoint sets $\{x_0\to C\}$ and $\{x_0\to b_1,\ b_1\to x_1\}$. The suffix consisting only of $C\to x_2$ tests membership of the first set. The suffix consisting only of $x_1\to b_2\to x_2$ tests the second. The four prefixes thus have four distinct residuals. Four also suffice here: record which of $C,x_1$ are initially reachable, then take closure with the final block. If $C$ first becomes reachable later it did so from an already reached $x_1$, so reconsidering the old arc $C\to x_1$ adds nothing. General reachability continues to decide the input in linear time.

## Nearest known result

Kleine Büning gives the unjoined Boolean implication family itself in §5, Figure 2. García de la Banda, Stuckey and Wazny give the earlier equality analogue, with exponentially many minimal inconsistent subsets. [Kleine Büning, §5, Fig. 2](https://doi.org/10.1016/j.tcs.2024.114538) · [García de la Banda et al., Example 3](https://doi.org/10.1145/888251.888256)

Linear-time propagation for Horn formulas is classical. Source-to-terminal path sets and ordered decision diagrams provide the classical path and residual-function comparisons. Here the local results are the exact all-input preservation criterion for the original strict-switch encoding, the occurrence-sensitive minimal supports after any allowed identification, and the distinction between preserving the old scan and admitting a different one-bit scan. No SAT complexity separation follows. [Dowling and Gallier](https://doi.org/10.1016/0743-1066(84)90014-1) · [Provan and Ball](https://doi.org/10.1287/opre.32.3.516) · [Bryant, ordered decision diagrams](https://doi.org/10.1109/TC.1986.1676819)

The [checker](check.py) compares occurrence reachability with independent simultaneous truth assignments on all 220 middle-name partitions through three stages. It enumerates minimal activated sets and residual functions. Across the 2, 15 and 203 partitions at one, two and three stages respectively, the counts admitting a one-bit stage scan are 2, 5 and 17. At four stages it checks a further 65,536 edge activations. The raw replay uses PySAT from the current interpreter or the repository environment. With neither available, the Boolean and path checks still run and the raw counts are reported as zero. On this checkout the raw replay includes the backward path and a five-stage bypass. [Retained check](checks.json)
