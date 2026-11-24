# The smallest structure with a hidden excess: result

Ticket `THIRD-HOLDER-20261123-001B` (direction 1 of `REVIEW-LEADS-20261123-001`; G18 with G17), 2026-11-23. Exhaustive
census for named classes and exact checks; scientific referee pending. [Pre-registration](preregistration.md) ·
[full tables and commands](results_draft.md) ·
[deviations](../../experiments/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest/deviations.md)

**If the setting birth may take a distinction that already has two holders, seven knots are enough, and the old
structure needs no distinction held three times: the third holder is the birth itself. If the birth must take a loose
distinction, nothing with at most three holders was found, and the only structure known is the 18-knot one with two
distinctions held four times.**

## The seven knots

Alice: nae(x1, x2, s1), nae(x1, x3, s2), even(x2, h1, h2), odd(x3, h1, h2).
Bob: even(y2, k1, k2), odd(s1, k1, k2), odd(y1, y2, y3, s2).

Twelve distinctions, 64 allowed words, every distinction with one or two holders, both knot laws in one structure.
Alice's x1, x2, x3 each have two holders before the birth. With every present word weighted equally and the setting
birth a not-all-equal knot on x1 and x2, or x1 and x3, with one fresh distinction, the four-correlation score is
exactly 19/9 and both complete records hide the far setting. Eight knots reach the ceiling of 20/9 with two extra
holders, and so does the 9-knot structure written down before the freeze.

## What was searched

Sides of at most 4 knots and 5 internal distinctions, internal distinctions with up to three holders:

| Observer distinctions | Shared between the sides | Side tables | Hidden pairs above 2 | Largest hidden score |
| --- | ---: | ---: | ---: | --- |
| Loose (class L) | 1 | 49,081 | 0, by argument | 2 |
| Loose (class L) | 2 | 221,545 | 0 | 2 |
| Loose, sides of 5 knots | 2 | 2,403,586 | 0 in 4.03 billion pairs scored | 2 |
| May already be shared (class S) | 1 | 390,107 | 0, by argument | 2 |
| May already be shared (class S) | 2 | 1,620,095 | 145 | 20/9 |

- **Lower bounds.** With loose observer distinctions: no hidden excess with both sides of at most 4 knots, nor of at
  most 5 knots with two shared distinctions. With observer distinctions that may be shared: none with 6 knots or fewer
  in all, so 7 is the least within these bounds. With one shared distinction between the sides none exists at any size.
- **Reduction.** No single knot can be removed from the 18-knot structure or from the 9-knot one: all 200 seeded
  orders end where they start.
- **Seeded search.** 2,000,000 lawful drawn sides per class of up to 9 knots. Nothing smaller than the census found;
  nothing at all with loose observer distinctions.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed | With two holders the enumerator reproduces the earlier census (596 and 3,018 side tables, largest hidden score exactly 2); brute force agrees with side tables on 100 drawn pairs with a third holder |
| P1 | Failed | No structure with loose observer distinctions and at most three holders was found by census, reduction or search |
| P2 | Held | None with both sides of at most 4 knots |
| P3 | Held | 7 knots |
| P4 | Held | The 9-knot structure gives 20/9, hidden, by full enumeration |

The thread enumerated the 7-knot and the 9-knot structures from their knot lists with separate code: 64 old words
each, 19/9 and 20/9, hidden, and in the 7-knot one no distinction with more than two holders.

## What this is about

About structures and a move ordinary growth never makes, under a supplied weighting and supplied settings. Pairs were
scored only where an exact reduction could not exclude them; the reduction was checked against pairing every ordered
pair on a test class. The census of sides of 5 knots was run for loose observer distinctions with two shared
distinctions only. Large regenerable files were removed from the outputs (`PRUNED.md`).

**Verdict.** Supported, with one prediction failed. The pre-registration expected a third holder to be enough when the
observer's distinctions are loose; nothing found says so. What is enough is narrower and simpler: a birth that takes a
distinction already held twice. With that one move the smallest structure has seven knots, both laws, and nothing else
out of the ordinary.
