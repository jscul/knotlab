"""Exhaust and independently sample the labelled one-edit population."""

from collections import Counter
from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import cache, reduce
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from operator import and_, or_
from pathlib import Path
from random import Random
import argparse
import json
import sys

import networkx as nx
from scipy.stats import beta


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESEARCH = ROOT / "research" / HERE.parent.name
PRIOR = ROOT / ("experiments/FOUR-READINGS-20261120-001D/"
                "FOUR-READINGS-20261120-001D-E001_unbuilt_sources")
LAWS = ("parity", "nae")
HORIZONS = (16, 32)
CAP = 128
FORECAST_CAP = 4096
COMPACT_CAP = 2048
SAMPLE_COUNT = 256
SEED = 20261120313
MEETINGS = ((0, 1), (0, 1), (0, 4), (1, 4), (2, 4), (2, 6), (3, 4), (3, 5), (5, 6))
LOOSE = (3, 0, 3, 3, 3, 2, 2)
OPERATIONS = ("add_loose", "delete_loose", "add_shared", "delete_shared")


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@cache
def libraries():
    prior_panel = load("four_source_edit_panel", PRIOR / "panel.py")
    return prior_panel, prior_panel.fix, prior_panel.end


@dataclass(frozen=True)
class Edit:
    operation: str
    holders: tuple[int, ...]
    distinction: int

    def applied(self, source):
        if self.operation.startswith("add"):
            return tuple((*row, self.distinction) if knot in self.holders else row
                         for knot, row in enumerate(source))
        return tuple(tuple(bit for bit in row if bit != self.distinction) for row in source)


def edit_population(source):
    _, physical, _ = libraries()
    owners, _, _ = physical.incidence(source)
    new_name = max(owners) + 1
    populations = {
        "add_loose": [((holder,), new_name) for holder in range(len(source))],
        "delete_loose": [(tuple(holders), bit) for bit, holders in sorted(owners.items())
                         if len(holders) == 1],
        "add_shared": [(pair, new_name) for pair in combinations(range(len(source)), 2)],
        "delete_shared": [(tuple(holders), bit) for bit, holders in sorted(owners.items())
                          if len(holders) == 2],
    }
    return tuple(Edit(operation, holders, bit) for operation in OPERATIONS
                 for holders, bit in populations[operation])


def bounded_groups(state, cap):
    _, _, operator = libraries()
    try:
        return operator._proposals(state, cap)
    except operator._Cap:
        return None


def next_parents(state, cap=CAP):
    _, _, operator = libraries()
    if not state.opens:
        return "closed", (), (), ()
    all_groups, unary, shortages = [], [], []
    capped = False
    for part in nx.connected_components(role_incidence(state)):
        live = [holder for kind, holder in part if kind == 0]
        sub = operator.restricted(state, live)
        groups = bounded_groups(sub, cap)
        if groups is None:
            capped = True
            continue
        all_groups.extend(groups)
        used = Counter(holder for group in groups for holder in group)
        short = [(holder, used[holder] - supply)
                 for holder, supply in sub.opens.items() if used[holder] > supply]
        if short:
            shortages.extend(short)
            continue
        offshoots = tuple((holder,) for holder, supply in sub.opens.items()
                          for _ in range(supply - used[holder]))
        capped |= len(groups) + len(offshoots) > cap
        unary.extend(offshoots)
    groups = tuple(sorted((g for g in all_groups if len(g) > 2))
                   + sorted(g for g in all_groups if len(g) == 2))
    if shortages:
        return "stall", (), groups, sorted(shortages)
    if capped:
        return "parent_cap", (), None, ()
    return "funded", groups + tuple(sorted(unary)), groups, ()


