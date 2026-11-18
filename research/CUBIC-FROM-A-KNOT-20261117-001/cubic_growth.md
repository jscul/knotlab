# Growing a three-dimensional meeting pattern from one knot

**A permitted continuation of the original eight-distinction cube has three directions that keep extending.** It grows through blocks of 27 and 64 positions and continues indefinitely. Around every original or new distinction, the number within bond distance \(r\) lies between fixed positive multiples of \(r^3\) for all sufficiently large \(r\). The proof applies at the boundary as well as in the interior. Every bit can change by a finite modification at every allowed state. [Local construction and proof](../../proofs/CUBIC-FROM-A-KNOT-20261117-001/CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth/proof.md)

## What made three directions possible

A loose distinction belongs to just one current parity knot. A new knot joins loose distinctions from up to three nearby knots and adds three fresh ones. The local parity rule requires an even number of its values to be one. In one parallel application, parents sharing neighbors make groups of three or two, and the remaining loose distinctions extend singly. Which groups are available can be read from the current meeting pattern. The resulting pattern has exactly the incidence of the nonnegative integer triples. Coordinates are used to prove this and check the output.

For the original six-state betweenness seed, five conservative additions first give the familiar eight positions. A fixed finite attachment aligns those positions with the new junctions. One of the original three cut directions is chosen, and each original distinction becomes an actual bit in a junction at its old position. After the finite alignment, the unbounded continuation can proceed in rounds using only the current incidence. The original cube keeps precisely its eight allowed rows. Each parity junction still admits every even assignment of its own bits. [Exact eight-distinction construction](../../proofs/CUBIC-FROM-A-KNOT-20261117-001/CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth/cube_interface.md)

| Open block | Position bits, including the original eight | Shared parity bits | Loose parity bits | Original joint states after extension |
| --- | ---: | ---: | ---: | ---: |
| Three positions each way | 27 | 54 | 27 | 8 |
| Four positions each way | 64 | 144 | 48 | 8 |

There is one observed position bit per junction, drawn from the full collection of shared and loose bits. Keeping the boundary bits lets every old allowed row extend. A separate replay of the anonymous parallel growth reached 220 junctions. The table gives exact finite checks. The cubic exponent comes from a proof for arbitrarily large radii. [Finite checks](../../proofs/CUBIC-FROM-A-KNOT-20261117-001/CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth/result.json)

## What the ruler reads

Bond distance between two distinctions is the smallest number of distinctions in a knot containing both, minus one. Each member of a bond enlarges its possible span by at most a fixed number of positions. From any starting distinction, there is also a growing set of positions reachable by knots whose sizes grow at most linearly with the step count. Counting the positions allowed by those two bounds gives cubic growth. The argument survives the restriction to the eight original states, even for balls centered on an original distinction. [All-radius bounds](../../proofs/CUBIC-FROM-A-KNOT-20261117-001/CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth/cube_interface.md#3-the-ruler-survives-the-finite-restriction)

The other distinctions at each junction matter. If we keep only one position bit per junction, every assignment to the new position bits is compatible with every original row. Three-dimensional growth is visible in how all the distinctions constrain one another.

Continuing the original cut cube using only its betweennesses also reaches the larger boxes. In that construction, its count of state disagreements reads the coordinate separations. Every distinct pair belongs to a three-place knot, so its bond distance stays two, even across a large box. The parity junctions give the positive construction its different ruler.

## Scope and reproduction

This is an existence result for a designed local law with three fresh bits per junction. Growing the parity branch from a ternary parity seed uses no initial alignment. Keeping the earlier betweenness cube uses the bounded attachment and a choice of value conventions. The local rule sees how the designated knots meet. The volume is measured from the resulting allowed states. The asynchronous moves also admit a tree, for instance by attaching a new knot separately to every loose end at every level. Simultaneous evaluation is explicitly supplied when using the parallel policy. This result establishes cubic growth on a discrete space extending outward from a corner. Recognizing a three-dimensional manifold from allowed states remains a separate open question. A separate reader within this task reviewed the proof.

From the repository root, the following commands reproduce the finite evidence. The files contain their own controls. [Proof design](preregistration.md)

~~~bash
k=CUBIC-FROM-A-KNOT-20261117-001
p="proofs/$k/$k-P001_local_growth"
python3 -B "$p/check.py"
python3 -B "$p/cut_control.py" --json
python3 -B "$p/path_check.py"
~~~
