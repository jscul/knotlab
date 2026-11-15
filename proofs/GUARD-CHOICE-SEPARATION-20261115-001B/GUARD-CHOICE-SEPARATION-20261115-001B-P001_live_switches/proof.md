# One guard changes whether a shared middle is needed

Status: Proved

## Standard statement

Cut a positive two-route serial instance between two **complete stages**. Write $x,b,z$ for the two outer boundaries and their common cut boundary. Splitting a hidden name gives its right-hand occurrences a fresh name everywhere in that interval. Its left-hand occurrences keep their identity. The raw clauses, the literal signs and all visible guard values are otherwise identical. Compare the sets of allowed triples $(x,b,z)$ after existentially quantifying every other hidden variable. The initial positive and final negative units can then be activated to test ordinary SAT. Before testing the full boundary table, their private guard groups are off.

There is a fixed two-stage layout with one shared positive middle $J$ and otherwise private names where **one raw switch** toggles whether splitting preserves every triple. Both local occurrences constrain $J$ in the safe instance. One safe setting needs different common values at different triples. A second safe setting has a satisfying assignment with both endpoint units active and with each local interval separately forcing the same value of $J$. In this second setting turning on one guard changes the joined ordinary decision to UNSAT while the split instance stays SAT.

More generally, with just one positive middle name spanning a cut, the only triples that splitting can add are $100$ and $110$, in the order $(x,b,z)$. All other middle and pad names may be reused internally. If **only padding names** span the cut, splitting any or all of them preserves *every* boundary triple. This latter assertion allows an arbitrary number of crossing pads and arbitrary reuse within either side.

## The original clauses and the one-switch examples

Each signed padded slot on $L_1,L_2,L_3$ consists of a witness disjunction $w_1\lor w_2\lor w_3$ and three clauses $\neg e_j\lor\neg w_j\lor L_j$. With all three guards on, the slot permits precisely the assignments making a literal true. With an off guard, its witness may be set true and the other two false. An implication $D$ has two slots, $D\lor\neg p$ and $D\lor p$. Both complete guard triples enforce $D$. With a private pad, one missing guard suffices to release $D$ completely, since the pad can satisfy the other half. An endpoint unit has four signed slots on two private pads and is enforced when all twelve guards are on. All these completions use the original hidden variables of their slots. The formulas below have 96 raw ternary clauses and 72 private guard bits. [Guarded two-route construction](../../TWO-RELAY-PADDING-20261115-001D/TWO-RELAY-PADDING-20261115-001D-P001_nested_pair_grouping/proof.md)

Use upper middle $J$ in both stages and a different private lower middle in each. Give the two branches per stage their usual positive implications. Use private pads on all eight implications. Disable both lower branches. In the split comparison write $J_L,J_R$ for the separate upper middles. Begin with the four upper implications

$$
x\longrightarrow J_L\longrightarrow b,\qquad b\longrightarrow J_R\longrightarrow z.
$$

Let $u$ and $v$ be the first guards in the negative-pad slots of the left and right *outgoing* upper implications. All other upper guards are on. The checker uses zero-based raw indices 30 and 54 for $u,v$. The same physical wiring realizes all three rows.

| Raw bits $(u,v)$ | Projected split relation | Projected joined relation |
| --- | --- | --- |
| $(1,1)$ | $x\le b\le z$ | $x\le b\le z$ |
| $(0,1)$ | $b\le z$ | $b\le z$ and $x\le z$ |
| $(0,0)$ | Every triple | Every triple |

For $(1,1)$ the left set of feasible middle values is $[x,b]\cap\{0,1\}$ and the right set is $[b,z]\cap\{0,1\}$. On every split-feasible triple they share the value $J=b$. On $000$ both sides force zero. On $111$ both force one. Thus both occurrences are locally essential and no single common value works on all admissible triples.

Turning $u$ off gives $(0,1)$. The split permits $x=1,b=0,z=0$ by choosing $J_L=1$ and $J_R=0$. The joined assignment would require both values of the same name. This is the only lost triple. Activating the same two endpoint units on both raw formulas forces $x=1,z=0$. The joined formula is UNSAT and the split formula is SAT with $b=0$. Releasing the endpoint units lets both instances use uniform route signals and restores ordinary satisfiability to both.

Instead turn $v$ off in this last setting. At $(0,0)$ both remaining implications point into their respective copies, $x\to J_L$ and $b\to J_R$. A common $J=1$ works everywhere. With both endpoint units active the triple $110$ is still feasible, and **both** local sets are precisely $\{1\}$ there. Turning $v$ on again changes the joined decision from SAT to UNSAT, while the split retains a satisfying triple with $b=0$. Two stages are the minimum for two nonempty whole-stage intervals, and one changed guard is the minimum positive Hamming distance. The two safe settings answer different local questions about essentiality and a globally fixed witness.

## Which middle conflicts can matter

For one side with endpoint values $a,d$, let $W(a,d)$ be its set of permitted values of the single shared middle before gluing. For all supplied internal guards,

$$
0\in W(0,0),\qquad 1\in W(1,1),\qquad W(0,1)=\{0,1\}.
$$

