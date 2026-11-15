# Exponentially many overlapping obstructions with a linear decision procedure

Status: Proved

## Standard statement

For each $r\ge 1$ there is a fixed, explicit strict 3-CNF system with $24r+24$ public Boolean switches. The unpinned relation on those switches has exactly $2^r$ minimally constrained supports under forgetting (K1–K3). Each contains $12r+24$ switches. Their common intersection consists of 24 switches. Every CNF in just the switches defining this relation requires at least $2^r$ clauses, and that number suffices. In contrast, deciding a specified switch vector takes $\Theta(r)$ deterministic bit probes in the worst case. It has an $O(r)$-size, $\Theta(\log(r+1))$-depth bounded-fan-in circuit. All inputs, bounds and asymptotics here refer to this explicit family.

A support is minimally constrained when its full projection is a proper nonempty subset of the Boolean cube and forgetting any coordinate makes the remaining projection full. All projections in this proof existentially quantify the other variables. A switch value supplied for the later decision is an ordinary input. The projection statements concern the system before any such values arrive. We make no claim of independently constructed recurrences, native composition or a global solver bound.

## Nearest known result

García de la Banda, Stuckey and Wazny give the example of two alternative two-equation routes per stage and contradictory endpoints, with one minimal unsatisfiable subset per route (Example 3). The exponential mechanism is known. Clause selectors are also standard in minimal unsatisfiable subset extraction. Here the routes use directed Boolean implications; the local calculation is their exact transfer to strict ternary clauses, the complete switch relation, the count of overlapping joint constraints and its flat CNF size versus parallel depth and sequential work. [Original two-route example](https://doi.org/10.1145/888251.888256) · [Selector variables and MUS extraction](https://www.mancoosi.org/papers/sat11-mus.pdf)

## The fixed system

Use endpoint units $x_0$ and $\neg x_r$. At stage $i$ use the implications $x_{i-1}\to a_i\to x_i$ and $x_{i-1}\to b_i\to x_i$, with both middle variables fresh at every stage. The four implications at a stage are four *separately* imposed binary clauses. The directed graph here is the conventional representation of these implications.

Replace each binary clause $D$ by $(D\lor u)$ and $(D\lor\neg u)$ for its own fresh bit $u$. Replace each unit $d$ by all four clauses $d\lor (\pm u)\lor(\pm v)$ on two fresh bits. Each resulting clause has three distinct variables. Any proper subset of a padding group allows a padding assignment even when its source clause is false, since the selected clauses exclude only their own distinct padding assignments. A complete group enforces the source clause.

For each of the resulting $8r+8$ strict clauses $L_1\lor L_2\lor L_3$, use fresh witnesses $w_j$ and switches $e_j$, and impose
\[
(w_1\lor w_2\lor w_3)\quad\land\quad
\bigwedge_{j=1}^3(\neg e_j\lor\neg w_j\lor L_j).
\]
When some switch is off, choosing its witness true and the other witnesses false satisfies the slot for any three literal values. With all three switches on, some literal must hold and any true literal supplies a witness. Private variables of different slots are disjoint. Thus for every switch assignment a source implication (respectively endpoint unit) is in force precisely when all six (respectively twelve) of its switches are on. This also realizes a restriction of the larger universal template by leaving every other slot off. The standalone family and its input vector have linear size in $r$ when slots are named by their fixed order.

## Decision

A contradiction occurs exactly when both endpoint units are in force and every stage has at least one complete two-implication branch. In that case the positive endpoint entails the final endpoint, which is required false. When the positive unit is absent, all originals can be false. When the negative unit is absent, they can all be true. When both are present and a stage is broken, assign true to precisely the variables reachable from $x_0$ through live implications. That assignment satisfies the final negative unit and every implication. The private padding and witnesses extend it by the preceding construction.

Scanning each constant-size block and combining these tests costs $O(r)$ bit operations. A fan-in-two circuit computes all stage answers with constant depth and total linear size, then takes their balanced conjunction with the endpoint tests.

## Exact overlap and cost of listing it

For each choice of one branch per stage let $R$ contain all switches for the two endpoint units and for the chosen two implications at every stage. Turning on exactly $R$ causes a contradiction; turning off any one member breaks its unique live route. Every contradicted setting contains such an $R$. Hence these are exactly the minimal unsatisfiable sets of enabled switches. There are $2^r$. Each has $24+12r$ elements. The common intersection has 24 elements because each branch can be avoided at its own stage.

For any set $U$ of switch variables, all the unobserved switches can be turned off. Therefore $U$ is constrained exactly when it contains a whole $R$, and $U$ is minimally constrained precisely when $U=R$. On each such $R$ the only forbidden joint state is the string of all ones. Forgetting any switch permits the zero choice and yields the entire remaining cube. Some state is allowed. This proves K1–K3 on the actual state relation.

Writing one all-negative clause on each $R$ defines the entire projected relation. To see that no CNF over the same public switches can use fewer clauses, consider the $2^r$ assignments that turn on exactly one minimal $R$ each. A clause false on two such assignments would also be false on their coordinatewise minimum: every literal false in both is still false there. That minimum is a proper subset of a minimal obstruction and is satisfiable. Thus one clause can exclude at most one of the $2^r$ selected assignments. This bound allows positive literals too. Naming intermediate results by auxiliary Boolean variables permits short descriptions.

The canonical negative clauses also minimize the total number of literal occurrences. A clause false on the minimal $R$ must contain the negative literal for each switch in $R$. Otherwise it would remain false when that switch alone was turned off, which makes the instance satisfiable. The exact minimum is $(12r+24)2^r$ literal occurrences.

Dually there are exactly $24+144r$ inclusion-minimal sets of switches whose zero settings guarantee satisfiability. Each of the 24 endpoint switches works on its own. With the endpoints intact, guaranteeing a break requires disabling both branches of at least one stage; otherwise choose one untouched branch per stage and turn on a full route. At each stage either branch has 12 switches and choosing one from each gives $12^2$ two-switch certificates.

On the activation vector for any one minimal $R$, flipping any of its $12r+24$ ones changes the answer. There is also an exact worst-case lower bound of **all $24r+24$ input bits**. Answer every endpoint probe with one. Within each stage answer one until a branch is fully queried. Answer zero on the last bit of whichever branch finishes first, and one throughout the other branch. Until both branches finish, the stage still has a completion of either value. All finished stages are live, and any incomplete endpoint can also take either value. Thus before the last distinct input bit, the observed answers admit both satisfiability outcomes. Reading the input once meets the bound. This argument allows adaptive probe order and arbitrary computation between probes.

Every input bit affects the answer on some assignment (select a route through its branch). A fan-in-two circuit of depth $h$ can depend on at most $2^h$ bits. Its depth is at least $\lceil\log_2(24r+24)\rceil$, matching the logarithmic order of the balanced computation. The bit-query bound charges single-bit access. A packed machine instruction can read several bits.

Already the restricted relation on $R$ has $2^{|R|}-1$ states. A nonempty affine Boolean system and any projection of it have a power of two states. Thus auxiliary XOR equations alone cannot describe that exact observable relation. Three permitted states, each with a different one of three distinct switches off, have the forbidden state as coordinatewise majority. This also excludes an existential 2-CNF definition: every binary clause is majority-closed and witnesses can be taken coordinatewise under majority. The displayed decision scan still works.

## Checks

The standard-library checker exhausts all source activation masks for $r=1,2,3$, independently checking satisfiability by simultaneous truth assignments. The masks number 64, 1,024 and 16,384, with 2, 4 and 8 minimally inconsistent subsets. Literal switch and padding truth tables are verified separately. At eight stages it checks the 256 obstructions, 120 bits per obstruction, 24 bits in all of them, and the 1,176 minimal zero certificates. The optional PySAT replay tests 1,215 complete activation vectors on the original guarded strict CNF, including individual switch deletions. Its four-switch slice of a minimally inconsistent setting has 15 feasible assignments, which the canonical knotlab forgetting check accepts. The all-$r$ conclusion follows from the argument above. [Checker](check.py) · [Checked values](checks.json)

Run `python3 -B check.py` from this directory. For raw CNF replay use the repository's Python environment with `check.py --with-solver`. The proof measures decision on the supplied activation vector, not formula compilation from arbitrary SAT.
