"""Replay the exact width-28 twins and their common or transported futures."""

from collections import Counter, deque
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
import sys


PROOFS = Path(__file__).resolve().parents[2]
STEM = "VARIABLE-OUTPUT-READER-20261118-001"
OLD = PROOFS / (STEM + "K") / (STEM + "K-P001_third_three_fresh")
J = PROOFS / (STEM + "J") / (STEM + "J-P001_seven_to_six")


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


previous = load("width_28_exact", OLD / "high_check.py")
literal = previous.literal
frontiers = load("witness_frontier", J / "frontier.py")


def original():
    record = json.loads((OLD / "high_check.json").read_text())
    rows = tuple(map(tuple, record["prefix_junctions"]))
    return tuple((*rows, (*side["cap_inputs"], *side["cap_outputs"])) for side in record["transition"])


def swap(bit):
    return {21: 22, 22: 21}.get(bit, bit)


def transported(rows):
    return tuple(tuple(swap(bit) for bit in row) for row in rows)


def matches_transport(left, right):
    return [set(row) for row in transported(left)] == [set(row) for row in right]


def extend(rows, inputs, outputs):
    holders, adjacent = literal.incidence(rows)
    assert len(set(inputs)) == len(inputs) and all(len(holders[bit]) == 1 for bit in inputs)
    assert literal.legal_parents([holders[bit][0] for bit in inputs], adjacent)
    assert outputs in (2, 3)
    return (*rows, (*inputs, *range(len(holders), len(holders) + outputs)))


def menu(rows, count):
    holders, adjacent = literal.incidence(rows)
    loose = sorted(bit for bit, sites in holders.items() if len(sites) == 1)
    return [group for group in combinations(loose, count)
            if literal.legal_parents([holders[bit][0] for bit in group], adjacent)]


def entries(rows, dual_check=False):
    literal.replay(rows)
    values, _ = previous.wired_table(rows)
    if dual_check:
        width = len(literal.incidence(rows)[0])
        dual = literal.scalar_table(literal.minimal_dual(rows), width)
        assert values == {key: count + 1 for key, count in dual.items()}
    return values


def differences(left, right):
    return [(p, left[p], right[p]) for p in sorted(left) if left[p] != right[p]]


def frozen_snapshot(rows, hold):
    holders, adjacent = literal.incidence(rows)
    if hold is not None:
        assert holders[hold] == [9]
    available = {bit: sites[0] for bit, sites in holders.items() if len(sites) == 1 and bit != hold}
    active = sorted(set(available.values()))
    loose = {site: sorted(bit for bit, owner in available.items() if owner == site) for site in active}
    pos = {site: i for i, site in enumerate(active)}
    masks = [sum(1 << pos[owner] for owner in nbrs if owner in pos) for nbrs in adjacent]
    retired = sorted({group for site, group in enumerate(masks) if site not in pos and group.bit_count() >= 2})
    raw = frontiers.old.Frontier(tuple(len(loose[v]) for v in active), tuple(masks[v] for v in active), tuple(retired))
    state, order = frontiers.canon(raw)
    return state, tuple(active[i] for i in order), loose


def narrow_closure(base, hold=None):
    """Verify every record transition against an actual history with the indicated reserve."""
    first = frozen_snapshot(base, hold)[0]
    representatives = {first: (base, ())}
    queue = deque([first])
    moves = Counter()
    outdegrees = Counter()
    positive = []
    transitions = []
    while queue:
        node = queue.popleft()
        rows, trace = representatives[node]
        check, active, loose = frozen_snapshot(rows, hold)
        assert check == node
        _, adjacent = literal.incidence(rows)
        allowed = [parents for size in (2, 3) for parents in combinations(range(len(active)), size)
                   if literal.legal_parents([active[i] for i in parents], adjacent)]
        assert set(allowed) == {group for group in frontiers.old.possible_parents(node) if len(group) >= 2}
        outdegrees[len(allowed)] += 1
        if any(len(parents) == 3 for parents in allowed):
            mark = next(tuple(loose[active[i]][0] for i in parents) for parents in allowed if len(parents) == 3)
            positive.append((trace, mark))
        for parents in allowed:
            operands = tuple(loose[active[i]][0] for i in parents)
            grown = extend(rows, operands, 2)
            successor = frontiers.step(node, parents, 2)
            assert frozen_snapshot(grown, hold)[0] == successor
            transitions.append(f"{node!r}|{parents!r}|{successor!r}")
            moves[len(parents)] += 1
            if successor not in representatives:
                representatives[successor] = (grown, (*trace, operands))
                queue.append(successor)
    first_positive = None
    if positive:
        trace, mark = positive[0]
        final = base
        for group in trace:
            final = extend(final, group, 2)
        assert mark in menu(final, 3)
        rival = transported(base)
        for group in trace:
            rival = extend(rival, tuple(map(swap, group)), 2)
        assert matches_transport(final, rival) and tuple(sorted(map(swap, mark))) in menu(rival, 3)
        first_positive = {"steps": len(trace), "left_input_sequence": trace, "left_legal_mark": mark,
                          "right_input_sequence": [tuple(map(swap, g)) for g in trace],
                          "right_legal_mark": tuple(map(swap, mark)), "width": len(literal.incidence(final)[0])}
    return {"records": len(representatives), "transitions_by_arity": dict(sorted(moves.items())),
            "records_by_number_of_available_parent_groups": dict(sorted(outdegrees.items())),
            "records_by_available_bit_count": dict(sorted(Counter(sum(node.loose) for node in representatives).items())),
            "closure_digest": sha256("\n".join(sorted(transitions)).encode()).hexdigest(),
            "positive_records": len(positive), "first_positive": first_positive}


