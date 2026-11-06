# Lane C: the signed Fibonacci law

Ticket `MUTUAL-SELECTION-20261031-001C`, 2026-10-31. Scouting pass (documentation). The hardness argument below is complete and checked,
but it is not activated as a theorem here.

## Question

The Fibonacci laws are the no-lone laws: {0,2,3} forbids exactly one 1, and {0,1,3} is its complement. With parity they are the
program's topological knots. With signs they can fail on cubic systems. Can the unsolvable ones be recognised in polynomial time, as for
not-all-equal (Pfaffian signings)?

## Findings

1. **Census** (`census.py`, every connected cubic bipartite graph on 2n ≤ 16 vertices, every signing up to point switching):

   | n | graphs | with Fibonacci failures | with not-all-equal failures (Pfaffian) | with both |
   | --- | --- | --- | --- | --- |
   | 3 | 1 | 0 | 0 | 0 |
   | 4 | 1 | 0 | 1 | 0 |
   | 5 | 2 | 1 | 0 | 0 |
   | 6 | 5 | 2 | 1 | 0 |
   | 7 | 13 | 8 | 2 | 0 |
   | 8 | 38 | 22 | 4 | 1 |

   - The failing signings per graph (14, 63, 72, 84, 160, 200, 240, 640, …) are not powers of 2, so they form no single switching class.
   - The two laws {0,2,3} and {0,1,3} fail on the same number of signings per graph, since switching a line exchanges them.
   - Failures are global. On simple systems the smallest conflicting set of lines is usually the whole system, like the Fano plane for
     not-all-equal.
2. **The Fibonacci gadgets are rich** (`gadget.py`). Gadgets are systems with three ports (one incidence each) and k ≤ 5 internal points:
   58.5 million signed structures, simple and with repeated lines.
   - They reach 15 of the 22 relation classes on three ports up to flips and permutations.
   - Among them are not-all-equal and a *constant* relation: one port forced, the other two free.
   - Neither exactly-one nor all-equal is reached directly at this size.
3. **Not-all-equal gadgets are rigid** (`gadget_nae.py`, the same 58.5 million structures). They reach exactly three relations: nothing,
   everything, and not-all-equal itself up to signs. So they never force a constant, and they cannot fan out. In particular they never
   reach the Fibonacci relation.
4. **The signed Fibonacci law is NP-complete on cubic systems** (`hardness.py`).
   - *Constant gadget.* Four internal points and five lines force one port to 1 and leave the other two free: lines (0,1,2), (0,1,3),
     (0,2,3), (1,2,a), (3,b,c) with signs 000, 010, 011, 000, 000.
   - *Equality line.* A no-lone line in which one point is seen as 0 accepts exactly the states where its other two points are equal.
     Chains of such lines copy a variable any number of times, each copy carrying one occurrence.
   - *Full gadget.* Lines (0,1,a), (0,1,b), (0,1,c) accept everything; they absorb spare occurrences. Fresh points are added until no
     point has more spare occurrences than one third of the total; then the three points with most spare occurrences are taken each time.
   - *Reduction.* Any instance of signed no-lone constraints, with any number of occurrences per variable, becomes a simple cubic system
     with the same solvability. Checked on 60 random instances, 20 of them unsolvable, giving cubic systems of up to 149 lines.
   - *Source.* The unbounded problem is NP-complete by Schaefer's theorem: the signed no-lone relations are not all 0-valid, 1-valid, Horn,
     dual-Horn, bijunctive or affine.
   - *Conclusion.* Deciding the signed Fibonacci law on cubic systems is NP-complete, so its unsolvable spaces are coNP-complete to
     recognise. Connected instances follow by joining components through full gadgets.

## Reading

- The Fibonacci knot fails on cubic systems, but its failures cannot be recognised unless NP = coNP. It has no mutual selection.
- The contrast with not-all-equal is visible in the gadgets.
  - Not-all-equal gadgets are rigid (nothing, everything, itself), which matches the Pfaffian structure.
  - Fibonacci gadgets reach constants, and a constant turns one line into an equality, which gives unlimited fan-out.
- **Not established.** That not-all-equal gadgets are rigid at every size. This is checked for k ≤ 5 only; at every size it would be a
  gadget-side explanation of the Pfaffian theorem.

## Interest as a standalone epic

**1/3 — Exploratory poking** for the hardness itself, a routine reduction once the constant gadget is found. **2/3** for the rigidity of
not-all-equal gadgets at all sizes, which would explain the knot's tractability from inside the law.

## Files

- `census.py`, `census.json`, `census.log`: the census.
- `gadget.py`, `gadget.json`, `gadget.log`: the Fibonacci gadget search and its catalogue.
- `gadget_nae.py`, `gadget_nae.json`, `gadget_nae.log`: the converse search with not-all-equal lines.
- `hardness.py`, `hardness.json`, `hardness.log`: the constant gadget and the checked reduction.
