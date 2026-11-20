"""Verify allowed-state lawfulness and the identified growth of the closing witnesses."""

from argparse import ArgumentParser
from collections import Counter
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "artifacts" / HERE.parent.name / HERE.name
OUT = DATA / "source_cert.json"
DESIGN = ROOT / "research/ORDINARY-DYNAMICS-20261120-001/definitions.md"
NAE = "NAE-GROWTH-20261119-001B"
DIMS = "DOUBLE-IDENT-20261119-001B"
THROUGH = 6


def local_module(identity, path):
    loader = spec_from_file_location(identity, path)
    module = module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


@cache
def growth_libraries():
    nae = local_module("source_certificate_nae", ROOT / "experiments" / NAE / (NAE + "-E001_nae") / "naelib.py")
    dims = local_module("source_certificate_dims", ROOT / "experiments" / DIMS / (DIMS + "-E001_dims") / "dims.py")
    return nae, dims


def fixtures():
    for extra in (0, 1):
        yield f"star/{extra}", {"source_kind": "three leaves at a hub", "hub": 0, "far": 0,
                               "u": [1, 2, 3], "ordinary_distance": 1, "extra": extra,
                               "sizes": [3 + extra, 3, 3, 3], "meetings": [(0, v) for v in (1, 2, 3)]}
    for length, all_doubled in [(n, False) for n in (4, 5, 8, 16)] + [(4, True)]:
        rails, meetings = [], []
        for rail in range(3):
            mid = list(range(2 + rail * (length - 1), 2 + (rail + 1) * (length - 1)))
            walk = [0, *mid, 1]
            rails.append(walk)
            for i, (u, v) in enumerate(zip(walk, walk[1:])):
                multiplicity = 1 if i in (0, length - 1) and not all_doubled else 2
                meetings.extend([tuple(sorted((u, v)))] * multiplicity)
        arity = Counter(v for meeting in meetings for v in meeting)
        live = [rail[1] for rail in rails]
        for extra in (0, 1):
            sizes = [arity[v] + 2 * (v in live) + extra * (v == 1) for v in range(3 * length - 1)]
            label = f"theta/{length}/{'all-doubled' if all_doubled else 'interior-doubled'}/{extra}"
            yield label, {"source_kind": "three internally disjoint routes", "hub": 0, "far": 1, "u": live,
                          "ordinary_distance": length - 1, "length": length, "extra": extra,
                          "all_doubled": all_doubled, "rails": rails,
                          "sizes": sizes, "meetings": meetings}


def mask(sites):
    total = 0
    for i in sites:
        total |= 1 << i
    return total


def row_masks(stars):
    return [mask(row) for row in stars]


def supported_equations(rows, sites):
    """Eliminate the physical indices outside a given support first."""
    inside = mask(sites)
    pivots, projected = {}, []
    for x in rows:
        while x & ~inside:
            key = (x & ~inside).bit_length() - 1
            old = pivots.get(key)
            if old is None:
                pivots[key] = x
                break
            x ^= old
        else:
            if x:
                projected.append(mask(i for i, site in enumerate(sites) if x >> site & 1))
    return sorted(set(projected))


def parity_read(rows, sites):
    projected = supported_equations(rows, sites)
    good = [w for w in range(1 << len(sites)) if all((w & e).bit_count() % 2 == 0 for e in projected)]
    return good, projected


def nae_read(solver, stars, sites):
    good, certificates = [], []
    for word in range(1 << len(sites)):
        pinned = [(d + 1) if word >> i & 1 else -(d + 1) for i, d in enumerate(sites)]
        if solver.solve(assumptions=pinned):
            model = {x - 1 for x in solver.get_model() if x > 0}
            assert all(0 < len(model.intersection(row)) < len(row) for row in stars)
            assert mask(i for i, d in enumerate(sites) if d in model) == word
            good.append(word)
            certificates.append(hex(mask(model)))
    return good, certificates


@cache
def canonical_relation(arity, good):
    variables = [f"x{i}" for i in range(arity)]
    bad = sorted(set(range(1 << arity)) - set(good))
    clauses = [" ".join(("~" if v >> j & 1 else "") + d for j, d in enumerate(variables)) for v in bad]
    args = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
            "--loops", *variables[:-1], "--contact", variables[-1], "--json"]
    command = subprocess.run(args, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
                             cwd=ROOT, capture_output=True, text=True)
    raw = json.loads(command.stdout)
    assert command.returncode == 0 and raw["is_knot"] and len(raw["allowed"]) == len(good), raw
    return {"places": arity, "K1_K2_K3": raw["is_knot"], "allowed_count": len(raw["allowed"]),
            "physical_projection_words": good}


