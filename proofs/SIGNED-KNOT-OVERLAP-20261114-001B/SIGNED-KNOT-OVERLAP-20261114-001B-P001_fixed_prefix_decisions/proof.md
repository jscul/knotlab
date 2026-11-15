# Completion decisions for a fixed family of ternary knots

Status: Proved

## Standard statement

For every $n\ge3$ there is a uniformly constructible Boolean rule system on $n$ public choices and six private choices for each of $m=8\binom n3$ slots. The entire system, including every literal sign, is fixed by $n$. A later input selects slots by supplying switch values and can pin a consistent partial assignment of the public choices. Deciding whether a state extends these pins is NP-complete over varying $n$. A system with aligned signs on the same scopes admits a monotone completion algorithm. A system with one affine equation on each of the same scopes admits Gaussian elimination.

Before pins, all three have exactly the same supports of ternary K1–K3 relations. On each such support the signed and aligned systems allow seven assignments, and the affine system allows four. Every other triple is unconstrained. On just the independently named guard bits, the signed system also has projections of unbounded arity missing exactly one assignment. Their supports correspond exactly to inclusion-minimal unsatisfiable sets of source clauses.

## Fixed rules and common input

Enumerate every triple $1\le i_1<i_2<i_3\le n$ and every choice of signs for its literals. A slot $s$ names the clause $C_s=L_{s1}\lor L_{s2}\lor L_{s3}$ on those three different public variables. All slots, including all eight sign choices on every triple, are present for every input of size parameter $n$. Give slot $s$ private Boolean choices $w_{s1},w_{s2},w_{s3}$ and $e_{s1},e_{s2},e_{s3}$. Its rules are

$$
w_{s1}\lor w_{s2}\lor w_{s3},
\qquad
\neg e_{sj}\lor\neg w_{sj}\lor L_{sj},\quad 1\le j\le3 .
$$

The common input menu is a bit $y_s$ per slot and an optional partial assignment $\rho\in\{*,0,1\}^n$ of the public variables. Pin all three $e_{sj}=y_s$ and leave every $w$ unpinned. A question with all public choices free uses $\rho=*^n$. The same menu and named coordinates apply to every comparison below. The signed and aligned algorithms also have the stated meanings if all $3m$ guard bits are supplied independently. The guard-projection theorem below treats them as their original, independent coordinates.

There are $n+6m$ choices and $4m$ rules, all strict ternary. An explicit listing takes $O((n+m)\log(n+m))$ bits with binary identifiers. A dense query takes $m$ switch bits, or $3m$ in the independent version, plus at most $2n$ bits for $\rho$ and an encoding of $n$. No instance-specific sign or rule is supplied. If $n$ and the fixed construction are known to both parties, transmitting this prefix costs zero bits.

## What a slot enforces

Fix public values and the three guards of a slot. If some $e_{sj}=0$, set that $w_{sj}=1$ and the other witnesses to zero. The slot extends for any public values. If all three guards are one, at least one witness must be one and its literal must hold. Conversely one true literal supplies such a witness by itself. Different slots have disjoint private choices. Thus a common state exists precisely when the public assignment can satisfy $\rho$ and every $C_s$ for which all three guards are one.

## Decision complexity and a smallest difference

The admitted source is uniform strict 3-CNF satisfiability with three distinct variables per clause. Parse its formula, compact the variables that occur, and suppress duplicate clauses. Use the fixed prefix at this new $n$ and turn on exactly the matching permanent slots. Return $\rho=*^n$. The slot equivalence preserves the answer in both directions. With $c$ input clauses one needs at most $3c$ public variables, so even writing the dense switch vector takes polynomial time. An empty formula maps to the all-off query at $n=3$. If malformed strings are part of the encoding language they map to the all-on, no-public-pins negative instance described below. These conventions also cover headers that declare many unused variables. A total assignment provides a polynomial-size certificate directly verified against the rules and input pins. Hence this family is NP-complete, already with all public choices free and all three guards in each slot pinned together. [Admitted strict-3-CNF theorem](../../EVIDENCE-001D/EVIDENCE-001D-P001_uniform_strict_3_cnf_sat_completeness_admission/proof.md)

