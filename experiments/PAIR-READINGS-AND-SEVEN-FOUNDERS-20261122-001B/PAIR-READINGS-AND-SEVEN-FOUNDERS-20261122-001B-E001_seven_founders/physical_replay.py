"""Independent named ordinary replay of the four-cut seven-founder catalogue."""

import argparse
from collections import Counter
from dataclasses import dataclass
from functools import cache, lru_cache
import gzip
from hashlib import sha256
from itertools import combinations
import json
from math import comb, factorial
from pathlib import Path
import os
import subprocess
import sys
from tempfile import NamedTemporaryFile

import networkx as nx
from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
LAWS = ("parity", "nae")
HORIZON = 4
PACKED_THRESHOLD = 128
PREVIOUS = "TWO-EXTRA-MEETINGS-AND-SEPARATE-POINTERS-20261121-001A"
ORDINARY = "ORDINARY-DYNAMICS-20261120-001A"


@dataclass(frozen=True)
class Frame:
    stars: tuple
    owners: dict
    loose: dict
    witnesses: tuple
    components: tuple
    pairs: tuple
    proposals: tuple


def named_source(n, edges, flags):
    meetings = nx.Graph()
    meetings.add_nodes_from(range(n))
    meetings.add_edges_from(edges)
    assert nx.is_connected(meetings)
    assert edges == tuple(sorted(set(edges))) and all(0 <= a < b < n for a, b in edges)
    assert all(b in (0, 1) for b in flags)
    rows = [[] for _ in range(n)]
    for name, (a, b) in enumerate(edges):
        rows[a].append(name)
        rows[b].append(name)
    next_name = len(edges)
    for h, (row, extra) in enumerate(zip(rows, flags, strict=True)):
        supply = max(0, 3 - meetings.degree(h)) + extra
        row.extend(range(next_name, next_name + supply))
        next_name += supply
        assert len(row) >= 3
    return tuple(tuple(row) for row in rows)


def inspect(stars):
    owners = {}
    for h, row in enumerate(stars):
        for d in row:
            current = owners.setdefault(d, [])
            assert len(current) < 2 and (not current or current[-1] < h)
            current.append(h)
    public = [set() for _ in stars]
    loose = {}
    for d, uses in owners.items():
        if len(uses) == 1:
            loose.setdefault(uses[0], []).append(d)
        else:
            left, right = uses
            public[left].add(right)
            public[right].add(left)
    reached = {0}
    todo = [0]
    while todo:
        extra = public[todo.pop()] - reached
        reached.update(extra)
        todo.extend(extra)
    assert len(reached) == len(stars)

    loose = {h: tuple(sorted(row)) for h, row in sorted(loose.items())}
    live = set(loose)
    witnesses = tuple((h, tuple(sorted(part))) for h, row in enumerate(public)
                      if len(part := row & live) >= 2)
    view = nx.Graph()
    view.add_nodes_from(loose)
    view.add_edges_from(p for _, row in witnesses for p in combinations(row, 2))
    parts = tuple(sorted(tuple(sorted(c)) for c in nx.connected_components(view)))
    seen = tuple(sorted(tuple(sorted(pair)) for pair in view.edges))
    blocks = tuple(frozenset(row) for _, row in witnesses)
    # A complete candidate is held if a single physical knot witnesses it.
    # Any subfamily of a held set is held too, so maximal valid groups are
    # exactly maximal cliques passing that witness test.
    maximal = tuple(sorted(tuple(sorted(g)) for g in nx.find_cliques(view)
                           if len(g) >= 3 and not any(set(g) <= b for b in blocks)))
    used = {pair for group in maximal for pair in combinations(group, 2)}
    proposals = maximal + tuple(pair for pair in seen if pair not in used)
    return Frame(stars, owners, loose, witnesses, parts, seen, proposals)


def support_mask(row):
    return sum(1 << d for d in row)


def span_basis(stars):
    basis = {}
    for support in stars:
        row = support_mask(support)
        while row:
            key = row.bit_length() - 1
            if key not in basis:
                basis[key] = row
                break
            row ^= basis[key]
    return basis


def in_span(basis, target):
    while target:
        pivot = target.bit_length() - 1
        if pivot not in basis:
            return False
        target ^= basis[pivot]
    return True


def sum_rows(stars):
    result = 0
    for row in stars:
        result ^= support_mask(row)
    return result


def physical_order(groups):
    return tuple(sorted(row for row in groups if len(row) >= 3)) + tuple(
        sorted(row for row in groups if len(row) == 2)) + tuple(sorted(row for row in groups if len(row) == 1))


