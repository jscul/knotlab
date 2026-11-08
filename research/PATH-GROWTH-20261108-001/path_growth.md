# Native paths that survive growth

Epic `PATH-GROWTH-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `PATH-HYBRID-20261108-001` found native four-ring paths across time, 16 with one rule per ring and 1,120
  with hybrid middle rings, none of which survives growing a ring. Its direction 1 was relayed by the coordinator on 2026-11-08 with
  the stop rule: a family native at every size from 3 to 9, or evidence that binding at every lag is tied to sizes, which would put
  A34 under challenge.
- **The question.** Fix each ring's linear rule and each contact's law, and let the path grow. Is some family native at every size?
  - **Ticket A.** Four rings growing together, 3 to 9 cells, with the middle rings' contacts antipodal or two apart; and paths growing
    from 4 to 9 rings.
  - **Ticket B.** Where growth breaks a path, persistence or composition, and a map of the shapes around 3/5/5/3.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No family survives growth.** With all four rings of 3, 4 or 5 cells, none of 36,864,000 paths is native, under every linear rule and every law, so no family of the two four-ring schedules can be followed. Of the longer families, 8 are native at four rings, the known construction, and none at five rings (0 of 1,024,000). | exploratory search (H1 fails); every verdict exact; the natives verified on full state spaces | A |
| 2 | **Growth breaks composition, not persistence.** At every level some paths keep all three contacts persistent (424 to 12,916), and their row cycles are short: of 24,650, all but 536 have a period of at most 12. None of them is native except at 3/5/5/3. | exploratory measure, exact | B |
| 3 | **Native paths sit at isolated shapes.** In a map of 90 shapes (end rings of 3 to 5 cells, middle rings of 4 to 7), native paths occur at 3 of the 36 size combinations: 3/5/5/3 (16), 5/6/6/5 (48, rule 90 end rings and the one-sided additive rules 60 and 102 in the middle) and 4/7/7/5 (16). With rule 150 on all four rings, 48 more sit at five shapes with an end ring of 6 cells or a middle ring of 8, 6/5/5/6 among them. No family is native at two shapes of the map. None of the 128 stays native when every ring, the end rings or the middle rings grow by one. | exploratory, exact; the smallest at each new shape verified on its full state space (`new_natives.json`) | B, decision note |

## Answer

No family of paths with one rule per ring survives growth. Native paths across time exist at a scatter of shapes, nine found so far,
each family at one shape, and none survives growing its rings by one cell or adding a ring. The rings themselves keep remembering
as they grow: what fails is composition, the last contact needing both ends' pasts at every lag. By the epic's stop rule, binding at
every lag is tied to particular sizes, and A34 is put under challenge.

## Reading

**Interpretation, not a theorem.**
- **For the gate.** Every native path found passes each contact gate and composes, and the composition is native. But no tested
  family keeps it under growth, which is the transport the network gate asks for. Under A34 a native network across time exists only
  at isolated sizes.
- **Why A34 is under challenge.** A34 reads composition as binding at every lag. Under that reading composition across time does not
  transport in any family tested. `INTERMITTENT-NET-20261108-001` found that intermittent composition, at recurring lags with the
  phase fixed by the chain itself, holds at every tested size for twenty rule-law pairs of three-ring chains. The alternative reading
  is the one that has transported so far.
- **Not long cycles.** Persistent paths keep short row cycles at every size, so long cycles do not explain the absence of
  composition. The heuristic of `PATH-HYBRID-20261108-001` said they did; it is corrected.
- **The recurring family.** Every native path found is affine: shifts, rules 150 and 90, and the one-sided additive rules 60 and 102.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| No family survives growth (A) | the followed families taken through every size of their schedules, to 9 cells or 9 rings | pass: the 8 followed families fail at five rings |
| Native paths sit at isolated shapes (B) | each of the 128 native paths found away from or beside 3/5/5/3 with one more cell on every ring, on the end rings or on the middle rings, contacts kept antipodal or at their distance (`new_natives.json`) | pass: none stays native |
| The new native paths are native (B) | the smallest at each new shape on its full state space | pass: 7 of 7 |

## Corrections

Two, logged in `docs/CORRECTIONS.md` with correction sections in the earlier notes.
- **Narrowing.** `NATIVE-PATH-20261108-001` found no native path with rule 150 on all four rings up to end rings of 5 cells, and its
  wider run NATIVE-PATH-S1, folded in here, finds 48 with end rings of 6 cells or a middle ring of 8. `PATH-HYBRID-20261108-001`'s
  answer, "with one rule per ring there is a single construction of 16 paths", holds only in its sweep's shapes: ticket B finds
  others at 5/6/6/5 and 4/7/7/5.
- **Not a block.** `PATH-HYBRID-20261108-001`'s heuristic that larger rings fail because their cycles grow long holds for its
  construction's larger versions, not in general (conclusion 2).

## Literature and provenance

- **Sources.** Linear recurring sequences over GF(2); additive automata on rings (Martin, Odlyzko and Wolfram 1984); xor-cycle chains
  (Alcolei, Perrot and Sené 2015) as the nearest substrate.
- **Classification.** Tickets A and B: new as far as found, a census of native paths across time by size.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A34 (composition at every lag), A36 (not needed here: every ring is uniform).
- **Status changed.** A34 is under challenge.
- **Scope.** Linear rules, contact laws by their linear parts, the declared families, schedules and shapes.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions: A (the size sweep) and B (the funnel and the map, with the checks of
  the new native paths). One long-running stress test of an earlier epic folded in, with a correction.
- **Administrative.** This note, the closure, and the data left for the separation thread.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — native paths that survive growth | **Status:** Negative evidence | No family survives growth; native paths sit at nine isolated shapes |
| Local direction — paths across time | Research directions | Under A34 composition does not transport; the stop rule puts A34 under challenge |
| Broader exploration — G5 with G1 | Known alternatives | Native separation and cycles of rings (B12, its own thread); hybrid rings that grow; nonlinear paths (B10) |
| Long-term goal — G5 Dynamics (question 4) | Obstruction learned | Composed topology across time exists, but only at isolated sizes under the every-lag reading |

**Corrections:** two, a narrowing and one not a block. **Goals:** a G5 checkpoint (obstruction learned). **Assumptions:** A34 put
under challenge.

- **What the attempt leaves open.**
  - Whether composition at recurring lags, A34's alternative, survives growth in paths.
  - Families beyond one linear rule per ring: hybrid rings with a repeating pattern, nonlinear rules.
  - Why composition sits at the shapes it does.
- **The missing bridge to the program's composed topology.** A native path whose composition survives the admitted transports,
  under one reading of composition across time.

**Next step:** Research directions — the epic's hypothesis failed, and the stop rule names the next step: a challenge of A34.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Challenge A34: composition at recurring lags across sizes (G5) | 3/3 — Major | 3/3 — Ready | Extend INTERMITTENT-NET's test of composition at recurring lags, with the phase fixed by the path, to four-ring paths, and run it on ticket A's growth families at every size → a family that composes this way at every size, which would favour the alternative reading, or none, which would leave composition across time tied to sizes under both readings | Alternative · deferred |
| 2 | Native separation and cycles of rings (backlog B12) | 3/3 — Major | 2/3 — Testable | Parked for its own thread; the data is in `research/PATH-HYBRID-20261108-001/native_paths.json` | Backlog |
| 3 | Hybrid rings that grow (G5) | 2/3 — Substantial | 2/3 — Testable | Hybrid middle rings with a repeating pattern of cell rules, grown with the ring → a hybrid family native at every size, or none | Alternative · deferred |
| 4 | Why composition sits at particular shapes (G5) | 2/3 — Substantial | 1/3 — Stated | Relate the native shapes to the factorisation of the rings' polynomials over GF(2) → a rule predicting the shapes, or the first shape it misses | Alternative · deferred |

1. **Challenge A34.**
   - **Payoff 3.** It decides whether composition across time can transport under some native reading, the gate's remaining item.
   - **Concreteness 3.** INTERMITTENT-NET's measure exists for chains, and the growth families are defined.
   - **Uncertainty.** Whether the phase the path fixes survives growth.
2. **Native separation.** It ties with direction 1 and runs in its own thread.
3. **Hybrid rings that grow.** Hybrid rings gave the most native paths; whether a repeating pattern grows is untested.
4. **Why these shapes.** No method yet beyond the polynomials' factorisations.

**Recommendation.** Research directions: take direction 1. If no family composes at recurring lags at every size either, record
composition across time as tied to sizes under both readings, and reassess G5 against question 4 before opening more of the
process line.

## Final report as sent

Sent to the owner on 2026-11-08 at 12:35 UTC and copied here verbatim.

PATH-GROWTH is closed and published (epic c2f64bcee, shared docs 76b403cda). No native path survives growth, so by the stop rule A34 is now under challenge. Both long runs are folded in, nothing is pending.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: native paths that survive growth | Negative evidence | No family with one rule per ring is native at two sizes; native paths sit at nine isolated shapes |
| Local direction: paths across time | Research directions | Under A34 composition never transports, so A34 is now under challenge |
| Broader exploration: G5 with G1 | Known alternatives | Separation and cycles of rings (B12, its own thread); hybrid rings that grow; nonlinear paths |
| Long-term goal: G5 (question 4) | Obstruction learned | Composed topology across time exists, but only at isolated sizes when composition means every lag |

- **Equal rings have no native path at all.** With all four rings at 3, 4 or 5 cells, none of 36.9 million paths is native. The longer families that are native at four rings all fail at five.
- **Growth breaks composition, not memory.** Paths whose contacts all persist exist at every size, mostly with short cycles, and none of them composes.
- **The native paths sit at isolated shapes.** In the map they sit at 3/5/5/3, 5/6/6/5 and 4/7/7/5. With rule 150 on every ring there are five more, such as 6/5/5/6. No family is native at two shapes, and none of the 128 survives one more cell. All are affine again, and the smallest at each new shape is verified on its full state space.

Next step: Research directions, selected #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Challenge A34: composition at recurring lags across sizes | 3/3 | 3/3 | Extend INTERMITTENT-NET's recurring-lag test (phase fixed by the path) to four-ring paths and run it on the growth families → a family composing that way at every size, or none (then composition across time is size-specific under both readings) | Awaiting go-ahead |
| 2 | Native separation and cycles of rings (B12) | 3/3 | 2/3 | Parked for its own thread; data in `native_paths.json` | Backlog |
| 3 | Hybrid rings that grow | 2/3 | 2/3 | Hybrid middle rings with a repeating cell pattern, grown with the ring | Alternative |
| 4 | Why composition sits at these shapes | 2/3 | 1/3 | Relate the shapes to how the rings' polynomials factor over GF(2) | Alternative |

**Corrections:** two. (1) Narrowing: NATIVE-PATH found no native path with rule 150 everywhere up to 5-cell end rings, but its wider run finds 48 at 6-cell end rings. PATH-HYBRID's "single construction with one rule per ring" also holds only for its two shapes. (2) Not a block: PATH-HYBRID's heuristic that big rings fail because their cycles grow long holds only for its own construction ([knotlab HISTORY](https://github.com/jscul/knotlab/blob/main/HISTORY.md)).
**Goals:** G5 checkpoint, obstruction learned; the next step is waiting for a go-ahead.
**Assumptions:** A34 (a chain composes when its far contact binds the ends at every lag) is moved from Confirmed to Under challenge.

[Decision note](https://github.com/jscul/knotlab/blob/main/research/PATH-GROWTH-20261108-001/path_growth.md)
