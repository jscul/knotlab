# Several addresses in sequence

Epic `ADDRESS-SEQ-20261110-001` (backlog B88, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md). Tickets A (`proofs/ADDRESS-SEQ-20261110-001A/`, long-running row ADDRESS-SEQ-A1) and B
(`proofs/ADDRESS-SEQ-20261110-001B/`).

## Answers (computed, small cases)

- **A, writing in sequence.** On 14 spaces (three Fano atoms on every line orbit of K_3 and K_4 and, one size past, on the first three of
  K_5; four atoms on every orbit of K_3), 90 addresses were written in turn, each followed by a random disturbance and return. Every write
  reached its target and every address was held: the acting atoms after the return were always the address just written, never the
  previous one. The memory is rewritten cleanly and keeps no trace of earlier addresses. Neither frozen interference nor frozen failure
  occurred.
- **B, the 17 unsettled runs of `ADDRESS-STEER-20261110-001`.** Seven reached the floor with one or both acting atoms turned transparent
  during the return, and the exact rule holds in all seven: these are learning steps that wound through an atom's handle and erased its
  bit. Ten stopped one unit above the floor with no move lowering the dissonance, local minima of the learner.

For the owner's picture: the learned network holds an address, can be rewritten, and forgets the old address completely. Disturbances
almost never erase it; when they do, it is by a learning step that rewrites one pattern's bit.

## Corrections

None.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — addresses in sequence (B88) | **Status:** Successful | 90 of 90 written and held; the 17 runs explained |
| Local direction — a learned memory in atoms | Continue | rewritable, at K_5 too |
| Broader exploration — learning program | Known alternatives | the proof; capacity |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | a rewritable learned register |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A proof of the atom rule (B87) | 2/3 — Substantial | 2/3 — Testable | role set by own handle; acting atom forces a unit → a proof, or a counterexample | Selected · started |
| 2 | Why the trap holds (B78) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1** is next by the coordinator's order.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B88 taken. **Assumptions:** none new.
