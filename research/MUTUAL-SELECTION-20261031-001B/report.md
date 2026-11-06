# Lane B: parity and the clauses with signs

Ticket `MUTUAL-SELECTION-20261031-001B`, 2026-10-31. Scouting pass (documentation); no theorem is activated.

## Question

With signs every knot can be posed on a cubic system. For parity and for the clauses: are the unsolvable systems recognisable, and do they
make any law easy beyond the universally easy ones?

## Findings

1. **Parity's unsolvable systems are recognisable, but select nothing.**
   - A signed parity system is a linear system Ax = b over GF(2), with A the line–point incidence matrix. It is unsolvable exactly when b
     lies outside the column space. On a graph with GF(2)-rank r that happens for 2ⁿ − 2^r of the 2ⁿ right-hand sides; checked on every
     census graph with n ≤ 7.
   - The whole coupling family f_λ = [1, λ, 1, λ] has Hadamard transform supported on {000, 111} for every λ: 4(λ + 1) and −4(λ − 1). It
     is a generalized equality, affine and polynomial on every graph.
   - So parity's family is easy everywhere, and its unsolvable spaces select nothing.
   - The other laws stay as hard on parity spaces as on all signed systems. For a law symmetric under complement, switching a line leaves
     its count unchanged but flips that line's parity right-hand side, so a hard instance can be moved into the parity-unsolvable class
     whenever A is singular. This is a sketch, not checked here.
2. **Clauses never fail.**
   - Every signed cubic system of three-literal clauses is satisfiable (Tovey 1984). A cubic bipartite graph has a perfect matching, so
     each clause owns one of its variables and sets it.
   - Checked on all 1,380,864 signings of the census graphs with n ≤ 6. The unsolvable class is empty.

## Reading

Neither law shows mutual selection. Parity's failures are recognisable, but its whole family is easy, so the selection is vacuous.
The clauses never fail.

## Interest as a standalone epic

**0/3 — Cold.** These are classical facts, recorded for the decision.

## Files

- `parity_clause.py`: the checks (run with `--write`; reads `../MUTUAL-SELECTION-20261031-001C/census.json`).
- `results.json` and `parity_clause.log`: the output.
