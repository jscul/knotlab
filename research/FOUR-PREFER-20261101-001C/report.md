# Five weak classes never failed

Ticket `FOUR-PREFER-20261101-001C`, 2026-11-01. Documentation with exact computation; no theorem is claimed.

## Question

- **What is settled.** Tickets A and B settle every four-place knot class except five that prefer a value and exclude only two or three
  states: classes 13, 14, 15 (three excluded states) and 16, 17 (two). With not-all-equal (18) and the clause (19) these are the weak
  classes.
- **What is known for the weak ones.** Not-all-equal and the clause provably never fail.
- **The question.** Do the other five ever fail on a 4-regular 4-uniform system?

## A counting bound

- **The bound.** A line excluding |E| states rules out |E| · 2^{n−4} of the 2ⁿ colourings. A failing system needs n|E| · 2^{n−4} ≥ 2ⁿ, so
  n ≥ 16/|E|.
- **Consequence.** Classes 16 and 17 cannot fail below n = 8, and classes 13–15 not below n = 6. Results on smaller systems are
  automatic.

## Exact search (`exact_search.py`, `exact_search.log`)

**The method.** Counterexample-guided SAT over the choice of one relation per line. It either finds a failing signing or proves that none
exists on the given system.

| Class | Excluded states | Systems decided | Failing signing |
| --- | --- | --- | --- |
| 13 | 3 | n = 5; n = 6 (two systems) | none |
| 14 | 3 | n = 5 | none |
| 15 | 3 | n = 5; n = 6 (two systems) | none |
| 16 | 2 | n = 5; n = 6 (two); n = 7 (two) | none |
| 17 | 2 | every simple system with n = 5, 6, 7; one random system with n = 8 | none |

**What the table shows.**
- **Meaningful entries.** For 13 and 15 these are the n = 6 systems; for 17 the n = 8 system, where a failure would have to be an exact
  cover. The rest lie below the counting bound.
- **Stopped runs.** The runs were stopped when the epic closed. With 48 to 96 relations per line they take minutes to tens of minutes per
  system beyond n = 6.

## Hill-climbing (`climb_small.py`, `climb_large.py`, and their logs)

**The method.** Hill-climbing over signings, minimising the number of solutions.

| Class | Simple systems n = 5–9 (23 systems) | n = 10 | n = 12 | n = 14 |
| --- | --- | --- | --- | --- |
| 13 | min 5 | 53, 58 | 140, 181 | 385, 297 |
| 14 | min 2 | 59, 60 | 187, 195 | 459, 397 |
| 15 | min 6 | 57, 57 | 121, 115 | 239, 258 |
| 16 | min 12 | 148, 144 | 493, 459 | 1359, 1369 |
| 17 | min 12 | 172, 181 | 517, 429 | 1542, 1566 |

**Control.** The same hill-climb reaches failures for every class that ticket B proves NP-complete; classes 9 and 10 fail only rarely
(earlier scan in this epic's working notes).

**The trend.** The smallest counts reached grow roughly exponentially with n. There is no sign of failure.

## Reading

- **What the evidence suggests.** The five weak classes behave like not-all-equal and the clause: they look robustly satisfiable.
- **What a proof would need.** A theorem that they never fail. It would need more than the existing arguments:
  - Tovey's matching works only for the clause, the only class with a forcing value at every place.
  - The Seymour–Thomassen argument works only for not-all-equal, whose constraints are complement-invariant.
  - The local lemma is far too weak at these densities.
- **For mutual selection.** A mutually selecting four-place knot would have to be one of these five (ticket D). Each has either no
  failures or failures never seen up to n = 14.

## Interest as a follow-up

**1/3.** A never-fails theorem for these five classes would complete the four-place picture unconditionally. The main uncertainty is
whether a general argument exists (for example a weighted Hall condition or a Thomassen-type parity argument).

## Files

- `exact_search.py`: the counterexample-guided search, using `four_lib` from FOUR-PLACE A; `exact_search.log`.
- `climb_small.py` and `climb_large.py`: the hill-climbs, using `four_lib` and FOUR-PREFER A's `prefer_lib`; their logs.