To prove the first two inclusions fill all local route signals with the common endpoint value. For endpoints $0,1$, choose either value of $J$ and give every interior boundary and every middle this value. Each positive implication holds, at the two terminal stages as well as inside. Any pad values are then valid and every raw slot has a witness. Local sharing of other names is compatible with these assignments.

A joined triple exists exactly when the local value sets intersect. Split feasibility needs only nonempty sets on both sides. At $000$ or $111$ the two sides have a common constant. Each of $001,010,011,101$ has a local endpoint pair $01$, making that side free to match any value supplied by the other side. This proves the two-triple bound. At either possible conflict the left set must be $\{1\}$ and the right set $\{0\}$. In $100$ the right set contains zero; in $110$ the left set contains one. Activating endpoint units intersects either relation with the corresponding restrictions on $x,z$. An unsafe trace changes the decision with opposite endpoint units exactly when no joined triple with these endpoints survives.

In the useful special case where **every implication pad is private**, any lost triple changes this ordinary endpoint decision. Eliminating the private pads gives a fixed directed graph of the enabled positive implications in each interval. For a lost triple, the left interval forces $J_L=1$ and is otherwise feasible. If $x$ did not reach $J_L$, setting true exactly the vertices reachable from the pinned true left boundaries would give $J_L=0$. The left terminal boundary $b$ has no outgoing implication within that interval and cannot itself force $J_L$. Thus $x$ reaches $J_L$. Similarly $J_R$ must reach $z$. If it did not, setting false precisely the vertices that can reach a pinned false right boundary would permit $J_R=1$. The right initial boundary $b$ has no incoming implication there. Joining $J_L$ to $J_R$ therefore enforces $x\to z$, ruling out both choices of $b$ at opposite endpoints. The split already supplies the offending triple. The argument uses the fixed implication graphs furnished by private pads.

## Why a cut crossed only by pads separates

Fix a split-feasible triple. At least one of $x\le b$ and $b\le z$ holds for Boolean boundaries. On a side with nondecreasing endpoints, *any simultaneous assignment to its padding names* extends to a satisfying assignment. Set every interior boundary and every middle to the initial boundary value of that side. All implications then hold, including those entering the final boundary. The padding values can be chosen independently of these implications. Complete the original clause witnesses as above.

Keep a solution on the other side. Give the nondecreasing side exactly the preserved solution's values on every crossing pad whose equality is required. Its completion introduces no conflict on any middle, since none crosses the cut. This constructs a joined solution with the requested triple and works for any subset of crossing padding equalities. At every split-feasible triple one entire local pad support is free. Splitting always preserves a joined solution in the forward direction. Applying identical endpoint guard settings preserves the equality of projected relations.

The pads on different intervals can still matter locally. For one crossing incoming pad in two stages, keep the outgoing upper implication fully active on each side. Choose opposite single incoming halves so that descending local endpoints require pad value one on the left and zero on the right. These opposite requirements cannot both occur in one triple, since the common boundary would need to be both zero and one. For a matched control, also share a positive middle $J$. Enable $x\to J$ and a private second-stage chain $b\to K\to z$ unconditionally. Enable $J\to b$ on the left only at $p=0$, and $J\to z$ on the right only at $p=1$. Leave all other implications off. With the two endpoint units on, either value of a joined $p$ forces $z=1$, contrary to the negative unit. Splitting just the pad permits $p_L=1,p_R=0,J=1,b=K=z=0$. This keeps the middle identity and the original guard settings.

## Nearest known result

The earlier adjacent-stage identification already found 39 of 256 enabled-implication masks where identifying two middles changes the opposite-endpoint decision. Its directed-reachability explanation supplies the historical baseline. The present contrast uses raw guard settings that differ in one bit on the same wiring, classifies the triples lost before the cut value is forgotten, and identifies an entire class of pad-only cuts on which splitting preserves the full projection. Fagin's classical lossless-join principle supplies relational background. The uniform positive-route completion above is a direct proof. [Adjacent-stage identification](../../UNSIGNED-ROUTE-JOINS-20261115-001A/UNSIGNED-ROUTE-JOINS-20261115-001A-P001_single_join_census/proof.md) · [Fagin, *Multivalued Dependencies and a New Normal Form for Relational Databases*](https://research.ibm.com/publications/multivalued-dependencies-and-a-new-normal-form-for-relational-databases)

## Replay

The literal-CNF checks independently solve joined and split instances with the same guards and pins using PySAT. Every positive model in the featured switch controls and larger cases is also evaluated against its actual ternary clauses. Of the 256 private-pad implication masks on the upper-middle wiring, 217 preserve every triple, 15 lose only $100$, 15 lose only $110$, and 9 lose both. All 39 unsafe masks change opposite-endpoint SAT. The raw one-pad comparison covers 1,024 effective masks. Direct enumeration of the four-valued guard flags on all eight implication positions covers 65,536 masks with four pads shared across the cut, making 524,288 triple comparisons. The larger raw checks reach ten stages and allow repeated names within each side. A separate AI reviewer in the same task reconstructed local essentiality and the complete-stage restriction. These finite replays have V1 provenance. This splitting theorem preserves the work of solving the remaining local relations as a separate question. [Checker](check.py) · [Results](checks.json)

