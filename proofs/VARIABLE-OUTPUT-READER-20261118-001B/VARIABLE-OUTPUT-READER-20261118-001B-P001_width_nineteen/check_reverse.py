"""Independent reverse census and exact marked-triple orbit check at width 19.

For a marked triple, the canonical group calculation counts its setwise
stabilizer. Orbit size then tells how many triples must be in the actual menu
if that menu contains the orbit. The canonical marked encodings also compare
complete menus between different presentations of one table.
"""

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations, product
from math import factorial
from pathlib import Path


WIDTH = 19
INFINITY = WIDTH
PAIRS = tuple(combinations(range(WIDTH), 2))
REFERENCE = (
    Path(__file__).resolve().parents[2] / "VARIABLE-OUTPUT-READER-20261118-001A"
    / "VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen" / "check_reference.py"
)
spec = importlib.util.spec_from_file_location("width_eighteen_reverse_tools", REFERENCE)
reverse = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reverse
spec.loader.exec_module(reverse)


def presentations(size, stats):
    for columns, neighbors, equivalent in reverse.shapes(size):
        stats["connected_bipartite_shapes"] += 1
        degrees = tuple(group.bit_count() for group in neighbors)
        total_loose = WIDTH - sum(degrees) // 2
        choices = [range(max(0, 3 - degree), min(3, 6 - degree) + 1) for degree in degrees]
        reachable_shape = False
        for loose in product(*choices):
            if sum(loose) != total_loose or not reverse.canonical_counts(loose, columns, equivalent):
                continue
            sizes = tuple(a + b for a, b in zip(degrees, loose))
            history = reverse.legal_history(neighbors, sizes)
            if not history:
                continue
            active = 0
            births = Counter()
            for joint in history:
                births[sizes[joint] - (neighbors[joint] & active).bit_count()] += 1
                active |= 1 << joint
            threes_after_seed = WIDTH - 3 - 2 * (size - 1)
            assert births == {2: size - 1 - threes_after_seed, 3: threes_after_seed + 1}
            reachable_shape = True
            junctions = [[] for _ in loose]
            name = 0
            for joint, group in enumerate(neighbors):
                for other in reverse.bits(group):
                    if other > joint:
                        junctions[joint].append(name)
                        junctions[other].append(name)
                        name += 1
            for joint, count in enumerate(loose):
                junctions[joint].extend(range(name, name + count))
                name += count
            assert name == WIDTH
            yield tuple(tuple(junction) for junction in junctions), history
        stats["reachable_shapes"] += reachable_shape


def triple_menu(junctions):
    owners = [tuple(i for i, group in enumerate(junctions) if name in group) for name in range(WIDTH)]
    neighbors = [set() for _ in junctions]
    loose = defaultdict(list)
    for name, groups in enumerate(owners):
        if len(groups) == 1:
            loose[groups[0]].append(name)
        else:
            first, second = groups
            neighbors[first].add(second)
            neighbors[second].add(first)
    legal = set()
    for a, b, c in combinations(loose, 3):
        first, second, third = neighbors[a], neighbors[b], neighbors[c]
        if first & second and second & third and third & first and not first & second & third:
            legal.update(tuple(sorted(triple)) for triple in product(loose[a], loose[b], loose[c]))
    return legal


def bond_table(junctions):
    parity_span = [0]
    for group in junctions:
        mask = reverse.mask_of(group)
        parity_span.extend(word ^ mask for word in parity_span[:])
    assert len(set(parity_span)) == len(parity_span)
    entries = [bytearray([INFINITY] * WIDTH) for _ in range(WIDTH)]
    for i in range(WIDTH):
        entries[i][i] = 0
    bonds = []
    for word in sorted(parity_span[1:], key=int.bit_count):
        if any(prior & word == prior for prior in bonds):
            continue
        bonds.append(word)
        value = word.bit_count() - 1
        assert value >= 2
        for i, j in combinations(reverse.bits(word), 2):
            if entries[i][j] == INFINITY:
                entries[i][j] = entries[j][i] = value
    return tuple(bytes(row) for row in entries), bonds, parity_span


def interchangeable(table):
    classes = []
    for i, row in enumerate(table):
        twin = i
        for j, representative in enumerate(classes):
            if j == representative and (row[:j] + row[j+1:i] + row[i+1:]
                                         == table[j][:j] + table[j][j+1:i] + table[j][i+1:]):
                twin = j
                break
        classes.append(twin)
    return classes


def refine(table, cells):
    while True:
        refined = []
        for cell in cells:
            if len(cell) == 1:
                refined.append(cell)
                continue
            groups = defaultdict(list)
            for i in cell:
                key = tuple(bytes(sorted(table[i][j] for j in other)) for other in cells)
                groups[key].append(i)
            refined.extend(tuple(groups[key]) for key in sorted(groups))
        if len(refined) == len(cells):
            return refined
        cells = refined


