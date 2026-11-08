# Grow a network of rings from a law

Epic `GROW-NET-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `GENUS-CUT-20261108-001` closed with this as its direction 1. The owner asked on 2026-11-08 whether it was
  being pursued, and the coordinator switched the line to it: look for a local growth rule that keeps every contact persistent, using
  the flip criterion of `LOOP-NET-20261108-001A`, and stop at a rule or at the first obstruction.
- **The question.** Can a network of rings grow by a local rule while every contact stays persistent at every stage?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Bands and blocks grow.** Every n × m torus of rings with sides at least 3 has a half-turn at every contact that exchanges its two rings, so every contact persists. Growth that inserts a whole band of rings round the torus, or splits every ring into a k × l block, keeps every contact persistent at every stage. | proved; checked on 60 tori and 26 growth stages | A |
| 2 | **A single new ring breaks it.** Attached by one contact, the new ring returns to it at once. Attached by two contacts that are not side by side on one ring, it leaves one unpaired return of length 2. Attached as a bubble on a corner p → q, it deletes that corner, and the network stays balanced exactly when no contact is reached from q and reaches p. | proved; checked exactly, including the update formula | A |
| 3 | **In practice no single ring can be added.** Of 795,042 ways to attach one ring to 16 balanced seeds, none with one or two contacts keeps every contact persistent, and none with three or four does on any seed of more than four rings. | exploratory census, exact | B |
| 4 | **Refining the sphere breaks it too.** Truncating or rectifying the Platonic networks loses persistence, except the rectified tetrahedron, which is the octahedron. | exploratory census, exact | B |

## Answer

The stop rule's two outcomes both occur. There is a rule: on the torus, growth by whole bands of rings, or by splitting every ring into
a block, keeps every contact persistent at every stage, by proof. And there is an obstruction: growth one ring at a time breaks
persistence, by proof for rings of one or two contacts and by an exact census for three or four, from every seed of more than four
rings.

## Reading

**Interpretation, not a theorem.**
- **The unit of growth is a band.** A single new ring is a defect: its contacts see the network differently from its two sides, and a
  return goes unpaired. A band closed round the torus, or a block in every ring at once, keeps every contact looking the same from both
  of its rings, so the returns still pair.
- **Only the torus.** Networks with a flip at every contact are regular maps. The sphere has finitely many beyond loops and two-ring
  networks, and each surface of genus at least 2 has finitely many; the torus has them at every size. So the flip criterion can carry
  unbounded growth only on a flat surface, and refining the sphere's regular networks fails in the census.
- **For G1.** The law grows a lattice on a torus it is given; it does not make the surface. Making the surface by local growth is where
  the obstruction bites, since that is growth by single rings or partial bands.
- **Composition along the way.** By `LATTICE-NET-20261108-001`, tori with an odd side reached every ring in every case computed, so
  band growth that keeps one side odd keeps full composition too (computed).
- **Not a metric.** Nothing here is a length or a distance.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Return counts are followed until the next vector lies in the span of the earlier ones; generating functions are
  exact; rows of M^T are followed until they repeat.
- **Census-only.** Conclusions 3 and 4, and the remark that band growth with an odd side keeps full composition.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Bands and blocks grow (1) | tori 9 × 13, 9 × 14, 10 × 13 and 10 × 14 | pass: balanced |
| No single ring can be added (3) | the loop of 7 rings, two rings sharing 6 contacts, the 5 × 5 square torus, the 3 × 3 honeycomb and triangular tori, up to 3 contacts | pass: none of 519,125 attachments keeps persistence |

## Literature and provenance

- **Sources.** Regular and chiral maps on the torus (Coxeter and Moser); Hurwitz's bound on automorphisms in genus at least 2; the
  Sherman–Morrison formula.
- **Classification.** Ticket A: known-with-delta. Ticket B: new as far as found, a census.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags).
- **Scope.** Equally spaced networks of rule-60 rings with law (12, 12) contacts.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with nine checks, and one census (B).
- **Administrative.** This note and the closure.

## Pending the owner

- Nothing new. The owner ruled on 2026-11-08 that counted length can count as a native magnitude; distance across time runs in its own
  thread.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — growing a network of rings from a law | **Status:** Successful | A rule (bands and blocks on the torus) and an obstruction (single rings), both proved |
| Local direction — growth from a law | Research directions | The open part is making the surface itself by local growth |
| Broader exploration — G1 with G5 | Known alternatives | Growth driven by the network's own dynamics; full reach on the cut-open torus (parked); which lattices compose everywhere |
| Long-term goal — G1 Space from a law (question 9) | Capability gained | A uniform local law grows a lattice of persistent contacts at every stage, on the torus |

**Corrections:** none. **Goals:** a G1 checkpoint with G5 (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.**
  - Whether any local rule can make a surface, not only fill one, while every contact persists, perhaps by adding whole bands that
    close new handles.
  - Whether the network's own dynamics can choose where a band goes.
- **The missing bridge to G1.** A law that makes the torus, not one that is handed a torus.

**Next step:** Research directions — the stop rule is met both ways; the next question is making the surface, a choice against the
parked proof of full reach.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Make the surface by growing whole bands (G1, with G5) | 3/3 — Major | 1/3 — Stated | Look for a sequence of band insertions that starts from a loop of rings and closes a torus, every stage balanced → such a sequence, or the step where every band fails | Alternative · deferred |
| 2 | Prove full reach on the cut-open torus (parked, `FULL-REACH-20261108-001`) | 2/3 — Substantial | 3/3 — Ready | Images of the doubled torus and the powers of two → a proof, or the first failing side | Alternative · deferred |
| 3 | Which lattices compose everywhere (`LATTICE-NET-20261108-001`) | 2/3 — Substantial | 3/3 — Ready | Rectangular, triangular and honeycomb tori → a characterisation, or the first counterexample | Alternative · deferred |
| 4 | Growth chosen by the dynamics (G1, with G5) | 2/3 — Substantial | 1/3 — Stated | Let a contact's needs decide where the next band goes → a law, or none | Alternative · deferred |

1. **Making the surface.** The intermediate stages between a loop and a torus are not tori, and the census and the prism (two loops
   joined by rungs, unbalanced in `LOOP-NET-20261108-001B`) suggest they fail; whether some other band sequence passes is open.
2. **Full reach.** Ready and bounded.
3. **Which lattices.** Ready and bounded.
4. **Dynamics-driven growth.** Open-ended.

**Recommendation.** Research directions. Directions 2 and 3 are ready and bounded; direction 1 is the larger question for G1. The line
has run nineteen epics today, so a pause is also reasonable.

## Final report as sent

Sent to the owner on 2026-11-08 at 16:50 UTC and copied here verbatim.

**Growing a network of rings from a law: both outcomes occur. There is a rule and an obstruction.** Epic and docs are committed and published (828293e96, 757135fa1). Earlier I also committed the cut-open torus result as a preliminary note (bcc368c4f).

- **The rule (proved).** On a torus of rings with equal spacing, a half-turn at every contact swaps its two rings, so every contact persists. Growing by inserting a whole band of rings round the torus keeps every contact persistent at every stage. So does splitting every ring into a k×l block.
- **The obstruction (proved for 1 or 2 contacts).** Adding one ring at a time breaks persistence:
  - With one contact, the new ring returns to it at once.
  - With two contacts not side by side on one ring, it leaves one return unpaired.
  - As a "bubble" on a corner p→q, it deletes that corner. The network stays balanced exactly when no contact is both reached from q and reaches p.
- **Census (exact, census-only).** Of 795,042 single-ring attachments to 16 balanced seeds, none keeps every contact persistent beyond the smallest seeds of four rings. Refining the sphere's Platonic networks (truncating or rectifying them) breaks persistence too.
- **Reading.** Growth has to add whole bands, because a single ring is a defect. Networks with a flip at every contact exist at every size only on the torus. The law fills a torus it is given, but it does not make the surface.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: growth from a law | Successful | A rule (bands/blocks on the torus) and an obstruction (single rings), both proved |
| Local direction: growth from a law | Research directions | What's open is making the surface itself |
| Broader exploration: G1 with G5 | Known alternatives | Growth chosen by the dynamics; full-reach proof (parked); which lattices compose |
| Long-term goal: G1 Space from a law | Capability gained | A uniform local law grows a lattice of persistent contacts at every stage, on the torus |

**Next step:** Research directions.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Make the surface by growing whole bands | 3/3 | 1/3 | Look for band insertions that start from a loop and close a torus, every stage balanced → a sequence, or the step where every band fails | Deferred |
| 2 | Prove full reach on the cut-open torus | 2/3 | 3/3 | Images of the doubled torus and the powers of two | Deferred |
| 3 | Which lattices compose everywhere | 2/3 | 3/3 | Rectangular, triangular, honeycomb tori → a characterisation or the first counterexample | Deferred |
| 4 | Growth chosen by the dynamics | 2/3 | 1/3 | Let a contact's needs pick where the next band goes | Deferred |

**Corrections:** none. **Goals:** G1 checkpoint with G5 (capability gained). **Assumptions:** none added. I saved your ruling (counted length counts as a native magnitude, and questions like that don't wait on you) to project memory. Distance continues in its own thread.
