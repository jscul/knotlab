"""Replay two rank-one rivals with an added six-distinction junction."""

from collections import Counter, defaultdict
from itertools import combinations
import json


CORE = (
    ("seed", (0, 1, 2)),
    ("i", (0, 3, 4)), ("j", (1, 5, 6)), ("k", (2, 7, 8)),
    ("p", (3, 5, 9, 10)), ("q", (4, 7, 11, 12)), ("a", (6, 8, 13, 14)),
)
MARK = (9, 11, 13)


def mask(indices):
    return sum(1 << i for i in indices)


def bits(word):
    return tuple(i for i in range(word.bit_length()) if word >> i & 1)


def incidence(history):
    holders = defaultdict(list)
    adjacent = {site: set() for site, _ in history}
    assert len(adjacent) == len(history)
    for site, support in history:
        assert len(support) == len(set(support))
        for bit in support:
            holders[bit].append(site)
    for holders_here in holders.values():
        assert 1 <= len(holders_here) <= 2
        if len(holders_here) == 2:
            a, b = holders_here
            assert b not in adjacent[a]
            adjacent[a].add(b)
            adjacent[b].add(a)
    return holders, adjacent


def legal(parents, adjacent):
    return (1 <= len(parents) <= 3 and len(set(parents)) == len(parents)
            and all(adjacent[a] & adjacent[b] for a, b in combinations(parents, 2))
            and (len(parents) < 3 or not set.intersection(*(adjacent[a] for a in parents))))


def replay(history):
    events = {}
    for index, (site, support) in enumerate(history):
        holders, adjacent = incidence(history[:index])
        used = tuple(bit for bit in support if bit in holders)
        fresh = tuple(bit for bit in support if bit not in holders)
        assert all(len(holders[bit]) == 1 for bit in used)
        parents = tuple(holders[bit][0] for bit in used)
        if index == 0:
            assert not parents and len(fresh) == 3
        else:
            assert len(fresh) in (2, 3) and legal(parents, adjacent), (site, used, fresh)
        events[site] = {"support": support, "operands": used, "fresh": fresh, "parents": parents}
    return events


def direct_triples(holders, adjacent):
    available = sorted(bit for bit, users in holders.items() if len(users) == 1)
    return [triple for triple in combinations(available, 3)
            if legal(tuple(holders[bit][0] for bit in triple), adjacent)]


def wired_bonds(history, holders):
    exterior = len(history)
    site_index = {site: i for i, (site, _) in enumerate(history)}
    meetings = [0] * (exterior + 1)
    ends = {}
    for bit, users in holders.items():
        a = site_index[users[0]]
        b = site_index[users[1]] if len(users) == 2 else exterior
        ends[bit] = (1 << a) | (1 << b)
        meetings[a] |= 1 << b
        meetings[b] |= 1 << a

    def connected(side):
        pending = visited = side & -side
        while pending:
            site = pending & -pending
            following = meetings[site.bit_length() - 1] & side & ~visited
            visited |= following
            pending = (pending ^ site) | following
        return visited == side

    all_sites = (1 << (exterior + 1)) - 1
    return {mask(bit for bit, endpoints in ends.items() if (endpoints & side).bit_count() == 1)
            for side in range(1, 1 << exterior)
            if connected(side) and connected(all_sites ^ side)}


def measure(history, width):
    events = replay(history)
    holders, adjacent = incidence(history)
    assert set(holders) == set(range(width))
    span = {0}
    for _, support in history:
        equation = mask(support)
        span |= {word ^ equation for word in span}
    assert len(span) == 1 << len(history)

    minimal = []
    minima = {}
    for word in sorted(span - {0}, key=lambda word: (word.bit_count(), word)):
        if any(word & smaller == smaller for smaller in minimal):
            continue
        minimal.append(word)
        for pair in combinations(bits(word), 2):
            minima.setdefault(pair, (word.bit_count(), word))
    assert set(minimal) == wired_bonds(history, holders)
    pairs = tuple(combinations(range(width), 2))
    assert minima.keys() == set(pairs)
    values = [minima[pair][0] for pair in pairs]
    result = {
        "history": [{"site": site, **event} for site, event in events.items()],
        "arity_counts": dict(sorted(Counter(len(row) for _, row in history).items())),
        "three_fresh_additions_after_seed": sum(len(event["fresh"]) == 3 for event in events.values()) - 1,
        "equation_rank": len(history), "allowed_state_count": 1 << (width - len(history)),
        "bond_count": len(minimal), "pair_minimum_histogram": dict(sorted(Counter(values).items())),
        "pair_minimum_upper_triangle": values, "exact_legal_triples": direct_triples(holders, adjacent),
    }
    return result, span, events, holders, minima