@lru_cache(maxsize=128)
def plan(stars):
    before = inspect(stars)
    if not before.loose:
        return before, (), (), (), (), ()
    demand = Counter(p for group in before.proposals for p in group)
    shortage = tuple((p, demand[p] - len(names)) for p, names in before.loose.items()
                     if demand[p] > len(names))
    if shortage:
        return before, shortage, (), (), (), ()
    groups = before.proposals + tuple((p,) for p, names in before.loose.items()
                                      for _ in range(len(names) - demand[p]))
    assert physical_order(groups) == groups
    indices = {p: iter(names) for p, names in before.loose.items()}
    inputs = tuple(tuple(next(indices[p]) for p in q) for q in groups)
    assert all(next(names, None) is None for names in indices.values())
    for group, values in zip(groups, inputs, strict=True):
        assert all(before.owners[d] == [p] for p, d in zip(group, values, strict=True))
    assert len({d for word in inputs for d in word}) == sum(map(len, before.loose.values()))
    start = max(before.owners) + 1
    trial_rows = stars + tuple(row + (start + i,) for i, row in enumerate(inputs))
    trial = inspect(trial_rows)
    demand = Counter(p for group in trial.proposals for p in group)
    return before, shortage, groups, inputs, tuple(demand[len(stars) + i] for i in range(len(groups))), trial.components


def literals(before, index, parents, inputs, lookahead, fresh):
    assert len(parents) == len(inputs)
    return {"holder": len(before.stars) + index, "parents": parents, "paid_names": inputs,
            "lookahead_demand": lookahead, "grant": len(fresh), "fresh_names": fresh}


def compact_end(frame):
    return {"opens": tuple((h, len(names)) for h, names in frame.loose.items()),
            "components": frame.components}


def name_end(frame):
    return {"loose_names": tuple(frame.loose.items()), "witnessed_live_subsets": frame.witnesses,
            "components": frame.components}


def pack_births(before, groups, demands, grants):
    """Retain the ordered roster to reconstruct each actual physical payment."""
    return {"encoding": "named_groups_and_contiguous_fresh", "first_child": len(before.stars),
            "first_fresh": max(before.owners) + 1,
            "ordered_parent_groups": groups, "lookahead_demands": demands, "grants": grants}


def unpack_births(before, record):
    assert record["encoding"] == "named_groups_and_contiguous_fresh"
    assert record["first_child"] == len(before.stars)
    assert record["first_fresh"] == max(before.owners) + 1
    indices = {p: iter(names) for p, names in before.loose.items()}
    fresh_at = record["first_fresh"]
    new = []
    for index, (group, demand, amount) in enumerate(zip(record["ordered_parent_groups"],
                                                        record["lookahead_demands"], record["grants"], strict=True)):
        paid = tuple(next(indices[p]) for p in group)
        fresh = tuple(range(fresh_at, fresh_at + amount))
        new.append(literals(before, index, group, paid, demand, fresh))
        fresh_at += amount
    assert all(next(names, None) is None for names in indices.values())
    return new


def terminal_receipt(before, inputs):
    support = support_mask(inputs)
    old_rank = len(span_basis(before.stars))
    assert support == sum_rows(before.stars)
    assert old_rank == len(before.stars)
    assert set(inputs) == {d for row in before.loose.values() for d in row}
    augmented = inputs + (max(before.owners) + 1,)
    odd_rank = len(span_basis(before.stars + (augmented,)))
    assert odd_rank == old_rank + 1
    assert len(span_basis(before.stars + (inputs,))) == old_rank
    return {"terminal_arity": len(inputs), "old_width": len(before.owners),
            "all_even_coefficient_rank_before_and_after": [old_rank, old_rank],
            "final_single_odd_augmented_rank": odd_rank,
            "old_rows_summed": tuple(range(len(before.stars))),
            "sum_of_old_rows_is_actual_input_support": True,
            "even_words_kept": 1 << (len(before.owners) - old_rank),
            "single_odd_words": 0}


