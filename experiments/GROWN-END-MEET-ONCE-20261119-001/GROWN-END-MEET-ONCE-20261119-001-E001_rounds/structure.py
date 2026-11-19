"""Replay the bounded-arity nine-site source and count pointwise symmetries."""

from collections import Counter
from itertools import combinations, permutations
import json
from pathlib import Path
import sys

FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
OUTPUT = ROOT / "artifacts" / FAMILY.parent.name / FAMILY.name / "structure.json"
PREVIOUS = "GROWN-END-SWAP-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / PREVIOUS / (PREVIOUS + "-E001_reached")))
import verify

LAW_ID = "EXTEND-ROUND-20261119-001A"
sys.path.insert(0, str(ROOT / "experiments" / LAW_ID / (LAW_ID + "-E001_extend")))
import extend

sys.path.insert(0, str(ROOT / "tools"))
from knotlab.knots import check_knot
from knotlab.relations import Relation

START = [
    [0, 2, 5, 6], [1, 3, 16, 17], [0, 1, 4], [2, 3, 4],
    [5, 7, 8], [6, 9, 10], [7, 9, 12, 13], [8, 11, 14], [10, 11, 15],
]
FIRST = [[12, 14, 18], [13, 15, 19], [16, 20, 21], [17, 22, 23]]
SECOND = [[18, 19, 24], [20, 22, 25, 26], [21, 27, 28], [23, 29, 30]]


def rank(rows):
    pivots = {}
    for row in rows:
        while row and row.bit_length() in pivots:
            row ^= pivots[row.bit_length()]
        if row:
            pivots[row.bit_length()] = row
    return len(pivots)


def start_projections():
    masks = [sum(1 << bit for bit in row) for row in START]
    width = max(max(row) for row in START) + 1
    states = [state for state in range(1 << width)
              if all((state & mask).bit_count() % 2 == 0 for mask in masks)]
    counts = []
    for row in START:
        names = tuple(str(bit) for bit in row)
        projected = frozenset(tuple(bool(state & (1 << bit)) for bit in row) for state in states)
        assert len(projected) == 1 << (len(row) - 1)
        assert check_knot(Relation(names, projected), names[:-1], names[-1]).is_knot
        counts.append(len(projected))
    return counts


def table_and_bonds(rows):
    masks = [sum(1 << x for x in row) for row in rows]
    dimension = rank(masks)
    assert dimension == len(rows)
    words = [0]
    for row in masks:
        words.extend([word ^ row for word in words])
    # The equations supported on the candidate have dimension exactly one
    # precisely when that word is support-minimal.
    bonds = [word for word in words[1:] if rank(row & ~word for row in masks) == dimension - 1]
    n = max(max(row) for row in rows) + 1
    table = [[0] * n for _ in range(n)]
    for word in sorted(bonds, key=int.bit_count, reverse=True):
        bits = [j for j in range(n) if (word >> j) & 1]
        for x, y in combinations(bits, 2):
            table[x][y] = table[y][x] = len(bits) - 1
    assert all(table[x][y] > 0 for x, y in combinations(range(n), 2))
    return table, bonds


def automorphisms(table, old, fixed):
    n = len(table)
    colors = [j + 2 if j in fixed else int(j >= old) for j in range(n)]
    while True:
        keys = [(colors[j], tuple(sorted(Counter(zip(colors, table[j])).items()))) for j in range(n)]
        distinct = {value: number for number, value in enumerate(dict.fromkeys(keys))}
        refined = [distinct[value] for value in keys]
        if len(set(refined)) == len(set(colors)):
            break
        colors = refined
    domains = [{k for k in range(n) if refined[k] == refined[j]} for j in range(n)]
    image = {}
    unused = set(range(n))

    def walk():
        if len(image) == n:
            yield tuple(image[j] for j in range(n))
            return
        sizes = []
        for j in range(n):
            if j in image:
                continue
            eligible = [k for k in domains[j] & unused
                        if all(table[j][a] == table[k][b] for a, b in image.items())]
            sizes.append((len(eligible), j, eligible))
        _, j, eligible = min(sizes)
        for k in eligible:
            image[j] = k
            unused.remove(k)
            yield from walk()
            unused.add(k)
            del image[j]

    return set(walk())


