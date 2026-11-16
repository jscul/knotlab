# Total work with two visible product summaries and learned affine implications

Keep the five adjacent products \(p_i=x_{i-1}x_i\), the six original inputs \(x_0,\ldots,x_5\), the displayed total \(s\) and the two reporting bits \(u=p_1,\ v=p_2\oplus p_3\). The rich evaluator has \(s=Q=\bigoplus_i p_i\). The plain evaluator requires \(s=1\oplus Q\) and leaves \(u,v\) free. In this interface the earlier result found eight cases and an optimal tree with six distinct terminal contradiction proofs. [Five-product case and guard result](../FIVE-PRODUCT-GUARDED-REUSE-20261115-001/decision.md)

## Common charges

| Operation | Charge |
| --- | --- |
| Ask one visible affine question | One unit, including both child continuations |
| Check one whole evaluator on the current affine conditions | One unit, including its entire affine hull or its empty answer |
| Check a learned consequence under its assumptions | Pay all questions and evaluator checks in the proof of the contradictory alternative. Writing the resulting conditional statement costs zero |
| Use a stored consequence once | One unit per use, including checking that the known affine equations imply its assumptions. Any missing guard facts have to be derived at their usual costs |
| Take linear consequences of equations already present | Zero units |

Every proof uses the same four kinds of operation. An ordinary continuation is part of the inference that introduces it. A guard citing an earlier proof must actually be satisfied; knowing it holds on the surviving inputs of both evaluators is insufficient to grant it for free. Proofs can rearrange both their questions and the order of local checks. Costs count verifiable proof operations, not execution time or the effort spent discovering a proof.

## The cheapest proof tree costs 23

The direct proof asks \(x_0,x_2,x_4\), across seven binary questions. After fixing their values, each evaluator's total is affine. Eight times it uses a rich check followed by a plain check, closing each branch. **Seven questions and sixteen local checks cost 23.** [Full proof](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001A/FIVE-PRODUCT-TOTAL-WORK-20261115-001A-P001_charged_tree/proof.md) · [Replayable operations](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001A/FIVE-PRODUCT-TOTAL-WORK-20261115-001A-P001_charged_tree/certificate.json)

For the matching lower bound, take a smallest tree. If a question already has a forced answer on one nonempty evaluator, a check of that evaluator costs the same unit and allows the proof to go straight to that answer. The other branch can be dropped. Hence in a smallest tree every paid split leaves both evaluators possible on each answer. On each terminal branch after its final split, the first evaluator check has nonempty output. At least two checks are needed to close. Even when all local inference was free the fixed pair required eight leaves, so every charged tree costs at least \((8-1)+2\cdot8=23\). A fresh proof of a single affine consequent used only once can be inlined by splitting on that consequent and taking its checked counterproof on the negative child. This makes the tree comparison apply to deductions that have to be proved afresh. [Tree normalization and controls](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001A/FIVE-PRODUCT-TOTAL-WORK-20261115-001A-P001_charged_tree/proof.md)

The earlier eight-case tree calls six distinct terminal proofs. Under the same prices its saved proofs require seven questions, twenty evaluator checks including those that establish assumptions, and eight citations, for **35 units**. Closing the branches directly on those same questions costs **29**. Changing the questions to the alternating inputs gives the optimum of **23**. [Replay of the earlier six proofs](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/checks.json)

## The proposed implication can be reused, but costs more

To derive \(v=0\Rightarrow x_0=0\), assume \(v=0,\ x_0=1\) and ask \(x_4=c\). The rich check gives \(u=x_1\) and \(s=x_1\oplus c(x_3\oplus x_5)\). The plain check then forces \(x_2(x_1\oplus x_3)=1\), hence \(x_2=1,\ x_1\oplus x_3=1\). The next rich check contradicts \(v=x_2(x_1\oplus x_3)=0\). This is one question and three local checks in each of the two answers. The seven-unit derivation is optimal for that countercase. [Learned proof and sector costs](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/proof.md) · [Concrete programs](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/certificates.json)

| Replayed proof | Questions | Rich checks | Plain checks | Citations | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cheapest ordinary tree | 7 | 8 | 8 | 0 | 23 |
| Proposed implication used in both \(x_2\) branches below \(v=0\) | 8 | 12 | 10 | 2 | 32 |
| Proposed implication used across branches whose common ancestor still permits \(v=1\) | 8 | 13 | 10 | 2 | 33 |
| Another implication, \(x_1=0\Rightarrow x_2=0\), reused across such a split | 8 | 10 | 10 | 2 | 30 |

The 32-unit proof costs 39 on literal expansion. Its two consumer branches are genuinely live when the deduction is applied. Their saturated affine sets shrink from 128 to 32 rows and from 64 to 16. Applying the lesson once before separating \(x_2\) gives a 27-unit proof. Even the seven units saved on literal expansion leave the shared proof nine above the 23-unit tree. Across all 288 signed implications between distinct displayed coordinates, using coordinate questions and arbitrary local hull checks, a single learned scalar used twice on live branches costs at least 30. The cheapest ordinary proof in that same coordinate menu is 23. The fully mixed XOR menu is larger. [Costs, search and negative controls](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/proof.md)