def trace(start, law, horizon=HORIZON):
    current = start
    cuts = []
    histories = [inspect(current).components]
    terminal = None
    status = "open"
    for age in range(1, horizon + 1):
        before, shortage, groups, inputs, demands, provisional = plan(current)
        if shortage:
            status = "stall"
            cuts.append({"age": age, "status": status, "shortages": shortage, "begin": name_end(before),
                         "multiple_groups": before.proposals, "births": []})
            break
        assert before.loose and groups

        # Connected complete physical holdings, one chosen loose name per
        # paid parent, and exactly two holders for every pre-existing shared
        # name justify the only compressed implication case.
        compact = len(before.components) > 1 and len(groups) > PACKED_THRESHOLD
        if compact:
            assert len(groups) >= len(before.components) >= 2
            assert all(any(set(group) <= set(component) for component in before.components) for group in groups)
            implied = tuple(False for _ in groups)
            parity_test = "connected_whole_and_two_or_more_paid_groups"
            actual_targets = tuple(i for i, d in enumerate(demands) if d == 0)
            if actual_targets:
                old_basis = span_basis(current)
                assert not any(in_span(old_basis, support_mask(inputs[i])) for i in actual_targets)
        else:
            old_basis = span_basis(current)
            implied = tuple(in_span(old_basis, support_mask(row)) for row in inputs)
            assert implied == ((True,) if len(groups) == 1 else tuple(False for _ in groups))
            parity_test = "literal_named_GF2"
            actual_targets = tuple(range(len(groups)))
        grants = tuple(0 if law == "parity" and imp else max(1, 3 - len(g), need)
                       for g, need, imp in zip(groups, demands, implied, strict=True))
        if law == "nae":
            assert all(len(row) >= 3 for row in current)
        closures = [i for i, f in enumerate(grants) if f == 0]
        if closures:
            assert law == "parity" and len(groups) == 1 and demands == (0,)
            terminal = terminal_receipt(before, inputs[0]) | {"holder": len(current), "inputs": inputs[0], "age": age}
        next_name = max(before.owners) + 1
        births = []
        for i, (group, used, demand, grant) in enumerate(zip(groups, inputs, demands, grants, strict=True)):
            fresh = tuple(range(next_name, next_name + grant))
            births.append(literals(before, i, group, used, demand, fresh))
            next_name += grant

        after = current + tuple(row["paid_names"] + row["fresh_names"] for row in births)
        followed = inspect(after)
        assert followed.loose == {b["holder"]: b["fresh_names"] for b in births if b["grant"]}
        assert (not followed.loose) == bool(closures)
        if not closures:
            assert followed.components == provisional
            assert len(followed.components) >= len(before.components)
        else:
            assert not followed.components
        component_by_holder = {h: c for c in before.components for h in c}
        component_calls = Counter(component_by_holder[g[0]] for g in groups)
        proper_closure_controls = []
        if len(before.components) > 1:
            for pos, g in enumerate(groups):
                piece = component_by_holder[g[0]]
                if component_calls[piece] != 1:
                    continue
                assert demands[pos] == 0 and pos in actual_targets and not implied[pos]
                assert set(inputs[pos]) == {d for h in piece for d in before.loose[h]}
                other_live = tuple((h, ds) for h, ds in before.loose.items() if h not in piece)
                assert other_live and grants[pos] > 0
                proper_closure_controls.append({"sole_child_in_its_live_component": births[pos],
                                                "old_live_component": piece, "other_old_loose_names": other_live,
                                                "actual_paid_input_outside_old_row_span": True})
        histories.append(followed.components)
        row = {"age": age, "status": "funded", "number_of_births": len(groups),
               "number_of_paid_names": sum(map(len, inputs)), "new_names": sum(grants),
               "zero_grants": tuple(births[i]["holder"] for i in closures),
               "parity_implication_check": parity_test, "whole_closed": bool(closures),
               "sole_whole_paying_child": len(groups) == 1,
               "paid_targets_actually_checked_by_GF2": len(actual_targets),
               "zero_demand_targets_checked_by_GF2": sum(demands[i] == 0 for i in actual_targets),
               "proper_live_component_closure_attempts": proper_closure_controls}
        if compact:
            packed = pack_births(before, groups, demands, grants)
            assert unpack_births(before, packed) == births
            row.update(begin=compact_end(before), end=compact_end(followed), births=packed)
        else:
            row.update(begin=name_end(before), end=name_end(followed), births=births)
        cuts.append(row)
        current = after
        if closures:
            status = "closed"
            break

    return {"termination": status, "last_paid_age": sum(cut["status"] == "funded" for cut in cuts),
            "cuts": cuts, "live_components_by_age": list(map(len, histories)),
            "first_split_age": next((i for i, components in enumerate(histories) if len(components) > 1), None),
            "terminal": terminal, "final_holders": len(current),
            "final_distinctions": len({d for row in current for d in row})}


def replay_rows(stars, history):
    frames = [stars]
    groups = []
    for cut in history["cuts"]:
        if cut["status"] == "stall":
            break
        raw = cut["births"]
        if isinstance(raw, dict):
            raw = unpack_births(inspect(frames[-1]), raw)
        assert len(raw) == cut["number_of_births"]
        following = frames[-1] + tuple(b["paid_names"] + b["fresh_names"] for b in raw)
        assert sum(len(row["paid_names"]) for row in raw) == cut["number_of_paid_names"]
        assert sum(len(row["fresh_names"]) for row in raw) == cut["new_names"]
        groups.append(raw)
        frames.append(following)
    return frames, groups


