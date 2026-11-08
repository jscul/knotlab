# Closure of growing a network of rings from a law

Status: Proved

Ticket `GROW-NET-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GROW-NET-20261108-001/grow_net.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every n x m torus of equally spaced rings (n, m >= 3) has a half-turn at every contact, so growth by inserting bands or splitting every ring into blocks keeps every contact persistent at every stage. | known-with-delta; proved | A |
| 2 | Attaching one new ring breaks persistence: by one contact, by two contacts not forming a bubble, and as a bubble on p -> q exactly when some contact is reached from q and reaches p. | known-with-delta; proved | A |
| 3 | Of 795,042 attachments of one ring to 16 balanced seeds, none by 1 or 2 contacts keeps persistence and none by 3 or 4 on a seed of more than four rings. | not found in prior work; exploratory census | B |
| 4 | Truncating or rectifying the Platonic networks loses persistence, except the rectified tetrahedron. | not found in prior work; exploratory census | B |

## Answer

On the torus, growth by whole bands or blocks keeps every contact persistent, by proof; growth one ring at a time does not.

## Pending the owner

- Nothing new; the owner ruled on counted length on 2026-11-08, and distance runs in its own thread.

## Recommendation

**Research directions**: making the surface by growing whole bands (Payoff 3/3, Concreteness 1/3), or the ready proofs of full reach
and of which lattices compose everywhere (Payoff 2/3, Concreteness 3/3). The table is in the decision note.
