# Closed loops of rings across time

Epic `LOOP-RINGS-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `SEPARATE-20261108-001` proved native separation across time on paths and on a cycle of four rings whose
  influence runs from one ring to the opposite one. Its direction 1 was a closed loop, in which influence goes all the way round and
  returns to its source. The coordinator relayed the go-ahead on 2026-11-08.
- **Why it is harder.** In the proved paths each contact is a closed loop with its two partners, fed from upstream. In a closed loop of
  rings the input comes back round, so that argument no longer applies, and the returning signal could cancel a contact's
  dependence on its own rings.
- **The question.** Can a closed loop of rings keep every contact binding both of its rings at every lag while influence returns
  round it?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Closed loops can persist.** Of 295,056 loops of three and four rule-60 rings, with every contact reading the chain that arrives from the contact before it, 2,707 keep every contact persistent. All 31 at size 4 agree on their full state spaces. The smallest has three rings of four cells, each contact reading its left neighbour on both of its rings. | exploratory census; every verdict exact | A |
| 2 | **How.** In the persistent loops each contact reads the chains from both neighbouring contacts, one on each ring. Under rule 60 each ring then carries a circuit through its two contacts. | exploratory | A |
| 3 | **Some loops transport.** 54 families of four-ring loops persist at every size from 4 to 16, and all of them mix the contacts' positions, half the rings at cell 2 and half at cell s − 2. No three-ring family persists at every size. | exploratory, exact at each size | A, decision note |
| 4 | **Influence returns.** In 2,659 of the 2,707 persistent loops every contact needs the rings it does not touch at some lag of its cycle, never at every lag: composition round the loop at recurring lags (A37). | exploratory, exact | decision note |

## Answer

The stop rule's first outcome holds for each loop found: persistent closed loops of rings exist across time, each one decided
exactly. Influence goes round them, and every contact needs the rings it does not touch at recurring lags. 54 four-ring families keep
this at every size tested, up to 16 cells. There is no proof for every size yet: the feedback round the loop is what the path proofs
avoided.

## Reading

**Interpretation, not a theorem.**
- **For composed topology across time.** A closed route, a loop of rings whose influence returns to its source while every contact
  stays complete, is the first closed structure of contacts across time. It is to paths what a cycle is to a line.
- **What makes it work.** Persistence survives feedback only when each contact listens to both of its neighbours. Then every ring
  becomes a circuit running through its two contacts.
- **Sizes.** Only four-ring loops with mixed positions persist at every size tested, so transport depends on balance round the loop.
- **Not a metric.** Nothing here is a length or a distance.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Closed loops can persist (1) | all 31 persistent loops at size 4 on their full state spaces | pass |
| Some loops transport (3) | the families persistent at sizes 4 to 10, at sizes 11 to 16 | pass: all 54 |

## Literature and provenance

- **Sources.** Linear recurring sequences over GF(2); Boolean automata cycles that intersect, studied for their asynchronous dynamics
  (Alcolei, Perrot and Sené 2015; Demongeot, Noual, Sené and coauthors).
- **Classification.** Ticket A: new as far as found, persistent closed loops of contacts across time.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags).
- **Scope.** Rule 60 rings (rule 102 by mirror symmetry), the declared laws, three and four rings, sizes 4 to 16.

## Ratio

Since the epic opened:
- **Substantive.** One evidence family (A, the census) and its characterisation.
- **Administrative.** This note and the closure.

## Pending the owner

- **Counted length as a native magnitude**, which gates distance across time; put to the owner by the coordinator on 2026-11-08.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — closed loops of rings | **Status:** Successful | Persistent closed loops exist, exact for each loop; 54 families persist at every size to 16 |
| Local direction — composed topology across time | Continue | A proof for every size, the analogue of the path theorem with feedback, is the next step |
| Broader exploration — G5 with G1 | Known alternatives | The rule-90 mechanism (B13); the gate's restrictions (B14); distance, once the owner rules |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Closed loops of contacts, the first closed routes across time, exist |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.**
  - A proof that the 54 families persist at every ring size.
  - Why three-ring loops never transport and four-ring loops need mixed positions.
- **The missing bridge to the program's composed topology.** A proved closed loop at every size, and then loops that share rings.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the four-ring loops persist at every size (G5, with G1) | 3/3 — Major | 2/3 — Testable | Write each contact's value by generating functions over GF(2): chains as powers of z/(1 + z), the loop as a circulant system; show some cell of each ring keeps coefficient 1 at every lag for the balanced positions → a theorem for every size, or the size where it fails | Selected · not started |
| 2 | The rule-90 mechanism (backlog B13) | 2/3 — Substantial | 2/3 — Testable | Parked | Backlog |
| 3 | The gate's restrictions (backlog B14) | 2/3 — Substantial | 3/3 — Ready | Parked | Backlog |
| 4 | Distance across time | 3/3 — Major | 1/3 — Stated | Waits on the owner's ruling on counted length | Alternative · deferred |

1. **Prove the four-ring loops.**
   - **Payoff 3.** It would make the first closed route across time hold at every size, as the path theorem does for paths.
   - **Concreteness 2.** The chains have closed forms, and the loop is a circulant system over GF(2)((z)). The cancellation of closed
     walks, C(2p, p) even, is a first handle.
   - **Uncertainty.** Whether a single cell's coefficient carries persistence, or only a union of cells does.
2. **The rule-90 mechanism.** Parked as B13.
3. **Restrictions.** Parked as B14.
4. **Distance.** Waits on the owner.

**Recommendation.** Continue with direction 1. If no single-cell witness exists, look for a union of cells forced by the balance of
positions, and stop with the size where the families first fail if they do.
