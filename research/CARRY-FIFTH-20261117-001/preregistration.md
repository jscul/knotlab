# Four distinctions to five

Start with the eight four-bit words with at most one change along a displayed order. Erase the order, the names of the four distinctions and the identities of any constituent knots. The input is the set of allowed states. The fresh distinction is identifiable as fresh. The question is whether that input selects one old distinction to carry forward when adding a single knot.

Test every truth relation on two distinct old distinctions and the new one. Use the canonical K1–K3 test and take its conjunction with the old allowed states. Require all eight old states to survive and compare the entire extension with the set of all five-bit threshold words in a possible reading. First preserve a common meaning for the two values across distinctions. Then allow a separate swap of the two values at each distinction. A successful endpoint extension, a successful insertion into the order and an invariant choice of one old distinction answer different questions. Report them separately.

Compute the old symmetries in both conventions. A proposed individual choice must be fixed by each old symmetry. Repeat with a specified growing end. Compare mirror growth histories that produce the same old states. Include an intersection/union check and a negative control with the same number of five-bit states as a successful extension. A reading cannot pass on its count alone.

This is an exact finite certificate. The initial threshold example and analytic predictions were known before the checker ran. Stop after this finite classification. No sample, timing rule or extrapolation to other substrates enters the conclusion.

## Prior work in the program

- `python3 -B scripts/track.py objects "betweenness disagreement count" --until 2026-11-17 --exclude CARRY-FIFTH-20261117-001 --limit 3`
- `python3 -B scripts/track.py objects "threshold sign vectors reorientation" --until 2026-11-17 --exclude CARRY-FIFTH-20261117-001 --limit 3`
- `python3 -B scripts/track.py objects "threshold line" --until 2026-11-17 --exclude CARRY-FIFTH-20261117-001 --limit 3`

`DISTANCE-ORDER-20261117-001` supplies the threshold-state criterion. `DISTANCE-DIM-20261117-001` shows why reading a pattern's dimensions and constructing them are separate claims. The contemporaneous study `KNOT-ORDER-20261117-001` studies single-knot growth with a common value convention. The present check independently evaluates the four-to-five case and allows independent renaming of each distinction's values.

The searches also returned `TWO-PRODUCT-SKETCHES-20261115-001`, `SWAPPED-ROUTE-GROUPING-20261115-001`, `TWO-RELAY-PADDING-20261115-001` and `SHARED-REPORT-CANCELLATION-20261115-001`. None supplies an input to the certificate.
