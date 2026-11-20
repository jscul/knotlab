# Can ordinary growth give the signature of entanglement?

**Independent referee pending.** A setting can play two different roles here. One can ask a different question of exactly the same states, or one can group the states by the setting they already contain. An observer can distinguish these procedures even when the four setting pairs occur equally often and both recorded outcome bits are fair. The owner's premise, aim and frozen readings are in the [design](preregistration.md).

## What has to be explained

Bell's locality assumption for this test asks for local responses and one common, setting-independent preparation. CHSH gives a four-correlation test of that assumption. For two available bits on each side put their signs in a single list, A₀,A₁,B₀,B₁. On that list the CHSH expression is A₀(B₀+B₁)+A₁(B₀−B₁). Exactly one parenthesis is zero and the other is ±2. Averaging over any one nonnegative, normalized weighting gives a magnitude at most 2. Each observer's marginal for a fixed setting also stays the same when the other setting changes. The bound holds even for a common source that depends on the entire structure. [Bell](https://journals.aps.org/ppf/abstract/10.1103/PhysicsPhysiqueFizika.1.195) · [Clauser, Horne, Shimony and Holt](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.23.880)

The literature's GHZ argument makes the common-assignment question exact using four prescribed parities. The related six-context construction of Mermin and Peres gives compatible readings where a single sign assignment fails. Kochen and Specker establish the more general obstruction to assigning context-independent quantum values. In the sheaf treatment, a common assignment concerns support, and a common probability distribution must also reproduce the weights in every context. Quantum theory itself bounds the CHSH magnitude by 2√2. [Greenberger, Horne and Zeilinger](https://arxiv.org/abs/0712.0921) · [Mermin](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.65.3373) · [Peres](https://doi.org/10.1016/0375-9601%2890%2990172-K) · [Kochen and Specker](https://doi.org/10.1512/iumj.1968.17.17004) · [Abramsky and Brandenburger](https://arxiv.org/abs/1102.0264) · [Cirel’son](https://doi.org/10.1007/BF00417500)

What this study adds is the comparison on actual grown knot structures, an explicit lawful realization of the change caused by conditioning on embodied settings, and a test of what an observer can learn from *both* local values. The comparison bears on possibility in this model. Inferring a claim about our universe would require an additional physical interpretation.

## Which operations the ordinary law supplies

| Candidate mechanism | What the structure supplies | What the reader supplies |
| --- | --- | --- |
| (a) Settings contained in the structure | Two existing distinctions can have jointly open values, and the rest of the state can retain information about them. | Naming them as selectors and conditioning on their values. Two fair, mutually independent selectors need not be independent of the quadruple of potential outcomes. |
| (b) Dependence on the other setting | A structural difference elsewhere can affect the next join, even when there is no chain of growing-end steps to it. This compares different presentations. | To use that sensitivity as a Bell response one must implement a setting as a change of presentation, or give a response access to the other setting. Varying which reading is taken on a fixed presentation performs neither operation. |
| (c) Locally compatible readings with no common explanation | Every existing state extends across an ordinary birth. Consequently exact projections and their readings on one stage admit joint assignments. Some choices of outcomes from different states can conflict. | To require an inconsistent parity family one must supply a distinct context-dependent relation or operation. Probabilities impose a second requirement: a common weighting. |
| (d) Weighting | The model gives allowed states and, after growth, counts of their extensions. | Turning counts into probabilities, transporting them, biasing a bit or weighting a preparation separately in each context. Any one common nonnegative weighting obeys CHSH for fixed local responses. Conditioning endogenous settings changes the effective weighting. |

The known growth results are relevant to (b) even in the absence of a Bell effect. In the reviewed pair of structures a ternary parity join can need zero or one fresh distinction when a remote part of the growing end differs. A parity bond on its inputs can determine closure. The parents' other children determine the fresh demand. Finite completed orders with the fixed map agree, with the named fairness qualification at infinity. These are statements about which knots arise. None supplies four preparation or measurement operations on one state. [Joint referee report](../ORDINARY-DYNAMICS-20261120-001/referee-R1/report.md)

## The result of conditioning

The targeted construction joins two sets of readings through two groups of four parity knots. Each group forces its two terminal distinctions to agree. Alice holds X,A₀,A₁,P and Bob holds Y,B₀,B₁. The equations imply A₀=B₁, A₁=B₀ and Y=B₀⊕B₁. The 128 allowed starting states give 32 states to each (X,Y) cell. Choosing the locally indexed bit gives a⊕b=XY on every state. Both selected bits have probability 1/2, while Alice can recover Y as A₀⊕A₁. Reading the same 128 states again under each external setting gives correlators (0,1,1,0) and S=2. Under the ordinary next funded growth the same marks still realize these effects. [Construction and counts for both laws](embodied_control.md)

A change of a conditional distribution is an observable statistical dependence. Sending a signal would additionally require someone to be able to set the selector. Here the law supplies no such action. At the recorded-bit interface the embodied table passes the usual marginal equations. At the interface exposing both local marks Alice's conditional distributions are disjoint. A table with a changing reported-bit marginal fails the requested entanglement signature even at the narrower interface. The second reading on this same parity start reaches magnitude 4 under an allowed relabelling and has just such a change, of 1/2 under uniform weights. The value 4 also exceeds the quantum bound. This gives a concrete explanation of the apparent violation. Conditioning counts a different set of allowed assignments in each setting cell. On the same structure the independently varied readings satisfy Bell’s bound.

## The smallest structures and the grown sample

Both external protocols first admit separated readers on two ternary knots with five distinctions. The unmarked distinction is shared and every marked cross pair is two steps apart. On a single ternary knot no separated pair of observers exists. With all assignments counted equally, the following are exact. Correlators are ordered 00,01,10,11. The maximum ranges over the eight CHSH sign conventions fixed in advance.

| Smallest connected start | Allowed states | I correlators | I maximum | II correlators | II maximum |
| --- | ---: | --- | ---: | --- | ---: |
| Even parity | 8 | (0, 0, 0, 0) | 0 | (1/2, 1/2, 1/2, 1/2) | 1 |
| Not-all-equal | 18 | (1/9, 1/9, 1/9, 1/9) | 2/9 | (5/9, 1/3, 1/3, 5/9) | 10/9 |

Two disjoint ternary knots on six distinctions are the smallest six-mark case. With 16 parity states or 36 not-all-equal states and uniform weighting the external I maximum is zero for both. The corresponding II maxima are 1/2 and 8/9. Uniform factorization across the two knots leaves biased yes/no answers for the pair-pattern question. A nonzero CHSH score by itself is not evidence for a dependence between the two sides. The [records](../../artifacts/ENTANGLEMENT-READ-20261120-001B/ENTANGLEMENT-READ-20261120-001B-E001_separated_readings/summary.json) give placements with no chain their own denominator.

The ordinary cohort contained 33 starts. Six were controls or built examples, 24 came from 12 labelled tree draws with matched extra-loose versions, and three were literal archived jumping starts. There were four draws with replacement from each of 16, 125 and 1,296 equally weighted words for sizes four, five and six respectively. Each matched version used the same labelled draw. Each archived start had one third of its separate stress comparison. The two six-knot archived starts have finite bursts; the seven-knot start has an exponential growth proof under parity. These comparisons sample initial and first grown states, including new distinctions. They do not count how often explosive growth occurs. The separately built two-relay case above is a targeted 34th source.

Every one of the 33 ordinary starts qualified and grew once under each law. The first structures agreed across the two laws. Across the 132 source-stage-law combinations the frozen marking procedure gave 694 placements, of which 256 read at least one newborn. Each law had 347 placements for external settings, including 159 with a separate selector on each side. All four embodied setting cells had positive weight in each of those 159. No frozen ordinary-cohort placement exceeded 2. The first grown stage alone gave 233 external and 107 embodied placements per law. The measured uniform-stage maxima on that stage equal the U rows below. Each maximum is an actual placement, not an optimization over every possible observer.

| Law | State weighting | External I | External II | Embodied I | Embodied II |
| --- | --- | ---: | ---: | ---: | ---: |
| Parity | Uniform stage or equally lifted start | 0 | 1 | 0 | 1 |
| Parity | Double when Alice's first mark is 1 | 0 | 1 | 0 | 4/3 |
| Not-all-equal | Uniform stage | 122/285 | 22/19 | 163/410 | 2 |
| Not-all-equal | Equally lifted start | 4/9 | 32/27 | 146/273 | 2 |
| Not-all-equal | Double when Alice's first mark is 1 | 122/285 | 1106/855 | 3988/6831 | 2 |

The two definitions expose different information. In 20 parity placements, the pair-pattern outcomes reveal a dependence that no single-mark setting pair shows under the uniform weighting. Growth preserves the possibility of each *old* state under both laws. With not-all-equal, uniform weighting of grown states changed the distribution of the old portion of the marks in 221 of 233 measured grown placements. The greatest total variation was 434/2565. Dividing each initial state's mass equally among its extensions preserved that distribution in all 233. Both uniform procedures preserved it in all 233 parity placements. The extension theorem concerns support, and the numerical changes concern the chosen weighting. [Full exact tables, including zero cells](../../artifacts/ENTANGLEMENT-READ-20261120-001B/ENTANGLEMENT-READ-20261120-001B-E001_separated_readings/exact_readings.json.gz)

## Global explanations and the nearest additions

An ordinary fresh birth has at least one completion for every allowed input tuple, and a birth with no fresh distinction adds only an entailed rule. In one complete update, different births have private fresh distinctions. Extend each birth in turn. This proves surjectivity of restriction to the previous stage, and induction gives it at every finite stage. Consequently every actual event of a projected context extends to a global state, and every common state weighting pushes forward to a common law on all specified answers. This rules out mechanism (c) for those native readings. A choice of several separately possible events can still fail. For either knot law, use a ternary central knot and one further ternary knot at each of its three marks. Three locally permitted selections can require all three central marks to be 1. Every pair of selections extends, and all three together violate the central rule. The remaining allowed selections still have a common explanation. In the four-context parity test, none of 64 potential sign assignments satisfies all requirements. In the six-context test it is none of 512. Deleting any one context restores 8 and 16 global assignments respectively. The uniform local tables agree on their overlaps in both inconsistent tests. A nonempty native presentation cannot impose all of either set of readings as exact projections. [Proof and parity controls](../../proofs/ENTANGLEMENT-READ-20261120-001A/ENTANGLEMENT-READ-20261120-001A-P001_common_state/proof.md)

For uniform parity states there is also an obstruction *after* conditioning. If both complete marked registers conceal the other affine selector, their four conditional laws have a common local explanation, even with arbitrary local processing. In each fixed setting cell write the remaining freedom as a uniform bit string. The change in either register caused by the other selector can be absorbed into a change of this bit string without altering its uniform distribution. One common string then serves all four setting pairs. The hypotheses matter: hiding the setting from one reported bit is weaker, as the ten-knot example shows. The affine proof applies to parity with uniform weighting. Whether uniform not-all-equal can give a conditional excess while both complete local registers conceal the other selector remains open.

The least change, counting altered contexts from four equal-output rules, is **one**. Let both observers return a fair shared bit and give Bob the opposite bit only at setting pair 11. The four correlations become (1,1,1,−1); both reported bits remain fair. Changing the rule on a fraction t of this last context gives S=2+2t. Bias the shared bit so it is 1 with probability p. At Bob's setting 1 the change in his probability of 1 across Alice's settings is t(1−2p). This control distinguishes a genuinely changed marginal from a joint rule hidden by the fair weighting. Implementing that one rule requires access to the pair of settings. No such resource follows from the ordinary growth definition.

One can even match a quantum-realizable four-context table by supplying *only a weighting* once the embodied reading interface exists. On two unlinked four-place parity knots give weight 5 to each allowed state satisfying a⊕b=xy for its actual readings and weight 1 to every other state. Each setting pair has 48 units of mass, versus 16 at equal weight. Both full local marked pairs stay uniform. The correlations are (2/3,2/3,2/3,−2/3), so S=8/3. This whole table is realized by the standard two-qubit Bell measurements on a Bell state mixed with white noise at visibility 2√2/3. Its origin here is the joint setting-and-outcome factor of five, mechanisms (a) and (d). Equal weighting of the same unlinked structure gives S=0. With the factor of five but independent settings the signed score is 2/3. This is a mathematical construction that answers the owner's possibility question at the level of the table. The factor itself has yet to arise from the growth law. [Exact family and quantum realization](../../proofs/ENTANGLEMENT-READ-20261120-001A/ENTANGLEMENT-READ-20261120-001A-P001_common_state/proof.md)

## Position and decision

| Scope | Verdict | What the study established |
|---|---|---|
| This attempt | **Status: Successful.** | Across 33 other starts, both knot laws and 694 marked placements, none exceeded 2. The panel included 12 labelled draws with matched variants, three archived explosive starts and 256 placements reading a newborn distinction. |
| Local direction — independent settings | **Obstruction proved.** | At every finite grown stage, both reading definitions obey CHSH ≤ 2 under any one common weighting. The largest external score in the 33-start panel was 4/9 for reading one distinction and 1106/855 for testing a pair pattern. |
| Broader exploration — contextuality | **The missing condition is identified.** | Every old state extends. The four GHZ requirements and six Mermin–Peres requirements have zero common assignments, so neither can arise as exact projections of one nonempty ordinary state set. A join can depend on a disconnected part of the growing end, but this supplies no response to a freely varied remote setting. |
| G17 meeting patterns and G5 dynamics | **Obstruction learned.** | With uniform parity states, if both *complete local pairs* hide the other setting, all four tables admit a common local explanation. The corresponding embodied-settings question for not-all-equal remains open. |

**Next step:** Continue with independent referee replay of the ten-knot witness and the full-pair theorem. The requested scientific stop has been reached.

| Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|
| 1. Replay conditioning versus independent settings | 2/3 — Substantial | 3/3 — Ready | Reconstruct the four tables and the common explanation → confirm or identify a failing case | Selected · referee pending |
| 2. Test uniform not-all-equal with both complete pairs hidden | 3/3 — Barrier | 2/3 — Testable | Require equal full-pair marginals before scoring → find an excess or prove a bound for a named class | Deferred · B223 |

**Corrections:** None to earlier research claims.  
**Goals:** B222 records the owner’s lead under G17 and G5, rated 3/3 for payoff and 3/3 for concreteness.  
**Assumptions:** A112 remains an interpretation. A119–A124 record the study’s scaffolds.  
**Scaffolds:** Two readings, three state weightings, marked observers and built versus sampled starts were compared. One minimum-control pencil prediction preceded the recorded freeze. Both reading definitions were already specified and stayed fixed.  
**Basket:** B222 reached its stop. B223 retains the open not-all-equal question.

## Final report as sent

2026-11-20 20:45 UTC

**The structure can produce a CHSH score of 4 with two fair reported bits when the settings are themselves part of the state. Independently varying the settings on those same states gives 2.** Results are referee pending. [Full study](https://github.com/jscul/knotlab/blob/main/research/ENTANGLEMENT-READ-20261120-001/decision.md)

The example has ten parity knots and 128 allowed states, with 32 states for each setting pair. The nearest marked distinctions of the two observers are three steps apart. Reading the bit indexed by each observer’s own setting gives correlations **(1, 1, 1, −1)**. Each reported bit stays exactly 50/50. Yet Alice can recover Bob’s setting by comparing her two available bits. This is mechanism **(a)**. The settings are fair and independent of each other, but sorting by them changes which underlying states are counted. The score of 4 also exceeds the quantum maximum of (2\sqrt2). [Exact counts](https://github.com/jscul/knotlab/blob/main/research/ENTANGLEMENT-READ-20261120-001/embodied_control.md) · [Quantum bound](https://doi.org/10.1007/BF00417500)

| Scope | Verdict | What the study established |
|---|---|---|
| This attempt | **Status: Successful.** | Across 33 other starts, both knot laws and 694 marked placements, none exceeded 2. The panel included 12 labelled draws with matched variants, three archived explosive starts and 256 placements reading a newborn distinction. |
| Local direction — independent settings | **Obstruction proved.** | At every finite grown stage, both reading definitions obey CHSH ≤ 2 under any one common weighting. The largest external score in the 33-start panel was 4/9 for reading one distinction and 1106/855 for testing a pair pattern. |
| Broader exploration — contextuality | **The missing condition is identified.** | Every old state extends. The four GHZ requirements and six Mermin–Peres requirements have zero common assignments, so neither can arise as exact projections of one nonempty ordinary state set. A join can depend on a disconnected part of the growing end, but this supplies no response to a freely varied remote setting. |
| G17 meeting patterns and G5 dynamics | **Obstruction learned.** | With uniform parity states, if both *complete local pairs* hide the other setting, all four tables admit a common local explanation. The corresponding embodied-settings question for not-all-equal remains open. |

Changing **one of four context rules** suffices to exceed 2. Bob flips an otherwise shared, fair bit only at setting pair 11. Biasing that bit makes Bob’s marginal change with Alice’s setting. A second scaffold answers John’s “could” at the level of a quantum table. On two unlinked parity knots, giving five times the weight to states with the desired joint parity reproduces an **entire quantum-compatible table at CHSH (8/3)**. Even the complete local pairs then hide the other setting. The weighting supplies that result through **(a) and (d)**. Ordinary growth has yet to derive it. [Proof and construction](https://github.com/jscul/knotlab/blob/main/proofs/ENTANGLEMENT-READ-20261120-001A/ENTANGLEMENT-READ-20261120-001A-P001_common_state/proof.md)

**Next step:** Continue with independent referee replay of the ten-knot witness and the full-pair theorem. The requested scientific stop has been reached.

| Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|
| 1. Replay conditioning versus independent settings | 2/3 — Substantial | 3/3 — Ready | Reconstruct the four tables and the common explanation → confirm or identify a failing case | Selected · referee pending |
| 2. Test uniform not-all-equal with both complete pairs hidden | 3/3 — Barrier | 2/3 — Testable | Require equal full-pair marginals before scoring → find an excess or prove a bound for a named class | Deferred · B223 |

**Corrections:** None to earlier research claims.  
**Goals:** B222 records the owner’s lead under G17 and G5, rated 3/3 for payoff and 3/3 for concreteness.  
**Assumptions:** A112 remains an interpretation. A119–A124 record the study’s scaffolds.  
**Scaffolds:** Two readings, three state weightings, marked observers and built versus sampled starts were compared. One minimum-control pencil prediction preceded the recorded freeze. Both reading definitions were already specified and stayed fixed.  
**Basket:** B222 reached its stop. B223 retains the open not-all-equal question.