In the aligned control all occurrences of a given public variable have one common polarity. The all-positive choice fixes a particular such control. Give each free public variable the value that makes its common literal true, retaining each pin in $\rho$. This simultaneously maximizes every selected clause. If a selected clause fails, all its variables are pinned against it. If none fails, the computed assignment extends by the slot equivalence. One pass through the variables and slots decides the input. With arbitrary consistent pins on the affine control, including pins on witnesses if desired, adjoin their unit equations and test the resulting binary linear system for consistency by Gaussian elimination.

At $n=3$ select all eight slots and leave the public choices free. Each signed clause forbids a different assignment of the three public variables, so the signed answer is no. The aligned answer is yes, witnessed by $(x_1,x_2,x_3)=(1,0,0)$ and $w_{s1}=1$ alone in each slot. Deleting any selected slot in the signed input restores the assignment that its clause forbids. This test is minimal in $n$ and in the number of selected clauses with no public pins. Three distinct variables are needed for a slot, and any seven strict clauses together forbid at most $7\cdot 2^{n-3}<2^n$ public assignments.

## The entire unpinned ternary support

A support here is a named set of variables whose projected allowed assignments pass the canonical forgetting test. On a ternary support this requires a nonempty proper relation whose projections onto all pairs are full. Each rule has its own distinct support because the witnesses and guards have the declared private identities.

For the signed or aligned system, consider any assignment of at most three choices. A directly falsified rule prevents extension. Suppose it falsifies none. Call a position of a slot touched when the assignment includes its $e$ or its $w$. If every slot has at least one untouched position, at most one position anywhere can have both $e=w=1$ already specified. Make its public literal true if necessary. A conflicting public pin would have directly falsified its guard. Set the remaining unpinned public variables arbitrarily and the unpinned guards to zero. Retain the pinned witness bits, set a witness to one at an untouched position in each slot, and set other unpinned witnesses to zero. This satisfies every rule.

Otherwise one slot has three touched positions. The three pins then consist of one private coordinate per position in that slot. All public variables are free. If a witness was pinned one, select it and set its free guard to zero. If no witness was pinned one, at least one position has its guard pinned and its witness free, since three witnesses pinned zero would have falsified the core. Select one such witness and, if its guard is one, make its literal true. The remaining free witnesses in that slot may be zero. The unpinned slots complete with their guards zero. This proves that every assignment on at most three choices extends exactly when it directly falsifies no rule. All unary and binary projections are full. On each declared triple only its unique forbidden assignment is lost, and every other triple is full. Keeping the named Boolean values reveals which assignment was lost. Keeping only the support and its cardinality does not record that sign information.

For the affine control use $w_{s1}+w_{s2}+w_{s3}=0$ and $e_{sj}+w_{sj}+x_{i_j}=0$ over $\mathbb F_2$. The support proof also works for any fixed right-hand sides. The coefficient rows are independent because each guard row has a unique $e$, and the core rows have disjoint witness supports. Thus every right-hand side is feasible. A projection of the solution set onto $U$ is proper exactly when a nonzero row combination is supported inside $U$. Indeed the projected solution set is a translate of the projected kernel. A linear form vanishing on that kernel lifts to a row-space vector supported inside $U$, and every such vector gives an equation of the projection.

