# The locking rule and overlapping loops

Status: Proved (L1 to L3 and the overlap facts by hand, with the advisor model) with an exact census of two arms; **referee pending**.
Ticket A of `research/LOOP-LOCK-20261112-001/preregistration.md`, frozen with the code in commit `36fd0e934`.

## 1. The rule (proved; exact on every cell)

- **L1.** A closed chain of k knots locks exactly when k is below the girth g of the step relation: 495 of 495 cells (45 harmonies,
  k = 2 to 12).
- **L2.** The open chain is free at every length exactly when the step relation has a step: 495 of 495 cells; the proof is the walk
  that stays, steps once and stays, at any place.
- **L3.** The seven harmonies whose loops lock have girths 8, 4, 12, 4, 7, 16 and 8. The one-orbit ones among them have one step
  offset (00101101: D = {5}, g = 8; 001010110101: {7}, g = 12; 0010101011010101: {9}, g = 16), so g = P, or several (0010011011:
  {1, 4, 7}, g = 4). Every other harmony has g = 2: its loops never lock.

## 2. Overlapping loops (exact)

| Pattern | Outcome | Against the advisor's rule |
| --- | --- | --- |
| Two loops through one shared copy (figure eights 3+3 to 6+6) | each loop locks exactly as it would alone | 75 of 75 |
| Two loops sharing a knot (3+3 to 6+6) | lock together exactly when g > max(1 + b₁, b₂); a lock spreads from a loop that locks alone to one that does not (two harmonies, 3+4); never a lock that neither loop has alone | 75 of 75 |
| Two loops sharing two copies and no knot (the crossed pair) | each fails alone and the union locks, for both harmonies with g = 4 | predicted (95%) |
| Circulants (n copies, steps +1 and +2), n = 5, 7, 9 | each loop fails alone and the union locks in 7 cells; strictly (no round trip of the union shorter than g) for 00101101 + 0011 at n = 7 = 2g − 1 | as predicted where tested; the one-generator case at n = 2g − 1 was out of range |
| Open chain of 8 (control) | every shared copy in its own class | as required |

## 3. Rings and drawn nestings (exact)

- **One-shift rings (each knot sharing two distinctions with the next).** Whole rings lock, every copy tied to the root, for many
  harmonies whose simple loops never lock (g = 2), and whether they do depends on the ring's length against the harmony's period:
  0011 locks the rings of 5, 6, 7, 9, 10 and 11 and not of 4, 8 or 12 (the multiples of its period 4); 0000011111 locks 4, 6, 8 and 11
  but none or almost none of the rest; 00101101 locks every odd ring and half or less of each even one. Locking on rings is
  arithmetic in the length and not monotone, as the advisor expected (65%).
- **Drawn three-copy nestings, levels 1 to 3.** No copy tied to the root for any harmony but the alternation, whose tied copies
  double (2, 4, 8 of 5, 14, 41).

## What this establishes

- Proved: which loops lock (k < g), the open chain free at every length, and the overlap facts (independence through one copy; the
  ear rule; no collective lock through a shared knot).
- Exact: crossed pairs and circulants lock collectively; rings of overlapping knots lock or not by the arithmetic of their length,
  even for harmonies whose simple loops never lock; drawn nestings tie nothing except for the alternation.
- Classical in kind: the rule is the girth of a reflexive digraph and, for one orbit, a zero-sum question on Z_P.
