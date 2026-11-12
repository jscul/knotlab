# Counting inside: least bonds across depths, pre-registration

Epic `BOND-DEPTH-20261112-001` (`NEST-COUNT-20261112-001` direction 1; G17, with G1), 2026-11-12, at the owner's go-ahead ("Yes,
let's continue on with that."). Frozen before the registered run. The canonical K1–K3 test is unchanged. Law NAE on three-place
knots; families as in `LIMIT-STATE-20261112-001` (the usual limit).

## The question

Inside a nested pattern, does the reach of the law (the least bond between a top distinction and a distinction s levels down) keep
growing with depth, or level off, and which is typical? `NEST-COUNT-20261112-001` proved that the ends carry only finite-state
information; that does not bound what happens inside (chains with no cycle of knots have bonds of steps apart + 2, which grow).

## In standard terms

The least size of a minimal non-shattered set (the literature's term for a bond) containing a root vertex and a vertex at derivation
depth s, in the satisfying assignments of an infinite iterated hyperedge-replacement NAE instance, restricted to one derivation ray.

## The method (frozen in `census.py`; validated before freezing)

The ray: C_0 = main, C_j the copy made by the definition's first SELF call inside C_{j−1}. Each copy is a block: its three ports, its
own distinctions, its knots, and its other SELF calls (side branches) as the limit relation G on their arguments; the last block's
ray call is G too. A bond W is sought among the ray's own distinctions, containing a port of C_0 and an own distinction of C_s. A DP
over blocks keeps (F, G): the families of reachable interface-state sets over all assignments of W so far, without and with one
member forgotten; W is constrained iff some assignment reaches nothing, minimal iff no one-forgotten assignment does. The cost |W| is
minimised level by level; the middle blocks are one map, so L(s) is eventually linear plus periodic, detected exactly when the
normalised cost vector over states repeats (to s = 30).

**Validation (before freezing; `validation.json`).** 40 random one-definition genuine families at s = 1, 2, 3 against exhaustive
search over the ray's distinctions (sets up to seven): 120 of 120 agree; two chains with no cycle of knots give 4, 5, 6, … = steps
apart + 2 (the proved RANDOM-FATES-B result) to s = 6.

## Settled by construction (stated, not tested)

- **Ray bonds are true bonds**, so L_ray ≥ L: "bounded" transfers to the true least bond, "growing" holds for ray bonds only (side
  branches could shortcut).
- **No class in between.** For one definition the middle blocks are identical, so L_ray(s) is a fixed-length shortest path in a
  finite weighted graph: eventually linear plus periodic, with rate the minimum cycle mean (the advisor's). Bounded against growing is
  therefore decided per family, and logarithmic or other growth cannot occur.
- **Endpoints.** The minimum over the three top ports and all own distinctions of C_s is read; other endpoints are not.

## Classes and predictions (frozen)

Per family: **bounded** (repeat found, gain 0), **growing** (repeat found, gain > 0: rate gain/period), **no ray bond** (none at any
s read), **undetermined within 30** (no repeat by s = 30, or more than 20,000 states).

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate: the validation above (done). | — |
| P1 | **Reach is typically bounded.** At least half of the 664 families have bounded least ray bonds. | below half |
| — | Reported: the growth rates, transient lengths, bounded limits, undetermined and capped counts. | — |

## Prior work

Bonds are the minimal non-faces of the shattering complex of the solution set (Sauer–Shelah; Pajor), and minimal supports of
implicates; on bounded treewidth the question is MSO (Courcelle; Arnborg, Lagergren and Seese), and the subset construction is the
usual ∃∀ blow-up (2-QBF on bounded treewidth: Chen; Pan and Vardi). The DP generalises `RANDOM-FATES-20261112-001C`'s exact
bandwidth-3 bond DP. Not found: the growth of least bonds with depth in nested NAE patterns.

## Stop rule and runtime

One run on 8 workers (expected minutes), its summary, a hand-off to the referee thread, report. The full census of the 223,261
families is not run; it is proposed afterwards with grades.