def complement_connectivity(stars):
    wired = nx.Graph()
    exterior = len(stars)
    holders = {}
    for k, row in enumerate(stars):
        for d in row:
            holders.setdefault(d, []).append(k)
    for row in holders.values():
        assert len(row) in (1, 2)
        a = row[0]
        b = row[1] if len(row) == 2 else exterior
        wired.add_edge(a, b)
    assert nx.is_connected(wired) and exterior in wired
    answer = []
    for deleted in range(len(stars)):
        others = set(wired) - {deleted}
        comp = wired.subgraph(others)
        path = list(nx.bfs_edges(comp, exterior))
        assert len(path) + 1 == len(others)
        answer.append(path)
    return answer


def frontier(stars, children):
    owners = {}
    for v, row in enumerate(stars):
        for d in row:
            owners.setdefault(d, []).append(v)
    ordinary = [set() for _ in stars]
    live = set()
    for row in owners.values():
        if len(row) == 1:
            live.update(row)
        else:
            a, b = row
            ordinary[a].add(b)
            ordinary[b].add(a)
    pair_children = set(children)
    assert pair_children <= live
    # Display directly the witnessed blocks involving the three pair children.
    blocks = sorted(tuple(sorted(ordinary[v] & pair_children)) for v in range(len(stars))
                    if ordinary[v] & pair_children)
    assert blocks == list(combinations(sorted(pair_children), 2))
    assert all(not (ordinary[v] & (live - pair_children)) for v in range(len(stars)) if ordinary[v] & pair_children)
    return {"near_loose": [[v, sum(owners[d] == [v] for d in stars[v])] for v in sorted(pair_children)],
            "witnessed_blocks": blocks, "other_live": sorted(live - pair_children)}


def layer_summary(P):
    rows = {}
    for v, age in enumerate(P.round_of):
        tally = rows.setdefault(str(age), Counter())
        tally[(P.parents[v], P.fresh[v])] += 1
    return {a: [[p, f, m] for (p, f), m in sorted(tally.items())] for a, tally in rows.items()}


