"""Test every cross-pair attachment of the minimal even grown choices above coverage two."""

from collections import Counter, defaultdict
from itertools import product
import json

from minimal_count import HERE, bits, minimal_words, reconstruct, sources
from minimal_measure import colourable, components, measure_cycles, occurrences


def pairings(items):
    if not items:
        yield ()
        return
    first, *rest = items
    for i, other in enumerate(rest):
        for remaining in pairings(rest[:i] + rest[i + 1:]):
            yield ((first, other), *remaining)


def analyse_attachment(paired):
    corners = defaultdict(list)
    orientations = defaultdict(list)
    covered = []
    same = 0
    for (a, b), matching in paired:
        for (i, forward), (j, other_forward) in matching:
            same_order = forward == other_forward
            same += same_order
            orientations[i].append((j, same_order))
            orientations[j].append((i, same_order))
            covered.append((a, b, i))
            for knot in (a, b):
                corners[knot, i].append((knot, j))
                corners[knot, j].append((knot, i))
    assert all(len(peers) == 2 for peers in corners.values())
    assert len(covered) == 2 * len(orientations)
    labels = components(corners)
    neighbour_colours = defaultdict(list)
    for a, b, i in covered:
        first, other = labels[a, i], labels[b, i]
        neighbour_colours[first].append((other, 1))
        neighbour_colours[other].append((first, 1))
    euler = len(set(labels.values())) - len(covered) + len(orientations)
    connected = len(set(components({i: [j for j, _ in targets]
                                    for i, targets in orientations.items()}).values())) == 1
    return colourable(orientations), euler, colourable(neighbour_colours), connected, same % 2


def analyse_choice(cycles, sign):
    at = occurrences(cycles)
    counts = Counter()
    examples = {}
    for matching in product(*(pairings(items) for items in at.values())):
        paired = list(zip(at, matching))
        orientable, euler, two_colourable, connected, parity = analyse_attachment(paired)
        assert connected and parity == sign
        result = orientable, euler, two_colourable
        counts[result] += 1
        if result not in examples:
            examples[result] = [
                [pair, [[left[0], right[0]] for left, right in matches]]
                for pair, matches in paired if len(matches) > 1
            ]
    return counts, examples


def main():
    measured = json.loads((HERE / "minimal_rows.json").read_text())
    wanted = {}
    for row in measured:
        if row["population"] != "closure" or "minimal strict even" not in row["tallies"]:
            continue
        coverage = row["tallies"]["minimal strict even"]["most at a cross pair"]
        count = sum(n for c, n in coverage.items() if int(c) > 2)
        if count:
            wanted[row["start"]] = count
    rows = {}
    choice_counts = Counter()
    attachment_counts = Counter()
    witnesses = []
    witnessed_fields = set()
    for source in sources():
        if source["population"] != "birth" or source["key"] not in wanted:
            continue
        code = reconstruct(source)
        found = 0
        outcomes = Counter()
        for word in minimal_words(code, 8):
            if (word & code.cost).bit_count() % 2:
                continue
            cycles = [code.cycles[i] for i in bits(word)]
            original = measure_cycles(cycles)
            if original["covered_twice"]:
                continue
            found += 1
            assert original["max_coverage"] == 4
            counts, examples = analyse_choice(cycles, original["sign"])
            variations = tuple(len({entry[i] for entry in counts}) > 1 for i in range(3))
            assert original["orientable"] == any(entry[0] for entry in counts)
            summary = (sum(counts.values()), *variations)
            outcomes[summary] += 1
            attachment_counts.update(counts)
            fields = ("orientability", "separated Euler count", "two-colourability")
            new_witnesses = [field for field, changes in zip(fields, variations)
                             if changes and field not in witnessed_fields]
            if new_witnesses:
                witnessed_fields.update(new_witnesses)
                witnesses.append({
                    "census start": source["key"],
                    "failing pairs": [source["pairs"][i] for i in bits(word)],
                    "cycles": cycles,
                    "properties varying with attachment": new_witnesses,
                    "outcomes": [
                        {"orientable": o, "Euler count": e, "two-colourable": t,
                         "pairing at fourfold cross pairs": examples[o, e, t]}
                        for o, e, t in sorted(counts)
                    ],
                })
        assert found == wanted[source["key"]]
        choice_counts.update(outcomes)
        rows[str(source["key"])] = [[*fields, total] for fields, total in sorted(outcomes.items())]
    assert set(map(int, rows)) == wanted.keys()
    receipt = {
        "scope": "Every minimal strict even choice with coverage above two in the strict-positive grown closures.",
        "weighting": "One per labelled choice for each choice histogram, one per attachment for the attachment histogram.",
        "row fields": ["attachments", "orientability varies", "Euler count varies", "two-colourability varies", "choices"],
        "choices with more than two occurrences at a cross pair": sum(choice_counts.values()),
        "choices by outcome variation and number of attachments": [
            [*fields, total] for fields, total in sorted(choice_counts.items())
        ],
        "attachment fields": ["orientable", "separated Euler count", "two-colourable", "attachments"],
        "attachments by outcome": [[*fields, total] for fields, total in sorted(attachment_counts.items())],
        "witnesses": witnesses,
        "closures by census start": rows,
    }
    (HERE / "minimal_attachment.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({key: fields for key, fields in receipt.items() if key != "closures by census start"}, indent=2))


if __name__ == "__main__":
    main()
