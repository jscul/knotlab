# Two contacts across time

Epic `PROCESS-CHAIN-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** It is the selected next step of `SHARED-CONTACT-20261108-001`, which found that a contact shared by two
  rings passes the whole contact gate across time in a fifth to a quarter of parity configurations on rings of 8 and 9 cells. The
  coordinator relayed the go-ahead on 2026-11-08.
- **The question.** The program's composed topology starts from two complete contacts that coexist in one substrate and compose
  by a native law. Here three rings form a chain: ring A and ring B share a contact c1, and ring B and ring C share a contact c2,
  d cells apart on ring B.
  - **Persistence.** Can both contacts persist?
  - **Composition.** Does the chain then bind its ends, c2 needing the pasts of both A and C at every lag once A's past can reach
    it?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Listening contacts never compose.** A contact that reads its rings and feeds nothing back is read by no one, so the far contact never depends on the far ring. | proved; computed on 7,392 maps | A |
| 2 | **The far ring arrives after crossing the middle ring.** In a shared chain, c2 does not depend on ring A's first row before lag d + 1. In 694 of 792 chains it does at lag d + 1. | proved; computed | A |
| 3 | **Linear chains bind along their M^T rows.** With linear or affine rules and affine contact laws, a contact binds two rings exactly when the support of its row of M^T meets both. | proved; computed on 15,360 verdicts | A |
| 4 | **Persistent contacts do not compose.** Of 5,632 chains, both contacts persist in 182, and in none of them does either contact bind the end rings at every lag from d + 1 on. The ends are bound at c2 in that sense in 2 chains, neither of which keeps both contacts. | exploratory experiment (H1 fails); one size past with off-centre contacts, the same | B |
| 5 | **Composition comes and goes.** In 195 chains c2 binds the end rings at some lags of the eventual cycle, and in 154 of them both contacts bind at those same lags. This happens mostly for the shift rules 15 and 170 and the linear rules 60, 90, 105 and 150. It never happens in a chain whose two contacts both persist. | exploratory, post hoc (not under the frozen contract) | B |

## Answer

At the sizes tested, two contacts that each persist across time never compose: the middle ring does not carry one end's past to
the far contact so that the far contact always needs it. Chains that carry it, mostly shift and linear rules, do so only at some
lags, and those chains lose the persistence of a contact. Composition across time needs shared identity (Theorem 1), and the
feedback that shared identity brings is what keeps persistence and composition apart here.

## Reading

**Interpretation, not a theorem.**
- **For the contact-network gate across time.** Two complete contacts are a native-network candidate only when they coexist,
  preserve their endpoints and compose by a substrate-native law. Here they coexist, and each can persist. But no tested chain
  has a native composition law that holds at every lag. So the network gate fails across time at these sizes.
- **How the persistent chains avoid composing.** Of the 182 chains where both contacts persist:
  - 112 have rings that read no neighbour, and are effectively listening;
  - in 62 the far ring's influence never reaches c2, being blocked by one-sided rules and laws or cancelled between the two ways
    round the middle ring;
  - in 4 it reaches c2 and fades;
  - in 4 it stays but can always be overridden.
- **What composing chains do.** Shift and linear rings carry a contact's past around the middle ring in pulses. At the lags when a
  pulse arrives, the chain binds its ends and both contacts bind, an intermittent native network.
- **The program's static result.** Static native networks of two contacts compose for laws that compose like cycles
  (`NATIVE-NETWORK-20261021-001`). Across time, with elementary rings as the substrate, composition is at best intermittent.

## Stress test

One size past the census, with the contacts moved off the opposite point of the middle ring (`stress_test.py`, `stress_test.json`;
590 s).

| Claim | One size past | Result |
| --- | --- | --- |
| No persistent chain composes (B), chains to 5/6/5 with opposite contacts | 4/5/4 and 5/7/5 (contacts 2 and 3, and 3 and 4, apart each way) and 5/8/5 (opposite): 4,224 chains | pass: 198 chains keep both contacts and none composes; no chain binds its ends at every lag from d + 1 on |
| The light cone (A), to 5/6/5 | the same chains | pass: no binding claimed before d + 1 |

## Literature and provenance

- **Sources.** Light cones of cellular automata on graphs. Boolean automata double-cycles (Demongeot, Noual, Sené and coauthors)
  share one node between two cycles. A chain shares two.
- **Static networks.** The program's own static native-network results (`NATIVE-NETWORK-20261021-001`).
- **Classification.**
  - **Ticket A.** Known-with-delta: elementary.
  - **Ticket B and the post hoc measure.** New as far as found: a census of chains of shared contacts by persistence and
    composition.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A31 (proposal-combining contacts, with the self-blind family beside it), A32 (binding).
- **Taken by default.** A34, new: a chain composes when its far contact binds the two end rings at every lag from the light-cone
  lag on. The post hoc measure shows the reading matters, since composition at recurring lags is common where composition at
  every lag is absent.
- **Scope.** All three rings on one rule, the same law at both contacts.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions: A (a proof) and B (an exploratory census, with its stress test and
  post hoc measure).
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — do two contacts compose across time | **Status:** Negative evidence | No chain with both contacts persistent composes, one size past included |
| Local direction — contact networks of processes | Research directions | Composition is intermittent; the next question is what substrate could carry it at every lag |
| Broader exploration — G5 with G1 | Known alternatives | Composition at recurring lags (A34's alternative); middle rings that carry without mixing |
| Long-term goal — G5 Dynamics (question 4) | Obstruction learned | Across time, persistence and composition did not coexist in elementary chains |

**Corrections:** none. **Goals:** a G5 checkpoint (obstruction learned). **Assumptions:** A34 added.

- **What the attempt leaves open.**
  - Whether a different middle substrate composes at every lag: a ring that carries its contact's past without mixing it, such as
    a shift whose contacts read it without cancellation.
  - Whether composition at recurring lags is the right reading of a network across time.
- **The missing bridge to the program's composed topology.** A substrate-native law by which two persistent contacts compose at
  every lag.

**Next step:** Research directions — the epic's main hypothesis failed, and the next step is a bounded search for a substrate
that composes, not a continuation of the census.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Intermittent networks (A34) | 2/3 — Substantial | 3/3 — Ready | Read composition at recurring lags: which chains compose at a positive share of lags with both contacts binding there, and whether that share has a native law → a law, or none | Alternative · deferred |
| 2 | A middle ring that carries without mixing (G5, with G1) | 3/3 — Major | 1/3 — Stated | Characterize middle-ring rules and contact laws for which c2's dependence on ring A never cancels → a construction, or a proof that cancellation is forced | Alternative · deferred |
| 3 | Why some rules persist (G5) | 2/3 — Substantial | 1/3 — Stated | Carried from `SHARED-CONTACT-20261108-001` | Alternative · deferred |
| 4 | Learning a rule from its knots (G16) | 2/3 — Substantial | 1/3 — Stated | Carried from `TIME-KNOTS-20261107-001` | Alternative · deferred |

1. **Intermittent networks.**
   - **Payoff 2.** If a network across time is a native network at recurring lags, composition exists in 195 chains already.
   - **Concreteness 3.** The measure is computed.
   - **Uncertainty.** Whether an intermittent law is native or a pattern drawn by the observer.
2. **A middle ring that carries without mixing.**
   - **Payoff 3.** It would give the first native network across time.
   - **Concreteness 1.** No construction yet. The shift rules come closest, and cancellation around the ring is the obstacle.
3. **Why some rules persist.** Carried.
4. **Learning a rule from its knots.** Carried.

**Recommendation.** Research directions. Directions 1 and 2 are bounded searches. Stop the process line after them if neither finds a
native composition law, and reassess G5 against the owner's question 4, which the line has answered for one process and for one
contact.
