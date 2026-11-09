# Rescue on maps of higher genus

Epic `RESCUE-GENUS-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `RESCUE-MAP-20261109-001` classified the tori that read distance plainly: apart from finitely many small
  ones, those holding a short loop along which the fastest way to every ring is a single route. `PLAIN-TIME-20261108-001` had found 141
  of 706 regular maps of genus at least 2 on time, with no rule by type, genus, curvature or size. Backlog B27 asked whether the tori's
  mechanism rescues them too; the coordinator selected it on 2026-11-09.
- **The question.** In the on-time maps of higher genus, is every ring reached, at one of its closest contacts, by a single shortest
  route, as on the tori, or do odd numbers of several routes rescue rings too? Does the answer hold on groups not read before?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The same mechanism rescues higher genus.** On seven groups not read before, every one of the 77 on-time regular maps of genus at least 2 (of 1,056) has, at every ring and for every contact it does not hold, a closest contact reached by a single shortest route. | exploratory census, exact, frozen hypothesis held | A |
| 2 | **One exception in 218 on-time maps.** On the earlier roster a map of S6 of type (6, 6), genus 61 and 120 rings, rescues two rings by counts of 2, 2 and 3 routes: an odd count of several routes, not a single one. | exploratory census, exact | A |
| 3 | **Ties beside a single route are common.** In 131 of the 218 on-time maps some ring has a tied closest contact beside one reached by a single route (2.4% of on-time ring–target pairs); the single route rescues it. | exploratory census, exact | A |
| 4 | **Shallow ties are harmless, so far.** Every map whose diameter is within two of its first tie is on time (19 maps, all on the earlier roster); no such map occurs on the new roster. | exploratory census, exact | A |

## Answer

Yes. Maps of higher genus are rescued as tori are: a map reads distance without freezing when every ring keeps, at one of its closest
contacts, a fastest way that is a single route. The frozen hypothesis held on all 77 on-time maps of seven new groups; the only ring
rescued otherwise, by an odd count of several routes, is in one map of S6. What decides whether a map keeps a single fastest way at
every ring is still not a rule by type, genus, size or depth of ties.

## Reading

**Interpretation, not a theorem.**
- **Uniqueness, not parity.** The plain first need asks for an odd count, but the maps that pass almost never use more than one route:
  parity rescues a ring once in 218 maps. Reading distance plainly is, in practice, having a unique fastest way.
- **The tori's picture carries over.** On tori the unique fastest way comes from a short loop; on higher genus it comes from however
  the map wraps, and the census does not say which wrappings keep it.
- **Given, not grown.** The maps are given by groups, not grown from a law.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Distances and counts are exact, by breadth-first search.
- **Census-only.** Every conclusion: the rosters only, orientably regular maps only.

## Stress test

The new roster is the stress test: seven groups beyond the pilot's, with H1 frozen before they were read (pre-registered in dee5004a4).
H1 passed with no counterexample on 1,056 maps. The run took 29 minutes and is registered in `docs/LONG_RUNNING.md` as RESCUE-GENUS-A1,
folded in.

## Literature and provenance

- **Sources.** Regular maps from generating pairs of finite groups (Conder's census; Coxeter and Moser); geodesic counts in quotients of
  hyperbolic tessellations; `PLAIN-TIME-20261108-001A`'s construction.
- **Classification.** New as far as found for the question asked: the mechanism by which finite maps of higher genus read distance
  plainly.

## Workspace assumptions

- **Relied on.** A30, A32, A40, A41.
- **Added.** None.
- **Scope.** Orientably regular maps of genus at least 2 of rule-60 rings with equally spaced law-(12, 12) contacts.

## Ratio

Since the epic opened:
- **Substantive.** One exploratory census (A), pre-registered.
- **Administrative.** The pre-registration, this note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — rescue on maps of higher genus | **Status:** Successful | The tori's mechanism holds out of sample on every new on-time map; one exception in 218 |
| Local direction — reading distance plainly | Research directions | What makes a map keep a single fastest way at every ring is not known beyond tori |
| Broader exploration — G5 | Known alternatives | The even-index mechanism (B30, the coordinator's call); B20, B22, B25, B26, B28, B29, B31 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Plain reading of distance is unique fastest ways, on tori by proof and on higher genus by census |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained); B27 taken; backlog B34 and B35 added. **Assumptions:** none
added or changed.

- **What the attempt leaves open.** A criterion on the map for keeping a single fastest way at every ring; why the S6 map's odd counts
  appear; whether irregular networks behave the same.
- **The missing bridge to the program's composed topology.** A law that grows a network keeping a single fastest way to every ring as it
  grows; the twist tube is one such network, not grown by any law found so far.

**Next step:** Research directions — none selected; the coordinator decides whether the even-index mechanism (B30) gets its own thread.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Growing a single fastest way (G1, with G5) | 3/3 — Major | 1/3 — Stated | Find a growth law whose stages keep a single fastest way at every ring, starting from the twist tube → a law that grows a network reading its distance plainly, or the obstruction | Alternative · deferred |
| 2 | The even-index mechanism (B30, G5) | 2/3 — Substantial | 1/3 — Stated | As in the backlog | Backlog |
| 3 | A criterion on the map (G5) | 2/3 — Substantial | 1/3 — Stated | Relate a map's shortest non-contractible walks to the rings whose fastest ways tie → a rule that predicts the on-time maps, or a counterexample | Alternative · deferred |
| 4 | The S6 exception (G5) | 1/3 — Minor | 3/3 — Ready | Read the two rings of the S6 map of type (6, 6), genus 61, and their routes → why three routes arrive, or a second such map | Alternative · deferred |

1. **Growing it.** Payoff 3: a law that grows networks reading their own distance without freezing would be question 9's space from a
   law, read across time; Concreteness 1: no growth law keeps the property yet.
2. **Even index.** As B30.
3. **A criterion.** Payoff 2: it would turn the census into a rule; Concreteness 1: no candidate yet.
4. **S6.** Payoff 1: one map; Concreteness 3: it is in hand.

**Recommendation.** Research directions, none selected: the coordinator asked to decide on B30 from this report; directions 1 and 3 go to
the backlog as B34 and B35.
