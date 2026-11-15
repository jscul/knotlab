# All boundary tables for two displayed positive middles

Status: Proved

## Standard statement

Use a nonempty serial block of guarded stages. Each stage has two positive implication chains from its initial boundary to its final boundary, each passing through one middle. The boundary names are distinct. Each middle name occurs in at most two middle positions, and each pad name in at most two implication positions. The two namespaces and all private guard and witness names are disjoint. Display two different positive middle names $h,k$, each with exactly **one** occurrence in this block, so each may also occur once in another block. Fix all stage guards. Release the original outer units when displaying the two boundary values $a,d$.

Let $T(a,d,h,k)$ mean that these four values extend to the original raw clauses. There are **324 different full tables**. A candidate table occurs exactly when it has both properties below.

1. It contains $0000$ and $1111$ in the order $(a,d,h,k)$.
2. Lowering $a$ or raising $d$ in an allowed tuple preserves membership.

One explicitly defined wiring with 152 stages realizes all 324 tables by changing guards alone. For each fixed $(a,d)$, the following is the complete list of conditions on the support $S_{ad}=\{(h,k):T(a,d,h,k)\}$.

| $(a,d)$ | Exact restriction on $S_{ad}$ | Number of supports | Attainable without a mixed pad |
| --- | --- | ---: | ---: |
| $00$ | Contains $00$ | 8 | 7 |
| $01$ | Contains $00$ and $11$ | 4 | 4 |
| $10$ | Any subset of the four pairs | 16 | 13 |
| $11$ | Contains $11$ | 8 | 7 |

A **mixed pad** has opposite signs in two active single-half implication positions. It is counted once per pad after reading the raw guards. Among the possible supports, OR and NAND require exactly one such pad, and XOR requires exactly two. Every other possible support requires zero. These are minima over block constructions at the indicated endpoint values. A supplied external unit subsequently excludes any endpoint row incompatible with it.

The starting three-stage example has a left support $\{10\}$ and a right support $\{00,01,11\}$ at the specified boundaries. The two coordinate projections agree separately while the joint supports are disjoint. The right-hand report there is the positive implication $h\to k$. Mixed pads permit supports beyond both directions of positive implication together. [Three-stage starting example](../../../research/GUARD-CHOICE-SEPARATION-20261115-001/decision.md)

## Necessity and count

Uniformly zero or one route signals satisfy every positive implication for every pad valuation and allow all private slots to complete. This proves the first property. The leftmost boundary occurs only as the tail of an implication, and the rightmost only as its head. Lowering the first or raising the last preserves every satisfied raw guarded clause, leaving the internal witness and pad choices fixed. This proves the second.

For a fixed $(h,k)$ the allowed endpoint sets are upward-closed in the four-element order with bottom $10$, incomparable middle elements $00,11$, and top $01$. The six possibilities are the empty set, the singleton top, either middle with the top, both middles with the top, and the whole set. For displayed pair $00$ the mandated tuple requires the endpoint element $00$, leaving three choices. For displayed pair $11$ there are likewise three. For each of $01,10$ all six choices remain. The construction below makes every combination attainable, so the count is $3\cdot 6\cdot 6\cdot 3=324$. The per-endpoint restrictions follow as well. For example, for arbitrary $R\subseteq\{0,1\}^2$, take $S_{10}=R$, $S_{00}=R\cup\{00\}$, $S_{11}=R\cup\{11\}$ and $S_{01}=R\cup\{00,11\}$. Together with the necessity argument this witnesses every listed single-row possibility.

## A fixed wiring for every admissible table

Introduce abstract Boolean signals $A,D,H,K$. For each of the fourteen nonconstant four-bit vectors $s$ prepare the four-literal clause that forbids precisely $s$ on these signals. Each clause contains at least one negative literal $\ell_-$ and one positive literal $\ell_+$. Call the other two literals $f,g$. With a separate auxiliary signal $W_s$, use the pair

$$
(\ell_-\lor f\lor W_s)\ \land\ (\neg W_s\lor g\lor\ell_+).
$$

After forgetting $W_s$ this forbids just $s$. If all four original literals are false the two requirements force opposite values of $W_s$. Otherwise one can set $W_s=0$ when either literal in the first half is true and $W_s=1$ in the remaining feasible cases. Both ternary clauses are mixed-sign. Write $\neg u\lor v\lor w$ as $(u\to v)\lor(u\to w)$ and $\neg u\lor\neg v\lor w$ as $(u\to w)\lor(v\to w)$. This uses two disjunctions of positive implications per four-bit row.

