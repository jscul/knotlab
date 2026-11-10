# Rigid worlds at radius 2

Epic `RIGID-WORLDS-20261110-001` (program topology, group `spacing`, `BOARD-DIST-20261110-001` direction 2, G1), 2026-11-10.
Pre-registered in commit 87caa46a3, with ticket A's census frozen there. The last epic before the night's rest, at the owner's
instruction to finish current epics and start no new one.

## The question

- **Where it comes from.** A law that names no relation never forces an infinite board (`BOARD-DIST-20261110-001`). Even the
  infinitary identity rule never forces the plane for one-bit Life-like laws (`LEIBNIZ-BOARDS-20261110-001`). Finite boards can be
  forced, though. The coordinator's go-ahead of 2026-11-10 asked for the constructive side of the owner's idea: a rule that makes a
  two-dimensional world.
- **The question.** With identity at radius 2 (names whose radius-2 views agree are one place), does any one-bit Life-like law, or
  the atom, force every board to be a genuinely two-dimensional torus?

## What counts

- **A two-dimensional torus.** An abelian board Z²/Λ with no lattice vector of L1 norm at most 4, so that every radius-2 ball is the
  plane's (13 distinct places). Thick cylinders, cycles and non-abelian boards do not count.
- **The bound.** A forced torus has at most 256 places, by the radius-2 swap of `BOARD-DIST-20261110-001A`. So any family of forced
  sizes is bounded at this radius.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **No law of the family forces a two-dimensional world (R1).** Every one of the 994 laws with any allowed board allows a board that is not a two-dimensional torus. | computed, exact, frozen | A |
| 2 | **What refutes them.** 769 (768 Life-like laws and the atom) allow the one-place board, since a constant colouring obeys them. 223 allow a thick abelian board with at most 8 places: 112 with 2 places, 64 with 3, 29 with 4, 14 with 5, 4 with 8. The two counting laws L40 and L80, whose only finite boards have 7 places, allow a plane-like non-abelian board with 7 places. | computed, exact | A |
| 3 | **31 laws allow no board.** They have no solution at all. | computed, exact | A |
| 4 | **The controls behave (R2).** A radius-2 law drawn from one 13-place torus forces exactly that torus, one size; the full law is refuted by the one-place board. | computed, exact | A |
| 5 | **The exact step was never needed.** Every law with a board was refuted by a board of the frozen list; none was undecided. | computed | A |

## Answer

Identity at radius 2 does not make any one-bit Life-like law, or the atom, choose a two-dimensional world. Every law that allows any
board also allows a tiny or thin one, mostly the one-place board or a cycle of two or three places. Forcing a two-dimensional torus is
possible: a law drawn from the torus itself, listing exactly its views, forces it, at one size. But that law draws the board in
advance, and no law of the family does it. Since a forced torus at this radius has at most 256 places, no family of sizes could grow
without bound here in any case.

## Reading

**Interpretation, not a theorem.**
- **Why the small boards win.** Identity at radius 2 asks that different places look different within two steps. Life-like laws
  count neighbours without telling directions apart. Wherever they allow a world at all, they allow one so small that it has few
  places to tell apart.
- **Drawn versus chosen.** The control shows the method can see forcing. What forces a world is a law that already contains the
  world's views, which is the finite form of drawing the board.
- **The finite shadow of the plane is bounded.** At any fixed radius the swap caps the size of a forced torus, so a growing family
  would need the radius, or the alphabet, to grow with it.
- **Nothing here is a length.**

## Lag cutoffs and census-only claims

- **Exact.** Each refutation is an explicit board with a colouring found by an exact solver; the 31 empty laws have no allowed view.
- **Census-only.** All conclusions; the family is the frozen one.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Conclusion 1 (every law with a board refuted) | — (each refutation is a certificate; a larger board list cannot change it) | not run |

## Literature and provenance

- **Sources.** De Bruijn tori and perfect maps (the drawn control is a torus colouring with distinct views); the swap bound and view
  boards of `BOARD-DIST-20261110-001A`.
- **Classification.** A census within the program's own setting; no claim of novelty.

## Workspace assumptions

- **Relied on.** A53, A54, as in `BOARD-DIST-20261110-001`.
- **Added.** None.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (the census and its controls).
- **Administrative.** This note, the pre-registration and the closure.

## Corrections

None to published claims.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — rigid worlds at radius 2 | **Status:** Successful | Decided for every law of the family: none forces a two-dimensional world, and the drawn control shows forcing is visible when it happens |
| Local direction — boards made of distinctions | Obstruction learned | Static laws, finitary or infinitary, at radius 1 or with identity at radius 2, do not choose the plane in the families studied |
| Broader exploration — question 9 | Known alternatives | Growth, larger alphabets, weakly aperiodic laws |
| Long-term goal — G1 Space from a law | Obstruction learned | A two-dimensional world is chosen only when its shape is named or drawn |

**Corrections:** none. **Goals:** a G1 checkpoint (obstruction learned); BOARD-DIST-20261110-001#2 taken. **Assumptions:** none added.
**Basket:** spacing's HARD-FLAT-20261107-001#3 (every accretion law, 2/3, 2/3), BOARD-DIST-20261110-001#3 (abstract names, 2/3, 2/3)
and LEIBNIZ-BOARDS-20261110-001#2 (weakly aperiodic laws, 2/3, 2/3); taken: none, since the project rests tonight; the proposal
below is for the morning.

- **What the attempt leaves open.** Laws with more values or a larger reading radius, where the 256-place cap rises; and boards that
  grow by a process rather than in one static CNF.

**Next step:** Research directions — proposed for the morning: #1, unless the coordinator chooses otherwise. Not started, by the
owner's instruction.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Weakly aperiodic laws under Leibniz's rule (LEIBNIZ-BOARDS-20261110-001#2) | 2/3 — Substantial | 2/3 — Testable | Build an explicit weakly aperiodic shift of finite type on F2 and decide whether it has a free point → a free point, or a counterexample to W | Proposed · not started |
| 2 | Every accretion law (HARD-FLAT-20261107-001#3) | 2/3 — Substantial | 2/3 — Testable | As recorded there | Alternative · not started |
| 3 | Abstract names (BOARD-DIST-20261110-001#3, A54) | 2/3 — Substantial | 2/3 — Testable | As recorded there | Alternative · not started |
| 4 | Growing radius: rigid worlds at radius r with r-bit-per-view laws | 2/3 — Substantial | 1/3 — Stated | Define a uniform family of laws over r and test whether forced tori grow with r → a growing family, or an obstruction | Alternative · not started |

1. **Weakly aperiodic laws.** Payoff 2: the only place the infinitary dichotomy can fail. Concreteness 2: such shifts exist on free
   groups, but none is in hand.
2. **Accretion laws.** Payoff 2: growth as the remaining route to a chosen plane. Concreteness 2: as rated there.
3. **Abstract names.** Payoff 2: whether the naming hides a drawing. Concreteness 2.
4. **Growing radius.** Payoff 2: the finite shadow of the plane growing with the radius would be the closest a static rule comes.
   Concreteness 1: no uniform family yet.

**Recommendation.** Research directions, proposed #1 for the morning; the board-as-distinctions line has reached its static limits
in the families studied.
