"""Exhaust small single-meeting presentations and their compatible ordinary origins."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations, permutations
import json
from pathlib import Path
from random import Random
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "minima.json"
sys.path.insert(0, str(ROOT / "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins"))
sys.path.insert(0, str(ROOT / "tools"))
import joinlib as ordinary
from knotlab import Relation, check_knot

KNOT_CAP = 4
DISTINCTION_CAP = 9
WITNESS_EXTENSION_CAP = 16
LAWS = ("parity", "nae")


def owners(stars):
    places = defaultdict(list)
    for i, support in enumerate(stars):
        assert len(support) == len(set(support))
        for d in support:
            places[d].append(i)
    assert all(len(xs) in (1, 2) for xs in places.values())
    return dict(places)


def connected(n, edges):
    return ordinary.connected(n, edges)


@cache
def canonical_incidence(n, edges, loose):
    return min((tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in edges)),
                tuple(loose[p.index(a)] for a in range(n))) for p in permutations(range(n)))


def profile(stars):
    places = owners(stars)
    edges = tuple(sorted(tuple(v) for v in places.values() if len(v) == 2))
    loose = Counter(v[0] for v in places.values() if len(v) == 1)
    assert len(edges) == len(set(edges)) and connected(len(stars), edges)
    return canonical_incidence(len(stars), edges, tuple(loose[j] for j in range(len(stars))))


def bounded_compositions(n, budget):
    if n == 0:
        yield ()
    else:
        for x in range(budget + 1):
            for rest in bounded_compositions(n - 1, budget - x):
                yield (x, *rest)


def sources():
    """Exactly one representative per connected simple support type within both caps."""
    table = {}
    for n in range(1, KNOT_CAP + 1):
        pairs = tuple(combinations(range(n), 2))
        seen = set()
        for k in range(n - 1, len(pairs) + 1):
            for graph in combinations(pairs, k):
                if not connected(n, graph):
                    continue
                degree = Counter(a for e in graph for a in e)
                floor = tuple(max(0, 3 - degree[j]) for j in range(n))
                for extra in bounded_compositions(n, DISTINCTION_CAP - k - sum(floor)):
                    loose = tuple(a + b for a, b in zip(floor, extra, strict=True))
                    key = canonical_incidence(n, graph, loose)
                    if key not in seen:
                        seen.add(key)
                        edges, ends = key
                        counts = Counter(a for e in edges for a in e)
                        stars = ordinary.stars_from([counts[j] + ends[j] for j in range(n)], edges)
                        table[n, key] = tuple(map(tuple, stars))
    return table


@cache
def exact_states(stars, law):
    names = tuple(sorted(owners(stars)))
    assert len(names) <= WITNESS_EXTENSION_CAP
    positions = {d: i for i, d in enumerate(names)}
    masks = tuple(sum(1 << positions[d] for d in row) for row in stars)
    keep = ((lambda row, m: (row & m).bit_count() % 2 == 0) if law == "parity" else
            (lambda row, m: 0 < row & m < m))
    rows = tuple(a for a in range(1 << len(names)) if all(keep(a, m) for m in masks))
    return names, rows


@cache
def local_relation(arity, law):
    return tuple(x for x in range(1 << arity) if
                 (x.bit_count() % 2 == 0 if law == "parity" else x not in (0, (1 << arity) - 1)))


def project(names, rows, mark):
    coords = [names.index(d) for d in mark]
    return tuple(sorted({sum(((x >> q) & 1) << j for j, q in enumerate(coords)) for x in rows}))


@cache
def lawful(stars, law):
    names, rows = exact_states(stars, law)
    return bool(rows) and all(len(row) >= 3 and project(names, rows, row) == local_relation(len(row), law)
                              for row in stars)


def certify_knot(stars, law):
    names, rows = exact_states(stars, law)
    sizes = []
    for held in stars:
        projected = project(names, rows, held)
        locations = tuple(str(d) for d in held)
        relation = Relation(locations, frozenset(tuple(bool((r >> i) & 1) for i in range(len(held))) for r in projected))
        assert check_knot(relation, locations[:-1], locations[-1]).is_knot
        sizes.append(len(projected))
    return sizes


@dataclass(frozen=True)
class Birth:
    index: int
    parents: tuple
    used: tuple
    fresh: tuple

    @property
    def support(self):
        return self.used + self.fresh


def complete_step(P, law):
    n = len(P.bits_of)
    old_owners = {d: tuple(js) for d, js in P.owner.items()}
    if law == "parity":
        rule = ordinary.S.gf2(ordinary.F.fewest)
    else:
        # Each candidate takes just one loose input per parent. The inherited
        # NAE coloring lemma gives a constant input row, so there is no implied birth.
        def rule(P, info, random):
            for row in info:
                row["implied"] = False
            return ordinary.F.fewest(P, info, random)
    result = P.step(rule, None)
    if result is None:
        return "stall", ()
    if result["new"] == 0:
        return "closed", ()
    births = []
    for j in range(n, len(P.bits_of)):
        p = P.parents[j]
        incoming, fresh = tuple(P.bits_of[j][:p]), tuple(P.bits_of[j][p:])
        ps = tuple(old_owners[d][0] for d in incoming)
        assert ps == tuple(sorted(set(ps))) and all(len(old_owners[d]) == 1 for d in incoming)
        births.append(Birth(j, ps, incoming, fresh))
    return "funded", tuple(births)


def reference(source, law):
    P = ordinary.S.from_junctions(source)
    layers = []
    for _ in range(KNOT_CAP - len(source) + 1):
        status, step = complete_step(P, law)
        if status != "funded":
            return layers, status
        layers.append(step)
    return layers, "lookahead_complete"


def fixed_map_gates(source):
    P = ordinary.S.from_junctions(source)
    live = [j for j in range(len(source)) if P.loose(j)]
    groups = P.groups_among(live)
    use = Counter(j for group in groups for j in group)
    return {"no_initial_unheld_triple": all(len(g) == 2 for g in groups),
            "at_most_one_common_holder_per_live_pair": all(len(P.nbr[a] & P.nbr[b]) <= 1
                                                               for a, b in combinations(live, 2)),
            "initially_funded": all(use[j] <= len(P.loose(j)) for j in live),
            "at_least_two_loose": sum(len(P.loose(j)) for j in live) >= 2}


def ready_births(layers, built):
    return tuple(e for layer in layers for e in layer if e.index not in built and set(e.parents) <= built)


def remaining_cohort(layers, built, final):
    for i, layer in enumerate(layers):
        rest = tuple(e for e in layer if e.index not in built)
        if rest:
            mixed = any(e.index in built for later in layers[i + 1:] for e in later)
            return None if mixed else ("funded", rest, len(rest) == len(layer))
    assert final != "lookahead_complete"
    return final, (), True


def indexed_events(events, ids):
    return tuple((tuple(sorted(ids[p] for p in e.parents)), len(e.fresh), e.used) for e in events)


def compare(continued, restarted):
    lc, rc = (Counter(p for p, _, _ in group) for group in (continued, restarted))
    shared = [(p, k, f, d, e) for p, k, d in continued for q, f, e in restarted if p == q and k != f]
    return lc != rc, shared


def rename_control(stars, law, future, source, layers, trace, continued):
    rng = Random(20261120862)
    holder_order = list(range(len(stars)))
    rng.shuffle(holder_order)
    position = {j: i for i, j in enumerate(holder_order)}
    keys, allowed = exact_states(stars, law)
    new_keys = [100 + 3 * i for i in range(len(keys))]
    rng.shuffle(new_keys)
    names = dict(zip(keys, new_keys, strict=True))
    moved = tuple(tuple(names[d] for d in reversed(stars[j])) for j in holder_order)
    status, ver = complete_step(ordinary.S.from_junctions(moved), law)
    recorded = Counter((tuple(sorted(position[j] for j in parents)), h) for parents, h, _ in future)
    got = Counter((e.parents, len(e.fresh)) for e in ver)
    assert recorded == got
    ren_names, ren_allowed = exact_states(moved, law)
    contents = project(ren_names, ren_allowed, tuple(names[d] for d in keys))
    assert contents == allowed
    assert lawful(moved, law)
    queries = {d for _, _, inputs in continued for d in inputs}
    previous = source
    audited = []
    for i, layer in enumerate(layers, 1):
        if any(e.index in trace or set(e.used) <= queries for e in layer):
            all_names = names.copy()
            for d in sorted(owners(previous).keys() - names.keys()):
                all_names[d] = 1000 + 11 * len(all_names)
            order = list(range(len(previous)))
            rng.shuffle(order)
            ids = {j: k for k, j in enumerate(order)}
            other = tuple(tuple(all_names[d] for d in reversed(previous[j])) for j in order)
            status2, actual = complete_step(ordinary.S.from_junctions(other), law)
            old_counts = Counter((tuple(sorted(ids[p] for p in e.parents)), len(e.fresh)) for e in layer)
            assert status2 == "funded" and old_counts == Counter((e.parents, len(e.fresh)) for e in actual)
            audited.append(i)
        previous += tuple(e.support for e in layer)
    return {"new_holder_order": holder_order, "renamed_distinctions_in_old_order": new_keys, "status": status,
            "independent_continued_complete_predecessors": audited}


def literal_extensions(stars, same_inputs, counts, law):
    names, old_rows = exact_states(stars, law)
    outcomes = []
    for h in counts:
        support = (*same_inputs, *range(max(names) + 1, max(names) + 1 + h))
        stage = stars + (support,)
        columns, rows = exact_states(stage, law)
        assert lawful(stage, law) and project(columns, rows, names) == old_rows
        outcomes.append({"new_support": support, "states": len(rows), "old_rows_preserved": True})
    return outcomes


def witness(stars, order, source, layers, trace, law, scope, continued, restarted, restart_status, common=None):
    names, cases = exact_states(stars, law)
    report = {"knots": len(stars), "distinctions": len(names), "source": source, "reached_supports": stars,
              "current_holder_ids_in_reference": order, "literal_birth_trace": [], "allowed_columns": names,
              "whole_allowed_states": cases, "actual_local_projection_sizes": certify_knot(stars, law),
              "law": law, "scope": scope, "continued_moves": continued, "restart_moves": restarted,
              "restart_status": restart_status,
              "source_fixed_map_gates": fixed_map_gates(source),
              "renaming": rename_control(stars, law, restarted, source, layers, trace, continued)}
    source_ids = set(range(len(source)))
    for j in trace:
        index, e = next((i, e) for i, layer in enumerate(layers, 1) for e in layer if e.index == j)
        assert set(e.parents) <= source_ids
        report["literal_birth_trace"].append({"depth": index, "parents": e.parents, "consumed": e.used, "fresh": e.fresh,
                                              "reference_holder": j})
        source_ids.add(j)
    if common:
        parents, h1, h2, continued_names, restart_names = common
        held = owners(stars)
        assert all(held[d] == held[g] == [j] for j, d, g in zip(parents, continued_names, restart_names, strict=True))
        report["same_inputs"] = {"parents": parents, "physical_distinctions": continued_names,
                                 "restart_preallocation_before_renaming_loose_slots": restart_names,
                                 "source_parents": [j for j in parents if order[j] < len(source)],
                                 "continued_fresh": h1, "restarted_fresh": h2,
                                 "literal_extensions": literal_extensions(stars, continued_names, (h1, h2), law)}
    return report


def score(source, law, lawful_types):
    layers, final = reference(source, law)
    if not layers:
        return {}, Counter()
    best = {}
    totals = Counter()
    admitted = all(fixed_map_gates(source).values())
    def store(category, data, common=None):
        stars, order, trace, scope, c, r, status = data
        size = len(stars), len(owners(stars))
        tags = ["all"]
        if all(len(row) == 3 for row in stars):
            tags.append("all_ternary")
        for domain in tags:
            key = "/".join((scope, domain, category))
            if key not in best or size < (best[key]["knots"], best[key]["distinctions"]):
                best[key] = witness(stars, order, source, layers, trace, law, scope, c, r, status, common)

    written = set(range(len(source)))
    events = {e.index: e for layer in layers for e in layer}
    seen = set()

    def visit(built, trace):
        if built in seen:
            return
        seen.add(built)
        order = tuple(sorted(built))
        stars = source + tuple(events[j].support for j in order if j in events)
        ready = ready_births(layers, built)
        if trace:
            assert lawful(stars, law)
            n, w = len(stars), len(owners(stars))
            assert (n, profile(stars)) in lawful_types
            totals[n, w, "reference_fragments"] += 1
            if admitted:
                totals[n, w, "reference_fragments_on_identified_sources"] += 1
            ids = {j: i for i, j in enumerate(order)}
            s, restart = complete_step(ordinary.S.from_junctions(stars), law)
            r = indexed_events(restart, dict(enumerate(range(n))))
            cohort = remaining_cohort(layers, built, final)
            readings = [("full_reference_ready", ready)]
            if cohort is not None:
                if cohort[2]:
                    boundary = indexed_events(cohort[1], ids)
                    assert cohort[0] == s and not any(compare(boundary, r))
                    assert not any(compare(indexed_events(ready, ids), r))
                    totals[n, w, "exact_complete_boundary_restarts"] += 1
                else:
                    readings.append(("remaining_cohort", cohort[1]))
                    totals[n, w, "proper_cohort_prefixes"] += 1
            else:
                totals[n, w, "strictly_mixed_fragments"] += 1
            for scope, current in readings:
                c = indexed_events(current, ids)
                different, shared = compare(c, r)
                data = stars, order, trace, scope, c, r, s
                totals[n, w, scope + "_comparisons"] += 1
                if different:
                    totals[n, w, scope + "_roster_collision"] += 1
                    store("different_parent_roster", data)
                if shared:
                    totals[n, w, scope + "_count_collision"] += 1
                    store("different_common_count", data, shared[0])
                    original = next((x for x in shared if all(order[j] < len(source) for j in x[0])), None)
                    if original:
                        totals[n, w, scope + "_original_count_collision"] += 1
                        store("different_common_count_all_parents_original", data, original)
                    multi = next((x for x in shared if len(x[0]) > 1), None)
                    if multi:
                        totals[n, w, scope + "_multi_count_collision"] += 1
                        store("different_common_multi_count", data, multi)
                    multi_original = next((x for x in shared if len(x[0]) > 1 and
                                           all(order[j] < len(source) for j in x[0])), None)
                    if multi_original:
                        store("different_common_multi_count_all_parents_original", data, multi_original)
        if len(stars) >= KNOT_CAP:
            return
        names, states = exact_states(stars, law)
        for e in ready:
            if len(names) + len(e.fresh) > DISTINCTION_CAP or len(e.support) < 3:
                continue
            after = built | {e.index}
            if after in seen:
                continue
            child = source + tuple(events[j].support for j in sorted(after) if j in events)
            child_names, child_states = exact_states(child, law)
            assert project(child_names, child_states, names) == states
            assert lawful(child, law)
            visit(after, (*trace, e.index))

    visit(frozenset(written), ())
    return best, totals


def closing_control():
    stars = ((0, 1, 3), (0, 2, 4), (1, 2, 5))
    result = {}
    for law in LAWS:
        names, rows = exact_states(stars, law)
        assert lawful(stars, law)
        state = ordinary.S.from_junctions(stars)
        status, births = complete_step(state, law)
        e, = births
        actual = project(names, rows, e.used)
        assert status == "funded" and e.parents == (0, 1, 2) and e.used == (3, 4, 5)
        assert len(e.fresh) == (law == "nae")
        assert actual == (local_relation(3, law) if law == "parity" else tuple(range(8)))
        aft = stars + (e.support,)
        new_names, new_rows = exact_states(aft, law)
        assert lawful(aft, law) and project(new_names, new_rows, names) == rows
        result[law] = {"actual_input_assignments": actual, "fresh": e.fresh, "new_canonical_support": e.support,
                       "loose_distinctions_after_birth": sum(len(v) == 1 for v in owners(aft).values())}
    return {"source": stars, "laws": result}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    originals = sources()
    result = {"max_knots": KNOT_CAP, "max_distinctions": DISTINCTION_CAP, "laws": {}, "closing_control": closing_control(),
              "note": "Full reference-ready includes mixed parent-closed subfamilies; remaining cohort uses proper unfinished layers."}
    for law in LAWS:
        legal = {key for key, stars in originals.items() if lawful(stars, law)}
        types = Counter()
        least = {}
        all_stats = Counter()
        for key, stars in originals.items():
            width = len(owners(stars))
            types[len(stars), width, "candidate_types"] += 1
            if key not in legal:
                continue
            types[len(stars), width, "lawful_types"] += 1
            status, _ = complete_step(ordinary.S.from_junctions(stars), law)
            types[len(stars), width, status] += 1
            if len(stars) >= KNOT_CAP:
                continue
            observed, stats = score(stars, law, legal)
            all_stats.update(stats)
            for category, entry in observed.items():
                old = least.get(category)
                if old is None or (entry["knots"], entry["distinctions"]) < (old["knots"], old["distinctions"]):
                    least[category] = entry
        result["laws"][law] = {"present_type_counts": [[*k, v] for k, v in sorted(types.items())],
                               "prefix_counts": [[*k, v] for k, v in sorted(all_stats.items())], "minima": least}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
