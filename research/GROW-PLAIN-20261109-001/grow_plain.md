# Grow a single fastest way

Epic `GROW-PLAIN-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `RESCUE-MAP-20261109-001` and `RESCUE-GENUS-20261109-001` found that a network reads its distance across time
  without freezing when every ring keeps a single fastest way to every contact: proved on tori, where it needs a short loop such as the
  twist (2, 1), and by census on higher genus, with one exception, a map of S6. Backlog B34 asked for a growth law that keeps the
  property; the coordinator selected it on 2026-11-09, after a bounded first step on the S6 exception.
- **The question.** Why is the S6 map rescued otherwise? Is there a law that grows a network reading its own distance plainly at every
  stage, starting from the twist tube, and what does it grow?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The S6 exception is a three-way tie between lifts.** Its two odd-rescued rings (exchanged by the half-turn about the target) each have a closest contact reached at distance 9 by three routes, every pair of which runs round a different handle: three lifts of the target at one distance, one route each. | exact reading | A |
| 2 | **A law grows a network that reads its distance plainly at every stage.** Inserting one ring into the twist torus, a local rewiring that cuts the three contacts spanning the gap and adds five round the new ring, gives the next twist torus; from 4 rings every stage has every contact persistent and is on time. The √3 triangular torus grows the same way from 3 rings, and the ladder by rungs. | proved | B |
| 3 | **Through tori it grows only a line.** Every sequence of on-time tori of unbounded index is eventually a tube, whose balls hold at most 4r + 1 rings: dimension 1. | proved | B |

## Answer

Yes, and it grows a line. One ring at a time, inserted anywhere along the twist tube, keeps every contact persistent and every ring's
fastest way single at every size, so each stage reads its own distance with nothing frozen. The band law loses this at its second band.
But no growth through tori can do it in two dimensions: an on-time torus of large index is a tube. The S6 exception is the one place
where parity, not a single fastest way, rescues a ring: three routes round three handles.

## Reading

**Interpretation, not a theorem.**
- **Space read plainly is a line.** A network of persistent contacts that a law grows can read its own distance across time without
  intervention, but on tori only by staying thin; a plane needs freezing to read its distance (A41).
- **Single-ring growth, rewired.** Attaching a ring breaks persistence (`GROW-NET-20261108-001A`); inserting one, with the contacts across the
  gap rejoined through it, keeps it. The law is local and uniform: the same rewiring at any gap.
- **Wrap-around parity needs handles.** On a surface of high genus a ball wraps round several handles at once, and three lifts can arrive
  together; a torus never uses that.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Distances and counts are exact; persistence is read through half-turns.
- **Census-only.** None: ticket A reads one map exactly, ticket B rests on proofs, its checks confirming them on stages to 60 rings.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Every stage on time and persistent (2) | stages to 60 rings, ladders to 30 rungs (the theorems cover every size) | pass |

No separate stress test was run: conclusion 2 follows from `RESCUE-MAP-20261109-001A`, whose stress test went to index 100 and 140, and
conclusion 1 is one exact reading.

## Literature and provenance

- **Sources.** Homology mod 2 of closed walks on a surface against its face boundaries; `RESCUE-MAP-20261109-001A`'s classification;
  `GROW-NET-20261108-001A`'s half-turn argument; `GROWN-DISTANCE-20261109-001A`'s ladder and balls.
- **Classification.** New as far as found for the question asked.

## Workspace assumptions

- **Relied on.** A30, A32, A40, A41, A42 (a grown network is read stage by stage).
- **Added.** None.
- **Scope.** Tori of rule-60 rings with equally spaced law-(12, 12) contacts, grown by local insertion; one regular map of S6.

## Ratio

Since the epic opened:
- **Substantive.** One exact reading (A) and one proof (B).
- **Administrative.** This note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — grow a single fastest way | **Status:** Successful | A law grows a network reading its distance plainly at every stage; through tori it grows only a line; the S6 exception explained |
| Local direction — space read plainly | Research directions | A two-dimensional network that reads its distance plainly at every size is not a torus, if it exists |
| Broader exploration — G1 with G5 | Known alternatives | Growth chosen by the dynamics (B23, the growth thread); B30, B35 |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | A local law grows a network that reads its own distance across time, but only a line; a plane read plainly needs another substrate |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned); B34 taken; backlog B36 and B37 added. **Assumptions:**
none added or changed.

- **What the attempt leaves open.** Whether any two-dimensional network, not a torus, reads its distance plainly at every size; whether a
  ring inserted while the network runs keeps the bindings it reaches, as bands do not.
- **The missing bridge to the program's composed topology.** A plane that reads its own distance across time without freezing, grown by a
  law; on tori the reading forces a line.

**Next step:** Research directions — none selected, for the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A plane read plainly beyond tori (G1, with G5) | 3/3 — Major | 1/3 — Stated | Look for two-dimensional networks that are not lattice tori (hyperbolic maps with a short loop, mixed lattices) whose balls grow faster than linearly and that are on time at every size → one, or an obstruction like Theorem 2 | Alternative · deferred |
| 2 | A ring inserted while running (G1, with G5) | 2/3 — Substantial | 2/3 — Testable | Insert a ring into the running twist tube, as `GROW-RUN-20261109-001` did with bands, and read which bindings survive → the insertion's light cone, or bindings kept everywhere | Alternative · deferred |
| 3 | Predicting the rescuing loops (B28, G5) | 1/3 — Minor | 2/3 — Testable | As in the backlog | Backlog |

1. **A plane read plainly.** Payoff 3: it would be question 9's space from a law read across time without intervention; Concreteness 1: no
   candidate family yet, and Theorem 2 rules out every torus of the three lattices.
2. **Running insertion.** Payoff 2: it tells whether single-ring growth can happen while the network runs; Concreteness 2: GROW-RUN's reading
   carries over.
3. **Prediction.** As B28.

**Recommendation.** Research directions, none selected; directions 1 and 2 go to the backlog as B36 and B37 for the coordinator to choose.

## Final report as sent

Sent to the owner on 2026-11-09 at 21:25 UTC and copied here verbatim.

Grow a single fastest way (B34) is closed and published (GROW-PLAIN-20261109-001), with the S6 exception explained first.
- **A law grows a network that reads its own distance plainly at every stage (proved).** Insert one ring into the twist torus ⟨(2,1),(N,0)⟩ by cutting the three contacts that span the gap and rejoining them through the new ring (five new contacts). The result is the next twist torus. From 4 rings on, every stage keeps every contact persistent (a half-turn at every contact) and every ring's fastest way single, so it reads its distance across time with nothing frozen. The √3 triangular torus grows the same way from 3 rings, and the ladder grows by rungs. The band law loses this at its second band.
- **But only a line (proved).** Any growth through tori that keeps the reading at every stage ends up in a tube, because an on-time torus of large index holds a family vector. Its balls then grow by 4 rings per step, so it's dimension 1. A plane read plainly would have to be something other than a torus of these lattices.
- **The S6 exception (exact).** Its odd-rescued ring has three routes to a closest contact, and each pair runs round a different handle. That's three lifts of the target arriving at one distance: parity by wrap-around, which no torus does.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: grow a single fastest way | Successful | A growth law keeps the plain reading at every stage; through tori it makes only a line; S6 explained |
| Local direction: space read plainly | Research directions | A two-dimensional network read plainly at every size isn't a torus, if one exists |
| Broader exploration: G1 with G5 | Known alternatives | Growth chosen by the dynamics (B23, growth thread); B30, B35 |
| Long-term goal: G1 Space from a law | Obstruction learned | A local law grows space that reads its own distance across time, but only a line |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | A plane read plainly beyond tori (B36) | 3/3 | 1/3 | Hyperbolic maps with a short loop or mixed lattices, on time at every size with superlinear balls → one, or an obstruction |
| 2 | A ring inserted while running (B37) | 2/3 | 2/3 | Insert a ring into the running twist tube, as GROW-RUN did with bands → its light cone, or bindings kept |
| 3 | Predicting the rescuing loops (B28) | 1/3 | 2/3 | As in the backlog |

**Corrections:** none. This doesn't change any GROW-RUN or GROWN-DISTANCE claim. One note on GROW-NET-20261108-001A: its Theorem 2 (attaching a ring breaks persistence) still holds as stated, but the insertion here also adds one ring at a time and keeps persistence because it rewires the contacts across the gap. Readings that say "single-ring growth breaks persistence" are true only for attachment. **Goals:** a G1 and G5 checkpoint (obstruction learned); B34 marked taken; B36 and B37 added to the backlog. **Assumptions:** none added or changed.

Commits on main: fd9d2bc5d (the epic) and 989286138 (goals doc and knot intuition entry). I staged only my own hunks. Every check was short (none over a minute) and nothing is running. No direction is selected; your call.
