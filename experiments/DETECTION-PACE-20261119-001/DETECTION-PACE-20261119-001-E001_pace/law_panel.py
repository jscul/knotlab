"""Replay the sixteen parity feedback tables on two closed-load preparations."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path
from random import Random
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLDER = "OLD-MARK-GEOMETRY-20261119-001"
sys.path.insert(0, str(ROOT / "experiments" / OLDER / (OLDER + "-E001_marks")))
import sources  # noqa: E402


growth = sources.growth
TABLES = tuple("".join(row) for row in product(growth.ACTIONS, repeat=2))
CAPS = {"junctions": 6000, "distinctions": 32000}
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "law_panel.json"
AGES = {"J1": 8, "J1x2": 4}


def digest(value):
    return sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def holders(stars):
    result = defaultdict(set)
    for knot, support in enumerate(stars):
        for d in support:
            result[d].add(knot)
    assert all(len(row) in (1, 2) for row in result.values())
    return result


def source_graph(stars):
    held = holders(stars)
    graph = nx.Graph()
    for knot, support in enumerate(stars):
        graph.add_node(knot, loose=sum(len(held[d]) == 1 for d in support))
    multiplicities = Counter(tuple(sorted(row)) for row in held.values() if len(row) == 2)
    for (u, v), weight in multiplicities.items():
        graph.add_edge(u, v, multiplicity=weight)
    return graph


def matcher(before, after):
    return nx.algorithms.isomorphism.GraphMatcher(
        before, after,
        node_match=lambda x, y: x["loose"] == y["loose"],
        edge_match=lambda x, y: x["multiplicity"] == y["multiplicity"])


def canonical(shape, maps):
    return min(tuple(sorted((tuple(sorted(transform[p] for p in parents)), fresh)
                            for parents, fresh in shape)) for transform in maps)


def direct_first_plan(graph, live, table, plan):
    """Check the roster and widths independently from the literal first-layer neighbor lists."""
    ordinary = {tuple(sorted(pair)) for v in graph for pair in combinations(graph[v], 2)}
    # Each possible binary proposal has a unique old common holder. Every
    # pairwise proposal triple has one common holder, so there is no unheld one.
    assert all(len(set(graph[u]) & set(graph[v])) == 1 for u, v in ordinary)
    for triple in combinations(graph, 3):
        if all(pair in ordinary for pair in combinations(triple, 2)):
            assert set.intersection(*(set(graph[v]) for v in triple))
    assert ordinary == {tuple(row["parents"]) for row in plan.details["candidate_groups"]}
    retained = {pair for pair in ordinary if table[bool(live.intersection(pair))] != "V"}
    peers = defaultdict(set)
    for u, v in retained:
        peers[u].add(v)
        peers[v].add(u)
    opens = nx.get_node_attributes(graph, "loose")
    expected_roster = Counter({pair: 1 for pair in retained})
    for v in opens:
        unused = opens[v] - len(peers[v])
        assert unused >= 0
        if unused:
            expected_roster[v,] += unused
    assert expected_roster == Counter(birth.parents for birth in plan.births)
    for birth in plan.births:
        group = birth.parents
        hot = bool(live.intersection(group))
        assert birth.active == hot and birth.action == table[hot]
        if len(group) == 1:
            v, = group
            demand, floor = opens[v] - 1, 2
        else:
            u, v = group
            demand = opens[u] + opens[v] - 2 - len(peers[u] & peers[v])
            floor = 1
        baseline = max(floor, demand)
        expected = max(floor, baseline + (birth.action == "+") - (birth.action == "-"))
        assert (birth.demand, birth.baseline, birth.fresh) == (demand, baseline, expected)
    return len(retained)


def peel(stars, initial_size):
    """Recover the source and first layer from current incidence with all values erased."""
    held = holders(stars)
    alive = set(range(len(stars)))
    live = {next(iter(row)) for row in held.values() if len(row) == 1}
    sizes = [len(alive)]
    first = None
    while len(alive) > initial_size:
        assert live and live < alive
        former = alive - live
        assert len(former) >= initial_size
        if len(former) == initial_size:
            first = []
            for child in live:
                parents = []
                fresh = 0
                for d in stars[child]:
                    other = held[d] - {child}
                    if other:
                        parent, = other
                        assert parent in former
                        parents.append(parent)
                    else:
                        fresh += 1
                assert parents and len(set(parents)) == len(parents) and fresh >= 1
                first.append((tuple(sorted(parents)), fresh))
        affected = set()
        for v in live:
            for d in stars[v]:
                held[d].remove(v)
                affected.add(d)
        live = {next(iter(held[d])) for d in affected if len(held[d]) == 1}
        alive = former
        sizes.append(len(alive))
    return sorted(alive), tuple(first or ()), sizes


def current_signature(stars, old, maps):
    survivor, first, sizes = peel(stars, len(old))
    assert survivor == list(range(len(old)))
    assert all(tuple(stars[i]) == old[i] for i in survivor)
    return canonical(first, maps), sizes


def transported_control(stars, old, expect):
    rng = Random(21120261119)
    reverse = list(range(len(stars)))
    rng.shuffle(reverse)
    distinction_ids = sorted(holders(stars))
    labels = distinction_ids.copy()
    rng.shuffle(labels)
    moved = dict(zip(distinction_ids, labels, strict=True))
    recoded = [tuple(moved[d] for d in stars[i]) for i in reverse]
    survivors, actual, sizes = peel(recoded, len(old))
    recovered = source_graph([recoded[i] for i in survivors])
    maps = [{survivors[k]: v for k, v in isometry.items()}
            for isometry in matcher(recovered, source_graph(old)).isomorphisms_iter()]
    assert maps and canonical(actual, maps) == expect
    return {"peel_sizes": sizes, "anonymous_signature": digest(expect)}


def nearest_live(stars, anchors):
    """Read the nearest current loose holders from each old mark and its two holders."""
    incidence = holders(stars)
    opposite = [set() for _ in stars]
    loose_degree = [0] * len(stars)
    for row in incidence.values():
        if len(row) == 1:
            loose_degree[next(iter(row))] += 1
        else:
            a, b = sorted(row)
            opposite[a].add(b)
            opposite[b].add(a)
    front = [v for v, n in enumerate(loose_degree) if n]
    if not front:
        return None
    distance = [-1] * len(stars)
    bases = [0] * len(stars)
    queue = deque(front)
    for i, v in enumerate(front):
        distance[v] = 0
        bases[v] = 1 << i
    while queue:
        v = queue.popleft()
        after = distance[v] + 1
        for w in opposite[v]:
            if distance[w] == -1:
                distance[w] = after
                queue.append(w)
            if distance[w] == after:
                bases[w] |= bases[v]
    assert all(d >= 0 for d in distance)

    def histogram(mask):
        result = Counter()
        while mask:
            bit = mask & -mask
            mask ^= bit
            result[loose_degree[front[bit.bit_length() - 1]]] += 1
        return [[degree, count] for degree, count in sorted(result.items())]

    def read(hops, basis):
        parts = histogram(basis)
        return {"incidence_hops": hops, "by_loose_degree": parts,
                "nearest_knots": sum(n for _, n in parts),
                "loose_distinctions": sum(loose * n for loose, n in parts)}

    reports = {}
    for mark in anchors:
        u, v = sorted(incidence[mark])
        depth = min(distance[u], distance[v])
        mask = 0
        for k in (u, v):
            if distance[k] == depth:
                mask |= bases[k]
        reports[str(mark)] = {"from_mark": read(2 * depth + 1, mask),
                              "from_holders": {str(k): read(2 * distance[k], bases[k]) for k in (u, v)}}
    return reports


def check_nearest(stars, reports):
    """Independently select all nearest live holders in the typed incidence graph."""
    incidence = holders(stars)
    graph = nx.Graph()
    graph.add_edges_from((("knot", k), ("distinction", d)) for d, row in incidence.items() for k in row)
    degrees = Counter(next(iter(row)) for row in incidence.values() if len(row) == 1)
    for mark in ("0", "8", "12", "15"):
        entry = reports[mark]
        tests = [(("distinction", int(mark)), entry["from_mark"])]
        tests.extend((("knot", int(k)), outcome) for k, outcome in entry["from_holders"].items())
        for root, outcome in tests:
            all_distances = nx.single_source_shortest_path_length(graph, root)
            least = min(all_distances["knot", k] for k in degrees)
            histogram = Counter(n for k, n in degrees.items() if all_distances["knot", k] == least)
            assert least == outcome["incidence_hops"]
            assert [list(pair) for pair in sorted(histogram.items())] == outcome["by_loose_degree"]


def stage_row(frame, signature, peel_sizes, anchors):
    stars = frame["stars"]
    birth = frame["births"]
    occupied = set(frame["occupied"])
    result = {"knots": frame["junction_count"], "distinctions": frame["distinction_count"],
              "new_knots": len(birth), "new_distinctions": sum(len(row["fresh"]) for row in birth),
              "birth_arities": dict(Counter(len(row["parents"]) for row in birth)),
              "live_loose_degrees": dict(Counter(len(ds) for ds in frame["loose"].values())),
              "open": bool(frame["live"]), "old_values_preserved": True,
              "occupied_loose_distinctions": sum(d in occupied
                                                  for ds in frame["loose"].values() for d in ds),
              "first_signature_from_current": digest(signature) if signature else None,
              "knots_after_successive_peels": peel_sizes}
    if anchors is not None:
        result["nearest_live"] = nearest_live(stars, anchors)
    return result


def simulate_trace(source, first, cold, signature, maps, depth, anchors, check_transport):
    old = tuple(map(tuple, source))
    occupied = first["occupied"]
    base = growth.grow(source, occupied, (cold, cold), rounds=0)["stages"]["0"]
    result = {"0": stage_row(base, (), [len(old)], anchors)}
    frame = first
    recoding = None
    termination = {"status": "age_limit", "last_age": depth}
    for age in range(1, depth + 1):
        assert frame["status"] == "extend"
        assert frame["occupied"] == occupied and not frame["new_occupied"]
        assert not any(set(row).intersection(occupied) for row in frame["loose"].values())
        if not frame["live"]:
            result[str(age)] = stage_row(frame, (), None, anchors)
            termination = {"status": "closed", "last_age": age}
            break
        observed, backward = current_signature(frame["stars"], old, maps)
        expected = [frame["junction_count"], *(result[str(t)]["knots"] for t in range(age - 1, -1, -1))]
        assert observed == signature and backward == expected
        result[str(age)] = stage_row(frame, observed, backward, anchors)
        if anchors is not None and age <= 2:
            check_nearest(frame["stars"], result[str(age)]["nearest_live"])
        if check_transport and age == 3:
            recoding = {"age": age, **transported_control(frame["stars"], old, observed)}
        shortages = {b["knot"]: b["demand"] - len(b["fresh"]) for b in frame["births"]
                     if cold != "V" and b["demand"] > len(b["fresh"])}
        result[str(age)]["next_exact_shortages_if_attempted"] = shortages
        result[str(age)]["next_round_funding_sufficient"] = not shortages
        if age == depth:
            break
        following = growth.step(frame["stars"], occupied, (cold, cold), caps=CAPS)
        assert (following["status"] == "stall") == bool(shortages)
        if shortages:
            assert following["shortages"] == shortages
        if following["status"] != "extend":
            termination = {"last_age": age, "attempted_age": age + 1,
                           **{k: v for k, v in following.items() if k not in ("candidate_groups", "lookahead_groups")}}
            break
        if cold == "V":
            expected_loose = Counter()
            for ports in frame["loose"].values():
                expected_loose[max(2, len(ports) - 1)] += len(ports)
            assert expected_loose == Counter(len(ports) for ports in following["loose"].values())
        # In the shared-only sector every successful stage is followed only by
        # the cold action. The nominal hot entry on this continuation is inert.
        assert not following["hot_live_parents"]
        frame = following
    return {"cold": cold, "termination": termination, "frames": result, "later_recoding": recoding}


def birth_rows(plan):
    return [[birth.parents, birth.active, birth.action, birth.demand,
             birth.baseline, birth.fresh, birth.clipped] for birth in plan.births]


def equal_size_examples(table, words, traces):
    summary = defaultdict(Counter)
    example = {}
    later_by_dose = defaultdict(Counter)
    for a, b in combinations(words, 2):
        if words[a]["weight"] != words[b]["weight"]:
            continue
        d = words[a]["weight"]
        x, y = (table[w] for w in (a, b))
        different = x["anonymous_first_signature"] != y["anonymous_first_signature"]
        same_totals = x["first_totals"] == y["first_totals"]
        summary[d]["word_pairs"] += 1
        summary[d]["different_geometry"] += different
        summary[d]["different_geometry_same_knot_and_distinction_totals"] += different and same_totals
        if different:
            mode = "same_totals" if same_totals else "different_totals"
            example.setdefault(mode, [a, b])
            left, right = [traces[row["continuation"]]["frames"] for row in (x, y)]
            for age in sorted(set(left) & set(right), key=int):
                if int(age) > 1 and all(left[age][name] == right[age][name] for name in ("knots", "distinctions")):
                    later_by_dose[d][age] += 1
                    example.setdefault("equal_totals_after_first_layer", [a, b, int(age)])
    return {k: dict(v) for k, v in summary.items()}, example, dict(later_by_dose)


def compare_table(table, load_rows, traces, words):
    quiet = next(k for k in words if not words[k]["occupied"])
    baseline = load_rows[quiet]
    base_trace = traces[baseline["continuation"]]
    result = {}
    for code, loaded in load_rows.items():
        current = traces[loaded["continuation"]]
        same = loaded["anonymous_first_signature"] == baseline["anonymous_first_signature"]
        same_roster = loaded["first_roster"] == baseline["first_roster"]
        cls = "same" if same else "fresh counts" if same_roster else "roster"
        if not same and same_roster:
            # P, plus, and the clipped minus are monotone width changes on each
            # fixed plan row. V's unary width equals P's.
            qtotal, ltotal = baseline["first_totals"][1], loaded["first_totals"][1]
            assert qtotal != ltotal
        common = sorted(set(base_trace["frames"]) & set(current["frames"]), key=int)
        equal_counts = [age for age in common if (base_trace["frames"][age]["knots"], base_trace["frames"][age]["distinctions"]) ==
                        (current["frames"][age]["knots"], current["frames"][age]["distinctions"])]
        finite = {"stall", "arity_stop", "closed"}
        qstop, lstop = base_trace["termination"], current["termination"]
        result[code] = {"first_uncolored_difference": None if same else 1, "kind": cls,
                        "matched_ages": list(map(int, common)),
                        "matched_ages_same_totals": list(map(int, equal_counts)),
                        "unilateral_structural_stop": (qstop["status"] in finite) != (lstop["status"] in finite),
                        "base_termination": qstop["status"], "loaded_termination": lstop["status"]}
        if same:
            assert base_trace["termination"] == current["termination"]
        if table[0] == table[1]:
            assert same and loaded["continuation"] == baseline["continuation"]
    return result


def compare_live(quiet, loaded, anchors, seam):
    first_by_mark, first_joint, first_individual = {}, {}, defaultdict(dict)
    by_age = {}
    for age in sorted(set(quiet["frames"]) & set(loaded["frames"]), key=int):
        difference = {}
        q = quiet["frames"][age]["nearest_live"]
        l = loaded["frames"][age]["nearest_live"]
        for i, d in enumerate(anchors):
            tag = str(d)
            offset = min(abs(i - seam), abs(i + 1 - seam))
            find = q[tag]["from_mark"], l[tag]["from_mark"]
            individual = q[tag]["from_holders"], l[tag]["from_holders"]
            assert find[0]["incidence_hops"] == find[1]["incidence_hops"] == 2 * int(age) + 1
            assert individual[0].keys() == individual[1].keys()
            if find[0] != find[1]:
                first_joint.setdefault(tag, [int(age), offset])
            for k, reading in individual[0].items():
                assert reading["incidence_hops"] == individual[1][k]["incidence_hops"] == 2 * int(age)
                if reading != individual[1][k]:
                    first_individual[tag].setdefault(k, int(age))
            if find[0] != find[1] or individual[0] != individual[1]:
                difference[tag] = {"offset": offset, "joint": find, "holders": individual}
                first_by_mark.setdefault(tag, [int(age), offset])
        by_age[age] = difference
    return {"first_difference_by_mark": first_by_mark, "first_joint_difference": first_joint,
            "first_individual_holder_difference": dict(first_individual), "differences_by_age": by_age}


def allocation_control():
    """Exhaust old ports and minimum lifts on the three-knot confluence witness."""
    stars = ((0, 2, 3), (0, 1, 4), (1, 5, 6))
    source = {frozenset(row) for row in stars}
    outcomes = {}
    for name, occupied in (("quiet", frozenset()), ("mixed", frozenset((0, 1, 2, 5)))):
        renamings = [
            p for p in permutations(range(7))
            if {frozenset(p[d] for d in support) for support in stars} == source
            and frozenset(p[d] for d in occupied) == occupied]
        outcomes[name] = {}
        for table in TABLES:
            plan = growth.plan_round(stars, occupied, table)
            assert plan.status == "extend"
            live = list(plan.stage.loose)
            colored, pointwise, active = set(), set(), Counter()
            for orders in product(*(tuple(permutations(plan.stage.loose[k])) for k in live)):
                ports = {k: iter(order) for k, order in zip(live, orders, strict=True)}
                consumed = [tuple(next(ports[k]) for k in birth.parents) for birth in plan.births]
                odd = [i for i, row in enumerate(consumed) if len(occupied.intersection(row)) % 2]
                for choices in product(*(range(plan.births[i].fresh) for i in odd)):
                    order = iter(choices)
                    frame = growth.realize_round(plan, allocation=consumed,
                                                 choose_fresh=lambda names: names[next(order)])
                    lit = set(frame["new_occupied"])

                    def signature(permutation):
                        return tuple(sorted((tuple(sorted(permutation[d] for d in row)), birth.fresh,
                                             int(not lit.isdisjoint(frame["fresh"][k])))
                                            for k, (row, birth) in enumerate(zip(consumed, plan.births, strict=True), 3)))

                    colored.add(min(signature(p) for p in renamings))
                    pointwise.add(signature(tuple(range(7))))
                    active[len(lit)] += 1
            actual_color = name == "quiet" or table[1] == "V"
            actual_names = table[0 if name == "quiet" else 1] == "V"
            assert (len(colored) == 1) == actual_color and (len(pointwise) == 1) == actual_names
            outcomes[name][table] = {"colored_outcomes": len(colored), "pointwise_old_outcomes": len(pointwise),
                                     "choices_by_new_occupied_count": dict(active)}
    return {"stars": stars, "mixed_occupied": [0, 1, 2, 5], "outcomes": outcomes}


def build_case(spec, depth):
    source = tuple(map(tuple, growth.predecessor().source_stars(spec)))
    graph = source_graph(source)
    maps = list(matcher(graph, graph).isomorphisms_iter())
    assert maps
    old_held = holders(source)
    words = {}
    activity_loads = {}
    for code, occupied in sources.loads(spec).items():
        growth._state(source, occupied)
        assert all(len(old_held[d]) == 2 for d in occupied)
        assert set(spec["roles"]["anchors"]).isdisjoint(occupied)
        active = tuple(i for i, support in enumerate(source) if not occupied.isdisjoint(support))
        activity_loads.setdefault(active, (code, occupied))
        words[code] = {"occupied": sorted(occupied), "weight": len(occupied),
                       "activity": activity_loads[active][0]}
    continuations, requests, table_rows, signatures = {}, {}, {}, {}
    for table in TABLES:
        unique = {}
        for active, (code, occupied) in activity_loads.items():
            plan = growth.plan_round(source, occupied, table, caps=CAPS)
            assert plan.status == "extend"
            retained = direct_first_plan(graph, set(active), table, plan)
            frame = growth.realize_round(plan)
            assert frame["occupied"] == sorted(occupied) and not frame["new_occupied"]
            shape = tuple(sorted((birth.parents, birth.fresh) for birth in plan.births))
            first = canonical(shape, maps)
            label = digest(first)
            assert signatures.setdefault(label, first) == first
            physical = (table[0], tuple(map(tuple, frame["stars"])))
            run = continuations.setdefault(physical, str(len(continuations)))
            if run not in requests:
                requests[run] = [frame, table[0], first, False]
            assert requests[run][2] == first
            if spec["id"] == "J1" and table[1] == "V":
                requests[run][3] = True
            unique[code] = {"active_source_knots": active, "retained_multi": retained,
                            "candidate_multi": len(plan.details["candidate_groups"]),
                            "first_roster": sorted(Counter(birth.parents for birth in plan.births).items()),
                            "anonymous_first_signature": label,
                            "first_totals": [frame["junction_count"], frame["distinction_count"]],
                            "births": birth_rows(plan), "continuation": run}
        table_rows[table] = unique
    traces, notes = {}, {}
    anchors = spec["roles"]["anchors"]
    q = next(code for code, word in words.items() if not word["occupied"])
    full = next(code for code, word in words.items()
                if len(word["occupied"]) == len(spec["roles"]["ring_edges"][0]))
    vivid = table_rows["PV"][words[full]["activity"]]["continuation"]
    for key, (first_frame, cold, signature, read_near) in requests.items():
        traces[key] = simulate_trace(source, first_frame, cold, signature, maps, depth,
                                     anchors if read_near else None, key == vivid)
    for table, rows in table_rows.items():
        read_words = {code: rows[word["activity"]] for code, word in words.items()}
        same_weight, exemplars, later_equal = equal_size_examples(read_words, words, traces)
        metadata = {"first_by_activity": rows, "same_weight_classes": same_weight,
                    "same_weight_witness_words": exemplars,
                    "same_weight_unequal_geometry_equal_later_totals_by_age": later_equal,
                    "against_quiet": compare_table(table, read_words, traces, words),
                    "quiet_word": q, "full_single_copy_word": full,
                    "anonymous_first_geometries": len({row["anonymous_first_signature"] for row in rows.values()})}
        if spec["id"] == "J1" and table[1] == "V":
            quiet, loaded = read_words[q], read_words[full]
            metadata["nearest_live_comparison"] = compare_live(
                traces[quiet["continuation"]], traces[loaded["continuation"]], anchors,
                spec["roles"]["seams"][0])
        notes[table] = metadata
        print(spec["id"], table, metadata["against_quiet"][full]["kind"],
              metadata["anonymous_first_geometries"], "activity geometries tested", flush=True)
    example, _, structure, _ = requests[vivid]
    return {"roles": spec["roles"], "source_stars": source, "physical_loads": words,
            "source_knot_automorphisms": maps, "shared_only_activity_count": len(activity_loads),
            "continuation_count": len(traces), "tables": notes, "continuations": traces,
            "recoding_check": transported_control(example["stars"], source, structure)}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", choices=tuple(AGES), default=list(AGES))
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    data = {"schema": 1, "caps": CAPS, "depths": AGES,
            "fixture_sha256": sha256((HERE / "inputs.json").read_bytes()).hexdigest(),
            "birth_columns": ["parents", "hot", "action", "demand", "ordinary_fresh", "fresh", "minus_clipped"],
            "general_old_color_confluence": [table for table in TABLES if table[1] == "V"],
            "general_pointwise_old_confluence": ["VV"], "shared_only_old_color_confluence": TABLES,
            "structurally_blind": [table for table in TABLES if table[0] == table[1]],
            "allocation_control": allocation_control(),
            "terminal_codes": {"closed": "structural closure", "arity_stop": "structural arity obstruction",
                               "stall": "exact funding shortage", "age_limit": "frozen analysis limit",
                               "junction_cap": "physical knot cap", "distinction_cap": "physical distinction cap"},
            "cases": {}}
    for name in args.cases:
        data["cases"][name] = build_case(sources.cases()[name], AGES[name])
        args.out.write_text(json.dumps(data, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
