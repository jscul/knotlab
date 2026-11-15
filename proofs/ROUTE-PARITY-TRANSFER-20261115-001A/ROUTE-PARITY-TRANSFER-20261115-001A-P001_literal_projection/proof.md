# Projecting every guarded route axiom onto the source clauses

Status: Proved

## Standard statement

Let \(F\) be a finite list of signed clauses, each on three distinct variables of \(x_1,\ldots,x_n\). Take the two-use compiler of TWO-RELAY-PADDING-20261115-001C. Its full output \(G\) includes the raw strictly ternary axioms and one unit for every guard value supplied on the compiler's selector menu. There is an explicit substitution \(\pi\) sending **every** variable of \(G\) to one signed source literal or one Boolean constant. It sends the positive representative of \(x_i\) back to \(x_i\). After removing false constants and duplicate literals, and discarding clauses containing a true constant or opposite literals, the multiset of surviving images consists of **one source clause per selected physical clause slot**. No resolution inference or existential simplification is needed for this identity.

In the listed construction, a different occurrence receives a different slot, even if two entries are equal after reordering their literals. In the fixed wiring at width \(n\), the list contains all \(8\binom n3\) signed clauses in the canonical order. Selecting a formula with repeated entries there selects each distinct signed clause once. The theorem includes \(n=0\), an empty clause list, isolated declared variables and an empty selection. Every clause has width exactly three wherever a source clause is present. Arbitrary guard settings outside the compiler's menu need not describe a source formula.

## Nearest known result

The preceding decision reduction gives a model of the raw formula from any satisfying source assignment. A natural choice there sets an intermediate wire from its departure signal and the pad's enabling value, which can depend on two bits. Here a wire can always copy its **destination** literal. Together with the pad and witness choices below, this yields a signed-literal substitution valid simultaneously for all source assignments and an exact syntactic identity on the axioms. A previous project proof uses affine substitutions to translate refutations after identifying their initial clause images. The present result supplies that initial-clause identity for this particular guarded compiler. [Two-use decision compiler](../../TWO-RELAY-PADDING-20261115-001C/TWO-RELAY-PADDING-20261115-001C-P001_pairwise_sharing/proof.md) · [Earlier whole-proof substitution argument](../../COMPRESSION-ROBUST-PROOF-COMPLEXITY-001HDW/COMPRESSION-ROBUST-PROOF-COMPLEXITY-001HDW-P001_common_restriction_conversion/proof.md)

## The substitution

For each signed source literal \(a\), let its signal \(X_a\) have image \(a\). Give the distinguished signals \(s,t\) images \(1,0\). Extend \(\pi\) to a negated literal by negating its image. Each compiled block uses a feedback middle \(G_v\), internal boundary copies \(v_0,\ldots,v_h\), and upper middles on the chain of internal implications. Give every one of these variables the image of \(v\). An abstract implication \(u\to v\) uses the same physical middle \(W_e\) at its two ports. Set \(\pi(W_e)=\pi(v)\). At the destination port the unconditional implication \(W_e\to v_j\) becomes true. At the departure port its conditional half has image \(\neg\pi(u)\lor\pi(v)\lor\pi(L_p)\), where \(L_p\) is its signed padding literal. The two feedback implications and all upper-chain implications are true because both sides have the same image.

Give the initial boundary and the input wire to \(s\) image \(1\). Give the final boundary and the output wire from \(t\) image \(0\). This makes both endpoint units, all their padded clauses, and their unconditional wire connections true. Give private padding, unused middles and the external boundaries between blocks image \(0\). The only active implications incident on the two physical endpoint wires are the stated connections. No active implication uses an external boundary between blocks. Fresh private edge pads appear in disabled implications or in both halves of an unconditional implication whose image is already true.

For each disjunction of two abstract implications \(D_1\lor D_2\), the compiler keeps just \(D_1\lor p\) and \(D_2\lor\neg p\) when the disjunction is selected. The possible cases are as follows. The two complement rows are always selected.

| Disjunction | \(\pi(p)\) | Image of the first kept half | Image of the second kept half |
| --- | --- | --- | --- |
| \((s\to X_x)\lor(s\to X_{\neg x})\) | \(\neg x\) | \(x\lor\neg x\) | \(\neg x\lor x\) |
| \((X_x\to t)\lor(X_{\neg x}\to t)\) | \(x\) | \(\neg x\lor x\) | \(x\lor\neg x\) |
| \((X_{\neg a}\to X_b)\lor(s\to X_c)\) | \(c\) | \(a\lor b\lor c\) | \(c\lor\neg c\) |

