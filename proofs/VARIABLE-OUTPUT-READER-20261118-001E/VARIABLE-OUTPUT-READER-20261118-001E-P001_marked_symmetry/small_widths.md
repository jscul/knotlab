# A counterexample needs at least 21 distinctions

**Statement.** Under the serial two-or-three-fresh parity rule, every full bond-distance isometry between reachable presentations of width at most 20 carries the actual legal triples to legal triples. Thus a counterexample, if one exists, needs at least 21 distinctions. Widths 18, 19 and 20 are covered by the existing exact comparisons. The argument below covers the other smaller widths. [Width 18](../../VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/proof.md) · [Width 19](../../VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/proof.md) · [Width 20](../../VARIABLE-OUTPUT-READER-20261118-001C/VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/proof.md)

## The first possible legal triples

Take three distinct holders of the proposed loose distinctions. In the classical meeting graph, a vertex represents a junction and an edge represents one shared distinction. The graph is simple and bipartite. The three holders lie on the same side, and each pair needs a different ordinary witness. An ordinary witness shared by all three would forbid the move. These six junctions therefore induce exactly a six-cycle.

Six junctions cannot realize this configuration. The last of the six would need to join its two earlier neighbors, which have no other common neighbor in that six-cycle. At least seven junctions are needed. The seed has three distinctions and each addition supplies at least two, so the first possible live triple is at width 15.

With exactly seven junctions the configuration has one further junction. The latest junction of the six-cycle needs it as an earlier common witness of its two neighbors. If the extra junction met only those two, substituting it for the latest junction would leave a bare six-cycle as the actual earlier prefix, which is impossible by the same argument. The extra junction must meet all three junctions on the opposite side of the six-cycle. It must be on the holders' side, because otherwise it is common to all three holders.

Thus the three holders are exactly the three junctions of ordinary degree two. They have at least one loose distinction each because their junction supports have size at least three. Every choice of one loose distinction from each is eligible. The other side's triple has the extra junction as common witness, and any triple containing the extra junction and two of the holders has the pair's original common witness. This seven-junction form is reachable at width 15. Add three children of the seed, then one junction for each pair of those children, using two fresh distinctions each time.

## Complete comparisons at widths 15–17

For \(j\) current junctions, the width \(w\) satisfies \(2(j-1)\le w-3\le3(j-1)\). These are the resulting depths and exact counts.

| Width | Junctions | Presentations | Presentations with a legal triple | Legal triples |
|---:|---:|---:|---:|---:|
| 15 | 5 | 21 | 0 | 0 |
| 15 | 6 | 201 | 0 | 0 |
| 15 | 7 | 80 | 6 | 22 |
| 16 | 6 | 258 | 0 | 0 |
| 16 | 7 | 403 | 23 | 95 |
| 17 | 6 | 212 | 0 | 0 |
| 17 | 7 | 1,007 | 48 | 244 |
| 17 | 8 | 298 | 23 | 52 |

Forward growth and a separate reverse-removal calculation agreed on all rows. The reverse calculation lists connected bipartite meeting graphs and compatible loose counts, then checks whether successive legal last-junction removals reach the seed. Each meeting graph with its loose counts fixes the parity incidence and current permission sets up to names, independently of which legal history led there. The forward calculation also compared the two existing implementations of the full table and the actual marked input menu on every presentation. [Forward growth](../../VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/check_width.py) · [Reverse-removal helpers](../../VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/check_reference.py)

All 302, 661 and 1,517 presentations at the respective widths have different exact full-table classes, including comparisons across junction counts. Within those classes the 6, 23 and 72 legal marked-triple orbits are complete. The orbit check compares the actual number of legal triples in each marked orbit with its exact size from the automorphism group and the marked stabilizer. A complete orbit cannot send an eligible triple to a forbidden one. The same exact canonical table comparison includes empty menus and differently named histories. [Exact marked-orbit checker](../../VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen/check_reverse.py)

## Replay

From the repository root, run the following with the workspace Python. It performs the full forward comparison against the saved counts and exact marked orbit criterion.

```sh
a=proofs/VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen
b=proofs/VARIABLE-OUTPUT-READER-20261118-001B/VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen
PYTHONPATH="$a:$b" .venv/bin/python -B - <<'PY'
from collections import Counter, defaultdict
from itertools import combinations

import check_width as growth
import check_reverse as exact

expected = {
    15: ({5: (21, 0, 0), 6: (201, 0, 0), 7: (80, 6, 22)}, 302, 6),
    16: ({6: (258, 0, 0), 7: (403, 23, 95)}, 661, 23),
    17: ({6: (212, 0, 0), 7: (1007, 48, 244), 8: (298, 23, 52)}, 1517, 72),
}
scout, _, rules = growth.inherited()
for width, target in expected.items():
    growth.WIDTH = exact.WIDTH = exact.INFINITY = width
    exact.PAIRS = tuple(combinations(range(width), 2))
    growth.MAX_JUNCTIONS = 1 + (width - 3) // 2
    growth.generate_width_fixtures.cache_clear()
    classes = {}
    counts = defaultdict(Counter)
    orbits = 0
    for fixture in growth.width_fixtures():
        checks = fixture.checks()
        menu = {tuple(sorted(use)) for use in scout.actual_menu(rules, checks) if len(use) == 3}
        assert menu == exact.triple_menu(tuple(checks.values()))
        counts[len(checks)].update(types=1, live=bool(menu), moves=len(menu))
        scalar = scout.full_table(scout.parity_span(checks), width)
        table, _, _ = exact.bond_table(tuple(checks.values()))
        for a, b in exact.PAIRS:
            observed = width if scalar[a, b] is None else scalar[a, b]
            assert observed == table[a][b]
        twins = exact.interchangeable(table)
        key, group, _ = exact.canonical(table, twins)
        marks, partial = exact.marked_orbits(table, twins, menu, group)
        assert not partial
        orbits += len(marks)
        if key in classes:
            assert classes[key] == marks.keys()
        else:
            classes[key] = marks.keys()
    tally = {j: tuple(record[k] for k in ("types", "live", "moves"))
             for j, record in counts.items()}
    assert (tally, len(classes), orbits) == target
    print(width, sorted(tally.items()), len(classes), orbits)
PY
```