def write_cohort(stars, state, law, parents):
    _, physical, operator = libraries()
    owners, _, loose = physical.incidence(stars)
    implied = law == "parity" and len(parents) == 1
    if implied:
        if len(parents[0]) < 3:
            return "subarity_stop", (), stars
        fresh = (0,)
    else:
        later_blocks = operator._parent_blocks(parents)
        later = operator.End(dict.fromkeys(range(len(parents)), 1), later_blocks)
        proposals = bounded_groups(later, FORECAST_CAP)
        if proposals is None:
            return "fresh_forecast_cap", (), stars
        demand = Counter(holder for group in proposals for holder in group)
        fresh = tuple(max(demand[index], 3 - len(group), 1)
                      for index, group in enumerate(parents))
    assert {holder: len(bits) for holder, bits in loose.items()} == state.opens
    remaining = {holder: iter(bits) for holder, bits in loose.items()}
    new_name = max(owners) + 1
    born = []
    for index, (group, count) in enumerate(zip(parents, fresh, strict=True)):
        inputs = tuple(next(remaining[holder]) for holder in group)
        introduced = tuple(range(new_name, new_name + count))
        born.append(physical.Birth(len(stars) + index, group, inputs, introduced))
        new_name += count
    assert all(next(queue, None) is None for queue in remaining.values())
    return "extend", born, stars + tuple(birth.support for birth in born)


def role_incidence(state):
    graph = nx.Graph()
    graph.add_nodes_from(((0, holder), {"role": "live", "loose": n})
                         for holder, n in state.opens.items())
    for index, block in enumerate(state.blocks):
        role = (1, index)
        graph.add_node(role, role="witness", loose=0)
        graph.add_edges_from((role, (0, holder)) for holder in block)
    return graph


def map_gates(state, groups):
    graph = role_incidence(state)
    components = [graph.subgraph(part).copy() for part in nx.connected_components(graph)]
    ranks = [part.number_of_edges() - len(part) + 1 for part in components]
    counts = Counter(pair for block in state.blocks for pair in combinations(block, 2))
    record = {
        "ranks": sorted(ranks),
        "two_witnesses_after_reduction": any(n > 1 for n in counts.values()),
        "unheld_group": any(len(group) >= 3 for group in groups),
        "total_loose": sum(state.opens.values()),
    }
    record["identified"] = (record["total_loose"] >= 2 and not record["two_witnesses_after_reduction"]
                            and not record["unheld_group"])
    return record, list(zip(components, ranks, strict=True))


def joined(*paths):
    assert all(first[-1] == following[0] for first, following in zip(paths, paths[1:]))
    return paths[0] + tuple(role for path in paths[1:] for role in path[1:])


def live_word(path):
    return tuple(holder for kind, holder in path[:-1] if kind == 0)


def compatible(first, second):
    circuit = joined(first, first, second)[:-1]
    return all(circuit[i] != circuit[(i + 2) % len(circuit)] for i in range(len(circuit)))


def returns_through(core, start, role_limit):
    def visit(path, used):
        for following in core[path[-1]]:
            if following == start and len(path) >= 8:
                yield (*path, start)
            elif following not in used and len(path) < role_limit:
                yield from visit((*path, following), used | {following})
    return tuple(visit((start,), {start}))


def node_type(attrs):
    return attrs["role"], attrs["loose"], attrs.get("marked", False)


def mark_orbit(core, mark):
    marked = core.copy()
    marked.nodes[mark]["marked"] = True
    other = core.copy()
    orbit = []
    for candidate in other:
        if core.degree(candidate) != core.degree(mark):
            continue
        if node_type(core.nodes[candidate]) != node_type(core.nodes[mark]):
            continue
        other.nodes[candidate]["marked"] = True
        if nx.is_isomorphic(marked, other, node_match=lambda x, y: node_type(x) == node_type(y)):
            orbit.append(candidate[1])
        del other.nodes[candidate]["marked"]
    return tuple(sorted(orbit))


def candidate_returns(core, period_limit):
    orbit = cache(lambda mark: mark_orbit(core, (0, mark)))
    candidates = []
    for start in (role for role in core if role[0] == 0):
        returns = returns_through(core, start, 2 * (period_limit - 4))
        for a in returns:
            first = live_word(a)
            for b in returns:
                second = live_word(b)
                if len(first) + len(second) > period_limit or not compatible(a, b):
                    continue
                first_names, second_names = set(first), set(second)
                names = first_names | second_names
                for private in second_names - first_names:
                    marks = orbit(private)
                    if names.issuperset(marks):
                        candidates.append((marks, first, second))
    return candidates


def select_tied(candidates):
    if not candidates:
        return []
    order = min((len(a) + len(b), len(a)) for _, a, b in candidates)
    chosen = {}
    for marks, a, b in candidates:
        if (len(a) + len(b), len(a)) == order:
            chosen.setdefault(marks, set()).add((a, b))
    return [{"marks": marks, "returns": sorted(words)}
            for marks, words in sorted(chosen.items())]