Consider a combination using $r$ guard rows and any core rows. It contains $r$ distinct private $e$ coordinates. With $r=0$, a nonzero combination has weight at most three exactly for one core. With $r=1$, the public bit and guard bit remain. Using the corresponding core leaves two witness bits instead of one, and every unrelated core adds three. Only the original guard has weight at most three. With $r=2$, two different public bits already bring the weight to four. If the public bits cancel, the guards came from different slots, since a slot uses three distinct public variables. Each of those two slots leaves at least one witness bit under either choice of core. With $r=3$, three guard bits remain and three public occurrences leave odd public weight, hence at least one more bit. With $r\ge4$, the guard bits alone suffice. The only nonzero combinations of weight at most three are therefore the original rows. Each named scope has exactly one parity equation on it and allows four assignments. Every other triple and all pairs are full. These claims about knots concern the unpinned systems. [Canonical K1–K3 test](../../../docs/FOUNDATIONAL_THESIS.md#canonical-knot-test)

## What the guards alone constrain

For any subset $U$ of the actual $e$ variables, project the unpinned signed system onto $U$. Each omitted guard can be set to zero, since it occurs only negated. Given a vector on $U$, its full slots are those with all three guards present and set to one. The slot equivalence identifies the projection exactly with satisfiability of this set of source clauses.

It follows that this projection passes K1–K3 if and only if $U$ consists of the three guards per member of some inclusion-minimal unsatisfiable set $F$ of source clauses. Indeed, a forbidden vector's full slots contain such an $F$. If a coordinate of $U$ lies outside its $3|F|$ guards, forgetting that coordinate still leaves a forbidden assignment, violating K2. Conversely suppose $U$ consists of exactly the guards of $F$. All ones is forbidden. Every other assignment removes at least one clause of $F$ from the full slots, leaving a satisfiable set. This relation is nonempty, proper, and full after any coordinate is forgotten.

The eight clauses at $n=3$ form such an $F$. Its guard relation allows $2^{24}-1$ assignments. On the grouped input menu it allows $255$ of $256$ vectors. In comparison, the aligned control allows all of them with no public pins. For the homogeneous affine control, eliminating the witnesses gives $\sum_j e_{sj}=x_1+x_2+x_3$ for each of the eight slots. Thus the eight switch parities must all agree. This allows $2\cdot 4^8=2^{17}$ independent guard vectors or precisely two grouped vectors. No existential system of XOR equations can represent the signed guard relation on these same switches. Projection preserves affineness, and every nonempty affine relation has power-of-two cardinality. This obstruction concerns exact representation with the specified named coordinates. Other reductions and nonlinear algorithms remain possibilities.

The arity grows without bound. Starting with the eight-clause set, replace one clause $A\lor B\lor C$ (signed literals on distinct variables) by

$$
A\lor B\lor t,\qquad \neg t\lor C\lor u,\qquad \neg t\lor C\lor\neg u
$$

with fresh $t,u$. Existentially forgetting $t,u$ restores the old clause. If $A$ or $B$ holds choose $t=0$, and if both fail choose $t=1$, which forces $C$. Deleting an untouched clause leaves an old satisfying assignment that extends through the replacement. For deletion of a new clause, use a satisfying assignment of all old clauses except the replaced one. It falsifies $A,B,C$. Delete the first new clause and take $t=0$. Delete the second and take $(t,u)=(1,0)$. Delete the third and take $(t,u)=(1,1)$. Each satisfies the two survivors. Inclusion-minimal unsatisfiability is preserved. After $r$ replacements there are $8+2r$ strict clauses and a projected relation on $24+6r$ individually named guards missing only the all-ones assignment.

## What is charged

The prefix depends only on public $n$ and has a polynomial-time generator. The varying bits in the NP-completeness reduction are the later pins. This differs from the preceding simultaneous-query problem, where the sender held an arbitrary private table and had to encode answers to all later queries. There the minimum advance message has exponential base six. Here the fixed prefix needs no advance message, yet the uniform later decision is NP-complete. Neither fact supplies an unconditional superpolynomial running-time lower bound for general SAT. Free unbounded advice specific to each $n$ is outside the uniform decision model. [Preceding joint-message result](../../JOINT-BRAID-READS-20261114-001Z/JOINT-BRAID-READS-20261114-001Z-P001_synthesis/proof.md)

## Nearest known result

Feige and Jozeph construct universal factor graphs for 3-SAT. The incidence pattern is fixed and the varying instance supplies polarities. Their Appendix B, Lemma 2, already uses the fixed-prefix mechanism directly. For given numbers of variables and clauses, the gate clauses of a SAT-verification circuit are fixed, and only the polarities of unit clauses supplying the encoded formula vary. Our named switches instead select permanent clause slots in a system with the explicit projections proved above. Schaefer classifies satisfiability for fixed finite Boolean constraint languages as their instances vary, including the tractable affine case. [Feige and Jozeph, Theorem 1 and Appendix B, Lemma 2, pp. 14–15](https://arxiv.org/pdf/1204.6484) · [Schaefer, STOC 1978](https://doi.org/10.1145/800133.804350)

Liffiton and Sakallah use one selector per input constraint to enable or disable it when studying minimally unsatisfiable subsets. Eliminating our witnesses implements a selector that is the conjunction of three named guards. The local claims specify every unpinned ternary projection and identify exactly which actual guards form minimally constrained projections for this construction. We do not claim priority for a general SAT reduction or dichotomy. [Liffiton and Sakallah, §2.2](https://markliffiton.com/publications/jar_liffiton_CAMUS.pdf)

The [checker](check.py) evaluates the fixed inputs and parity combinations, verifies the clause replacement on actual truth tables, and runs the canonical knot checker on the supported relation types and on the eight grouped switches.
