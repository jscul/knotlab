# Exact bond-distance minima between the two attached rings

## Adaptive calculation and resource bounds

Use the frozen literal T4 and T8 stages in the existing export. The three readings are the minimum across all original exclusive distinctions, the minimum across original exclusive shared distinctions, and the distance of the two fixed original \(c_1\)–\(c_2\) distinctions. Exclusivity uses the original holders. The bond calculation uses the holders in the specified full stage, including the descendants that acquire original loose distinctions.

Attempt ages zero through two and proceed to later exported ages while a tested min-fill ordering has width at most twelve. Keep the auxiliary exterior last. At each width test, break min-fill ties by degree and then by each of the two orders of literal names, taking the smaller resulting width. The calculation stops at 20 million candidate state joins or forgetting steps, 80,000 states in one separator-color bucket, one million retained table states or 60 seconds for an attempted case and age. A stopped row is censored. Check small exhaustive cases and compare the age-zero results with the already completed pinned-cut measurements. These are additional exact readings on the frozen distinctions.

## Exact results

| Start | Age | Decomposition width | Any original exclusive pair | Originally shared exclusive pair | Fixed \(c_1\)–\(c_2\) pair |
|---|---:|---:|---:|---:|---:|
| T4 | 0 | 3 | 31 | 31 | 31 |
| T4 | 1 | 5 | 19 | 27 | 27 |
| T4 | 2 | 10 | 19 | 27 | 27 |
| T8 | 0 | 3 | 39 | 39 | 39 |
| T8 | 1 | 5 | 27 | 35 | 35 |
| T8 | 2 | 10 | 27 | 35 | 35 |

The originally shared exclusive sets are \(\{17,18,19\}\) and \(\{22,23,24\}\). The fixed pair is \(17,22\). Each all-exclusive set has 16 original distinctions, including its 13 original loose distinctions. At ages one and two the winning all-exclusive witnesses meet the two mark sets at original loose distinctions 73 and 85. The corresponding winning originally shared witnesses contain the fixed pair. Allowing the original loose distinctions therefore reduces the minimum by eight at ages one and two, on each placement. Across the exact ages, T8's reading exceeds T4's by eight in each tier. [Exact minima and physical witnesses](../../artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/ring_distance_dp.json)

At age three both tested elimination orders reached width at least 13 on both cases. This is a statement about the orders used. The solver checked that the age-two complete cuts still attain the same costs with both shores connected at age three. Those are upper bounds, and the age-three minima and the later ages remain unmeasured here.

## Why the calculation is exact

Wiring all loose distinctions to the auxiliary exterior represents the homogeneous parity equations by junction incidence. The support of a sum of the equations is a cut. A nonempty cut is inclusion minimal exactly when each shore is connected. Each literal distinction contributes one to the cut size, including each distinction in a parallel bundle. The objective is the smallest such cut size with the required two crossings, less one.

The elimination bags form a tree by attaching each bag to the bag of its earliest still present neighbour. For each assignment of the two colors on a separator the table records the connectivity partition induced by the processed part, which colors have already closed a component, and which mark sets have been hit. A component that loses its last separator member can no longer connect to later junctions, so that color can never open or close a second component. The exterior has a fixed color. At the root each color must have closed exactly one component. Each literal distinction is charged at its earlier endpoint. Keeping the cheapest realization for each boundary state preserves the minimum and stores one physical shore to replay.

Two exact reductions keep the width-ten calculations inside the resource limits. For the first, encode a partition by the binary vector of all internal bipartitions of its separator colors that split none of its components, with one anchor fixed for each present color. The dot product modulo two of vectors for a present and a future partition is one exactly when their joined partition connects each present color. Indeed a color with \(k\) joined components gives \(2^{k-1}\) compatible bipartitions. Within a fixed color and mark bucket, process states in order of cost and retain a basis of these vectors. Any discarded vector is a sum of lower-cost or equal-cost vectors, so any future partition it can complete is also completed by a retained vector of no greater cost. Sealed colors and marks are kept in separate basis groups.

For the second reduction, the previous age's literal winning shore, with all added junctions put on the exterior side, is checked directly as a feasible current shore for each query. This supplies a current upper bound. A separate min-sum pass on the same tree gives exact relaxed crossing costs inside and outside every bag, dropping connectivity and mark requirements. If charges already made plus the relaxed charges still owed exceed the largest of the three known upper bounds, the partial state can be dropped. Every query still has an available optimum within this ceiling. The initial unpruned attempt exceeded the work limit at age two in both cases, and rank reduction alone also reached that limit. The final calculation used 191,971 and 785,401 transitions at age two on T4 and T8, respectively.

The direct controls enumerate all cuts on 48 small multigraphs, with and without the cost reduction. A disconnected-shore control has two marked leaf distinctions whose joint crossing is possible only by leaving a shore disconnected. The solver returns infinity. A three-distinction parallel bundle gives distance two and counts each member separately. Independent connected-shore enumeration on the literal sources checked 6,133 shores on T4 and 3,973 on T8, agreeing with all three reported minima and with the pinned source readings. The retained winning shores are verified against each literal full stage. The complete final calculation took about 1.4 seconds on the workspace host. [Checker](../../experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/world_ring_distance_dp.py) · [Pinned-cut measurements](../../artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/bond_first.json)
