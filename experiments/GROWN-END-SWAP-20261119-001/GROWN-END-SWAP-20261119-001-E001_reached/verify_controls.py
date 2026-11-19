"""Explicit support fixtures for the frozen controls and two proposed histories."""

import json
from itertools import combinations

from verify import Arrangement, check, exact_table


def case(start, current, following, swap=None, certificates=()):
    labels = sorted({x for star in current for x in star})
    transposition = {} if swap is None else dict([swap, swap[::-1]])
    return {"a": {"start": start, "current": current, "next": following},
            "permutation": [[x, transposition.get(x, x)] for x in labels],
            "certificates": list(certificates)}


def fixtures():
    static = [[0, 1, 2, 3], [0, 1, 4, 5, 6, 7], [2, 3, 8, 9, 10, 11],
              [4, 5, 12], [6, 7, 13], [8, 9, 14], [10, 11, 15]]
    yield "static_proposition_x", case(None, static, static + [[12, 13, 16], [14, 15, 17]], (0, 2),
                                      [{"stage": "next_a", "pair": [0, 1], "distance": 2, "shore": [1, 3, 4, 7]},
                                       {"stage": "next_b", "pair": [1, 2], "distance": 3, "shore": [0]}])

    seed = [[0, 1, 2]]
    open_stage = seed + [[0, 3, 4], [1, 5, 6], [2, 7, 8]]
    pairs_stage = open_stage + [[3, 5, 9], [4, 7, 10], [6, 8, 11]]
    yield "reached_identity", case(seed, open_stage, pairs_stage)
    closed = case(seed, pairs_stage, pairs_stage + [[9, 10, 11]])
    closed["a"]["intermediate"] = [open_stage]
    yield "implied_closure", closed

    seven = [[0, 1, 2, 3], [0, 1, 4, 5, 6], [2, 3, 14, 15], [4, 7, 10, 11],
             [5, 6, 12], [7, 8, 9], [8, 9, 13]]
    seven_current = seven + [[10, 12, 16], [11, 13, 17], [14, 18, 19], [15, 20, 21]]
    yield "frozen_seven_junction_start", case(seven, seven_current, seven_current +
                                             [[16, 17, 22], [18, 20, 23, 24], [19, 25, 26], [21, 27, 28]], (0, 2))

    six = [[0, 1, 2, 3], [0, 1, 4, 5], [2, 3, 13, 14], [4, 6, 9, 10],
           [5, 6, 7, 8, 11], [7, 8, 12]]
    six_current = six + [[9, 11, 15], [10, 12, 16], [13, 17, 18], [14, 19, 20]]
    six_next = six_current + [[15, 16, 21], [17, 19, 22, 23], [18, 24, 25], [20, 26, 27]]
    yield "six_junction_start", case(six, six_current, six_next, (0, 2))
    yield "wrong_renaming", case(six, six_current, six_next, (15, 16))


def minimal_xor_table(supports):
    words = {0}
    for support in supports:
        row = sum(1 << x for x in support)
        words |= {word ^ row for word in words}
    minimal = []
    labels = sorted({x for support in supports for x in support})
    table = {p: None for p in combinations(labels, 2)}
    for word in sorted(words - {0}, key=int.bit_count):
        if any(word & smaller == smaller for smaller in minimal):
            continue
        minimal.append(word)
        for pair in combinations((x for x in labels if word & (1 << x)), 2):
            if table[pair] is None:
                table[pair] = word.bit_count() - 1
    return table


def main():
    output = {}
    for name, data in fixtures():
        outcome = check(data, 100_000, unrestricted=True)
        xor_checks = {}
        for stage in ("current", "next"):
            supports = data["a"][stage]
            table, _, _ = exact_table(Arrangement.parse(supports), 100_000)
            assert minimal_xor_table(supports) == table, f"cut/XOR disagreement at {name} {stage}"
            xor_checks[stage] = len(table)
        output[name] = {"input": data, "result": outcome, "xor_crosscheck_entries": xor_checks}
    for name in ("static_proposition_x", "frozen_seven_junction_start", "six_junction_start"):
        outcome = output[name]["result"]
        assert outcome["current_tables_match"] and outcome["reading"]["keeps_reading"]
        assert bool(outcome["decisive_bonds"]) and outcome["extensions"]["allows_within_parent_repair"] is None
    assert not output["static_proposition_x"]["result"]["reachable_a"]
    for name in ("reached_identity", "implied_closure"):
        assert output[name]["result"]["extensions"]["also_matches_round_junctions"]
    wrong = output["wrong_renaming"]["result"]
    assert not (wrong["current_tables_match"] and wrong["reading"]["keeps_reading"])
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
