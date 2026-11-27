"""Rerun the exact carried readings, their fixing and deletion controls."""

import argparse
from collections import Counter
from contextlib import redirect_stdout
from dataclasses import asdict
import io
from itertools import product
import json
from pathlib import Path
import sys
import time

from pysat.solvers import Solver

from growth_rule import advance, loose


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from knotlab.cli import main as canonical_check


def words(size):
    return tuple("".join(bits) for bits in product("01", repeat=size))


def signed(names, word):
    return [x if bit == "1" else -x for x, bit in zip(names, word, strict=True)]


def canonical(words_seen, arity):
    missing = sorted(set(words(arity)) - set(words_seen))
    if not words_seen or not missing:
        return None
    names = [f"g{i}" for i in range(arity)]
    clauses = ";".join(" ".join(("~" if bit == "1" else "") + n
                                for n, bit in zip(names, word)) for word in missing)
    capture = io.StringIO()
    with redirect_stdout(capture):
        rc = canonical_check(["check", "--cnf", clauses, "--loops", *names[:-1],
                              "--contact", names[-1], "--json"])
    doc = json.loads(capture.getvalue())
    assert rc == 0 and set(doc["allowed"]) == set(words_seen)
    return {key: doc[key] for key in ("binding", "loss_on_erasure", "coexistence", "is_knot")}


class Table:
    """Each bit is an AND of conditions of the form 'these distinctions all agree'."""

    def __init__(self, supports, readers, omit=None):
        self.supports = supports
        self.readers = readers
        self.count = max(x for group in supports for x in group) + 1
        next_name = self.count + 1
        clauses = []
        for i, support in enumerate(supports):
            if i != omit:
                names = [x + 1 for x in support]
                clauses.extend((names, [-n for n in names]))
        self.outputs = []
        for reader in readers:
            partial = []
            for block in reader:
                equal = next_name
                next_name += 1
                names = [x + 1 for x in block]
                for other in names[1:]:
                    clauses.extend(([-equal, -names[0], other], [-equal, names[0], -other]))
                clauses.extend(([equal] + names, [equal] + [-n for n in names]))
                partial.append(equal)
            bit = next_name
            next_name += 1
            clauses.extend([[-bit, item] for item in partial])
            clauses.append([bit] + [-item for item in partial])
            self.outputs.append(bit)
        self.solver = Solver(bootstrap_with=clauses)

    def image(self, held=(), witness=False):
        image = {}
        for word in words(len(self.outputs)):
            if self.solver.solve(assumptions=list(held) + signed(self.outputs, word)):
                if witness:
                    true_vars = {n for n in self.solver.get_model() if n > 0}
                    state = "".join("1" if i + 1 in true_vars else "0" for i in range(self.count))
                else:
                    state = None
                image[word] = state
        return image


def literal(supports, readers):
    count = max(x for k in supports for x in k) + 1
    masks = [sum(1 << x for x in k) for k in supports]
    outputs = {}
    for s in range(1 << count):
        if all((s & mask) not in (0, mask) for mask in masks):
            outputs[s] = "".join(
                str(int(all(len({(s >> x) & 1 for x in pieces}) == 1 for pieces in reader)))
                for reader in readers
            )
    changes = [0] * len(readers)
    remaining = set(outputs)
    classes = []
    while remaining:
        start = remaining.pop()
        size = 0
        pending = [start]
        while pending:
            state = pending.pop()
            size += 1
            for place in range(count):
                other = state ^ (1 << place)
                if other in remaining:
                    pending.append(other)
                    remaining.remove(other)
                if other > state and other in outputs:
                    for i, (before, after) in enumerate(zip(outputs[state], outputs[other])):
                        changes[i] += before != after
        classes.append(size)
    only_loose = loose(supports)
    return {
        "allowed_states": len(outputs), "states_by_word": dict(sorted(Counter(outputs.values()).items())),
        "single_change_classes_sizes": sorted(classes), "single_changes_altering_each_value": changes,
        "loose_distinctions": only_loose,
        "distinct_loose_words": len({tuple((s >> x) & 1 for x in only_loose) for s in outputs}),
    }


