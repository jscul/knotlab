# A middle ring that carries without cancelling

Epic `AFFINE-WIRE-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** It is direction 1 of `INTERMITTENT-NET-20261108-001`. The coordinator relayed the go-ahead on
  2026-11-08 with a stop condition: if arrival sets of affine chains always have gaps, close the process line with that as the
  obstruction.
- **What the earlier epics found.**
  - In chains of three rings with one rule and one contact law throughout, no chain with both contacts persistent composes at
    every lag (`PROCESS-CHAIN-20261108-001`).
  - Native intermittent composition happens only on affine substrates (`INTERMITTENT-NET-20261108-001`).
- **The question.** Among affine chains, with each ring its own rule and each contact its own law, is there one in which both
  contacts persist and the far contact binds the end rings at every lag from d + 1 on? That would pass the contact-network gate's
  composition across time.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The question is about row sequences.** In an affine chain, binding and composition at lag T are read from the supports r_T(c) = e_c M^T. Each row sequence is eventually periodic, so persistence and composition are decided exactly by iterating two row vectors. | proved; checked against full state spaces on 1,200 chains | A |
| 2 | **Persistent composition exists.** Of 9,216,000 affine chains, 45,406 keep both contacts persistent. 2,376 of those compose at every lag from d + 1 on, and in 380 both contacts bind the end rings. In 430 the contacts are two or three cells apart, so the middle ring carries c1's past across its own cells: middle rules 150, 60, 102, 90 and the shifts 170 and 240. The smallest: rule 150 on all three rings, 3/5/3 cells, the contacts two apart, each contact reading both of its middle-ring neighbours and one neighbour of its end ring. | exploratory search (H1, forced gaps, fails); verified on full state spaces; canonical check by the generic enumerator and knotlab | B |
| 3 | **It transports, sparsely.** One size past the search, with a middle ring of 8 cells, 80 chains in 40 of the 337 composing rule-law groups still compose persistently with the contacts two or more cells apart. | exploratory stress test | B |

## Answer

The stop condition is not met: gaps are not forced. On affine substrates, with the rings and contacts chosen apart from each other,
two complete contacts between processes can coexist, each binding its two rings at every lag, and compose: from the moment the far
ring's influence can arrive, the far contact needs the pasts of both end rings at every lag. In the smallest example the far contact
settles into a fixed parity of cells from all three rings and both contacts' first values, a single knot that persists. This is a
persistent native network across time.

## Reading

**Interpretation, not a theorem.**
- **For the contact-network gate.** Two complete contacts form a native-network candidate when they pass every contact gate,
  coexist in one substrate, preserve endpoint identity, compose by a substrate-native law, and retain composition under admitted
  restrictions, transports and recodings. The constructions do the following:
  - each contact persists, two-sided and lost under erasure (A32);
  - they coexist in one space-time law and keep their identities;
  - they compose by the substrate's own linear dynamics, with nothing drawn;
  - recoding by constants changes nothing, by the affine reduction;
  - transport to a larger middle ring keeps composition for some families only;
  - restrictions were not tested.
- **Why the uniform chains failed.** The constructions mix laws: a contact reads its middle ring on both sides and its end ring on
  one side. Many also mix rules. A single rule and law everywhere made the two ways round the middle ring cancel.
- **Where the line stands.** One process, one contact and two contacts have each been read. Persistent composition exists on
  affine substrates and not on the nonlinear ones tested, and intermittent composition is native only on affine substrates. The
  program's recurring family, parity and affine laws, is again the one that composes.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Persistent composition with d ≥ 2 exists (B) | a middle ring of 8 cells (the search went to 7), end rings of 3 to 6 cells (the search went to 5), every position with d ≥ 2, for all 337 composing rule-law groups: 26,960 chains (`stress_test.json`) | pass: 80 chains in 40 groups compose persistently; 1,280 did not repeat within 20,000 lags and are undecided |
| The constructions are verified (B) | the 12 smallest with d ≥ 2 on their full state spaces (`verify_transport.json`) | pass |
| The smallest construction's knot (B) | generic enumerator at lags 1 to 8, knotlab check on the eventual parity (`canonical.json`) | pass: one knot through c2(T) at every lag, meeting both end rings from lag d + 1 = 3 on |

## Literature and provenance

- **Sources.** Linear recurring sequences over finite fields, and additive automata on rings (Martin, Odlyzko and Wolfram 1984).
- **Classification.**
  - **Ticket A.** Known-with-delta: the reduction of the gate to row sequences.
  - **Ticket B.** New as far as found: persistent composition of two contacts across time, and its constructions.
- **Where the question came from.** The coordinator's choice of direction 1.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A34 (composition at every lag).
- **Scope.** Linear rules, contact laws by their linear parts, and the declared sizes.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions: A (a proof) and B (an exploratory search with its verification and
  stress test).
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
| This attempt — persistent composition on affine chains | **Status:** Successful | 2,376 chains compose persistently; 430 through the middle ring; verified |
| Local direction — networks of processes | Continue | The network gate's remaining items, and paths of more contacts, are open |
| Broader exploration — G5 with G1 | Known alternatives | The pulse law; learning a rule from its knots (G16) |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | A persistent native network across time exists, on affine substrates |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.**
  - The gate's restrictions, and transport in general.
  - Chains of more than two contacts: native paths across time.
  - Whether any nonlinear chain composes persistently.
- **The missing bridge to the program's composed topology.** A native path: several contacts in a row, each composing with the
  next.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Native paths across time (G5, with G1) | 3/3 — Major | 2/3 — Testable | Chains of four rings and three contacts built from the composing families, with the gate's restrictions and transports checked → a path whose ends are bound at every lag, or the length at which composition fails | Selected · not started |
| 2 | The pulse law of affine chains (G5) | 2/3 — Substantial | 2/3 — Testable | Carried from `INTERMITTENT-NET-20261108-001` | Alternative · deferred |
| 3 | Nonlinear persistent composition (G5) | 2/3 — Substantial | 1/3 — Stated | Search nonlinear chains seeded from the affine constructions → one, or an obstruction | Alternative · deferred |
| 4 | Learning a rule from its knots (G16) | 2/3 — Substantial | 1/3 — Stated | Carried | Alternative · deferred |

1. **Native paths across time.**
   - **Payoff 3.** A path of contacts with its ends bound is the first composed topology across time, adjacency then distance.
   - **Concreteness 2.** Ticket A's reduction extends to longer chains unchanged.
   - **Uncertainty.** Whether composition survives a second middle ring.
2. **The pulse law.** Carried.
3. **Nonlinear persistent composition.** No method yet beyond search.
4. **Learning a rule from its knots.** Carried.

## Final report as sent

Sent to the owner on 2026-11-08 at 09:53 UTC and copied here verbatim.

A positive result: a persistent native network across time exists. Your stop condition, forced gaps, is not met. I searched 9.2 million affine chains, letting each ring have its own rule and each contact its own law. In 2,376 of them both contacts persist and the far contact needs both end rings' pasts at every lag once they can reach it. In 430 the middle ring carries the signal across its own cells. The smallest is rule 150 on rings of 3, 5 and 3 cells, verified on its full state space and with knotlab. [Decision note](https://github.com/jscul/knotlab/blob/main/research/AFFINE-WIRE-20261108-001/affine_wire.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt | Successful | Persistent composition found and verified |
| Local direction | Continue | Paths of more contacts, and the gate's restrictions, are open |
| G5 Dynamics (question 4) | Capability gained | A persistent native network across time, on affine substrates |

**Next step:** Continue, with #1 selected.

| # | Direction | Payoff | Concreteness | Status |
| --- | --- | --- | --- | --- |
| 1 | Native paths across time: four rings, three contacts | 3/3 | 2/3 | Selected, not started |
| 2 | The pulse law of affine chains | 2/3 | 2/3 | Deferred |
| 3 | Persistent composition on nonlinear substrates | 2/3 | 1/3 | Deferred |
| 4 | Learning a rule from its knots (G16) | 2/3 | 1/3 | Deferred |

**Corrections:** one, a Narrowing. My two earlier epics said persistent contacts "never compose" and that persistent composition "remains absent". That was true only for chains with one rule and one law throughout, and mixed chains do compose ([history](https://github.com/jscul/knotlab/blob/main/HISTORY.md)).
**Goals:** a G5 checkpoint.
**Assumptions:** none changed.

Say if you want me to start native paths.
