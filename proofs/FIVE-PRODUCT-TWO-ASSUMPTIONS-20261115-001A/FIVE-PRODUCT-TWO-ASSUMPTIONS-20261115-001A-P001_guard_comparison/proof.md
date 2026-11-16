# Two assumptions for the same conclusion

Status: Proved

## Standard statement

On the original five-product instance, let \(N_a\) be the stored rule
\[
      (v=0,\ x_2=a)\ \Longrightarrow\ x_0=0,\qquad a\in\{0,1\}.
\]
The least proof cost when training this rule is optional is **23** for each \(a\). If the rule is actually trained, the cost is **exactly 24 for \(a=0\)** and **between 26 and 28 for \(a=1\)**. More generally, with \(c\) paid citations of that one trained rule, the lower bounds are \(\max(24,22+c)\) and \(\max(26,23+c)\), respectively. Training both designated rules costs at least 28 in total including the main proof. These bounds allow every visible affine question and every placement of the two individual source checks.

Write \(p_i=x_{i-1}x_i\), \(1\le i\le5\), and \(Q=\sum_i p_i\) over \(\mathbb F_2\). The visible bits are \(x_0,\ldots,x_5,s,u,v\). Rich means \(s=Q,u=p_1,v=p_2+p_3\). Plain means \(s=1+Q\) with both reports free. A question costs one for its two branches. A source check costs one and replaces the current affine cell by the affine hull of that source's surviving points. A stored rule is trained by refuting its premise together with the negated conclusion. Each citation costs one, requires the whole current cell to satisfy the premise, and intersects the cell with the conclusion. The bounds also allow a citation that closes its branch. The positive 24-unit witness uses a citation with surviving rows and a live continuation.

## Nearest known result

The accepted five-product total-work results give ordinary cost 23, optimum 23 when one equation may imply one further equation, and a lower bound of 25 for training \(v=0\Rightarrow x_0=0\), comprising training 7 and main cost at least 18. Their two-triple interpolation and sector-restriction bounds are used below. The new arguments compare specific conjunctive premises at equal training price and use the non-affine source rows that remain in four exceptional first-query branches. [Ordinary tree proof](../../FIVE-PRODUCT-TOTAL-WORK-20261115-001A/FIVE-PRODUCT-TOTAL-WORK-20261115-001A-P001_charged_tree/proof.md) · [One-premise proof](../../FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/one_premise.md) · [Sector restriction](../../FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/sector_proof.md)

## Training and replacement at every citation

Let \(B_a\) denote the rule \(x_2=a\Rightarrow x_0=0\). Training either rule imposes \(x_0=1,x_2=a\); training \(N_a\) also imposes \(v=0\). In both cases ask \(x_4\). On each answer, \(p_1=x_1\), \(p_2+p_3=a(x_1+x_3)\), and \(p_4+p_5=x_4(x_3+x_5)\) are affine. The rich check therefore imposes \(s=Q\), and the following plain check closes. This costs \(1+2\cdot2=5\).

For the matching lower bound, further set \(x_1=x_3=u=v=0\). On the free bits \(x_4,x_5,s\), the two sources read \(s=x_4x_5\) and \(s=1+x_4x_5\). Each set of four rows spans the whole three-bit space. Each answer to a nonconstant affine question contains both source types, so each child costs at least two. No initial source check changes the cell. The three-bit problem costs at least five. Under this affine restriction, questions may become constant and each original source check is simulated by at most one corresponding check. The common restriction proves exactly five for all four training problems.

Replace a proof's stored \(N_a\) by \(B_a\) and use the five-unit training proof for \(B_a\). At each original citation the current cell already satisfies \(x_2=a\), and the new update is the identical intersection with \(x_0=0\). Induction over the unchanged main tree gives precisely the same cells and liveness at every node. This holds for arbitrarily many citations, including ones under different earlier checks. The one-equation lower bound of 23 now excludes 21 and 22. The ordinary tree attains 23 when training is optional. The training bodies cannot in general be copied when a premise is removed. Asking \(x_4+v\) and checking plain then rich on each answer costs 5 on both narrow training premises. On the broader premises each first plain call retains 64 rows, including eight rich rows, so that body fails there. The \(x_4\) body proves the replacement directly.

