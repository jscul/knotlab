"""Follow a still-loose alternative input of the six-place site at arbitrary depth."""

from collections import Counter, deque
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import chain, permutations, product
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
PROOFS = HERE.parents[1]
path, = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001J").glob("*/frontier.py")
spec = spec_from_file_location("minimum_width_frontier", path)
previous = module_from_spec(spec)
sys.modules[spec.name] = previous
spec.loader.exec_module(previous)
old = previous.old


def prefixes():
    """Represent every pre-exception frontier allowed by the predecessor."""
    records = {}
    queue = deque()
    for rows in previous.initial_histories():
        state = previous.literal_snapshot(rows)[0]
        if state not in records:
            records[state] = rows
            queue.append(state)
    while queue:
        state = queue.popleft()
        rows = records[state]
        reconstructed, active, loose = previous.literal_snapshot(rows)
        assert state == reconstructed
        allowed = old.verify_literal_moves(rows, state, active, loose)
        for parents in sorted(allowed):
            if len(parents) < 2:
                continue
            child = previous.step(state, parents, 2)
            if child not in records:
                physical = tuple(active[i] for i in parents)
                records[child] = previous.advance(rows, physical, 2)
                queue.append(child)
    assert len(records) == 1118
    return records


@cache
def vertex_orbits(front):
    """Orbits of the live sites under every automorphism of the particular frontier."""
    groups = {}
    for site, count in enumerate(front.loose):
        memberships = sorted(group.bit_count() for group in front.retired if group & (1 << site))
        color = (count, front.adjacent[site].bit_count(), tuple(memberships))
        groups.setdefault(color, []).append(site)
    least = list(range(len(front.loose)))
    for blocks in product(*(permutations(group) for group in groups.values())):
        source = tuple(chain.from_iterable(groups.values()))
        target = list(range(len(front.loose)))
        for i, j in zip(source, chain.from_iterable(blocks)):
            target[i] = j
        if front.restrict(tuple(target)) == front:
            for i, image in enumerate(target):
                least[i] = min(least[i], image)
    return tuple(least)


def add(rows, operands, outputs):
    state = dict(enumerate(rows))
    assert old.original_rule().legal_local_move(state, operands, old.FRESH_FOR_PARENT_TEST)
    width = 1 + max(map(max, rows))
    return (*rows, (*operands, *range(width, width + outputs)))


def tagged_state(rows, holder):
    front, active, loose = previous.literal_snapshot(rows)
    return (front, vertex_orbits(front)[active.index(holder)]), active, loose


