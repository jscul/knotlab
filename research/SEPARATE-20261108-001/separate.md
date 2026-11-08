# Native separation across time

Epic `SEPARATE-20261108-001` (program foundations), 2026-11-08. Backlog B12.

## The question

- **Where it comes from.** `RECUR-PROOF-20261108-001` proved that paths whose rings run rule 60 or 102, with contacts two apart,
  compose at recurring lags with every contact persistent at every ring size and length. Its direction 1 was backlog B12, native
  separation and cycles of rings, which the coordinator relayed to this thread on 2026-11-08. Directions 2 and 3 went to the backlog.
- **The program's order.** Adjacency, then native paths, then separation, and only then distance. Native separation is an
  intervention that meets every native route between two recurrence sets, with reachability before it and a complete account of the
  routes after it that proves their absence (`docs/COMMON_VERBIAGE.md`).
- **The question.** On the proved families, does cutting a contact separate the ends of a path at every lag? And in four rings closed
  into a cycle, does one cut still separate?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Routes are walks of reads.** A contact's value at lag T depends on a first-row cell exactly when the number of walks of length T from it to that cell in the reads graph is odd. Cutting a contact, freezing it so that it reads nothing, removes every walk through it. | proved | A |
| 2 | **A cut separates a path.** In the proved paths of n rings the last contact needs the first ring at the lags with C(T − (n − 1), e) odd. After cutting any one contact it needs the first ring at no lag, and every other contact still binds both of its rings at every lag: a native separation across time. | proved; checked on 1,686 paths of 3 to 8 rings and on full state spaces | A |
| 3 | **A cycle needs two cuts.** Four rings closed into a cycle with two routes from R_0 to R_2: every contact persists, and R_2's two contacts need R_0 at the two routes' binomial lag sets. Cutting a contact on one route removes exactly that route's lags, so it does not separate; one cut on each route does. The least separating cut has the size of the number of routes, as Menger's theorem says. | proved; checked on 636 cycles at sizes 4 to 24 and on full state spaces | A |
| 4 | **Routes come from the laws.** With the same four contacts oriented round the cycle, every route from R_0 to R_2 passes through one contact, and one cut separates. | computed (208 cycles) | A |

## Answer

The stop rule's first outcome holds. Native separation exists across time on the proved families. Cutting any contact of a path stops
the far end needing the first ring at every lag, while the rest of the path keeps its contacts. In a cycle of four rings with two
routes, one cut leaves the other route's composing lags intact and two cuts separate. Which contacts must be cut is fixed by the
laws, through the routes their reads make.

## Reading

**Interpretation, not a theorem.**
- **Where the program stands across time.** With these families the order's first three steps are in place in one declared
  substrate:
  - contacts that pass the gate;
  - native paths that transport (under A37);
  - native separation, here proved.

  Distance is next in the order, and it waits on the owner's pending decision about counted length as a native magnitude.
- **What a cycle adds.** It is the first structure across time with two disjoint routes, so cut size starts to measure something
  relational: how many routes join two rings. That is a count of routes, not a length or a metric.
- **The intervention.** A cut freezes the contact (A38, added). Other cuts are possible, such as a contact that stops reading one
  of its rings.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| A cut separates a path (2) | 3 to 8 rings at sizes 4 to 14, every choice of positions and every cut, and 300 random paths mixing rules 60 and 102 | pass: 1,686 paths |
| A cycle needs two cuts (3) | sizes 4 to 24, all 16 choices of positions, every cut of one or both route contacts, and 300 random mixtures | pass: 636 cycles |
| Full state spaces (2, 3) | three rings at sizes 4 and 5, four rings at size 4, cycles at sizes 4 and 5, every cut | pass: 272 readings |

## Literature and provenance

- **Sources.** Menger's theorem (Menger 1927); walks counted by matrix powers; `RECUR-PROOF-20261108-001`'s binomial coefficients.
- **Classification.** Ticket A: known-with-delta. The delta is the reading across time, a route being a chain of reads whose count
  fixes a contact's dependence at each lag.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags).
- **Added.** A38: a contact is cut by freezing it.
- **Scope.** Linear networks of rings with rule 60 or 102 and the stated laws.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with its checks.
- **Administrative.** This note, the closure, and backlog entries B13 and B14.

## Pending the owner

- **Counted length as a native magnitude**, carried and now in the way of the next step: it decides whether the number of contacts
  or lags along a route may serve as a distance across time.
- Carried from earlier epics: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the
  SELECTION-NOTE erratum; superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — native separation across time | **Status:** Successful | A cut separates a path; a cycle needs one cut per route; proved |
| Local direction — composed topology across time | Continue | Cycles with feedback, where influence returns to its source, are the next structure |
| Broader exploration — G5 with G1 | Known alternatives | The rule-90 mechanism (B13); the gate's restrictions (B14); distance, once the owner rules on counted length |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Adjacency, native paths and separation now exist across time in one substrate |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** A38 added.

- **What the attempt leaves open.**
  - Cycles in which influence goes all the way round and returns, so that Lemma 1's feed-forward condition fails.
  - Distance across time, which needs the owner's ruling on counted length.
- **The missing bridge to the program's composed topology.** A loop of rings whose influence returns to its source while every
  contact still persists: the first closed route across time.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Closed loops of rings across time (G5, with G1) | 3/3 — Major | 2/3 — Testable | Orient four rings round a cycle with the first contact also reading the chain from the last, so influence returns to its source; test persistence and composition at sizes 4 to 12, then prove or locate the failure → a persistent loop of rings across time, or the obstruction | Selected · not started |
| 2 | The rule-90 mechanism (backlog B13) | 2/3 — Substantial | 2/3 — Testable | Parked | Backlog |
| 3 | The gate's restrictions under A37 (backlog B14) | 2/3 — Substantial | 3/3 — Ready | Parked | Backlog |
| 4 | Distance across time | 3/3 — Major | 1/3 — Stated | Waits on the owner's ruling on counted length as a native magnitude | Alternative · deferred |

1. **Closed loops.**
   - **Payoff 3.** A loop whose influence returns is the first closed route across time, the step from paths to cycles in the
     composed topology.
   - **Concreteness 2.** The networks library handles it; Lemma 1 fails there, so the proof needs a new argument.
   - **Uncertainty.** Whether feedback round the loop cancels a contact's dependence on its partners.
2. **The rule-90 mechanism.** Parked as B13.
3. **Restrictions.** Parked as B14.
4. **Distance.** Waits on the owner.

**Recommendation.** Continue with direction 1, and put the counted-length question to the owner through the coordinator, since it
gates distance, the order's next step.