Each row has its own pad, shared only between its two conditional ports. Thus every sign pattern of a source clause works. In an unselected data row use the same pad image \(c\). Both conditional halves are off, and its two destination copies still give true unconditional implications. The order chosen for \(a,b,c\) only selects which physical half supplies the source clause.

It remains to account for the raw guards and witnesses of **each** padded ternary slot. Write its three signed padded literals as \(L_1,L_2,L_3\). Its raw axioms are
\[
(w_1\lor w_2\lor w_3),\qquad
(\neg e_j\lor\neg w_j\lor L_j)\quad(1\le j\le3).
\]
Map each guard \(e_j\) to its pinned value. Every raw pin unit is then true. If all three switches are on, set \(\pi(w_j)=\pi(L_j)\). All three guarded clauses become true, and the witness disjunction has the image of the padded clause. If some switch is off, choose the first such \(j\), set \(\pi(w_j)=1\) and give the other witnesses image \(0\). The witness disjunction is true, the chosen position's negated guard is true, and the other positions' negated witnesses are true. This also works for all seven partially or wholly disabled patterns at a single slot. The compiler uses wholly disabled slots when deselecting a source clause.

All raw variables have now received a consistent image. Of the four raw clauses of a kept slot, only the witness disjunction can survive. In the table there is exactly one such survivor per selected data slot. Opposing halves, disabled occurrences, complements, endpoint groups, feedback, separators and pins contribute none. This proves the multiset equality. Evaluating these images at any source assignment gives a particular simultaneous assignment to all hidden variables, and the resulting pinned raw CNF has precisely the truth value of the selected source formula. For \(n=0\) the construction uses only constants. At positive width the complement blocks retain the signed representatives even for a variable absent from the data clauses.

If the supplied physical catalogue has \(m\) data slots, the predecessor uses \(h=2n+m\) disjunctions, \(v=2n+2\) abstract signals and \(r=4h+2v+4=12n+4m+8\) stages. There are \(32(r+1)\) raw ternary clauses and \(24(r+1)\) guard pins. Once names are indexed, writing the table of variable images requires \(O(r)\) operations. The fixed full catalogue has \(m=8\binom n3\).

## Counterexamples and checks

Changing just the prescribed image of a selected data pad to \(\neg c\) leaves the raw formula intact but changes its two residuals to \(a\lor b\lor\neg c\) and \(c\). Copying any surviving raw witness disjunction into the formula a second time also leaves all satisfying assignments intact and doubles its source-clause multiplicity.

For a stronger semantic control, take the empty source on \(x,y\) and adjoin the four ordinary strict ternary clauses on their positive representatives and a fresh \(z\) that encode \(z=x\mathbin{\oplus}y\). Exactly one \(z\) extends each pair of source values. With the two representatives still mapped to \(x,y\), each of the six possible signed-literal or constant images for \(z\) fails on some source assignment. Hence the four additional axioms cannot all have tautological images under this requirement. The faithful images of the two source representatives matter in this example.

The [checker](check.py) evaluates every signed literal of the predecessor's emitted raw clauses and every signed guard unit. It compares normalized clause **multisets** directly, using the immutable compiler to generate the target and a separate symbolic evaluation to test it. It includes all 256 selectors at \(n=3\), catalogues at \(n=4,5\), listed duplicate and reordered clauses at \(n=7\), isolated variables and four widths with no data clauses, including zero. It runs the wrong-pad, raw-duplicate and XOR controls and all eight guard patterns on a selected slot. The importable function build_projection returns the raw formula object, its pins, and a map keyed by positive target variable IDs. In that map \(\pm(n+1)\) denote the two constants.

The uniform theorem follows from the clause calculation. The finite replay is V1, since it uses the actual predecessor emitter and this proof's independently written image evaluator. A separate AI investigator in the same task checked the need to preserve both representatives in the XOR control. This result concerns the compiled axioms. A transfer of refutation length must also preserve the inference rules of the chosen proof system. [Retained numerical checks](checks.json)