def reverse_replay(stars, history, law):
    frames, layers = replay_rows(stars, history)
    final_width = len({d for row in frames[-1] for d in row})
    renames = {d: final_width - 1 - d for d in range(final_width)}
    reverse = list(reversed(range(len(stars))))
    for old, new in zip(frames[:-1], frames[1:], strict=True):
        reverse.extend(reversed(range(len(old), len(new))))
    to_new = {old: new for new, old in enumerate(reverse)}
    checked = 0
    for age, layer in enumerate(layers, start=1):
        previous = frames[age - 1]
        recoded = tuple(tuple(renames[d] for d in previous[k]) for k in reverse[:len(previous)])
        old, shortages, proposal, _, demand, _ = plan(recoded)
        assert not shortages
        if law == "parity" and len(proposal) == 1:
            grant = (0,)
        else:
            grant = tuple(max(1, 3 - len(g), n) for g, n in zip(proposal, demand, strict=True))
        assert Counter(zip(proposal, demand, grant, strict=True)) == Counter(
            (tuple(sorted(to_new[k] for k in child["parents"])), child["lookahead_demand"], child["grant"])
            for child in layer)
        paid = [renames[d] for child in layer for d in child["paid_names"]]
        assert sorted(paid) == sorted(d for names in old.loose.values() for d in names)
        basis = span_basis(recoded)
        for child in layer:
            inputs = tuple(renames[d] for d in child["paid_names"])
            births = tuple(renames[d] for d in child["fresh_names"])
            assert in_span(basis, support_mask(inputs)) == (len(layer) == 1)
            assert all(old.owners[d] == [to_new[k]] for d, k in zip(inputs, child["parents"], strict=True))
            row_after = frames[age][child["holder"]]
            assert set(inputs + births) == {renames[d] for d in row_after}
            checked += 1
        transformed = tuple(tuple(renames[d] for d in frames[age][k]) for k in reverse[:len(frames[age])])
        after = inspect(transformed)
        assert after.loose == {to_new[b["holder"]]: tuple(sorted(renames[d] for d in b["fresh_names"]))
                               for b in layer if b["grant"]}
    if history["termination"] == "stall":
        failed = history["cuts"][-1]
        previous = frames[-1]
        recoded = tuple(tuple(renames[d] for d in previous[k]) for k in reverse[:len(previous)])
        _, shortages, groups, _, _, _ = plan(recoded)
        assert shortages == tuple(sorted((to_new[k], n) for k, n in failed["shortages"])) and not groups
    return {"new_holder_order_to_original": reverse, "new_distinction_of_original": [renames[d] for d in renames],
            "number_of_paid_names_replayed_by_child": checked,
            "transported_founder": tuple(tuple(renames[d] for d in stars[k]) for k in reverse[:len(stars)]),
            "unary_copies_and_amounts_preserved": True}


def effective_blocks(witnesses):
    raw = set(tuple(row) for _, row in witnesses)
    return tuple(sorted(row for row in raw if not any(set(row) < set(other) for other in raw)))


def as_end_graph(hints):
    result = nx.Graph()
    result.add_nodes_from((h, {"kind": "owner", "loose": len(row)}) for h, row in hints["loose_names"])
    for i, block in enumerate(effective_blocks(hints["witnessed_live_subsets"]), start=1):
        result.add_node(-i, kind="witness", loose=0)
        result.add_edges_from((-i, h) for h in block)
    return result


def repeated_ends(stars, history):
    if history["termination"] != "open" or history["live_components_by_age"][-1] != 1:
        return []
    frames, _ = replay_rows(stars, history)
    observed = [name_end(inspect(row)) for row in frames]
    graphs = list(map(as_end_graph, observed))
    equal = []
    for a, b in combinations(range(len(graphs)), 2):
        check = nx.isomorphism.GraphMatcher(graphs[a], graphs[b], node_match=lambda x, y: x == y)
        if check.is_isomorphic():
            how = {i: j for i, j in check.mapping.items() if i >= 0}
            counts = [{h: len(row) for h, row in observed[k]["loose_names"]} for k in (a, b)]
            assert {how[h]: n for h, n in counts[0].items()} == counts[1]
            older = {tuple(sorted(how[h] for h in block))
                     for block in effective_blocks(observed[a]["witnessed_live_subsets"])}
            assert older == set(effective_blocks(observed[b]["witnessed_live_subsets"]))
            equal.append({"age_pair": [a, b], "live_holder_transport": sorted(how.items()),
                          "preserves_loose_and_all_maximal_witness_subsets": True})
    return equal