For each disjunction $D_1\lor D_2$ use one new pad $p$ at two positions. Keeping $D_1\lor p$ and $D_2\lor\neg p$ enforces that disjunction after $p$ is forgotten. Deselecting its two conditional halves removes it. A guarded ternary slot whose three switches are on enforces its padded disjunction. An off switch permits its local witness to satisfy the slot independently. Thus a guard menu can independently select exactly the two disjunctions for each forbidden four-bit row.

The following details realize the abstract signals on the actual two-use stage layout. They specialize the predecessor's construction on the chosen list of positive implications. [Two-use signal-block compiler](../../TWO-RELAY-PADDING-20261115-001C/TWO-RELAY-PADDING-20261115-001C-P001_pairwise_sharing/proof.md)

- For each abstract signal $v$, place one stage per incident wire end between an opening stage and a closing stage. The internal boundaries are $v_0,\ldots,v_m$. A private middle $G_v$ appears in the two enclosing stages, with only $G_v\to v_0$ at the start and $v_m\to G_v$ at the end. Stage $j$ in between has an unconditional upper chain $v_{j-1}\to M_j\to v_j$. The cycle forces every one of these signals and fresh upper middles to equal $v$. Equal values satisfy all its requirements.
- An implication from $u$ to $v$ has a separate middle wire appearing twice, once in the lower branch of a stage in each corresponding signal block. The departure connects $u$ to the wire with the indicated conditional half. The arrival connects the wire to $v$ unconditionally. Disable their unused halves and directions as prescribed. For fixed pad values, eliminating this wire gives precisely the conditional implication. Taking the wire equal to $v$ always extends a satisfying abstract assignment.
- A first external stage and a port of the $A$ block enforce $a\to A$. A port of the $D$ block and a last external stage enforce $D\to d$. Both terminal wires occur twice. Fill unused branches with distinct middle names and disabled implications. Give every unconditional or disabled edge a private pad. Mark one fresh upper chain middle in the $H$ block and one in the $K$ block as the actual displayed names $h,k$. Their fixed structural blocks have incident wires even when all optional data are switched off. Those marked names occur once each.

The checker's one fixed roster uses 18 abstract signals, 28 disjunctions and 56 conditional implications. The 112 incident-wire stages, 36 enclosing stages, two endpoint ports and two external stages give 152. The original raw emitter produces 4,896 strictly ternary clauses and 3,672 distinct guard bits. For each forbidden $s$, the guard menu acts on twelve bits belonging to its four conditional halves. The other half at each such implication occurrence stays disabled. Each paired pad and each reused middle has at most two physical positions. The raw clause list is the same for all menus.

Select precisely the rows outside a candidate $T$ satisfying the two stated properties. On the internal signals the forbidden-row construction enforces $T(A,D,H,K)$. The observed boundary table is therefore

$$
\exists A,D\ \bigl(a\le A\ \land\ T(A,D,h,k)\ \land\ D\le d\bigr).
$$

Lowering the left endpoint and raising the right endpoint show that this implies $T(a,d,h,k)$. Conversely choose $A=a,D=d$. This proves sufficiency without assuming the endpoints supplied by the external caller are copied in both directions.

## What one mixed pad changes

For a fixed endpoint row, any set of two-bit observations can be described by ordinary signed clauses forbidding individual pairs. The language of unary constraints and the directed positive implications $h\to k$ and $k\to h$ has a more restrictive exact test. A support is describable in it iff it is closed under coordinatewise minimum and maximum. For two bits the only incomparable observations are $01$ and $10$. If both are present, closure requires $00$ and $11$. The three failures are precisely OR, NAND and XOR. Conversely the empty set and the nine nonempty rectangles are described by unary constraints (including no constraints for the full set). The two remaining three-element closed sets each require one of the directed implications. The diagonal $\{00,11\}$ requires both. Thus unary constraints alone fit ten masks, at most one directed implication fits twelve, and allowing both fits thirteen.

