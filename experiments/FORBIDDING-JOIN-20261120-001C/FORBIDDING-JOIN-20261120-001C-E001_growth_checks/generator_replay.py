"""Rebuild the seven-knot source from its literal holdings under the frozen count rules."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, product
import json
from pathlib import Path


MEETINGS = ((0, 1), (0, 4), (1, 4), (2, 4), (2, 6), (3, 4), (3, 5), (5, 6))
OPEN_COUNTS = (3, 0, 3, 3, 3, 2, 2)
ARCHIVED_HOLDINGS = ((7, 25), (15, 50), (27, 92), (46, 167), (78, 307))
# Two returns of the 25-distinction witness (GENERATORS source.md, lines 39–56).
PERIOD = (4, 0, 2, 5, 4, 0, 3, 6)
LAWS = ("parity", "nae")
VARIANTS = ("ordinary", "one_fewer", "only_floor")


def source(repeats):
    rows = [[] for _ in OPEN_COUNTS]
    shared = MEETINGS + repeats
    for distinction, (a, b) in enumerate(shared):
        rows[a].append(distinction)
        rows[b].append(distinction)
    next_name = len(shared)
    for row, count in zip(rows, OPEN_COUNTS, strict=True):
        row.extend(range(next_name, next_name + count))
        next_name += count
    return tuple(map(tuple, rows))


def holdings(rows):
    owners = defaultdict(list)
    neighbors = [set() for _ in rows]
    loose = defaultdict(list)
    for knot, row in enumerate(rows):
        assert len(row) >= 3 and len(set(row)) == len(row)
        for name in row:
            owners[name].append(knot)
    for name, sites in sorted(owners.items()):
        if len(sites) == 1:
            loose[sites[0]].append(name)
        else:
            a, b = sites
            neighbors[a].add(b)
            neighbors[b].add(a)
    return owners, neighbors, dict(sorted(loose.items()))


def maximal_complete_sets(adjacent, group, eligible, excluded):
    if not eligible and not excluded:
        yield group
        return
    pivot = max(eligible | excluded, key=lambda v: len(adjacent[v] & eligible))
    for v in sorted(eligible - adjacent[pivot]):
        yield from maximal_complete_sets(adjacent, group | {v}, eligible & adjacent[v], excluded & adjacent[v])
        eligible.remove(v)
        excluded.add(v)


def groups(blocks, live):
    witnesses = [set(block) & live for block in blocks]
    adjacent = {v: set() for v in live}
    for block in witnesses:
        for a, b in combinations(sorted(block), 2):
            adjacent[a].add(b)
            adjacent[b].add(a)
    larger = [tuple(sorted(group)) for group in maximal_complete_sets(adjacent, set(), set(live), set())
              if len(group) >= 3 and not any(group <= block for block in witnesses)]
    covered = {pair for group in larger for pair in combinations(group, 2)}
    pairs = [(a, b) for a in sorted(live) for b in sorted(adjacent[a]) if a < b and (a, b) not in covered]
    return sorted(larger) + pairs


def allowed(values, law):
    if law == "parity":
        return sum(values) % 2 == 0
    return 0 < sum(values) < len(values)


def fresh_count(ordinary, parents, variant):
    floor = max(0, 3 - parents)
    if variant == "one_fewer":
        return min(ordinary, max(floor, ordinary - 1))
    if variant == "only_floor":
        return min(ordinary, floor)
    return ordinary


def plan(rows, variant):
    owners, neighbors, loose = holdings(rows)
    if not loose:
        return {"status": "closed", "births": []}
    parents = groups(neighbors, set(loose))
    used = Counter(v for group in parents for v in group)
    shortages = [{"parent": v, "available": len(names), "demand": used[v], "deficit": used[v] - len(names)}
                 for v, names in loose.items() if used[v] > len(names)]
    if shortages:
        return {"status": "permanent_stall", "proposed_groups": parents, "strict_shortages": shortages, "births": []}
    parents.extend((v,) for v, names in loose.items() for _ in range(len(names) - used[v]))
    # A second private opening lets any proposed old input be set and its holder
    # repaired for either law, leaving all other constraints untouched.
    assert all(len(loose[v]) >= 2 for group in parents for v in group)
    child_witnesses = defaultdict(set)
    for child, group in enumerate(parents, len(rows)):
        for v in group:
            child_witnesses[v].add(child)
    following = groups(child_witnesses.values(), set(range(len(rows), len(rows) + len(parents))))
    demand = Counter(v for group in following for v in group)
    available = {v: iter(names) for v, names in loose.items()}
    next_name = max(owners) + 1
    births = []
    for child, group in enumerate(parents, len(rows)):
        p, d = len(group), demand[child]
        q = max(d, 3 - p, 1)
        f = fresh_count(q, p, variant)
        assert f > 0  # This specimen never reaches a zero-fresh funded proposal.
        inputs = tuple(next(available[v]) for v in group)
        fresh = tuple(range(next_name, next_name + f))
        next_name += f
        births.append(dict(knot=child, parents=group, inputs=inputs, fresh=fresh, p=p, D=d, q=q, f=f,
                           pre_birth_projection_size=2**p, implied=False, strict_fresh_shortage=max(0, d - f)))
    assert all(next(pool, None) is None for pool in available.values())
    return {"status": "extend", "births": births, "following_proposals_with_all_children_live": following}


def source_states(rows, law):
    """Factor completions and exact displayed projections over shared distinctions."""
    owners, _, loose = holdings(rows)
    shared = [d for d, knots in owners.items() if len(knots) == 2]
    completions = Counter()
    projections = [set() for _ in rows]
    for shared_values in product((0, 1), repeat=len(shared)):
        pins = dict(zip(shared, shared_values, strict=True))
        good = []
        for v, row in enumerate(rows):
            words = []
            for values in product((0, 1), repeat=len(loose.get(v, ()))):
                partial = pins | dict(zip(loose.get(v, ()), values, strict=True))
                word = tuple(partial[d] for d in row)
                if allowed(word, law):
                    words.append(word)
            good.append(words)
        if all(good):
            local_modes = []
            for v, row in enumerate(rows):
                if v in loose:
                    bits = [pins[d] for d in row if d in pins]
                    local_modes.append(bits[0] if len(set(bits)) == 1 else None)
                projections[v].update(good[v])
            # Each mode records whether this holder forbids all its loose bits
            # taking one common value when the already shared bits are fixed.
            completions[tuple(local_modes)] += 1
    certificate = []
    for row, observed in zip(rows, projections, strict=True):
        expected = {word for word in product((0, 1), repeat=len(row)) if allowed(word, law)}
        assert observed == expected
        omissions = [len({word[:i] + word[i+1:] for word in observed}) for i in range(len(row))]
        assert omissions == [2**(len(row) - 1)] * len(row) and 0 < len(observed) < 2**len(row)
        certificate.append(dict(arity=len(row), projection_size=len(observed), omission_sizes=omissions))
    return loose, completions, certificate


def nae_weighted_count(loose, modes, births=()):
    """Contract the small source and optional first layer by inclusion–exclusion."""
    live = tuple(loose)
    used = {d for birth in births for d in birth["inputs"]}
    independent = {d for names in loose.values() for d in names} - used
    total = 0
    for modes_by_knot, multiplicity in modes.items():
        exclusions = [(v, bit) for v, bit in zip(live, modes_by_knot, strict=True) if bit is not None]
        subtotal = 0
        for choice in product((0, 1), repeat=len(exclusions)):
            pins = {d: bit for (v, bit), take in zip(exclusions, choice, strict=True) if take for d in loose[v]}
            mass = 2**len(independent - pins.keys())
            for birth in births:
                local = [((pins[d],) if d in pins else (0, 1)) for d in birth["inputs"]]
                mass *= sum(2**birth["f"] - int(len(set(values)) == 1) for values in product(*local))
            subtotal += (-1)**sum(choice) * mass
        total += multiplicity * subtotal
    return total


def replay(initial, law, variant, increments):
    loose, modes, source_projections = source_states(initial, law)
    if law == "parity":
        # The shared incidence is connected and at least one opening makes the
        # rows independent. Each subsequent positive birth has a private column.
        count = 2**(len(holdings(initial)[0]) - len(initial))
    else:
        count = nae_weighted_count(loose, modes)
    assert count > 0
    source_count = count
    result = {"source_allowed_assignments": count, "source_projected_knot_checks": source_projections,
              "holdings": [(len(initial), len(holdings(initial)[0]))], "rounds": []}
    rows = initial
    for age in range(1, increments + 1):
        turn = plan(rows, variant)
        turn["attempted_cluster_size"] = age + 1
        result["rounds"].append(turn)
        if turn["status"] != "extend":
            turn["retained_allowed_assignments"] = count
            result["stop"] = turn["status"]
            break
        births = turn["births"]
        before = count
        if law == "parity":
            count *= 2**sum(b["f"] - 1 for b in births)
        elif age == 1:
            count = nae_weighted_count(loose, modes, births)
        else:
            count = None  # Exact per-assignment fibers are certified below.
        roster = Counter((b["p"], b["f"]) for b in births)
        turn["survival"] = dict(preceding_allowed_assignments=before, preceding_survivors=before,
                                new_allowed_assignments=count, retained_fraction="1", literal_L_defined=True,
                                source_states_with_lifts=source_count,
                                inherited_support="all preceding allowed assignments",
                                full_displayed_projections_preserved=True,
                                fiber_factors_by_p_and_f=[dict(p=p, f=f, multiplicity=n)
                                                         for (p, f), n in sorted(roster.items())],
                                fiber_rule=("2^(f-1)" if law == "parity" else "2^f - 1 if inputs all agree, else 2^f"))
        rows += tuple(b["inputs"] + b["fresh"] for b in births)
        result["holdings"].append((len(rows), len(holdings(rows)[0])))
    else:
        result["stop"] = "checked_prefix"
    return result


def canonical(word):
    return min(word, word[::-1])


def phases(size):
    return [tuple(PERIOD[(start + i) % len(PERIOD)] for i in range(size)) for start in range(len(PERIOD))]


def source_member(word):
    return any(not any(mark in word[i:i+k] and word[i:i+k] == word[i+k:i+2*k]
                       for k in range(1, len(word)//2 + 1) for i in range(len(word) - 2*k + 1)) for mark in (2, 3))


def window_demand(word, blocks):
    size_by_pair = {}
    for block in blocks:
        for pair in combinations(sorted(block), 2):
            assert pair not in size_by_pair
            size_by_pair[pair] = len(block)
    meetings = [tuple(sorted(pair)) for pair in zip(word, word[1:])]
    assert all(any(a in block and b in block for block in blocks) for a, b in meetings)
    assert all(not any(set(triple) <= block for block in blocks) for triple in zip(word, word[1:], word[2:]))
    return sum(OPEN_COUNTS[v] for v in word) - sum(size_by_pair[pair] for pair in meetings)


def historical_packet(initial, baseline):
    _, neighbors, loose = holdings(initial)
    blocks = [adjacent & set(loose) for adjacent in neighbors]
    realized = {word: word[0] for word in map(canonical, phases(1))}
    witness = []
    for size, turn in enumerate(baseline["rounds"], 2):
        by_parents = {birth["parents"]: birth for birth in turn["births"] if birth["p"] == 2}
        current = {}
        for word in set(map(canonical, phases(size))):
            parents = tuple(sorted((realized[canonical(word[:-1])], realized[canonical(word[1:])])))
            birth = by_parents[parents]
            assert birth["f"] == window_demand(word, blocks)
            current[word] = birth["knot"]
        witness.append(dict(size=size, distinct_physical_windows=len(current)))
        realized = current
    proof_checks = []
    for size in (15, 16, 17):
        previous = set(map(canonical, phases(size - 1)))
        windows = phases(size)
        assert len(set(map(canonical, windows))) == len(PERIOD)
        assert all(source_member(word) == (size == 15) for word in windows)
        phase_records = []
        for i, word in enumerate(windows):
            parents = (canonical(word[:-1]), canonical(word[1:]))
            assert parents[0] != parents[1] and all(parent in previous for parent in parents)
            assert all(source_member(parent) == (size <= 16) for parent in parents)
            phase_records.append(dict(phase=i, word=word, parent_words=parents,
                                      predicted_ordinary_fresh=window_demand(word, blocks)))
        proof_checks.append(dict(size=size, all_phases_source=size == 15, phases=phase_records))
    return dict(period=PERIOD, release_size=16, physical_checks=witness, identified_window_checks=proof_checks,
                authority="Historical ordinary fixed-map theorem, with independent finite phase checks. No rival map used.")


def run():
    initial = source(((0, 1),))
    wide = source(((0, 1), (2, 4), (2, 6), (3, 5)))
    result = dict(frozen_commit="fd556bf96a", source_supports=initial, wide_control_supports=wide,
                  referee_holdings=ARCHIVED_HOLDINGS, laws={}, wide_ordinary={},
                  lift_weight_certificate=("Multiply the private factors within each round for a fixed preceding state. "
                                           "Every factor is positive. To weight a later state under literal L, give each "
                                           "start mass one and divide by its number of complete lifts to that stage."))
    for law in LAWS:
        arms = {variant: replay(initial, law, variant, 5) for variant in VARIANTS}
        ordinary = arms["ordinary"]
        assert tuple(ordinary["holdings"][:5]) == ARCHIVED_HOLDINGS
        assert ordinary["holdings"][5] == (134, 576)  # Last independently published increment in source.md.
        for variant in VARIANTS[1:]:
            trial = arms[variant]
            assert trial["stop"] == "permanent_stall" and len(trial["rounds"]) == 2
            assert all(b["f"] > 0 for b in trial["rounds"][0]["births"])
            fields = ("parents", "inputs", "p", "D", "q")
            for rival, control in zip(trial["rounds"][0]["births"], ordinary["rounds"][0]["births"], strict=True):
                assert all(rival[field] == control[field] for field in fields)
            assert trial["rounds"][1]["proposed_groups"] == ordinary["rounds"][0]["following_proposals_with_all_children_live"]
        assert arms["one_fewer"]["holdings"][1] != arms["only_floor"]["holdings"][1]
        ordinary["periodic_product"] = historical_packet(initial, ordinary)
        result["laws"][law] = arms
        wide_ordinary = replay(wide, law, "ordinary", 2)
        assert [len(t["births"]) for t in wide_ordinary["rounds"]] == [8, 12]
        result["wide_ordinary"][law] = wide_ordinary
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(run(), separators=(",", ":"), sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
