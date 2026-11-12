# Harmonies substituted for distinctions

Status: Proved (E1, E2 by hand, from the pinning theorem and the twisted-pin lemmas) with an exact census of three arms; **referee
pending** (the background referee thread). Ticket A of `research/ENDLESS-BLOCK-20261112-001/preregistration.md`, frozen with the code in
commit `b602c411a`.

## 1. Every order: endless blocks lock completely (E1; exact)

On all 45 harmonies and the three test patterns, the nested base has exactly the harmony's states and every copy is equal to the root
at every place: the theorem's prediction, on every cell.

## 2. Every order, lagged: folded by the loop's net lag (E2; exact)

On the closed chain of 3 knots with every lag s from 0 to P − 1: living as predicted (some state's least period divides gcd(P, s)) in
502 of 502 cells, and the states are exactly those fixed by the shift by gcd(P, s) in all 148 living cells. **After the freeze (by
hand, labelled so):** with the referee's rule of `TWIST-PIN-20261112-001` (a twisted copy takes the states within k moves of their image
around a cycle of k knots), harmonies show no cycle-length effect here: a move, a change on a set meeting every knot at most once,
would make each of its places flippable alone, and a harmony has none, so the only state within any number of moves of t∘h is t∘h.

## 3. One order: the open arm (exact)

- **Always lives, no new tie inside a copy** (P3, the advisor's): held on every cell.
- **A single knot ties copies** only for the alternation 01.
- **Cycle-born ties (the frozen criterion): found.** In 7 of the 45 harmonies, a closed chain of knots ties copies that the chain
  unrolled three times leaves untied, for both lifts of the far end: 1,376 ties in 17 cells. After the run (descriptive,
  `after_run_longer_unrolling.py`), all 1,376 are still untied on the chain unrolled nine times, so they are not an artefact of a short
  window.
- **What they are.** For 00101101 (period 8) on a closed chain of k knots, the root copy is tied to every copy on the loop, place by
  place (equal at i, unequal at i + 4, its half period): the loop locks every copy on it into one shared state, while an open chain
  lets consecutive copies sit at different offsets. The states number 8 × 3^k: one shared state for the loop, three choices for each
  copy hanging off it.
- **Loop length matters for two harmonies.** 0010011011 and 00101101 + 0011 lock their loop at 3 knots and not at 4 or 6; the other
  five lock at 3, 4 and 6.

| Harmony (orbits) | P | Loops that lock (knots) | Cycle-born ties at 3 / 4 / 6 |
| --- | --- | --- | --- |
| 00101101 | 8 | 3, 4, 6 | 32 / 48 / 80 |
| 0010011011 | 10 | 3 only | 40 / 0 / 0 |
| 001010110101 | 12 | 3, 4, 6 | 48 / 72 / 120 |
| 00101101 + 0011 | 8 | 3 only | 16 / 0 / 0 |
| 00100101101101 + 01 | 14 | 3, 4, 6 | 56 / 84 / 140 |
| 0010101011010101 | 16 | 3, 4, 6 | 64 / 96 / 160 |
| a four-orbit harmony of period 16 | 16 | 3, 4, 6 | 64 / 96 / 160 |

- **Rings of 6 and 7 differ** in their number of states for many harmonies (the two-shift arm); no cycle-born test was frozen there.

## What this establishes

- Proved: bound in every order, endless blocks lock completely; with lags they are folded by the loops' net lags, with no
  cycle-length effect.
- Exact on the range: bound in one order (a stitch of three harmonies by their own kinds), some harmonies make a closed loop lock every
  copy on it into one state, which no open chain does, and for two harmonies only a loop of 3 knots does so.
- Not established: a rule for which harmonies lock, and why at some lengths; prior work on such loop-born phase locking was not found
  beyond the analogues in the pre-registration.