def compare(name, width, history_h, history_r, root):
    h, h_span, _, _, h_min = measure(history_h, width)
    r, r_span, events, holders, r_min = measure(history_r, width)
    assert h_span < r_span and len(r_span) == 2 * len(h_span)
    cap = events["x"]
    assert h_span | {word ^ mask(cap["support"]) for word in h_span} == r_span
    high = {site for site, row in history_r if len(row) > 4}
    assert high == {"x"} and max(h["arity_counts"]) <= 4
    assert len(cap["parents"]) == len(cap["fresh"]) == 3
    assert MARK in h["exact_legal_triples"] and not r["exact_legal_triples"]
    assert h["pair_minimum_histogram"] != r["pair_minimum_histogram"]
    assert all(min(h_min[pair][0], 6) == min(r_min[pair][0], 6) for pair in h_min)

    order = {site: i for i, (site, _) in enumerate(history_r)}
    late = max(cap["parents"], key=order.__getitem__)
    late_operand, = (bit for bit in cap["operands"] if late in holders[bit])
    child_outputs = {}
    for bit in cap["fresh"]:
        assert len(holders[bit]) == 2 and holders[bit][0] == "x"
        child_outputs[holders[bit][1]] = bit
    assert len(child_outputs) == 3
    auxiliary = {site: len(set(events[site]["parents"]) - high) for site in child_outputs}
    assert {site for site, degree in auxiliary.items() if degree == 0} == ({root} if root else set())

    def witness(pair, expected):
        pair = tuple(sorted(pair))
        kh, support_h = h_min[pair]
        kr, support_r = r_min[pair]
        assert (kh, kr) == expected
        return {"pair": pair, "K_source": kh, "K_rival": kr,
                "minimizing_bond_source": bits(support_h), "minimizing_bond_rival": bits(support_r)}

    later = [child_outputs[site] for site, degree in auxiliary.items() if degree]
    output_pairs = [witness(pair, (8, 6)) for pair in combinations(later, 2)]
    assert output_pairs
    return {
        "case": name, "width": width, "source": h, "rival": r, "extra_equation": cap["support"],
        "latest_cap_parent": late, "latest_cap_operand": late_operand, "auxiliary_root": root,
        "auxiliary_indegrees_by_cap_child": auxiliary, "cap_output_by_child": child_outputs,
        "opposite_triple_verdict": {"mark": MARK, "source_legal": True, "rival_legal": False},
        "all_named_pairs_equal_when_capped_above_K5": len(h_min),
        "named_full_pairs_with_different_minima": sum(h_min[p][0] != r_min[p][0] for p in h_min),
        "different_full_histograms_exclude_every_isometry": True,
        "late_parent_and_auxiliary_root": witness((late_operand, child_outputs[root]), (7, 6)) if root else None,
        "two_nonroot_children": output_pairs,
    }


