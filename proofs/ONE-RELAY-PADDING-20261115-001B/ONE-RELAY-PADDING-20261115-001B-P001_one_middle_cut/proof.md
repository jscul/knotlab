# A linear SAT algorithm with shared padding and one repeated middle

Status: Proved

## Standard statement

At stage $i=1,\ldots,r$ there are two branches $x_{i-1}\to m\to x_i$. The boundaries $x_0,\ldots,x_r$ are distinct. At most one middle name $J$ is reused, positively and with arbitrary multiplicity. It may occupy both middle positions of the same stage. All other middle positions have their own variables. Use the guarded strict ternary encoding below, with arbitrary reuse of Boolean padding names **between implication occurrences**. The two endpoint units retain private padding, and each witness and each public switch retains its own name. No boundary, middle or padding variable is externally pinned. Given a Boolean value for every switch, ordinary existential satisfiability is decidable in $O(r)$ indexed operations. On a positive answer a full assignment to the strict formula can be produced in the same bound.

## What a falsified implication requires

Let $D_e=\neg u\lor v$ be the source clause of occurrence $e$. Its two padded slots contain $D_e\lor p_e$ and $D_e\lor\neg p_e$, using the same pad within the pair. A pad name can occur in any number of other pairs. A strict clause $L_1\lor L_2\lor L_3$ has three local witnesses and three local switches. The rules are the witness disjunction and the three guards $\neg e_j\lor\neg w_j\lor L_j$. With all three switches on, some literal must be true. Otherwise the witness for an off switch suffices irrespective of the literal values. Call a padded slot active when all three switches are on. This elimination is exact for each assignment of its three literals.

When the source implication is true, its active slots impose no demand on the pad. When it is false, its active slots impose exactly one of four requirements.

| Active padded slots | Requirement for falsifying the implication |
| --- | --- |
| Neither | Free |
| Only $D_e\lor p_e$ | $p_e=1$ |
| Only $D_e\lor\neg p_e$ | $p_e=0$ |
| Both | Impossible |

Write $d(e)$ for this requirement. A collection of requirements is jointly possible exactly when it contains no impossible requirement and no pad is required both true and false. In particular, a singly active slot with literal $p_e$ *enforces* its implication at $p_e=0$ and *allows it to fail* at $p_e=1$.

Each endpoint unit $x_0$ or $\neg x_r$ is padded by all four sign combinations on two private variables. It is enforced exactly when all four of its slots are active. If its literal is false and some slot is inactive, use the unique pad assignment forbidden by that missing slot. When the positive endpoint is unenforced, set every boundary and middle false. When only the negative endpoint is unenforced, set every boundary and middle true. Every implication is then true, so the reused pads may be assigned arbitrarily. These cases include partially switched endpoint slots.

## The two values of the shared middle

Now let both endpoints be enforced. A candidate cut $k$, with $1\le k\le r$, sets $x_0,\ldots,x_{k-1}$ true and $x_k,\ldots,x_r$ false. At stages earlier than $k$, give each ordinary middle value one. At stages later than $k$, give each ordinary middle zero. All implications through these ordinary middles are then true.

At the cut an ordinary branch must break. For each ordinary middle there, choose either the incoming or the outgoing occurrence for its false implication. Choosing the incoming one sets the middle false, and choosing the outgoing one sets it true. The other occurrence on that branch is true. There are zero, one or two ordinary branches at the cut, so at most four combinations of demands.

- For $J=1$, add $d(J\to x_i)$ for **every** occurrence of $J$ at every stage $i\ge k$. All incoming occurrences into $J$ are true. Its outgoing occurrences before $k$ are true.
- For $J=0$, add $d(x_{i-1}\to J)$ for **every** occurrence of $J$ at every stage $i\le k$. All outgoing occurrences from $J$ are true. Its incoming occurrences after $k$ are true.

If no middle is shared, either value can be used for the empty collection of special occurrences. If both positions in a stage are $J$, the two occurrences generate their separate requirements and there is no ordinary branch there. For any proposed value, cut and choices, the listed requirements are exactly the requirements on the false implications of the constructed assignment. Their consistency proves sufficiency under arbitrary global pad reuse.

For necessity start with any satisfying assignment, retaining its actual pad values. If $J=1$, take $k$ one past the **last true boundary**. There is such a cut since $x_0=1$ and $x_r=0$. The original values at the cut are $1,0$, and every original $x_i$ for $i\ge k$ is zero. Each indicated $J\to x_i$ is already false in this very assignment. Each ordinary branch at the cut likewise has exactly one false occurrence according to its own middle value. The retained pads therefore meet all requirements. Earlier boundaries may now be filled with ones. If $J=0$, take $k$ to be the **first false boundary**. All $x_{i-1}$ for $i\le k$ were true, so every indicated incoming occurrence into $J$ was already false. The two cut boundary values and the ordinary middle choices give the same argument. Later boundaries may now be filled with zeroes. This proves existence of a normalized assignment with the original values of all shared pads.