With no mixed pad, set the value of each pad to release all its single active halves simultaneously. A fully enabled implication remains a positive implication independently of its pad value. For the resulting positive implications, intersections and unions of two models are models, also after fixing common endpoint values or projecting away private signals. This proves the zero-pad obstruction for the three exceptional masks. The closed supports allowed at each endpoint are all possible without mixed pads. At a single stage, fixed endpoints supply the available unary pins by enabling the appropriate incoming or outgoing implication. At $10$ enabling both through one middle gives the empty support. Both directions between $h,k$ can be supplied in three stages with a single private middle $G$ repeated twice. Enable $G\to x_1$ and $x_2\to G$ in the enclosing stages. In the central stage enable $h\to x_2$ and $x_1\to k$ for $h\to k$, reverse the roles for $k\to h$, or enable both complete central branches for equality. All pads here are private. These choices realize the last column of the first table.

A single-stage block has two one-use observed middles $h,k$. At endpoints $10$ its four potential implications act as the literals $h,\neg h,k,\neg k$. Pair the two incoming positions with opposite active single halves to obtain $h\lor k$. Pair the two outgoing positions independently to obtain $\neg h\lor\neg k$. Either pair alone requires one mixed pad and suffices for its named relation. Both together impose XOR. The same outgoing pair gives NAND at $00$ and the incoming pair gives OR at $11$. More generally every three-element row at $10$ is a single signed binary clause supplied by two appropriate positions. Unary pins give rectangles. The two disjoint pairings implementing the two clauses of equality or the two clauses of XOR give the remaining diagonals. All sixteen supports thus already appear in a single stage at $10$.

To prove XOR requires **at least two mixed pads on any permitted block**, suppose a single such pad suffices. After releasing all other one-sided pads, drop its two conditional implications temporarily and call the remaining positive implication graph $G$. The two values of the mixed pad give exactly the alternatives $G+e$ or $G+f$, adding one directed implication each because the pad occurs at most twice. Their union of projected models is supposed to be XOR. Both off-diagonal assignments are then feasible in $G$. By its closure under minimum and maximum the two diagonals are feasible there as well.

For a positive implication graph with some true and false pins, inconsistency means a true-pinned vertex reaches a false-pinned vertex. Otherwise setting exactly the vertices reached from true pins to one gives a model. Consider adding the single implication $u\to v$ to $G$. If this makes displayed $00$ impossible, a path through this new implication must begin at a *fixed true endpoint*, since neither displayed bit is true there. Its part up to $u$ belongs to $G$. Similarly, if it makes displayed $11$ impossible, a path through it must end at a *fixed false endpoint*. Its part from $v$ belongs to $G$. The two path fragments combine with $u\to v$ to give inconsistency for **all** displayed values. Any alternative omitting both diagonals therefore contributes no assignment. Applying this to each alternative contradicts the presence of the two off-diagonals. The one-stage XOR construction proves sharpness. With four uses of a single pad, $h\lor p$, $k\lor\neg p$, $\neg h\lor\neg p$ and $\neg k\lor p$ together realize XOR at $10$.

## Nearest known result

The predecessor already compiles arbitrary strict 3-SAT at opposite endpoints to a positive two-use stage layout. Its quantitative source is the signal-block construction. Another predecessor classifies projected positive-implication systems by forced values and a preorder. Classical work on conjunctive definitions of Boolean relations gives general background for recognizing tables by closure and bases. The local statement here identifies which *simultaneous* boundary-and-middle tables survive the actual serial endpoint directions, makes every one available on one fixed guarded wiring, and gives the mixed-pad threshold for XOR. [Two-use compiler](../../TWO-RELAY-PADDING-20261115-001C/TWO-RELAY-PADDING-20261115-001C-P001_pairwise_sharing/proof.md) · [Positive-implication projections](../../ROUTE-FRONTIER-MEMORY-20261115-001A/ROUTE-FRONTIER-MEMORY-20261115-001A-P001_exact_boundary_profiles/proof.md) · [Creignou, Kolaitis and Zanuttini](https://www.sciencedirect.com/science/article/pii/S0022000008000196)

## Validation and scope

The checker enumerates all 65,536 candidate tables, compiles each of the 324 passing tables as a guard vector on the same raw CNF, and obtains its sixteen observed entries by PySAT. It checks selected complete models against every original clause. Replacing the two opposite signs with equal signs gives the same raw clause skeleton but releases the forbidden rows, as verified on a menu requiring exclusions. A separate exhaustive single-stage check covers the ten possible two-use pad partitions and all 256 half-activation menus per partition, yielding 34 distinct full tables. A separate same-task reviewer reconstructed the monotone-endpoint spectra and audited the two-use requirement. Together these finite checks corroborate the symbolic statements at V1. A table test on supplied entries does not compute those entries from an arbitrary guarded input. [Checker](check.py) · [Recorded counts](checks.json)

