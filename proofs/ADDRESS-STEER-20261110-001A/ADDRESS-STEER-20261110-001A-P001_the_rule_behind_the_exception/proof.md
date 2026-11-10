# The rule behind the exception

Status: Exact finite computation (`check.py`, SAT over every state), pre-registered in `research/ADDRESS-STEER-20261110-001/preregistration.md`.

With no even face, a state with no violated line is at the floor: each line has one agreeing corner, so the agreeing corners number n, and
E = (n − V)/2 = g − 1 at genus g. So the floor states are exactly the states that satisfy every line.

On 11 spaces (three Fano atoms at l0 and line distances 2 and 3 on every line orbit of K_3 and K_4; four atoms at l0 and distances 2, 3 and
4 on every orbit of K_3), over all 1,280 sign classes:

- **R-a.** In the one class per space where every atom acts as its line, no state satisfies every line.
- **R-b.** In every other class, every state satisfying every line has, for each acting atom, a face with three agreeing corners inside it
  or at its junctions: SAT finds no state without one.
- **R-c.** In every class with fewer acting atoms than units, some such state has a unit at a face outside every acting atom.
- **Counts.** Each atom acts as its line in exactly one of the four classes of its own handle, independently: with three atoms 1, 9, 27
  and 27 classes have 3, 2, 1 and 0 acting atoms; with four, 1, 12, 54, 108 and 81.

So the rule is exact on these spaces: each acting atom holds a unit, and units beyond the acting atoms are free. The exception of
`READ-ADDRESS-20261110-001` is a class with one acting atom for two units, where the second unit is free. "The acting atoms are the
address" is a rule whenever as many atoms act as there are units, and otherwise the acting atoms are part of the address.

Scope: K_3 and K_4, three and four Fano atoms (A48). A proof for every knot sphere is not written (backlog B87).
