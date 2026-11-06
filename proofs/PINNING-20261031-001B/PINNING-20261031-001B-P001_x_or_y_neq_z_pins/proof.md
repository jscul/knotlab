# x ∨ (y ≠ z) pins, so it is NP-complete on cubic systems

Status: Proved

Ticket `PINNING-20261031-001B`, 2026-10-31.

## Dependencies

- **`PINNING-20261031-001A`.** Lemma 1 (five classes), Theorem 4 (the pinning theorem), Proposition 5 (Schaefer status), and its
  library `pin_lib.py`, bound by hash.

## The law

- **The relation.** R = x ∨ (y ≠ z) = {x = 1} ∪ {001, 010}. Its truth table over 000, 001, …, 111 is 01101111. It is the only asymmetric
  three-place knot class: 12 relations under flips and permutations.
- **Schaefer status.** It lies in none of Schaefer's tractable classes, so it is NP-complete with unbounded occurrences (check 1).

## Theorem

**Statement.** Deciding x ∨ (y ≠ z), with signs and any order of places, on simple cubic systems is NP-complete. Its unsolvable cubic
systems are therefore coNP-complete to recognise.

**Proof.** The three hypotheses of the pinning theorem hold (check 2; each piece re-verified by enumeration).
- **A pinning piece.** It has internal points 0–3 and the lines (0,1,2), (0,1,3), (0,2,3), (1,2,a), (3,b,c), with relations given by the
  truth tables 11111001, 10011111, 10011111, 10111110, 11111001. It accepts exactly a = 0. This is the skeleton that also pins the
  Fibonacci law and parity (ticket A).
- **A link.** With x pinned to 0, R(0, y, z) is y ≠ z, a disequality.
- **A full piece.** The lines (0,1,a), (0,1,b), (0,1,c) with relation 11111001: setting the internal points to make the first place true
  satisfies all three lines whatever a, b, c are.

By ticket A, Theorem 4, the unbounded problem reduces to simple cubic systems. The unbounded problem is NP-complete (Schaefer). ∎

## Checks

| Check | Result |
| --- | --- |
| 3. Reduction | 80 random instances with any number of occurrences become cubic, simple systems of up to 205 lines with the same solvability; 4 sources were unsolvable. |
| 4. Small systems | No failure on any cubic system with n = 4 or 5, exhaustively: 20,736 and 2 × 248,832 relation assignments. None in 400 samples each at n = 6, 8, 10. |
| 4. Explicit failure | Two pinning pieces with opposite pins, glued at the pinned port and padded with full pieces, form an unsolvable simple cubic system of 25 lines. The unsolvable sources of check 3 give larger ones. |
| 5. Controls | Reading the disequality link as an equality breaks the reduction (7 of 40 instances disagree). R is not unchanged by flipping every place. |

## Reading

- x ∨ (y ≠ z) prefers a value (the face x = 1 satisfies it), and it pins.
- Its failures are rare on small systems, much as Tovey's argument would suggest: a face lets a line be satisfied by one point alone. But
  they exist, and recognising them is as hard as deciding satisfiability.
- Like the Fibonacci law, it has no mutual selection unless P = NP.

## Novelty

The reduction pattern is standard. The explicit pieces for this law, and the observation that one skeleton pins every pinning knot, have
no overlap found yet.
