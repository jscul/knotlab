# The literal minimum responses at size two

The fourteen fixed stages contain **485 ordinary four-distinction responses** and **650 pairs of responses sharing exactly one distinction**. The smallest nonzero closed change uses four distinctions in each case. With the current loose distinctions free, a pair held by the same junction gives a change of size two. No size-three change occurs in any of the fourteen stages. [Exact catalogue and literal supports](../../artifacts/MOTION-AT-EDDY-20261119-001/MOTION-AT-EDDY-20261119-001-E001_motion/patterns.json)

| Case | Ordinary four-responses | Pairs sharing exactly one distinction | Closed state dimension | Dimension of original-cycle residue |
|---|---:|---:|---:|---:|
| B | 15 | 14 | 15 | 0 |
| J0 | 24 | 39 | 25 | 1 |
| J1 | 24 | 39 | 25 | 1 |
| J2 | 24 | 39 | 25 | 1 |
| T4 | 33 | 64 | 35 | 2 |
| T8 | 33 | 64 | 35 | 2 |
| C1 | 22 | 36 | 22 | 0 |
| R0 | 5 | 5 | 6 | 1 |
| R1 | 5 | 5 | 6 | 1 |
| R2 | 5 | 5 | 6 | 1 |
| B81 | 79 | 78 | 79 | 0 |
| J81 | 88 | 103 | 89 | 1 |
| T81 | 97 | 128 | 99 | 2 |
| R31 | 31 | 31 | 32 | 1 |

## Exact catalogue and rulers

A change is allowed when its support has even incidence at every junction. Wiring current loose distinctions to an exterior for parity calculation makes an allowed support an even subgraph. Every smallest change through a specified distinction is that distinction and a shortest alternate path between its holders in the wired graph. This follows by decomposing an even support into simple circuits and keeping the one through the specified distinction. Shortest-path counts give every tied minimum, and the catalogue of all circuits of length two through four supplies their complete literal supports at these stages. Holding other current loose distinctions fixed deletes those distinctions from the path computation. A current loose target with all other current loose distinctions pinned cannot change, since summing all parity equations gives even total change across the loose distinctions.

Physical reach is measured in co-knotted-pair steps of actual distinctions. The distance traversal uses only common physical holders, even for changes that use loose distinctions. A synthetic control has two loose distinctions meeting only at the auxiliary exterior whose actual distinction-step distance is two. On its marked shared distinction, the free minimum has size three and the pinned minimum has size four. The source-only co-knotted marks are passed to the evaluator separately from the anonymous incidence API. [Anonymous incidence and response helpers](../../experiments/MOTION-AT-EDDY-20261119-001/MOTION-AT-EDDY-20261119-001-E001_motion/motion_stage.py)

All 2,899 distinguished targets were read with both policies. Every originally shared and every consumed original loose distinction has free minimum size four. Every current loose distinction has free minimum size two. In the pinned arm the original distinctions consumed by unary children are fixed. All finite minimum responses in both arms have size at most four, so every tied support is listed. The separate catalogue of physically connected changes through size four consists of 1,407 two-distinction circuits through loose distinctions, 485 ordinary four-circuits, 7,935 four-circuits using loose distinctions, and 249 physically connected unions of two disjoint two-circuits. The latter are composite changes. These counts are sums over the fourteen named starts.

All the ordinary four-circuits have two consecutive original shared distinctions and a common child of their two outer holders. A four-circuit with no children would require an original four-cycle. A four-circuit through two children would require two distinct children of the same two original parents, which the actual complete group law excludes. The remaining case has one child and a two-meeting original path. Conversely every such path produces its binary child, since all original junctions are live, each candidate pair has only one common holder and there is no unheld group of three or more. Neither physical parallel distinctions nor a triangle occurs. Every original loose distinction has been taken, and current loose holders have no shared distinction with each other, so the exterior supplies neither an ordinary-target two-circuit nor a three-circuit. Thus each ordinary four-circuit is minimum for every one of its four distinctions under both loose-value policies. All 485 were recovered both from anonymous incidence and from the original two-meeting paths with their literal consumed distinctions.

Each four-response has two private distinctions supplied to its binary child. Because the children are distinct for distinct responses, a response pair shares precisely the original distinctions shared by its two original paths. The overlap relation was independently graded using every literal pair of responses. Jointly shuffling holder order and changing distinction names preserved every minimum, its tied supports, the co-knotted steps from the evaluator's fixed marks and the entire overlap relation in all cases.

## Closed occupancy and the reference assignment

