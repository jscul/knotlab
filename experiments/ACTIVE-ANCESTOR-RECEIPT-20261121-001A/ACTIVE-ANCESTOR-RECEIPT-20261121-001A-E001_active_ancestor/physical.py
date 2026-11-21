"""Read the physical marks, paid cuts and unmarked source maps of B280."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import io
from itertools import combinations
import json
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLDER_SCOPE = "SHARED-DONOR-AND-SIGN-RESPONSE-20261121-001A"
OLDER = ROOT / "experiments" / OLDER_SCOPE / (OLDER_SCOPE + "-E001_shared_donor") / "physical.py"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "physical.json.gz"
CAP = 8192
LAWS = ("parity", "nae")
SEEDS = (20261121801, 20261121901)


@cache
def archived():
    spec = spec_from_file_location("b280_shared_donor_sources", OLDER)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Case:
    d: int
    control: str
    switch: str

    @property
    def key(self):
        return f"{self.d}_{self.control}_{self.switch}"

    @property
    def cut_sites(self):
        d = self.d
        near, far = (d // 4, 3 * d // 4), (5 * d // 4, 7 * d // 4)
        return {"none": (), "near": near, "far": far, "full": near + far}[self.switch]


def cases():
    return (
        Case(32, "main", "none"), Case(32, "main", "full"),
        Case(32, "sym", "none"), Case(32, "sym", "full"),
        Case(32, "main", "near"), Case(32, "main", "far"),
        Case(32, "one", "none"), Case(32, "one", "full"),
        Case(64, "main", "none"), Case(64, "main", "full"),
        Case(32, "ss", "none"), Case(32, "ss", "full"),
    )


def build(case):
    old = archived().joint().prior()
    p = old.Preparation([], {}, {})
    for tag in ("R", "S"):
        for tail, head, multiplicity in old.closed_frame(tag):
            p.candidate_pair(tail, head, multiplicity)
    p.candidate_pair("R.r1", "S.b2")
    p.candidate_pair("R.b2", "a")
    p.candidate_pair("b", "S.b2")
    p.passage(["a", *(f"p{i}" for i in range(1, case.d + 14)), "b"])
    length = 2 * case.d + 1
    for tag, tail_count in (("c", 3), ("u", 5)):
        for i in range(length):
            a, b = f"{tag}{i}", f"{tag}{(i + 1) % length}"
            p.candidate_pair(a, b, doubled=4)
            for _ in range(tail_count - 1):
                p.new_distinction(p.role_id[a], p.arc_witness[a, b])
    p.candidate_pair("a", "c0", doubled=3)
    if case.control != "one":
        p.candidate_pair(f"c{case.d}", "b")
    attachment = 3 * case.d // 2
    p.candidate_pair(f"c{attachment}", f"u{attachment}")
    if case.control != "sym":
        p.passage(["z0", "z1", "z2", "z3", "z0"])
        p.candidate_pair(f"c{attachment + 2}", "z0")
    if case.control == "ss":
        for i, site in enumerate((26, 27), 1):
            for role in (f"c{site}", f"c{site + 1}"):
                tip = f"w{i}"
                p.candidate_pair(role, tip)
                p.new_distinction(p.role_id[role], p.arc_witness[role, tip])
    for site in case.cut_sites:
        p.switch_witness_heads((f"c{site}", f"c{site + 1}"), (f"u{site}", f"u{site + 1}"))
    return p


@dataclass
class Reading:
    owners: dict
    ordinary: nx.Graph
    opens: dict
    candidate: nx.Graph
    pair_witnesses: dict
    roles: dict
    circuits: tuple
    circuit_arcs: tuple
    c_donors: set
    gates: dict
    clock_holdings: dict


def oriented_cycle(arcs, first):
    result = [first]
    while True:
        onward, = arcs.successors(result[-1])
        if onward == first:
            return result
        assert onward not in result
        result.append(onward)


def read_original(stars):
    old = archived().joint().prior()
    f = old.fixture()
    owners, ordinary, loose = f.incidence(stars)
    assert nx.is_connected(ordinary)
    _, candidate = f.witnessed_end(ordinary, loose)
    incidence = Counter(tuple(sorted(owner)) for owner in owners.values() if len(owner) == 2)
    regular, directed, split = nx.DiGraph(), nx.DiGraph(), nx.Graph()
    ordinary_witness, pair_witness = {}, {}
    c_donors, u_donors = set(), set()
    for k in sorted(set(ordinary) - loose.keys()):
        u, v = sorted(ordinary[k])
        assert u in loose and v in loose
        a, b = (incidence[tuple(sorted((k, p)))] for p in (u, v))
        pair = frozenset((u, v))
        assert pair not in pair_witness and len(stars[k]) == a + b
        pair_witness[pair] = k
        if (a, b) == (2, 2):
            split.add_edge(u, v, witness=k)
            continue
        if (b == 4 and a in (3, 5)) or (a == 4 and b in (3, 5)):
            tail, head, mark = (u, v, a) if b == 4 else (v, u, b)
            (c_donors if mark == 3 else u_donors).add(tail)
            directed.add_edge(tail, head, witness=k, tail_names=mark)
            continue
        tail, head, multiplicity = (u, v, b) if a == 1 else (v, u, a)
        assert min(a, b) == 1 and multiplicity in (2, 3)
        regular.add_edge(tail, head, multiplicity=multiplicity)
        ordinary_witness[tail, head] = k
    assert set(pair_witness) == set(map(frozenset, candidate.edges))
    assert all(ordinary[k].keys().isdisjoint(loose.keys()) for k in loose)
    assert c_donors.isdisjoint(u_donors) and c_donors | u_donors == set(directed)
    assert all(directed.in_degree(k) == directed.out_degree(k) == 1 for k in directed)

    physical = old.PhysicalReading(regular, ordinary_witness, loose)
    frames = old.decode_frames(physical)
    old_live = set(frames.values())
    a, = set(regular.successors(frames["R.b2"])) - old_live
    b, = set(regular.predecessors(frames["S.b2"])) - old_live
    c0, = set(regular.successors(a)) & c_donors
    assert regular[a][c0]["multiplicity"] == 3
    first = oriented_cycle(directed, c0)
    d = (len(first) - 1) // 2
    assert len(first) == 2 * d + 1 and len(c_donors) == len(u_donors) == len(first)
    link, = ((u, v) for u, v in regular.edges if u in directed and v in directed)
    first_link, second_link = sorted(link, key=lambda k: k not in first)
    phase = first.index(first_link)
    assert phase == 3 * d // 2 and second_link not in first
    second = oriented_cycle(directed, second_link)
    assert len(second) == len(first) and set(first).isdisjoint(second)
    second = second[-phase:] + second[:-phase]
    assert second[phase] == second_link
    middle = {}
    for i, (one, two) in enumerate(zip(first, second, strict=True)):
        assert (one in c_donors) != (two in c_donors)
        middle[f"c{i}"], middle[f"u{i}"] = (one, two) if one in c_donors else (two, one)
    assert frozenset((middle[f"c{phase}"], middle[f"u{phase}"])) == frozenset(link)

    reference = nx.shortest_path(regular.subgraph(set(regular) - old_live - set(directed)), a, b)
    assert len(reference) == d + 15
    roles = frames | middle | {"a": a, "b": b}
    roles.update({f"p{i}": k for i, k in enumerate(reference[1:-1], 1)})
    z_entry = [(u, v) for u, v in regular.edges if u in directed and v not in {a, b} and v not in directed]
    if z_entry:
        start, z0 = z_entry[0]
        assert len(z_entry) == 1 and start == middle[f"c{phase + 2}"]
        z = oriented_cycle(regular, z0)
        assert len(z) == 4
        roles.update({f"z{i}": k for i, k in enumerate(z)})

    gates = {}
    for w in sorted(set(split) - c_donors):
        u, v = sorted(split[w])
        assert w not in directed and set(split[w]) <= c_donors
        tail, head = (u, v) if directed.has_edge(u, v) else (v, u)
        assert directed[tail][head]["tail_names"] == 3
        tags = {k: label for label, k in middle.items()}
        site = int(tags[tail][1:])
        assert tags[tail] == f"c{site}" and tags[head] == f"c{site + 1}" and site in (26, 27)
        roles[f"w{site - 25}"] = w
        gates[str(site)] = {"donors": (tail, head, w),
                            "witnesses": (directed[tail][head]["witness"], split[w][tail]["witness"], split[w][head]["witness"])}
    assert set(roles.values()) == set(loose)
    assert all(len(row) == candidate.degree(k) for k, row in loose.items())
    clock = {str(k): value for k, value in old.stable_origins(stars, physical, frames).items()}
    arcs = tuple(sorted((u, v, data["tail_names"], data["witness"]) for u, v, data in directed.edges(data=True)))
    return Reading(owners, ordinary, loose, candidate, pair_witness, roles,
                   (tuple(first), tuple(second)), arcs, c_donors, gates, clock)


def certify_supports(stars, law, holders):
    old = archived().joint()
    f = old.prior().fixture()
    arities = Counter(len(stars[k]) for k in holders)
    with old.projector(stars, law) as project:
        for k in holders:
            assert project(stars[k]) == f.expected_words(law, len(stars[k]))
            f.canonical_relation(law, len(stars[k]))
    return {n: {"holders": count, "allowed_rows_per_holder": old.prior().canonical_row_count(law, n)}
            for n, count in sorted(arities.items())}


def literal_step(stars, law, age):
    old = archived().joint()
    f = old.prior().fixture()
    owners, ordinary, loose = f.incidence(stars)
    blocks, candidate = f.witnessed_end(ordinary, loose)
    multiple = f.multi_groups(blocks, candidate)
    uses = Counter(k for row in multiple for k in row)
    w_counts = Counter(tuple(sorted(row)) for b in blocks for row in combinations(b, 2))
    turn = f.step(f.from_stars(stars), law, max_births=CAP)
    assert turn.status == "extend" and not turn.implied and 1 < len(turn.parents) <= 1024
    status, births, physical_multi = f.literal_turn(stars, law)
    assert status == "extend" and multiple == physical_multi
    paid = {p: [] for p in loose}
    used_fresh = set()
    rows = []
    with old.projector(stars, law) as project:
        for b, demand in zip(births, turn.demand, strict=True):
            for parent, name in zip(b.parents, b.inputs, strict=True):
                assert owners[name] == [parent]
                paid[parent].append(name)
            assert b.fresh and all(x not in owners and x not in used_fresh for x in b.fresh)
            used_fresh.update(b.fresh)
            inputs = project(b.inputs)
            assert inputs == tuple(range(1 << len(b.inputs)))
            rows.append({"holder": b.knot, "parents": b.parents, "consumed_names": b.inputs,
                         "fresh_names": b.fresh, "demand": demand, "grant": len(b.fresh),
                         "input_projection": inputs})
    assert {k: sorted(row) for k, row in paid.items()} == loose
    evolved = stars + tuple(b.support for b in births)
    _, _, new_loose = f.incidence(evolved)
    assert new_loose == {b.knot: list(b.fresh) for b in births}
    cut = {
        "age": age, "status": status, "births": rows,
        "payment": {k: {"names": loose[k], "actual": paid[k], "multi": uses[k], "unary": len(loose[k]) - uses[k]}
                    for k in loose},
        "unheld_groups_of_at_least_three": [r for r in multiple if len(r) > 2],
        "unique_witness_per_candidate": max(w_counts.values()) == 1,
        "local_newborn_projection": certify_supports(evolved, law, range(len(stars), len(evolved))),
        "old_assignments_extend": True,
    }
    return evolved, cut


def spine_topology(reading, licenses, actual_two_cuts):
    """Read the marked and mark-forgetting return from actual paid births."""
    label_of = {k: role for role, k in reading.roles.items()}
    paid_parents = {b["holder"]: b["parents"] for b in licenses.values()}
    arcs_by_pair = {(a, b): (mult, w) for a, b, mult, w in reading.circuit_arcs}
    two_rows = {frozenset(row["parents"]): row for row in actual_two_cuts["births"]}
    original_steps = {}
    for a, b, multiplicity, witness in reading.circuit_arcs:
        birth = licenses[frozenset((a, b))]
        assert set(birth["parents"]).issuperset((a, b))
        original_steps[a, b] = {
            "tail": label_of[a], "head": label_of[b], "tail_multiplicity": multiplicity,
            "witness": witness, "is_c_step": a in reading.c_donors and b in reading.c_donors,
            "paid_cut_one_holder": birth["holder"], "paid_cut_one_parents": birth["parents"],
            "paid_cut_one_grant": birth["grant"], "paid_cut_one_inputs": birth["consumed_names"],
        }
    words = []
    for orbit in reading.circuits:
        windows = orbit + orbit[:2]
        for a, b, c in zip(windows, windows[1:], windows[2:]):
            x, y = original_steps[a, b], original_steps[b, c]
            l, r = x["paid_cut_one_holder"], y["paid_cut_one_holder"]
            assert set(paid_parents[l]) & set(paid_parents[r]) == {b}
            hit = two_rows[frozenset((l, r))]
            words.append({"original_word": (label_of[a], label_of[b], label_of[c]),
                          "paid_cut_two_holder": hit["holder"], "paid_cut_two_parents": hit["parents"],
                          "paid_cut_two_inputs": hit["consumed_names"], "paid_cut_two_grant": hit["grant"],
                          "c_only": x["is_c_step"] and y["is_c_step"],
                          "no_extra_original": len(x["paid_cut_one_parents"]) == len(y["paid_cut_one_parents"]) == 2})
    assert all((a, b) in arcs_by_pair for a, b in original_steps)

    def components(exclude_extra):
        graph = nx.DiGraph()
        graph.add_nodes_from(reading.c_donors)
        graph.add_edges_from((a, b) for (a, b), data in original_steps.items()
                             if data["is_c_step"] and (not exclude_extra or len(data["paid_cut_one_parents"]) == 2))
        result = []
        for component in nx.weakly_connected_components(graph):
            subgraph = graph.subgraph(component)
            closed = all(subgraph.in_degree(k) == subgraph.out_degree(k) == 1 for k in component)
            if closed:
                start = min(component, key=lambda k: int(label_of[k][1:]))
                order = oriented_cycle(subgraph, start)
            else:
                start, = (k for k in component if not subgraph.in_degree(k))
                ends = tuple(k for k in component if not subgraph.out_degree(k))
                end, = ends
                order = nx.shortest_path(subgraph, start, end)
            assert set(order) == component
            result.append({"closed_return": closed, "roles": [label_of[k] for k in order]})
        result.sort(key=lambda r: tuple(int(role[1:]) for role in r["roles"]))
        final_size = None if any(x["closed_return"] for x in result) else max(len(x["roles"]) for x in result)
        return {"components": result, "finite_ceiling": final_size, "arbitrarily_long": final_size is None}

    return {
        "directed_original_witnesses": sorted(original_steps.values(), key=lambda row: (row["tail"], row["head"])),
        "actual_cut_two_windows": words, "c_family": components(False), "c_family_without_extra": components(True),
        "mark_forgetting_cycles": [[label_of[k] for k in orbit] for orbit in reading.circuits],
    }


def gate_history(reading, licenses, two, fore_before_two, fore_after_two):
    if not reading.gates:
        return {}
    label_of = {k: role for role, k in reading.roles.items()}
    payer = reading.roles["c27"]
    left, right = (licenses[frozenset(reading.gates[site]["donors"][:2])] for site in ("26", "27"))
    assert set(left["parents"]) & set(right["parents"]) == {payer}
    result = []
    for site, row in (("26", left), ("27", right)):
        donors = reading.gates[site]["donors"]
        assert set(row["parents"]) == set(donors)
        result.append(row | {
            "site": site, "original_donor_roles": [label_of[k] for k in row["parents"]],
            "original_witnesses": reading.gates[site]["witnesses"],
            "shared_donor_charge": row["consumed_names"][row["parents"].index(payer)],
        })
    assert result[0]["shared_donor_charge"] != result[1]["shared_donor_charge"]
    born_ids = {row["holder"] for row in result}
    through, = (row for row in two["births"] if born_ids <= set(row["parents"]))
    assert set(through["parents"]) == born_ids
    following = [g for g in fore_after_two["proposed_multiple_groups"] if through["holder"] in g]
    assert len(following) == through["demand"] == through["grant"]
    return {
        "shared_donor": payer, "shared_donor_original_loose": reading.opens[payer], "crossings": result,
        "through": through | {"next_demand_parent_sets": following},
        "whole_maximal_sets_around_the_pair": [row for row in fore_before_two["maximal_candidate_sets"]
                                               if born_ids <= set(row["members"])],
    }


def test_relabelled(stars, original, reading, cuts, law, seed):
    f = archived().joint().prior().fixture()
    renamed, to_original = f.rename(stars, seed)
    orig, parents, _, depth = f.peel(renamed, law)
    assert depth == 2
    ordered = sorted(orig)
    mapping = [to_original[k] for k in ordered]
    assert set(mapping) == set(range(len(original)))
    older = read_original(tuple(renamed[k] for k in ordered))
    assert {label: mapping[k] for label, k in older.roles.items()} == reading.roles
    assert {mapping[k] for k in older.c_donors} == reading.c_donors
    assert {tuple(mapping[k] for k in orbit) for orbit in older.circuits} == set(reading.circuits)
    assert {(mapping[a], mapping[b], m, mapping[w]) for a, b, m, w in older.circuit_arcs} == set(reading.circuit_arcs)
    assert {(frozenset(mapping[k] for k in pair), mapping[w]) for pair, w in older.pair_witnesses.items()} == (
        set(reading.pair_witnesses.items())
    )
    assert older.gates.keys() == reading.gates.keys()
    for site, gate in older.gates.items():
        assert {key: tuple(mapping[k] for k in row) for key, row in gate.items()} == reading.gates[site]
    actual = {r["holder"]: frozenset(r["parents"]) for cut in cuts for r in cut["births"]}
    assert {to_original[k]: frozenset(to_original[j] for j in row) for k, row in parents.items()} == actual
    return {"seed": seed, "depth": depth, "true_parent_lists_recovered": len(actual),
            "source_indices_in_recoding": ordered, "recoded_to_original_holder": to_original,
            "recoded_full_stars": renamed}


def test_sidecar(stars, reading):
    sidecar = {role: k for role, k in reading.roles.items()}
    changed = {
        ({"c": "u", "u": "c"}[role[0]] + role[1:] if role[0] in "cu" else role): k
        for role, k in sidecar.items()
    }
    assert sidecar != changed
    prepared = {"full_holdings": stars, "nominal_role_map": changed}
    decoded = read_original(prepared["full_holdings"])
    assert decoded.roles == reading.roles and decoded.c_donors == reading.c_donors
    assert decoded.circuit_arcs == reading.circuit_arcs
    return {"swapped_roles": sum(sidecar[k] != changed[k] for k in sidecar),
            "role_read_matches_original": True, "swapped_sidecar": changed}


def single_deletions(reading):
    label_of = {k: role for role, k in reading.roles.items()}
    graph = reading.candidate.copy()
    profile = []
    for a, b in list(graph.edges):
        graph.remove_edge(a, b)
        sizes = tuple(sorted(map(len, nx.connected_components(graph))))
        graph.add_edge(a, b)
        pair = tuple(sorted((label_of[a], label_of[b])))
        profile.append({"candidate_pair": pair, "component_sizes": sizes})
    assert len(profile) == len(reading.candidate.edges)
    counts = sorted(Counter(x["component_sizes"] for x in profile).items())
    return {"all_single_deletions": sorted(profile, key=lambda row: row["candidate_pair"]),
            "component_size_multiset": counts}


def run_case(case, seeds):
    p = build(case)
    stars = p.immutable()
    reading = read_original(stars)
    assert reading.roles == {role: p.role_id[role] for role in reading.roles}
    assert len(reading.c_donors) == 2 * case.d + 1
    assert len(reading.gates) == (2 if case.control == "ss" else 0)
    assert all(pair_witness == p.arc_witness[pair] for pair, pair_witness in
               [((tail, head), reading.pair_witnesses[frozenset((p.role_id[tail], p.role_id[head]))])
                for tail, head in p.arc_witness])
    label_of = {h: role for role, h in reading.roles.items()}
    middle_nodes = {k for label, k in reading.roles.items() if not label.startswith(("R.", "S."))}
    routes = tuple(sorted(tuple(label_of[k] for k in route) for route in nx.all_shortest_paths(
        reading.candidate.subgraph(middle_nodes), reading.roles["a"], reading.roles["b"]
    )))
    assert len(routes) == 1 and len(routes[0]) - 1 == (case.d + 14 if case.control == "one" else case.d + 2)

    outcomes = {}
    for law in LAWS:
        source_projection = certify_supports(stars, law, range(len(stars)))
        after_one, cut_one = literal_step(stars, law, 1)
        after_two, cut_two = literal_step(after_one, law, 2)
        covers = {}
        for row in cut_one["births"]:
            for pair in combinations(row["parents"], 2):
                key = frozenset(pair)
                assert key not in covers
                covers[key] = row
        assert set(covers) == set(reading.pair_witnesses)
        fore_one = archived().ordinary_forecast(after_one, law)
        fore_two = archived().ordinary_forecast(after_two, law)
        assert fore_one["status"] == fore_two["status"] == "extend"
        assert (len(cut_one["unheld_groups_of_at_least_three"]) == len(reading.gates)
                and not cut_two["unheld_groups_of_at_least_three"])
        cuts = (cut_one, cut_two)
        outcomes[law] = {
            "source_projections": source_projection, "cuts": cuts,
            "gate_history": gate_history(reading, covers, cut_two, fore_one, fore_two),
            "circuit_family": spine_topology(reading, covers, cut_two),
            "forecast_at_cut_two": fore_two,
            "recodings": [test_relabelled(after_two, stars, reading, cuts, law, seed) for seed in seeds],
        }
    assert outcomes["parity"]["gate_history"] == outcomes["nae"]["gate_history"]
    assert outcomes["parity"]["circuit_family"] == outcomes["nae"]["circuit_family"]
    for left, right in zip(outcomes["parity"]["cuts"], outcomes["nae"]["cuts"], strict=True):
        assert left["births"] == right["births"]
    clock_live = {k for name, k in reading.roles.items() if name.startswith(("R.", "S."))}
    return {
        "case": case.key, "d": case.d, "control": case.control, "switch": case.switch, "switched_sites": case.cut_sites,
        "original_stars": stars, "original_distinction_count": len(reading.owners), "live_roles": reading.roles,
        "loose_names": {label_of[k]: row for k, row in reading.opens.items()},
        "candidate_pairs": sorted(tuple(sorted((label_of[a], label_of[b]))) for a, b in reading.candidate.edges),
        "candidate_pair_witnesses": sorted((tuple(sorted(label_of[k] for k in pair)), w)
                                           for pair, w in reading.pair_witnesses.items()),
        "circuit_arcs": [(label_of[a], label_of[b], mult, 4, w) for a, b, mult, w in reading.circuit_arcs],
        "shortest_middle_candidate_routes": routes, "clock_holdings": reading.clock_holdings,
        "clock_prefix": archived().joint().clock_prefix(outcomes["parity"]["cuts"], clock_live),
        "unmarked_single_deletion_census": single_deletions(reading),
        "sidecar_swap": test_sidecar(stars, reading), "laws": outcomes,
    }


def symmetric_transport(first, second):
    a, b = (read_original(row["original_stars"]) for row in (first, second))
    src_special = set().union(*map(set, a.circuits))
    transport = {k: b.roles[role] for role, k in a.roles.items() if k not in src_special}
    transport.update({i: j for x, y in zip(a.circuits, b.circuits, strict=True) for i, j in zip(x, y, strict=True)})
    assert set(transport) == set(a.opens) and set(transport.values()) == set(b.opens)
    assert all(len(a.opens[k]) == len(b.opens[transport[k]]) for k in a.opens)
    assert {frozenset(transport[k] for k in pair) for pair in a.pair_witnesses} == b.pair_witnesses.keys()
    transport.update({w: b.pair_witnesses[frozenset(transport[k] for k in pair)]
                      for pair, w in a.pair_witnesses.items()})
    assert set(transport) == set(a.ordinary) and set(transport.values()) == set(b.ordinary)
    assert {frozenset(transport[k] for k in edge) for edge in a.ordinary.edges} == set(map(frozenset, b.ordinary.edges))
    native = {}
    for law in LAWS:
        current = dict(transport)
        for x, y in zip(first["laws"][law]["cuts"], second["laws"][law]["cuts"], strict=True):
            target = {frozenset(row["parents"]): row for row in y["births"]}
            assert len(target) == len(y["births"]) == len(x["births"])
            for row in x["births"]:
                hit = target[frozenset(current[k] for k in row["parents"])]
                assert (row["grant"], row["demand"]) == (hit["grant"], hit["demand"])
                current[row["holder"]] = hit["holder"]
            assert len(set(current.values())) == len(current)
        native[law] = current
    return {"original_holder_transport": transport, "paid_prefix_transport": native}


def match_checks(rows):
    keyed = {r["case"]: r for r in rows}
    base = keyed["32_main_none"]
    assert all(row["clock_holdings"] == base["clock_holdings"] and row["clock_prefix"] == base["clock_prefix"]
               for row in rows)
    with gzip.open(archived().joint().PRIOR_RECEIPT, "rt", encoding="utf-8") as source:
        archive = next(row for row in json.load(source)["cases"] if row["variant"] == "active" and row["d"] == 32)
    assert {k: [list(star), list(loose)] for k, (star, loose) in base["clock_holdings"].items()} == (
        archive["common_original_holdings"]
    )
    matched = {}
    for row in rows:
        if row["switch"] == "none":
            continue
        other = keyed[f"{row['d']}_{row['control']}_none"]
        assert row["live_roles"] == other["live_roles"] and row["loose_names"] == other["loose_names"]
        pre = {frozenset(pair): w for pair, w in other["candidate_pair_witnesses"]}
        post = {frozenset(pair): w for pair, w in row["candidate_pair_witnesses"]}
        left, right = other["original_stars"], row["original_stars"]
        changed = []
        for site in row["switched_sites"]:
            old_c = ("c" + str(site), "c" + str(site + 1))
            old_u = ("u" + str(site), "u" + str(site + 1))
            for (tail, head), (_, other_head) in [(old_c, old_u), (old_u, old_c)]:
                w = pre[frozenset((tail, head))]
                assert w == post[frozenset((tail, other_head))]
                assert set(left[w]) & set(left[row["live_roles"][tail]]) == set(right[w]) & set(right[row["live_roles"][tail]])
                removed = set(left[w]) - set(right[w])
                gained = set(right[w]) - set(left[w])
                assert removed == set(left[w]) & set(left[row["live_roles"][head]]) and len(removed) == 4
                assert gained == set(right[w]) & set(right[row["live_roles"][other_head]]) and len(gained) == 4
                changed.append({"witness": w, "removed_head_names": sorted(removed), "new_head_names": sorted(gained)})
        assert {i for i, (x, y) in enumerate(zip(left, right, strict=True)) if x != y} == {r["witness"] for r in changed}
        assert tuple(map(len, left)) == tuple(map(len, right))
        matched[row["case"]] = {"matched_live_holders": len(row["live_roles"]), "spent_witness_changes": changed}
    for d in (32, 64):
        left, right = [keyed[f"{d}_main_{mode}"]["unmarked_single_deletion_census"]["component_size_multiset"]
                       for mode in ("none", "full")]
        assert left != right
    sym_a, sym_b = (keyed[f"32_sym_{mode}"] for mode in ("none", "full"))
    assert sym_a["unmarked_single_deletion_census"]["component_size_multiset"] == (
        sym_b["unmarked_single_deletion_census"]["component_size_multiset"]
    )
    return {
        "matched_original_clocks": len(base["clock_holdings"]),
        "matched_clock_only_birth_counts": [len(row) for row in base["clock_prefix"]],
        "literal_witness_swaps": matched,
        "unmarked_symmetric_transport": symmetric_transport(sym_a, sym_b),
    }


def input_hashes():
    manifest = HERE / "contract.json"
    contract = json.loads(manifest.read_bytes())
    preregistration = ROOT / contract["preregistration"]
    frozen = {preregistration.with_name(name): digest for name, digest in contract["scientific_design_sha256"].items()}
    frozen[ROOT / contract["advisor_receipt"]] = contract["advisor_sha256"]
    assert all(sha256(path.read_bytes()).hexdigest() == digest for path, digest in frozen.items())
    old = archived().joint()
    source = [Path(__file__).resolve(), OLDER, archived().JOINT, old.PRIOR, old.PRIOR_RECEIPT,
              old.prior().FIXTURES, old.prior().END_OPERATOR, manifest, preregistration, *frozen]
    return {str(f.relative_to(ROOT)): sha256(f.read_bytes()).hexdigest() for f in source}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    hashes = input_hashes()
    rows = [run_case(case, tuple(seed + i for seed in SEEDS)) for i, case in enumerate(cases())]
    receipt = {"schema": "b280-physical-v1", "cases": rows, "matches": match_checks(rows),
               "bound_source_hashes": hashes, "literal_cut_cap": CAP}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as out, gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as gzipped:
        with io.TextIOWrapper(gzipped, encoding="utf-8", newline="\n") as payload:
            json.dump(receipt, payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            payload.write("\n")
    print(sha256(args.output.read_bytes()).hexdigest(), args.output)


if __name__ == "__main__":
    main()
