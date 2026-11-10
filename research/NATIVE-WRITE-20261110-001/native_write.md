# Native writing

Epic `NATIVE-WRITE-20261110-001` (backlog B119, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md), frozen with the code in commit `22c1a427f` before any run on the test spaces. Proof families:
`proofs/NATIVE-WRITE-20261110-001A/` (four fresh spaces) and `proofs/NATIVE-WRITE-20261110-001B/` (one size past).

## The answer

**Yes: the layered memory can be written natively.** A learner that sees only its own dissonance and the address it is asked for (a bit
per atom, each atom given by its region) wrote every frozen target exactly, and every address held after a disturbance: 80 of 80 on
four fresh spaces and 20 of 20 on a six-atom space one size past, with no inexact stop. Every earlier address had been written by a
search that was told the target configuration.

The learner knows an atom holds a 1 the way the memory itself does: **an atom acts exactly when the dissonance in it cannot be walked
away.** It tests its memory by letting its state wander on the floor without learning (the probe), and it changes signs only on atoms
whose answer is wrong (attention).

- **P1 (proved by hand, from lemma 3 of `OTHER-ATOMS-20261110-001A`).** An acting atom has dissonance in its region in every state. So the
  probe never fails an acting atom asked 1, and an atom asked 0 that the probe ever finds clear is transparent.
- **P2 (proved by hand).** A write changes only atoms the probe found wrong; atoms already right are never touched.
- **Region lemma (exact, every class of seven spaces).** An atom acts exactly when its own constraints cannot clear its region: 7,264 acting
  and 21,792 transparent atom-classes, no exception.
- **The frozen test (computed).** 100 of 100 writes exact and held. Medians of 4,200 to 15,100 steps and 18 to 67 probes per write, on spaces of 45 to 99 points.
- **The control (computed).** With the probe replaced by the same test read at one instant, 84 of 100 writes stopped inexactly: units
  sitting in atoms that did not act, the old search's failure.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| P1: an acting atom's region always holds dissonance; the probe's only possible error is a false 1 | proved by hand |
| P2: a write changes only atoms found wrong | proved by hand |
| Region lemma: acting exactly when the atom's own constraints cannot clear its region (seven spaces) | exhaustive computation |
| Native writing: 100 of 100 exact and held, no inexact stop | computed, frozen |
| Without the probe: 84 of 100 inexact | computed, frozen |

## Against the pre-registration

Every mark held: native writing on S1 to S4 (20 of 20 on each; the mark was 18), R (no inexact stop), U (65 of 80 inexact; the mark was
20), the census, and the stress test S5 (20 of 20). B119 is answered yes for this learner. Not blind: the learner was developed on two dev
spaces before the freeze, and the test spaces were not run until then.

## What it changes

- **Writing no longer needs an outside map.** The learning line's addresses were all written by a search told the target; now a learner
  that sees its own dissonance and the request writes them, on four- to six-atom memories at two levels.
- **Reading a role is native.** Whether an atom acts was read by a solver on its outer points. It is also read by the point itself: the
  dissonance in an acting atom cannot leave it (P1), and in a transparent one the walk carried it out before every stop (computed: no
  false 1 in 100 writes).
  This is the owner's picture made exact: a stored 1 is a tension the state cannot walk away.
- **The inexact writes are explained.** The old search stopped on units, and a unit can sit in an atom that does not act. The control
  shows the same failure in 84 of 100 writes; the probe removes it entirely.
- **What remains outside.** The address is given as each atom's region (A57); the floor is a count of the learner's own points, lines and
  faces. The probe's reliability is computed, not proved: P1 rules out every error but a free unit that stays put for 20,000 steps
  (backlog B130).

## Assumptions

Added: A57 (an address asks for a bit per atom, each atom given by its region). Relied on: A20, A21, A46, A47, A49, A52. A50: the probe
is its walk; while writing, the learner uses its alternative, state flips at a temperature (history line added).

## Corrections

None.

## In the owner's words

Asked for a word, the learner keeps working only on the cells whose answer is wrong, and it knows a cell holds a 1 when the tension
there cannot be walked away. No one tells it the configuration to aim for.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: native writing (B119) | **Status:** Successful | 100 of 100 exact and held with no outside map; the probe is why |
| Local direction: writing the layered memory | Continue | a native writer exists; its probe's reliability is the one computed link |
| Broader exploration: learning program | Known alternatives | inputs and outputs, the probe as a theorem, writing with only the ones named |
| Long-term goal: G15 Learning: a point in a learned knot space | Capability gained | the point now writes and reads the memory itself |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Inputs and outputs (B120) | 2/3 — Substantial | 2/3 — Testable | input points held by the world at each value, the native writer storing the examples, a composite read as the output → an input-output map learned from examples and held, or the input never reaches the handle | Selected · awaiting go-ahead |
| 2 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | on the smallest space, whether the floor plateau reaches a clear region of every transparent atom from every floor state → a proof that a long enough probe never errs, or a trapped free unit | Alternative · deferred |
| 3 | Writing with only the ones named (B131) | 1/3 — Incremental | 2/3 — Testable | the same learner told only the atoms asked 1, testing whether outside dissonance ever moves → exact writes, or unnamed atoms left acting | Alternative · deferred |
| 4 | A frame fixed by learning (B126) | 1/3 — Incremental | 1/3 — Exploratory | as recorded; the native writer winds at random, so a fixed frame needs a different rule | Alternative · deferred |

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B119 taken; B130 and B131 added; B120's concreteness raised to
2/3. **Assumptions:** A57 added; A50 history line (writing uses its alternative).
**Basket:** B120 (inputs and outputs), B130 (a probe that is a theorem); taken: B120 as the selected next step.
