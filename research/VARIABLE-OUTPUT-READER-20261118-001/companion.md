# Can bond distances still identify the next joins when the number of fresh distinctions varies?

The dimension study asks how a rule chooses the number of fresh distinctions. This companion asks what the rule can see when that choice is left open. Begin with the same three-place even-parity seed. Keep the existing rule for which parents can join and which loose distinction each can contribute. At every subsequent junction allow either two or three fresh distinctions.

The known inverse recovers all junctions on the actual distinctions, the allowed states and every legal next join under the growth law with exactly three fresh outputs. Its proof uses the three outputs to bound how small a combined parity constraint can be. The metric theorem for general parity bases allows infinite bond distance between disconnected parts. These statements have different hypotheses and conclusions. [Published inverse](../BOND-NEXT-JOIN-20261117-001/next_joins.md) · [Metric theorem](../BOND-METRIC-20261118-001/bond_metric.md)

## Exploratory check

The old reader first fails after three junctions. Give the seed distinctions the names 0, 1 and 2. Add one junction on 0, 3 and 4, and another on 1, 5 and 6. Each triple has even parity. The fixed-three reader adds a spurious junction on 3, 4, 5 and 6. All 16 combinations on those four distinctions occur. Choosing the four values fixes 0 and 1 by the child equations and then 2 by the seed equation. The names are just for verifying the example.

Across all 1,045 reachable arrangements through six junctions, every distance-preserving renaming also preserved the true junctions, the allowed states and the permitted next choices on existing distinctions. The check covered renamings within one arrangement as well as comparisons across arrangements and across different junction counts. It gave the same answer after pooling all bond distances above five. The fixed-three control covered 31 arrangements through five junctions. This is an exploratory finite census assembled to choose the direction. [Pilot](scout.py) · [Results](scout.json)

| Number of junctions | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Distinct arrangements with either output count | 1 | 2 | 5 | 25 | 132 | 880 |

The first untested kind of move has three parents. Such parents need three different witnesses, one common neighbor for each pair, because a neighbor common to all three excludes the move. With just those six junctions the meeting pattern would be a six-junction ring. Its last junction would have had two earlier parents without an earlier common neighbor, so this pattern cannot arise by itself. Seven existing junctions suffice. Give the root three children, then add a junction on each of the three pairs of children. Those last three junctions can supply the eighth.

As a targeted check beyond the census, let the three children introduce 3, 2 and 3 distinctions. Let their three pair joins, in the order first–second, first–third and second–third, introduce 2, 3 and 2. The seven-junction table then admits 12 distinct choices of old operands for a three-parent join. All 48 renamings preserving its full table preserve those choices, as do all 48 preserving its table through five. This checks one arrangement against its own symmetries. Comparisons against other seven-junction arrangements remain open.

## What would settle the direction

Find a rule that returns exactly which existing distinctions may be joined, using only the present bond-distance table, for every finite history under these permissions. Alternatively, exhibit two reachable tables related by a renaming that carries a legal next join to an illegal one. A symmetry of one table that does this also suffices. A failure visible only after pooling distances above five calls for checking the full table.

Compare the first three-parent arrangements against all other reachable tables of the same width. Use the spurious four-distinction junction to characterize the small combined parity constraints that the fixed-three proof excluded. An exact general reader would remove the fixed-three assumption from this part of growth. A collision would identify the particular choice a distance reader cannot distinguish on this family. A rule choosing its own dimension could still admit a narrower family of histories. External novelty has not been assessed.