The directions can matter even for the same original boundary values $1,0,1,0$. With $J$ in the first position of every stage, enforce only $x_0\to J$ and $J\to x_2$ along with the endpoints. These values have a model, and normalization has to retain $x_2=1$. Instead enforce only $x_1\to J$ and $J\to x_3$ along with the endpoints. The same boundary values again have a model, but normalization has to retain $x_1=0$. The two legal normalized patterns are respectively $1,1,1,0$ and $1,0,0,0$.

## Linear sweeps and assignment construction

Test $J=1$ by moving $k$ from $r$ down to 1. Before testing a cut, add the demands of its outgoing $J$ occurrences to the demands already held from later stages. For $J=0$ use a fresh collection, move $k$ from 1 up to $r$, and add its incoming $J$ occurrences. At a cut try the at most four ordinary-branch combinations, temporarily adding and removing at most two demands per trial.

For each indexed pad keep the two demand multiplicities. Keep a count of impossible demands and of pads with positive multiplicity on both sides. Adding or removing one demand updates these counts in constant time. A candidate works when both conflict counts are zero. One pass over the switch groups decodes the demands. Each of the two sweeps has constant work per stage. The counters, source choices and output use $O(r)$ words. Indexing arbitrary external names is a separate input operation.

For the first successful trial, assign each demanded pad its required value and choose zero for free pads. Use the cut and the recorded ordinary breaks to fill every boundary and middle as above. Complete each endpoint's two private pads as in the first step. For every padded slot, set just one witness true, choosing a position with its switch off or with its literal true. Such a position exists by the construction and all remaining witnesses can be zero. This explicitly extends the supplied switches to a satisfying assignment of every strict clause. If both sweeps fail, necessity rules out every assignment.

## A minimal interaction between two identifications

Take $r=2$, identify $a_1=a_2=J$, and use one pad $z$ for the two outgoing occurrences $J\to x_1$ and $J\to x_2$. All other implication pads are private. Enforce both endpoint units, the incoming $x_0\to J$, and the ordinary branch $x_1\to b_2\to x_2$. For the two outgoing occurrences activate just $D_{J\to x_1}\lor z$ and $D_{J\to x_2}\lor\neg z$, respectively. Leave the $b_1$ branch and the incoming $x_1\to J$ off. The number of on switches is $2\cdot12+3\cdot6+2\cdot3=48$.

We have $x_0=J=1$ and $x_2=0$. At $z=0$ the first outgoing occurrence forces $x_1=1$, whence the ordinary second branch forces $x_2=1$. At $z=1$ the second outgoing occurrence directly forces $x_2=1$. Splitting $J$ alone restores SAT: take $z=1$, $a_1=1$, $a_2=0$, and $x_1=b_2=0$. Splitting $z$ alone also restores SAT: take the first outgoing pad one and the second zero. Both outgoing occurrences may now fail with $J=1$ and $x_1=b_2=x_2=0$.

All 48 on switches are essential. Removing an endpoint switch permits a constant source assignment. Removing one switch from either singly active outgoing slot permits both outgoing occurrences to fail by choosing the pad to disable the other one. Damaging the incoming $x_0\to J$ lets its private remaining signed pad literal absorb a false implication, so choose $J=0$ and all boundaries after $x_0$ false. Damaging either edge of the ordinary second branch allows that edge to fail using its private pad. Choose $z=0$ and $x_1=1$, then choose $b_2$ according to which edge must break. Since further switch deletions only weaken constraints, every proper subset of the 48 is satisfiable. On the corresponding guard-only projection the unique forbidden vector is all ones, because all other switches may be set to zero.

## Nearest known result

Repeated Boolean literal labels on paths and switching networks have a classical semantics once the labels receive fixed values. Shannon's relay calculus treats series and parallel composition, and Jukna describes the use of repeated tests in switching networks and branching programs. Here padding is existentially chosen, so the closure must respect every shared occurrence of the same pad. The local result is the two complete cut normal forms, the linear literal-demand sweeps, the strict assignment construction and the minimal interaction above. The theorem is restricted to positive identification of at most one middle name and private endpoint padding, switches and witnesses. [Shannon, relay and switching circuits](https://dspace.mit.edu/entities/publication/2dffdeb7-2862-4575-8a8e-b29fb59319e5) · [Jukna, switching-network definitions](https://www.numdam.org/item/ITA_1995__29_1_75_0.pdf) · [Independent-padding predecessor](../../UNSIGNED-ROUTE-JOINS-20261115-001B/UNSIGNED-ROUTE-JOINS-20261115-001B-P001_joined_reachability/proof.md)

The [checker](check.py) constructs full assignments, compares the sweeps with direct Boolean models and a raw SAT solver, and checks each deletion from the 48-switch example. In its four-switch restriction it fixes the other 44 on switches and leaves the original off switches off. The computed 15 feasible rows pass the canonical forgetting test. The raw replay uses PySAT from the current interpreter or the repository environment and reports zero oracle cases if neither provides it. [Recorded results](checks.json)