def cutoff_three_swap(history, width, three_fresh):
    presentation, _, _, holders, minima = measure(history, width)
    assert max(presentation["arity_counts"]) <= 4
    assert presentation["three_fresh_additions_after_seed"] == three_fresh
    swap = {10: 11, 11: 10}
    assert all(len(holders[i]) == 1 and len(dict(history)[holders[i][0]]) == 4 for i in swap)
    assert all(entry[0] > 3 for pair, entry in minima.items() if any(i in swap for i in pair))

    def image(group):
        return tuple(sorted(swap.get(i, i) for i in group))

    assert all(min(entry[0], 4) == min(minima[image(pair)][0], 4) for pair, entry in minima.items())
    mapped_mark = image(MARK)
    assert MARK in presentation["exact_legal_triples"] and mapped_mark not in presentation["exact_legal_triples"]
    assert mapped_mark == (9, 10, 13) and holders[9] == holders[10]
    pair = (9, 10)
    values = minima[pair][0], minima[image(pair)][0]
    assert values[0] == 4 < values[1]
    return {"width": width, "presentation": presentation, "transposed": sorted(swap),
            "legal_mark": MARK, "forbidden_image": mapped_mark,
            "all_pairs_equal_when_capped_above_K3": len(minima),
            "first_distinguishing_cutoff": 4,
            "pair_witness": {"pair": pair, "image": image(pair), "K": values}}


def verify_unary_formula(before, after, old_width, anchor):
    """Check every entry after one unary attachment with three fresh bits."""
    old = dict(zip(combinations(range(old_width), 2), before["pair_minimum_upper_triangle"], strict=True))
    pairs = tuple(combinations(range(old_width + 3), 2))
    new = after["pair_minimum_upper_triangle"]
    assert len(new) == len(pairs)
    for (i, j), actual in zip(pairs, new, strict=True):
        if j < old_width:
            expected = old[i, j]
        elif i >= old_width or i == anchor:
            expected = 4
        else:
            expected = old[min(i, anchor), max(i, anchor)] + 2
        assert actual == expected, ((i, j), actual, expected)
    return len(pairs)


def main():
    x = ("x", (9, 11, 13, 15, 16, 17))
    s = ("s", (15, 18, 19))
    y = ("y", (19, 14, 20, 21))
    tail = (("t", (16, 20, 22, 23)), ("u", (17, 21, 24, 25)))
    source_history = (*CORE, y, s, *tail)
    rival_history = (*CORE, x, s, y, *tail)
    root_case = compare("auxiliary_root_and_two_nonroots", 26, source_history, rival_history, "s")
    assert root_case["source"]["three_fresh_additions_after_seed"] == 3
    assert root_case["rival"]["three_fresh_additions_after_seed"] == 1

    anchor = 25
    assert anchor not in MARK and all(len(incidence(history)[0][anchor]) == 1
                                     for history in (source_history, rival_history))
    attachment = ("z", (anchor, 26, 27, 28))
    padded = compare("common_unary_attachment", 29, (*source_history, attachment),
                     (*rival_history, attachment), "s")
    for side in ("source", "rival"):
        s_before = root_case[side]["three_fresh_additions_after_seed"]
        assert padded[side]["three_fresh_additions_after_seed"] == s_before + 1
    padded["common_attachment_operand"] = anchor
    padded["unary_formula_entries_verified"] = {
        side: verify_unary_formula(root_case[side], padded[side], 26, anchor)
        for side in ("source", "rival")
    }

    y = ("y", (14, 15, 16, 17))
    x = ("x", (9, 11, 13, 18, 19, 20))
    tail = (("t", (15, 18, 21, 22)), ("u", (16, 19, 23, 24)), ("v", (17, 20, 25, 26)))
    no_root_case = compare("only_nonroot_children", 27, (*CORE, y, *tail), (*CORE, y, x, *tail), None)
    assert no_root_case["source"]["three_fresh_additions_after_seed"] == 4
    assert no_root_case["rival"]["three_fresh_additions_after_seed"] == 2

    no_three = cutoff_three_swap(CORE, 15, 0)
    one_three = cutoff_three_swap((*CORE, ("y", (14, 15, 16, 17))), 18, 1)
    one_three["unary_formula_entries_verified"] = verify_unary_formula(
        no_three["presentation"], one_three["presentation"], 15, 14)
    print(json.dumps({"pair_order": "K = minimum bond size, for pairs in lexicographic order",
                      "cases": [root_case, no_root_case],
                      "lower_cutoff_controls": [no_three, one_three],
                      "common_attachment_control": padded}, indent=2))


if __name__ == "__main__":
    main()