For the named implication, any proof whose only trained fact is that implication and which cites it at least twice must cost **at least 24 even with arbitrary visible XOR questions**. Write \(F=\{v=0,x_0=1\}\). Paying for its refutation costs seven. As a relaxation, grant the main proof both source relations with all rows in \(F\) removed. Every legal citation now holds on the surviving raw rows, so the citations can be dropped from this relaxed ordinary proof. Its cost is at least fifteen, on top of the actual citation charges. Thus even a different placement of the two applications cannot turn this particular learned statement into a win. [Sector lower](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/sector_proof.md)

In the 33-unit proof the first split asks for \(x_2\). On the zero branch a paid rich check establishes \(v=0\) from \(v=x_2(x_1\oplus x_3)\). On the one branch the proof asks for \(v\) before citing the result on its zero answer. The checker rejects the same proof when the first guard check is removed.

## One affine premise and one affine conclusion

Allow the proof to learn one rule \(G\Rightarrow L\), where \(G\) and \(L\) are each a single affine equation on any of the nine visible bits. Allow arbitrary adaptive XOR questions, and any number of correctly guarded uses. The optimum with this option is **exactly 23**, attained by the ordinary tree. If an implication is used only once, splitting on its conclusion inlines its proof without increasing cost. If an ancestor of every use already establishes the guard, the proof can do this once there. Its counterproof runs once on one answer; all cited continuations on the other answer already satisfy the conclusion.

The full check also covers applications below different ancestors. When the two equations are independent, the forbidden set \(G\land\neg L\) is an affine subspace of codimension two. In nine bits there are 173,740 such subspaces. Recode the instance into three triples of the form \(t_i=y_iw_i\) on the rich side. An input of the plain side violates an odd number of these identities. Affine permutations of the four correct rows in each triple, together with permutations of the triples, preserve both source relations. They divide the 173,740 forbidden subspaces into 126 classes. For each class there are three choices of which affine equation is the guard. Testing all 511 possible root questions and embedding residual two-triple problems gives a direct lower bound of at least 23 for every one of the 378 representatives, including the charge for proving the proposed consequence. The lower estimate reaches exactly 23 on 21 representatives and is at least 24 on the other 357. This is a finite checked proof, including the cases where the main tree invokes the same lemma under incomparable branches. It does not identify a rule with a conjunction of premises with one of these one-premise rules. [One-implication proof and replay](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/one_premise.md)

One residual example illustrates the difference between a cheap conditional problem and a cheap proof. The countercase can cost five units, and a solver *given* the remaining sector can finish in thirteen. The real proof must route its branches, establish the guard and pay for citations. Those steps rule out the apparent two-unit saving on the remaining candidates. [Certificates and lower bounds](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/proof.md)


For the specific learned statement \(v=0\Rightarrow x_0=0\) the full one-premise calculation gives a stronger bound. Training costs seven and the main proof costs at least eighteen, giving **at least 25 units for any proof paying for that one named implication**. A one-citation witness costs 26, so the minimum when this statement is trained and used is either 25 or 26. With two live citations the displayed witness costs 32. [Named representative and exhaustive calculation](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/one_premise.md)

## How much remains possible with more general learned facts

The best proved interval with optional learning is **21 to 23 units**. The ordinary tree supplies 23. The lower covers a finite checked list of learned scalar affine conclusions under affine guards, even with arbitrary visible XOR questions, either evaluator's local deductions and earlier citations while a branch is open. It assumes that a repeated proof is referenced and paid for. It does not assert that a proof using genuine repeated citations attains 23. A 21- or 22-unit construction would therefore be a real advantage.

The proof counts the original assignments that a local evaluator check can exclude. Each of the 64 honest rich rows must eventually falsify a plain-side conditional inference somewhere in the proof. Each effective plain check can exclude at most twelve of them. A nonempty such check leaves only plain rows, so its continuation can be replaced by a single rich check that closes. The other direction is checked on 192 plain rows, each violating exactly one of three independent displayed product identities after an invertible recoding. At least five rich checks are needed to exclude them. The strongest constraint couples the two counts: a plain check covering many rich rows leaves few single-error rows available for its mandatory rich check. Counting the questions and citations needed to support distinct checks, and checking the few remaining extremal covers, excludes total cost 20 as well. [Full lower bound and matched controls](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001B/FIVE-PRODUCT-TOTAL-WORK-20261115-001B-P001_learned_affine_work/lower_21.md)

## Where a two-unit saving could still come from

