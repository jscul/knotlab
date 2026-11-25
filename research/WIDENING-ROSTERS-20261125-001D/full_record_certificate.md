# An exact certificate for the two complete private records

This is a mathematical test for a future full-cohort check. It contains no cohort measurements. Its population would be every recorded occurrence with an actual shared distinction and two eligible holders under the [source-preserving reading](link_reading.md). The existing bounded representative check keeps its own selection and cutoff.

## Target for one occurrence

Use the complete post-meeting stage under its actual knot law, with formula $F$. Keep the physical $(u,v,c)$ and its incoming route, phase, first-meeting round and split-part provenance. Put

$$
A=P(u)\setminus P(v),\qquad B=P(v)\setminus P(u),\qquad
E=(P(u)\cap P(v))\setminus\{c\},\qquad Q=A\cup B\cup\{c\}.
$$

Let $Z$ contain **every** other variable, including every element of $E$. The exact target is $G(a,b,k)=\exists Z\,F(a,b,c=k,Z)$. Thus the values of an extra shared place must agree at all its holders in a single extension. Eliminating a different copy on each side can change the answer. For an attainable value $k$, denote by $G_k$ the allowed pairs of records and by $A_k,B_k$ its two projections.

The product through $c$ holds exactly when $G_k=A_k\times B_k$ for every attainable $k$. A proper attachment on $A$ requires $\pi_{Ac}G\subsetneq\pi_AG\times\pi_cG$. If $c$ is open this means $A_0\ne A_1$ as sets, irrespective of their cardinalities. Use the same criterion on $B$. A **proper two-sided product** requires all three facts. Report coherence, openness of $c$, product and both proper-attachment verdicts individually. An empty arm has one possible value and cannot be proper. An inconsistent stage supplies no coexisting records.

Different $c$ at the same holder pair give different targets, since the other shared places are hidden. For a common-knot route the same $c$ must be held by the older witness and both endpoints. For a cross take it must be the actual distinction acquired by the newborn from an oppositely descended pre-round holder. A mixed holder descended from both selected parts does not by itself supply two independent roles. Descent from an additional third part is permitted by the registered reading and must remain labelled. The same projection at identical stage, holders and $c$ can serve several route occurrences, which retain their separate source records. No single shared identity, an untested computation, and a failed product are distinct outcomes.

## When the two holder constraints determine the full result

Keep the actual constraints of $u$ and $v$. Remove other constraints one at a time whenever the chosen constraint has a place $z\notin Q$ appearing in no other constraint **still present**. Record the removed constraint and that pivot $z$. A single even-parity constraint can always be satisfied by choosing $z$. A not-all-equal constraint with at least one other distinct place can always be satisfied by choosing $z$ opposite the value of such a place. The physical rows here use distinct places; a repeated literal must not be mistaken for a second place. Unassigned places can be chosen freely when restoring a row. Restore the removed rows in reverse removal order. Their pivots do not occur in the part already restored, so this constructs an extension of every residual solution. Every original solution trivially projects to a residual one. Consequently the operation preserves the exact projection onto $Q$.

A reverse birth order is one way to find pivots. A recorded fresh distinction qualifies only if it is outside $Q$ and is now private to that row. Later takes, multiple holders and a selected endpoint's protected private places can prevent removal. Bars restrict future growth and impose no bit value. A residual group of rows independent of all retained variables can be discarded only after its satisfiability has been certified, or conditioned on every relevant shared bit if there is one.

If only the two protected holder rows remain, let $\sigma(a)$ be the parity of the private record $a$, with empty parity zero. The complete answers follow directly.

| Knot law and other shared places | Exact projected relation after the two-row reduction | Product and attachments |
| --- | --- | --- |
| Even parity, $E$ empty | $\sigma(a)=k$ and $\sigma(b)=k$ | For nonempty arms, product and both attachments proper. |
| Not-all-equal, $E$ empty | $a$ is not the constant record $k$, and $b$ is not the constant record $k$ | For nonempty arms, product and both attachments proper. |
| Even parity, $E$ nonempty | $\sigma(a)=\sigma(b)$, with either value of $k$ | For nonempty arms, product fails at each $k$ and neither arm is proper relative to $c$. If an arm is empty, the other's parity must be zero and the product holds with no proper attachment. |
| Not-all-equal, $E$ nonempty | All $(a,b,k)$ | Product, with no proper attachment to $c$. |

