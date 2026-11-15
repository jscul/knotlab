# Choosing how to order two routes within each stage

2026-11-15 (Pacific). Goals G3 and G16.

## The question

Which two-use route layouts acquire a nested reading after branch swaps, what is the minimum number of exceptions across every such order, and does that number force solver work?

## Prior work in the program

`scripts/track.py objects "nested two-use guarded routes" --until 2026-11-15 --exclude SWAPPED-ROUTE-GROUPING-20261115-001 --limit 3`

`scripts/track.py objects "swapping branch order alternating occurrence pairs" --until 2026-11-15 --exclude SWAPPED-ROUTE-GROUPING-20261115-001 --limit 3`

`scripts/track.py objects "minimum exceptional names interval solver" --until 2026-11-15 --exclude SWAPPED-ROUTE-GROUPING-20261115-001 --limit 3`

`scripts/track.py objects "maximum nested matching finite state paths" --until 2026-11-15 --exclude SWAPPED-ROUTE-GROUPING-20261115-001 --limit 3`

- `TWO-RELAY-PADDING-20261115-001` studied NP-completeness with at most two uses in both middle and pad roles, and a complementary sign-parameter solver. This epic searches all within-stage branch orders and minimizes the number of conditioned identities jointly with that choice.
- `ROUTE-FRONTIER-MEMORY-20261115-001` studied Tight deterministic stage-order memory and exact residual count on one fixed guarded route schedule. This epic searches all within-stage branch orders and minimizes the number of conditioned identities jointly with that choice.
- `PERIODIC-READ-20261111-001` studied The two knot classes and the global hollow triples of swapped one-pair weaves. This epic searches all within-stage branch orders and minimizes the number of conditioned identities jointly with that choice.
- `UNSIGNED-ROUTE-JOINS-20261115-001` studied All-input correctness of the original stage scan and linear decision after arbitrary positive middle joins. This epic searches all within-stage branch orders and minimizes the number of conditioned identities jointly with that choice.
- `KNOTS-ALONE-20261111-001` studied Connected two-fold weaves under the not-exactly-one knot. This epic searches all within-stage branch orders and minimizes the number of conditioned identities jointly with that choice.
- `JOINT-BRAID-READS-20261114-001` studied Private single-state tests for simultaneous ternary crossing queries. This epic searches all within-stage branch orders and minimizes the number of conditioned identities jointly with that choice.
- `OVERLAP-READ-20261111-001` studied Finite NAE relations read through pair counts, with books and the Pasch as examples. This epic searches all within-stage branch orders and minimizes the number of conditioned identities jointly with that choice.
- `PROVED-RATE-20261113-001` studied Least ray bonds in one-definition nested families alive only in the limit. This epic searches all within-stage branch orders and minimizes the number of conditioned identities jointly with that choice.

The predecessor proves the fixed-order nested decision and witness algorithm and a search bound for exceptional names. Its guarded stages give exactly two interchangeable whole branches, each with one middle and two pad positions.

## Prior work outside the program

Interval recurrences for keeping many noninterleaving pairs occur in Nussinov et al., Algorithms for Loop Matchings (https://doi.org/10.1137/0135006). Parsing paths through a finite automaton to optimize a nested pairing is also established (https://doi.org/10.1038/s41586-023-06127-z). Both are comparisons. The proofs below derive all bounds directly, using the unique physical mate and its two possible locations.

## Evidence and stopping rule

Check independence of swaps, repeated identities and whole guard-block order. Test zero recognition and exact minimum against independent enumeration of all typed two-stage layouts, then stress larger layouts. Recover concrete orders, exception sets and SAT witnesses and pin them on the original raw clause system. Compare unavoidable alternation on a live easy family with the compiler. Stop once these tests and the bounds are accounted for, or isolate a counterexample.
