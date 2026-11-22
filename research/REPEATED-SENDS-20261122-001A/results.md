# Two source requests and one ordinary receipt

**The same receiver gets one positive receipt. It cannot get a second under the enrolled ordinary growth rule.** At birth it reads three private marks. All three acquire distinct coholders in one later event. They are then ineligible for another payment. Old holders acquire no new marks, and the two allowed sender addresses are disjoint from the receiver. No further ordinary cut, however many occur, can change this receiver's permitted record. [Physical receiver check](../../artifacts/REPEATED-SENDS-20261122-001A/REPEATED-SENDS-20261122-001A-E001_repeated_sends/receiver_gate.json)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt · distinct second receipt at the fixed R | **Ruled out for all ordinary continuations** | Every mark R can observe is already shared after its one positive finish. |
| Repeating the same source action | Conditional on payment and admission | Two early swaps undo each other; the original holder-preserving swap ends when the two marks obtain different coholders. |
| Inference from complete local history | Exact ambiguity | All eight records retain both repeated intents and every source outcome attainable in the same protocol. |
| G15 Learning and G5 Dynamics | Obstruction learned | A second attempt, an actual second physical move and an additional observable receipt have different conditions. |

## What happened at the source

The experiment issued either two idle requests or two requests to transpose the same marked pair, initially 01. It also enrolled the mixed orders to isolate the effect of the second instruction. While the marks are private to S₀, two forward transpositions are both real and change 01 → 10 → 01. The first payment subsequently sees the same values as two idle requests. A second swap can therefore change the single future receipt's distribution by canceling the first swap *before* anything was paid. [Complete source census](../../artifacts/REPEATED-SENDS-20261122-001A/REPEATED-SENDS-20261122-001A-E001_repeated_sends/source.json.gz)

After payment each mark still belongs to S₀, but each also belongs to a different child. The earlier transposition was guaranteed lawful by acting on two marks with identical holdings. That structural operation is unavailable from then on. For parity, transposing the unequal values would violate both paid children on every reached word. For not-all-equal, the stricter structural condition still fails, yet the swapped values can preserve the full law on particular already-formed words. The separate permissive control tried the swap on the current word and left all other values unchanged. Unadmitted attempts stayed in the population and produced no refusal signal at R. In 18 of 24 not-all-equal source settings, identical whole S₀ readings accompanied both lawful and refused outcomes. The other six admitted every enrolled allocation under the chosen background. [Full allowed and refused word examples](../../artifacts/REPEATED-SENDS-20261122-001A/REPEATED-SENDS-20261122-001A-E001_repeated_sends/source.json.gz)

The table uses the earlier archived complete starting word (both reference inputs zero) and the pointwise-lawful not-all-equal control. “Both” counts two actual moves among all twice-requested trials. Two later trials share exactly the same relevant child state. When one succeeds, its inverse restores a lawful state; when the first is refused, the next sees the same obstacle.

| Timing of the two swap requests | Actual moves, intact | Actual moves, diverted | Best equal-odds guess of twice idle vs twice requested, intact | Same guess after diversion |
| --- | --- | --- | ---: | ---: |
| Both before payment | Both, 1 | Both, 1 | 1/2 | 1/2 |
| First before payment, second afterward | Both, 7/8; first only, 1/8 | Both, 15/16; first only, 1/16 | 789/1568 | 1/2 |
| Both after payment | Both, 7/8; neither, 1/8 | Both, 7/8; neither, 1/8 | 1/2 | 1/2 |

“Afterward” includes before R is born, between its birth and finish, or after its finish, with all ten ordered placements represented. When an action is requested after the finish, the recorded finish already preceded that request. For the holder-preserving rule, the number of actual moves in these three timing cases is respectively two, one and zero on either law. Under pointwise parity the same counts hold. These counts describe the source even when R cannot distinguish them. [Timing and probabilities](../../artifacts/REPEATED-SENDS-20261122-001A/REPEATED-SENDS-20261122-001A-E001_repeated_sends/archive_reference_summary.json)

## What R can infer

No history ruled out either repeated intent. No history ruled out any actual two-position source outcome that could otherwise occur under its protocol. An impossible late structural swap, for example, was excluded by the operation itself before reading R. Every one of the eight fresh words occurs with every attainable source status in each relevant comparison. The receiver cannot always decide which send was requested or whether an otherwise possible second move succeeded. [Exact joint law](../../artifacts/REPEATED-SENDS-20261122-001A/REPEATED-SENDS-20261122-001A-E001_repeated_sends/joint.json.gz)

