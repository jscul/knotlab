# Travelling ladders across the fold

Status: Partial (to be set to Proved after the referee)

Ticket `ACROSS-FOLD-20261112-001A`, 2026-11-12. The statement ("Theorem L") is in `research/ACROSS-FOLD-20261112-001/preregistration.md`.

## Standard statement

In the sheared frame of base 16 (the 3-uniform hypergraph on Z² with edges {z, z+(0,1), z+(1,0)} and {z, z+(0,2), z+(1,2)}), let L_y
for y ≥ 2 be {(0,0), (0,1), (0,2)} ∪ {(0,4), (0,6), …, (0,y)} (y even) or {(0,−1), (0,0), (0,1)} ∪ {(0,3), (0,5), …, (0,y)} (y odd).
For y = 2, …, 8 and every k ≥ max(3, ⌊(y+1)/2⌋ + 1), L_y ∪ {(k, y)} is a minimal non-shattered set under proper 2-colourings, of
size ⌊(y+1)/2⌋ + 3. So (k, y) is at bond distance at most ⌊(y+1)/2⌋ + 2 from the origin there.

## Proof

**Forcing.** By FOLD's column rule, a pair c_x(r) = c_x(r+1) forces c_{x+1}(r) ≠ c_x(r) and a pair c_x(r) = c_x(r+2) forces
c_{x+1}(r+2) ≠ c_x(r). If L_y is all a in column x, the triple's three pairs force the triple's rows in column x+1 to ā (FOLD), and
each rung r (two rows above the previous member) is forced to ā through the pair (r − 2, r). So L_y is all ā in column x+1, and by
induction all a·(−1)^k in column k: the value at (k, y) is forced, and L_y ∪ {(k, y)} is not shattered (check C1 verifies the step).

**Minimality.** Every proper part is shattered for the stated k: check C2 decides it exactly for every such k, by states periodic in
the row coordinate (periods from the set's row span + 3 to 11): their columns form a finite transfer graph, the columns reachable in k
steps from a column with an infinite past are eventually periodic in k, and the union over periods is decided on a finite range of k.
For y ≥ 5 and 3 ≤ k ≤ ⌊(y+1)/2⌋ the set is not minimal: a pure ladder of rungs two rows apart, without the triple, shrinks by one rung
per column and already forces (k, y) (C2 lists the failing k). Without the rung below the top (y ≥ 4) the set is not constrained at
k = 3 (C3). ∎

## Nearest known result

The mechanism is FOLD's (directional forcing; Ledrappier's shift as the nearest precedent). Classification: known-with-delta.

## Checks

`check.py` (result in `result.json`).
