"""Screen the named one-shrink sources for alternative six-place supports."""

from collections import Counter
from hashlib import sha256
from itertools import chain, combinations
import json
from pathlib import Path

from closure import OLD, RULE, actual_triples


CLOSURE_DIGEST = "e09c80114789cb0321c3c78e752c6df0a40b103041937bf4e62c269a09d2897d"


def examples():
    data = Path(__file__).with_name("closure.json").read_bytes()
    assert sha256(data).hexdigest() == CLOSURE_DIGEST
    saved = json.loads(data)
    unique = {}
    for group in saved["shortest_post_exception_histories"]:
        before, after = group["prior_shrinks"], group["subsequent_shrinks"]
        if before + after != 1:
            continue
        for field in ("first_with_a_legal_triple", "first_with_a_legal_triple_using_high_output"):
            item = group[field]
            rows = tuple(map(tuple, item["junction_supports"]))
            key = rows, item["exceptional_site"]
            unique.setdefault(key, []).append(f"{before},{after}/{field}")
    for case in saved["last_site_complement_test"]["all_complementary_cases"]:
        prefix = case["prefix"]
        key = tuple(map(tuple, prefix["junction_supports"])), prefix["exceptional_site"]
        unique.setdefault(key, []).append(f"complementary_prefix_{prefix['width']}")
    return unique


def literal_history(rows, high):
    encountered = set(rows[0])
    assert len(encountered) == 3
    shrink_count = 0
    inputs_high = outputs_high = None
    for site, scope in enumerate(rows[1:], 1):
        previous = dict(enumerate(rows[:site]))
        inputs = tuple(bit for bit in scope if bit in encountered)
        outputs = set(scope) - encountered
        assert len(inputs) + len(outputs) == len(scope)
        assert RULE.legal_local_move(previous, inputs, OLD.FRESH_FOR_PARENT_TEST)
        if site in (1, 2):
            assert (len(inputs), len(outputs)) == (1, 3)
        elif site == high:
            assert (len(inputs), len(outputs)) == (3, 3)
            inputs_high, outputs_high = frozenset(inputs), frozenset(outputs)
        else:
            assert len(inputs) in (2, 3) and len(outputs) == 2
            shrink_count += len(inputs) == 3
        encountered.update(outputs)
    assert shrink_count == 1 and inputs_high is not None and outputs_high is not None
    assert encountered == set(range(len(encountered)))
    return inputs_high, outputs_high, encountered


def bipartition(graph):
    colors = {0: 0}
    visited = [0]
    for site in visited:
        for neighbor in sorted(graph[site]):
            if neighbor not in colors:
                colors[neighbor] = 1 - colors[site]
                visited.append(neighbor)
            assert colors[neighbor] != colors[site]
    assert colors.keys() == graph.keys()
    return colors


def witness_roster(inputs, owners, graph):
    input_sites = tuple(owners[bit] for bit in inputs)
    witnesses = tuple(tuple(sorted(graph[a] & graph[b])) for a, b in combinations(input_sites, 2))
    if not all(witnesses) or set.intersection(*(graph[site] for site in input_sites)):
        return None
    return input_sites, witnesses


def critical(before_in, before_out, candidate_in, candidate_out):
    if before_in & candidate_out or candidate_in & before_out:
        return False
    return not (before_in & candidate_in) or before_out == candidate_out


def grade(rows, high, labels):
    source_input, source_output, ground = literal_history(rows, high)
    source_support = source_input | source_output
    menu = actual_triples(rows)
    assert menu
    lows = {i: scope for i, scope in enumerate(rows) if i != high}
    users, neighbors = RULE.incidence(lows)
    color = bipartition(neighbors)
    single = {bit: holders[0] for bit, holders in users.items() if len(holders) == 1}
    mandatory = ground - users.keys()
    possible = sorted(single)
    assert mandatory <= source_output
    assert len(possible) == 2 * (6 - len(mandatory))

    counters = Counter()
    adverse = []
    true_orientation_seen = False
    for selected in combinations(possible, 6 - len(mandatory)):
        counters["supports_considered"] += 1
        holders = tuple(single[bit] for bit in selected)
        if len(set(holders)) != len(holders):
            continue
        counters["supports_meeting_each_low_at_most_once"] += 1
        if len({color[site] for site in holders}) != 1:
            continue
        counters["bipartite_supports"] += 1
        support = frozenset(selected) | mandatory
        possible_menu = None
        for proposed in combinations(selected, 3):
            counters["orientations_considered"] += 1
            witnesses = witness_roster(proposed, single, neighbors)
            if witnesses is None:
                continue
            counters["orientations_with_legal_low_input_witnesses"] += 1
            inputs = frozenset(proposed)
            outputs = support - inputs
            if support != source_support and not critical(source_input, source_output, inputs, outputs):
                continue
            counters["orientations_after_critical_pair_filter"] += 1
            true_orientation_seen |= (inputs == source_input and outputs == source_output)
            if support == source_support:
                counters["orientations_of_unchanged_support"] += 1
                continue
            if possible_menu is None:
                modified = (*rows[:high], tuple(sorted(support)), *rows[high + 1:])
                possible_menu = actual_triples(modified)
            if possible_menu == menu:
                continue
            counters["adverse_orientations"] += 1
            input_holders, pair_witnesses = witnesses
            adverse.append({
                "candidate_high_support": tuple(sorted(support)),
                "candidate_inputs": proposed, "candidate_outputs": tuple(sorted(outputs)),
                "low_input_holders": input_holders, "low_pair_witnesses_in_input_pair_order": pair_witnesses,
                "common_source_inputs": tuple(sorted(inputs & source_input)),
                "legal_in_source_only": tuple(sorted(menu - possible_menu)),
                "legal_in_candidate_only": tuple(sorted(possible_menu - menu)),
                "abstract_candidate_triple_menu": tuple(sorted(possible_menu)),
            })
    assert true_orientation_seen
    return {
        "closure_records": labels, "width": 1 + max(chain.from_iterable(rows)),
        "named_source_history": rows, "source_high_site": high,
        "source_high_inputs": tuple(sorted(source_input)), "source_high_outputs": tuple(sorted(source_output)),
        "source_named_triple_menu": tuple(sorted(menu)),
        "mandatory_high_bits": tuple(sorted(mandatory)),
        "only_one_low_holder": tuple((bit, single[bit]) for bit in possible),
        "counts": dict(counters),
        "adverse_orientations_of_abstract_supports": adverse,
    }


def run():
    fixtures = [grade(rows, high, labels) for (rows, high), labels in examples().items()]
    assert any(case["adverse_orientations_of_abstract_supports"] for case in fixtures)
    return {
        "closure_artifact_sha256": CLOSURE_DIGEST,
        "screen_scope": "Named genuine sources with one shrinking join and a live triple menu. "
                        "Candidate supports retain all named low scopes. Candidate menus grade the "
                        "resulting present incidence. Pair minima and chronology of candidates are outside this test.",
        "literal_sources": len(fixtures),
        "cases": fixtures,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
