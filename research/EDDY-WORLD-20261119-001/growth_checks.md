# Literal growth and source checks

All ten frozen starts pass the projected K1–K3 test, and all 160 completed stages match an independent count of connected clusters on their unrolled maps. The larger joined junctions reach eight places, but satisfy every hypothesis of the identification used here. The cut control C1 preserves each source junction's loose count from J1. Its map has three endless chains in one piece and two in the other, so its cumulative growth has dimension three. [Frozen starts](../../experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/inputs.json) · [Literal stages](../../artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/stages.json)

## Source qualification

For a source junction, remove it from the holder graph with every loose distinction wired to one auxiliary exterior. Each remaining connected component receives a subset of the observed junction's distinctions. The projected even-parity relation has one equation per nonempty subset. Necessity follows by summing the parity equations in that component. Sufficiency follows by pairing the set distinctions within each component and joining each pair along a path. In every frozen source each observed junction has one such subset, consisting of its entire support. Its full projection is one even-parity relation, all its proper projections are free, and its zero assignment is allowed. The exporter uses knotlab directly for these finite projections through seven places and the same exact component formula at eight.

The physical source is connected, each distinction has one or two holders, and each case has at least two loose distinctions. The actual group enumeration verifies funding, absence of initial groups of three or more, and at most one common holder for every pair of live junctions. These are the DOUBLE-IDENT hypotheses. The source rank reported below is the cycle rank of the incidence graph on the live junctions and their maximal blocks. The endless chains are the ones added under the floor to source leftovers. Every map piece has a cycle or an endless chain, so there is no finite piece requiring a relay. [DOUBLE-IDENT](../DOUBLE-IDENT-20261119-001/line_summary.md) · [The floor and chains](../CHAIN-IDENT-20261119-001/chain_ident.md)

| Start | Map-piece cycle ranks | Endless chains by piece | Growth read from the map |
|---|---:|---:|---|
| B | 0, 0 | 2, 2 | \(17+2t\) births at age \(t\), cumulative dimension two |
| R0 | 1 | 0 | Five births per age |
| R1 | 1 | 0 | Exponential, rate 1.1347241384 |
| R2 | 1 | 0 | Exponential, rate 1.2627754530 |
| J0 | 1 | 4 | Exponential, rate 1.8566748839 |
| J1 | 1 | 4 | Exponential, rate 1.9401082222 |
| J2 | 1 | 4 | Exponential, rate 2.0246491243 |
| T4, T8 | 3 | 4 | Exponential |
| C1 | 0, 0 | 3, 2 | Polynomial, cumulative dimension three |

Each of the two pieces in B is a path extended indefinitely at both ends, giving its source length plus \(t\) intervals of size \(t+1\). In each Jk, deleting the off-cycle parts of the incidence map leaves a cycle with five source junctions. Its off-cycle parts are four paths ending at \(b_0,b_1,b_{15},b_{16}\), each extended by exactly one endless chain. Two attach at the seam junction and two at its block. Once a cluster traverses the whole cycle, each of these four attachments permits any prefix length independently, giving a factor \(1/(1-z)\) for each. The \(k\) leftovers on the cycle each give \(1+z\). The lap weight is therefore \(z^5(1+z)^k/(1-z)^4\). Successive full traversals sum geometrically, with the rate given by the reciprocal positive root of lap weight one. The corresponding Rk lap weight is \(z^5(1+z)^k\). These rates follow from the verified map shapes. The empirical count prefixes below provide a separate check of the growth. [Lap weights of isolated rings](../RING-CORES-20261119-001/ring_cores.md)

The T4 and T8 maps have branching in the part that remains after pruning the finite attachments and chains. Their finite incidence cores each have rank three. In a connected core of minimum degree two and rank greater than one, every sufficiently long nonbacktracking walk visits a junction or block of degree at least three. A longer stretch through degree-two members alone would go around a separate cycle in that connected core. Thus there are at least two choices within each bounded number of steps. Their lifts give exponentially many rooted path clusters in the unrolled map, even after dividing by the number of possible roots of each finite cluster. The finite maximum degree also bounds the number of connected clusters of each size exponentially from above. This uses the map shape directly at the joined junctions' actual arities.

The C1 replay also checks that its meetings differ from J1 only by deletion of \(c_2\)–\(c_3\). The loose counts match exactly and the demands change at the cut. The verified three-chain piece ends at \(b_0,b_{16},c_3\). The other piece ends at \(b_1,b_{15}\). The extra chain is a consequence of the floor at \(c_3\). C1 therefore controls removal of the ring return at equal physical openings, with the indicated change in cumulative growth dimension.

## Complete recorded stages

| Start | Last complete age | Accumulated junctions | Accumulated distinctions | First omitted age | Prospective junctions | Prospective distinctions |
|---|---:|---:|---:|---:|---:|---:|
| B | 32 | 1,617 | 3,250 | — | — | — |
| R0 | 32 | 165 | 335 | — | — | — |
| R1 | 29 | 1,720 | 7,510 | 30 | 1,960 | 8,742 |
| R2 | 17 | 1,378 | 6,739 | 18 | 1,744 | 8,841 |
| J0 | 7 | 1,394 | 7,609 | 8 | 2,522 | 15,029 |
| J1 | 6 | 953 | 5,184 | 7 | 1,784 | 10,767 |
| J2 | 6 | 1,147 | 6,787 | 7 | 2,254 | 14,865 |
| T4 | 5 | 1,025 | 5,926 | 6 | 2,146 | 13,960 |
| T8 | 5 | 912 | 4,814 | 6 | 1,773 | 10,350 |
| C1 | 11 | 2,038 | 7,593 | 12 | 2,517 | 9,436 |

The limits are 2,048 junctions and 8,192 distinctions. The raw stage export records the first triggered limit. The verifier computes the complete forecast for that first omitted age from its parent groups and their lookahead demand. The forecast makes no physical birth. The last measured cluster size in each case is one more than its last complete age. Each exported stage preserves the permanent IDs of the accumulated junctions and distinctions, the complete growing end, and the parent and consumed-distinction lists for the new junctions. The initial roles and source-junction ancestry are evaluator metadata. The physical joining law uses live incidences and funded counts.

## Replay and independent count

The exporter uses FIRST-KNOT's parity presentation and JOIN-GROWTH's complete group enumeration. For each step it checks the full parent list, the identity and one-time consumption of each formerly loose distinction, the fresh count from the next group demand, and the equation rank change. A positive fresh count makes the new parity satisfiable for any earlier allowed state. A zero fresh count requires an already implied equation, verified by GF(2) elimination. These checks ensure conservative growth throughout the recorded prefix. [Exporter and verifier](../../experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/world_growth.py)

The independent count uses only the initial block and loose-count data. In the unrolled map, each selected source-type point can independently include a connected prefix of each attached branch. Start with one size unit and one source-type point. When an incidence branch is available, multiply by one plus its recursively counted nonempty choices. A leftover contributes its first point with independent prefixes of its zero, one or two floor chains. Truncate by the observed size, and keep a second index counting how many source-type points were selected. Sum the rooted counts over source types and divide each term by its number of possible roots. This recovers all 160 sizes exactly, with whole prefix counts in each case.

Run `python3 -B experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/world_growth.py --verify` to reproduce the literal export in memory, compare it with the saved stage object, and print this independent count with the omitted-age forecasts. Small development controls covered implied closure, a proper constrained source projection, an unfunded first stage, a parallel meeting, and exclusion before either resource limit.
