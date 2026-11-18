# One construction with cubic growth

Owner-selected proof question, 17 November 2026. The target is one coherent continuation from one ternary knot with arbitrarily large three-direction blocks. Fix bond distance throughout the volume claim. For distinct bits it is the least size of a K1–K3 knot through both, minus one. Evaluate it on the allowed states of the infinite system. Each bit must flip by a finite change at every solution. The finite examples check the growth presentation and its open boundary.

## Supplied rule and tests

The branch state contains the constraints, their local relations and which distinctions they share. One step consumes one loose bit from each of one, two or three distinct constraints, and supplies three new bits and one even-parity constraint on the whole tuple. For several parents each pair must have a common neighboring constraint in the current presentation. For three, no single constraint may neighbor all three. No coordinates, identities used as labels, ages or existing arrangement are inputs to this move. The three fresh bits, the arithmetic of even parity and the incidence tests are features of the chosen law.

Test a parallel policy for this move. On the current loose ends form the admissible groups of three, then the neighboring pairs outside these groups, then singleton groups for the remaining loose bits. All groups are read from one snapshot. Prove that their result up to renaming has the incidence of the nonnegative three-dimensional lattice. A serial branch may be selected for the exact boxes at sides two, three and four. For infinite growth, prove independent lower and upper bounds on bond-ball volume. Count junctions, shared bits, and loose bits separately.

As a matched control start with the actual eight-distinction cube of betweenness cuts. Extend it by its original sorts of moves. Test the count of state disagreements separately from bond distance. As a stronger bridge, retain all eight original distinctions and their full joint relation. Test a finite attachment in which they become the positive edges of one cut direction at the eight corresponding positions of the parity construction. Audit both conservativity and the infinite ruler after this restriction. The alignment of the eight-place interface is an explicit design choice.

Failure conditions include a spurious group on a complete round, loss of an old state, a variable that cannot flip locally, or distant values joined by bounded-size bonds. Compare singleton-only growth, closed boundaries, and the original cut-only box. Full state recovery of the local constraint list and agreement of every asynchronous schedule are separate questions.

This is a proof plan with finite checks. The proposed geometric identification, bounds and an exploratory replay of the cut-only box were already known during design. The saved checks of the local growth and aligned bridge follow preflight. The Fable 5.2 advisor highlighted scheduling as a source. The serial move witnesses existence; simultaneous evaluation is an additional specified policy. Its eligibility tests inspect the current incidence, and the alternatives supply a negative control.

## Prior work in the program

`python3 -B scripts/track.py objects "cubic bond-ball growth" --until 2026-11-18 --exclude CUBIC-FROM-A-KNOT-20261117-001 --limit 3`

`python3 -B scripts/track.py objects "cube of splits" --until 2026-11-18 --exclude CUBIC-FROM-A-KNOT-20261117-001 --limit 3`

- `LOGIC-AXIS-20261107-001` proves cubic volume on a supplied full lattice. `OPEN-END-GROWTH-20261107-001` grows the endless line from a knot and constructs the product of two lines. `FOLD-20261112-001` and `BOND-BALLS-20261111-001` study changes in the ruler on supplied patterns.
- `KNOT-ORDER-20261117-001`, `GRID-GROW-20261117-001`, `STATE-RULES-20261117-001` and `CUBE-DOUBLING-20261118-001` give the cut systems and their finite-growth interface. The cube-doubling proof's referee is pending. Only the eight-place case is used and its states are replayed here. `AFFINE-FACTOR-RANK-20261115-001` concerns restrictions of Boolean computations.

## Additional proof checks after design

The marked-path audit and the test of the marginal retaining one position bit per junction were added during proof review. They check steps of the argument. They were outside the original finite test plan.
