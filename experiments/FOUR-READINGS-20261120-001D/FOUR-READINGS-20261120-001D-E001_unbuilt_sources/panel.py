"""Count proof-certified, physically recognized releases on the frozen labelled starts."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from functools import cache
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import random
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
HORIZON = 16
CAP = 128
LAWS = ("parity", "nae")


def module(name, relative):
    path = ROOT / "experiments" / relative
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


base = module("s4_base", "GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators/sample.py")
old, end, nae = base.libraries()
fix = module("s4_fixtures", "GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators/fixtures.py")


def graph_of(state):
    graph = nx.Graph()
    graph.add_nodes_from(state.opens)
    for block in state.blocks:
        graph.add_edges_from(combinations(block, 2))
    return graph


def classify_initial(graph, loose, groups, funded):
    live = {v for v, h in enumerate(loose) if h > 0}
    roles = nx.Graph()
    roles.add_nodes_from((0, v) for v in live)
    seen = Counter()
    for w in graph:
        near = sorted(set(graph[w]) & live)
        if len(near) > 1:
            roles.add_edges_from(((0, v), (1, w)) for v in near)
            seen.update(combinations(near, 2))
    ranks = sorted(len(roles.subgraph(c).edges) - len(c) + 1 for c in nx.connected_components(roles))
    assert max(ranks, default=0) <= 1
    valid = (funded and sum(loose) >= 2 and not any(len(g) >= 3 for g in groups)
             and max(seen.values(), default=0) <= 1)
    return {"identified": valid, "cycle_counts": ranks, "multi_witness": max(seen.values(), default=0) > 1,
            "first_unheld_group": any(len(g) >= 3 for g in groups)}


def path_features(state, graph):
    n = len(graph)
    if n < 2 or sum(graph.degree(v) == 1 for v in graph) != 2 or max(dict(graph.degree).values()) > 2:
        return set(), False
    tips = {v for v in graph if graph.degree(v) == 1 and state.opens[v] == 2}
    stable = bool(tips) and all(1 <= state.opens[v] <= 2 if graph.degree(v) == 1
                                else state.opens[v] == 2 for v in graph)
    return tips, stable


def component_run(state, law, single, horizon=HORIZON):
    """Indices are scorer notation. The predicates see only opens and witnessed sets."""
    roots = {}
    pure, ancestry = {}, {}
    meetings, common = {}, {}
    sizes = [len(state.opens)]
    first_stable = None
    cutoff = None
    closed = False
    all_rosters = hashlib.sha256()
    for age in range(1, horizon + 1):
        # Once two parts exist their descendants stay separate and nonempty, forbidding
        # a sole parity closure. Applying NAE on each is the nonclosing parity operator.
        turn = end.step(state, law if single else "nae", max_births=CAP)
        if turn.status == "cap":
            cutoff = {"before_age": age, "at_least": turn.planned_births_lower}
            break
        if turn.status == "closed":
            closed = True
            break
        assert turn.status == "extend"
        all_rosters.update(repr((turn.parents, turn.fresh)).encode("ascii"))
        if turn.implied:
            closed = True
            sizes.append(0)
            break
        nxt = turn.end
        graph = graph_of(nxt)
        assert nx.is_connected(graph)
        tips, stable = path_features(nxt, graph)
        if stable and first_stable is None:
            first_stable = age
        next_pure, next_ancestry = {}, {}
        for child, parents in enumerate(turn.parents):
            tags = set().union(*(ancestry.get(p, ()) for p in parents))
            pure_parents = sorted(pure[p] for p in parents if p in pure)
            for pair in combinations(pure_parents, 2):
                meetings.setdefault(pair, {"age": age, "parents": list(parents)})
            for pair in combinations(sorted(tags), 2):
                common.setdefault(pair, {"age": age, "parents": list(parents)})
            if len(parents) == 1 and parents[0] in pure:
                tag = pure[parents[0]]
                next_pure[child] = tag
                if child not in tips:
                    roots[tag]["read_continuously"] = False
            elif child in tips:
                # A newborn of degree one has demand one; with two openings it
                # must have one parent by the actual minimum-arity rule.
                assert len(parents) == 1
                tag = len(roots)
                roots[tag] = {"age": age, "parent": parents[0], "child": child,
                              "read_continuously": True, "certified_at": None}
                next_pure[child] = tag
                tags.add(tag)
            if child in next_pure and stable:
                rec = roots[next_pure[child]]
                if rec["read_continuously"] and rec["certified_at"] is None:
                    rec["certified_at"] = age
            next_ancestry[child] = tags
        assert set(pure.values()) <= set(next_pure.values())
        state, pure, ancestry = nxt, next_pure, next_ancestry
        sizes.append(len(nxt.opens))
    successes = {k for k, v in roots.items() if v["certified_at"] is not None}
    pending = {k for k, v in roots.items() if v["read_continuously"] and k not in successes}
    def relation(table):
        return [{"families": list(k), **v} for k, v in sorted(table.items()) if set(k) <= successes]
    incom = [{"families": list(k), **v} for k, v in sorted(common.items())
             if set(k) <= successes and k not in meetings and v["age"] > max(roots[z]["age"] for z in k) + 1]
    return {"sizes": sizes, "cutoff": cutoff, "closed": closed, "stable_from": first_stable,
            "rosters_sha256": all_rosters.hexdigest(), "roots": list(roots.values()),
            "successes": len(successes), "pending": len(pending), "direct": relation(meetings),
            "first_common": relation(common), "collateral_candidates": incom}


@cache
def legality(stars):
    return old.source_lawfulness(nae.S.from_junctions(stars))


def matched_off(stars, initial, part, law):
    """Exhaust the registered one-place donor-off comparator for opposite initial tips."""
    sub = end.restricted(initial, part)
    graph = graph_of(sub)
    eligible, stable = path_features(sub, graph)
    if not stable or len(eligible) != 2:
        return []
    d = len(part) - 1
    where = {v: set(stars[v]) for v in part}
    all_counts = Counter(bit for star in stars for bit in star)
    identities = sorted(eligible)
    edits = []
    for donor in identities:
        receiver, = eligible - {donor}
        loose_bit = min(b for b in where[donor] if all_counts[b] == 1)
        edited = tuple(tuple(b for b in row if b != loose_bit) if k == donor else row
                       for k, row in enumerate(stars))
        legal = legality(edited)[law]["lawful"]
        item = {"donor": donor, "receiver": receiver, "bit": loose_bit, "legal": legal}
        if not legal:
            edits.append(item)
            continue
        off = end.from_stars(edited)
        assert off.blocks == initial.blocks
        assert off.opens == {v: h - int(v == donor) for v, h in initial.opens.items()}
        assert end.step(off, law, max_births=CAP).status == "extend"
        # In the literal comparator all other parts and openings agree. The restricted
        # local calculation uses the full global closing promise in component_run.
        off_run = component_run(end.restricted(off, part), law, len(part) == len(off.opens), d + 3)
        assert off_run["successes"] == 1 and off_run["sizes"] == [d + 1] * (d + 4)
        item.update(funded=True, first_common_age=d + 2, after_age=d + 3,
                    receiver_inclusive_on_off=[d + 2, d + 1], on_off_joint_births=[1, 0],
                    on_off_next_joint_births=[2, 0], off_sizes=off_run["sizes"])
        edits.append(item)
    return edits


def outcome(n, unknown, threshold):
    return "yes" if n >= threshold else "unknown" if unknown else "no"


def full_run(stars, law, physical, horizon=HORIZON):
    source = end.from_stars(stars)
    start_plan = end.step(source, law, max_births=CAP)
    assert start_plan.status != "cap"
    legal = legality(stars)[law]["lawful"]
    fund = legal and start_plan.status == "extend"
    groups = end.proposals(source)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(stars)))
    graph.add_edges_from(physical)
    loose = [source.opens.get(i, 0) for i in range(len(stars))]
    ident = classify_initial(graph, loose, groups, fund)
    comps = [sorted(p) for p in nx.connected_components(graph_of(source))]
    parts = []
    if fund:
        for ids in comps:
            part = component_run(end.restricted(source, ids), law, len(comps) == 1, horizon)
            part["initial_holders"] = ids
            part["donor_off"] = matched_off(stars, source, ids, law) if part["collateral_candidates"] else []
            for row in part["donor_off"]:
                if row.get("funded"):
                    assert any(e["age"] == row["first_common_age"] for e in part["collateral_candidates"])
                    # Inclusive counts at age d+2 correspond to size d+3.
            parts.append(part)
    n = sum(p["successes"] for p in parts)
    unknown = any(p["cutoff"] or p["pending"] for p in parts)
    nr_direct = sum(len(p["direct"]) for p in parts)
    incandidates = any(p["collateral_candidates"] for p in parts)
    indirect = any(e.get("funded") and e["first_common_age"] <= horizon for p in parts for e in p["donor_off"])
    # A different matched physical comparison may settle an unmatched collateral pair.
    total_rank_obstruction = ident["identified"] or bool(parts) and all(p["closed"] or p["stable_from"] for p in parts)
    source_unknown = fund and not total_rank_obstruction
    outcomes = {"funded": "yes" if fund else "no",
                "one_or_more": outcome(n, unknown, 1), "two_or_more": outcome(n, unknown, 2),
                "exactly_one": "no" if n >= 2 else "unknown" if unknown else "yes" if n == 1 else "no",
                "direct": outcome(nr_direct, unknown, 1),
                "indirect": outcome(int(indirect), unknown or incandidates and not indirect, 1),
                "recurrent": "unknown" if source_unknown else "no"}
    # For the additional identified return-word reading the original incidence must
    # contain two independent returns. A nonidentified start is not a negative
    # for arbitrary later presentations. Keep those cases censored.
    broader_registered = dict(outcomes)
    if source_unknown:
        for key in ("one_or_more", "two_or_more", "direct", "indirect"):
            if broader_registered[key] == "no":
                broader_registered[key] = "unknown"
        if n < 2:
            broader_registered["exactly_one"] = "unknown"
    return {"legal": legal, "funded": fund, "identified": ident, "source_status": start_plan.status,
            "shortages": start_plan.shortages, "parts": parts, "observed": outcomes,
            "with_return_uncertainty": broader_registered, "certified_releases": n,
            "certified_indirect": indirect, "candidate_indirect": incandidates, "any_capped": any(p["cutoff"] for p in parts)}


def source_rows(count):
    rng = random.Random(20261120401)
    added_rng = random.Random(20261120402)
    for i in range(count):
        n = rng.randrange(4, 9)
        code = [rng.randrange(n) for _ in range(n - 2)]
        spare = [int(rng.randrange(4) == 0) for _ in range(n)]
        tree = nx.from_prufer_sequence(code)
        extra = added_rng.choice([list(pair) for pair in combinations(range(n), 2) if not tree.has_edge(*pair)])
        for name in ("tree", "tree_plus_meeting"):
            graph = tree.copy()
            if name == "tree_plus_meeting":
                graph.add_edge(*extra)
            shared = sorted(tuple(sorted(p)) for p in graph.edges)
            loose = [max(0, 3 - graph.degree(v)) + spare[v] for v in range(n)]
            stars = fix.source_from(shared, loose)
            yield {"pair_index": i, "weighting": name, "knots": n, "distinctions": len(shared) + sum(loose),
                   "prufer": code, "coins": spare, "extra_meeting": extra if name != "tree" else None,
                   "cycle_length": len(nx.cycle_basis(graph)[0]) if name != "tree" else None,
                   "meetings": shared, "loose": loose, "stars": stars,
                   "laws": {law: full_run(stars, law, shared) for law in LAWS}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=256)
    parser.add_argument('--output', type=Path, default=OUT/'draws.jsonl')
    args = parser.parse_args()
    with args.output.open('w') as f:
        for row in source_rows(args.limit):
            print(json.dumps(row, separators=(',', ':')), file=f)
            f.flush()


if __name__ == '__main__':
    main()