@cache
def founder_checks(n, edges):
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    graph.add_edges_from(edges)
    result = {}
    for h in graph:
        erased = graph.copy()
        erased.remove_node(h)
        components = []
        for part in sorted(tuple(sorted(c)) for c in nx.connected_components(erased)):
            pivot = next((k for k in part if graph.degree(k) <= 2), None)
            assert pivot is not None
            components.append({"component": part, "degree_at_most_two_pivot": pivot})
        result[h] = components
    return result


def solver_for(stars, law, physical_width=0):
    solver = Minisat22()
    internal = max(physical_width, max(d for row in stars for d in row) + 1) + 1
    for support in stars:
        row = [d + 1 for d in support]
        if law == "nae":
            solver.add_clause(row)
            solver.add_clause([-d for d in row])
            continue
        left = row[0]
        for right in row[1:]:
            new = internal
            internal += 1
            for clause in ((left, right, -new), (-left, -right, -new), (left, -right, new), (-left, right, new)):
                solver.add_clause(list(clause))
            left = new
        solver.add_clause([-left])
    return solver


def complete_word_check(solver, scope, word):
    pins = [(d + 1) if word & (1 << i) else -(d + 1) for i, d in enumerate(scope)]
    return solver.solve(assumptions=pins)


def canonical(word, arity, law):
    return word.bit_count() % 2 == 0 if law == "parity" else word not in (0, (1 << arity) - 1)


@cache
def canonical_cli(arity, law):
    if arity < 2:
        return {"arity": arity, "method": "direct one-place even terminal projection",
                "whole_is_restrictive": True, "only_proper_projection_full": True,
                "ordinary_small_arity_exception": True, "canonical_loop_role_arity": False}
    names = [f"f{i}" for i in range(arity)]
    clauses = [" ".join(f"~{d}" if word & (1 << i) else d for i, d in enumerate(names))
               for word in range(1 << arity) if not canonical(word, arity, law)]
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "; ".join(clauses),
           "--loops", *names[:-1], "--contact", names[-1], "--json"]
    data = subprocess.run(cmd, cwd=ROOT, env=os.environ | {"PYTHONPATH": str(ROOT / "tools")},
                          capture_output=True, text=True)
    if arity == 2:
        assert data.returncode == 2 and "a knot binds at least two loops" in data.stderr
        return {"arity": arity, "whole_projection_words": [0, 3] if law == "parity" else [1, 2],
                "each_single_name_free": True, "ordinary_small_arity_exception": True,
                "canonical_loop_role_arity": False, "cli_result": data.stderr.strip()}
    data.check_returncode()
    row = json.loads(data.stdout)
    assert row["is_knot"] and row["binding"] and row["invisible_in_parts"] and row["coexistence"]
    return {"arity": arity, "allowed_count": len(row["allowed"]), "K1_K2_K3": True}


def original_lawful_stars(stars):
    ballot = {}
    width = max(d for row in stars for d in row) + 1
    for law in LAWS:
        receipt = []
        with solver_for(stars, law) as solver:
            for holder, support in enumerate(stars):
                arity = len(support)
                raw = [word for word in range(1 << arity) if complete_word_check(solver, support, word)]
                expected = [word for word in range(1 << arity) if canonical(word, arity, law)]
                assert raw == expected
                with solver_for(stars[:holder] + stars[holder + 1:], law, width) as other:
                    assert all(complete_word_check(other, support, word) for word in range(1 << arity))
                receipt.append({"holder": holder, "canonically_admitted": raw, "erasing_row_leaves_full_support": True})
        ballot[law] = receipt
    return ballot


def tested_nae_inputs(frames, layers):
    records = []
    for age, layer in enumerate(layers, 1):
        with solver_for(frames[age - 1], "nae") as solver:
            for birth in layer:
                scope = tuple(birth["paid_names"])
                assert complete_word_check(solver, scope, 0)
                assert complete_word_check(solver, scope, (1 << len(scope)) - 1)
        records.append({"age": age, "births": len(layer), "uniform_inputs_extend_both_ways": True})
    return records


