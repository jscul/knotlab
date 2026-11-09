# Growth by every allowed cut at once

Epic `GROW-ALL-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `GROW-CHOOSE-20261109-001` found that growth chosen by the dynamics grows a tube when bands are added one at a
  time, and that its order-free form, a band at every cut where one keeps every contact persistent, all at once, grew both ways at lags
  0 and 1 before its networks passed the run's size limit. The coordinator gave backlog B38 the go-ahead on 2026-11-09 as the bounded
  last test of plane growth: if it stops by lag 3, pivot to B39.
- **The question.** Read the order-free rule past lag 1 on running tubes. Does it keep growing both ways?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Every cut stays allowed: the network doubles.** On the 3 × 3, 3 × 4 and 4 × 4 tubes at g = 2, every cut both ways is allowed at lags 0, 1 and 2 and every combination read persists (lags 0 and 1 on every tube, lag 2 on 3 × 3; the others pass 700 rings), so the rule inserts a band at every cut each lag: both sides double, 3 × 3 to 6 × 6 to 12 × 12 to 24 × 24, every stage read balanced in the whole-history reading. | exploratory, exact per decision | A |
| 2 | **No refusal at lag 3, no confirmation either.** On the 24 × 24 network of lag 3, none of the 48 cuts fails within 50,000 lags, and none of their states repeats within that, so all are unknown. No cut was refused at any lag of any tube. | exploratory; a failure would be exact | A |
| 3 | **At g = 3 the readings run out.** On the 3 × 3 tube at g = 3 the 24 cuts of the 12 × 12 network at lag 2 did not repeat within 400,000 steps: unknown, none refused. | exploratory | A |
| 4 | **Every contact is reborn every lag.** A band at every cut cuts every contact, and with the fresh split both halves are born: the rings carry the network's memory, its contacts live one lag each, and "every contact persists" means that whenever growth stops every contact persists from then on. | reading of the rule | A |

## Answer

It does not stop by lag 3. Filling every allowed cut at once finds every cut allowed at every lag read exactly, so the network doubles
both sides each lag, 3 × 3 to 24 × 24, every stage balanced in the whole-history reading: a native, order-free growth law that grows
the declared rings both ways (A45) while the network runs, where one band at a time grows a tube or breaks. At lag 3 nothing is refused
but the readings run out. The price is that every contact is cut and reborn each lag: the rings carry the memory, and the stages, square
tori with both sides at least 6, read distance only through freezes (`GROWN-DISTANCE-20261109-001A`, Theorem 3). By the coordinator's
rule the line does not pivot to B39; the next step is B19's own question on this network: distance and balls while it doubles.

## Reading

**Interpretation, not a theorem.**
- **Doubling is the band law's order-free form.** Filling every allowed cut is splitting every ring into a 2 × 2 block at every lag, the
  block growth `GROW-NET-20261108-001` proved balanced stage by stage; here it keeps every stage balanced while the network runs, where
  one band at a time does not (`GROW-RUN-20261109-001`). What the doubling avoids is a cut through old influence that the rest of the
  network does not share: every old ring is cut the same way at once.
- **A plane, with a price.** The rule grows both ways, so its balls grow like the plane's at every scale reached, but its contacts are
  renewed every lag; only the rings persist across growth.
- **Causal horizons to come.** Influence crosses a ring in about 2g lags while the rings between two old rings double every lag, so no
  old ring's influence can reach its old neighbour: the doubling network's balls of influence should stay bounded in the old lattice's
  terms. That is B19's question on a network that grows both ways, and the next step.

## Lag cutoffs and census-only claims

- **Exact per decision at lags 0 to 2** (a full period of the state, at most 400,000 steps); at lag 3 a refusal is exact and "no failure
  within 50,000 steps" is recorded as unknown.
- **Census-only.** All conclusions: four tubes, lags 0 to 3.

## Stress test

| Claim | Check | Result |
| --- | --- | --- |
| The doubling run is read correctly | An independent re-implementation of the doubling with actual bits (random first row and births, one first-row cell flipped at a time), against the run's dependence sets, lags 1 to 14 with doublings at lags 0, 1 and 2 | pass: 112 flips, 0 mismatches |
| choose_lib's row insertions | against `GROW-RUN-20261109-001A`'s growrun_lib, validated by actual bits there, four splits, 20 lags after an insertion at lag 5 | pass: 0 mismatching lags |

One size past the tubes (5 × 5 and larger) is not run: their lag-2 networks pass 700 rings. The checks are `validate.py` beside this note,
its output `validate.json`.

## Literature and provenance

- **Sources.** Block growth of tori (`GROW-NET-20261108-001`); self-similar substitution growth (a 2 × 2 block per tile); additive
  cellular automata on growing graphs.
- **Classification.** New as far as found, an exploratory run.

## Workspace assumptions

- **Relied on.** A30, A32, A42 (confirmed), A44 (born cells open), A43 (confirmed: one band at a time grows one way).
- **Added.** None.

## Ratio

Since the epic opened:
- **Substantive.** One frozen exploratory run (A) on four tubes; one independent validation.
- **Administrative.** This note and the closure; a first launch stopped inside lag 3 and relaunched, recorded in the contract.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — growth by every allowed cut at once | **Status:** Successful | Exact to lag 2: every cut allowed, the network doubles both ways, every stage balanced; nothing refused at lag 3 |
| Local direction — a plane grown by its own dynamics | Continue | The doubling law is the first native law found that grows the declared rings both ways while the network runs |
| Broader exploration — G1 with G5 | Known alternatives | An invertible substrate (B39); a proof of the doubling's balance; the plain reading under re-routing (A45) |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A uniform local law, split every ring into four each lag, grows a plane of rings with every stage balanced while it runs (computed to 24 × 24) |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (capability gained), B38 marked taken, B49 and B50 added. **Assumptions:** none
added; the result is stated for the declared rings (A45).

- **What the attempt leaves open.** Whether every lag stays allowed (a proof); what the doubling network reads as distance and how its
  balls grow while it doubles; whether its contacts' one-lag lives can be read as persistence across growth.
- **The missing bridge to the program's composed topology.** Distance across time on a network that grows itself both ways.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Distance and balls in the doubling network (B19 on a plane that grows itself; B49) | 3/3 — Major | 3/3 — Ready | On the running 3 × 3 tube doubled at every lag, read the time of flight between old rings and the rings each contact needs by each lag, against the ring distance that doubles every lag → a horizon (old rings that never need each other) and the dimension the balls read, or none | Selected · awaiting go-ahead |
| 2 | Why doubling keeps every stage balanced (B50) | 3/3 — Major | 2/3 — Testable | Use the old lattice's translations and half-turns, which the whole history keeps, to pair the returns that could cancel an old ring's binding → a proof for every lag, or the lag where it fails | Alternative · deferred |
| 3 | Growth on an invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | A scratch search found no uniform linear rule with a self-blind contact law that is both invertible and persistent on small tubes; make it exact and complete → a substrate, or the reason none exists | Alternative · deferred |
| 4 | A faster exact persistence reading | 1/3 — Minor | 2/3 — Testable | The eventual period from the minimal polynomial of the fixed network → lag 3 and beyond confirmed or refused | Alternative · deferred |

1. **Distance in the doubling network.** Payoff 3: it is B19's question on the first network a law grows both ways, and a horizon would
   be a native causal structure of growth. Concreteness 3: the run is exact and fast to lag 2 and its stages are known tori.
2. **A proof of the balance.** Payoff 3: it would make the doubling law a theorem at every lag. Concreteness 2: the symmetries are there,
   the pairing argument is not.
3. **Invertible substrate.** Payoff 2: separates rule 60's forgetting from growth. Concreteness 3: a finite search.
4. **Faster reading.** Payoff 1: confirms lag 3. Concreteness 2.

**Recommendation.** Continue with #1, B19's question on the doubling network; stop it at a horizon read exactly or at the lag where
the readings run out.