def ways_to_read(components, cut, horizon):
    period_limit = (horizon - cut + 1) // 2
    if period_limit < 8:
        return [], False
    candidates = []
    capped = False
    for role_graph, rank in components:
        if rank < 2:
            continue
        if len(role_graph) > 48 or sum(role == 0 for role, _ in role_graph) > 20:
            capped = True
            continue
        core = nx.k_core(role_graph, k=2)
        candidates.extend(candidate_returns(core, period_limit))
    return select_tied(candidates), capped


def residual_turns(state, groups):
    _, _, operator = libraries()
    residual = {group for group in groups if len(group) == 2}
    ordered = residual | {g[::-1] for g in residual}
    adjacency = operator.neighbors(state)
    turns = nx.DiGraph()
    turns.add_nodes_from(sorted(ordered))
    for a, b in sorted(ordered):
        for c in sorted(adjacency[b] - adjacency[a] - {a}):
            if (b, c) in ordered:
                turns.add_edge((a, b), (b, c))
    return residual, turns


def residual_reading(state, groups, cut, horizon):
    """Post-screen certificate using the proved two-parent turn rule."""
    limit = (horizon - cut + 1) // 2
    roles = role_incidence(state)
    if limit < 8 or len(state.opens) > 20 or len(roles) > 48:
        return [], {}
    residual, turns = residual_turns(state, groups)
    all_cycles = {}
    for component in nx.strongly_connected_components(turns):
        for cycle in nx.simple_cycles(turns.subgraph(component), length_bound=limit - 4):
            for i, pair in enumerate(cycle):
                word = tuple(a for a, _ in cycle[i:] + cycle[:i])
                if len(word) >= 4 and len(word) == len(set(word)):
                    all_cycles.setdefault(pair, set()).add(word)

    orbit = cache(lambda mark: mark_orbit(roles, (0, mark)))
    candidates = []
    for cycles in all_cycles.values():
        for a in sorted(cycles):
            for b in sorted(cycles):
                if len(a) + len(b) > limit:
                    continue
                for private in set(b) - set(a):
                    marks = orbit(private)
                    if set(a + b).issuperset(marks):
                        candidates.append((marks, a, b))
    evidence = {"two_parent_groups": sorted(residual), "allowed_turns": sorted(turns.edges)}
    return select_tied(candidates), evidence