The two genuine local samples read the same fresh word at birth and at first payment. Their joint law places all mass on equal pairs. Observing both improved the best equal-odds guess by **zero in every one of 480 repeated-intent comparisons**. With one request before and one after payment, the intact not-all-equal answer is exactly the earlier single-receipt **789/1568 = 50.32%**; the first early swap generated that difference. Parity gives 1/2. Two early requests cancel, and two late requests cannot influence a new R value. Both cases give 1/2 under both laws. Moving the first marked payment to a different child gives 1/2 for R in every timing case. [Earlier single-receipt comparison](../HIDDEN-SENDER-MARKS-20261122-001A/results.md) · [Joint and mixed-order checks](../../artifacts/REPEATED-SENDS-20261122-001A/REPEATED-SENDS-20261122-001A-E001_repeated_sends/joint.json.gz)

A real source correlation survives without a second receipt. Given two requested swaps on the intact archived not-all-equal word, with the first early and the second late, the chance that both actually moved was 7/8 before observing R. Conditional on the one finished word it is **67/74 for 000** and **47/58 for 111**. Both remain strictly between zero and one. One common cause is the first child's fresh bank; part of it goes toward R, and its unchanged values also determine whether a later flip would be lawful. Counting only successful offers would select on that hidden bank. Under the actual twice-requested prior, the optimal true-two-versus-fewer choice still always favors two, achieving 7/8. Under the equal-intent mixture at this background the actual event priors become 7/16 for two and 9/16 for fewer; the best classification of that event remains 9/16. The complete tables distinguish these questions. [Unselected actual-event joint and posterior tables](../../artifacts/REPEATED-SENDS-20261122-001A/REPEATED-SENDS-20261122-001A-E001_repeated_sends/joint.json.gz)

The census has 1,920 enrolled request protocols (two laws, three routing conditions, four fixed old backgrounds, ten placements, four request words and two meanings of admission). Each repetition of names, background or timing has its own stated meaning and receives no population weighting. With equal intent odds, 432 of the 480 repeated-intent comparisons gave 1/2 and the other 48 gave the same single-receipt 789/1568. The 48 are intact or coherently renamed not-all-equal trials with exactly one request before payment. All computed probabilities use the previously stated rule of choosing a lawful complete fresh word uniformly at each actual birth conditional on its paid inputs. The reachability and continuation claims require no probability law. [Full physical witnesses](../../artifacts/REPEATED-SENDS-20261122-001A/REPEATED-SENDS-20261122-001A-E001_repeated_sends/witnesses.json.gz) · [Scientific replay](referee_handoff.md)

A separate in-study implementation reproduced all 1,920 protocol cells, 480 intent comparisons and 528 complete physical witnesses. It rejected every one of the 56 unequal birth/finish word pairs and a fabricated sender tag. In 108 protocols an actual source exchange was possible after R had already finished; none could produce another local observation. Independent scientific referee pending. [Verification record](../../artifacts/REPEATED-SENDS-20261122-001A/REPEATED-SENDS-20261122-001A-E001_repeated_sends/verification.json)

**Next step:** Research directions — No next action selected.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A receiver allowed to obtain a second fresh bank | 3/3 · repeatable ordinary sensing | 1/3 · needs a new continuation mechanism | Specify how one receiver keeps its identity and gains new observable distinctions → an admitted mechanism or its first obstruction | Alternative · deferred |
| 2 | More cuts with this fixed receiver | 1/3 · same exhausted bank | 3/3 · invariant covers all later cuts | Check eligibility of its three already-shared marks → none | Alternative · deferred |

**STOP** for repeated receipt at this fixed ordinary holder. The absence of a second receipt extends to every continuation preserving the frozen growth and read rules. The measured probabilities concern the enrolled source and supplied weighting.

**Corrections:** None to a released claim.

**Goals:** G15 and G5 gain the exact condition that limits this receiver to a single paid local change and the comparison with actual repeated source requests.

**Assumptions:** Common complete old word within each paired trial, simultaneous ordinary funded cuts, continuing identity of the fixed holder, and retention of all unannounced refusals.

**Scaffolds:** Marked source addresses, offered timing and two requests, permissive whole-state check as a control, local mark orientation and finish, matched allocation diversion, and the separately supplied conditional fresh-word weighting. A further read of a different holder would change the experiment.
