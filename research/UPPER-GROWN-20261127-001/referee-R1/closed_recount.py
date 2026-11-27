"""Independently enumerate the closed systems, their bonds, and their boxes.

The archived generator is used only to restore the original numbering for
saved examples. Class coverage is checked by exhaustive breadth-first graph
generation. The relation search uses exact allowed-state bitsets. Its short
screen can witness a word's presence; every proposed absence is checked over
all allowed states. No study implementation is imported.
"""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path
import resource
import time

import networkx as nx
import numpy as np


STUDY = Path(__file__).resolve().parents[1]
GRAPH_SIZES = (4, 6, 8, 10, 12)
WITNESS_TRIALS = 12
WITNESS_WINDOW = 256


def indices(mask):
    while mask:
        least = mask & -mask
        yield least.bit_length() - 1
        mask ^= least


def as_mask(items):
    return sum(1 << i for i in items)


def packed(row):
    return int.from_bytes(np.packbits(row, bitorder="little").tobytes(), "little")


def adjacency(n, links):
    neighbors = [0] * n
    for a, b in links:
        assert a != b and not (neighbors[a] >> b) & 1
        neighbors[a] |= 1 << b
        neighbors[b] |= 1 << a
    return tuple(neighbors)


def label_graph(neighbors, order):
    positions = {old: new for new, old in enumerate(order)}
    return tuple(as_mask(positions[w] for w in indices(neighbors[v])) for v in order)


def breadth_first_keys(neighbors):
    """Every legal breadth-first labeling, including every root and tie order."""
    n = len(neighbors)

    def extend(order, seen, next_knot):
        while len(order) < n and next_knot < len(order):
            new = neighbors[order[next_knot]] & ~seen
            next_knot += 1
            if new.bit_count() > 1:
                for order_new in permutations(indices(new)):
                    yield from extend(order + order_new, seen | new, next_knot)
                return
            if new:
                order += (new.bit_length() - 1,)
                seen |= new
        if len(order) == n:
            yield label_graph(neighbors, order)

    for root in range(n):
        yield from extend((root,), 1 << root, 0)


def breadth_first_key(neighbors):
    order = [0]
    seen = 1
    for v in order:
        new = neighbors[v] & ~seen
        order.extend(indices(new))
        seen |= new
    return label_graph(neighbors, order) if len(order) == len(neighbors) else None


def generated_cubic(n):
    """Fill each knot's degree, adding newly discovered knots in BFS order."""
    neighbors = [0] * n

    def choose(knot, seen):
        if knot == n:
            yield tuple(neighbors)
            return
        needed = 3 - neighbors[knot].bit_count()
        occupied = [v for v in range(knot + 1, seen)
                    if neighbors[v].bit_count() < 3 and not (neighbors[knot] >> v) & 1]
        for count in range(max(0, needed - (n - seen)), min(len(occupied), needed) + 1):
            new = needed - count
            if seen + new == knot + 1 and seen + new < n:
                continue
            for past in combinations(occupied, count):
                mates = past + tuple(range(seen, seen + new))
                added = as_mask(mates)
                neighbors[knot] |= added
                for v in mates:
                    neighbors[v] |= 1 << knot
                yield from choose(knot + 1, seen + new)
                for v in mates:
                    neighbors[v] ^= 1 << knot
                neighbors[knot] ^= added

    yield from choose(0, 1)


def archive_rows(n):
    files = sorted((STUDY / "out").glob(f"cubic_{n}*.jsonl"))
    batches = []
    for path in files:
        result = []
        for line, raw in enumerate(path.read_text().splitlines(), 1):
            row = json.loads(raw)
            assert row["points"] == n and row["seconds"] >= 0
            result.append((path.name, line, row))
        batches.append(result)
    return [batch[i] for i in range(max(map(len, batches))) for batch in batches if i < len(batch)]


