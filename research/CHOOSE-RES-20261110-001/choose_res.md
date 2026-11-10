# Choosing the resolution

Epic `CHOOSE-RES-20261110-001` (backlog B62, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md); frozen contract and run in
`experiments/CHOOSE-RES-20261110-001A/CHOOSE-RES-20261110-001A-E001_a_learner_given_a_target_class/`; results and their interpretation in
`artifacts/CHOOSE-RES-20261110-001A/.../run/`; stress test one size past in [stress_test.py](stress_test.py).

## The question

A class-forced pair can be resolved into any of three other classes: three different resolutions, the "action or resolution" of the
owner's picture. Given a target class, can a learner that sees only the lines at a hole reach it, what does choosing cost, and which
resolution does a learner reach without a target?

## The answer

- **Choosing has a price, set by the handle (proved bound).** Every resolution into a class changes at least as many signs as the
  smallest cycle in its class change (`LEARN-HANDLES-20261109-001` theorem 3.2). On a thin torus of N points the short class costs at least
  2 and the two long ones about N / 2: choosing a far resolution means going once around the long way.
- **A learner told the target reaches it (computed).** C7 keeps the class its own sign changes have made and steers its second hole toward
  the copy of the over-agreeing face that gives the target. It reached the target in 3,173 of 3,186 runs, every one on the thin tori, at a
  cost within 0.4 sign changes of the cheapest walk there (at 40 points: 8.3 for the short class, about 21 for the long ones). The 13
  misses, on a Fano torus and on grown tori, entered the target face in the wrong sheet; refusing that move (post hoc) reached all 180
  grown-torus targets. One size past, to 46 points, every target was reached.
- **Without a target, how the learner moves decides (computed, against the pre-registration).** Random moves ended in the short class in
  only 13% of runs on thin tori of at least 20 points, and in each long class in about 44%; sight of radius 3 in 63%; the outside-distance
  rule in 96 to 99%. The pre-registered expectation that every untargeted learner defaults to the short class was wrong.

For the owner's picture: once a handle exists there is more than one way to resolve, and a learner can pick one if it carries the
choice; the further resolution costs the length of the handle. A learner that does not carry a choice still ends up somewhere specific,
and where depends on how it moves: a wandering learner mostly takes the long way.

## Evidence

All computed (exploratory) except the cost bound, which is `LEARN-HANDLES-20261109-001`'s theorem. The target class is supplied from
outside, as A26 allows a target. C7' is post hoc.

## Corrections

None.

## Does tonight's work make B54 (layers) more concrete?

Yes, under one reading. In `GROW-HANDLE-20261110-001` a Fano atom spliced in for a line acts, from outside, exactly as that line (in its
class) and becomes transparent when learning winds through it. That is a two-level network: the sphere's lines are the upper level, and an
atom is a pattern, one level down, that stands for one of them. The sphere's forced dissonance, an upper-level fact, was removed by
learning inside the lower level. So "learning at one level resolves a dissonance forced at another" now has a working example. The first
real B54 step becomes concrete: replace several or all lines of a knot sphere by atoms (the builder exists) and ask how the dissonance
moves between atoms and between the levels. Under that reading B54 rises to Concreteness 2/3. Under its original reading, names as parity
knots (`GEOMETRY-LAW-20261029-001`), nothing changed, and it stays at 1/3.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — choosing the resolution (B62) | **Status:** Partially successful | a targeted learner chooses; the default expectation failed |
| Local direction — steering by re-signing | Continue | resolutions can be chosen at a known price |
| Broader exploration — learning program | Known alternatives | growth trigger, layers through atoms |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | the point can be guided to a chosen resolution |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Grow where learning is stuck (B68) | 2/3 — Substantial | 2/3 — Testable | grow an atom only where sight finds no resolution → once at the dissonance, or not | Selected · started |
| 2 | Layers through atoms (sub-goal B54) | 3/3 — Barrier | 2/3 — Testable | replace several lines of K_2 by atoms → the dissonance moves between levels, or stays put | Alternative · deferred |
| 3 | Why random learning goes the long way (B69) | 1/3 — Incremental | 3/3 — Ready | the second hole's moves after the first is absorbed → a reason, or a count | Alternative · deferred |

- **#1** is next by the coordinator's order.
- **#2** is the B54 view above; it stays a sub-goal with the new reading and rating recorded.
- **#3** is a mechanism question about the 13% (a guess, unchecked: after the first hole passes, the lines on its path agree backwards,
  so the second hole is pushed the other way).

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B62 taken; sub-goal B54 re-rated (Concreteness 2/3 under the atom
reading); B69 added. **Assumptions:** a history line for A26 (a target class supplied from outside).

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (00:53 UTC).

**B62 done: a learner can choose its resolution, and choosing has a price.** Told which class to end in, a learner that tracks the class its own changes have made reached it in 3,173 of 3,186 runs. On thin tori it was within half a step of the cheapest walk. The price is the handle: the far resolution costs about half the torus, the near one 2 steps. My pre-registered guess was wrong: without a target, random learners mostly go the long way (only 13% short).

**On B54 (layers):** yes, more concrete now. The grown Fano atom acts from outside exactly as the line it replaced, and learning inside it removed the sphere's dissonance. That's a two-level network where learning one level down resolved a contradiction forced one level up. Next step: replace several lines by atoms and watch the dissonance move between levels (2/3 now, kept as a sub-goal).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: choosing (B62) | **Status:** Partially successful | targeted choice works; default guess failed |
| Local direction: steering by re-signing | Continue | resolutions chosen at a known price |
| Broader exploration: learning program | Known alternatives | growth trigger, layers via atoms |
| Long-term goal: G15 | Capability gained | the point can be guided to a chosen resolution |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Grow where learning is stuck (B68) | 2/3 — Substantial | 2/3 — Testable | grow only where sight finds nothing → once at the dissonance, or not | Selected · started |
| 2 | Layers through atoms (B54) | 3/3 — Barrier | 2/3 — Testable | several lines of K_2 replaced by atoms → dissonance crosses levels, or not | Alternative · deferred |
| 3 | Why random learning goes long (B69) | 1/3 — Incremental | 3/3 — Ready | trace both holes' paths → a reason | Alternative · deferred |

**Corrections:** none. **Goals:** G15 checkpoint; B62 taken; B54 re-rated; B69 added. **Assumptions:** A26 history line.