def record(supports, readers, *, direct=False, fixing=True):
    carries = [{x for block in reader for x in block} for reader in readers]
    assert sum(map(len, carries)) == len(set().union(*carries))
    bits = len(readers)
    table = Table(supports, readers)
    image = table.image(witness=True)
    output = {"supports": supports, "carriers_all_equal_within_each_list": readers,
              "carrier_sets_disjoint": True, "witnesses_in_distinction_order": image,
              "missing": sorted(set(words(bits)) - set(image)),
              "delete_one_value_image_sizes": [len({w[:i] + w[i + 1:] for w in image}) for i in range(bits)],
              "canonical_check": canonical(image, bits)}
    if direct:
        output["literal"] = literal(supports, readers)
        assert set(output["literal"]["states_by_word"]) == set(image)
    if fixing:
        fixed = []
        for support in supports:
            local = {}
            for read in words(len(support)):
                reached = table.image(signed([x + 1 for x in support], read))
                if reached:
                    local[read] = tuple(reached)
            fixed.append({
                "feasible_readings": len(local),
                "fixed_image_size_counts": dict(sorted(Counter(map(len, local.values())).items())),
                "holds_all_words_if_fixed_to": [r for r, seen in local.items() if len(seen) == len(image)],
                "readings_leaving_both_values_for_each_carrier": [
                    sum(len({w[i] for w in seen}) == 2 for seen in local.values()) for i in range(bits)
                ],
            })
        output["fix_each_knot"] = fixed
        output["whole_valuation_of_any_one_knot_determines_a_carrier"] = any(
            0 in row["readings_leaving_both_values_for_each_carrier"] for row in fixed
        )
    table.solver.delete()
    deletion = []
    for i in range(len(supports)):
        without = Table(supports, readers, omit=i)
        witnessed = without.image(witness=True)
        without.solver.delete()
        deletion.append({"knot": i, "words": len(witnessed), "new_words_with_state":
                         {w: s for w, s in witnessed.items() if w not in image}})
    output["remove_each_law_keeping_all_distinctions"] = deletion
    return output


