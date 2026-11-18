# Can bond distances tell which joins come next?

Owner-selected direction 1, 17 November 2026. This ticket tests the pure parity assembly of [the cubic growth study](../CUBIC-FROM-A-KNOT-20261117-001/cubic_growth.md). The nonlinear attachment of the original eight is a different question.

## Question and comparison

Give the reader the scalar bond distance for every pair of present distinctions in an arbitrary naming. It receives no junction list, state table, coordinates, loose-bit labels or history. The input includes the distinctions on the open boundary. The growth law is supplied. Recover the exact junction supports on those same distinctions, the loose bits, the legal serial joins and the full simultaneous prescription, including a possible shortage of loose bits. A simultaneous prescription specifies parent groups and all injections of distinct loose bits to their uses. A collision must use one bijection preserving the entire distance table but failing to carry the legal joins to the other pattern. A match of distance histograms or of output sizes does not establish one.

Rearrangements are legal finite prefixes of the serial parity rule. A move adds one junction with one loose bit from each of one, two or three distinct parents and three fresh bits. Each pair of parents must have an ordinary common neighbor. A triple must have no one neighbor common to all three. The outside used for checking parity is never a parent or a common neighbor in the growth rule. The complete rounds are the predecessor's simultaneous policy, including its choice among interchangeable loose bits.

## First check and proof obligations

First compare genuinely different presentations with equally many junctions. Enumerate the small legal shapes through seven junctions when feasible, keeping how many loose bits each has. Compute scalar tables from all combinations of the parity equations and support minimality. Rename the distinctions before reading each table. Score exact supports, loose bits and both the serial and the simultaneous rule, including blocked transitions; use at least two name permutations. The coordinate-free comparison on arrangements of four must include a chain, three children of the seed, and a rearrangement in which the seed neighbors a junction on five bits. Include a direct check against binary allowed states in the four-junction cases. Keep single-size collision searches distinct from a theorem about all sizes.

The earlier decision check already recovered the first two nontrivial complete rounds. Its reader knew the smallest stars and removed spurious pairs at the last distance threshold. Here the planned reader considers successively the cut sizes three through six. A candidate proof from the design stage uses the last three members of any selected set of junctions to bound the size of a sum of three or more equations. The ordinary meeting graph looks bipartite. If this helps to rule out short sums, it remains to distinguish genuine junctions from sums of two neighboring equations, including a three-bit junction next to a five-bit one. Distances at most a threshold suffice for the proposed test. Equal-distance cliques and naive closeness are controls. Test the finite rearrangements before deciding the theorem or counterexample.

The advisor highlighted the outside vertex, the difference between a whole bond and a scalar minimum, shadowing of individual pair distances, exact allocation symmetries and proper inclusion-minimality. All are tested by the proof or finite controls. The outside has no parity rule of its own. A three-junction sum of size six was an advisor challenge; bipartiteness is the proposed discriminator. We disclose the proof idea and earlier pilot before collecting the new census, so this is a proof with verification.

## Prior work in the program

`python3 -B scripts/track.py objects "bond distance meeting pattern" --until 2026-11-18 --exclude BOND-NEXT-JOIN-20261117-001 --limit 3`

`python3 -B scripts/track.py objects "recover junctions minimal cuts" --until 2026-11-18 --exclude BOND-NEXT-JOIN-20261117-001 --limit 3`

`python3 -B scripts/track.py objects "pure parity cubic growth" --until 2026-11-18 --exclude BOND-NEXT-JOIN-20261117-001 --limit 3`

- `CUBIC-FROM-A-KNOT-20261117-001` gives the source construction and independent referee. `DISTANCE-INFO-20261117-001` exhibits a bond-table collision for other truth tables. `KNOT-SPACE-20261020-001` uses full parity states for a different recovery question.
- `OVERLAP-READ-20261111-001` reads a different knot law on overlapping bases. `CARRIER-20261117-001` and `LEVEL-REACH-20261114-001` concern reach in addressed families.
- `GUARD-CHOICE-SEPARATION-20261115-001`, `TWO-CHOICE-IMPLICATIONS-20261115-001` and `ONE-RELAY-PADDING-20261115-001` concern cuts or relays in a different family.
- `QUADRATIC-ROUTE-TRANSFER-20261115-001`, `GROUPED-PRODUCT-REPLAY-20261115-001` and `TWO-RELAY-PADDING-20261115-001` use parity or growth for other computations.

## Standard statement and known comparison

The standard object is the pair table of minimum cocircuit cardinalities of a cographic binary matroid. The distinguished graph supports are the ordinary vertex stars, with open edges represented by distinct bits. Whitney's 2-isomorphism theorem concerns the full cycle matroid. This particular reader only has one scalar per pair. The final argument must justify why that weaker input works on this restricted graph family. External novelty is unassessed. [Whitney, 1933](https://doi.org/10.2307/2371127)
