"""Classify the marked holdings of strict minimum splits without using the study's search."""

import argparse
import json
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations, permutations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRIOR = HERE.parents[1] / "MOST-FAILING-20261127-001/referee-R1/codes.jsonl"


def read_rows(path):
    with path.open() as stream:
        for line in stream:
            yield json.loads(line)


def reader_mark(holders, pair):
    """One strict reader is two unordered distinction holder lists."""
    return tuple(sorted(holders[d] for d in pair))


@cache
def canonical(marked, all_holdings=()):
    """Exact simultaneous relabelling of knots, reader labels and their two settings.

    The optional multiset includes every distinction, even those outside the readers.
    A knot absent from both arguments is deliberately invisible to this comparison.
    """
    incidence = Counter(h for m in marked for setting in m for h in setting)
    full_counts = Counter(h for setting in all_holdings for h in setting)
    blocks = defaultdict(list)
    for h in sorted(incidence.keys() | full_counts.keys()):
        blocks[(incidence[h], full_counts[h])].append(h)
    blocks = [blocks[signature] for signature in sorted(blocks)]
    best = None
    for assignments in product(*(permutations(block) for block in blocks)):
        order = [h for block in assignments for h in block]
        new = {h: i for i, h in enumerate(order)}

        def relabel(setting):
            return tuple(sorted(new[h] for h in setting))

        marks = tuple(sorted(tuple(sorted(relabel(s) for s in mark)) for mark in marked))
        all_values = tuple(sorted(relabel(s) for s in all_holdings))
        key = marks, all_values
        if best is None or key < best:
            best = key
    return best


def make_code(row):
    owners = defaultdict(list)
    for h, knot in enumerate(row["supports"]):
        for d in knot:
            owners[d].append(h)
    owners = {d: tuple(hs) for d, hs in owners.items()}
    assert all(len(hs) == 2 for hs in owners.values())
    holder_pairs = list(combinations(range(len(row["supports"])), 2))
    bits = {key: 1 << i for i, key in enumerate(holder_pairs)}
    odd = 1 << len(bits)
    options = defaultdict(list)
    by_mark = {}
    for i, (u, v) in enumerate(row["pairs"]):
        mark = reader_mark(owners, (u, v))
        (a, b), (c, d) = mark
        assert len({a, b, c, d}) == 4
        cross = [tuple(sorted((h, k))) for h in (a, b) for k in (c, d)]
        col = sum(bits[p] for p in cross)
        alt = a < c < b < d or c < a < d < b
        assert col == sum(1 << j for j, check in enumerate(row["checks"]) if (check >> i) & 1)
        assert alt == bool((row["cost"] >> i) & 1)
        by_mark[mark] = col + odd * alt
        options[mark].append((u, v))
    marks = sorted(options)
    return owners, marks, [by_mark[m] for m in marks], [options[m] for m in marks], odd


def count_lifts(selected, options):
    """Count injective choices of actual distinctions for the chosen holder pairs."""
    candidates = sorted((options[i] for i in selected), key=len)
    masks = [[((1 << a) | (1 << b), (a, b)) for a, b in opts] for opts in candidates]

    @cache
    def count(k, used):
        if k == len(candidates):
            return 1
        return sum(count(k + 1, used | pair) for pair, _ in masks[k] if not used & pair)

    total = count(0, 0)
    example = []
    if total:
        taken = 0
        for k, group in enumerate(masks):
            for mask, pair in group:
                if not taken & mask and count(k + 1, taken | mask):
                    example.append(pair)
                    taken |= mask
                    break
            else:
                raise AssertionError("nonzero completion count requires a choice")
    count.cache_clear()
    return total, example


