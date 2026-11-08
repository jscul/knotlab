# Make the surface by growing whole bands

Epic `BAND-SURFACE-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `GROW-NET-20261108-001` proved that a lattice of rings on a torus grows by whole bands with every contact
  persistent, but the torus was given. Its direction 1, relayed by the coordinator on 2026-11-08 as the open half of the owner's
  question: find band insertions that start from a loop of rings and close a torus with every stage balanced, or the step where every
  band fails.
- **The question.** Can the band law make the torus from a loop, not only fill a torus it is handed?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **One band makes the torus.** Inserting a band into a loop of n rings joins each new ring to its partner on both sides, which gives the n × 2 torus. Every n × m torus with n ≥ 3 and m ≥ 2 has a half-turn at every contact, so the loop, the n × 2 torus and every later torus are balanced. | proved; checked for n = 3 to 12 and at cell level | A |
| 2 | **Where the band sits decides the surface.** Of 1,813,632 ways to place a first band, the balanced ones lie on a sphere only once (the cube), on the torus for the n × 2 tori and for single rungs on loops of 4, 6 and 8 rings, and otherwise on surfaces of genus 2 to 4, mostly with no flip at every contact. | exploratory census, exact | B |

## Answer

The stop rule's first outcome holds. Starting from a loop of rings, the band law makes the torus at its first step and keeps every
contact persistent at every stage after: loop, n × 2 torus, n × 3 torus, and so on. No band had to fail.

## Reading

**Interpretation, not a theorem.**
- **A band round both sides is a handle.** A loop of rings sits on a sphere with two faces. A band joined to it on both sides runs through
  both faces at once, and that closes a handle: the surface becomes a torus in one step, with every contact still persistent.
- **For G1.** A uniform local law, insert a band, now makes the torus from a loop and grows the lattice on it, with every contact a
  persistent knot across time at every stage. What the law does not choose is where the band goes; the rule fixes that.
- **Beyond the torus.** Balanced first bands on surfaces of genus 2 to 4 exist, most with no symmetry, so bands may grow higher genus
  too; whether later bands keep them balanced is open.
- **Not a metric.** Nothing here is a length or a distance.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Return counts are followed until the next vector lies in the span of the earlier ones; rows of M^T until they repeat.
- **Census-only.** Conclusion 2.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| One band makes the torus (1) | loops of 3 to 12 rings, and tori up to 10 × 6 including every side of two | pass |
| Where the band sits decides the surface (2) | single rungs on a loop of 8 rings, one past the scratch run | pass: the pattern holds (torus for even n, no sphere) |

## Literature and provenance

- **Sources.** Rectangular tori and their half-turns; regular maps {4,4} (Coxeter and Moser).
- **Classification.** Ticket A: known-with-delta. Ticket B: new as far as found, a census.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags).
- **Scope.** Equally spaced networks of rule-60 rings with law (12, 12) contacts.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with five checks, and one census (B).
- **Administrative.** This note and the closure.

## Pending the owner

- Nothing.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — making the surface by bands | **Status:** Successful | One band makes the torus from a loop, every stage balanced, by proof |
| Local direction — growth from a law | Research directions | The torus is made; higher genus by bands is the open next |
| Broader exploration — G1 with G5 | Known alternatives | Full reach on the cut-open torus (ready); which lattices compose everywhere (ready); growth chosen by the dynamics |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A uniform local law makes a surface, the torus, from a loop, with every contact persistent at every stage |

**Corrections:** none. **Goals:** a G1 checkpoint with G5 (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.**
  - Whether later bands keep the balanced first bands of genus 2 to 4 balanced, so that bands grow surfaces of higher genus.
  - Whether the network's dynamics can choose where a band goes.

**Next step:** Research directions — the stop rule is met in its first outcome; the next question is either higher genus by bands or
the ready proof of full reach.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Higher genus by bands (G1, with G5) | 3/3 — Major | 2/3 — Testable | Add a second band to the balanced genus-2 first bands (loops of 5 rings) in every way → a balanced genus-2 network after two bands, or the step where every band fails | Alternative · deferred |
| 2 | Prove full reach on the cut-open torus (`FULL-REACH-20261108-001`) | 2/3 — Substantial | 3/3 — Ready | Images of the doubled torus and the powers of two → a proof, or the first failing side | Alternative · deferred |
| 3 | Which lattices compose everywhere (`LATTICE-NET-20261108-001`) | 2/3 — Substantial | 3/3 — Ready | Rectangular, triangular and honeycomb tori → a characterisation, or the first counterexample | Alternative · deferred |
| 4 | Growth chosen by the dynamics (G1, with G5) | 2/3 — Substantial | 1/3 — Stated | Let a contact's needs pick where the next band goes → a law, or none | Alternative · deferred |

1. **Higher genus.** The census gives balanced starting points of genus 2 to 4; the search for a second band is bounded and exact.
2. **Full reach.** Ready; the coordinator's fallback.
3. **Which lattices.** Ready.
4. **Dynamics-driven growth.** Open-ended.

**Recommendation.** Research directions, leaning to direction 1 for G1 or direction 2 as the coordinator's ready fallback.
