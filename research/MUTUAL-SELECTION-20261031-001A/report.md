# Lane A: plain systems and the exactly-one law

Ticket `MUTUAL-SELECTION-20261031-001A`, 2026-10-31. Scouting pass (documentation); no theorem is activated.

## Question

Which symmetric three-place laws have plain unsolvable cubic systems at all? For those that do, can the unsolvable ones be recognised in
polynomial time?

## Findings

1. **Only laws that exclude both constant colourings can fail on plain systems.**
   - A symmetric law is a set W of allowed weights. If 0 ∈ W, the all-zero colouring satisfies every plain system; if 3 ∈ W, the all-one
     colouring does.
   - So a plain cubic system can be unsolvable only for W ⊆ {1, 2}: exactly-one {1}, exactly-two {2} and not-all-equal {1, 2}. All three
     do fail: random systems for {1} and {2}, and the Fano plane for {1, 2}.
2. **Among the symmetric knots, only not-all-equal can fail.**
   - The knots are the laws with full two-place projections: not-all-equal {1,2}; parity {0,2} and {1,3}; the Fibonacci no-lone laws
     {0,2,3} and {0,1,3}; the clauses {0,1,2} and {1,2,3}.
   - Only not-all-equal excludes both constants. The no-lone laws, which with parity are the program's topological knots, never fail on
     plain systems.
   - This is elementary and printed by `plain.py`.
3. **Exactly-one is NP-complete to decide on cubic systems.**
   - A set S of points meeting every line of a cubic system H exactly once is an exact cover of the points of the dual H* by its lines, in
     which every element lies in exactly three sets.
   - That is exact cover by 3-sets with three occurrences per element, which is NP-complete (Gonzalez 1985, Theoretical Computer Science
     38).
   - The correspondence was checked on 120 random systems (equal counts). Exactly-two is the same problem after complementing.
   - So the unsolvable exactly-one spaces are coNP-complete to recognise.

## Reading

- On plain systems, mutual selection is special to the knot for an elementary reason: not-all-equal is the only knot that can fail.
- The non-knot laws that also fail (exactly-one, exactly-two) cannot have their failures recognised unless NP = coNP.

## Interest as a standalone epic

**0/3 — Cold.** The facts are elementary or classical. Their value is as part of the scan's decision.

## Files

- `plain.py`: the checks (run with `--write`).
- `results.json` and `plain.log`: the output.