For parity with $E\ne\varnothing$, each holder equates its private parity to $k\oplus\sigma(E)$. Any requested parity for $E$ is available. For not-all-equal, set one extra common place to $1-k$; both holder constraints are then satisfied for all private records. With $E$ empty the excluded opposite combination for a proper attachment can be exhibited explicitly. Under parity choose a record of parity $1-k$. Under not-all-equal choose the constant record $k$. That record occurs with $1-k$, the value $k$ occurs separately, and their combination violates that holder. With the study's three-place minimum, empty private arms cannot occur when $E$ is empty.

The smallest extra-place check uses rows $(a,c,e)$ and $(b,c,e)$. Parity allows only $a=b$ with either value of $c$. Separately forgetting $e$ in each row would incorrectly allow all eight triples. Not-all-equal genuinely allows all eight, by taking $e=1-c$ once in both rows.

**Why checking each holder alone is insufficient.** On two holders $(a,p,c)$ and $(b,q,c)$ add a third constraint on $(a,b,c)$ under the same law. Each holder still has precisely its entire isolated allowed-state table. Under parity, given any first-holder state one can choose $b=a\oplus c$ and then $q=b\oplus c$, and conversely. Under not-all-equal, choose $b=1-c$ to extend any first-holder state, and conversely. Yet the third constraint forbids combinations of two separately allowed records at the same $c$. For example, even parity rejects $(a,p,b,q,c)=(1,1,0,0,0)$, and not-all-equal rejects $(0,1,0,1,0)$. Both arm attachments are proper in these examples. The product must be tested separately.

Some implications survive **without** eliminating the rest of the stage.

* For parity and $E=\varnothing$, an open $c$ already proves both proper attachments. Every record on either side determines $c$ by parity. The whole-stage product still needs checking.
* For parity and $E\ne\varnothing$, the two private parities must always agree. If two full solutions with the same $c=k$ give opposite private parities, crossing their private records yields a forbidden combination. This certifies failure of the product, even in a large residual system. If instead the only achievable private parity differs between $k=0,1$, each attachment is proper. A single private parity seen at each $k$ does not decide the product.
* For not-all-equal and $E=\varnothing$, a full model with a monochromatic private $A$ record, together with openness of $c$, proves that attachment proper. The record and its matching value of $c$ cannot occur together. Test the other side separately. Additional constraints could forbid every monochromatic record, so failure of this sufficient test leaves the attachment unsettled. With $E\ne\varnothing$, a holder alone supplies no such exclusion. The full stage must determine what values the other common places may take.

## Exact parity test by elimination

Let $M$ be the matrix of **all** even-parity equations in the stage, with one column per physical distinction, or an exactly reduced equivalent matrix. Write $d_J=\dim\pi_J\ker M$. For any selected columns $J$,

$$
d_J=|J|-\operatorname{rank} M+\operatorname{rank} M_{\overline J}.
$$

Indeed the dimension of the full kernel is the column count less the rank. Its subspace with $J$ fixed to zero is the kernel on the complementary columns. Subtract their dimensions. This also handles dependent rows and any number of holders of a distinction.

Compute $d_A,d_B,d_c,d_{Ac},d_{Bc},d_Q$ and

$$
\delta=d_{Ac}+d_{Bc}-d_c-d_Q,\quad
\epsilon_A=d_A+d_c-d_{Ac},\quad
\epsilon_B=d_B+d_c-d_{Bc}.
$$

The join of the two projections has dimension $d_{Ac}+d_{Bc}-d_c$. Both arms map onto their common $c$ projection, and one copy of that dimension was counted twice. Inclusion of $G$ in the join now shows that the product holds exactly when $\delta=0$. Each $\epsilon$ is zero or one; it is one exactly for a proper attachment. The homogeneous system has a zero solution; $d_c=1$ means $c$ is open. All counts, if required, are powers of two from these dimensions, with no enumeration of private records. An independent implementation may project a basis of full solutions onto the selected columns and take its rank.

For a checkable nonproduct witness, find an assignment in the joined linear space outside $G$. Keep the separate full-stage linear extensions of its $Ac$ and $Bc$ records and a combination of original rows whose hidden columns cancel and whose visible parity this assignment violates. For a positive verdict the rank equalities, with independently checked row reductions on the same source matrix, suffice.

## Exact and sufficient not-all-equal tests