def all_minima(marks, columns, options, target, maximum):
    """Match two disjoint ordered lists of at most three holder-pair types each.

    At a minimum, two readers cannot have the same unordered pair of holder lists.
    Removing both would preserve every equation, the sign and the other disjoint
    readers. Every feasible minimum therefore occurs among the subsets below.
    """
    @cache
    def half(size):
        table = defaultdict(list)
        for ids in combinations(range(len(columns)), size):
            val = 0
            for i in ids:
                val ^= columns[i]
            table[val].append(ids)
        return table

    for size in range(1, maximum + 1):
        left = half(size // 2)
        right = half(size - size // 2)
        frequencies = Counter()
        examples = {}
        for parity, heads in left.items():
            for tail in right.get(parity ^ target, ()):
                for head in heads:
                    if head and head[-1] >= tail[0]:
                        continue
                    ids = head + tail
                    total, example = count_lifts(ids, options)
                    if total:
                        shape = canonical(tuple(marks[i] for i in ids))
                        frequencies[shape] += total
                        examples.setdefault(shape, example)
        if frequencies:
            half.cache_clear()
            return size, frequencies, examples
    raise AssertionError("The archived witness does not bound a realizable minimum")


def pass_and_double(marked, i, choice):
    """Pass one setting of a reader through a new knot, and double its mate."""
    new_knot = max(h for pair in marked for setting in pair for h in setting) + 1
    split = marked[i][choice]
    doubled = marked[i][1 - choice]
    rest = list(marked[:i] + marked[i + 1 :])
    for endpoint in split:
        half = tuple(sorted((endpoint, new_knot)))
        rest.append(tuple(sorted((half, doubled))))
    return canonical(tuple(sorted(rest)))


def direct_minimum_check(row, optimum, expected):
    """Control: choose actual disjoint pairs in order, without grouping by holders."""
    owners = {d: tuple(i for i, support in enumerate(row["supports"]) if d in support)
              for support in row["supports"] for d in support}
    choices = []
    for i, pair in enumerate(row["pairs"]):
        parity = (row["cost"] >> i) & 1
        for check in row["checks"]:
            parity = (parity << 1) | ((check >> i) & 1)
        a, b = pair
        choices.append((1 << a | 1 << b, parity, reader_mark(owners, pair)))
    target = 1 << len(row["checks"])
    for length in range(1, optimum + 1):
        counts = Counter()

        def extend(first, used, val, selection):
            left = length - len(selection)
            if not left:
                if val == target:
                    counts[canonical(tuple(sorted(selection)))] += 1
                return
            for j in range(first, len(choices) - left + 1):
                mask, contribution, mark = choices[j]
                if not used & mask:
                    extend(j + 1, used | mask, val ^ contribution, selection + (mark,))

        extend(0, 0, 0, ())
        assert counts == (expected if length == optimum else {})


def repetition_example():
    """Verify the two-bit repetition isometry on every logical basis state.

    Knots 0,1,2,3 are the four original questions. For their first reader,
    the meeting (0,1) passes through 4, and (2,3) is doubled. The two copies
    of (2,3) use different readers. Each row below is one distinction.
    """
    specification = [
        ((0, 4), 0, "Z"), ((1, 4), 1, "Z"), ((2, 3), 0, "X"), ((2, 3), 1, "X"),
        ((0, 2), 2, "X"), ((1, 3), 2, "Z"), ((0, 3), 3, "X"), ((1, 2), 3, "Z"),
    ]
    marks = tuple(sorted(tuple(sorted(hs for hs, reader, _ in specification if reader == i))
                         for i in range(4)))
    base = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
    only_child, = {pass_and_double(base, i, j) for i in range(3) for j in range(2)}
    assert only_child == canonical(marks)
    after_two = defaultdict(set)
    for i, settings in enumerate(marks):
        for j, setting in enumerate(settings):
            if (2, 3) not in settings:
                role = "A setting of one of the two untouched original readers"
            elif setting == (2, 3):
                role = "One of the two copies made at the first doubling"
            else:
                role = "One of the two halves made at the first pass"
            after_two[pass_and_double(marks, i, j)].add(role)
    assert sum(len(roles) for roles in after_two.values()) == 3
    physical = ["".join(next((op for holders, r, op in specification if h in holders and i == r), "I")
                        for i in range(4)) for h in range(5)]
    logical = ["ZXX", "ZZZ", "XXZ", "XZX"]

    def act(ops, basis):
        bitword, sign = basis, 1
        for i, op in enumerate(ops):
            if op == "Z" and (basis >> i) & 1:
                sign *= -1
            if op == "X":
                bitword ^= 1 << i
        return bitword, sign

    def lift(bits):
        return (bits << 1) | (bits & 1)

    for h, check in enumerate(physical):
        for bits in range(8):
            image, sign = act(logical[h] if h < 4 else "III", bits)
            assert act(check, lift(bits)) == (lift(image), sign)
    for a, b in combinations(physical, 2):
        for bits in range(16):
            def compose(first, second):
                nxt, s1 = act(first, bits)
                end, s2 = act(second, nxt)
                return end, s1 * s2
            assert compose(a, b) == compose(b, a)
    for start in range(16):
        state, sign = start, 1
        for check in physical:
            state, extra = act(check, state)
            sign *= extra
        assert (state, sign) == (start, -1)
    # Twice the amplitude, so the entire verification uses integers.
    logical_state = {0: 1, 6: 1, 3: 1, 5: -1}
    physical_state = {lift(b): amp for b, amp in logical_state.items()}
    for check, wanted in zip(physical, [1, 1, 1, -1, 1], strict=True):
        actual = {}
        for b, amp in physical_state.items():
            image, sign = act(check, b)
            actual[image] = sign * amp
        assert actual == {b: wanted * amp for b, amp in physical_state.items()}
    return only_child, after_two, {
        "logical checks in knot order": logical, "encoded checks including the added knot": physical,
        "basis convention": "Bit 0 is the first reader. The isometry duplicates this bit.",
        "intertwining equalities on logical basis states": 5 * 8,
        "pairwise commutation equalities on four-reader basis states": 10 * 16,
        "whole product equals minus identity on basis states": 16,
        "normalized logical state, with first reader printed first": "(|000> + |011> + |110> - |101>)/2",
        "normalized encoded state": "(|0000> + |0011> + |1110> - |1101>)/2",
        "verified signs in knot order on this encoded state": [1, 1, 1, -1, 1],
    }


def audit(study, prior):
    owners, marks, columns, options, odd = make_code(prior)
    witness = [tuple(p) for p in study["strict readers"]]
    options_map = {p: c for c, poss in zip(columns, options) for p in poss}
    val = 0
    for p in witness:
        val ^= options_map[p]
    assert val == odd and len({d for p in witness for d in p}) == 2 * len(witness)
    active = tuple(sorted(reader_mark(owners, p) for p in witness))
    selected = canonical(active)
    optimum, counts, examples = all_minima(marks, columns, options, odd, len(witness))
    assert optimum == len(witness) == study["fewest strict readers"] and selected in counts
    direct_control = prior["start"] in {786, 6131, 6181, 6185}
    if direct_control:
        direct_minimum_check(prior, optimum, counts)
    holding = tuple(sorted(owners.values()))
    active_settings = [s for m in active for s in m]
    active_meetings = Counter(active_settings)
    full_meetings = Counter(holding)
    active_degrees = Counter(h for s in active_settings for h in s)
    passed = []
    for h, degree in active_degrees.items():
        if degree != 2:
            continue
        ends = sorted(k for s in active_settings if h in s for k in s if k != h)
        if len(set(ends)) == 2:
            passed.append({"knot": h, "full size": len(prior["supports"][h]),
                           "meetings directly between its two ends": full_meetings[tuple(ends)]})
    return {
        "start": prior["start"], "fewest strict readers": optimum, "selected": selected,
        "counts": counts, "examples": examples,
        "ungrouped control": direct_control,
        "whole holding": canonical((), holding), "whole holding with selected marks": canonical(active, holding),
        "unmarked reader distinctions": canonical((), tuple(sorted(s for m in active for s in m))),
        "outside distinctions": len(owners) - 2 * len(witness),
        "knots with no reader setting": prior["knots"] - len({h for m in active for s in m for h in s}),
        "passes": passed,
        "smallest full knot": min(map(len, prior["supports"])),
        "full multiplicities at doubled meetings": sorted(full_meetings[s] for s, n in active_meetings.items() if n == 2),
    }


def report(rows):
    after_one, after_two, operator = repetition_example()
    selected = Counter(r["selected"] for r in rows)
    kinds = {shape for row in rows for shape in row["counts"]}
    order = sorted(kinds, key=lambda shape: (-selected[shape], shape))
    ids = {shape: i + 1 for i, shape in enumerate(order)}
    table = []
    for shape in order:
        chosen = [r for r in rows if r["selected"] == shape]
        admits = [r for r in rows if shape in r["counts"]]
        table.append({
            "shape": ids[shape], "readers as unordered pairs of holder lists": shape[0],
            "fewest strict readers": len(shape[0]), "selected closures": len(chosen),
            "knots holding a reader setting": len({h for mark in shape[0] for setting in mark for h in setting}),
            "labelled minimum strict words": sum(r["counts"][shape] for r in admits),
            "closures with some minimum of this shape": len(admits),
            "closures with every minimum of this shape": sum(len(r["counts"]) == 1 for r in admits),
            "distinct whole holdings among selected closures": len({r["whole holding"] for r in chosen}),
            "distinct whole holdings with selected marks": len({r["whole holding with selected marks"] for r in chosen}),
            "outside distinction counts of selected closures": dict(sorted(Counter(r["outside distinctions"] for r in chosen).items())),
            "counts of unasked knots of selected closures": dict(sorted(Counter(r["knots with no reader setting"] for r in chosen).items())),
            "after exactly one repetition encoding of the three-reader form": shape == after_one,
            "after exactly two repetition encodings of the three-reader form": shape in after_two,
            "permitted second passes yielding this shape": sorted(after_two.get(shape, set())),
            "example census start": admits[0]["start"],
            "one minimum there as pairs of distinction IDs": admits[0]["examples"][shape],
        })

    by_start = []
    for r in rows:
        by_start.append({
            "start": r["start"], "selected shape": ids[r["selected"]],
            "all minimum strict words by shape": {ids[s]: c for s, c in sorted(r["counts"].items(), key=lambda x: ids[x[0]])},
            **({"one actual word of each shape": {ids[s]: pairs for s, pairs in r["examples"].items()}}
               if len(r["counts"]) > 1 else {}),
        })
    primary = [r for r in rows if r["selected"] == after_one]
    for r in primary:
        assert len(r["passes"]) == len(r["full multiplicities at doubled meetings"]) == 1
    fuller = [r for r in primary if r["passes"][0]["full size"] > 2]
    return {
        "inputs": ["../results.jsonl (selected strict readers and no-odd-ring filter)",
                   "../../MOST-FAILING-20261127-001/referee-R1/codes.jsonl (reconstructed birth-pair lists and holdings)"],
        "weighting of closure counts": "One vote per eligible census start, restricted to strict splits without an odd ring around a knot.",
        "equivalence": "Retain the two holders of each distinction in a reader, and which two distinctions are that reader. Omit all other distinctions and knots they alone touch. Relabel knots, readers and the two settings within each reader.",
        "closures": len(rows), "selected marked shapes": len(selected), "marked shapes over all tied minima": len(kinds),
        "unmarked shapes of the selected reader distinctions": len({r["unmarked reader distinctions"] for r in rows}),
        "closures with multiple minimum strict words": sum(sum(r["counts"].values()) > 1 for r in rows),
        "closures with multiple minimum marked shapes": sum(len(r["counts"]) > 1 for r in rows),
        "total minimum strict words (labelled distinctions)": sum(sum(r["counts"].values()) for r in rows),
        "independent ungrouped controls, census indices": [r["start"] for r in rows if r["ungrouped control"]],
        "number of different shapes with exactly two repetition encodings of the three-reader form": len(after_two),
        "selected closures with exactly two repetition encodings of the three-reader form": sum(selected[s] for s in after_two),
        "whole versus selected one-encoding projection": {
            "whole holdings with all knots of size at least three": sum(r["smallest full knot"] >= 3 for r in primary),
            "full sizes of its two-setting knot, count by size": dict(sorted(Counter(r["passes"][0]["full size"] for r in primary).items())),
            "full multiplicities at the doubled meeting, count by multiplicity": dict(sorted(Counter(r["full multiplicities at doubled meetings"][0] for r in primary).items())),
            "full direct meetings between the ends of the pass, count by multiplicity": dict(sorted(Counter(r["passes"][0]["meetings directly between its two ends"] for r in primary).items())),
            "example where the two-setting knot holds further distinctions": ({"census start": fuller[0]["start"], **fuller[0]["passes"][0]} if fuller else None),
        },
        "operator certificate for the one-encoding shape": operator, "shapes": table, "by census start": by_start,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Time a prefix without replacing the full JSON output.")
    args = parser.parse_args()
    studies = {row["start"]: row for row in read_rows(HERE.parent / "results.jsonl")
               if row["strict"] and row["shortest odd ring around a knot"] is None}
    rows = []
    for prior in read_rows(PRIOR):
        if prior.get("start") in studies:
            rows.append(audit(studies[prior["start"]], prior))
            if args.limit and len(rows) == args.limit:
                break
    if not args.limit:
        assert len(rows) == len(studies)
    result = report(rows)
    print(json.dumps({key: result[key] for key in (
        "closures", "selected marked shapes", "marked shapes over all tied minima",
        "closures with multiple minimum strict words", "closures with multiple minimum marked shapes",
        "total minimum strict words (labelled distinctions)")}))
    if not args.limit:
        (HERE / "shapes.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