def archived_six():
    old_art = ROOT / "artifacts" / PREVIOUS / (PREVIOUS + "-E001_meetings") / "physical_population.json.gz"
    population = json.loads(gzip.decompress(old_art.read_bytes()))
    archive, = (row for row in population if row["laws"]["parity"]["termination"] == "closed")
    flags = tuple(archive["extra"])
    edges = tuple(map(tuple, archive["edges"]))
    assert flags == (0, 0, 0, 0, 1, 1)
    stars = named_source(6, edges, flags)
    assert stars == tuple(map(tuple, archive["founder_rows"]))
    own = {}
    for law in LAWS:
        present = trace(stars, law)
        frames, layers = replay_rows(stars, present)
        ref = archive["laws"][law]["cuts"]
        assert len(layers) == len(ref) == HORIZON
        assert tuple(len(row) for row in layers) == (4, 4, 3, 1)
        for computed, older in zip(layers, ref, strict=True):
            assert [(b["parents"], b["paid_names"], b["grant"]) for b in computed] == [
                (tuple(b["parents"]), tuple(b["inputs"]), b["fresh"]) for b in older["births"]]
        assert present["termination"] == archive["laws"][law]["termination"]
        own[law] = present
        if law == "nae":
            own[law]["literal_uniform_input_extension"] = tested_nae_inputs(frames, layers)
    return {"archived_six_founder_id": archive["id"], "edges": edges, "flags": flags, "founder_rows": stars, "laws": own}


def catalogue_checks(entries):
    grouped = {}
    ids = set()
    for row in entries:
        edges = tuple(map(tuple, row["edges"]))
        flags = tuple(row["flags"])
        assert len(edges) == 8 and len(flags) == 7 and row["id"] not in ids
        ids.add(row["id"])
        bucket = grouped.setdefault(edges, {})
        assert flags not in bucket
        bucket[flags] = row
    labelled_unflagged = 0
    tree_origins = 0
    shapes = []
    for edges, bucket in sorted(grouped.items()):
        graph = nx.Graph(edges)
        assert nx.is_connected(graph) and set(graph) == set(range(7))
        automorphisms = tuple(tuple(perm[h] for h in range(7))
                              for perm in nx.isomorphism.GraphMatcher(graph, graph).isomorphisms_iter())
        def canonical_flags(name):
            return min(tuple(name[k] for k in perm) for perm in automorphisms)
        expected = {canonical_flags(tuple(map(int, f"{mask:07b}"))) for mask in range(1 << 7)}
        assert {canonical_flags(flags) for flags in bucket} == expected and len(bucket) == len(expected)
        tau = 0
        for subset in combinations(edges, 6):
            tree = nx.Graph(subset)
            tau += set(tree) == set(range(7)) and nx.is_tree(tree)
        assert tau > 0
        for flags, row in bucket.items():
            decorated_symmetries = sum(flags == tuple(flags[h] for h in p) for p in automorphisms)
            assert row["labelled"] == factorial(7) // decorated_symmetries
            assert row["tau"] == tau
            assert row["distinct_mass"] == row["labelled"] * 3 ** (7 - sum(flags))
            assert row["tree_edit_mass"] == tau * row["distinct_mass"]
        labelled = factorial(7) // len(automorphisms)
        assert sum(x["labelled"] for x in bucket.values()) == labelled * (1 << 7)
        labelled_unflagged += labelled
        tree_origins += labelled * tau
        shapes.append({"canonical_meetings": edges, "tau": tau,
                       "labelled_unflagged": labelled, "literal_private_pivots_after_any_holder_erasure":
                       founder_checks(7, edges)})
    assert tree_origins == 7 ** 5 * comb(15, 2)
    return {"shapes": shapes, "distinct_unflagged_labelled": labelled_unflagged,
            "tree_edit_unflagged_labelled": tree_origins,
            "total_unweighted_labelled_flagged": labelled_unflagged * 2 ** 7,
            "distinct_mass_denominator": labelled_unflagged * 4 ** 7,
            "tree_edit_mass_denominator": tree_origins * 4 ** 7}


def add_controls(row, roles):
    stars = row["founder_rows"]
    row["literal_founder_projection_and_row_erasure"] = original_lawful_stars(stars)
    row["coherent_physical_reversal"] = {}
    for law in LAWS:
        r = row["laws"][law]
        row["coherent_physical_reversal"][law] = reverse_replay(stars, r, law)
        if law == "nae" and "terminal_candidate" in roles:
            frames, layers = replay_rows(stars, r)
            r["literal_uniform_NAE_input_extension_checks"] = tested_nae_inputs(frames, layers)
    row["proof_control_roles"] = sorted(roles)