def source_word(word, marks):
    repeated = set()
    for width in range(1, len(word) // 2 + 1):
        for start in range(len(word) - 2 * width + 1):
            middle = start + width
            block = word[start:middle]
            if block == word[middle:middle + width]:
                repeated.update(block)
    return any(mark not in repeated for mark in marks)


def word_windows(word, size):
    doubled = word * (1 + (size + len(word) - 1) // len(word))
    return {min(window, window[::-1])
            for i in range(len(word)) for window in [doubled[i:i + size]]}


def release_checks(certificate, anchor):
    by_period = {}
    for a, b in certificate["returns"]:
        copies = 1
        while True:
            word = a * copies + b
            period = len(word)
            if anchor + 2 * period - 1 > HORIZONS[-1] and copies > 1:
                break
            by_period.setdefault(period, set()).add(word)
            copies += 1
    results = []
    for period, words in sorted(by_period.items()):
        launch = 2 * period
        stages = [set().union(*(word_windows(word, q) for word in words))
                  for q in range(launch - 1, launch + 2)]
        assert all(source_word(w, certificate["marks"]) for w in stages[0])
        assert all(not source_word(w, certificate["marks"]) for w in stages[1] | stages[2])
        for old, new in zip(stages, stages[1:]):
            assert all({min(w[:-1], w[:-1][::-1]), min(w[1:], w[1:][::-1])} <= old for w in new)
        results.append({"period": period, "launch_age": anchor + launch - 1,
                        "phases_before_at_after": list(map(len, stages))})
    return results


def distinct_periodic_products(certs, anchor, horizon):
    births = {}
    for cert in certs:
        for a, b in cert["returns"]:
            copies = 1
            while anchor + 2 * (copies * len(a) + len(b)) - 1 <= horizon:
                word = a * copies + b
                period = len(word)
                phases = frozenset(word_windows(word, 2 * period))
                assert len(phases) == period
                births.setdefault(period, set()).add(phases)
                copies += 1
    return [{"period": period, "launch_age": anchor + 2 * period - 1,
             "widths_of_distinct_products": sorted(map(len, distinct)),
             "width_of_tied_union": len(set().union(*distinct))}
            for period, distinct in sorted(births.items())]


def peeled_original(stars):
    _, physical, _ = libraries()
    removed = 0
    while stars:
        _, ordinary, loose = physical.incidence(stars)
        live = set(loose)
        if any(live.intersection(ordinary[knot]) for knot in live):
            return stars, removed
        if not live:
            break
        stars = tuple(row for knot, row in enumerate(stars) if knot not in live)
        removed += 1
    return None, removed


def normalized_reading(certs, indices=None):
    def label(holder):
        return indices[holder] if indices is not None else holder
    return sorted((tuple(sorted(map(label, cert["marks"]))),
                   sorted((tuple(map(label, a)), tuple(map(label, b)))
                          for a, b in cert["returns"]))
                  for cert in certs)


def replay_reader(stars, cut, horizon, certs, law, original, *, residual=False):
    _, physical, operator = libraries()
    changed, names = physical.rename(stars, 2046)
    recovered, depth = peeled_original(changed)
    assert recovered is not None and depth == cut
    assert sorted(map(len, recovered)) == sorted(map(len, original))
    state = operator.from_stars(changed)
    status, _, groups, _ = next_parents(state)
    assert status == "funded"
    if residual:
        under_rename, _ = residual_reading(state, groups, cut, horizon)
    else:
        gates, components = map_gates(state, groups)
        assert gates["identified"]
        under_rename, _ = ways_to_read(components, cut, horizon)
    assert normalized_reading(certs) == normalized_reading(under_rename, names)

    words = {a * copies + b for cert in certs for a, b in cert["returns"] for copies in (1, 2)}
    holders = {(holder,): holder for holder in operator.from_stars(stars).opens}
    checked = []
    for size in range(2, 6):
        state = operator.from_stars(stars)
        status, parents, _, _ = next_parents(state)
        if status != "funded":
            break
        status, born, following = write_cohort(stars, state, law, parents)
        if status != "extend":
            break
        _, old_born, _ = physical.literal_turn(stars, law)
        assert Counter((b.parents, len(b.fresh)) for b in born) == Counter(
            (b.parents, len(b.fresh)) for b in old_born)
        by_parents = {frozenset(birth.parents): birth.knot for birth in born
                      if len(birth.parents) == 2}
        next_holders = {}
        for word in words:
            for window in word_windows(word, size):
                prefixes = (window[:-1], window[1:])
                roster = frozenset(holders[min(part, part[::-1])] for part in prefixes)
                next_holders[window] = by_parents[roster]
        holders = next_holders
        checked.append({"relative_size": size, "all_births": len(born),
                        "window_parent_rosters": len(holders)})
        origin, depth = peeled_original(following)
        assert origin == original and depth == cut + size - 1
        stars = following
    return {"anonymous_relabel": True, "literal_parent_audits": checked}


def roster_repeat(state, age, seen):
    graph = role_incidence(state)
    fingerprint = (tuple(sorted(state.opens.values())), tuple(sorted(map(len, state.blocks))))
    for earlier_age, earlier in seen.get(fingerprint, ()):
        matcher = nx.algorithms.isomorphism.GraphMatcher(
            earlier, graph, node_match=lambda x, y: node_type(x) == node_type(y))
        if matcher.is_isomorphic():
            return {"cuts": [earlier_age, age], "live_width": len(state.opens),
                    "recoding": sorted(matcher.mapping.items())}
    seen.setdefault(fingerprint, []).append((age, graph))
    return None


def compact_roster(state, groups):
    """The complete parent lists, before allocating any distinctions."""
    used = Counter(holder for group in groups for holder in group)
    assert all(used[holder] <= loose for holder, loose in state.opens.items())
    unary = tuple((holder,) for holder, loose in state.opens.items()
                  for _ in range(loose - used[holder]))
    return groups + unary


def turn_components(turns):
    def canonical(word):
        return min(w[i:] + w[:i] for w in (word, word[::-1]) for i in range(len(w)))
    parts, cycles = [], set()
    for part in nx.strongly_connected_components(turns):
        if len(part) < 2:
            continue
        graph = turns.subgraph(part)
        branching = max(dict(graph.out_degree()).values())
        parts.append({"ordered_pairs": len(part), "max_internal_successors": branching,
                      "actual_pair_states": sorted(part)})
        if branching == 1:
            start = min(graph)
            word = [start[0]]
            following, = graph[start]
            while following != start:
                word.append(following[0])
                following, = graph[following]
            cycles.add(canonical(tuple(word)))
    return sorted(parts, key=lambda p: p["actual_pair_states"]), sorted(cycles)


def held_block_bound(state, residual):
    worst = 0
    for block in state.blocks:
        if len(block) < 3:
            continue
        if len(block) == len(state.opens):
            return None
        members = set(block)
        graph = nx.Graph()
        graph.add_nodes_from(block)
        graph.add_edges_from(pair for pair in residual if members.issuperset(pair))
        worst = max(worst, max(map(len, nx.find_cliques(graph))))
    return worst


def compact_extension(original, ordinary_prefix):
    _, _, operator = libraries()
    state = operator.from_stars(original)
    labels = {holder: holder for holder in state.opens}
    next_label = len(original)
    widths, records, ancestry = [], [], {}
    first_common, first_full_cycle, cycle_masks = {}, {}, {}
    expected_cycle = None
    for age in range(HORIZONS[-1] + 1):
        widths.append(len(state.opens))
        groups = bounded_groups(state, FORECAST_CAP)
        if groups is None:
            reason = "joining_group_cap"
            break
        parents = compact_roster(state, groups)
        assert len(parents) > 1  # No law-specific closure through this cut.
        residual, turns = residual_turns(state, groups)
        parts, cycles = turn_components(turns)
        records.append({
            "age": age,
            "open_holders": len(state.opens),
            "next_roster_size": len(parents),
            "next_parent_arity_histogram": dict(sorted(Counter(map(len, parents)).items())),
            "residual_pair_count": len(residual),
            "recurrent_turn_components": parts,
            "unoriented_nonbranching_cycles": cycles,
            "max_residual_clique_in_proper_held_block": held_block_bound(state, residual),
        })
        if expected_cycle is not None:
            pairs = list(zip(expected_cycle, expected_cycle[1:] + expected_cycle[:1], strict=True))
            assert all(turns.has_edge(a, b) for a, b in zip(pairs, pairs[1:] + pairs[:1], strict=True))
        if age == HORIZONS[-1] or len(parents) > COMPACT_CAP:
            reason = "horizon" if age == HORIZONS[-1] else "compact_birth_cap"
            break

        if len(cycles) == 1 and len(cycles[0]) == 4:
            cycle, = cycles
            cycle_masks[age] = sum(1 << v for v in cycle)
            by_roster = {frozenset(group): j for j, group in enumerate(parents) if len(group) == 2}
            expected_cycle = tuple(by_roster[frozenset(pair)]
                                   for pair in zip(cycle, cycle[1:] + cycle[:1], strict=True))
        else:
            expected_cycle = None

        blocks = operator._parent_blocks(parents)
        forecast = operator.End(dict.fromkeys(range(len(parents)), 1), blocks)
        proposals = bounded_groups(forecast, FORECAST_CAP)
        if proposals is None:
            reason = "fresh_forecast_cap"
            break
        demand = Counter(holder for group in proposals for holder in group)
        fresh = tuple(max(demand[j], 3 - len(group), 1) for j, group in enumerate(parents))
        if age < len(ordinary_prefix) and "actual_parent_roster_hash" in ordinary_prefix[age]:
            translated = tuple((tuple(labels[p] for p in group), count)
                               for group, count in zip(parents, fresh, strict=True))
            digest = sha256(repr(translated).encode("ascii")).hexdigest()
            assert digest == ordinary_prefix[age]["actual_parent_roster_hash"]
        records[-1]["literal_prefix_crosscheck"] = (
            age < len(ordinary_prefix) and "actual_parent_roster_hash" in ordinary_prefix[age])

        ancestry[age] = {holder: 1 << holder for holder in state.opens}
        for old_age, old_ancestors in list(ancestry.items()):
            newer = {j: reduce(or_, (old_ancestors[parent] for parent in group))
                     for j, group in enumerate(parents)}
            common = reduce(and_, newer.values())
            ancestry[old_age] = newer
            if common and old_age not in first_common:
                first_common[old_age] = {"all_births_age": age + 1,
                                         "required_older_holders": [i for i in range(common.bit_length())
                                                                    if common >> i & 1]}
            if old_age in cycle_masks:
                if age + 1 == old_age + 2:
                    # The four physical two-step phase rosters omit different
                    # old members. No shared ancestor can occur at two steps.
                    assert common == 0
                if common & cycle_masks[old_age] == cycle_masks[old_age]:
                    first_full_cycle.setdefault(old_age, age + 1)
        labels = {j: next_label + j for j in range(len(parents))}
        next_label += len(parents)
        state = operator.End(dict(enumerate(fresh)), blocks)
    return {
        "compact_width_cap": COMPACT_CAP,
        "age_reached": len(widths) - 1,
        "cohort_widths": widths,
        "stop": reason,
        "exact_rosters": records,
        "any_compulsory_older_holder_by_cut": first_common,
        "entire_four_cycle_compulsory_by_cut": first_full_cycle,
    }


def examine(original, law, legal, horizon):
    _, physical, operator = libraries()
    result = {"legal": legal, "funded": False, "screen": "no", "recurrence": "no",
              "reason": "illegal_source", "trace": []}
    if not legal:
        return result
    assert peeled_original(original) == (original, 0)
    stars = original
    previous_rosters = {}
    scan_capped = False
    for age in range(horizon + 1):
        state = operator.from_stars(stars)
        status, parents, groups, shortages = next_parents(state)
        if age == 0:
            result["funded"] = status == "funded"
        observed = {"age": age, "live": len(state.opens), "roster_status": status}
        result["trace"].append(observed)
        if status in {"stall", "closed"}:
            observed["shortages"] = shortages
            result["reason"] = status
            return result
        if status == "parent_cap":
            break
        observed["planned_births"] = len(parents)
        stopped_cycle = roster_repeat(state, age, previous_rosters)
        if stopped_cycle:
            result.update(reason="bounded_repeating_roster", recurring_roster=stopped_cycle)
            return result
        gates, components = map_gates(state, groups)
        observed.update(gates)
        if gates["identified"]:
            if max(gates["ranks"], default=0) <= 1:
                result["reason"] = "identified_at_most_one_cycle_per_part"
                return result
            certs, survey_cap = ways_to_read(components, age, horizon)
            scan_capped |= survey_cap
            if certs:
                proof = [c | {"packet_phase_checks": release_checks(c, age)} for c in certs]
                first = min(f["launch_age"] for entry in proof for f in entry["packet_phase_checks"])
                assert first <= horizon
                result.update(reason="certified_return_words", screen="yes", recurrence="yes",
                              launch_age=first, proof=proof,
                              distinct_periodic_products=distinct_periodic_products(certs, age, horizon),
                              live_only_prediction="unresolved_for_named_return",
                              reading_audit=replay_reader(stars, age, horizon, certs, law, original))
                return result
        if age == horizon:
            break
        step_status, births, updated = write_cohort(stars, state, law, parents)
        if step_status == "subarity_stop":
            result["reason"] = step_status
            return result
        if step_status != "extend":
            observed["write_status"] = step_status
            status = step_status
            break
        observed["actual_parent_roster_hash"] = sha256(
            repr(tuple((b.parents, len(b.fresh)) for b in births)).encode("ascii")).hexdigest()
        stars = updated
    result.update(reason=status if status != "funded" else "horizon", recurrence="unknown",
                  structural_survey_capped=scan_capped)
    earliest_launch_from_cut = 2 * 8 - 1
    if scan_capped or (status != "funded" and age + 1 + earliest_launch_from_cut <= horizon):
        result["screen"] = "unknown"
    return result


def prove_residual_returns(original, law, horizon):
    _, _, operator = libraries()
    stars = original
    for age in range(horizon - 14):
        state = operator.from_stars(stars)
        status, parents, groups, _ = next_parents(state)
        if status != "funded":
            break
        certs, evidence = residual_reading(state, groups, age, horizon)
        if certs:
            proof = [c | {"packet_phase_checks": release_checks(c, age)} for c in certs]
            first = min(f["launch_age"] for entry in proof for f in entry["packet_phase_checks"])
            assert first <= horizon
            return {
                "anchor_age": age,
                "complete_holding_supports": stars,
                "first_certified_launch_age": first,
                "residual_evidence": evidence,
                "proof": proof,
                "distinct_periodic_products": distinct_periodic_products(certs, age, horizon),
                "reading_audit": replay_reader(stars, age, horizon, certs, law, original, residual=True),
            }
        status, _, stars = write_cohort(stars, state, law, parents)
        if status != "extend":
            break
    return None


def totals(rows, law, horizon, denominator, weights=None):
    chosen = []
    for row in rows:
        evidence = row["by_law"][law][str(horizon)]
        if denominator == "legal" and not evidence["legal"]:
            continue
        if denominator == "funded" and not evidence["funded"]:
            continue
        weight = 1 if weights is None else weights[row["edit"]["operation"]]
        chosen.append((weight, evidence))
    norm = sum(weight for weight, _ in chosen)
    views = {}
    for event in ("legal", "funded", "screen", "recurrence", "recurrence_including_residual_proof"):
        counts = dict.fromkeys(("yes", "no", "unknown"), 0)
        for weight, evidence in chosen:
            outcome = evidence[event]
            if isinstance(outcome, bool):
                outcome = "yes" if outcome else "no"
            counts[outcome] += weight
        assert sum(counts.values()) == norm
        if norm:
            bounds = [Fraction(counts["yes"], norm),
                      Fraction(counts["yes"] + counts["unknown"], norm)]
            views[event] = {"counts_or_mass": {k: str(v) if isinstance(v, Fraction) else v
                                             for k, v in counts.items()},
                            "identification_interval_exact": list(map(str, bounds)),
                            "identification_interval": list(map(float, bounds))}
        else:
            views[event] = {"counts_or_mass": counts, "identification_interval": None}
    return {"units": len(chosen), "weight": str(norm) if isinstance(norm, Fraction) else norm,
            "events": views}


def add_intervals(data):
    n = data["units"]
    if not n:
        return data
    for rates in data["events"].values():
        measured = rates["counts_or_mass"]
        y = measured["yes"]
        upper = y + measured["unknown"]
        lo = float(beta.ppf(.025, y, n - y + 1)) if y else 0.0
        hi = float(beta.ppf(.975, upper + 1, n - upper)) if upper < n else 1.0
        rates["binomial_95"] = [lo, hi]
        detection_upper = float(beta.ppf(.975, y + 1, n - y)) if y < n else 1.0
        rates["detector_binomial_95"] = [lo, detection_upper]
        if not y:
            rates["zero_detections_one_sided_95_upper"] = 1 - 0.05 ** (1 / n)
    return data


def deterministic_controls(source):
    panel, physical, _ = libraries()
    word_a, word_b = (4, 0, 2, 5), (4, 0, 3, 6)
    published = release_checks({"marks": [2, 3], "returns": [(word_a, word_b), (word_b, word_a)]}, 0)
    assert [r["launch_age"] for r in published] == [15, 23, 31]
    assert published[0]["phases_before_at_after"] == [8, 8, 8]
    cycle = physical.source_from([(k, (k + 1) % 5) for k in range(5)], [2] * 5)
    relay = physical.source_from([(0, k) for k in (1, 2, 3)], [1, 2, 2, 2])
    controls = {}
    for law in LAWS:
        start = examine(source, law, panel.legality(source)[law]["lawful"], HORIZONS[-1])
        assert start["recurrence"] == "yes" and start["launch_age"] == 15
        cycle_read = examine(cycle, law, panel.legality(cycle)[law]["lawful"], HORIZONS[-1])
        assert cycle_read["reason"] == "identified_at_most_one_cycle_per_part"
        physical.certify_source(relay, law)
        frames, layers = physical.trajectory(relay, law, 6)
        _, ordinary, loose = physical.incidence(frames[4])
        _, witnessed = physical.witnessed_end(ordinary, loose)
        pair, = [part for part in nx.connected_components(witnessed) if len(part) == 2]
        assert all(witnessed.degree(knot) == 1 and len(loose[knot]) == 2 for knot in pair)
        shared, = [birth for birth in layers[4][0] if set(birth.parents) == pair]
        assert all(any(birth.parents == (knot,) for birth in layers[4][0]) for knot in pair)
        controls[law] = {"return_word": start, "bare_cycle": cycle_read,
                         "relay": {"release_age": 4, "direct_child_age": 5,
                                   "two_lasting_endpoint_families": sorted(pair),
                                   "actual_direct_parents": shared.parents,
                                   "fresh_at_joint_birth": len(shared.fresh),
                                   "recurrent": False}}

    sys.path.insert(0, str(PRIOR))
    explosive = load("four_source_edit_partnered", PRIOR / "explosive.py")
    counts, rosters, excluded = explosive.partnered_kernel()
    _, replay = explosive.partnered_literal(physical, counts, rosters, excluded)
    return {"original_published_marker": published,
            "physical_controls_by_law": controls,
            "explosive": {"description": "order-three partnered runaway",
                          "early_parentage_checks_by_law": replay,
                          "birth_counts_through_age_four": counts,
                          "age_five_birth_count": "2^2043-24",
                          "recurrence": "no",
                          "reason": "every_birth_has_every_two_step_ancestor"}}


def assemble():
    panel, physical, _ = libraries()
    prereg = RESEARCH / "preregistration.md"
    contract = HERE / "contract.json"
    digest = sha256(prereg.read_bytes()).hexdigest()
    assert json.loads(contract.read_bytes())["preregistration_sha256"] == digest

    source = physical.source_from(MEETINGS, LOOSE)
    population = edit_population(source)
    sizes = Counter(edit.operation for edit in population)
    assert [sizes[op] for op in OPERATIONS] == [7, 16, 21, 9]
    rng = Random(SEED)
    ranks = [rng.randrange(len(population)) for _ in range(SAMPLE_COUNT)]
    rows = []
    for atom, edit in enumerate(population):
        edited = edit.applied(source)
        legal = panel.legality(edited)
        laws = {
            law: {str(horizon): examine(edited, law, legal[law]["lawful"], horizon)
                  for horizon in HORIZONS}
            for law in LAWS
        }
        for law in LAWS:
            for horizon in HORIZONS:
                result = laws[law][str(horizon)]
                if result["recurrence"] == "unknown":
                    extra = prove_residual_returns(edited, law, horizon)
                    if extra is not None:
                        result["post_screen_residual_return_proof"] = extra
                result["recurrence_including_residual_proof"] = (
                    "yes" if "post_screen_residual_return_proof" in result else result["recurrence"])
        rows.append({"atom": atom, "edit": asdict(edit), "supports": edited,
                     "local_projection_verdicts": legal, "by_law": laws})

    summary = {}
    weights = {operation: Fraction(1, 4 * sizes[operation]) for operation in OPERATIONS}
    for label, units, masses in (
        ("exact_uniform", rows, None),
        ("exact_equal_operation_classes", rows, weights),
        ("fresh_uniform", [rows[rank] for rank in ranks], None),
    ):
        def cell(law, horizon, denominator):
            data = totals(units, law, horizon, denominator, masses)
            return add_intervals(data) if label == "fresh_uniform" else data
        summary[label] = {
            law: {str(horizon): {denom: cell(law, horizon, denom)
                                 for denom in ("all", "legal", "funded")}
                  for horizon in HORIZONS}
            for law in LAWS
        }
    by_operation = {
        op: {law: {str(horizon): totals([r for r in rows if r["edit"]["operation"] == op],
                                       law, horizon, "all") for horizon in HORIZONS}
             for law in LAWS} for op in OPERATIONS
    }
    inputs = (Path(__file__).resolve(), prereg, contract, PRIOR / "panel.py", PRIOR / "explosive.py",
              Path(physical.__file__), Path(panel.end.__file__),
              ROOT / "research/HEAVY-GROWTH-20261119-001/pure.md",
              ROOT / "research/HEAVY-GROWTH-20261119-001/held_ancestry.md")
    compact = {}
    for row in rows:
        before = row["by_law"]["parity"][str(HORIZONS[-1])]
        if before["recurrence_including_residual_proof"] != "unknown":
            continue
        alternate = row["by_law"]["nae"][str(HORIZONS[-1])]
        assert before["trace"] == alternate["trace"]
        compact[row["atom"]] = compact_extension(row["supports"], before["trace"])
    return {"original_supports": source, "sample_seed": SEED, "sample_ranks": ranks,
            "operation_sizes": sizes, "horizons": HORIZONS, "per_component_birth_cap": CAP,
            "forecast_group_cap": FORECAST_CAP, "catalogue": rows, "summary": summary,
            "by_operation_exact_uniform": by_operation, "controls": deterministic_controls(source),
            "later_compact_diagnostics": compact,
            "sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in inputs}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = json.dumps(assemble(), sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(raw)
    else:
        print(raw, end="")


if __name__ == "__main__":
    main()