If both \(N_0,N_1\) are trained, the first cannot be cited on a nonempty cell during training of the other because \(x_2\) is fixed to the opposite value. The two bodies cost at least ten. In the main proof, the single rule \(v=0\Rightarrow x_0=0\) can replace both rules at all citations with the same intersections and liveness. Its accepted main price is at least 18 if it is used. Without a main citation the ordinary lower bound is 23. Thus every proof training both costs at least \(10+18=28\).

## What each additional citation costs

Let \(F_a=\{x_0=1,x_2=a,v=0\}\) be the forbidden training cell. On deleting \(F_a\) from both sources, a citation can be removed from the main proof because every surviving row in its guard already satisfies its conclusion. Pruning branches with empty surviving union also removes citations that would close a branch. The accepted sector restriction gives
\[
       W\ \ge\ 5+c+T(R\setminus F_a,P\setminus F_a).
\]
Use the invertible triples
\[
 (x_1,x_0,u),\qquad (x_2,x_1+x_3,v),\qquad (x_4,x_3+x_5,s+u+v).
\]
Writing \(e=p+yw\) on each triple \((y,w,p)\), rich means all three \(e\)'s are zero and plain means they have odd sum. Each \(F_a\) depends only on the first two triples. The predecessor's spectator bound on the remaining, unchanged third triple gives 17 on the complement for \(a=0\) and 18 for \(a=1\). Its coarse bounds already attain these figures. This proves \(22+c\) and \(23+c\). For joint training the union \(F_0\cup F_1\) is the predecessor's \(x_0=1,v=0\) sector with complement cost at least 15. Thus total work with both declarations is also at least \(25+c\), where \(c\) counts all main citations.

## A stricter bound when one rule is trained

Both sources span the full initial affine cell, and neither guard is entailed there. The first useful main operation is a question. Use the predecessor's two-triple embeddings for each of the 511 possible first questions \(q\). In answer \(b\), choose a touched triple and two honest local rows of opposite local \(q\)-value. Selecting between these rows affinely by the remaining bits embeds two complete triples in the answer. Each injection preserves the rich and plain predicates pointwise.

On such an injection \(E\), pull back the premise equations to \(g,j\) and the conclusion to \(l\). Let \(U(h,l)\) be the accepted exact cost on two full triples when \(h\Rightarrow l\) is supplied without training and citations remain paid. A proof using the narrow premise \(g\land j\) can instead cite any one of \(g\Rightarrow l,j\Rightarrow l,(g+j)\Rightarrow l\). Here \(g+j\) denotes the sum of both equations including their right sides. The actual affine context of any original citation entails all three, and each update remains \(l\). Therefore each first-query answer costs at least the maximum of these three prices over all its injections. The checker reuses the predecessor's 26,387-cell calculation for \(U\), with its separate source checks, and takes the sum of these two answer bounds plus one for \(q\). Questions are packed in the displayed triple order, from the lowest bit of the first triple.

| Rule | First-question main lower bounds and numbers of questions | Questions initially below 19 |
| --- | --- | --- |
| \(N_0\) | 18 on 3, 19 on 3, 20 on 1, 21 on 50, 22 on 20, 23 on 434 | 8, 48, 56 |
| \(N_1\) | 18 on 1, 21 on 3, 22 on 3, 23 on 504 | 40 |

Each exceptional question touches only the middle triple. In one answer choose a true local row \(t\) satisfying the guard and a false local row \(t'\) failing it. Embed seven free bits consisting of the first and third triples plus a bit \(d\), by putting \(t+d(t+t')\) in the middle triple. The raw checks below verify all 128 points. If the two remaining errors are \(e_1,e_3\), the restricted sources and rule become
\[
  R:\ d=e_1=e_3=0,\qquad P:\ d+e_1+e_3=1,\qquad (d=0)\Rightarrow x_0=0.
\]

