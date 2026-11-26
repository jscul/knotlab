"""Literal checks on the old ring parities and on the frozen seven-knot draw.

Run from the repository root with .venv/bin/python -B. Each new support is
regrown by the independent ordinary-round implementation in this folder.
"""

import argparse
import io
import json
import resource
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from functools import cache
from itertools import combinations
from pathlib import Path
from time import perf_counter

from growth import advance


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
PREVIOUS = RESEARCH / "LAYERS-20261126-001" / "referee-R1"
sys.path.insert(0, str(RESEARCH.parent / "tools"))
from knotlab.cli import main as canonical_check


def mask(ids):
    return sum(1 << place for place in ids)


def indices(word):
    while word:
        bit = word & -word
        yield bit.bit_length() - 1
        word ^= bit


def pivots(words):
    found = {}
    for word in words:
        while word:
            p = word.bit_length() - 1
            if p not in found:
                found[p] = word
                break
            word ^= found[p]
    return found


def kernel(equations, width):
    rows = pivots(equations)
    ordered = sorted(rows.items())
    for p in range(width):
        if p in rows:
            continue
        state = 1 << p
        for q, row in ordered:
            if (state & row).bit_count() % 2:
                state |= 1 << q
        yield state


def span(basis):
    values = [0]
    for word in basis:
        values += [v ^ word for v in values]
    return values


def restrict(word, places):
    return sum(((word >> place) & 1) << j for j, place in enumerate(places))


def observations(word, labels):
    return sum(((word & label).bit_count() % 2) << j for j, label in enumerate(labels))


def columns_of(stage):
    width = max(max(knot) for knot in stage) + 1
    columns = [0] * width
    for j, knot in enumerate(stage):
        for d in knot:
            columns[d] |= 1 << j
    assert all(s.bit_count() in (1, 2) for s in columns)
    return columns


def small_changes(columns):
    """Join disjoint increasing tuples with the same parity violations.

    Every size-w support has exactly one split after its first floor(w/2)
    places, including the empty prefix for size one. Repeated meetings and
    combinations of separate allowed changes are included without special cases.
    """
    places = range(len(columns))
    tables = {}
    for size in (0, 1, 2):
        table = defaultdict(list)
        for part in combinations(places, size):
            syndrome = 0
            for d in part:
                syndrome ^= columns[d]
            table[syndrome].append((part[-1] if part else -1, mask(part)))
        tables[size] = table

    result = []
    for size in range(1, 6):
        split = size // 2
        table = tables[split]
        for suffix in combinations(places, size - split):
            syndrome = 0
            for d in suffix:
                syndrome ^= columns[d]
            matching = table.get(syndrome, ())
            if matching:
                first = suffix[0]
                high = mask(suffix)
                result.extend(low | high for last, low in matching if last < first)
    return result


def through_each(moves):
    """Include every tie at the first size seen through each open distinction."""
    by_size = defaultdict(list)
    for change in moves:
        by_size[change.bit_count()].append(change)
    seen = 0
    chosen = []
    for changes in sorted(by_size):
        same_size = [change for change in by_size[changes] if change & ~seen]
        chosen.extend(same_size)
        for change in same_size:
            seen |= change
    return chosen, seen


def renumbered(rows):
    return [sorted(row) for row in rows]


@cache
def check_projection(width, allowed):
    names = [f"v{j}" for j in range(width)]
    clauses = []
    for value in range(1 << width):
        if value not in allowed:
            clauses.append(" ".join(("~" if (value >> j) & 1 else "") + name
                                    for j, name in enumerate(names)))
    captured = io.StringIO()
    args = ["check", "--cnf", ";".join(clauses), "--loops", *names[:-1],
            "--contact", names[-1], "--erasure", "forgetting", "--json"]
    with redirect_stdout(captured):
        assert canonical_check(args) == 0
    result = json.loads(captured.getvalue())
    return result["binding"], result["loss_on_erasure"], result["coexistence"]


def local_views(stage, rows, kernel_basis, width, labels):
    views = []
    passing = 0
    for i, knot in enumerate(stage):
        places = sorted(knot)
        here = pivots(restrict(word, places) for word in kernel_basis)
        allowed = tuple(sorted(span(here.values())))
        passing += all(check_projection(len(knot), allowed))
        invisible = kernel(rows + [1 << d for d in knot], width)
        images = {0: 0}
        for word in invisible:
            v = observations(word, labels)
            if v not in images:
                images.update({value ^ v: old ^ word for value, old in images.items()})
        views.append({"knot": i, "values_at_zero_observation": sorted(images),
                      "changes_proving_those_values": {v: list(indices(x))
                                                       for v, x in sorted(images.items()) if v}})
    return views, passing


def class_record(stage, rows, allowed_bits, moves, labels):
    local = []
    for knot in stage:
        places = sorted(knot)
        viewed_moves = (restrict(move, places) for move in moves)
        for on_knot in kernel(viewed_moves, len(knot)):
            local.append(mask(places[p] for p in indices(on_knot)))
    laws_rank = len(pivots(rows))
    local_bits = len(pivots(rows + local)) - laws_rank
    move_rank = len(pivots(moves))
    label_bits = allowed_bits - move_rank
    violations = Counter(observations(move, labels) for move in moves)
    return {
        "distinct_moves": len(moves), "move_sizes": dict(sorted(Counter(m.bit_count() for m in moves).items())),
        "move_rank": move_rank, "class_bits": label_bits, "single_knot_span": local_bits,
        "whole_held_modulo_single_knot_span": label_bits - local_bits,
        "changes_of_named_pair_on_moves": dict(sorted(violations.items())),
    }