def class_coverage(n, rows):
    all_labels = {}
    labels_per_class = []
    for index, (_, _, row) in enumerate(rows):
        neighbors = adjacency(n, row["links"])
        assert all(d.bit_count() == 3 for d in neighbors)
        forms = set(breadth_first_keys(neighbors))
        assert forms and forms.isdisjoint(all_labels), (n, index, "duplicate or disconnected")
        labels_per_class.append(len(forms))
        all_labels.update(dict.fromkeys(forms, index))

    computed = set(generated_cubic(n))
    assert computed == all_labels.keys(), (n, len(computed), len(all_labels))

    # Continue through the twelve-knot replay's stated 3,000 trials. For
    # smaller sizes first matching class representatives suffice to recover
    # the original distinction numbering, when the seed follows that pattern.
    seeds_seen = {}
    drew_in_archive_order = True
    prefix = 3000 if n == 12 else 300
    for offset in range(prefix):
        graph = nx.random_regular_graph(3, n, seed=1000 + n + offset)
        links = list(graph.edges())
        key = breadth_first_key(adjacency(n, links))
        if key is None:
            continue
        index = all_labels[key]
        if index in seeds_seen:
            continue
        drew_in_archive_order &= index == len(seeds_seen)
        seeds_seen[index] = (1000 + n + offset, links)
    match = [sorted(seeds_seen[i][1]) == list(map(tuple, row["links"])) if i in seeds_seen else False
             for i, (_, _, row) in enumerate(rows)]
    if n == 12:
        assert all(match) and drew_in_archive_order
    numbering = {i: seeds_seen[i][1] for i, agree in enumerate(match) if agree}
    return {"graphs": len(rows), "breadth_first_labeled_graphs": len(computed),
            "labelings_per_class": labels_per_class, "first_seeded_representatives_match": sum(match),
            "first_seeded_classes_in_archive_order": drew_in_archive_order,
            "seeded_trials": prefix, "last_first_occurrence_seed": max((s for s, _ in seeds_seen.values()), default=None)}, numbering


def supports_from_links(n, links):
    holders = [[] for _ in range(n)]
    for distinction, (a, b) in enumerate(links):
        holders[a].append(distinction)
        holders[b].append(distinction)
    return tuple(tuple(holder) for holder in holders)


def stage_states(supports):
    # Fix one raw distinction to 0. Global complements preserve every law and
    # agreement, including under each source-law deletion.
    width = 1 + max(max(knot) for knot in supports)
    states = np.arange(1 << (width - 1), dtype=np.uint32)
    violations = np.zeros(len(states), dtype=np.uint32)
    for i, knot in enumerate(supports):
        mask = as_mask(knot)
        x = states & mask
        violations[(x == 0) | (x == mask)] |= 1 << i
    allowed = states[violations == 0]
    # Scattering the first few witnesses is an acceleration only. Full states
    # decide all proposed absent words, independently of this order.
    order = np.random.default_rng(61013).permutation(len(allowed))
    return width, allowed[order], states, violations


def reading_tables(width, allowed, supports):
    all_states = (1 << len(allowed)) - 1
    raw = [packed((allowed >> i) & 1) for i in range(width)]
    local_cells = []
    for a, b, c in supports:
        d = raw[a] ^ raw[b]
        e = raw[a] ^ raw[c]
        # A knot's relative bit patterns determine its values up to complement.
        # The agreement being tested is complement invariant.
        local_cells.append((d & e, d & ~e, e & ~d, all_states ^ (d | e)))

    carriers, yes, strict = [], [], []
    for size in (2, 3):
        for carrier in combinations(range(width), size):
            a, b = carrier[:2]
            d = raw[a] ^ raw[b]
            if size == 3:
                e = raw[a] ^ raw[carrier[2]]
                agreement = all_states ^ (d | e)
                uses_every_place = all((d & e, d & ~e, e & ~d))
            else:
                agreement = all_states ^ d
                uses_every_place = True
            if agreement == 0 or agreement == all_states:
                continue
            if any(not any((agreement & cell) not in (0, cell) for cell in cells) for cells in local_cells):
                continue
            carriers.append(carrier)
            yes.append(agreement)
            strict.append(uses_every_place)

    width_bytes = (len(allowed) + 7) // 8
    by_reading = np.array([np.frombuffer(row.to_bytes(width_bytes, "little"), dtype=np.uint8) for row in yes])
    by_state = np.unpackbits(by_reading, axis=1, count=len(allowed), bitorder="little").T if yes else []
    state_yes = [packed(row) for row in by_state]
    return carriers, yes, strict, state_yes