**This seven-bit problem costs at least seven.** With no citations, fixing \(d=0\) leaves the ordinary two-triple problem of cost 11. With \(k\ge2\) citations, fix \(d=0\) and the entire first triple to zero. The citations can all be deleted and the third triple still costs five, giving \(5+k\ge7\). Suppose exactly one occurrence is used. The plain source spans all seven bits, while the rich hull is the full \(d=0\) cell. If the first useful operation is a rich check, the remaining proof on \(d=0\) costs at least six. With its citation retained the zero first triple restricts it to a five-unit ordinary problem after deleting that citation, and without using the citation its cost is at least 11. A first question constant on \(d=0\) also leaves this six-unit subproblem in one child. For a first question nonconstant on \(d=0\), each answer contains a complete ordinary one-triple instance by the same affine interpolation. At most one child contains the single citation. The other child costs at least five. The child containing the citation costs at least one, giving \(1+5+1=7\). A citation is unavailable at the initial seven-bit cell.

| \(a\) | Packed \(q\) | Answer with the seven-bit problem | \(t,t'\) there | Unguarded true row in the opposite answer |
| --- | --- | --- | --- | --- |
| 0 | 8 | 0 | 0, 4 | 1 |
| 0 | 48 | 1 | 2, 3 | 1 |
| 0 | 56 | 0 | 0, 3 | 1 |
| 1 | 40 | 1 | 1, 4 | 0 |

Fixing the last-column row in the opposite answer leaves the ordinary two-triple price 11. Thus all three exceptional first questions for \(N_0\) cost at least \(1+7+11=19\). For \(N_1\), question 40 is \(x_2+v\). Its answer zero precludes the rule on the whole affine cell. Applying the ordinary spectator bound to that entire answer gives at least 13, so question 40 costs at least \(1+7+13=21\). Together with the table and the five-unit training, these give the lower bounds 24 and 26.

For the matching 24-unit proof with \(N_0\), train for five and ask \(x_2\) at the root. When \(x_2=0\), a rich check yields \(v=0\). Cite \(N_0\), then ask \(x_4\) and check rich followed by plain in each answer. That branch costs seven and its citation removes live states while retaining live states. When \(x_2=1\), ask \(x_0\) and \(x_4\) in sequence. All products contributing to \(Q\) are now affine, and four rich-then-plain closures cost eight. This branch costs 11. The total is \(5+1+7+11=24\).

For a 28-unit live-use proof with \(N_1\), train for five and ask \(x_2+v\). On answer one, a rich check fixes the middle triple to its sole honest row \((1,0,0)\). Cite the rule and use the five-unit \(x_4\) tree, so this child costs seven. On answer zero, ask \(x_0\) and \(x_4\). At each of the four leaves, a rich check imposes the first and third affine block errors equal to zero. In the middle triple \(p=y\), so the next plain check requires \(y(1+w)=1\), which fixes \(y=1,w=0\). A rich check closes. This child costs \(3+4\cdot3=15\), giving \(5+1+7+15=28\). The checker tests the actual live citation on this proof too.

## Validation and scope

The focused replay independently builds the sources directly from the five path products on all 512 visible words, executes the training bodies and the 24- and 28-unit positive proofs, and rejects removing its paid guard-establishing check or carrying its training body unchanged to an invalid wider premise. The first-question and spectator computations reuse the accepted predecessor algorithms. The new local embeddings and their raw predicate checks cover all four exceptional first questions, including original rows with unrestricted plain-side reports. The finite checker class is V1 for reused recursions and V2 for independently reconstructed source rows and direct proof replay. [Checker](check.py) · [First-question calculation](first_questions.cpp) · [Checked result](checks.json)

The bounds concern the two designated deductions on one fixed finite proof instance. The exact optimum after training \(N_1\) remains between 26 and 28. General proofs with different conjunctive guards or additional stored facts remain outside this classification.