def canonical(table, twins, marked=()):
    """Return the exact canonical encoding, stabilizer order and a label order."""
    start = [tuple(i for i in range(WIDTH) if i not in marked)]
    if marked:
        start.append(marked)

    def search(cells):
        frozen = []
        factor = 1
        choices = []
        for cell in refine(table, cells):
            if all(twins[i] == twins[cell[0]] for i in cell):
                frozen.extend((i,) for i in cell)
                factor *= factorial(len(cell))
            else:
                choices.append(len(frozen))
                frozen.append(cell)
        if not choices:
            order = tuple(cell[0] for cell in frozen)
            encoding = bytes(table[order[i]][order[j]] for i, j in PAIRS)
            return encoding, factor, order

        pivot = min(choices, key=lambda i: len(frozen[i]))
        cell = frozen[pivot]
        groups = defaultdict(list)
        for i in cell:
            groups[twins[i]].append(i)
        best = None
        count = 0
        for group in groups.values():
            lead = group[0]
            branch = frozen[:pivot] + [(lead,), tuple(i for i in cell if i != lead)] + frozen[pivot+1:]
            encoding, orders, label_order = search(branch)
            if best is None or encoding < best:
                best, count, order = encoding, orders * len(group), label_order
            elif encoding == best:
                count += orders * len(group)
        return best, count * factor, order

    return search(start)


def marked_orbits(table, twins, triples, group_order):
    groups = defaultdict(list)
    for triple in sorted(triples):
        groups[tuple(sorted(twins[i] for i in triple))].append(triple)
    marks = {}
    actual_counts = Counter()
    for group in groups.values():
        key, stabilizer, ordering = canonical(table, twins, group[0])
        orbit_size, remainder = divmod(group_order, stabilizer)
        assert not remainder
        if key in marks:
            assert marks[key][1] == orbit_size
        else:
            marks[key] = (group[0], orbit_size, ordering)
        actual_counts[key] += len(group)
    partial = {key for key, count in actual_counts.items() if count != marks[key][1]}
    assert all(count <= marks[key][1] for key, count in actual_counts.items())
    return marks, partial


def table_map(first, second, first_order, second_order):
    mapping = dict(zip(first_order, second_order, strict=True))
    assert all(first[i][j] == second[mapping[i]][mapping[j]] for i, j in PAIRS)
    return mapping


def partial_orbit_witness(table, twins, legal, marks, partial):
    key = min(partial)
    first, _, order = marks[key]
    for wrong in combinations(range(WIDTH), 3):
        if wrong in legal:
            continue
        wrong_key, _, wrong_order = canonical(table, twins, wrong)
        if wrong_key == key:
            mapping = table_map(table, table, order, wrong_order)
            assert tuple(sorted(mapping[i] for i in first)) == wrong
            return {"from": first, "to": wrong, "permutation": sorted(mapping.items())}
    raise AssertionError("A partial orbit must contain a forbidden triple")


def direct_group_order(table, marked=()):
    """Enumerate the fixture's maps directly without canonical refinement."""
    profiles = [(bytes(sorted(row)), i in marked) for i, row in enumerate(table)]
    domains = [tuple(j for j, profile in enumerate(profiles) if profile == own) for own in profiles]
    names = sorted(range(WIDTH), key=lambda i: len(domains[i]))
    assigned = {}

    def extend(offset):
        if offset == WIDTH:
            return 1
        name = names[offset]
        total = 0
        for target in domains[name]:
            if target in assigned.values() or any(table[name][old] != table[target][new]
                                                  for old, new in assigned.items()):
                continue
            assigned[name] = target
            total += extend(offset + 1)
            del assigned[name]
        return total

    return extend(0)