def disjoint_masks(carriers):
    masks = [as_mask(carrier) for carrier in carriers]
    containing = defaultdict(int)
    for i, carrier in enumerate(carriers):
        for place in carrier:
            containing[place] |= 1 << i
    all_readings = (1 << len(carriers)) - 1
    disjoint = []
    for carrier in carriers:
        shared = 0
        for place in carrier:
            shared |= containing[place]
        disjoint.append(all_readings ^ shared)
    return masks, disjoint


def bond_census(carriers, yes, strict, state_yes):
    _, disjoint = disjoint_masks(carriers)
    all_states = (1 << len(state_yes)) - 1
    no = [all_states ^ value for value in yes]
    all_readings = (1 << len(carriers)) - 1
    trial_signatures = [(value, all_readings ^ value) for value in state_yes[:WITNESS_WINDOW]]
    trial_window = (1 << WITNESS_WINDOW) - 1
    links = [0] * len(yes)
    for i, value in enumerate(yes):
        for j in indices(disjoint[i] & (-1 << (i + 1))):
            if value & yes[j] and value & no[j] and no[i] & yes[j] and no[i] & no[j]:
                links[i] |= 1 << j

    missing_histogram = Counter()
    single_words = Counter()
    strict_bonds = 0
    clauses = []
    for i, left in enumerate(links):
        for j in indices(left):
            possible = left & links[j]
            if not possible:
                continue
            missing = defaultdict(int)
            cells = (no[i] & no[j], no[i] & yes[j], yes[i] & no[j], yes[i] & yes[j])
            for cell_number, cell in enumerate(cells):
                need_zero = possible
                need_one = possible
                trial = cell & trial_window
                for _ in range(WITNESS_TRIALS):
                    state = trial & -trial
                    if not state:
                        break
                    seen_one, seen_zero = trial_signatures[state.bit_length() - 1]
                    need_zero &= seen_one
                    need_one &= seen_zero
                    if not (need_zero | need_one):
                        break
                    trial ^= state
                for k in indices(need_zero):
                    if not (cell & no[k]):
                        missing[k] |= 1 << (2 * cell_number)
                for k in indices(need_one):
                    if not (cell & yes[k]):
                        missing[k] |= 2 << (2 * cell_number)

            for k, words in missing.items():
                missing_histogram[words.bit_count()] += 1
                strict_bonds += bool(strict[i] and strict[j] and strict[k])
                if words.bit_count() == 1:
                    word = words.bit_length() - 1
                    clauses.append((2 * i + (word >> 2), 2 * j + ((word >> 1) & 1), 2 * k + (word & 1)))
                    single_words[f"{word:03b}"] += 1
    return missing_histogram, single_words, strict_bonds, clauses