def archive_match(source):
    roster = json.loads((ROOT / "research/FORBID-EDITS-20261126-001/starts.json").read_text())
    expected = [3, [[0, 1, 1], [0, 2, 1], [1, 2, 1]], [1, 1, 1]]
    hits = [i for i, entry in enumerate(roster) if entry == expected]
    assert len(hits) == 1
    index = hits[0]
    archived = json.loads((HERE.parent / "census.jsonl").read_text().splitlines()[index])
    assert archived["start"] == f"census {index}"
    names = {0: 1, 1: 0, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
    mapped = [sorted(names[x] for x in k) for k in source]
    by_holder = [[] for _ in range(3)]
    for x, (i, j, number) in enumerate(expected[1]):
        assert number == 1
        by_holder[i].append(x)
        by_holder[j].append(x)
    for i, support in enumerate(by_holder):
        support.append(i + 3)
    assert by_holder == mapped
    return {"zero_based_ordinal_in_full_census": index, "archived_start": expected,
            "map_from_display_to_archived_identities": names, "supports_in_archived_numbering": mapped,
            "archived_record": archived}


def first_birth(rounds):
    source = ((0, 1, 3), (1, 2, 4), (2, 0, 5))
    old = (((1, 5),), ((2, 3),), ((0, 4),))
    born = (((1, 5),), ((2, 3),), ((0, 4, 6),))
    stage = advance(source)
    assert stage.status == "funded" and stage.supports[-1] == (3, 4, 5, 6)
    out = {"archive": archive_match(source), "source": record(source, old, direct=True),
           "births": [asdict(b) for b in stage.births],
           "first_round_old_reading": record(stage.supports, old, direct=True),
           "with_birth_reading": [], "meeting_selected_choices": []}
    # Pair every source distinction with the loose distinction of the only
    # source knot that does not hold it. Add the fresh one to any one pair.
    opposite = []
    old_loose = set(loose(source))
    for shared in sorted(set(range(6)) - old_loose):
        other, = [k for k in source if shared not in k]
        only, = old_loose & set(other)
        opposite.append((shared, only))
    for selected in range(3):
        family = tuple(((p + (6,) if j == selected else p),) for j, p in enumerate(opposite))
        t = Table(stage.supports, family)
        out["meeting_selected_choices"].append(
            {"carriers": family, "missing": sorted(set(words(3)) - set(t.image()))})
        t.solver.delete()
    for r in range(1, rounds + 1):
        out["with_birth_reading"].append({
            "round": r, **record(stage.supports, born, direct=(r <= 3), fixing=(r <= 3))
        })
        if r < rounds:
            stage = advance(stage.supports)
            assert stage.status == "funded"
    return out


def nine_ring(rounds):
    size = 9
    source = tuple((i, (i + 1) % size, size + i, 2 * size + i) for i in range(size))

    def grouped(start, direction):
        groups = []
        for b in range(3):
            block = []
            for shift in range(3):
                i = (start + direction * (3 * b + shift)) % size
                shared = i if direction == 1 else (i + 1) % size
                block.append((shared, size + i, 2 * size + i))
            groups.append(tuple(block))
        return tuple(groups)

    readers = grouped(0, 1)
    baseline = record(source, readers)
    assert baseline["missing"] == ["111"]
    out = {"source": baseline, "three_local_preparations": [], "choices_up_to_output_order": []}
    for i, reader in enumerate(readers):
        part = source[3*i:3*i + 3]
        tab = Table(part, (reader,))
        out["three_local_preparations"].append({"source_knots": list(range(3*i, 3*i + 3)),
                                                "words_in_isolation": sorted(tab.image())})
        tab.solver.delete()
    for start, direction in product(range(3), (1, -1)):
        family = grouped(start, direction)
        tab = Table(source, family)
        out["choices_up_to_output_order"].append({"start": start, "direction": direction,
                                                  "missing": sorted(set(words(3)) - set(tab.image()))})
        tab.solver.delete()
    out["ordinary_growth"] = []
    stage = source
    for r in range(1, rounds + 1):
        step = advance(stage)
        if step.status != "funded":
            out["ordinary_growth"].append({"attempted_round": r, "status": step.status})
            break
        stage = step.supports
        out["ordinary_growth"].append({
            "round": r, "births": [asdict(b) for b in step.births], **record(stage, readers, fixing=r == 1),
        })
    return out


def seven_ring(limit):
    size = 7
    source = tuple((i, (i + 1) % size, size + i) for i in range(size))
    opposites = tuple((size + i, (i + 3) % size) for i in range(size))
    readings = tuple((p,) for p in opposites)
    # Fixing any one knot is the stronger test. Search every partition into
    # three groups of sizes two, two and three, up to the order of the groups.
    from carrier_search import partitions

    singles = record(source, readings, direct=True)
    assert singles["missing"] == ["1111111"]
    hist = Counter()
    best_value = None
    best = None
    for ordinal, partition in enumerate(partitions(size)):
        if limit is not None and ordinal >= limit:
            break
        family = tuple(tuple(opposites[j] for j in group) for group in partition)
        tab = Table(source, family)
        sizes = Counter()
        for local in source:
            for pattern in words(3):
                if len(set(pattern)) == 2:
                    held = signed([x + 1 for x in local], pattern)
                    sizes[len(tab.image(held))] += 1
        tab.solver.delete()
        hist[sizes[7]] += 1
        value = (sizes[7], min(sizes))
        if best_value is None or best_value < value:
            best_value = value
            best = {"partition": partition, "sizes": dict(sizes), "family": family}
    best_case = None
    if best is not None:
        best_case = dict(best, evidence=record(source, best["family"], direct=True))
    growth = advance(source)
    return {"source": singles, "growth_status": growth.status, "group_partitions": sum(hist.values()),
            "count_by_number_of_the_42_feasible_fixes_retaining_all_seven": dict(sorted(hist.items())),
            "best_case": best_case}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("birth", "nine", "seven"))
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--limit-partitions", type=int)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    if args.case == "birth":
        out = first_birth(args.rounds)
    elif args.case == "nine":
        out = nine_ring(args.rounds)
    else:
        out = seven_ring(args.limit_partitions)
    out["elapsed_seconds"] = time.monotonic() - started
    if args.out:
        args.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"case": args.case, "elapsed_seconds": out["elapsed_seconds"],
                      "source_missing": out["source"]["missing"]}))
