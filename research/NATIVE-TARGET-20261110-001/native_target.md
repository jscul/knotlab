# A native target for learning

Epic `NATIVE-TARGET-20261110-001` (backlog B61, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md); frozen contract and run in
`experiments/NATIVE-TARGET-20261110-001A/NATIVE-TARGET-20261110-001A-E001_native_signals_that_steer_learning/`; results and their
interpretation in `artifacts/NATIVE-TARGET-20261110-001A/.../run/`.

## The question

`LEARN-HANDLES-20261109-001` proved that on a class-forced torus learning removes the least dissonance, a violated line and an
over-agreeing face, only by winding around a handle, and a local rule did it from every start. But that rule was told the graph distance
to the over-agreeing face by the experimenter (A26). Can a signal that the law and the state supply themselves do the same?

## The answer

Yes, computed on the two Fano tori and the 57 thin tori of even index up to 40 points (exploratory, pre-registered):

| Rule | What it sees | At 40 points (torus(40, 1, 1)), mean steps |
| --- | --- | --- |
| R0 random | nothing | 64.4 |
| R1, R2, R3 sight | its own moves, 1 to 3 ahead (native, local) | 21.4, 15.5, 12.9 |
| R4 most states | how many states share x's dissonance after each move (native, global) | 19.3 |
| R5 | R4, taking an absorbing move when it sees one | 17.9 |
| R6 fewest states (control) | as R4, reversed | 46.6 |
| R7 outside distance (reference) | the experimenter's distance to the over-agreeing face | 7.5 |

- Every native rule but the control resolved every run, and every resolved run of every rule replayed as learning steps that wind.
- The count of states that share the state's dissonance is a native pull: it is 2 (x and its complement) when the holes are far from
  the over-agreeing face and grows as they approach (mean log N from 1.0 to 6.0 at 40 points), so a learner that keeps the most such
  states is drawn to it. Opposite charges attract, as same charges repelled on the sphere. The pull is uneven at contact: on six tori
  the count at distance 1 is below that at distance 2, so the pre-registered diagnostic fails read strictly.
- The control, which keeps the fewest states, never resolves on the Fano tori and on the thin tori is no better than random: slower on
  10 of 16, faster on 6.
- One size past (42 to 46 points) R4 and R5 again resolved every run and beat random.

For the owner's picture: the "strength based on stability" has a native form. A point is drawn to its resolution by keeping the
world's options open, the number of ways the world can be while carrying the same tension, and no outside map is needed. A learner that
can look three of its own steps ahead does better still. Neither is as fast as an outside map, so the outside distance carried real
information, about a factor of two at 40 points.

## Evidence and provenance

All claims are computed (exploratory) on finite tori; none is proved. The rules and the definition of native were frozen before any
native rule ran (A47). Known with delta: entropic attraction between opposite defects (Fisher and Stephenson's monomer correlations,
Ciucu's electrostatics of holes) and maximum-entropy steering; new are its use as the learning signal on the class-forced tori and the
comparison with sight and with the outside distance.

## Corrections

None.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a native target for learning (B61) | **Status:** Successful | sight and the count of shared-dissonance states both steer |
| Local direction — steering by re-signing | Continue | learning now needs no outside input on these tori |
| Broader exploration — learning program | Known alternatives | growing a handle, chosen resolution, layers |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | the point is drawn natively, by stability |

Unresolved: why the count's pull is uneven at contact, and whether it holds off the thin tori, which are chains; the class-forced tori
tested are all thin or Fano.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Learning that grows a handle (sub-goal B60) | 3/3 — Barrier | 2/3 — Testable | splice a Fano atom at a knot sphere's violated line, then learn → resolved by winding through it, or still forced | Selected · awaiting go-ahead |
| 2 | Choosing the resolution (B62) | 2/3 — Substantial | 2/3 — Testable | a native rule given a target class on thin tori → all reached, or the long class needs more | Alternative · deferred |
| 3 | Why the pull is uneven at contact | 1/3 — Incremental | 3/3 — Ready | transfer-matrix counts by hole positions → a closed form, or the dip explained | Alternative · deferred |
| 4 | A point moving between layers (sub-goal B54) | 3/3 — Barrier | 1/3 — Stated | smallest two-level network with one dissonance → it crosses levels, or not | Alternative · deferred |

- **#1** is now concrete. A sphere's forced dissonance can never be resolved (`LEARN-HANDLES-20261109-001`, theorem 1), and the record
  has a native move that adds exactly one handle: splicing a Fano atom (the Fano plane less a point, the knot's own uniform contradiction)
  across a 3-edge cut adds one handle to the incidence graph's genus (`THREEFOLD-SURFACES-20261030-001`, splice lemma). The move is local
  and can be made where the dissonance shows, at the violated line. First step: on K_2 to K_4, replace the violated line by a Fano atom,
  build the knot space of the spliced graph's minimal map (a torus), and ask whether its law still forces a dissonance, and if so whether
  learning resolves it by winding through the new handle. What is missing is code: a builder from a rotation system to a knot space,
  hence 2/3. If it works, dissonance that learning cannot remove makes space.
- **#2** reads "guide the points to some action": the three classes are three resolutions.
- **#3** is a closed-form question on chains; cheap, local payoff.
- **#4** is unchanged.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B61 taken; sub-goal B60 re-rated to Concreteness 2/3 with its
first step; B54 carried. **Assumptions:** A47 added (what a native signal is); history lines for A26 (the outside target is not needed on
these tori) and A27 (the count, weighed by the state's dissonance, steers).
