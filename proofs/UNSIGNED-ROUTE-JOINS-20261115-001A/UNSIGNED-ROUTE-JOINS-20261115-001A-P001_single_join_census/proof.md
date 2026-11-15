# One middle identification changes the minimal switch supports

Status: Proved

## Standard statement

Take $r\ge1$ stages with endpoint units $x_0$ and $\neg x_r$. Stage $i$ has four independently enabled Boolean implications, in the order $x_{i-1}\to a_i$, $a_i\to x_i$, $x_{i-1}\to b_i$, $b_i\to x_i$. Identify exactly two distinct middle variables among the $2r$ names $a_i,b_i$. Keep each implication occurrence, padding bit, witness and switch separately named. A minimal switch support is an inclusion-minimal set of switches whose ones already force unsatisfiability.

Write $d$ for the difference of the two stage indices. Each row counts supports for one fixed choice of the identified pair. A full route uses $2r$ implications and its support has $24+12r$ switches.

| Identification | Old supports still minimal | Old supports now nonminimal | New minimal supports | Switches in each new support |
| --- | ---: | ---: | ---: | ---: |
| Same stage, $d=0$ | $2^r$ | $0$ | $2^r$ | $24+12r$ |
| Adjacent stages, $d=1$ | $3\cdot2^{r-2}$ | $2^{r-2}$ | $2^{r-2}$ | $24+12(r-1)$ |
| Stages $d\ge2$ apart | $3\cdot2^{r-2}$ | $2^{r-2}$ | $2^{r-d-1}$ | $24+12(r-d)$ |

Distinct stages require $1\le d\le r-1$. At adjacent stages the *number* of minimal supports stays at $2^r$, although the decision and the support sizes both change. Two stages already give three old supports of size 48 and one new support of size 36. The old stage-by-stage scan misses 39 contradictions among the 256 settings of the eight implications with both endpoint units active.

## Nearest known result

