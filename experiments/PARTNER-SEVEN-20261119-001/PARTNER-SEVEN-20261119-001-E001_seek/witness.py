"""Replay a six-place start reaching complete partnered growth."""

from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
import sys


ROOT = Path(__file__).resolve().parents[3]
LAW = "experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py"
REPLAY = "experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/verify.py"
PARTNERS = ((0, 1), (2, 3), (4, 5))
NONPARTNERS = tuple((u, v) for u, v in combinations(range(6), 2) if u // 2 != v // 2)
TRANSVERSALS = tuple(product(*PARTNERS))
TWO_MEMBER_BLOCKS = range(20, 32)
SEED = 20261119073
SAMPLES = 32


def import_file(name, path):
    spec = spec_from_file_location(name, ROOT / path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def supports(members, meetings, loose):
    rows = [[] for _ in range(members)]
    holders = list(meetings)
    holders.extend((u,) for u, count in enumerate(loose) for _ in range(count))
    for b, js in enumerate(holders):
        for j in js:
            rows[j].append(b)
    return rows


def start(matching):
    pair_index = {pair: i for i, pair in enumerate(NONPARTNERS)}
    meetings = [(j, pair_index[pair]) for j, triple in enumerate(TRANSVERSALS, 12)
                for pair in combinations(triple, 2)]
    pair_blocks = [(u, far) for u in range(6) for far in PARTNERS if u not in far]
    meetings.extend((j, pair_index[tuple(sorted((u, v)))])
                    for j, (u, far) in enumerate(pair_blocks, 20) for v in far)
    assert sorted(u for pair in matching for u in pair) == list(TWO_MEMBER_BLOCKS)
    meetings.extend(matching)
    return supports(32, meetings, [2] * 12)


def control_start(held):
    meetings = [(6 + j, u) for j, pair in enumerate(NONPARTNERS) for u in pair]
    meetings += [(j, j + 1) for j in range(6, 18, 2)]
    meetings.extend((18 + j, u) for j, triple in enumerate(held) for u in triple)
    loose = [4 - sum(u in triple for triple in held) for u in range(6)]
    return supports(18 + len(held), meetings, loose)


def quotient_checks(verifier, words, visible):
    """Dual equations surviving existential projection to visible names."""
    outside = {}
    inside = []
    for word in words:
        while unseen := word & ~visible:
            pivot = unseen.bit_length()
            if pivot not in outside:
                outside[pivot] = word
                break
            word ^= outside[pivot]
        else:
            inside.append(word)
    return verifier.linear_basis(inside)


def ordered(sets):
    return sorted(map(sorted, sets))


def roster(verifier, state):
    live = sorted(state.live)
    possible = {frozenset(b) for b in verifier.common_meeters(state.neighbors, state.live) if len(b) >= 2}
    blocks = verifier.maximal_sets(possible)
    candidates = {frozenset(pair) for b in blocks for pair in combinations(b, 2)}
    maximal = set()
    for size in range(len(live), 2, -1):
        for group in map(frozenset, combinations(live, size)):
            if all(frozenset(pair) in candidates for pair in combinations(group, 2)):
                if not any(group < other for other in maximal):
                    maximal.add(group)
    held = maximal & blocks
    free = maximal - held
    groups = free | {pair for pair in candidates if not any(pair <= g for g in free)}
    assert groups == verifier.groups(state.neighbors, state.live)
    return {
        "live": live,
        "loose_per_live": [sum(j == u for u in state.loose.values()) for j in live],
        "candidate_pair_count": len(candidates),
        "noncandidates": ordered(set(map(frozenset, combinations(live, 2))) - candidates),
        "maximal_blocks": ordered(blocks),
        "held_maximal_cliques": ordered(held),
        "next_groups": ordered(groups),
    }


def measure_stage(verifier, state):
    audit = verifier.start_audit(state)
    assert audit["census_open_legal"] and audit["meets_once"]
    width = len(state.labels)
    assert state.labels == tuple(range(width))
    rank = len(verifier.linear_basis(state.masks))
    assert rank == len(state.stars)
    # With one supported equation on each support, its projection is all even
    # assignments. Every one-name erasure is full and the zero state survives.
    assert all(set(quotient_checks(verifier, state.masks, word).values()) == {word}
               for word in state.masks)
    return {
        "junctions": len(state.stars),
        "distinctions": width,
        "arity_counts": dict(Counter(map(len, state.stars))),
        "rank": rank,
        "all_local_projections_even": True,
        "all_distinctions_unforced": not audit["forced_distinctions"],
        **roster(verifier, state),
    }


def replay(law, verifier, rows, depth):
    game = law.from_junctions(rows)
    state = verifier.Arrangement.parse(rows)
    records = [{"age": 0, **measure_stage(verifier, state), "supports": rows}]
    for age in range(1, depth + 1):
        step = game.step(law.gf2(law.F.fewest), None)
        assert step and step["new"] and not game.implied_mismatch
        new_rows = [sorted(support) for support in game.bits_of]
        new = verifier.Arrangement.parse(new_rows)
        births = verifier.round_replay(state, new)
        width = len(state.labels)
        assert quotient_checks(verifier, new.masks, (1 << width) - 1) == verifier.linear_basis(state.masks)
        assert all(sorted(set(row["taken"].values()) | set(row["fresh"])) == new_rows[j]
                   for j, row in enumerate(births, len(state.stars)))
        records.append({
            "age": age,
            **measure_stage(verifier, new),
            "supports": new_rows,
            "births": [{"junction": j, **birth} for j, birth in enumerate(births, len(state.stars))],
            "forgets_to_previous_relation": True,
        })
        state = new
    return records


def partnered(stage, order, opens, held, free):
    non = stage["noncandidates"]
    assert len(non) == order and sorted(j for pair in non for j in pair) == stage["live"]
    assert stage["loose_per_live"] == [opens] * (2 * order)
    transversals = set(map(frozenset, product(*non)))
    blocks = set(map(frozenset, stage["maximal_blocks"]))
    blocked = {t for t in transversals if any(t <= b for b in blocks)}
    assert len(blocked) == held
    groups = set(map(frozenset, stage["next_groups"]))
    assert groups == transversals - blocked and len(groups) == free
    demand = Counter(j for g in groups for j in g)
    assert set(demand) == set(stage["live"]) and all(d == opens for d in demand.values())
    return {"order": order, "held_transversals": held, "free_transversals": free,
            "outside_live_junctions": []}


def witnessed(law, verifier, rows, canonical_to_current):
    a, b, c, d = stages = replay(law, verifier, rows, depth=3)
    assert [(s["junctions"], s["distinctions"]) for s in stages] == [(32, 78), (38, 102), (46, 142), (56, 262)]
    assert a["arity_counts"] == {3: 20, 6: 12}
    assert a["live"] == sorted(canonical_to_current[j] for j in range(12))
    assert a["loose_per_live"] == [2] * 12
    expected = [frozenset(canonical_to_current[j] for j, pair in enumerate(NONPARTNERS) if u in pair)
                for u in range(6)]
    blocked = [frozenset(canonical_to_current[NONPARTNERS.index(pair)] for pair in combinations(t, 2))
               for t in TRANSVERSALS]
    assert a["held_maximal_cliques"] == ordered(blocked)
    assert a["next_groups"] == ordered(expected)
    for s, count, parents, fresh in ((b, 6, 4, 4), (c, 8, 3, 5), (d, 10, 4, 12)):
        assert len(s["births"]) == count
        assert all((len(q["taken"]), len(q["fresh"]), q["demand"], q["implied"]) ==
                   (parents, fresh, fresh, False) for q in s["births"])
    birth_by_parents = {frozenset(q["taken"]): q["junction"] for q in b["births"]}
    reached = [birth_by_parents[s] for s in expected]
    assert b["live"] == sorted(reached)
    assert b["noncandidates"] == ordered([(reached[u], reached[v]) for u, v in PARTNERS])
    assert b["maximal_blocks"] == ordered([(reached[u], reached[v]) for u, v in NONPARTNERS])
    b["reached_junction_for_each_of_the_six_labels"] = reached
    for s, values in ((b, (3, 4, 0, 8)), (c, (4, 5, 6, 10)), (d, (5, 12, 8, 24))):
        s["partnered"] = partnered(s, *values)
    return stages


def canonical_knot_checks():
    sys.path.insert(0, str(ROOT / "tools"))
    from knotlab.knots import check_knot
    from knotlab.patterns import parity

    checks = []
    for arity in (3, 6):
        names = [f"x{i}" for i in range(arity)]
        relation = parity(names, odd=False)
        report = check_knot(relation, names[:-1], names[-1])
        assert report.is_knot
        checks.append({"places": arity, "allowed_assignments": len(relation.rows), "K1_K3": True})
    return checks


def main():
    law = import_file("partner_production", LAW)
    verifier = import_file("partner_replay", REPLAY)
    matching = list(zip(TWO_MEMBER_BLOCKS[::2], TWO_MEMBER_BLOCKS[1::2], strict=True))
    primary = witnessed(law, verifier, start(matching), list(range(32)))

    controls = []
    for held in ([], [(0, 2, 4), (1, 3, 5)]):
        initial, following = replay(law, verifier, control_start(held), depth=1)
        expected = 8 - len(held)
        reading = partnered(initial, 3, 4 - len(held) // 2, len(held), expected)
        assert len(following["births"]) == expected
        controls.append({"held": held, "reading": reading, "actual_births": expected})

    rng = Random(SEED)
    samples = []
    for case in range(SAMPLES):
        shuffled = rng.sample(list(TWO_MEMBER_BLOCKS), len(TWO_MEMBER_BLOCKS))
        sample_matching = ordered(zip(shuffled[::2], shuffled[1::2], strict=True))
        rows = start(sample_matching)
        row_order = rng.sample(range(32), 32)
        names = rng.sample(range(78), 78)
        renamed = [[names[b] for b in rows[j]] for j in row_order]
        stages = witnessed(law, verifier, renamed, [row_order.index(j) for j in range(32)])
        samples.append({
            "sample": case,
            "matching_before_renaming": sample_matching,
            "junction_order": row_order,
            "distinction_renaming": names,
            "reached_partnered_at_age": 1,
            "successive_live_counts": [len(r["live"]) for r in stages],
            "held_transversals_ages_one_to_three": [r["partnered"]["held_transversals"] for r in stages[1:]],
        })
    print(json.dumps({
        "freeze": "0127d80d6",
        "engines": {"production": LAW, "independent_replay": REPLAY},
        "literal_witness": {"matching": matching, "stages": primary},
        "local_knotlab_controls": canonical_knot_checks(),
        "partnered_controls": controls,
        "weighting": {
            "name": "Uniform perfect matching of the twelve two-member-block holders with independent uniform junction and distinction renamings",
            "seed": SEED,
            "possible_matchings": 10_395,
            "sample_count": SAMPLES,
            "distinct_sampled_matchings": len({tuple(map(tuple, s["matching_before_renaming"])) for s in samples}),
            "successful_replays": len(samples),
            "samples": samples,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