One next test is to strengthen the single guard \(v=0\) by an additional raw assumption \(x_2=a\). For each \(a\in\{0,1\}\), the countercase for \((v=0,\ x_2=a)\Rightarrow x_0=0\) fixes \(x_0=1\). It has six remaining visible coordinates \((x_1,x_3,x_4,x_5,s,u)\). The rich relation on them requires \(u=x_1\), \(a(x_1\oplus x_3)=0\), and \(s=Q\). The plain relation requires \(s=1\oplus Q\). Here \(Q=x_1\oplus a(x_1\oplus x_3)\oplus x_4(x_3\oplus x_5)\). Exact ordinary minimization in this six-bit case costs **five units** for either value of \(a\), compared with seven to train the original single-premise fact. The main proof would have to establish both assumptions on each use. This gives two concrete guard candidates without asserting a 21- or 22-unit refutation. [Finite-cost routine](../../proofs/FIVE-PRODUCT-TOTAL-WORK-20261115-001A/FIVE-PRODUCT-TOTAL-WORK-20261115-001A-P001_charged_tree/charged.py)

To replay the two training costs, run the following with the A family's directory on the Python import path.

~~~python
from charged import exact_costs

for value in (0, 1):
    rich = plain = 0
    for word in range(64):
        x1, x3, x4, x5, s, u = [(word >> j) & 1 for j in range(6)]
        middle = value & (x1 ^ x3)
        q = x1 ^ middle ^ (x4 & (x3 ^ x5))
        if u == x1 and middle == 0 and s == q:
            rich |= 1 << word
        if s != q:
            plain |= 1 << word
    assert exact_costs(6, rich, plain).weighted == 5
~~~

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — beat the cheapest tree on the fixed pair | **Status:** Partially successful | Allowing one simple rule leaves the optimum at 23. The broader optimum is 21–23. |
| Local direction — reuse \(v=0\Rightarrow x_0=0\) | Settled | Its counterproof costs seven. Training and using this rule costs at least 25. |
| Broader exploration — several assumptions or several learned facts | Open | Only costs 21 and 22 would improve on the tree. |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Obstruction learned | A repeated deduction alone need not save total work. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One learned consequence under two affine assumptions | 2/3 — Substantial | 3/3 — Ready | Try both five-unit counterproofs with \(v=0,x_2=a\) → exhibit a 21- or 22-unit proof or exclude both candidates | Selected · started |
| 2 | Two interacting single-premise implications | 2/3 — Substantial | 2/3 — Testable | Test whether one deduction makes the other's guard available across branches → certify a strict saving or eliminate that interaction | Alternative · deferred |

For #1, adding the second assumption cuts either counterproof to five local work units. Reaching both assumptions at genuinely distinct uses is the remaining cost to test. For #2, a second fact could make a previously unavailable guard cheap. A valid comparison must charge both of their derivations and every use. The 23-unit upper for the class permitting one simple lemma is attained by the ordinary tree, which uses zero citations.

**Basis:** Two same-task mathematical proofs with finite executable checks, original-source certificates, a second reviewer and explicit wrong-guard/circularity controls. Prior work on ordinary clause learning and resolution over parity is background only. The design-advisor command could not authenticate.

**Goals:** G3 and G16 gain an exact comparator for proof work, a settled result for a single affine implication, and a two-unit remaining range with more general learned facts. No goal wording changed.

**Assumptions:** The quoted numbers use one unit per question, one per separate evaluator check, and one per named citation with its affine guard verified. A one-use deduction's scalar discharge costs the operations in its checked countercase. For comparison, making references free would remove two units from the displayed 32- and 30-unit repeated proofs and leave the 23-unit direct certificate intact. The theorems about optimality use the declared unit prices. No standing assumption changed.

**Corrections:** No accepted claim changed. Four residual sector estimates below 23 would have been insufficient for a tie by themselves. The test of the legal first question and actual citation guards supplies the missing lower bound.

**Basket:** The previous five-product study's first direction was taken. The proposed eleven-versus-twelve census on seven products remains deferred.

## Final report as sent

2026-11-16 01:00:28 UTC

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — beat the cheapest tree on the fixed pair | **Status:** Partially successful | The tree optimum is 23. One simple learned rule ties it; the broader optimum is 21–23. |
| Local direction — reuse \(v=0\Rightarrow x_0=0\) | Settled | Its counterproof costs seven; two citations force a total of at least 24. |
| Broader exploration — several assumptions or several learned facts | Open | Only costs 21 and 22 would improve on the tree. |
| G3 Hardness at three places and G16 Learning the rules behind what a system allows | Obstruction learned | A repeated deduction alone need not save total work. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | One learned consequence under two affine assumptions | 2/3 — Substantial | 3/3 — Ready | Try both five-unit counterproofs with \(v=0,x_2=a\) → exhibit a 21- or 22-unit proof or exclude both candidates | Selected · started |
| 2 | Two interacting single-premise implications | 2/3 — Substantial | 2/3 — Testable | Test whether one deduction makes the other's guard available across branches → certify a strict saving or eliminate that interaction | Alternative · deferred |