def all_cases(catalogue):
    summary = catalogue_checks(catalogue)
    census = {law: Counter() for law in LAWS}
    by_outcome = Counter()
    labelled_outcome = Counter()
    direct = Counter()
    edited = Counter()
    records = []
    arities = {"founders": set(), "closing": set()}
    for source in catalogue:
        edges = tuple(map(tuple, source["edges"]))
        flags = tuple(source["flags"])
        start = named_source(7, edges, flags)
        one = dict(source) | {"founder_rows": start, "laws": {}}
        arities["founders"].update(map(len, start))
        for law in LAWS:
            r = trace(start, law)
            one["laws"][law] = r
            arity = None if r["terminal"] is None else r["terminal"]["terminal_arity"]
            if arity is not None:
                arities["closing"].add(arity)
            initial = r["live_components_by_age"][0]
            last = r["live_components_by_age"][-1]
            key = law, r["termination"], r["last_paid_age"], initial, last, arity
            by_outcome[key] += 1
            labelled_outcome[key] += source["labelled"]
            direct[key] += source["distinct_mass"]
            edited[key] += source["tree_edit_mass"]
            domain = census[law]
            domain[r["termination"]] += 1
            domain["paid_cuts"] += r["last_paid_age"]
            domain["total_births"] += sum(c.get("number_of_births", 0) for c in r["cuts"])
            domain["actual_row_span_checks"] += sum(c.get("paid_targets_actually_checked_by_GF2", 0) for c in r["cuts"])
            domain["actual_zero_demand_row_span_checks"] += sum(
                c.get("zero_demand_targets_checked_by_GF2", 0) for c in r["cuts"])
            domain["proper_live_component_closure_attempts"] += sum(
                len(c.get("proper_live_component_closure_attempts", ())) for c in r["cuts"])
            domain["whole_paying_candidates"] += sum(c.get("sole_whole_paying_child", False) for c in r["cuts"])
            domain["packed_cuts"] += sum(isinstance(c["births"], dict) for c in r["cuts"])
            domain["max_holders"] = max(domain["max_holders"], r["final_holders"])
            domain["max_distinctions"] = max(domain["max_distinctions"], r["final_distinctions"])
            domain["max_birth_cohort"] = max(domain["max_birth_cohort"],
                                             *(c.get("number_of_births", 0) for c in r["cuts"]))
            if r["termination"] == "stall":
                domain["earlier_paid_cuts_before_stall"] += r["last_paid_age"]
            if not r["last_paid_age"]:
                assert r["termination"] == "stall" and len(r["cuts"]) == 1
            if r["termination"] == "open":
                assert r["last_paid_age"] == HORIZON
                domain["open_and_connected_at_four"] += last == 1
                domain["open_and_split_at_four"] += last > 1
        p, n = (one["laws"][law] for law in LAWS)
        assert n["termination"] != "closed"
        assert (p["termination"] == "stall") == (n["termination"] == "stall")
        p_cut, n_cut = p["cuts"], n["cuts"]
        if p["termination"] == "closed":
            assert p_cut[:-1] == n_cut[:len(p_cut)-1]
            final = p_cut[-1]["births"][0]
            matched = n_cut[len(p_cut)-1]["births"][0]
            assert final["paid_names"] == matched["paid_names"] and final["parents"] == matched["parents"]
            assert (final["grant"], matched["grant"]) == (0, max(1, 3 - len(final["parents"])))
        else:
            assert p_cut == n_cut
        records.append(one)
    for law in LAWS:
        assert sum(labelled_outcome[k] for k in by_outcome if k[0] == law) == summary["total_unweighted_labelled_flagged"]
        assert sum(direct[k] for k in by_outcome if k[0] == law) == summary["distinct_mass_denominator"]
        assert sum(edited[k] for k in by_outcome if k[0] == law) == summary["tree_edit_mass_denominator"]

    positive = [x for x in records if x["laws"]["parity"]["termination"] == "closed"]
    rank = lambda x: (x["laws"]["parity"]["last_paid_age"], x["laws"]["parity"]["final_holders"],
                      x["laws"]["parity"]["final_distinctions"], len({n for r in x["founder_rows"] for n in r}),
                      x["edges"], x["flags"])
    positive.sort(key=rank)
    canonical_orders = sorted(records, key=lambda x: (x["edges"], x["flags"]))
    roles = {}
    def select(x, why):
        roles.setdefault(x["id"], set()).add(why)
    for row in positive:
        select(row, "terminal_candidate")
        for neighbour in canonical_orders:
            if neighbour["edges"] == row["edges"] and sum(
                    i != j for i, j in zip(neighbour["flags"], row["flags"], strict=True)) == 1:
                select(neighbour, "one_flag_neighbour_of_an_actual_closure")
    for row in canonical_orders:
        r = row["laws"]["parity"]
        if r["termination"] == "open" and r["live_components_by_age"][0] == 1:
            select(row, "initially_funded_connected_parity_survivor")
        if r["termination"] == "open" and r["live_components_by_age"][-1] == 1:
            r["exact_repeated_end_isomorphisms"] = repeated_ends(row["founder_rows"], r)
    if not positive:
        reported = next((row for row in canonical_orders if row["id"] in roles),
                        next(row for row in canonical_orders if row["laws"]["parity"]["last_paid_age"]))
        select(reported, "first_bounded_open_control")
    for status in ("stall", "open"):
        example = next((j for j in canonical_orders if j["laws"]["parity"]["termination"] == status), None)
        if example is not None:
            select(example, "lexical_" + status + "_reversal_control")
    repeated_unary = None
    for example in canonical_orders:
        if any(len(births := cut["births"]) and isinstance(births, list)
               and max(Counter(b["parents"] for b in births if len(b["parents"]) == 1).values(), default=0) > 1
               for cut in example["laws"]["parity"]["cuts"]):
            repeated_unary = example
            break
    if repeated_unary is not None:
        select(repeated_unary, "repeated_unary_reversal_control")
    for row in records:
        if row["id"] in roles:
            add_controls(row, roles[row["id"]])

    weights = [{"law": k[0], "termination": k[1], "last_paid_age": k[2], "initial_live_components": k[3],
                "final_live_components": k[4], "terminal_arity": k[5],
                "orbits": by_outcome[k], "labelled": labelled_outcome[k],
                "distinct_mass": direct[k], "tree_edit_mass": edited[k]}
               for k in sorted(by_outcome, key=repr)]
    summary |= {"decorated_classes": len(catalogue), "laws": {key: dict(value) for key, value in census.items()},
                "outcomes": weights, "ranked_actual_parity_closures": [x["id"] for x in positive],
                "ranked_parity_closures_of_arity_at_least_three": [
                    x["id"] for x in positive if x["laws"]["parity"]["terminal"]["terminal_arity"] >= 3],
                "physical_controls": {x: sorted(y) for x, y in roles.items()},
                "canonical_arity_check": {
                    law: [canonical_cli(arity, law) for arity in sorted(arities["founders"] |
                          {max(3, k) if law == "nae" else k for k in arities["closing"]})]
                    for law in LAWS
                }}
    return records, summary


