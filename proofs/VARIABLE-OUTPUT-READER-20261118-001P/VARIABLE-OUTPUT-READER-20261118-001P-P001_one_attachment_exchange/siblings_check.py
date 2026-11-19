"""Measure the strict child-output comparison on the archived one-spent examples."""

from collections import Counter
import json
from pathlib import Path


def connected(vertices, adjacency):
    reached = 0
    pending = vertices & -vertices
    while pending:
        site = pending & -pending
        reached |= site
        pending ^= site
        pending |= adjacency[site.bit_length() - 1] & vertices & ~reached
    return reached == vertices


def bond_minima(rows, pairs):
    exterior = len(rows)
    adjacency = [0] * (exterior + 1)
    holders = {}
    for site, row in enumerate(rows):
        for bit in row:
            holders.setdefault(bit, []).append(site)
    for ends in holders.values():
        if len(ends) == 1:
            ends = [ends[0], exterior]
        left, right = ends
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left

    stars = [sum(1 << bit for bit in row) for row in rows]
    marked = {pair: (1 << pair[0]) | (1 << pair[1]) for pair in pairs}
    best = {pair: len(holders) + 1 for pair in pairs}
    all_sites = (1 << (exterior + 1)) - 1
    cut = 0
    for index in range(1, 1 << exterior):
        shore = index ^ (index >> 1)
        cut ^= stars[(index & -index).bit_length() - 1]
        size = cut.bit_count()
        improved = [pair for pair, bits in marked.items() if size < best[pair] and cut & bits == bits]
        if improved and connected(shore, adjacency) and connected(all_sites ^ shore, adjacency):
            for pair in improved:
                best[pair] = size
    assert all(value <= len(holders) for value in best.values())
    return best


def run():
    family = Path(__file__).resolve().parent
    archive, = (family.parents[1] / "VARIABLE-OUTPUT-READER-20261118-001O").glob("*/frontier.json")
    examples = json.loads(archive.read_text())["minimum_literal_examples"]
    by_spend = Counter()
    marked_sizes = Counter()
    child_sizes = Counter()
    min_later = None
    for example in examples:
        rows = example["junction_supports"]
        high, child = example["fourth_site"], example["spending_child"]
        later_names = {bit for row in rows[child + 1 :] for bit in row}
        loose = [f for f in rows[child][-2:] if f not in later_names]
        if not loose:
            continue
        inputs, outputs = rows[high][:-3], rows[high][-3:]
        spent, = set(outputs).intersection(rows[child])
        marked = [(i, spent) for i in inputs]
        child_pairs = [(i, f) for i in inputs for f in loose]
        observed = bond_minima(rows, marked + child_pairs)
        assert all(observed[pair] <= 6 for pair in marked)
        assert all(observed[pair] > 6 for pair in child_pairs)
        marked_sizes.update(observed[pair] for pair in marked)
        child_sizes.update(observed[pair] for pair in child_pairs)
        key = (len(rows[child]) - 2, bool(rows[child + 1 :]), 2 - len(loose))
        by_spend[key] += 1
        if len(loose) == 1:
            pair = min(child_pairs, key=observed.get)
            candidate = (observed[pair], example["width"], high, child, *pair)
            min_later = candidate if min_later is None else min(min_later, candidate)

    return {
        "archive": archive.relative_to(family.parents[2]).as_posix(),
        "source_examples": len(examples),
        "examples_with_a_loose_child_output": sum(by_spend.values()),
        "by_spending_parents_later_sites_spent_child_outputs": [
            [*key, value] for key, value in sorted(by_spend.items())
        ],
        "high_input_to_spent_meeting_size_counts": dict(sorted(marked_sizes.items())),
        "high_input_to_loose_child_output_size_counts": dict(sorted(child_sizes.items())),
        "least_size_with_one_child_output_used": dict(
            zip(("bond_size", "width", "fourth_site", "spending_child", "input", "output"), min_later)
        ),
    }


if __name__ == "__main__":
    Path(__file__).with_name("siblings_check.json").write_text(json.dumps(run(), indent=2) + "\n")