def padded_control(count):
    rows = [set(row) for row in START]
    # Subdivide the A-to-most-recent junction distinction. The third holder
    # starts at V, then U, then the successively inserted junctions.
    previous = 4
    third_sites = [5, 4]
    next_bit = 18
    for k in range(count):
        rows[previous].remove(5)
        rows[previous].add(next_bit)
        rows[third_sites[k]].add(next_bit + 1)
        previous = len(rows)
        third_sites.append(previous)
        rows.append({5, next_bit, next_bit + 1})
        next_bit += 2
    start = verify.Arrangement.parse([sorted(row) for row in rows])
    audit = verify.start_audit(start)
    assert audit["census_open_legal"] and audit["meets_once"]
    assert {len(row) for row in rows} <= {3, 4}
    stage = [frozenset(row) for row in rows]
    for expected in ((1, 1, 2, 2), (1, 2, 2, 2)):
        nxt = extend.grow1(stage)
        old_bits = set().union(*stage)
        assert tuple(len(row - old_bits) for row in nxt[len(stage):]) == expected
        stage = nxt
    return len(rows)


def run():
    literal = [START, START + FIRST, START + FIRST + SECOND]
    stage = [frozenset(row) for row in START]
    for expected in literal[1:]:
        stage = extend.grow1(stage)
        assert list(map(sorted, stage)) == expected
    old = 24
    swap = list(range(old))
    swap[0], swap[1] = 1, 0
    case = {"a": dict(zip(("start", "current", "next"), literal)), "permutation": list(enumerate(swap))}
    replay = verify.check(case, 1 << 18)
    assert replay["reachable_a"] and replay["reading"]["keeps_reading"]
    assert replay["lineage_a"]["start"]["census_open_legal"] and replay["lineage_a"]["start"]["meets_once"]
    seen = []
    for label, rows in zip(("current_a", "next_a"), literal[1:]):
        agg = verify.Arrangement.parse(rows)
        wired, _, metadata = verify.exact_table(agg, 1 << 18)
        t, bonds = table_and_bonds(rows)
        assert all(t[x][y] == value for (x, y), value in wired.items())
        assert len(bonds) == metadata["bonds"]
        seen.append((t, bonds))
    fixed = set().union(*FIRST)
    tables = [data[0] for data in seen]
    groups = [automorphisms(t, old, fixed) for t in tables]
    old_group = groups[0]
    extendible = old_group & {p[:old] for p in groups[1]}
    central = {p + tuple(range(4, old)) for p in permutations(range(4))}
    assert len(old_group & central) == 8 and len(extendible & central) == 4
    assert tuple(swap) in old_group and tuple(swap) not in extendible
    assert all(set(p[:old]) == set(range(old)) for p in groups[1])
    marks = [{0, 2, 4}, {1, 2, 4}]
    triple = []
    for marked in marks:
        mask = sum(1 << x for x in marked)
        triple.append(min((word.bit_count() for word in seen[0][1] if word & mask == mask), default=None))
    assert triple == [None, 5]
    return {
        "start_sites": list("ABCDUVSTW"), "start": START, "first": FIRST, "second": SECOND,
        "simultaneous_start_projection_sizes_passing_knotlab": start_projections(),
        "current_live_distinctions_fixed": sorted(fixed),
        "law_replay_and_wired_minima_agree": True,
        "stage_counts": [{"junctions": len(rows), "pairs": len(t) * (len(t) - 1) // 2,
                          "bonds": len(bonds), "D_0_2": t[0][2], "D_1_2": t[1][2]}
                         for rows, (t, bonds) in zip(literal[1:], seen)],
        "current_pointwise_permutations": len(old_group),
        "current_pointwise_permutations_with_some_extension": len(extendible),
        "next_pointwise_permutations_preserving_old_set": len(groups[1]),
        "central_permutations": len(old_group & central),
        "central_permutations_with_some_extension": len(extendible & central),
        "triple_marks_and_minimum_bond_sizes": [[sorted(m), v] for m, v in zip(marks, triple)],
        "padded_start_sizes_with_legality_and_both_fresh_lists_replayed": [
            padded_control(size) for size in (0, 1, 2, 3, 10)
        ],
    }


if __name__ == "__main__":
    output = json.dumps(run(), indent=2) + "\n"
    if sys.argv[1:] == ["--check"]:
        assert OUTPUT.read_text() == output
    else:
        OUTPUT.write_text(output)