def full_law_marked_branch(left, right, ltable, rtable):
    """A local branch with a live marked triple, attached along the single bit 23."""
    plan = [((23,), 3), ((28,), 3), ((29,), 3), ((30,), 3),
            ((31, 34), 2), ((32, 37), 2), ((35, 38), 2)]
    size = len(left)
    for inputs, outputs in plan:
        left = extend(left, inputs, outputs)
        right = extend(right, inputs, outputs)
    assert matches_transport(left, right)
    a, b = set(menu(left, 3)), set(menu(right, 3))
    assert a == b and (40, 42, 44) in a and (40, 41, 42) not in a
    piece = left[size:]
    local, _ = previous.wired_table(piece)
    assert local == previous.wired_table(right[size:])[0]

    def glued(table, i, j):
        if j < 28:
            return table[i, j]
        if i == 23 or i >= 28:
            return local[i, j]
        return table[tuple(sorted((i, 23)))] + local[23, j] - 2

    pairs = list(combinations(range(46), 2))
    predicted = {(i, j): glued(ltable, i, j) for i, j in pairs}
    assert all(predicted[i, j] == glued(rtable, i, j) for i, j in pairs)
    assert entries(left) == entries(right) == predicted
    return {"inputs_and_output_counts": plan, "width": 46, "exact_entries_by_one_bit_gluing": len(pairs),
            "entries_independently_checked_on_both_complete_histories": len(predicted),
            "labeled_triple_menus_equal": True, "legal_triples": sorted(a), "forbidden_control": [40, 41, 42]}


def run():
    left, right = original()
    assert matches_transport(left, right)
    start_left, start_right = entries(left, True), entries(right, True)
    assert start_left == start_right and len(start_left) == 378 and not menu(left, 3) and not menu(right, 3)
    assert menu(left, 2) == menu(right, 2) == [(x, y) for x in (23, 24) for y in (25, 26, 27)]
    cases = []
    for pair in menu(left, 2):
        lrows, rrows = extend(left, pair, 2), extend(right, pair, 2)
        assert matches_transport(lrows, rrows)
        detailed = pair == (23, 25)
        lv, rv = entries(lrows, detailed), entries(rrows, detailed)
        diff = differences(lv, rv)
        assert len(diff) == 4 and len(lv) == 435
        assert all(lv[key] == rv[tuple(sorted(map(swap, key)))] for key in lv)
        assert all({a, b} == {6, 8} for _, a, b in diff)
        cases.append({"common_input_pair": pair, "named_differences_K": diff})
    left_one, right_one = extend(left, (23, 25), 2), extend(right, (23, 25), 2)
    assert (22, 28) in menu(left_one, 2) and (22, 28) not in menu(right_one, 2)
    assert (21, 28) in menu(right_one, 2) and (21, 28) not in menu(left_one, 2)
    first = entries(extend(left_one, (22, 28), 2))
    matched = entries(extend(right_one, (21, 28), 2))
    assert all(first[p] == matched[tuple(sorted(map(swap, p)))] for p in first)
    spent = [(p, first[p], matched[p]) for p in ((21, 30), (21, 31), (22, 30), (22, 31))]
    assert [readings[1:] for readings in spent] == [(6, 4), (6, 4), (4, 6), (4, 6)]
    second = entries(extend(right_one, (24, 26), 2))
    histograms = [dict(sorted(Counter(vals.values()).items())) for vals in (first, second)]
    assert histograms[0] != histograms[1]
    common, whole = narrow_closure(left, 22), narrow_closure(left)
    assert common["records"] == 27 and common["positive_records"] == 0
    assert 0 not in common["records_by_number_of_available_parent_groups"]
    assert whole["first_positive"]["steps"] == 6
    assert whole["records_by_available_bit_count"] == {5: 23, 6: 87}
    singletons = [set(menu(rows, 1)) for rows in (left, right)]
    unary_spend = [entries(extend(rows, (tip,), 2)) for rows, tip in ((left, 22), (right, 21))]
    unary_readings = [(p, unary_spend[0][p], unary_spend[1][p]) for p in ((21, 28), (22, 28))]
    assert [entry[1:] for entry in unary_readings] == [(5, 3), (3, 5)]
    full_first = []
    unary_six_counts = []
    for action in ((23,), (25,), (23, 25)):
        for outputs in (2, 3):
            a, b = (entries(extend(rows, action, outputs)) for rows in (left, right))
            dif = differences(a, b)
            assert len(dif) == (0 if len(action) == 1 else 2 * outputs)
            full_first.append({"representative_inputs": action, "outputs": outputs, "named_differences_K": dif})
            if len(action) == 1 and outputs == 2:
                unary_six_counts.append(Counter(a.values())[6])
    assert unary_six_counts == [145, 137]
    return {"base_width": 28, "base_exact_entries": 378, "width_30_successors": cases,
            "width_30_example_binary_menus": [menu(left_one, 2), menu(right_one, 2)],
            "width_32_transported_spare_uses_K": spent,
            "first_nontransported_anonymous_difference_at_width_32": {
                "left_second_action": [22, 28], "right_second_action": [24, 26], "K_histograms": histograms},
            "narrow_common_name_closure": common, "narrow_individual_closure": whole,
            "full_law_one_sided_initial_singletons": [sorted(a - b) for a, b in (singletons, singletons[::-1])],
            "full_law_transported_unary_spare_use_K": unary_readings,
            "full_law_unary_two_outputs_K6_counts_on_23_and_25": unary_six_counts,
            "full_law_first_actions_up_to_equal_loose_bits": full_first,
            "full_law_identity_equal_with_legal_triples": full_law_marked_branch(left, right, start_left, start_right)}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
