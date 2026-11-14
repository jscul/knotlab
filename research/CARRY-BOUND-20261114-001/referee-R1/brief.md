# Referee brief CARRY-BOUND-R1 (from the coordinator, 2026-11-14, Codex-assisted)

**The epic.** `CARRY-BOUND-20261114-001`, commit 722b89388. The note is `carry_bound.md`; the pre-registration and addendum are
99b396c40, cc2ece62c and c75547967.

**Claims.**
- **The window (Lemma W).** It bounds L at every large depth in 5,074 of the 5,789 in-scope families, with bounds of at most 4.
- **The live quotient (Lemma G).** 632 families grow, since their carried values are never read.
- **What is left.** 83 families are undecided.
- **The census split.** First-ray growth splits 58.0 / 39.6 / 2.4.
- **Two corrections logged.** A Narrowing of TIE-CYCLE's reading, and a Not-a-block on the pre-registration's fixed point in G.

**The owner's least-sure points.**
- Lemma W's exactness and identity merging.
- Lemma G's soundness when a carried port is constrained above but unread below.
- Whether the frozen cap rule correctly leaves 2 complete window bounds undecided.
- "Bounded at every large depth" with its exact depth threshold.
- Whether the split uses CENSUS-FORGET's covered-target scope.
