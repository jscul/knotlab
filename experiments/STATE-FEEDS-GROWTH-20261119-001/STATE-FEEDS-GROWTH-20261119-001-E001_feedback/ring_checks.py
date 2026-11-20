"""Replay the finite controls for the bare-ring results in selection.md."""

from collections import Counter, defaultdict
from itertools import combinations, product
import json

from growth import ACTIONS, grow, step


LENGTHS = (5, 7, 8, 9, 10, 11, 12, 17)
VETO_STEPS = 6
PLUS_STEPS = 8
CAPS = {"junctions": 6000, "distinctions": 32000}


def ring(n, spares=()):
    extras = {i: 3 * n + k for k, i in enumerate(sorted(spares))}
    return [((i - 1) % n, i, n + 2 * i, n + 2 * i + 1) + ((extras[i],) if i in extras else ())
            for i in range(n)]


def parent_pair(i, n):
    return frozenset(((i - 1) % n, (i + 1) % n))


def handover(stars):
    n = len(stars)
    stage = step(stars, caps=CAPS)
    assert stage["status"] == "extend" and len(stage["born"]) == n
    assert all(len(row) == 2 for row in stage["fresh"].values())
    by_parents = {frozenset(row): v for v, row in stage["parent_sets"].items()}
    children = [by_parents[parent_pair(i, n)] for i in range(n)]
    syndromes = defaultdict(int)
    for v, row in enumerate(stage["stars"]):
        for d in row:
            syndromes[d] ^= 1 << v
    responses = []
    for i, child in enumerate(children):
        old = ((i - 1) % n, i)
        response = frozenset((*old, *(d for _, d in stage["consumed"][child])))
        assert len(response) == 4 and not response.intersection(stage["fresh"][child])
        assert all(len(response.intersection(row)) % 2 == 0 for row in stage["stars"])
        for d in old:
            other = [s for e, s in syndromes.items() if e != d]
            mark = syndromes[d]
            assert mark and mark not in other
            assert all(a ^ b != mark for a, b in combinations(other, 2))
        responses.append(response)
    return stage, children, responses


def completed(trace, rounds):
    assert trace["termination"] == {"status": "age_limit", "last_age": rounds}
    return [trace["stages"][str(s)] for s in range(rounds + 1)]


def veto_checks(raw, stage, children, responses):
    n = len(raw)
    patterns = {"quiet": (), "one_response": (0,), "two_consecutive_responses": (0, 1),
                "two_distance_two_responses": (0, 2), "alternating_responses": tuple(range(0, n, 2)),
                "full_responses": tuple(range(n)), "raw_source_ring": tuple(range(n))}
    records = {}
    for name, indices in patterns.items():
        if name == "raw_source_ring":
            start, occupied = raw, set(range(n))
        else:
            start, occupied = stage["stars"], set()
            for index in indices:
                occupied.symmetric_difference_update(responses[index])
            assert {i for i, v in enumerate(children) if occupied.intersection(start[v])} == set(indices)
        k = sum(not parent_pair(i, n).isdisjoint(indices) for i in range(n))
        frames = completed(grow(start, occupied, ("P", "V"), VETO_STEPS, caps=CAPS), VETO_STEPS)
        assert set(frames[0]["live"]) == set(range(n) if name == "raw_source_ring" else children)
        earlier = len(start) - n
        births = [n]
        cumulative = [n]
        for s, frame in enumerate(frames[1:], 1):
            actual = len(frame["born"])
            total = frame["junction_count"] - earlier
            assert actual == n + s * k and total == n * (s + 1) + k * s * (s + 1) // 2, (n, name, s)
            assert frame["vetoed_multi"] == (k if s == 1 else 0)
            assert all(len(row) == 2 for row in frame["fresh"].values())
            assert frame["occupied"] == sorted(occupied) and not frame["new_occupied"] and not frame["spent_occupied"]
            births.append(actual)
            cumulative.append(total)
        records[name] = {"hot_indices": indices, "occupied": sorted(occupied), "k": k,
                         "births_by_update": births, "cumulative_from_initial_boundary": cumulative}
    return records


def birth_profile(frame):
    counts = Counter((len(row["parents"]), row["demand"], len(row["fresh"])) for row in frame["births"])
    return [[*profile, count] for profile, count in sorted(counts.items())]


def count_controls(stage, children, occupied):
    n = len(children)
    tables = {}
    for table in product(ACTIONS, repeat=2):
        quiet, hot = (step(stage["stars"], state, table, caps=CAPS) for state in ((), occupied))
        assert quiet["status"] == hot["status"] == "extend"
        quiet_counts, hot_counts = [(len(r["born"]), r["distinction_count"] - stage["distinction_count"])
                                    for r in (quiet, hot)]
        assert (quiet_counts == hot_counts) == (table[0] == table[1])
        if table[0] == table[1]:
            assert quiet["stars"] == hot["stars"]
        tables["".join(table)] = {"quiet_births_and_fresh": quiet_counts, "hot_births_and_fresh": hot_counts}

    quiet = completed(grow(stage["stars"], (), ("P", "-"), PLUS_STEPS, caps=CAPS), PLUS_STEPS)
    assert all(len(r["born"]) == n for r in quiet[1:])
    minus = grow(stage["stars"], occupied, ("P", "-"), PLUS_STEPS, caps=CAPS)
    shrunk = minus["stages"]["1"]
    stop = minus["termination"]
    reduced = {v for v, ds in shrunk["fresh"].items() if len(ds) == 1}
    assert len(reduced) == 2 and stop["status"] == "stall" and stop["next_age"] == 2
    assert stop["shortages"] == dict.fromkeys(reduced, 1) and not stop["hot_live_parents"]

    plus = step(stage["stars"], occupied, ("P", "+"), caps=CAPS)
    assert plus["status"] == "extend" and not plus["new_occupied"]
    extra_indices = {i for i in range(n) if 0 in parent_pair(i, n)}
    ids = {frozenset(row): v for v, row in plus["parent_sets"].items()}
    for i in range(n):
        v = ids[frozenset(children[j] for j in parent_pair(i, n))]
        assert len(plus["fresh"][v]) == 2 + (i in extra_indices)
    physical = completed(grow(plus["stars"], occupied, ("P", "+"), PLUS_STEPS, caps=CAPS), PLUS_STEPS)
    restarted = completed(grow(ring(n, extra_indices), rounds=PLUS_STEPS, caps=CAPS), PLUS_STEPS)
    profiles = []
    for left, right in zip(physical[1:], restarted[1:], strict=True):
        assert not left["hot_live_parents"]
        profile = birth_profile(left)
        assert profile == birth_profile(right)
        profiles.append(profile)
    return {"profile_columns": ["parents", "demand", "fresh", "count"], "tables": tables,
            "minus": {"quiet_completed_updates": PLUS_STEPS, "hot_completed_updates": stop["last_age"],
                      "shortages": stop["shortages"]},
            "plus": {"synthetic_spare_indices": sorted(extra_indices), "matched_profiles": profiles}}


def main():
    readings = {}
    for n in LENGTHS:
        raw = ring(n)
        stage, children, responses = handover(raw)
        readings[n] = {"veto": veto_checks(raw, stage, children, responses),
                       "count_controls": count_controls(stage, children, responses[0]),
                       "least_four_responses_verified": len(responses)}
    result = {"circumferences": LENGTHS, "veto_preparations": sum(len(r["veto"]) for r in readings.values()),
              "veto_updates_per_preparation": VETO_STEPS, "plus_following_updates_per_length": PLUS_STEPS,
              "by_circumference": readings}
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
