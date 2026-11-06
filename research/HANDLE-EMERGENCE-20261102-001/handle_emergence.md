# Emergence needs a handle

Epic `HANDLE-EMERGENCE-20261102-001` (program topology), 2026-11-02.

## The question

- **The approval.** The owner said "Let's keep going!" to SPLICE-TREE-20261102-001's recommendation.
- **The question it approved.** When a removal opens a cut, does new emergence need both a hub that has become a knot (six port
  patterns) and a non-planar removed side, so that planar glue only composes?
- **The plan.** First test planar spaces beyond the census, where one new knot refutes the conjecture. Then find how handles create,
  and try to prove the planar case.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Planar removed sides create nothing beyond the census.** The test: 24 planar knot spaces of 10–14 points (ladder growth from the cube, prisms, the truncated octahedron; Kasteleyn signs, failure checked), spliced into four census spaces. Result: 1612 removals, 432,867 crossing knots, none new. Census: planar sides 0 of 560; Fano and census 58 create 936 knots at 100 of 208 removals. No four-pattern interface creates (1400). | computation | A |
| 2 | **A new knot is a three-point constraint through the hub.** Every new knot (936) has one point of the removed line's hub, one near point off the ports and one far point. The hub and the near point pin all three ports to one pattern, and the far point separates it: a joint use of the ports that no single port carries, so no elimination produces it. | computation; two elementary lemmas | B |
| 3 | **Necessary, not sufficient.** New knots need a pinned pair that a far point separates: 100 of the 200 such removals create, and none without such a pair. In the Fano plane every removed line meets the closing line, the hub sits on that port, and the pinned pair's odd port is the hub's own. | computation | B |
| 4 | **The odd-point model.** Choosing each line's odd point is a bijection between solutions up to complement and choices of one incidence per line with prescribed parities on every cycle. | proof; 56 census removals | C |
| 5 | **The skip model on plane spaces.** With Kasteleyn's face condition, a line skips the corner opposite its odd point, and every face must hold an odd number of skipped corners. With n + 2 faces for n lines the knot fails by counting. After a removal the solutions are exactly the perfect matchings of the other lines to the faces off the removed line. All failing signings of the planar census spaces satisfy the face condition. | proof; 17 plane spaces, 488 signings | C |
| 6 | **Planar interfaces.** A line meeting the removed line shares a face with it, so it has at most four port patterns. The Fano plane's mechanism (the hub on the closing line, pinned as odd) therefore never appears on a plane side. | proof; 1494 pairs | C |
| 7 | **A handle leaves slack.** On genus g there are n + 2 − 2g faces and 2g homology parities, so counting no longer forces failure. On the Fano plane's 16 torus embeddings the face condition holds. After a removal, 14 face-odd assignments remain (each with one face skipped three times), of which the homology parities keep 5. | proof of the count; computation | C |

## Answer

- **Yes, as far as tested.** No planar removed side creates, beyond the census as within it. Creation needs six port patterns and a
  non-planar side, and four-pattern interfaces never create.
- **How a handle creates.** It creates a three-point knot through the removed line's hub: the hub and one near point fix the whole
  port pattern, and one far point answers to it.
- **Why a plane space doesn't.** Removing a line turns a plane space's solutions into perfect matchings of lines to faces. A line
  meeting the removed line loses a face, so the configuration that creates in the Fano plane cannot arise.
- **What is not proved.** The full planar statement, that a plane side never creates, is reduced but not proved.

## Reading

- **Topology from logic, concretely.** On a plane space the knot fails by counting faces against lines (Euler's formula). Each handle
  removes two faces and adds two global parities, the homology of the space.
- **Where creation lives.** It happens exactly where those parities, rather than counting, decide (14 face-odd assignments against 5
  solutions in the Fano plane).
- **What this ties together.**
  - THREEFOLD-SURFACES: each Fano atom is a handle.
  - THREEFOLD-SPIN: the knot's signs are Kasteleyn on minimal maps.
  - The program's long-standing reading of holes as what a loop remembers.
- **Doctrine.** Hubs remain equality fan-out. What is created is emergence (knots), not contact, native paths or distance.

## Literature

- **Ours.**
  - HUB-GLUE A–C and SPLICE-TREE A–C.
  - THREEFOLD-SPACES (failure is sign-nonsingularity), THREEFOLD-GRAMMAR, THREEFOLD-SURFACES, THREEFOLD-SPIN.
  - The census of MUTUAL-SELECTION C.
- **Classical.**
  - Kasteleyn's face condition for plane Pfaffian orientations.
  - Moret's theorem that planar not-all-equal 3-SAT is polynomial, via planar maximum cut ([Moret 1988, SIGACT News 19(2):51–54](https://en.wikipedia.org/wiki/Not-all-equal_3-satisfiability)).
  - Euler's formula.
- **New here, as stated.**
  - The skip model (failure by counting, solutions as line–face perfect matchings, interfaces read off matched faces).
  - The genus count.
  - The pin-and-separate description of new knots.
  - The planar test.

  A bounded search found no statement of the skip model, so folklore risk is moderate.

## Pending the owner

Still open from earlier epics:
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- whether counted length should ever count as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — does new emergence need a handle? | **Status:** Partially successful | **Survived the refutation test** decisively: 2172 planar removals, none creating. **Mechanism described.** A three-point knot through the hub, pinned and separated. **Structure proved.** The skip model, planar interfaces, and handle slack. **Unresolved.** A proof that plane sides never create, and when handles do. |
| Local direction — planar non-creation | Continue | **The reduction.** The skip model turns it into a statement about perfect matchings of lines to faces, with the closing line's matched face carrying the interface. **What is left.** One combinatorial step: showing that a pinning always passes through a single port class. |
| Broader exploration — where the knot's emergence is created | Known, with a lead | **Planar glue composes; handles create.** On a handle the face slack and the homology parities decide which skip assignments are solutions. |
| Long-term goal — composed structure and topology from native emergence | Capability gained | **What is gained.** A direct, proved link between the knot's solutions and the topology of its space: counting faces on genus 0, and homology parities on handles. Selection on a plane space is a perfect matching of lines to faces. **The limit.** Hubs are equality fan-out; no native path or distance is claimed. |
| Next recommendation — planar glue only composes | **Next step:** Continue. **First,** prove that a plane removed side never creates, from the skip model. **First discriminator.** Prove or refute, in plane line–face matchings, that a near relative value forcing the closing line's matched face always passes through a single port class. Check the lemma on ticket A's spaces before attempting the proof. **Then,** on handles, test whether new knots are exactly what the homology parities add: on the Fano plane's splices, cut along a non-contractible cycle and see whether creation disappears. | **If yes.** A theorem: emergence after selection is created only in handles, by homology. **If no.** The planar evidence stays finite, and the handle story needs another invariant. **Alternatives.** Count kept states on genus g by twisted Pfaffians (1/3; close to THREEFOLD-SPIN). Classify which far sides answer a handle's pinning (1/3). |
| Interest — that recommendation | **2/3 — Promising** | **Evidence.** Overwhelming finite evidence (no new knot in 2172 planar removals). The skip model already proves the plane-side mechanism cannot form, and the step left is a concrete matching statement. **Main uncertainty.** That step may need new plane-matching combinatorics, and the homology reading of creation is so far one computed example. |
| Execution — that action | Deferred to the owner | **Not started.** No new epic opened. **Bound.** The plane spaces of ticket A and the Fano plane's splices. **Stop when** planar non-creation is proved or a counterexample to the single-port lemma appears; then reassess the homology reading. |