def check_case(source, relations):
    library, dims = growth_libraries()
    sizes, meetings = source["sizes"], source["meetings"]
    old = library.J.stars_from(sizes, meetings)
    assert len(old) == len({frozenset(s) for s in old}) and min(map(len, old)) >= 3
    original = library.S.from_junctions(old)
    complement_paths = complement_connectivity(old)
    graph = nx.Graph(meetings)
    distant = [nx.shortest_path_length(graph, v, source["far"]) for v in source["u"]]
    assert distant == [source["ordinary_distance"]] * 3
    rows = row_masks(old)
    projections = []
    with library._solver(original, len(old)) as solver:
        for knot, row in enumerate(old):
            sites = sorted(row)
            arity = len(sites)
            parity, elimination = parity_read(rows, sites)
            nae, witnesses = nae_read(solver, old, sites)
            assert elimination == [(1 << arity) - 1]
            assert parity == [w for w in range(1 << arity) if w.bit_count() % 2 == 0]
            assert nae == list(range(1, (1 << arity) - 1))
            for name, good in (("parity", parity), ("not-all-equal", nae)):
                key = f"{name}/{arity}"
                item = canonical_relation(arity, tuple(good))
                assert relations.setdefault(key, item) == item
            projections.append({"knot": knot, "scope": sites, "arity": arity,
                                "parity_equations_on_scope": elimination,
                                "NAE_satisfying_words": nae,
                                "NAE_full_state_witness_hex": witnesses})
    source_class = dims.DC.classify(sizes, meetings)
    read, why = dims.predict(sizes, meetings)
    assert source_class == "in" and read == 2 * source["extra"]
    spelling = dims.DC.data(sizes, meetings)
    live = spelling[3]
    assert set(live) == set(source["u"]) | ({source["far"]} if source["extra"] else set())
    assert {tuple(sorted(row)) for row in spelling[4]} == set(combinations(sorted(source["u"]), 2))

    nae_log = []
    p, fate_p = library.grow(sizes, meetings, "parity", rounds=THROUGH)
    q, fate_q = library.grow(sizes, meetings, "nae", rounds=THROUGH, log=nae_log)
    cut_present = [v for v, a in enumerate(p.round_of) if a == 1]
    wanted = [v for v in cut_present if p.parents[v] == 2]
    near_end = len(old) + len(cut_present)
    first_stars = p.bits_of[:near_end]
    local = frontier(first_stars, wanted)
    assert set(p.fresh[v] for v in wanted) == {1}
    assert all(count == 1 for _, count in local["near_loose"])
    top = next(v for v, a in enumerate(p.round_of) if a == 2 and p.parents[v] == 3)
    top_q = next(v for v, a in enumerate(q.round_of) if a == 2 and q.parents[v] == 3)
    old_ports = p.bits_of[top][:3]
    assert old_ports == q.bits_of[top_q][:3] and p.fresh[top] == source["extra"] and q.fresh[top_q] == 1
    before_p = row_masks(p.bits_of[:near_end])
    before_q = q.bits_of[:near_end]
    p_words, p_constraint = parity_read(before_p, old_ports)
    with library._solver(q, near_end) as solver:
        q_words, q_certs = nae_read(solver, before_q, old_ports)
    assert p_words == (list(range(8)) if source["extra"] else [0, 3, 5, 6])
    assert q_words == list(range(8))
    cutoff_p = sum(a <= 2 for a in p.round_of)
    cutoff_q = sum(a <= 2 for a in q.round_of)
    parity_at_top, _ = parity_read(row_masks(p.bits_of[:cutoff_p]), p.bits_of[top])
    with library._solver(q, cutoff_q) as solver:
        nae_at_top, _ = nae_read(solver, q.bits_of[:cutoff_q], q.bits_of[top_q])
    top_gates = {"parity": canonical_relation(len(p.bits_of[top]), tuple(parity_at_top)),
                 "not-all-equal": canonical_relation(len(q.bits_of[top_q]), tuple(nae_at_top))}
    if not source["extra"]:
        canonical_relation(3, tuple(p_words))
        assert fate_p == "closed" and p.round_of[top] == max(p.round_of)
        p_fate_label = "finite closure at layer two"
    else:
        assert fate_p == "alive"
        p_fate_label = "unending dimension two by two separated live-path recurrences"
    assert fate_q == "alive" and not nae_log
    p_layers, q_layers = layer_summary(p), layer_summary(q)
    p_counts, q_counts = p.counts_by_round(), q.counts_by_round()
    if source["extra"]:
        assert p_layers == q_layers
        assert p_counts[1:] == [4, 3, 4, 6, 8, 10]
    else:
        assert p_counts[1:] == [3, 1] and q_counts[1:] == [3, 1, 1, 2, 3, 4]
    return {**source, "literal_stars": old, "physical_distinctions": original.nbits,
            "source_removed_knot_connectivity_BFS_from_exterior": complement_paths,
            "K_checks_source": projections, "arity_counts": dict(Counter(map(len, old))),
            "initial_live": live, "identified_class": source_class, "classified_parity_dimension": read,
            "classification_reason": why, "end_of_layer_one": local,
            "layer_two_near_parents": wanted, "layer_two_near_inputs": old_ports,
            "parity_input_words": p_words, "parity_input_supported_equations": p_constraint,
            "NAE_input_words": q_words, "NAE_input_full_stage_one_witness_hex": q_certs,
            "layer_two_born_top_at_its_own_support": top_gates,
            "parity_NAE_first_near_fresh_difference": [p.fresh[top], q.fresh[top_q]],
            "parity_fate": p_fate_label,
            "NAE_fate": "unending dimension two by the live-path recurrence",
            "parity_shapes": p_layers, "NAE_shapes": q_layers,
            "parity_birth_counts_including_source": p_counts,
            "NAE_birth_counts_including_source": q_counts,
            "literal_NAE_implied_observations": nae_log}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    relations, data = {}, {}
    for tag, source in fixtures():
        result = check_case(source, relations)
        data[tag] = result
        print(tag, result["physical_distinctions"], result["classified_parity_dimension"],
              result["parity_fate"], result["NAE_birth_counts_including_source"], flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"schema": 1, "fixture_design_sha256": sha256(DESIGN.read_bytes()).hexdigest(),
                                    "finite_replay_through": THROUGH, "source_cases": data,
                                    "anonymous_projection_gates": relations}, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
