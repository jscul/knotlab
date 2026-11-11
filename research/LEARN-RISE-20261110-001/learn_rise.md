# Learning at a rise

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `LEARN-RISE-20261110-001` (backlog B80, G15; program learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in
[preregistration.md](preregistration.md). Proof family: `proofs/LEARN-RISE-20261110-001A/LEARN-RISE-20261110-001A-P001_swapping_the_atoms_roles/`
(long-running row LEARN-RISE-A1); post-hoc search [posthoc_targeted.py](posthoc_targeted.py).

## The question

The leftover dissonance sits in whichever Fano piece acts as its line (`LAW-HOLDS-20261110-001`), so moving it means changing the law, and
at the floor learning has no step. One unit above the floor it does. With the state moving and learning acting, can the leftover be
carried to the other atom?

## The answer

Yes, computed, but by a post-hoc search. The pre-registered breadth-first search stopped at its cap everywhere: it reaches only about four
moves deep. A targeted search over the same moves, aimed at a floor state of a law in which the other atom acts as its line, found a path
from all 9 starts: 16 to 43 moves, of which 4 to 16 are learning steps, never more than one unit above the floor. At the end the atoms have
swapped roles (7) or both are transparent (2).

For the owner's picture: the point can carry a pattern's leftover tension to another pattern, but only together with learning. The state
moves the dissonance up and around; learning rewrites which pattern stands for the contradiction; and the tension settles where the new
learning puts it.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| No path of about four moves or fewer reaches the other atom | computed (frozen breadth-first search, capped) |
| Paths of 16 to 43 moves reach it on all 9 starts, with learning steps and flips, at most one unit above the floor | computed (post hoc, targeted; paths not shortest) |

## Against the pre-registration

R1 is not decided by the frozen test (capped); post hoc it holds on all 9 starts. R2 held in kind (both learning and flips on every path)
and failed in length (only 2 of 6 K_2 paths within 20 moves).

## Corrections

None.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — learning at a rise (B80) | **Status:** Partially successful | frozen test capped; post hoc the leftover moves |
| Local direction — moving the leftover by learning | Continue | it works, with the state's help |
| Broader exploration — learning program | Known alternatives | choosing the atom, shortest paths |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | learning places a pattern's tension |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Learning chooses which atom holds the leftover (B81) | 2/3 — Substantial | 3/3 — Ready | three or four atoms on K_3, a target atom named → the targeted learner places the leftover in each, or some atom is unreachable | Selected · awaiting go-ahead |
| 2 | Why the trap holds (B78) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |
| 3 | Learning on an overgrown surface (B70) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1** reads the leftover as a stored symbol: if learning can put it in any chosen atom, the network holds a learned address.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); B80 taken; B81 added. **Assumptions:** none new.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (02:16 UTC).

**B80 done: learning can carry the leftover tension to another pattern, with the point's help.** My pre-registered search ran out of room: it could only look about four moves deep, so it's inconclusive. A targeted search afterwards (post hoc, labelled as such) aimed at a law where the other atom acts as the line. It found a path from all 9 starts: 16 to 43 moves, mixing state flips with 4 to 16 learning steps, never more than one unit above the floor. The atoms swap roles and the tension follows. So the state moves the dissonance up and around, learning rewrites which pattern stands for the contradiction, and the tension settles where learning puts it.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: learning at a rise (B80) | **Status:** Partially successful | frozen test capped; post hoc it works |
| Local direction: moving the leftover by learning | Continue | works with the state's help |
| Broader exploration: learning program | Known alternatives | choosing the atom, shortest paths |
| Long-term goal: G15 | Capability gained | learning places a pattern's tension |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Learning chooses which atom holds it (B81) | 2/3 — Substantial | 3/3 — Ready | 3–4 atoms on K_3, a named target → every atom reachable, or not | Selected · awaiting go-ahead |
| 2 | Why the trap holds (B78) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |
| 3 | Overgrown surfaces (B70) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

#1 would make the leftover a learned address: a symbol the network holds, placed by learning, readable by where the tension sits.

**Corrections:** none. **Goals:** G15 checkpoint; B80 taken; B81 added. **Assumptions:** none new.
