"""Replay the exact bounded search over small two-terminal parity cores."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVE = ROOT / "experiments/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds"
INF = 9999


def setup(params):
    global engine, order, maximum, shard, population
    engine = params["engine"]
    order = int(params["order"])
    maximum = int(params["maximum"])
    shard = int(params.get("shard", 131072))
    population = (maximum + 1) ** (order * (order - 1) // 2)


def cases():
    for start in range(0, population, shard):
        yield f"n{order}-w{maximum}-{start // shard:04d}", [start, min(start + shard, population)]


def run(case_id, payload):
    first, last = payload
    output = subprocess.check_output([engine, *map(str, (order, maximum, first, last))], text=True)
    records = [json.loads(line) for line in output.splitlines()]
    assert (records[-1]["first_index"], records[-1]["past_index"]) == (first, last), case_id
    return records


def collect(folders):
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results

    summaries = []
    for folder in folders:
        setup(json.loads((folder / "job.json").read_bytes())["params"])
        finished = load_results(folder)
        expected = {case_id for case_id, _ in cases()}
        assert expected == set(finished)
        assert all(case["status"] == "ok" for case in finished.values())
        total = Counter()
        setup_examples, failures = [], []
        for case_id in sorted(finished):
            rows = finished[case_id]["result"]
            total.update(rows[-1]["counts"])
            for row in rows[:-1]:
                if "unrefined_separator_example" in row:
                    setup_examples.append(row["unrefined_separator_example"])
                else:
                    failures.append(row["breaking_example"])
        assert total["admissible_cores"] == sum(total[k] for k in (
            "only_parallel_domains", "same_separator_minima_through_three", "same_triple_minima_at_price_one",
            "no_possible_tie_price", "requiring_current_price_search",
        ))
        assert len(failures) == total["breaking_cores"]
        summaries.append({"junctions": order, "highest_multiplicity": maximum, "labeled_weight_vectors": population,
                          "shards": len(expected), "counts": dict(total),
                          "first_unrefined_separator_example": setup_examples[0] if setup_examples else None,
                          "breaking_examples": failures})
    return sorted(summaries, key=lambda row: (row["junctions"], row["highest_multiplicity"]))


def rows_from_weights(n, weights):
    rows = [[] for _ in range(n)]
    width = 0
    for (s, t), multiplicity in zip(combinations(range(n), 2), weights, strict=True):
        crossing = list(range(width, width + multiplicity))
        rows[s].extend(crossing)
        rows[t].extend(crossing)
        width += multiplicity
    return rows, width


def xor_bonds(rows):
    words = {0}
    for row in rows:
        mask = sum(1 << name for name in row)
        words |= {word ^ mask for word in words}
    bonds = []
    for mask in sorted(words - {0}, key=lambda mask: (mask.bit_count(), mask)):
        if not any(mask & small == small for small in bonds):
            bonds.append(mask)
    return bonds


def contains_all(bonds, marks):
    want = sum(1 << x for x in marks)
    return next((mask.bit_count() for mask in bonds if mask & want == want), INF)


def changed(bonds, width, image, arity):
    count = 0
    first = None
    for mark in combinations(range(width), arity):
        other = tuple(sorted(image[x] for x in mark))
        x, y = contains_all(bonds, mark), contains_all(bonds, other)
        if x != y:
            count += 1
            if first is None:
                first = {"marks": mark, "image": other, "bond_cardinalities": [x, y]}
    return {"changed": count, "first": first}


def literal_virtual_control(case):
    rows, width = rows_from_weights(case["n"], case["weights"])
    assert width == case["width"]
    image = case["image"]

    def virtual(price):
        return xor_bonds([row + list(range(width, width + price)) if s < 2 else row
                          for s, row in enumerate(rows)])

    def separate(marks):
        size = contains_all(unit_bonds, (*marks, width))
        return INF if size == INF else size - 1

    unit_bonds = virtual(1)
    together = [word for word in unit_bonds if not (word & (1 << width))]
    different_separators = []
    for length in (1, 2, 3):
        for marks in combinations(range(width), length):
            moved = tuple(sorted(image[x] for x in marks))
            source, target = separate(marks), separate(moved)
            if source != target:
                different_separators.append((marks, moved, source, target))
    assert all(len(test[0]) == 3 for test in different_separators)
    assert [separate(case["triple"]), separate(case["triple_image"])] == case["L"]
    assert [contains_all(together, case[key]) for key in ("triple", "triple_image")] == case["B"]
    order = (len(different_separators), different_separators[0] if different_separators else None)
    result = {"rows": rows, "separator_triple_comparisons": order}
    if case["lambda"]:
        current = virtual(case["lambda"])
        result["old_pair_comparison"] = changed(current, width, image, 2)
        result["old_triple_comparison"] = changed(current, width, image, 3)
        result["lower_price_triple_comparison"] = changed(unit_bonds, width, image, 3)
        assert result["old_pair_comparison"]["changed"] == result["old_triple_comparison"]["changed"] == 0
        assert result["lower_price_triple_comparison"]["changed"] > 0
    return result


def hidden_separator_controls(panels):
    return [literal_virtual_control(witness) for panel in panels
            if (witness := panel["first_unrefined_separator_example"]) is not None]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    modes.add_parser("prepare").add_argument("binary", type=Path)
    modes.add_parser("collect").add_argument("folders", nargs="+", type=Path)
    control = modes.add_parser("controls")
    control.add_argument("summary", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare":
        subprocess.run(["c++", "-std=c++20", "-O3", str(HERE / "weighted_core.cpp"), "-o", str(args.binary)], check=True)
    elif args.mode == "collect":
        print(json.dumps(collect(args.folders), indent=2))
    elif args.mode == "controls":
        print(json.dumps(hidden_separator_controls(json.loads(args.summary.read_bytes())), indent=2))


if __name__ == "__main__":
    main()
