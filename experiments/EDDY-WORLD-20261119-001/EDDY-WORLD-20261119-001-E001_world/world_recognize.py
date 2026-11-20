"""Read branching cycles from anonymous literal incidence and check their finite readouts."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
sys.path.insert(0, str(ROOT / "proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead"))
sys.path.insert(0, str(ROOT / "experiments/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached"))
import deadlib as D
import verify as V


@dataclass(frozen=True)
class Incidence:
    rows: tuple
    owners: dict
    neighbors: tuple
    loose: tuple

    @classmethod
    def read(cls, supports):
        # Local integer atom names are assigned without inspecting their original values.
        names, owners = {}, defaultdict(list)
        rows = []
        for u, support in enumerate(supports):
            row = tuple(names.setdefault(x, len(names)) for x in support)
            if not row or len(set(row)) != len(row):
                raise ValueError("Every junction needs a nonempty support of distinct names")
            rows.append(row)
            for x in row:
                owners[x].append(u)
        if not rows or any(len(v) > 2 for v in owners.values()):
            raise ValueError("Expected a presentation with one or two holders per distinction")
        neighbors = [set() for u in rows]
        loose = [0] * len(rows)
        for uses in owners.values():
            if len(uses) == 1:
                loose[uses[0]] += 1
            else:
                a, b = uses
                neighbors[a].add(b)
                neighbors[b].add(a)
        return cls(tuple(rows), dict(owners), tuple(map(frozenset, neighbors)), tuple(loose))

    @property
    def live(self):
        return {u for u, count in enumerate(self.loose) if count}

    def shared_graph(self):
        g = nx.Graph()
        g.add_nodes_from(range(len(self.rows)))
        g.add_edges_from((a, b) for a, point in enumerate(self.neighbors) for b in point if a < b)
        return g


def complete_groups(neighbors, live):
    held = {frozenset(row & live) for row in neighbors if len(row & live) >= 2}
    candidate = nx.Graph()
    candidate.add_nodes_from(sorted(live))
    candidate.add_edges_from((u, v) for block in held for u, v in combinations(sorted(block), 2))
    large = {frozenset(group) for group in nx.find_cliques(candidate)
             if len(group) >= 3 and not any(set(group) <= b for b in held)}
    covered = {frozenset(pair) for group in large for pair in combinations(group, 2)}
    pairs = {frozenset(pair) for pair in candidate.edges} - covered
    return held, candidate, large, pairs


def restore_predecessor(frame, names, limit):
    """Reconstruct the sole possible preceding roster of a nonclosing reached frame."""
    young = frame.live
    if not young:
        return None, "closed_frame_has_no_loose_end"
    if any(frame.neighbors[u] & young for u in young):
        return None, "loose_holders_share_a_distinction"
    old = [u for u in range(len(frame.rows)) if u not in young]
    if not old:
        return None, "removing_loose_holders_leaves_no_junction"
    if len(young) > limit:
        return None, "peel_live_size_cap"
    born = sorted(young)
    past = Incidence.read([frame.rows[u] for u in old])
    if len(past.live) > limit:
        return None, "peel_live_size_cap"
    if not nx.is_connected(past.shared_graph()):
        return None, "past_is_disconnected"
    if any(len(row) < 3 for row in past.rows):
        return None, "past_has_short_support"
    # Keeping the literal labels tests the observed transition itself.
    try:
        left = V.Arrangement.parse([list(frame.rows[u]) for u in old])
        right = V.Arrangement.parse([list(frame.rows[u]) for u in (*old, *born)])
        checked = V.round_replay(left, right)
    except ValueError as problem:
        return None, str(problem)
    parents = {names[u]: frozenset(names[old[v]] for v in row["taken"])
               for u, row in zip(born, checked, strict=True)}
    assert not any(row["implied"] for row in checked)
    return (past, tuple(names[u] for u in old), parents), None


def invert(stars, limit):
    current = Incidence.read(stars)
    names = tuple(range(len(current.rows)))
    records = []
    while True:
        previous, reason = restore_predecessor(current, names, limit)
        if previous is None:
            break
        past, old_names, parents = previous
        records.append({"frame": current, "names": names, "birth_parents": parents})
        current, names = past, old_names
    source = {"frame": current, "names": names, "birth_parents": {}}
    original = [source, *reversed(records)]
    return original, reason


def finite_branch_root(weight):
    """Bracket the unique positive real rate of a nonnegative lap series."""
    def compare(z):
        numerator = sum(coef * z**i for i, coef in enumerate(weight.num) if coef)
        return numerator - (1 - z)**weight.j

    if not weight.j and compare(Fraction(1)) == 0:
        return (Fraction(1), Fraction(1))
    lo, hi = Fraction(0), Fraction(1)
    for _ in range(32):
        middle = (lo + hi) / 2
        if compare(middle) < 0:
            lo = middle
        else:
            hi = middle
    return 1 / hi, 1 / lo


def lap_weight(A, piece):
    """The single-cycle formula with every off-cycle branch included."""
    core = nx.k_core(piece["H"], k=2)
    on = set(core)
    assert all(core.degree(u) == 2 for u in on)
    value = D.R_ONE
    for kind, u in sorted(core):
        if kind == "p":
            assert not A["raypend"][u]
            value = value * D.Rat(D.pmul(D.Z, D.ppow(D.ONEZ, A["spares"][u])))
            for w in A["of"].get(u, []):
                if ("b", w) not in on:
                    for q in A["blocks"][w] - {u}:
                        value = value * (D.R_ONE + D.hang(A, q, w))
        else:
            for q in A["blocks"][u]:
                if ("p", q) not in on:
                    value = value * (D.R_ONE + D.hang(A, q, u))
    return value


def encode_fraction(q):
    return [q.numerator, q.denominator]


def cyclic_core(piece, names):
    core = nx.k_core(piece["H"], k=2)
    return {kind: sorted(names[v] for k, v in core if k == kind) for kind in ("p", "b")}


def layer_distances(frame, names):
    """The observed minimum shared-distinction steps to any loose holder."""
    distances = nx.multi_source_dijkstra_path_length(frame.shared_graph(), frame.live, weight=None)
    return {names[u]: q for u, q in distances.items()}


def map_model(frame, names, live, horizon=0):
    """Read the published cluster law only on its exact local hypotheses."""
    if not live:
        return {"status": "closed_or_empty"}, None
    held, cgraph, large, residual = complete_groups(frame.neighbors, live)
    counts = Counter(u for group in large | residual for u in group)
    if any(counts[u] > frame.loose[u] for u in live):
        return {"status": "unfunded"}, None
    pair_uses = Counter(pair for row in frame.neighbors for pair in combinations(sorted(row & live), 2))
    found = {"blocks": sorted(sorted(names[v] for v in row) for row in held),
             "maximal_unheld_groups": len(large), "residual_pairs": len(residual),
             "candidate_components": nx.number_connected_components(cgraph)}
    if any(n > 1 for n in pair_uses.values()) or large:
        return {**found, "status": "outside_cluster_scope",
                "duplicate_common_holder": any(n > 1 for n in pair_uses.values())}, None
    if sum(frame.loose[u] for u in live) < 2:
        return {**found, "status": "too_few_loose_distinctions"}, None

    edges = [users for users in frame.owners.values() if len(users) == 2]
    sizes = [len(row) - (frame.loose[u] if u not in live else 0) for u, row in enumerate(frame.rows)]
    state = D.analyse(sizes, edges)
    assert live == state["live"]
    results = []
    for piece in state["pieces"]:
        rank = piece["rank"]
        record = {"rank": rank, "junctions": sorted(names[u] for u in piece["points"]),
                  "core": cyclic_core(piece, names), "pendant_rays": piece["rays"]}
        if rank == 1:
            size_bound = len(piece["points"]) + sum(state["spares"][u] + 2 * state["raypend"][u]
                                                     for u in piece["points"])
            core_is_full = len(record["core"]["p"]) + len(record["core"]["b"]) == len(piece["H"])
            record["kind"] = "circulation" if core_is_full and size_bound == len(piece["points"]) else "eddy"
            if size_bound < D.NS:
                W = lap_weight(state, piece)
                lo, hi = finite_branch_root(W)
                record.update({"lap_numerator": [(i, c) for i, c in enumerate(W.num) if c],
                               "lap_denominator_one_minus_z_power": W.j,
                               "rate_interval": [encode_fraction(lo), encode_fraction(hi)]})
            else:
                record["rate_status"] = "lap_degree_cap"
        else:
            record["kind"] = "interacting_cycles" if rank > 1 else "acyclic"
        results.append(record)
    results.sort(key=lambda p: p["junctions"])
    if horizon:
        assert 0 < horizon < D.NS - 2
        found["counts_through_relative_age"] = D.exact_counts(state, horizon)
    return {**found, "status": "exact_cluster_model", "pieces": results}, state


def source_rings(frame, names, state, horizon):
    """Find every simple cyclic block of the inferred physical source."""
    if state is None:
        return []
    graph = frame.shared_graph()
    rings = []
    for point in nx.biconnected_components(graph):
        sub = graph.subgraph(point)
        if len(point) < 3 or any(sub.degree(v) != 2 for v in point):
            continue
        if not set(point) <= state["live"]:
            continue
        # The isolated ring keeps its spare distinctions, with its own pair demand.
        order = sorted(point)
        index = {u: i for i, u in enumerate(order)}
        local = [(index[u], index[v]) for u, v in sub.edges]
        spare = [state["open"][u] - state["d"][u] for u in order]
        sizes = [4 + count for count in spare]
        model = D.analyse(sizes, local)
        if model["d"] != model["dsum"] or any(
            piece["rank"] != 1 for piece in model["pieces"]
        ):
            continue
        if any(len(g) > 2 for g in V.groups([model["nb"][u] for u in range(len(order))], model["live"])):
            continue
        W = [lap_weight(model, piece) for piece in model["pieces"]]
        rates = [finite_branch_root(w) for w in W]
        lower, upper = max(x[0] for x in rates), max(x[1] for x in rates)
        rings.append({"knots": sorted(names[u] for u in point),
                      "seam": sorted(names[u] for u in point if graph[u].keys() - point),
                      "spare_holders": sorted(names[u] for u, count in zip(order, spare, strict=True) for _ in range(count)),
                      "spares": sum(spare), "rate_interval": [encode_fraction(lower), encode_fraction(upper)],
                      "kind": "eddy" if lower > 1 else "circulation",
                      "isolated_counts": D.exact_counts(model, horizon) if horizon else None})
    return sorted(rings, key=lambda row: row["knots"])


def recognize(stars, *, limit=768, horizon=36):
    """Accept only unmarked supports. Absolute ages and source names are evaluator data."""
    chain, stop = invert(stars, limit)
    root = chain[0]
    frame, names = root["frame"], root["names"]
    current_view, _ = (map_model(chain[-1]["frame"], chain[-1]["names"], chain[-1]["frame"].live)
                       if len(chain[-1]["frame"].live) <= limit else ({"status": "live_size_cap"}, None))
    if stop == "peel_live_size_cap":
        source_model, rings = {"status": "source_not_resolved_within_cap"}, []
    elif not frame.live:
        source_model, rings = {"status": "no_open_source_identified"}, []
    elif not V.start_audit(V.Arrangement.parse([list(r) for r in frame.rows]))["census_open_legal"]:
        source_model, rings = {"status": "inferred_source_fails_canonical_support_gate"}, []
    else:
        source_model, state = map_model(frame, names, frame.live, horizon)
        rings = source_rings(frame, names, state, horizon)
    return {"inferred_start_junctions": sorted(names), "exact_predecessor_steps": len(chain) - 1,
            "first_rejected_predecessor": stop, "source_model": source_model,
            "source_carriers": rings, "current_model": current_view, "chain": chain}


def inferred_background(source, carriers):
    """Recover the unique longest path after the ring-exclusive sites are removed."""
    frame, names = source["frame"], source["names"]
    ring_only = {u for row in carriers for u in set(row["knots"]) - set(row["seam"])}
    remainder = frame.shared_graph().subgraph(u for u, name in enumerate(names) if name not in ring_only)
    if not remainder:
        return []
    if not nx.is_tree(remainder):
        return None
    longest = -1
    paths = set()
    for u, paths_from_u in nx.all_pairs_shortest_path(remainder):
        for v, route in paths_from_u.items():
            if u > v:
                continue
            length = len(route)
            if length >= longest:
                if length > longest:
                    paths.clear()
                    longest = length
                paths.add(frozenset(names[p] for p in route))
    return sorted(next(iter(paths))) if len(paths) == 1 else None


def minimum_steps(graph, left, right):
    if not left or not right:
        return None
    distance = dict.fromkeys(left, 0)
    pending = deque(left)
    while pending:
        u = pending.popleft()
        if u in right:
            return distance[u]
        for v in graph[u]:
            if v not in distance:
                distance[v] = distance[u] + 1
                pending.append(v)
    return None


def summarize_layers(result):
    """Read source support and physical interaction after the recognizer has finished."""
    chain, carriers = result["chain"], result["source_carriers"]
    background = inferred_background(chain[0], carriers)
    if background is None:
        raise ValueError("The inferred source does not have a unique background path")
    marks = [set(row["knots"]) for row in carriers]
    exclusive = [q - set(background) - set().union(*(m for m in marks if m != q)) for q in marks]
    seams = [set(c["seam"]) for c in carriers]
    ancestors = {u: frozenset({u}) for u in chain[0]["names"]}
    mass, scope = [], None
    for age, stage in enumerate(chain):
        frame, names, born = stage["frame"], stage["names"], stage["birth_parents"]
        new = names if age == 0 else sorted(born)
        ancestors.update({u: frozenset.union(*(ancestors[p] for p in row)) for u, row in born.items()})
        live_parents = {u: ancestors[u] for u in new}
        pure = [{u for u, support in live_parents.items() if support <= r} for r in marks]
        pure_exclusive = [{u for u in bucket if ancestors[u] & tract} for bucket, tract in zip(pure, exclusive)]
        only_background = {u for u, support in live_parents.items() if support <= set(background)}
        graph = nx.relabel_nodes(frame.shared_graph(), dict(enumerate(names)))
        row = {"relative_age": age, "size": age + 1, "births": len(new),
               "pure_rings": list(map(len, pure)), "pure_exclusive_rings": list(map(len, pure_exclusive)),
               "pure_background": len(only_background),
               "seam_only_intersection": [len(q & only_background) for q in pure],
               "outside_all_named_parts": len(set(new) - (only_background | set().union(*pure))),
               "ring_vertex_sets": [sorted(r) for r in pure_exclusive],
               "pure_support_by_junction": {u: sorted(a) for u, a in live_parents.items()}}
        if len(marks) == 2:
            unrestricted = {u for u, support in live_parents.items() if all(support & tract for tract in exclusive)}
            row.update({"mixed_exclusive_both": len(unrestricted),
                        "mixed_exclusive_both_names": sorted(unrestricted),
                        "seam_physical_steps": minimum_steps(graph, seams[0], seams[1]),
                        "pure_parts_physical_steps": minimum_steps(graph, pure_exclusive[0], pure_exclusive[1])})
            if age == 0:
                _, candidate, _, _ = complete_groups(frame.neighbors, frame.live)
                candidate = nx.relabel_nodes(candidate, dict(enumerate(names)))
                scope = {"exclusive_source_candidate_steps": minimum_steps(candidate, exclusive[0], exclusive[1]),
                         "exclusive_source_physical_steps": minimum_steps(graph, exclusive[0], exclusive[1])}
        mass.append(row)
    if scope is not None:
        first = next((r for r in mass if r["mixed_exclusive_both"]), None)
        scope["first_joint_age"] = first["relative_age"] if first else None
        scope["first_joint_multiplicity"] = first["mixed_exclusive_both"] if first else None
    return {"background": background, "layers": mass, "two_rings": scope}


def relabel(stars, seed):
    rng = random.Random(seed)
    holders = list(range(len(stars)))
    distinctions = sorted({x for row in stars for x in row})
    names = list(range(10000, 10000 + len(distinctions)))
    rng.shuffle(holders)
    rng.shuffle(names)
    trans = dict(zip(distinctions, names, strict=True))
    output = [[trans[x] for x in stars[u]] for u in holders]
    for row in output:
        rng.shuffle(row)
    return output, holders


def verify_primary(case, entry):
    stages, roles = entry["stages"], entry["input"]["roles"]
    final_age = max(map(int, stages))
    latest = stages[str(final_age)]
    found = recognize(latest["stars"])
    chain = found["chain"]
    assert final_age == found["exact_predecessor_steps"]
    assert found["source_model"]["status"] == "exact_cluster_model", case
    assert len(chain[0]["names"]) == len(stages["0"]["stars"])
    last_ages = layer_distances(chain[-1]["frame"], chain[-1]["names"])
    assert max(last_ages.values()) == final_age and set(last_ages) == set(range(len(latest["stars"])))
    weights = {frozenset(row["knots"]): row for row in found["source_carriers"]}
    assert set(weights) == set(map(frozenset, roles["rings"]))
    for key, spare in zip(roles["rings"], roles["ring_spares"], strict=True):
        assert weights[frozenset(key)]["spare_holders"] == sorted(spare)
    summaries = summarize_layers(found)
    assert summaries["background"] == sorted(roles["background"])
    predicted = found["source_model"]["counts_through_relative_age"]
    for age, layer in enumerate(chain):
        truth = stages[str(age)]
        this = summaries["layers"][age]
        assert len(layer["names"]) == len(truth["stars"])
        assert predicted[age] == this["births"] == len(truth["born"])
        assert all(last_ages[u] + age == final_age for u in truth["born"])
        assert {int(k): frozenset(p) for k, p in truth["parent_sets"].items()} == layer["birth_parents"]
        assert all(s == truth["source_coordinate_maps"]["ancestry"][u]
                   for u, s in this["pure_support_by_junction"].items())
        assert this["pure_rings"] == [row["isolated_counts"][age] for row in found["source_carriers"]]

    expected = {tuple(row["knots"]): (row["spares"], row["kind"]) for row in found["source_carriers"]}
    tested = []
    # Independent recodings include a source-only and interior observation.
    for i, age in enumerate((0, min(2, final_age), final_age)):
        original = stages[str(age)]["stars"]
        shuffled, holders = relabel(original, f"world-anonymous-v1:{case}:{i}")
        readout = recognize(shuffled, horizon=max(2, age))
        mapped = {tuple(sorted(holders[u] for u in row["knots"])): (row["spares"], row["kind"])
                  for row in readout["source_carriers"]}
        assert mapped == expected
        assert readout["exact_predecessor_steps"] == age
        assert sorted(holders[u] for u in readout["inferred_start_junctions"]) == list(range(len(stages["0"]["stars"])))
        renamed_age = layer_distances(readout["chain"][-1]["frame"], readout["chain"][-1]["names"])
        assert {holders[u]: d for u, d in renamed_age.items()} == {u: last_ages[u] - final_age + age
                                                                  for u in range(len(original))}
        for row in readout["chain"]:
            observed = {holders[u]: frozenset(holders[p] for p in group) for u, group in row["birth_parents"].items()}
            if observed:
                layer = age - next(iter(renamed_age[u] for u in row["birth_parents"]))
                assert observed == chain[layer]["birth_parents"]
        testified = readout["source_model"]["counts_through_relative_age"]
        assert testified == predicted[:len(testified)]
        tested.append(age)

    model = found["source_model"]
    if any(piece["rank"] > 1 for piece in model["pieces"]):
        source, names = chain[0]["frame"], chain[0]["names"]
        _, state = map_model(source, names, source.live)
        higher = [P for P in state["pieces"] if P["rank"] > 1]
        model["multicycle_rate_numeric"] = [{
            "rank": P["rank"], "iteration_limits": [1600, 4800],
            "rates": [D.branch_rate(state, P, iters=steps) for steps in (1600, 4800)]
        } for P in higher]
    report = {k: found[k] for k in found if k != "chain"}
    report["recoded_ages"] = tested
    report["source_knots_beyond_current_live"] = sorted(set(chain[0]["names"]) - set(stages[str(final_age)]["live"]))
    report["age_verified_from_loose_holder_steps_through"] = final_age
    report["background"] = summaries["background"]
    for row in summaries["layers"]:
        del row["pure_support_by_junction"]
    return report, summaries


def residual_return(candidate, residual):
    """Find two distinct returns from one residual turn, if this direct certificate exists."""
    ahead = defaultdict(set)
    for u, v in map(tuple, residual):
        ahead[u].add(v)
        ahead[v].add(u)
    turns = nx.DiGraph()
    for u, peers in ahead.items():
        turns.add_nodes_from((u, v) for v in peers)
        for v in peers:
            for w in ahead[v] - {u} - set(candidate[u]):
                turns.add_edge((u, v), (v, w))
    for component in sorted(nx.strongly_connected_components(turns), key=lambda c: min(c)):
        sub = turns.subgraph(component)
        branch = next((u for u in sorted(component) if sub.out_degree(u) >= 2), None)
        if branch is None:
            continue
        first, second = sorted(sub[branch])[:2]
        walks = [[branch, *nx.shortest_path(sub, child, branch)] for child in (first, second)]
        return {"return_paths": walks, "equalized_return_length": (len(walks[0]) - 1) * (len(walks[1]) - 1)}
    return None


def end_fragment(stars):
    """The evaluator erases all older holders, retaining each remaining literal support."""
    frame = Incidence.read(stars)
    keep = sorted(frame.live | set().union(*(frame.neighbors[u] for u in frame.live)))
    return [stars[u] for u in keep], keep


def read_fragment(stars, *, limit=768):
    """Try an orientation from the two-slice fresh law, without age or roles."""
    frame = Incidence.read(stars)
    graph = frame.shared_graph()
    shared = Counter(tuple(row) for row in frame.owners.values() if len(row) == 2)
    output = []
    for comp in sorted(nx.connected_components(graph), key=min):
        sg = graph.subgraph(comp)
        record = {"holders": sorted(comp), "orientations": []}
        output.append(record)
        if not nx.is_bipartite(sg):
            record["status"] = "not_bipartite"
            continue
        if sg.number_of_edges() == 0:
            record["status"] = "no_shared_distinction"
            continue
        if any(shared[tuple(sorted((a, b)))] != 1 for a, b in sg.edges):
            record["status"] = "multiple_shares_to_a_parent"
            continue
        parity = nx.bipartite.color(sg)
        rejected = []
        for color in range(2):
            live = {u for u in comp if parity[u] == color}
            if len(live) > limit:
                rejected.append("child_size_cap")
                continue
            if any(not frame.loose[u] for u in live):
                rejected.append("child_has_no_fresh_distinction")
                continue
            _, candidate, large, residual = complete_groups(frame.neighbors, live)
            d = Counter(u for group in large | residual for u in group)
            if any(frame.loose[u] != max(d[u], 3 - sg.degree(u), 1) for u in live):
                rejected.append("fewest_count_mismatch")
                continue
            model, _ = map_model(frame, tuple(range(len(frame.rows))), live)
            turn = residual_return(candidate, residual)
            record["orientations"].append({"proposed_current": sorted(live),
                                           "local_model": model["status"],
                                           "cyclic_pieces": [dict(rank=q["rank"], kind=q["kind"])
                                                             for q in model.get("pieces", []) if q["rank"]],
                                           "two_residual_returns": turn})
        record["rejected"] = rejected
        record["status"] = ("orientation_unresolved" if not record["orientations"] else
                            "ambiguous_orientation" if len(record["orientations"]) > 1 else "one_orientation")
    return output


def weighted_fragment(stars):
    """Compressed incidence. A loose count and shared multiplicities retain every incidence."""
    frame = Incidence.read(stars)
    graph = nx.Graph()
    for u, f in enumerate(frame.loose):
        graph.add_node(u, base=f)
    for a, b in (tuple(row) for row in frame.owners.values() if len(row) == 2):
        value = graph[a][b]["count"] + 1 if graph.has_edge(a, b) else 1
        graph.add_edge(a, b, count=value)
    refine(graph)
    return graph, frame


def refine(graph, anchor=None):
    colors = {u: (graph.nodes[u]["base"], u == anchor) for u in graph}
    old = 0
    while len(set(colors.values())) != old:
        old = len(set(colors.values()))
        feature = {u: (colors[u], tuple(sorted((colors[v], edge["count"]) for v, edge in graph[u].items())))
                   for u in graph}
        code = {s: i for i, s in enumerate(sorted(set(feature.values())))}
        colors = {u: code[s] for u, s in feature.items()}
    nx.set_node_attributes(graph, colors, "color")
    nx.set_node_attributes(graph, {u: u == anchor for u in graph}, "rooted_flag")


def graph_match(first, second):
    return nx.isomorphism.GraphMatcher(
        first, second, node_match=lambda a, b: (a["base"], a["color"], a["rooted_flag"]) == (
            b["base"], b["color"], b["rooted_flag"]),
        edge_match=lambda a, b: a["count"] == b["count"]
    )


def fragment_signature(graph):
    return (tuple(sorted(Counter((d["base"], graph.degree[u], d["color"]) for u, d in graph.nodes(data=True)).items())),
            tuple(sorted(Counter(d["count"] for _, _, d in graph.edges(data=True)).items())))


def lift_literal(first, second, mapping):
    """Make the distinction renaming for a verified multiplicity-preserving map."""
    left, right = defaultdict(list), defaultdict(list)
    for a, users in first.owners.items():
        left[tuple(sorted(mapping[u] for u in users))].append(a)
    for a, users in second.owners.items():
        right[tuple(sorted(users))].append(a)
    assert left.keys() == right.keys()
    image = {}
    for users, names in left.items():
        image.update(zip(sorted(names), sorted(right[users]), strict=True))
    assert {row: frozenset(image[v] for v in first.rows[row]) for row in mapping} == {
        row: frozenset(second.rows[mapping[row]]) for row in mapping
    }
    return image


def check_orbit(fragment, truth, cap=8192, holders_cap=144):
    """Test whether exact isometries move the unordered family of pure current cohorts."""
    graph, frame = weighted_fragment(fragment)
    cohorts = list(map(frozenset, truth["cohorts"]))
    roster = set(cohorts)
    if not roster:
        return {"status": "no_ring_cohort"}

    def role_cells(g):
        cells = defaultdict(set)
        for u in g:
            role = tuple(i for i, members in enumerate(cohorts) if u in members)
            cells[g.nodes[u]["color"]].add(role)
        return dict(cells)

    cells = role_cells(graph)
    if all(len(role) == 1 for role in cells.values()):
        return {"status": "fixed_by_untyped_refinement", "stable_cells": len(cells)}

    class_id = {u: graph.nodes[u]["color"] for u in graph}
    if len(cohorts) == 2 and all(() not in roles for roles in cells.values() if len(roles) > 1):
        unit = min(u for u in cohorts[0] if len(cells[class_id[u]]) > 1)
        options = sorted(u for u in graph if class_id[u] == class_id[unit])
        rooted = graph.copy()
        refine(rooted, anchor=unit)
        known = role_cells(rooted)
        fixed = all(len(x) == 1 for x in known.values())
        answers = []
        if fixed:
            for v in options:
                if v == unit:
                    answers.append({"root_image": v, "type": "stabilizer_fixes_both"})
                    continue
                target = graph.copy()
                refine(target, anchor=v)
                check = graph_match(rooted, target)
                if not check.is_isomorphic():
                    answers.append({"root_image": v, "type": "no_isomorphism"})
                    continue
                p = check.mapping
                assert p[unit] == v
                roles = {frozenset(p[u] for u in s) for s in roster}
                literal = lift_literal(frame, frame, p)
                if roles != roster:
                    return {"status": "opposed_membership", "holders": p, "distinctions": literal,
                            "before": sorted(sorted(r) for r in roster), "after": sorted(sorted(r) for r in roles),
                            "encoded_distinction_supports": frame.rows,
                            "preserves_current_side": {p[u] for u in truth["current"]} == truth["current"]}
                answers.append({"root_image": v, "type": "copy_swap" if v in cohorts[1] else "fixes_both",
                                "holders": p, "distinctions": literal,
                                "encoded_distinction_supports": frame.rows})
            return {"status": "untyped_unordered_family_certified", "anchor": unit, "anchor_images": answers,
                    "stable_cells": len(cells), "rooted_stable_cells": len(known)}

    if len(graph) > holders_cap:
        return {"status": "holder_cap"}
    seen = 0
    for p in graph_match(graph, graph).isomorphisms_iter():
        seen += 1
        if seen > cap:
            return {"status": "automorphism_cap", "automorphisms_checked": cap}
        image = {frozenset(p[u] for u in s) for s in roster}
        if image != roster:
            image_bits = lift_literal(frame, frame, p)
            return {"status": "opposed_membership", "automorphisms_checked": seen,
                    "holders": p, "distinctions": image_bits,
                    "before": sorted(sorted(r) for r in roster), "after": sorted(sorted(r) for r in image),
                    "encoded_distinction_supports": frame.rows,
                    "preserves_current_side": {p[u] for u in truth["current"]} == truth["current"]}
    return {"status": "family_invariant_in_this_fragment", "automorphisms_checked": seen}


def compare_fragments(panel):
    """Compare every matched size of the recorded certified cuts."""
    by_size = defaultdict(list)
    for q in panel:
        by_size[len(q["frame"].rows), len(q["frame"].owners)].append(q)
    counts = Counter()
    counts["all_observation_pairs"] = len(panel) * (len(panel) - 1) // 2
    instances, different_cases = [], []
    for bucket in by_size.values():
        for a, b in combinations(bucket, 2):
            counts["same_size_pairs"] += 1
            if a["name"][0] != b["name"][0]:
                counts["same_size_cross_case_pairs"] += 1
                different_cases.append({"frames": [a["name"], b["name"]], "isomorphic": False})
            if a["signature"] != b["signature"]:
                continue
            matcher = graph_match(a["graph"], b["graph"])
            counts["submitted_to_exact_isometry"] += 1
            if not matcher.is_isomorphic():
                continue
            counts["exactly_isomorphic"] += 1
            if a["name"][0] != b["name"][0]:
                counts["exactly_isomorphic_across_cases"] += 1
                different_cases[-1]["isomorphic"] = True
            if a["kind"] != b["kind"]:
                counts["opposes_intrinsic_eddy_presence"] += 1
                instances.append({"frames": [a["name"], b["name"]], "holders": matcher.mapping,
                                  "distinctions": lift_literal(a["frame"], b["frame"], matcher.mapping)})
    counts["eliminated_by_unequal_size"] = counts["all_observation_pairs"] - counts["same_size_pairs"]
    counts["eliminated_by_incidence_colors"] = counts["same_size_pairs"] - counts["submitted_to_exact_isometry"]
    return {"counts": dict(counts), "opposition_examples": instances, "matched_sizes_across_cases": different_cases}


def ablation(cases, primary, interaction):
    fragments, results = [], {}
    for key, entry in cases.items():
        results[key] = []
        hit = any(r["kind"] == "eddy" for r in primary[key]["source_carriers"])
        for age, stage in sorted(entry["stages"].items(), key=lambda t: int(t[0])):
            if age == "0":
                continue
            fragment, keep = end_fragment(stage["stars"])
            index = {u: i for i, u in enumerate(keep)}
            graph, frame = weighted_fragment(fragment)
            name = [key, int(age)]
            fragments.append({"name": name, "graph": graph, "frame": frame,
                              "signature": fragment_signature(graph), "kind": hit})
            trial = read_fragment(fragment)
            revealed = {index[u] for u in stage["live"]}
            pure = [{index[u] for u in s} for s in interaction[key]["layers"][int(age)]["ring_vertex_sets"]]
            status = check_orbit(fragment, {"current": revealed, "cohorts": pure})
            results[key].append({"age": int(age), "holders": len(frame.rows), "distinctions": len(frame.owners),
                                 "total_components": len(trial),
                                 "direct_phase_template": dict(Counter(x["status"] for x in trial)),
                                 "components_with_actual_child_side_admitted": sum(
                                     any(set(o["proposed_current"]) == set(x["holders"]) & revealed
                                         for o in x["orientations"]) for x in trial),
                                 "direct_cycle_witnesses": [o for x in trial for o in x["orientations"]
                                                           if o["cyclic_pieces"] or o["two_residual_returns"]],
                                 "source_cohort_orbit": status})
    return {"cuts": results, "matched_size_analysis": compare_fragments(fragments),
            "scope": "The direct reader uses incidence only. The untyped orbit checker compares its exact maps to evaluator cohorts."}


def main():
    from world_growth import STAGES, load_study

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTIFACTS)
    args = parser.parse_args()
    stage_digest = sha256(STAGES.read_bytes()).hexdigest()
    cases = load_study()["cases"]
    primary, interaction = {}, {}
    for case, row in cases.items():
        primary[case], interaction[case] = verify_primary(case, row)
        print(case, "recognized", flush=True)
    for case, result in primary.items():
        for i, ring in enumerate(result["source_carriers"]):
            own = interaction[f"R{ring['spares']}"]["layers"]
            for item in interaction[case]["layers"]:
                assert item["pure_rings"][i] == own[item["relative_age"]]["pure_rings"][0]
    secondary = ablation(cases, primary, interaction)
    print("ablation complete", flush=True)
    args.output.mkdir(parents=True, exist_ok=True)
    assert sha256(STAGES.read_bytes()).hexdigest() == stage_digest
    primary_evidence = {"cases": primary, "ablation": secondary, "verified_stages": sum(
        len(case["stages"]) for case in cases.values()), "stage_archive_sha256": stage_digest}
    for name, data in (("recognition", primary_evidence), ("interaction", interaction)):
        path = args.output / (name + ".json")
        pending = path.with_suffix(".pending")
        pending.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        pending.replace(path)


if __name__ == "__main__":
    main()
