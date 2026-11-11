# Closure of what it takes to hold a count

Status: Proved

Ticket `HOLD-COUNT-20261111-001Z`, 2026-11-11.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/HOLD-COUNT-20261111-001/hold_count.md`.

Words (2026-11-11). Reworded under the owner's language rule: a knot space is now a drawn knot pattern, its points
distinctions and its lines knots, an atom a piece and a world of knots a pattern (Intuitions guide, Glossary). The
mathematics is unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A drawn knot pattern with the not-all-equal law reads a count of n held distinctions mod m (n >= m - 1) only for even m and odd n; it holds the count of three mod 4 exactly as a full adder. | classical in substance (Post's self-dual functions) | A, refereed |
| 2 | The 8-point parity torus (2,0,4) is a full adder; 13 of 1,128 spaces hold one. | exhaustive computation | A |
| 3 | No space of the census holds the count of three held points mod 3 or mod 4 with one held reference point. | exhaustive computation | A |
| 4 | Of the four kinds of self-dual map using all four of four held points, the census spaces show only the weighted majority and maj(a, b, a+c+d), the two that cannot count mod 3. | computed after the run | A |

## Answer

The knot law writes a count in binary at its least size, and counts in threes need more than one fixed value from outside.

## Recommendation

**Continue:** does a drawn knot pattern read its own relation (a xor NAE, or the parity-majority switch), awaiting a go-ahead.