After safe row removal, fix one value $c=k$. If no connected component of the residual variable-and-constraint incidence contains both a variable of $A$ and a variable of $B$, any admissible $A$ record and $B$ record can be combined: take their solutions on their respective components and extend the remaining satisfiable components. This proves $G_k=A_k\times B_k$. Keep shared hidden variables in the component test. Merely deleting all the common places would amount to giving the two ends independent witnesses. Components may be found after correct simplification with $c$ fixed. In particular a not-all-equal row containing the fixed $k$ now requires at least one of its other places to have value $1-k$. In the actual uniform not-all-equal system global bit complementation exchanges the two $c$ fibers. Once the stage is known satisfiable, a product proof for one fiber transports to the other. This symmetry equates sizes across the two fibers but need not equate the sets of private records.

There is a short positive certificate even if unremoved rows still meet both private records. Protect $A,B,E$ and fix $c=k$. Seek one assignment to all remaining hidden places that gives every nonholder row both a zero and a one among the places whose values are now fixed, including $c$ wherever present. Two ordinary SAT clauses per nonholder row, requiring a fixed zero and a fixed one, suffice for this search. Check the returned assignment row by row. It then satisfies every nonholder row for **every** choice on the protected places, so every jointly allowed assignment of the two holder rows at $k$ extends. Restore any peeled constraints afterward. This proves the exact two-row answer for that fiber. When $E$ is nonempty one may also fix a named $e\in E$ to $1-k$ before the search. This choice already permits every private-record combination in the two holder rows, so a successful certificate gives the full free fiber. Include every occurrence of $e$ at outside holders in the check. A failed search is inconclusive because hidden values might depend on the requested private records.

Another positive certificate is an explicit way to combine any two full solutions with the same $k$. It must keep $A$ from the first, $B$ from the second and $c=k$, and provide one joint assignment for every hidden place. The component argument and the reverse-pivot assignment are simple such constructions. A proposed Boolean circuit giving the hidden values can be verified by testing whether any two admissible input solutions give an output violating even one original constraint. Proved unsatisfiability of that check certifies the product. A failure of that particular circuit only refutes the circuit: another extension of the same records could work.

For a complete decision, let $F(a,b,k,z)$ be the original or exactly reduced stage relation. Failure of the product has the following exact formula:

$$
\exists a_1,b_1,z_1,a_2,b_2,z_2,k:\quad
 F(a_1,b_1,k,z_1)\land F(a_2,b_2,k,z_2)
 \land \forall z\,\neg F(a_1,b_2,k,z).
$$

An ordinary SAT check finds each individual extension or certifies its absence after its records are fixed. Two positive full assignments at the same $c$ and an independently certified impossible crossing prove nonproduct. One counterexample search with no witness found need not prove a product. For an exact positive verdict, use exhaustive projection or an exact quantified solver, or supply a universal construction as above. Exact variable elimination or projected counting over a small residual scope can also decide the equality. Count **distinct private records**, since their numbers of hidden completions can differ. There is no claimed uniform efficiency bound for the not-all-equal decision.

For an attachment, strictness has an analogous witness. Give an allowed $a$ record and its full extension at $k_0$, a model allowing $k_1$, and a proof that $F(a,B,k_1,Z)$ has no solution for any $B,Z$. This compares the attachment with the product of the marginal supports and remains valid with extra shared places, arbitrary routes and unrelated restrictions within $A$. Reverse the roles for the other side. Proving *absence* of a restrictive attachment requires covering every separately attainable record and contact value, for example through exact marginal equality or a universal extension. An unresolved joint product need not discard an independently proved proper-arm flag.

## Evidence and stopping

A full-cohort contract can record, for each occurrence, its input digest and physical support sets, the two-holder reduction and its pivots if available, and one of the validated exact decisions or sufficient certificates above. Record separately any missing shared identity, fixed $c$, empty arm, impossibility witness, or unresolved obligation. Cache by complete stage, knot law, support sets and $c$ while retaining the mapping to all physical occurrences. A resource limit, incomplete quantified proof, failure of one pivot order, or absence of a sampled counterexample is **undecided** for the gates it leaves open.

For a positive product every pair of separately formed functions of the two private records also factors through $c$. If both their projections with $c$ were free, the resulting three-place relation would be free. Thus no such functions yield a K1–K3 knot. A failed product establishes conditional dependence on these records. It does not identify a binary knot, two native recurrence witnesses, or the causal contribution of this take. No conclusion transfers to other side distinctions outside these two private records without an additional source argument. [Canonical allowed-state test](../../docs/FOUNDATIONAL_THESIS.md#canonical-knot-test)
