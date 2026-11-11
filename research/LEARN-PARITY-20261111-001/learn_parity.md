# A learned memory that computes parity

Epic `LEARN-PARITY-20261111-001` (sub-goal B146, G15 with G16; program learning), 2026-11-11, at the coordinator's go-ahead. Pre-registered
in [preregistration.md](preregistration.md), frozen with the code in commit `00aafe7f6` before any learning run. Proof family:
`proofs/LEARN-PARITY-20261111-001A/`.

## The answer

**Yes. A learner that sees only its own dissonance learned the parity of three held points from examples, inside a memory, and held it.**
In 10 of 10 runs on the bare 8-point torus (2, 0, 4) and 10 of 10 runs on a memory (the knot sphere K_2 with that torus grown as an atom),
the unchanged learner, credit from pinned dissonance with the sturdier probe and no outside map, turned the map into parity, kept it
through a disturbance, switched it to its negation and back: 60 of 60 writes, no inexact stop, a median of 13,400 and 18,000 steps.

- **Realizable (exact).** Each interface computes parity in exactly one of its four classes, the torus's most constrained.
- **Learned (computed, frozen).** Every run reached that class with the right frame and held it.
- **What is and is not crossed.** Theorem D is not crossed: parity is self-dual. Theorem M is not crossed: it bounds readings of stored
  classes, and parity here is a map of held values; as a function of the stored class it is a gate, present in one class. What is crossed
  is the observation that every learned map, and every map at the earlier memories' interfaces, was unate: this is the first learned map
  that is not.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Parity of three held points is realizable on the torus (2, 0, 4) and in the memory, in one class each | exhaustive computation |
| The unchanged learner learns and holds it from examples: 20 of 20 runs, 60 of 60 writes | computed, frozen |
| Theorems D and M are consistent with it | by hand (from their statements) |

## Against the pre-registration

All marks held (R, P1, P2), no inexact stop, as predicted. The learner was not changed.

## What it changes

- **The learned memory computes beyond monotone and unate maps.** Earlier memories held their atoms as switches read on their sides; a torus
  held from inside, in its tightest class, counts. Combined with the gates of `IN-OUT-20261110-001` and majority, which small knot spaces
  compute often, the learned memory has non-monotone, non-unate building blocks.
- **The open question moves to composition.** Majority with negated inputs generates every self-dual function (Post's lattice); whether a
  memory can wire learned gates into larger functions, the output of one held as the input of the next, is next (sub-goal B148).

## Assumptions

None added or changed. Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

None.

## In the owner's words

A learner that feels only its own tension, shown eight examples, wound a ring of eight points into the one pattern that counts, and the
ring kept counting after it was shaken. It did this every time, alone and inside a larger memory.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a learned memory that computes parity (B146) | **Status:** Successful | 20 of 20 runs learned and held parity; 60 of 60 writes |
| Local direction: learning non-unate maps | Continue | parity learned; larger functions need composition |
| Broader exploration: learning program | Known alternatives | composing learned gates, parity of more held points, the probe as a theorem |
| Long-term goal: G15 Learning: a point in a learned knot space | Capability gained | the first learned non-unate map, inside a memory |

**Next step:** Research directions — selected: #2 (holding, per the coordinator, until a go-ahead)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Composing learned parity into larger functions (sub-goal B148) | 3/3 — Major | 1/3 — Exploratory | two parity tori in one memory, the output of one held as an input of the other, learning five-input parity from examples → a learned composite map, or what stops the wiring | Alternative · recorded as a sub-goal |
| 2 | Parity of more held points (B149) | 2/3 — Substantial | 2/3 — Testable | the exact search on lattice tori up to 24 points for parity of five held points (an even number is impossible by theorem D), then learning the smallest → a torus that counts more, or a bound on how many points one torus counts | Selected · awaiting go-ahead |
| 3 | A probe that is a theorem (B130) | 2/3 — Substantial | 1/3 — Exploratory | as recorded | Alternative · deferred |
| 4 | How learning cost grows with atoms (B143) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

Direction 2 comes first as the cheaper discriminator: whether one torus counts more points says how much wiring direction 1 needs.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained, with G16); sub-goal B146 taken; sub-goal B148 and B149 added.
**Assumptions:** none new or changed.
**Basket:** B149 (parity of more held points), B130 (a probe that is a theorem); taken: B149 as the selected next step; B148 recorded as a
sub-goal.