Kleine Büning gives the unjoined directed Boolean construction in §5, Fig. 2, with a choice between two implication chains at each stage and exponentially many minimally unsatisfiable subformulas. García de la Banda, Stuckey and Wazny give an earlier equality-constraint analogue in Example 3. The preceding project result transfers the unjoined construction to strict ternary clauses with independent switches. This proof computes the change caused by one identification, including the old supports that lose minimality and the exact assignments on which the old scan fails. [Kleine Büning (2024)](https://doi.org/10.1016/j.tcs.2024.114538) · [García de la Banda, Stuckey and Wazny (2003)](https://doi.org/10.1145/888251.888256) · [Predecessor synthesis](../../SIGNED-KNOT-OVERLAP-20261114-001Z/SIGNED-KNOT-OVERLAP-20261114-001Z-P001_synthesis/proof.md) · [Unjoined switch construction](../../SIGNED-KNOT-OVERLAP-20261114-001C/SIGNED-KNOT-OVERLAP-20261114-001C-P001_many_easy_obstructions/proof.md)

## From raw switches to simple paths

A source implication $D$ contributes the padded pair $D\lor u,D\lor\neg u$ on a fresh $u$. A unit contributes all four choices of signs on its two private padding bits. A strict clause with literals $L_1,L_2,L_3$ becomes the four clauses

\[
(w_1\lor w_2\lor w_3)\quad\land\quad
\bigwedge_{h=1}^3(\neg e_h\lor\neg w_h\lor L_h).
\]

With all three switches on, this slot can be satisfied exactly when some $L_h$ holds. With one switch off, its witness alone can be set true for any literal values. If a padded group is incomplete, its padding bits can take a pattern excluded only by an absent clause. Thus a source implication is active exactly when all six switches in its block are on. Each unit requires all twelve. This reduction holds for each assignment of the public original variables, so it also holds under the stated identification. It gives $24+24r$ switches.

Use the classical directed graph of the active implication occurrences, retaining parallel occurrences. Both endpoint units together with a directed path from $x_0$ to $x_r$ give a contradiction. If a unit is absent, an all-false or all-true assignment works. With both units present and no path, set exactly the variables reachable from $x_0$ true. Every implication is satisfied and $x_r$ is false. The padding and witnesses extend these assignments.

Every directed walk joining the endpoints contains a simple path, obtained by deleting repetitions. The occurrences of a simple path alone contain a unique route between the endpoints, so removing any one of them destroys it. Consequently the inclusion-minimal contradictory source sets consist exactly of the two units and a simple occurrence-labelled path. Their minimal switch supports contain both unit blocks and all six switches of each path occurrence. An incomplete extra block contributes nothing to minimality. In the unpinned projection onto any such support, all tuples except its all-one tuple extend, since the outside switches may be set to zero. Conversely any constrained switch projection contains one of these supports, by turning every omitted switch off.

## Counting the simple paths

In the unjoined system there are two branch choices per stage. Joining $a_i$ and $b_i$ makes both incoming occurrences end at the same variable and both outgoing occurrences start there. Any incoming choice can now be paired with any outgoing choice. The four locally distinct ordered pairs give $4\cdot2^{r-1}=2^{r+1}$ simple paths. Exactly half use their original pairing. Parallel occurrences at this stage have distinct switch blocks even when they express identical implications.

Now join one middle at stage $i$ with one at stage $j>i$, and call the shared variable $z$. An old route that uses both selected middles visits $z$ twice. There are $2^{r-2}$ such routes. All other old routes remain simple. A new simple path enters $z$ via the incoming occurrence at $i$ and leaves via the outgoing occurrence at $j$. It uses one of two branches at each of the $i-1+r-j=r-d-1$ outside stages, and neither chooses nor visits an intervening branch. Its length is $2(r-d)$.

These exhaust the possibilities. A simple path sees $z$ at most once. Using the incoming and outgoing occurrences of the same stage gives an old route. Entering at $j$ and exiting at $i$ cannot work. Before its first visit to $z$ the path advanced stage by stage, so it already passed $x_i$, which the proposed exit immediately revisits. Finally, each old route visiting $z$ twice contains a unique new shortcut, obtained by deleting the walk from its first visit to its second. Each shortcut occurs in $2^{d-1}$ such old routes, one per choice of the original branches strictly between $i$ and $j$. This establishes every entry of the table.

## Counting the wrong answers

The old scan returns UNSAT when both units are active and every stage has an intact original branch. Every such route survives as a walk under identification, so the only possible error is a SAT answer on a joined UNSAT formula. Each stage has four independent implication activations. Of its 16 settings, seven have an intact branch. With both endpoints active there are $16^r$ possible source masks. Counting the two endpoint activations as independent inputs gives $4\cdot16^r$ masks. The error numerator is identical for both denominators.

At a same-stage join, any active incoming and any active outgoing suffice. This gives nine of 16 local settings, adding two to the old seven. All other stages must work. The number of missed contradictions is $2\cdot7^{r-1}$.

For $d\ge1$, the joined formula is also contradictory when each outside stage works and the earlier selected incoming occurrence and the later selected outgoing occurrence are both active. These conditions give a shortcut. There are $8^2 16^{d-1}$ settings inside the joined interval satisfying them. Conditional on its required occurrence being active, either boundary stage has five of eight settings with an original branch. Four have the same-branch partner active, and one has that partner off and the other branch completely on. All $d-1$ intervening stages would also have to work for the original scan. Subtracting this overlap gives the error count

\[
 7^{\,r-d-1}\bigl(64\,16^{d-1}-25\,7^{d-1}\bigr).
\]

Adding $7^r$ gives the total number of joined UNSAT source masks. At the first possible sizes, the same-stage, adjacent and separated identifications miss respectively 2 of 16, 39 of 256 and 849 of 4,096 masks with both units active.

Raw switch assignments give incomplete blocks greater weight. Write $c=64$ for the settings of a six-switch implication block. Only one activates it. An unaffected stage works in $p=2c^2-1$ settings. With one specified occurrence already active, the same stage works in $q=c^2+c-1$ settings. These follow by counting the settings with either complete branch and subtracting their intersection. At a same-stage join the two crossed pairings each require the two other occurrences to be inactive. The corresponding raw error count is $2(c-1)^2p^{r-1}$. At distinct stages it is

\[
 p^{\,r-d-1}\bigl(c^6(c^4)^{d-1}-q^2p^{d-1}\bigr).
\]

The two active endpoint blocks have exactly one raw realization each. The two raw error numerators therefore apply among all $2^{24+24r}$ switch vectors, or among $2^{24r}$ with both endpoint blocks stipulated on. Substituting $c=2$ instead recovers the source counts. At one stage the raw error numerator is 7,938.

## Smallest incorrect decision on the strict CNF

At $r=1$, set both endpoints and just $b_1$'s incoming occurrence and $a_1$'s outgoing occurrence active. Before identification, $x_0=b_1=1$ and $a_1=x_1=0$ extend. Afterwards the incoming implication forces the shared middle true and the outgoing implication forces it false. In the four-bit implication order above, with the first occurrence least significant, the only erroneous masks are 6 and 9. Mask 6 is the first.

Number the raw switches from zero in block order $\bigl(x_0,\neg x_1,a\text{-in},a\text{-out},b\text{-in},b\text{-out}\bigr)$. Set positions $0$–$23$ and $30$–$41$ on and every other position off. The unjoined strict CNF is satisfiable and the joined strict CNF unsatisfiable on this same 48-bit vector. Each of the 36 individual deletions restores satisfiability. Every contradiction needs both 12-switch endpoint blocks and at least two separate six-switch implication blocks, proving minimality also by cardinality over the entire family. Fixing all but positions $0,12,30,36$ as in this vector leaves 15 allowed four-bit tuples. The checker submits the table observed on the actual clauses to the canonical K1–K3 forgetting test. The four-bit statement uses this fixed restriction. The uniform counts concern unpinned minimal supports.

## Reproduction and scope

Run the following command from this family directory. The default replay uses the repository Python environment for PySAT and prints the recomputed counts in a JSON object.

~~~sh
python3 -B check.py
~~~

One calculation enumerates simple paths on occurrence-labelled implications. A second enumerates original Boolean assignments with both endpoints forced and collects all subsets of the implications each assignment satisfies. It extracts the inclusion-minimal impossible masks directly. A constant witness covers all subsets for each of the other three endpoint settings. The two calculations agree on every identification through four stages, totaling 50 layouts and 7,592,000 source activation vectors. The fourth-stage counts by $d=0,1,2,3$ are 32, 16, 14 and 13 minimal supports. Their corresponding scan errors per layout are 686, 1,911, 5,943 and 15,159. Direct path enumeration also checks all 202 further labelled joins at five, six and seven stages.

Independently, the checker renames the one middle in the predecessor's fully expanded strict clauses and passes the clauses to a SAT solver. At every layout with one or two stages it tests two raw representatives of every source setting, totaling 12,416 solver comparisons. The two representatives use different completions of inactive blocks when available. It also verifies 53 new minimal supports on the literal CNF and all 2,736 individual deletions, including same-stage, adjacent and distant cases at six stages. The all-$r$ conclusions follow from reachability and the counting argument. They concern this one-identification family and its specified scan. [Executable checker](check.py) · [Finite counts](checks.json)