def literal_positive():
    checks = (*reverse.TARGET[:-1], (*reverse.TARGET[-1], 18))
    expected = set(product((11, 12), (13, 14, 15), (16, 17, 18)))
    legal = triple_menu(checks)
    assert legal == expected
    table, bonds, parity_span = bond_table(checks)
    equations = tuple(reverse.mask_of(group) for group in checks)
    values = [int(not any((row & equation).bit_count() % 2 for equation in equations))
              for row in range(1 << WIDTH)]
    rows = [word for word, allowed in enumerate(values) if allowed]
    assert len(rows) == 4096
    stride = 1
    while stride < len(values):
        for block in range(0, len(values), 2 * stride):
            for i in range(block, block + stride):
                left, right = values[i], values[i + stride]
                values[i], values[i + stride] = left + right, left - right
        stride *= 2
    assert {i for i, value in enumerate(values) if value == len(rows)} == set(parity_span)
    reverse.direct_bond_check(rows, bonds)

    twins = interchangeable(table)
    key, order, labeling = canonical(table, twins)
    distinguished = (11, 13, 16)
    _, stabilizer, _ = canonical(table, twins, distinguished)
    assert order == direct_group_order(table) == 72
    assert stabilizer == direct_group_order(table, distinguished) == 4

    extension_counts = {}
    for fresh in (2, 3):
        width = (1 << WIDTH) - 1
        observed = reverse.mask_of(distinguished)
        extensions = {row | (word << WIDTH) for row in rows for word in range(1 << fresh)
                      if ((row & observed).bit_count() + word.bit_count()) % 2 == 0}
        assert {row & width for row in extensions} == set(rows)
        assert len(extensions) == len(rows) * (1 << (fresh - 1))
        extension_counts[fresh] = len(extensions)

    relabel = tuple(WIDTH - i - 1 for i in range(WIDTH))
    other = tuple(bytes(table[relabel[i]][relabel[j]] for j in range(WIDTH)) for i in range(WIDTH))
    other_legal = {tuple(sorted(relabel[i] for i in triple)) for triple in legal}
    other_twins = interchangeable(other)
    other_key, other_order, other_labeling = canonical(other, other_twins)
    assert key == other_key and order == other_order
    mapping = table_map(table, other, labeling, other_labeling)
    assert {tuple(sorted(mapping[i] for i in triple)) for triple in legal} == other_legal
    good, partial = marked_orbits(table, twins, legal, order)
    other_good, other_partial = marked_orbits(other, other_twins, other_legal, other_order)
    assert good.keys() == other_good.keys() and not partial and not other_partial

    removed = (12, 13, 16)
    inserted = (11, 12, 16)
    assert removed in legal and inserted not in legal
    mutated = (legal - {removed}) | {inserted}
    assert len(mutated) == len(legal)
    wrong, partial = marked_orbits(table, twins, mutated, order)
    assert partial
    witness = partial_orbit_witness(table, twins, mutated, wrong, partial)
    assert witness["from"] in mutated and witness["to"] not in mutated
    return {"checks": checks, "literal_rows": len(rows), "bond_count": len(bonds), "legal_triples": sorted(legal),
            "unmarked_group_order": order, "legal_orbit_sizes": sorted(item[1] for item in good.values()),
            "directly_checked_stabilizer": stabilizer,
            "extension_row_counts_for_named_triple": extension_counts,
            "renaming_preserves_exact_menu": True,
            "same_count_negative": {"removed_legal_triple": removed, "inserted_illegal_triple": inserted,
                                    "detected_legal_to_illegal_in_mutant": witness}}


def run():
    stages = {}
    seen = {}
    coverage = Counter(dict.fromkeys(("legal_marked_orbits", "presentations_with_partial_orbits",
                                      "cross_presentation_table_matches", "cross_matches_touching_triples",
                                      "cross_presentation_triple_conflicts"), 0))
    first_conflict = None
    for size in (7, 8, 9):
        stats = Counter()
        for checks, history in presentations(size, stats):
            stats["presentations"] += 1
            legal = triple_menu(checks)
            stats["triple_bearing_presentations"] += bool(legal)
            stats["legal_triples"] += len(legal)
            table, _, _ = bond_table(checks)
            twins = interchangeable(table)
            key, group_order, labeling = canonical(table, twins)
            marks, partial = marked_orbits(table, twins, legal, group_order)
            coverage["legal_marked_orbits"] += len(marks)
            if partial:
                coverage["presentations_with_partial_orbits"] += 1
                if first_conflict is None:
                    first_conflict = {"checks": checks, "history": history,
                                      "within_presentation": partial_orbit_witness(table, twins, legal, marks, partial)}
            prior = seen.get(key)
            if prior is None:
                seen[key] = (checks, history, table, labeling, legal, marks.keys())
                continue
            old_checks, old_history, old_table, old_ordering, old_legal, old_marks = prior
            coverage["cross_presentation_table_matches"] += 1
            coverage["cross_matches_touching_triples"] += bool(legal or old_legal)
            if marks.keys() != old_marks:
                coverage["cross_presentation_triple_conflicts"] += 1
                if first_conflict is None:
                    mapping = table_map(table, old_table, labeling, old_ordering)
                    mapped = {tuple(sorted(mapping[i] for i in triple)): triple for triple in legal}
                    bad = sorted(mapped.keys() ^ old_legal)[0]
                    if bad in mapped:
                        source, target, operand, transported = (checks, history), (old_checks, old_history), mapped[bad], bad
                    else:
                        mapping = {b: a for a, b in mapping.items()}
                        source, target, operand = (old_checks, old_history), (checks, history), bad
                        transported = tuple(sorted(mapping[i] for i in bad))
                    first_conflict = {"source": source, "target": target, "from": operand,
                                      "to": transported, "permutation": sorted(mapping.items())}
        threes_after_seed = WIDTH - 3 - 2 * (size - 1)
        stages[size] = {**stats, "two_output_births_after_seed": size - 1 - threes_after_seed,
                       "three_output_births_after_seed": threes_after_seed}
    return {"width": WIDTH, "junction_counts": stages, "full_table_classes": len(seen),
            "class_count_with_legal_triple": sum(bool(data[4]) for data in seen.values()),
            "coverage": dict(sorted(coverage.items())), "first_conflict": first_conflict,
            "positive_and_mutant": literal_positive(),
            "reverse_checker_sha256": hashlib.sha256(REFERENCE.read_bytes()).hexdigest()}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
