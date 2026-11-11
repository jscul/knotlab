# Several addresses in sequence

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `ADDRESS-SEQ-20261110-001` (backlog B88, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md). Tickets A (`proofs/ADDRESS-SEQ-20261110-001A/`, long-running row ADDRESS-SEQ-A1) and B
(`proofs/ADDRESS-SEQ-20261110-001B/`).

## Answers (computed, small cases)

- **A, writing in sequence.** On 14 spaces (three Fano pieces on every line orbit of K_3 and K_4 and, one size past, on the first three of
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
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | a rewritable learned register |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A proof of the atom rule (B87) | 2/3 — Substantial | 2/3 — Testable | role set by own handle; acting atom forces a unit → a proof, or a counterexample | Selected · started |
| 2 | Why the trap holds (B78) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1** is next by the coordinator's order.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B88 taken. **Assumptions:** none new.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (02:40 UTC).

**B88 done: the learned address is a rewritable register.** I wrote 90 addresses one after another on 14 spaces: three atoms on K_3, K_4 and, one size up, K_5; four atoms on K_3. Each write was followed by a random disturbance. Every write landed and every address was held. It never fell back to the previous address, so writing leaves no trace of the old one. The 17 runs from B86 that didn't settle back split into two kinds. In 7, a learning step during the return wound through an atom's handle and erased that atom's bit, exactly as the rule allows. The other 10 got stuck one unit above the floor with no downhill move. All computed on small cases.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: addresses in sequence (B88) | **Status:** Successful | 90 of 90 written and held; the 17 explained |
| Local direction: a learned memory in atoms | Continue | rewritable, at K_5 too |
| Broader exploration: learning program | Known alternatives | the proof; capacity |
| Long-term goal: G15 | Capability gained | a rewritable learned register |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A proof of the atom rule (B87) | 2/3 — Substantial | 2/3 — Testable | per-atom role + local check → proof for every knot sphere, or a counterexample | Selected · started |
| 2 | Why the trap holds (B78) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

On B87's effort: it looks tractable without max effort. Each atom's role seems to depend only on its own handle, and "an acting atom holds a unit" only on a small neighbourhood of the atom. So the proof should reduce to a handful of finite local checks plus a decomposition argument. I'll say so if it turns out harder.

**Corrections:** none. **Goals:** G15 checkpoint; B88 taken. **Assumptions:** none new.
