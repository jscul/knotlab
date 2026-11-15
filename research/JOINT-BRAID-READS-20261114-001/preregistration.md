# How much a message must retain for simultaneous crossing tests

November 14, 2026 (Pacific). Goals G3 and G16.

## The question

On b pairs of three labels, how many bits must a message retain about an arbitrary set of joint states when a later reader chooses one crossing power and one desired label per pair and asks for a single state passing them all?

## Prior work in the program

`scripts/track.py objects "braid crossing summary" --until 2026-11-14 --exclude JOINT-BRAID-READS-20261114-001 --limit 3`

`scripts/track.py objects "one-way communication joint queries" --until 2026-11-14 --exclude JOINT-BRAID-READS-20261114-001 --limit 3`

`scripts/track.py objects "simultaneous allowed states" --until 2026-11-14 --exclude JOINT-BRAID-READS-20261114-001 --limit 3`

- `TRUE-RATE-20261113-001` studied Carried top ports among certified bounded and growing nested rules. This study uses independent reversible crossings followed by one common existential quantifier on an arbitrary correlated table.
- `LOOP-LOCK-20261112-001` studied Locks in overlapping closed chains and circulants of stitched harmony copies. This study uses independent reversible crossings followed by one common existential quantifier on an arbitrary correlated table.
- `TIE-CYCLE-20261114-001` studied Forced ties and idempotent types in the product semigroups of nested families' per-call port relations. This study uses independent reversible crossings followed by one common existential quantifier on an arbitrary correlated table.
- `LIMIT-STATE-20261112-001` studied Joint placements of all-equal call ends at three consecutive dead depths in genuine limit-only families. This study uses independent reversible crossings followed by one common existential quantifier on an arbitrary correlated table.
- `RULER-20261111-001` studied The endless six-regular weave under the not-all-equal knot. This study uses independent reversible crossings followed by one common existential quantifier on an arbitrary correlated table.
- `WITNESS-COUNT-20261112-001` studied Least all-equal call counts at dead depths of genuine limit-only nested not-all-equal families. This study uses independent reversible crossings followed by one common existential quantifier on an arbitrary correlated table.
- `ODD-FAMILY-20261112-001` studied The odd harmony of period 73 made by steps 1, 2, 27 and 54 modulo 73. This study uses independent reversible crossings followed by one common existential quantifier on an arbitrary correlated table.
- `BASES-WITHIN-20261112-001` studied Allowed outer states, state counts and tie classes of levels nested by unlagged stitches. This study uses independent reversible crossings followed by one common existential quantifier on an arbitrary correlated table.

The single-pair predecessor and STRAND-RETURN provide the one-pair baseline. Independent-pair multiplication of answer counts assumes a product input. We change that assumption and allow any subset of the joint state space.

## Prior work outside the program

The log of the number of neighborhood unions of an incidence matrix is the Boolean cut function of Bui-Xuan, Telle and Vatshelle (https://arxiv.org/abs/0903.4796). The representative-set and half-induced matching bounds for tensor powers in Towards Tight Bounds for Graph Homomorphism Parameterized by Cutwidth (https://pure.tudelft.nl/ws/portalfiles/portal/214071710/LIPIcs.ICALP.2024.77.pdf) supply the classical comparison. The object here is specifically the incidence matrix of the measured affine crossing powers; the candidate local result is its exact base and interpretation for future existence tests. The argument is checked directly.

## Evidence and stopping rule

Use the literal three-label crossing to construct the 9 by 9 incidence matrix. Compare the largest private-state certificate at one pair with modular rank and an ordered submatrix. In powers, test the common-state condition on explicit examples and seek matching exponential rates from private tests and small generators. Test a product-input competitor. Stop upon a proved rate or a measured gap; distinguish input length, message bits, and one-query time.
