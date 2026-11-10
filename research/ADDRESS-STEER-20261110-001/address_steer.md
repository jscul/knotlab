# Does the stored address steer later learning?

Epic `ADDRESS-STEER-20261110-001` (backlog B86, G15; program learning), 2026-11-10, at the coordinator's go-ahead, as a fuller epic with
failure stated in advance. Pre-registered in [preregistration.md](preregistration.md). Tickets A (`proofs/ADDRESS-STEER-20261110-001A/`),
B (`.../001B/`) and C (`.../001C/`, long-running row ADDRESS-STEER-C1).

## Answers

- **A, the rule behind the exception (exact, SAT over every state, 1,280 classes of 11 spaces).** With no even face, the floor states are
  exactly the states satisfying every line. If every Fano atom acts as its line there are none; otherwise every acting atom holds a unit in
  every floor state; and when fewer atoms act than there are units, the extra units can sit anywhere, including outside every acting atom.
  Each atom acts in exactly one of the four classes of its own handle, independently of the others. So "the acting atoms are the address" is
  a rule whenever as many atoms act as there are units; `READ-ADDRESS-20261110-001`'s exception is a class with fewer, where one unit is free.
  The pre-registered failure (a class breaking the rule) did not occur.
- **B, four atoms (computed, frozen search).** Every triple of four atoms was written as the holders of the three units on every line orbit
  of K_3 (12 of 12). Writing now holds in 36 of 36 cases (K_3 and K_4 with three atoms, K_3 with four).
- **C, a fresh tension (computed).** After one random upper flip, a learner that lowers the dissonance returned to the written law's acting
  atoms in 240 of 240 runs; after two or three flips in 463 of 480. The stored address decides how a new tension resolves: it comes back to
  what was learned. The pre-registered expectation (80% at k = 1) held on every configuration read by acting atoms, and on 23 of 24 read by
  the written pair (the 24th is the exception's single-acting configuration, whose acting atom was kept 30 of 30).

For the owner's picture: in this learned network the memory is a set of patterns that stand for their lines. Learning writes it, the law
keeps it in every state, each pattern carries its own bit in its own signs, and a fresh disturbance settles back into it. All of this is
computed or exact on small cases (K_3 and K_4, three or four atoms); a proof for every sphere is not written.

## Corrections

None.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — does the address steer later learning (B86) | **Status:** Successful | exact rule, writing at four atoms, memory survives tension |
| Local direction — a learned memory in atoms | Continue | rule exact on small cases; proof open |
| Broader exploration — learning program | Known alternatives | a proof, sequences of addresses |
| Long-term goal — G15 Learning: a point in a learned knot space | Capability gained | memory written, kept and steering resolution |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A proof of the atom rule (B87) | 2/3 — Substantial | 2/3 — Testable | each atom's role is set by its own handle's class, and an acting atom forces a unit in its region → a proof for every knot sphere, or a sphere where it fails | Selected · awaiting go-ahead |
| 2 | Several addresses in sequence (B88) | 2/3 — Substantial | 3/3 — Ready | write, disturb, rewrite in turn → each new address held, old ones overwritten cleanly, or interference | Alternative · deferred |

- **#1** would turn the rule from exact-on-small-cases into a theorem: both halves look local (the handle's class, the atom's own lines).
- **#2** reads the memory as a register that can be rewritten.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B86 taken; B87 and B88 added. **Assumptions:** none new.
