# Starts where both distances grow

Epic `BOTH-LONG-20261126-001`, under G18, at the coordinator's go-ahead after `SECOND-CHECK-20261126-001` (after one
round a ring's class is read across the ring and changed by five distinctions, or the reverse: one distance short). Two
questions: does ordinary growth itself make structures whose class is both read and changed only by many distinctions,
growing with size; and on such a structure, is there a native reading under which the two kinds of whole-loop fact
change each other, so that a relative sign is set by the structure? Computed; advisor consulted read-only in the
repository ([question](advisor_question.md), [answer](advisor_answer.md)); referee pending.


> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, no Block.** All 50 ring preparations and 44 from six
> sampled starts matched. **Narrowings:** the ring's size bounds the smaller distance (eight knots, round four: 8/11 free,
> 9/8 pinned); of the 350 sampled starts, 153 reached round four and 75 ever had a class; **"a start with a long cycle is
> rare" is wrong**: cycles of five or more knots occur in 99 of 200 census starts and 85 of 150 extension starts, yet their
> distances stay small, so a long cycle in the start is not enough; the old odd ring attains both minima but so do other
> sets; one sampled start had 128 ties through a distinction, over the cap of 64 (keeping every tie reproduced its
> distances); a recorded reading does use the class character as a supplied weighting; with loose values pinned at
> nonzero values a positive class can still be singled out. Logged in `docs/CORRECTIONS.md`.
## How the distances are read ([`distances.py`](distances.py))

Under parity a structure is a graph: knots as vertices, each shared distinction an edge between its two holders, and,
with loose values free, each loose distinction an edge to one extra unconstrained vertex, so the allowed changes are
exactly the cycles. The moves are the shortest cycles through each edge (the motion study's rule, every tie kept up to 64,
with the cap's hits counted); H their span. **Change distance:** the least cycle outside H, found among the literature's
Horton candidates (a shortest path from a vertex to each end of an edge; a least cycle outside any subspace is among
them, by the advisor's argument). **Read distance:** the least class label (a set with even overlap with every move and odd
overlap with some cycle), by an exact solver, one class generator at a time (exact for two classes, an upper bound for
four or more).

## What was found

- **Rings grown round by round** (n knots with two loose distinctions each; `rings_dist.jsonl.gz`):

  | | Loose values free | Loose values pinned |
  |---|---|---|
  | Odd rings (n = 5, 7, 9, 11) | read n; change 5, 7, … rising by two a round to n, then n (both n from about (n − 3)/2 rounds) | read 3, 5, … rising to n; change n (both n from about (n − 1)/2 rounds) |
  | Even rings (n = 4, 6, 8, 10, 12) | read n; change 2r + 3, rising without bound in the rounds read | n = 8, 10, 12: read 2r + 1; change n, the old ring, which is not a label (n = 4, 6: one class) |

  So **ordinary growth does make a class with both distances long**: on every odd ring both reach the ring's length n
  and stay there to round 6. But neither distance ever exceeds n: the length scale is the start ring's, a built start
  (the advisor's point). Growth supplies the class (a bare ring has none) and the second long distance; the first is the
  ring itself.
- **Sampled starts** (seed 20261127: 200 census starts of three to five knots and 150 of the six-to-eight-knot extension,
  grown to round 4; `census_dist.jsonl.gz`, `extension_dist.jsonl.gz`): the largest min(read, change) is 4, at one
  start, the four-knot ring itself; otherwise 3 or less. Under these weightings a start with a long cycle is rare, and
  without one growth does not lengthen both distances *(R1: wrong; long cycles are common in the sample, and growth still
  does not lengthen both distances there)*.
- **On odd rings the old ring is its own conjugate.** The least class change is the old ring r itself, and it is also a
  class label (r overlaps every move evenly and some allowed change oddly), from the round both distances reach n (pinned:
  from round 1); r overlaps itself oddly (n odd), so changing by r flips the parity read of r. On even rings the least
  change (pinned: the old ring) is not a label. The tie cap of 64 was never reached; the solver timed out on five late
  rows of the largest rings (not run).

## Is the relative sign set by the structure? (an argument, with the advisor's corrections)

The class character, +1 on the class of the all-zero state and −1 on the other, is invariant under every move and changes
sign under the long change. It is not peculiar to odd rings: every two-class structure has it, and every label gives the
same function on the allowed states. What odd rings add is narrower: one set, the old ring, is both a least change and a
least label. The character is fixed by the structure only because the all-zero state is allowed (with loose values pinned
at other values there is no canonical choice), and it sums to zero over the allowed states, so it is a signed function,
not a weighting of samples. No recorded reading weights by it (searched: the motion study uses the old ring's parity as a
read; the sign studies' weightings are quadratic, products of parities or differences of indicators); using it as a
weight is the motion study's supplied signed read. **So the structure fixes which signed function a relative sign would
be, and growth makes the class it lives on with both distances long, but no native reading uses it.**

## The next-layer question (for the other thread)

One ring gives one two-valued whole-loop fact with nothing to relate it to: a candidate distinction, not a layer. The
advisor's test, not run here: grow two or three odd rings that meet, read the classes and their labels, and ask whether
some sum of ring labels is forced on every allowed state while no single label is (a next-layer parity knot), and
whether a least class change changes exactly two of them (a next-layer move).

## What this does not say

- That growth lengthens both distances beyond the start's ring; no row read does.
- Other move rules (the classes are the move rule's, A291); not-all-equal; rings beyond twelve knots or six rounds.
