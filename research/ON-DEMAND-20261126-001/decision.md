# A local reader's view grown on demand: what stands

Epic `ON-DEMAND-20261126-001` (the coordinator's go-ahead on the owner's intuition; goals G17 with G1), closed 26
November 2026. A check by the thread, not registered: computed; frozen with the advisor's review and hand test before
the runs; referee pending; the engine's five-knot check is a stress test pending. [The note](README.md)

## What stands

1. **A reader's view through round t needs only the start within t + 1 steps of the map.** Under not-all-equal, in all
   2,256 (reader, round) cases of 60 random trees of 40 knots, 58 starts of 25 knots with cycles and 148 six-knot census
   starts that do not stall, the growth run on the live knots within t + 1 steps of a start knot gives that knot's view
   through round t exactly, in both readings. Within t steps suffices except where the edge passes through a round-1
   group of three or more (27 cases, none in the trees).
2. **Any admission order gives the same view.** Every region holding those knots, and every step of admitting more,
   gave the same view (1,544 checks).
3. **Two rules read the whole start.** A knot short in round 1 stops the whole growth, and in 2 of 252 stalling starts it
   lies where no region grown from the reader reaches; under parity a birth that takes every loose distinction closes
   the growth, and every one of the 53 cases where a region's view differed was such a closure.
4. **A reader rests on a fraction of the growth**: a median of 28% of the births in the trees and 34% with cycles.

**Not shown.** Anything settled by being read: the far part is unread, not undetermined. Admission composed with births
made one at a time; readers that are made knots; starts beyond 40 knots.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a reader's view on demand, frozen and tested on fresh starts | **Status:** Successful; the stop met with none broken | 2,256 of 2,256 cases within t + 1 steps |
| Local direction — what a reader needs of the growth | Continue | The reach is t + 1 steps; parity's implied birth and the round-1 shortage are the only whole-start reads |
| Broader exploration — the owner's simulation picture (Chapter 11) | Capability gained | Computing only what a reader needs works, with one check of the whole start |
| Long-term goal — G17 Typical and rare meeting patterns, with G1 | Capability gained | A reader's dependence on the start is bounded and measured |

**Next step:** Research directions — selected: #1 (the coordinator's queued go-ahead)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Whole-ring facts as the distinctions of a second layer: do several rings' whole-loop facts obey a knot rule among themselves, and does that keep a fact no single ring holds? | 3/3 — the owner's emergence at more than one layer | 2/3 — the two-class sign under parity is the first layer | Read the nested-pattern and bases-within-bases records, then a frozen test on rings that share knots → a second layer, or an argument that the layers do not stack | Selected · not started |
| 2 | Admission composed with births one at a time | 2/3 — the owner's picture of filling in during the growth, without rounds | 2/3 — both halves exist (`LOCAL-ROUND-20261123-001`) | Admit knots at random births of the asynchronous law → the view, or a mismatch | Alternative · deferred |
| 3 | A proof that t + 1 steps suffice | 2/3 — turns the cone into a theorem | 2/3 — the identification and the hand test name the one case | Prove it on the identification's class, with groups read whole → a proof, or a counterexample | Alternative · deferred |

**Corrections:** none.
**Goals:** checkpoint row added (G17, G1; capability gained).
**Assumptions:** A288 added (scaffold: the reader, the region rule, the round, the cap, the populations).
**Basket:** the postulates line's top items belong to the hearing and meeting lines; `COPYING-PARTS-20261123-001#1` (a
round read locally) is #2's closest kin.
**Scaffolds:** A288. Swapped: the knot law, the reading, the weighting (trees, trees with lines, the census), the seed,
the region (balls, random supersets, admission in steps). Not swapped: the reader as a start knot, the round, the cap
(rounds past it not read). The result survives every swap made, so it is about the model's locality under
not-all-equal; the parity differences belong to the parity law.
**Advisor:** consulted before the freeze; its hand test broke "t steps" and set the frozen claim at t + 1; taken: the
holders are read one start step beyond the knots, the cap and the round are scaffolds, admission during the growth, "the
far part is unread, not undetermined"; not taken: composing admission with births one at a time.