When current loose values are pinned to zero, both private bits at a binary child agree. A unary child has just one non-loose bit, which is fixed at zero. In any closed allowed state, sum the occupied four-responses to remove all the private bits. The remainder is an allowed change supported entirely on original shared distinctions. The private pairs prove independence of the responses and uniqueness of this decomposition. Thus a closed occupancy has exactly \(2^r\) physical states over it when the original holder arrangement has cycle rank \(r\). In the tree cases the occupancies exhaust the closed state space. In the ring cases an original-cycle change can remain at zero occupancy. GF(2) elimination checked the full closed rank and unrestricted rank in all fourteen stages.

The checker explicitly enumerated all 32,960 closed assignments from B, R0, R1 and R2, and all 32,768 unrestricted assignments of R0. The count of occupied responses from the zero assignment is one way to grade a state. When an allowed value recoding is applied to both the state and its reference, their difference and its occupancy agree before and after. Forgetting the reference admits an allowed value recoding by one four-response that carries a raw occupied state to raw zero. An unmarked occupancy therefore cannot be read invariantly under those recodings.

The code also counts the exact physical weights with up to three occupied responses in each case. For \(k\) occupied slots the weight is \(2k\) from their private bits plus the number of original distinctions used an odd number of times. On a finite path that latter count is twice the number of occupied runs. The three-slot minimum is eight on B and B81. At a junction incident to at least three original meetings, three responses can use each of three original distinctions twice, leaving a six-distinction state. The joined and cut cases attain that smaller weight. These are closed configurations of the code, and the state count alone does not determine their continuation under a local rule.

## Translation and source controls

Along each background path, the successive two-meeting windows give ordered copies of the four-response. Each successive pair shares the intervening original distinction, and its difference is an allowed change of size six. With first and last original path distinctions used by the evaluator, the distance pair of window \(i\) is \((i,L-2-i)\) for a path of \(L\) original meetings. The ring windows close under the same overlap relation. One literal rotation of all holder and distinction names is an exact symmetry on both bare ring controls, including R31. The file records both permutations. These checks establish permitted translations and returns on a fixed stage. A transport rule is a separate test.

The extended cases were made from their frozen source specifications with the same complete-round producer. B81 has the 81-junction path with leftovers at \(b_0,b_1,b_{79},b_{80}\). J81 joins the one-leftover five-ring at \(b_{30}\), and T81 joins a second at \(b_{50}\). R31 has one bare 31-junction ring at four places per junction. All pass the projected source knot test, the initial funding test and the DOUBLE-IDENT conditions. In the simple source holder graph, two common neighbours would give a four-cycle. An unheld triple would give a six-cycle, since its three pair witnesses must differ and a pair witness equal to the third junction would force a triangle. Any larger clique obeys the same condition by the uniqueness of a pair witness. The frozen sources have none of these three short cycles. Their paid loose counts therefore equal the sum of the other-neighbour counts at each holder's neighbours, plus the specified leftovers.

The B81 map has two pieces with two endless chains each, giving the CHAIN-IDENT cumulative dimension two. The odd ring makes the J81 map connected, of cycle rank one with four chains. The second odd ring gives T81 a connected map of rank three. Every piece thus has a cycle or a chain. The identified map applies also at the funded junctions of arity eight. The direct RING-CORES five-place theorem applies to R31 and the isolated rings; the larger joined fates use the identified maps. [Identification with multiplicities](../DOUBLE-IDENT-20261119-001/line_summary.md) · [Rings in the five-place class](../RING-CORES-20261119-001/ring_cores.md) · [Chain dimension](../CHAIN-IDENT-20261119-001/chain_ident.md)

As a separate one-size-past control, the three published J1 states and their two six-distinction differences were replayed at size eight. The one additional complete layer has 1,784 junctions and 10,767 distinctions, within the supplemental limits of 2,048 and 12,000. All older recorded stages reproduce exactly. The three permitted states keep their literal distinctions and the fixed-source-holder readings \((6,8),(7,7),(8,6)\). This is a replay of available states one size beyond the prior seven-size bound. [Published pulse](../EDDY-WORLD-20261119-001/decision.md)

## Reproduction

Run the catalogue from the repository root.

    python3 -B experiments/MOTION-AT-EDDY-20261119-001/MOTION-AT-EDDY-20261119-001-E001_motion/patterns.py

The run permits at most 200,000 literal circuits per cardinality and five million incidence-generated pair comparisons, with explicit all-state enumeration only up to 16 free coordinates after elimination. All named stages completed within the bounds. In 39 small synthetic incidences a direct table of allowed states verified 572 target-policy readings and independently classified all 637 physically connected allowed changes of size at most four. The frozen fourteen-stage run, those controls and the size-eight pulse took about 2.4 seconds on the workspace host. [Catalogue checker](../../experiments/MOTION-AT-EDDY-20261119-001/MOTION-AT-EDDY-20261119-001-E001_motion/patterns.py)
