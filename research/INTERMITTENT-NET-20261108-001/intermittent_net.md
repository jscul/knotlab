# Intermittent networks across time

Epic `INTERMITTENT-NET-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** It is direction 1 of `PROCESS-CHAIN-20261108-001`, which the coordinator relayed on 2026-11-08 as the
  next step, with direction 2 as the fallback.
- **The finding it starts from.** In chains of three rings joined by two shared contacts, no chain with both contacts persistent
  composes at every lag. But 195 chains compose at some lags of their eventual cycle.
- **The question.** Is that intermittent composition native? That is, does the chain itself single out its composing lags, so that
  no observer supplies a phase, and does it survive transport to other ring sizes? It challenges A34, the strict reading of
  composition.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Intermittent composition is a strobed chain's persistent composition.** The composing lags recur with the period P of the chain's T-step maps, so the chain observed at one residue modulo P composes at every observed lag or at none. The phase is the only input the chain does not fix. | proved; computed on 263 chains | A |
| 2 | **In linear chains composition is arrival.** With linear or affine rules and affine laws, the chain composes exactly at the lags where its far contact depends on both end rings. In any chain, composition implies arrival. | proved; computed on 6,016 and 75,114 lags | A |
| 3 | **Native intermittent composition needs an affine rule.** Of 7,040 chains, 244 compose at recurring lags. In 92 the composing lags are singled out by the chain: composition exactly at arrival, and both contacts binding there. Every one of the 92 runs an affine rule (15, 170, 60, 90, 105 or 150). With a nonlinear rule this never happens, since the other cells can override an end that has arrived. Twenty rule-law groups, all shifts or additive rules, compose at every decided size. | exploratory experiment (H1, H2 and H3 fail as universal statements) | B |

## Answer

Intermittent composition is native only on affine substrates. There the chain composes exactly when the influence of both ends
arrives at the far contact, both contacts bind at those lags, and for twenty rule-law pairs this recurs at every tested size. On
nonlinear substrates the arrival of both ends does not settle composition, so the composing lags would have to be chosen by an
observer.

## Reading

**Interpretation, not a theorem.**
- **For the contact-network gate.** The gate asks that a network compose by a substrate-native law and persist. Across time,
  composition fails persistence by its intermittence, so A34's strict reading stands for the gate. What exists is weaker: a
  native but intermittent network, on affine substrates only.
- **The program's recurring answer.** It is the same family the program keeps meeting. Towers of patterns of patterns keep only
  parity (`GEOMETRY-LAW-20261029-001`), and static native networks compose for laws that compose like cycles, affine over finite
  fields (`NATIVE-NETWORK-20261021-001`, `AFFINE-TOPS-20261021-001`). Across time, the composing lags are a native law where the
  substrate is affine.
- **Pulses.** In affine chains each ring carries a contact's past round itself in pulses. The far contact composes when a pulse
  from each end arrives, and the composing share of the cycle, from 0.12 to 0.83, is fixed by the chain.

## Stress test

The census one size past, at 5/7/5 (contacts 3 and 4 apart each way) and 5/8/5 (opposite), with ticket B's own code (run as the
user unit `intermittent-net-s1`, 286 s; `stress_result.json`, `stress_rows.json`).

| Claim | One size past | Result |
| --- | --- | --- |
| Native intermittent composition needs an affine rule (B) | 5/7/5 and 5/8/5: 2,816 chains, 132 undecided | pass: 112 compose at recurring lags (62 with affine rules, 50 with nonlinear ones); the 24 whose composing lags are singled out all run affine rules (15, 170, 90, 105, 150) |
| The control: linear chains compose at their arrival lags (A) | the same chains | pass |

## Correction (2026-11-08)

Logged in `docs/CORRECTIONS.md` as a narrowing. The answer and the closure said that persistent composition "remains absent". That
held for the uniform chains tested, one rule and one law throughout. `AFFINE-WIRE-20261108-001` found it in 2,376 affine chains that
mix rules and laws.

## Correction (2026-11-08, A34 overturned)

Logged in `docs/CORRECTIONS.md` as not a block. The reading and the workspace-assumptions section kept A34 for the gate because the
gate "asks for persistence, which intermittent composition fails". The gate asks persistence of every contact and composition that
survives the admitted transports. `RECUR-PATH-20261108-001` found 452 families of paths with every contact persistent that compose
at recurring lags at every size tested, while under A34 none composes at two sizes. A34 was overturned by that challenge's
pre-registered rule and replaced by A37.

## Literature and provenance

- **Sources.** Eventual periodicity of finite dynamics. Additive cellular automata on rings (Martin, Odlyzko and Wolfram 1984) for
  the affine pulses.
- **Classification.**
  - **Ticket A.** Known-with-delta: the doctrine's reading of a strobe.
  - **Ticket B.** New as far as found: the census of intermittent composition by nativeness.
- **Where the question came from.** The coordinator's choice of direction 1, from the previous epic's post hoc measure.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A34 (composition), the last under challenge.
- **A34.** Confirmed for the contact gate. The gate asks for persistence, and intermittent composition fails it by definition. It
  is native only on affine substrates, which is recorded with the entry.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions: A (a proof) and B (an exploratory census).
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
| This attempt — is intermittent composition native | **Status:** Partially successful | Native exactly on affine substrates; never on nonlinear ones |
| Local direction — networks of processes | Research directions | Persistent composition is absent in uniform chains (narrowed: see the correction) and native intermittent composition is affine only |
| Broader exploration — G5 with G1 | Known alternatives | Direction 2, a middle ring that carries without cancelling; affine pulse laws |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | A native network across time exists, intermittently, on affine substrates |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** A34 confirmed for the gate.

- **What the attempt leaves open.**
  - A closed form for the composing lags of affine chains, in terms of the ring polynomials.
  - Whether some middle ring makes the pulses overlap into composition at every lag (direction 2).
- **The missing bridge to the program's composed topology.** Persistent composition of two contacts across time.

**Next step:** Research directions — the process line has answered its questions for one process, one contact and two contacts;
what remains are two bounded searches, and the line should stop if neither finds persistent composition.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A middle ring that carries without cancelling (G5, with G1) | 3/3 — Major | 2/3 — Testable | Affine chains first: choose ring sizes and contact laws whose pulse arrivals cover every lag, from the ring polynomials → persistent composition, or a proof that the arrival sets of affine chains always have gaps | Alternative · deferred |
| 2 | The pulse law of affine chains (G5) | 2/3 — Substantial | 2/3 — Testable | The composing lags from the ring polynomials and the contacts' delays → a formula matching ticket B's 92 chains | Alternative · deferred |
| 3 | Learning a rule from its knots (G16) | 2/3 — Substantial | 1/3 — Stated | Carried from `TIME-KNOTS-20261107-001` | Alternative · deferred |

1. **A middle ring that carries without cancelling.**
   - **Payoff 3.** Persistent composition would pass the network gate across time.
   - **Concreteness 2.** Ticket A's linear criterion turns the search into polynomial algebra on affine chains, which this epic
     shows are the only candidates for native composition.
   - **Uncertainty.** Whether gaps in the arrival sets are forced.
2. **The pulse law.**
   - **Payoff 2.** It would make the intermittent network's law explicit.
   - **Concreteness 2.** It needs the polynomials of a chain, not only of a ring.
3. **Learning a rule from its knots.** Carried.

**Recommendation.** Research directions. Direction 1 is the fallback the coordinator named, now sharpened to affine chains. Stop
the process line if it finds that arrival sets of affine chains always have gaps.