def check_stage(stage, labels, literal=False):
    columns = columns_of(stage)
    width = len(columns)
    equations = [mask(k) for k in stage]
    allowed = list(kernel(equations, width))
    available = 0
    for word in allowed:
        available |= word
    small = small_changes(columns)
    short, covered = through_each(small)
    if literal:
        words = span(allowed)
        assert set(small) == {v for v in words if 1 <= v.bit_count() <= 5}
        exhaustive_short, exhaustive_covered = through_each(words[1:])
        assert exhaustive_covered == available
        if covered == available:
            assert set(short) == set(exhaustive_short)
        short = exhaustive_short
        pair_counts = dict(sorted(Counter(observations(w, labels) for w in words).items()))
    else:
        if covered != available:
            raise ValueError(f"bounded changes missed mobile distinctions {list(indices(available & ~covered))}")
        pair_counts = None
    shortset = set(short)
    smallset = set(small)
    pair_rank = len(pivots(observations(w, labels) for w in allowed))
    views, passing = local_views(stage, equations, allowed, width, labels)
    return {
        "knots": len(stage), "distinctions": width, "free_to_change": available.bit_count(),
        "allowed_rank": len(allowed), "passing_projected_knot_test": passing,
        "shortest": class_record(stage, equations, len(allowed), short, labels),
        "up_to_five": class_record(stage, equations, len(allowed), small, labels),
        "overlap_of_the_two_move_sets": len(smallset & shortset),
        "joint_value_rank": pair_rank, "states_per_joint_value": 1 << (len(allowed) - pair_rank),
        "literal_joint_counts": pair_counts, "reading_at_each_knot": views,
    }


def construct(n, meetings, loose):
    knots = [set() for _ in range(n)]
    for d, (a, b) in enumerate(meetings):
        knots[a].add(d)
        knots[b].add(d)
    d = len(meetings)
    for knot, count in zip(knots, loose, strict=True):
        knot.update(range(d, d + count))
        d += count
    return tuple(map(frozenset, knots))


def ring_meetings(n, offset):
    return [(offset + i, offset + (i + 1) % n) for i in range(n)]


def nine_knots(double):
    rings = ring_meetings(4, 0) + ring_meetings(4, 4)
    if double:
        meetings = [(0, 8), (0, 8), (4, 8), (4, 8)]
        loose = [2] * 8 + [0]
    else:
        meetings = [(0, 8), (2, 8), (4, 8)]
        loose = [2, 2, 2, 2, 3, 2, 2, 2, 0]
    return construct(9, rings + meetings, loose)


def seven_knots():
    # The 240th accepted seven-knot draw, distinguishable by its full incidence.
    pairs = [(0, 3), (0, 5), (1, 6), (1, 6), (2, 4),
             (2, 5), (3, 4), (3, 4), (5, 6), (5, 6)]
    return construct(7, pairs, [2, 2, 2, 1, 1, 0, 0])


def expand_case(stage, rounds, labels, literal=False):
    stages = []
    for t in range(rounds + 1):
        if t:
            stage, status, _ = advance(stage)
            assert status == "funded"
        row = check_stage(stage, labels, literal=literal)
        row.update(round=t, supports=renumbered(stage))
        stages.append(row)
    return stages


def replay(pilot):
    # Each pair uses original distinction names retained by growth.
    rings = [mask(range(4)), mask(range(4, 8))]
    unreadable = mask([0, 17])
    local_sum = mask([1, 5])
    names = [unreadable, unreadable ^ local_sum]
    if pilot:
        cases = {"double_meetings": expand_case(nine_knots(True), 0, rings)}
    else:
        cases = {"double_meetings": expand_case(nine_knots(True), 3, rings),
                 "single_meetings": expand_case(nine_knots(False), 1, rings),
                 "frozen_seven_knot_draw": expand_case(seven_knots(), 1, names, literal=True)}
    archive = json.loads((PREVIOUS / "moves_deep.json").read_text())
    other = next(c for c in archive["cases"] if c["pattern"] == "4_4_joins1_inside1_copies2_rings")
    assert renumbered(nine_knots(True)) == other["source_supports"]
    if not pilot:
        assert cases["double_meetings"][-1]["supports"] == other["last_stage_supports"]
        single = json.loads((PREVIOUS / "joint_check.json").read_text())
        assert cases["single_meetings"][0]["supports"] == single["source"]["supports"]
        assert cases["single_meetings"][1]["supports"] == single["grown"]["supports"]
        seven = json.loads((PREVIOUS / "witness.json").read_text())
        assert cases["frozen_seven_knot_draw"][0]["supports"] == seven["source"]
        assert cases["frozen_seven_knot_draw"][1]["supports"] == seven["grown"]["supports"]
    return {
        "weighting": "One prepared start per stated construction or identified draw.",
        "named_labels": {"double_meetings": [list(indices(x)) for x in rings],
                         "single_meetings": [list(indices(x)) for x in rings],
                         "frozen_seven_knot_draw": [list(indices(x)) for x in names]},
        "cases": cases,
        "incidence_compared_to_earlier_certificates": "sources and designated grown stages" if not pilot else "double-meeting source",
    }


if __name__ == "__main__":
    cap = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    start = perf_counter()
    result = replay(options.pilot)
    result["pilot"] = options.pilot
    result["seconds"] = round(perf_counter() - start, 6)
    result["peak_resident_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    options.output.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({"seconds": result["seconds"], "peak_resident_KiB": result["peak_resident_KiB"]}))