def boxes_from_clauses(carriers, clauses):
    """Find each box by its least signed reading and one two-by-two rectangle."""
    pairs = defaultdict(int)
    links = defaultdict(dict)
    for a, b, c in clauses:
        for u, v, t in ((a, b, c), (a, c, b), (b, c, a)):
            pairs[u, v] |= 1 << t
        for u, v, t in ((a, b, c), (b, a, c), (c, a, b)):
            links[u][v] = links[u].get(v, 0) | (1 << t)
            links[u][t] = links[u].get(t, 0) | (1 << v)

    raw_masks = [as_mask(c) for c in carriers]
    carrier_masks = [m for m in raw_masks for _ in range(2)]
    contains = defaultdict(int)
    for i, carrier in enumerate(carriers):
        for place in carrier:
            contains[place] |= 3 << (2 * i)
    all_signed = (1 << len(carrier_masks)) - 1
    disjoint = []
    for carrier in carriers:
        shared = 0
        for place in carrier:
            shared |= contains[place]
        disjoint.extend((all_signed ^ shared,) * 2)

    boxes = []
    if len(links) < 6:
        return boxes
    for a, graph in links.items():
        if len(graph) < 4:
            continue
        after_a = -1 << (a + 1)
        future = [(b, row & after_a) for b, row in graph.items() if b > a]
        viable = as_mask(b for b, row in future if row.bit_count() >= 2)
        if viable.bit_count() < 4:
            continue
        future = sorted((b, row & viable) for b, row in future if (viable >> b) & 1)
        disjoint_a = disjoint[a] & after_a
        for i, (b0, b0_row) in enumerate(future):
            above_b0 = -1 << (b0 + 1)
            b0_row &= above_b0
            if b0_row.bit_count() < 2:
                continue
            for b1, b1_row in future[i + 1:]:
                if carrier_masks[b0] & carrier_masks[b1]:
                    continue
                common = b0_row & b1_row
                if common.bit_count() < 2:
                    continue
                a1_pool = disjoint_a & disjoint[b0] & disjoint[b1]
                alternatives = []
                for c in indices(common):
                    b1c = (b1, c) if b1 < c else (c, b1)
                    other_a = a1_pool & disjoint[c] & pairs[b0, c] & pairs[b1c]
                    if other_a:
                        alternatives.append((c, other_a))
                for (c0, with_c0), (c1, with_c1) in combinations(alternatives, 2):
                    if not (carrier_masks[c0] & carrier_masks[c1]):
                        for a1 in indices(with_c0 & with_c1):
                            boxes.append(((a, a1), (b0, b1), (c0, c1)))
    assert len(boxes) == len(set(boxes))
    return sorted(boxes)