def input_hashes(population):
    scope = ROOT / "research" / HERE.parent.name
    prereg = scope / "preregistration.md"
    approved = scope / "advisor_receipt.json"
    prereg_hash = sha256(prereg.read_bytes()).hexdigest()
    assert prereg_hash in approved.read_text()
    predecessor = ROOT / "artifacts" / PREVIOUS / (PREVIOUS + "-E001_meetings") / "physical_population.json.gz"
    ordinary = ROOT / "experiments" / ORDINARY / (ORDINARY + "-E001_ordinary") / "end_operator.py"
    paths = [Path(__file__).resolve(), population, prereg, approved, predecessor, ordinary,
             ROOT / "tools/knotlab/cli.py", ROOT / "tools/knotlab/knots.py"]
    return {str(p.resolve().relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths}


def write_events(stream, cases):
    with gzip.GzipFile(filename="", fileobj=stream, mode="wb", mtime=0) as dst:
        dst.write(b"[\n")
        for i, row in enumerate(cases):
            if i:
                dst.write(b",\n")
            dst.write(json.dumps(row, sort_keys=True, separators=(",", ":")).encode())
        dst.write(b"\n]\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", type=Path, default=OUT / "population.json.gz")
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    hashes = input_hashes(args.population)
    with gzip.open(args.population, "rt") as stream:
        catalogue = json.load(stream)
    earlier = archived_six()
    cases, summary = all_cases(catalogue)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    events = args.output_dir / "physical_events.json.gz"
    report = args.output_dir / "physical_summary.json"
    with NamedTemporaryFile(dir=args.output_dir, prefix=".physical_replay.", delete=False) as buffer:
        name = Path(buffer.name)
        try:
            write_events(buffer, cases)
            buffer.flush()
            receipt = summary | {"schema": "b293-physical-v1", "horizon": HORIZON,
                                 "source_hashes": hashes, "paired_archived_six_founder_control": earlier,
                                 "physical_events_sha256": sha256(name.read_bytes()).hexdigest(),
                                 "packed_record_semantics": pack_births.__doc__}
            payload = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()
            if args.verify:
                assert events.read_bytes() == name.read_bytes() and report.read_bytes() == payload
            else:
                name.replace(events)
                report.write_bytes(payload)
            print("B293", len(cases), json.dumps(summary["laws"], sort_keys=True),
                  receipt["physical_events_sha256"], sha256(payload).hexdigest())
        finally:
            name.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