def classify(role):
    origins = Counter()
    representatives = {}
    queue = deque()

    def register(prior_shrinks, rows, consumed, spare, holder, birth):
        marked, _, _ = tagged_state(rows, holder)
        key = (prior_shrinks, *marked)
        if key not in representatives:
            representatives[key] = (rows, consumed, spare, holder, birth)
            queue.append(key)

    if role == "input":
        for front, rows in prefixes().items():
            _, active, loose = previous.literal_snapshot(rows)
            birth = len(rows)
            for parents in old.possible_parents(front):
                if len(parents) != 3:
                    continue
                sites = [active[i] for i in parents]
                consumed = tuple(min(loose[site]) for site in sites)
                new_rows = add(rows, consumed, 3)
                for selected, holder in zip(consumed, sites):
                    alternatives = sorted(set(loose[holder]) - {selected})
                    if alternatives:
                        shrinks = 7 - sum(front.loose)
                        origins[shrinks] += 1
                        register(shrinks, new_rows, selected, alternatives[0], holder, birth)

    else:
        # Choose any first or subsequent use of an output from the exceptional holder.
        # The closure marks that holder until its last output is consumed.
        import closure
        _, records, _, _, _ = closure.explore()
        for state, (rows, high) in records.items():
            if high is None or state.high_holder == closure.NO_LIVE_MARKER:
                continue
            names, loose, allowed = closure.literal_options(rows, state, high)
            for parents in sorted(allowed):
                if len(parents) < 2 or state.high_holder not in parents:
                    continue
                taken = tuple(min(loose[names[i]]) for i in parents)
                old_high_bit = min(loose[high])
                child = add(rows, taken, 2)
                holder = len(rows)
                spare = max(child[-1])
                origins[state.prior_shrinks] += 1
                register(state.prior_shrinks, child, old_high_bit, spare, holder, high)

    sizes, positives, moves = Counter(), Counter(), Counter()
    literal = {}
    positive_representatives = []
    while queue:
        key = queue.popleft()
        prior_shrinks, state, tagged_index = key
        rows, consumed, spare, holder, birth = representatives[key]
        (check, index), active, loose = tagged_state(rows, holder)
        assert (check, index) == (state, tagged_index) and spare in loose[holder]
        allowed = old.verify_literal_moves(rows, state, active, loose)
        total = 7 - sum(state.loose)
        grade = (prior_shrinks, total)
        sizes[grade] += 1
        permitted = [parents for parents in sorted(allowed) if len(parents) == 3 and active.index(holder) in parents]
        if permitted:
            positives[grade] += 1
            parents = permitted[0]
            triple = sorted(spare if active[i] == holder else min(loose[active[i]]) for i in parents)
            candidate = dict(rows=rows, consumed=consumed, spare=spare, birth_index=birth,
                             junctions=len(rows), width=1+max(map(max, rows)), legal_mark=triple)
            positive_representatives.append(candidate)
            if grade not in literal or candidate["width"] < literal[grade]["width"]:
                literal[grade] = candidate
        for parents in sorted(allowed):
            if len(parents) < 2:
                continue
            sites = [active[i] for i in parents]
            if holder in sites and len(loose[holder]) == 1:
                continue
            operands = tuple(min(bit for bit in loose[site] if bit != spare) for site in sites)
            child = add(rows, operands, 2)
            register(prior_shrinks, child, consumed, spare, holder, birth)
            moves[grade] += 1

    thresholds = distance_checks(positive_representatives)
    return {"representative_distance_checks": thresholds, "eligible_starts_by_previous_shrinks": dict(sorted(origins.items())),
            "reachable_tagged_records": len(representatives),
            "classes": [{"shrinks_at_birth": a, "shrinks_total": b, "states": count,
                         "transitions_preserving_spare": moves[a,b], "with_legal_spare": positives[a,b],
                         "example": literal.get((a,b))}
                        for (a,b), count in sorted(sizes.items())]}


def distance_checks(cases):
    """Measure the two affected rows through D=5, retaining an exact collision if any."""
    path, = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001H").glob("*/check_reader.py")
    spec = spec_from_file_location("short_pair_measure", path)
    engine = module_from_spec(spec)
    spec.loader.exec_module(engine)
    summary = Counter()
    first = {}
    for case in cases:
        rows, width, a, b = case["rows"], case["width"], case["consumed"], case["spare"]
        eligible = engine.oracle.permissions(rows)
        mark = tuple(case["legal_mark"])
        alternate = tuple(sorted(a if x == b else x for x in mark))
        assert mark in eligible and alternate not in eligible
        table, _, _ = engine.measured_short_bonds(rows, width, 6)
        diffs = {}
        for k in (5, 6):
            diffs[k] = [x for x in range(width) if x not in (a, b)
                        and min(table.get(tuple(sorted((a, x))), 7), k + 1)
                        != min(table.get(tuple(sorted((b, x))), 7), k + 1)]
        score = "match_at_five" if not diffs[6] else "match_at_four" if not diffs[5] else "separate_by_four"
        summary[score] += 1
        if score not in first or width < first[score]["width"]:
            first[score] = {**case, "forbidden_image": alternate,
                            "entries_differing_at_D4": 2 * len(diffs[5]),
                            "entries_differing_at_D5": 2 * len(diffs[6])}
    return {"counts": dict(sorted(summary.items())), "examples": first}


if __name__ == "__main__":
    print(json.dumps({name: classify(name) for name in ("input", "output")}, indent=2))