def named_box(box, carriers):
    return tuple(tuple((carriers[signed // 2], signed % 2) for signed in pair) for pair in box)


def decode_box(box):
    return tuple(tuple((tuple(carrier), val) for carrier, val in pair) for pair in box)


def box_key(box):
    return tuple(sorted(tuple(sorted(pair)) for pair in box))


def upper_words(box, states):
    words = np.zeros(len(states), dtype=np.uint8)
    for pair in box:
        x, y = [states & as_mask(carrier) for carrier, _ in pair]
        (c0, v0), (c1, v1) = pair
        one = ((x == 0) | (x == as_mask(c0))) == v0
        two = ((y == 0) | (y == as_mask(c1))) == v1
        words = (words << 1) | (one != two)
    return words


def read_upper(box, allowed, single_violations):
    counts = 2 * np.bincount(upper_words(box, allowed), minlength=8)
    missing = np.flatnonzero(counts == 0)
    restored = [2 * int(np.isin(upper_words(box, states), missing).sum()) for states in single_violations]
    # Exactly seven upper words entail K1--K3. The eight lower clauses are
    # separately essential: the forbidden disjunctive word has exactly one
    # signed-true reading per pair, and removing one clause admits that word.
    return {"carriers_and_missing_values": box, "words": counts.tolist(),
            "missing": [f"{word:03b}" for word in missing],
            "restored_assignments_by_deleted_law": restored,
            "laws_needed": [i for i, n in enumerate(restored) if n > 0]}


def brute_small(width, supports, carriers):
    """Tiny control with literal assignments and explicit tuple images."""
    states = [s for s in product((0, 1), repeat=width)
              if all(len({s[x] for x in knot}) == 2 for knot in supports)]
    readings = []
    for size in (2, 3):
        for arity in combinations(range(width), size):
            values = tuple(int(len({s[x] for x in arity}) == 1) for s in states)
            if len(set(values)) != 2:
                continue
            for knot in supports:
                fixes = defaultdict(set)
                for state, value in zip(states, values):
                    fixes[tuple(state[x] for x in knot)].add(value)
                if not any(len(fix) == 2 for fix in fixes.values()):
                    break
            else:
                readings.append((arity, values))
    assert carriers == [c for c, _ in readings]
    count = 0
    for triple in combinations(readings, 3):
        if len(set().union(*(set(c) for c, _ in triple))) < sum(len(c) for c, _ in triple):
            continue
        words = set(zip(*(values for _, values in triple)))
        if len(words) < 8 and all(len({(w[i], w[j]) for w in words}) == 4
                                  for i, j in combinations(range(3), 2)):
            count += 1
    return count


def read_system(n, index, archived, links):
    file, line, row = archived
    start = time.perf_counter()
    supports = supports_from_links(n, links)
    width, allowed, states, violations = stage_states(supports)
    carriers, yes, strict, state_yes = reading_tables(width, allowed, supports)
    readiness = time.perf_counter()
    missing_histogram, single_words, strict_bonds, clauses = bond_census(carriers, yes, strict, state_yes)
    bonds_ready = time.perf_counter()
    assert n > 6 or sum(missing_histogram.values()) == brute_small(width, supports, carriers)
    boxes = [named_box(box, carriers) for box in boxes_from_clauses(carriers, clauses)]
    boxes_ready = time.perf_counter()
    single_violations = [states[violations == 1 << i] for i in range(n)]
    upper = [read_upper(box, allowed, single_violations) for box in boxes]
    strict_table = dict(zip(carriers, strict))
    strict_boxes = sum(all(strict_table[carrier] for pair in box for carrier, _ in pair) for box in boxes)
    computed = {"bonds": sum(missing_histogram.values()), "boxes": len(boxes), "boxes read": min(50, len(boxes))}
    if all(len(r["missing"]) == 1 for r in upper):
        computed["upper missing exactly one"] = computed["boxes read"]
    if all(len(r["laws_needed"]) == n for r in upper):
        computed["every knot needed"] = computed["boxes read"]
    errors = {name: {"recount": value, "archived": row[name]} for name, value in computed.items()
              if row[name] != value}
    witness = None
    if row["example"]:
        old_example, = row["example"]
        box = decode_box(old_example["box"])
        witness = read_upper(box, allowed, single_violations)
        if box_key(box) not in {box_key(b) for b in boxes}:
            errors["archived_example_is_a_box"] = False
        expected = {"upper missing": witness["missing"], "laws needed": witness["laws_needed"],
                    "reads a born distinction": False, "a birth needed": False}
        for name, value in expected.items():
            if old_example[name] != value:
                errors[f"archived_example_{name}"] = {"recount": value, "archived": old_example[name]}
    elif boxes:
        errors["missing_archived_example"] = True

    return {"knots": n, "archive_index": index, "file": file, "line": line, "links": row["links"],
            "distinction_links": [sorted(link) for link in links],
            "supports": supports, "distinctions": width, "allowed_states": 2 * len(allowed),
            "readings": len(carriers), "readings_using_every_place": sum(strict), "bonds": computed["bonds"],
            "bonds_by_absent_word_count": missing_histogram, "single_absent_words": single_words,
            "bonds_using_every_carrier_place": strict_bonds, "boxes": len(boxes),
            "boxes_using_every_carrier_place": strict_boxes,
            "archived_example": witness, "all_upper": upper, "archive_field_disagreements": errors,
            "seconds": {"setup": round(readiness - start, 4), "bond_count": round(bonds_ready - readiness, 4),
                        "box_count": round(boxes_ready - bonds_ready, 4),
                        "full_system": round(time.perf_counter() - start, 4)}}


def replay_comparison(systems):
    path = STUDY / "post" / "replay_box.json"
    cases = [(p, line, row) for p, line, row in sorted(archive_rows(12)) if row["example"]]
    replay = json.loads(path.read_text())
    assert len(replay) == len(cases)
    by_location = {(system["file"], system["line"]): system for system in systems if system["knots"] == 12}
    differences = []
    compared = 0
    for (file, line, _), saved in zip(cases, replay):
        if (file, line) not in by_location:
            continue
        system = by_location[file, line]
        witness = system["archived_example"]
        expected = {"bonds": system["bonds"], "missing": [[int(ch) for ch in w] for w in witness["missing"]],
                    "reported": witness["missing"], "knots needed": len(witness["laws_needed"])}
        compared += 1
        if saved != expected:
            differences.append({"file": file, "line": line, "recount": expected, "replay": saved})
    return {"total_saved": len(replay), "compared": compared, "disagreements": differences}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, choices=GRAPH_SIZES, action="append")
    parser.add_argument("--indices", type=int, nargs="+")
    parser.add_argument("--coverage-only", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--records", type=Path, help="Append each completed system to this new JSONL file.")
    args = parser.parse_args()
    tic = time.perf_counter()
    reports = []
    class_checks = {}
    if args.records:
        args.records.touch(exist_ok=False)
    if args.output and args.output.exists():
        parser.error("Output already exists.")
    for n in args.size or GRAPH_SIZES:
        rows = archive_rows(n)
        class_checks[n], numbering = class_coverage(n, rows)
        print(f"size={n}, classes={len(rows)}, BFS labelings={class_checks[n]['breadth_first_labeled_graphs']}", flush=True)
        if args.coverage_only:
            continue
        for i in args.indices if args.indices is not None else range(len(rows)):
            links = numbering.get(i, rows[i][2]["links"])
            stage = read_system(n, i, rows[i], links)
            reports.append(stage)
            if args.records:
                with args.records.open("a") as records:
                    records.write(json.dumps(stage) + "\n")
            print(f"  {i}: {stage['bonds']} bonds, {stage['boxes']} boxes, {stage['seconds']}", flush=True)
    summarize = {}
    for n in class_checks:
        subset = [r for r in reports if r["knots"] == n]
        summarize[n] = {"systems": len(subset), "systems_with_boxes": sum(r["boxes"] > 0 for r in subset),
                        "bonds": sum(r["bonds"] for r in subset), "boxes": sum(r["boxes"] for r in subset),
                        "strict_boxes": sum(r["boxes_using_every_carrier_place"] for r in subset),
                        "one_upper_word_missing": sum(len(u["missing"]) == 1 for r in subset for u in r["all_upper"]),
                        "every_law_needed": sum(len(u["laws_needed"]) == n for r in subset for u in r["all_upper"]),
                        "field_disagreements": {f"{r['file']}:{r['line']}": r["archive_field_disagreements"] for r in subset
                                                if r["archive_field_disagreements"]}}
    result = {"class_coverage": class_checks, "summary": summarize, "replay": replay_comparison(reports),
              "settings": {"single_process": True, "witness_rows_per_cell": WITNESS_TRIALS,
                           "witness_window": WITNESS_WINDOW, "state_permutation_seed": 61013,
                           "complement_representatives": True,
                           "numbering": "A distinction's label is its zero-based index in that row's distinction_links.",
                           "upper_words": "Counts in lexicographic order 000 through 111.",
                           "knots": "Deletion counts indexed by supports in that row."},
              "raw_file_digests": {str(p.relative_to(STUDY)): sha256(p.read_bytes()).hexdigest()
                                   for p in sorted((STUDY / "out").glob("cubic_*.jsonl"))} |
                                  {"post/replay_box.json": sha256((STUDY / "post" / "replay_box.json").read_bytes()).hexdigest()},
              "resources": {"seconds": round(time.perf_counter() - tic, 3),
                            "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
              "systems_file": args.records.name if args.records else None}
    if not args.records:
        result["systems"] = reports
    print(json.dumps({k: v for k, v in result.items() if k not in ("systems", "raw_file_digests")}, indent=2), flush=True)
    if args.output:
        args.output.write_text(json.dumps(result, indent=1) + "\n")


if __name__ == "__main__":
    main()
