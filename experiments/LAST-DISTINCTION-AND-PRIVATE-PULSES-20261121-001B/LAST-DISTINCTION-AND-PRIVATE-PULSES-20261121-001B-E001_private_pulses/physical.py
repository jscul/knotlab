"""Literal physical sources, two ordinary cuts and the occupied witness projection."""

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
PRIOR_SCOPE = "TICK-BIRTHS-AND-SCARCITY-20261121-001A"
PRIOR = ROOT / "experiments" / PRIOR_SCOPE / (PRIOR_SCOPE + "-E001_tick_births") / "physical.py"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "physical.json.gz"
LAWS = ("parity", "nae")
CAP = 8192
SEEDS = (20261121501, 20261121601)
P_SITES = (1, 5, 9, 13)
Q_SITES = (3, 7)
NEAR = (8, 10)
REMOTE = (15, 17)


@cache
def previous():
    spec = spec_from_file_location("b283_previous_paid_sources", PRIOR)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@cache
def fixtures():
    return previous().archive().joint().prior().fixture()


@dataclass(frozen=True)
class Case:
    key: str
    switches: tuple = ()
    retag: bool = False
    break_sender: bool = False
    erase_origin: bool = False
    shortage: bool = False


def cases():
    return (
        Case("intact"), Case("near", NEAR), Case("remote", REMOTE),
        Case("near_retag", NEAR, retag=True), Case("near_remote", NEAR + REMOTE),
        Case("intact_s_break", break_sender=True), Case("near_s_break", NEAR, break_sender=True),
        Case("o_erased", erase_origin=True), Case("p_shortage", shortage=True),
    )


def original_role(tag, i):
    if i in P_SITES:
        return "p" if tag == "c" else "h"
    if i in Q_SITES:
        return "q" if tag == "c" else "k"
    return f"{tag}{i}"


def local_count(tag, i, leaving):
    if i in P_SITES:
        values = (3 if tag == "c" else 5, 6, 7, 8, 9, 10, 11, 12)
        return values[2 * P_SITES.index(i) + int(leaving)]
    if i in Q_SITES:
        values = (3 if tag == "c" else 5, 6, 7, 8)
        return values[2 * Q_SITES.index(i) + int(leaving)]
    return (3 if tag == "c" else 5) if leaving else 4


def prepare(case):
    old = previous()
    p = old.archive().joint().prior().Preparation([], {}, {})
    retag_incidence = []
    for tag in ("c", "u"):
        for i in range(20):
            j = (i + 1) % 20
            a, b = original_role(tag, i), original_role(tag, j)
            counts = local_count(tag, i, True), local_count(tag, j, False)
            old.add_pair(p, (a, b), counts)
            if tag == "u":
                w = p.arc_witness[a, b]
                if counts[0] == 5:
                    retag_incidence.append((p.role_id[a], w))
                if j in (1, 3):
                    assert counts[1] == 5
                    retag_incidence.append((p.role_id[b], w))
    root = ("O", "O1", "O2", "O3")
    for a, b in zip(root, root[1:] + root[:1], strict=True):
        old.add_pair(p, (a, b), (1, 2))
    for tag, tail in (("S", 2), ("V", 6)):
        for i in range(7):
            old.add_pair(p, (f"{tag}{i}", f"{tag}{(i + 1) % 7}"), (tail, 4))
    for pair, counts in (
            (("H", "c0"), (1, 11)), (("H", "S0"), (1, 13)),
            (("c18", "u18"), (1, 2)), (("O1", "V0"), (1, 15))):
        old.add_pair(p, pair, counts)
    start = p.new_name
    old.add_pair(p, ("O", "H"), (1, 17))

    edits = []
    for i in case.switches:
        j = (i + 1) % 20
        pairs = [(original_role(tag, i), original_role(tag, j)) for tag in ("c", "u")]
        n = local_count("c", j, False)
        assert local_count("u", j, False) == n
        edits.append({"kind": "circuit_head_exchange", "site": i, "size": n,
                      "changes": old.exchange(p, *pairs, n)})
    if case.break_sender:
        edits.append({"kind": "private_head_exchange", "size": 4,
                      "changes": old.exchange(p, ("S3", "S4"), ("V3", "V4"), 4)})
    if case.retag:
        for donor, witness in retag_incidence:
            names = sorted(set(p.stars[donor]) & set(p.stars[witness]))
            assert len(names) == 5
            removed = names[-2:]
            for k in (donor, witness):
                p.stars[k] = [d for d in p.stars[k] if d not in removed]
            edits.append({"kind": "retag", "donor": donor, "witness": witness, "removed_names": removed})
    if case.erase_origin:
        names = (start + 1, p.new_name - 1)
        donor = p.role_id["O"], p.role_id["H"]
        w = p.arc_witness.pop(("O", "H"))
        assert w == len(p.stars) - 1
        p.role_id.pop("witness O → H")
        shared = set(p.stars.pop())
        for k, d in zip(donor, names, strict=True):
            assert d in p.stars[k] and d not in shared
            p.stars[k] = [b for b in p.stars[k] if b not in shared and b != d]
        edits.append({"kind": "erase_origin_pair", "witness": w, "donors": donor,
                      "removed_shared": sorted(shared), "removed_private": names})
    if case.shortage:
        k = p.role_id["p"]
        _, _, loose = fixtures().incidence(p.immutable())
        assert len(loose[k]) == 8
        d = loose[k][-1]
        p.stars[k].remove(d)
        edits.append({"kind": "private_shortage", "donor": k, "removed_names": [d]})
    return p, edits


@dataclass
class Reading:
    owners: dict
    ordinary: nx.Graph
    opens: dict
    candidate: nx.Graph
    witnesses: dict
    port: dict
    r_order: dict
    marks: set
    anchors: dict
    sender: tuple
    reserve: tuple
    o_pair: bool


def read_source(stars):
    f = fixtures()
    owned, whole, loose = f.incidence(stars)
    _, candidate = f.witnessed_end(whole, loose)
    witnesses = {}
    ports = {k: {} for k in loose}
    for w in sorted(set(whole) - loose.keys()):
        a, b = sorted(whole[w])
        assert a in loose and b in loose
        left, right = [sorted(set(stars[k]) & set(stars[w])) for k in (a, b)]
        assert left and right and len(left) + len(right) == len(stars[w])
        pair = frozenset((a, b))
        assert pair not in witnesses
        witnesses[pair] = w
        for u, v, x, y in ((a, b, left, right), (b, a, right, left)):
            ports[u][v] = {
                "peer": v, "witness": w, "local_names": x, "peer_names": y,
                "local_count": len(x), "peer_count": len(y), "circuit": min(len(x), len(y)) >= 3,
            }
    assert set(witnesses) == set(map(frozenset, candidate.edges))
    assert all(set(whole[k]).isdisjoint(loose.keys()) for k in loose)

    def signed(x, y):
        return [(k, j) for k, row in ports.items() for j, r in row.items()
                if (r["local_count"], r["peer_count"]) == (x, y)]

    (h, c0), = signed(1, 11)
    (same_h, s0), = signed(1, 13)
    assert same_h == h
    (o1, v0), = signed(1, 15)
    o, = (k for k, j in signed(1, 2) if j == o1)
    o2, = (j for k, j in signed(1, 2) if k == o1)
    o3, = (j for k, j in signed(1, 2) if k == o2)
    assert (o3, o) in signed(1, 2)
    origin = signed(1, 17)
    assert origin in ([], [(o, h)])
    circuit = nx.Graph()
    for k, row in ports.items():
        circuit.add_edges_from((k, j) for j, d in row.items() if d["circuit"])
    (c18, u18), = ((a, b) for a, b in signed(1, 2) if a in circuit and b in circuit)
    scope = set().union(*(nx.node_connected_component(circuit, k) for k in (c0, c18, u18)))
    order = {k: tuple(sorted(circuit[k], key=lambda j: ports[k][j]["local_count"])) for k in sorted(scope)}
    assert all(len(row) >= 2 and len({ports[k][j]["local_count"] for j in row}) == len(row)
               for k, row in order.items())
    p, = (k for k in order[c0] if len(order[k]) == 8)
    other_p, = (k for k in order if k != p and len(order[k]) == 8)
    walk = [c0, p]
    for _ in range(7):
        walk.append(previous().successor(order, *walk[-2:])[1])
    q = next(k for k in walk[2:] if len(order[k]) == 4)
    k, = (v for v in order if v != q and len(order[v]) == 4)
    marks = {k for k, row in ports.items() if any(r["circuit"] and r["local_count"] == 3 for r in row.values())}
    s_next = dict(signed(2, 4))
    v_next = dict(signed(6, 4))

    def prefix(start, arrows):
        result = [start]
        for _ in range(3):
            result.append(arrows[result[-1]])
        return result

    sender = prefix(s0, s_next)
    reserve = prefix(v0, v_next)
    ends = s_next[sender[-1]], v_next[reserve[-1]]
    s4, = (v for v in ends if v in s_next)
    v4, = (v for v in ends if v in v_next)
    sender.extend((s4, s_next[s4], s_next[s_next[s4]]))
    reserve.extend((v4, v_next[v4], v_next[v_next[v4]]))
    assert s_next[sender[-1]] == s0 and v_next[reserve[-1]] == v0
    anchors = dict(O=o, O1=o1, O2=o2, O3=o3, H=h, c0=c0, p=p, h=other_p, q=q, k=k, c18=c18, u18=u18,
                   c2=walk[2], c4=walk[4], c6=walk[6], c8=walk[8])
    anchors.update({f"S{i}": k for i, k in enumerate(sender)})
    anchors.update({f"V{i}": k for i, k in enumerate(reserve)})
    assert len(set(anchors.values())) == len(anchors)
    return Reading(owned, whole, loose, candidate, witnesses, ports, order, marks,
                   anchors, tuple(sender), tuple(reserve), bool(origin))


def literal_cut(stars, law, age):
    """Plan on each connected component, then commit only a funded whole cut."""
    f = fixtures()
    owned, whole, loose = f.incidence(stars)
    components = sorted(tuple(sorted(part)) for part in nx.connected_components(whole))
    original = [tuple(stars[k] for k in part) for part in components]
    forecasts = [previous().archive().ordinary_forecast(block, law) for block in original]
    shortages = [(part[k], count) for part, plan in zip(components, forecasts, strict=True)
                 for k, count in plan["shortages"]]
    result = {"age": age, "status": "stall" if shortages else "extend", "shortages": shortages,
              "births": [], "components": [{"local_to_whole": part, "forecast": plan}
                                            for part, plan in zip(components, forecasts, strict=True)]}
    if shortages:
        assert any(plan["status"] == "stall" for plan in forecasts)
        return stars, result
    assert all(plan["status"] == "extend" and not plan["implied"] and len(plan["funded_births"]) >= 2
               for plan in forecasts)
    assert sum(len(plan["funded_births"]) for plan in forecasts) <= CAP

    serial = max(owned) + 1
    paid = {k: [] for k in loose}
    growing = []
    with previous().archive().joint().projector(stars, law) as project:
        for part, block, plan in zip(components, original, forecasts, strict=True):
            assert len(plan["funded_births"]) <= 1024
            status, births, groups = f.literal_turn(block, law)
            assert status == "extend" and groups == plan["proposed_multiple_groups"]
            for b, (p, demand, count) in zip(births, plan["funded_births"], strict=True):
                assert p == b.parents and count == len(b.fresh) and count >= 1 and len(p) == 2
                parents, names = zip(*sorted((part[k], d) for k, d in zip(p, b.inputs, strict=True)), strict=True)
                for k, d in zip(parents, names, strict=True):
                    assert owned[d] == [k]
                    paid[k].append(d)
                # Choose one whole-cut name supply, including for components
                # whose local allocator would reuse another component's name.
                fresh = tuple(range(serial, serial + count))
                serial += count
                whole_id = len(stars) + len(growing)
                projected = project(names)
                assert projected == tuple(range(1 << len(names)))
                growing.append(names + fresh)
                result["births"].append({"holder": whole_id, "parents": parents, "consumed_names": names,
                                         "fresh_names": fresh, "demand": demand, "grant": count,
                                         "input_projection": projected})
    assert {k: sorted(bits) for k, bits in paid.items()} == loose
    grown = stars + tuple(growing)
    assert f.incidence(grown)[2] == {b["holder"]: list(b["fresh_names"]) for b in result["births"]}
    result["paid_names_by_donor"] = paid
    result["old_assignments_extend"] = True
    result["newborn_local_knot_checks"] = {
        n: {"holders": count, "allowed_rows": previous().relation_size(law, n), "K1_K2_K3": True}
        for n, count in sorted(Counter(map(len, growing)).items())
    }
    return grown, result


def retained_words(reading, cuts):
    if cuts[0]["status"] != "extend":
        return {}
    one, two = ({frozenset(b["parents"]): b for b in c["births"]} for c in cuts)
    assert one.keys() == reading.witnesses.keys()
    assert len(two) == sum(len(row) * (len(row) - 1) // 2 for row in reading.port.values())
    a = reading.anchors

    def pair(x, y):
        return one[frozenset((x, y))]

    def triple(x, y, z):
        return two[frozenset((pair(x, y)["holder"], pair(y, z)["holder"]))]

    chosen = previous().successor(reading.r_order, a["q"], a["c8"])[1]
    assert chosen in (a["p"], a["h"])
    source = {
        "short_private_pair": pair(a["S0"], a["S1"]),
        "short_private_triple": triple(a["S0"], a["S1"], a["S2"]),
        "H_receiver_arm_root": triple(a["H"], a["c0"], a["p"]),
        "H_two_armed_root": triple(a["c0"], a["H"], a["S0"]),
        "q_to_c8": pair(a["q"], a["c8"]),
        "c8_to_selected": pair(a["c8"], chosen),
        "q_c8_selected": triple(a["q"], a["c8"], chosen),
    }
    if reading.o_pair:
        source.update(O_to_H=pair(a["O"], a["H"]),
                      O_H_c0=triple(a["O"], a["H"], a["c0"]),
                      O_H_S0=triple(a["O"], a["H"], a["S0"]))
    return {"anchors": source, "selected_occupied_tip_peer": chosen,
            "occupied_tip_original_witness": reading.witnesses[frozenset((a["c8"], chosen))]}


def projected_names(stars, scope, law):
    with previous().archive().joint().projector(stars, law) as project:
        return project(scope)


def check_recoding(final, source, original, cuts, law, seed):
    f = fixtures()
    renamed, to_original = f.rename(final, seed)
    _, ordinary, _ = f.incidence(renamed)
    recovered_source = []
    actual = {}
    observed_depths = []
    for component in nx.connected_components(ordinary):
        indices = sorted(component)
        older, parents, _, depth = f.peel(tuple(renamed[k] for k in indices), law)
        observed_depths.append(depth)
        recovered_source.extend(indices[k] for k in older)
        actual.update({to_original[indices[k]]: frozenset(to_original[indices[i]] for i in row)
                       for k, row in parents.items()})
    expected_depth = sum(c["status"] == "extend" for c in cuts)
    assert set(observed_depths) == {expected_depth}
    recovered_source.sort()
    to_old = [to_original[k] for k in recovered_source]
    assert set(to_old) == set(range(len(source)))
    read = read_source(tuple(renamed[k] for k in recovered_source))
    assert {role: to_old[k] for role, k in read.anchors.items()} == original.anchors
    assert {to_old[k] for k in read.marks} == original.marks
    assert {to_old[k]: tuple(to_old[j] for j in row) for k, row in read.r_order.items()} == original.r_order
    assert {frozenset(to_old[k] for k in pair): to_old[w] for pair, w in read.witnesses.items()} == original.witnesses
    for donor, other_port in read.port.items():
        for peer, row in other_port.items():
            orig = original.port[to_old[donor]][to_old[peer]]
            assert (row["local_count"], row["peer_count"]) == (orig["local_count"], orig["peer_count"])
    real = {b["holder"]: frozenset(b["parents"]) for c in cuts for b in c["births"]}
    assert real == actual
    return {"seed": seed, "recoded_full_stars": renamed, "recoded_to_original_holder": to_original,
            "source_indices_in_recoding": recovered_source, "component_depths": sorted(observed_depths),
            "actual_parent_lists_recovered": len(actual)}


def walk_bound(order, reading):
    seed = reading.anchors["c0"], reading.anchors["p"]
    pair = seed
    trail = []
    while pair not in trail:
        trail.append(pair)
        pair = previous().successor(order, *pair)
    assert pair == seed
    flags = [v in reading.marks for _, v in trail]
    longest = None
    if not all(flags):
        size = 0
        longest = 0
        for flag in flags + flags:
            size = size + 1 if flag else 0
            longest = max(size, longest)
    rooted = None if all(flags) else ([seed[0] in reading.marks] + flags).index(False)
    return {"seeded_states": trail, "period": len(trail), "longest_c_only_r_arm": longest,
            "rooted_r_prefix_cap": rooted}


def run_case(case, seeds, scope):
    p, edits = prepare(case)
    source = p.immutable()
    reading = read_source(source)
    a = reading.anchors
    assert a == {role: p.role_id[role] for role in a}
    assert reading.witnesses == {
        frozenset((p.role_id[x], p.role_id[y])): k for (x, y), k in p.arc_witness.items()
    }
    assert max(nx.triangles(reading.candidate).values()) == 0
    assert all(len(d) >= 2 and len(d) == reading.candidate.degree(k) - int(case.shortage and k == a["p"])
               for k, d in reading.opens.items())
    components = sorted(tuple(sorted(c)) for c in nx.connected_components(reading.ordinary))
    assert len(components) == (2 if case.erase_origin else 1)
    c_h = next(row for row in components if a["H"] in row)
    assert (a["O"] in c_h) == reading.o_pair
    assert (a["S0"] in c_h) and (a["c0"] in c_h)
    c_ports = reading.port
    c8_to_p = a["p"] in c_ports[a["c8"]]
    assert c8_to_p == (8 not in case.switches)
    by_law = {}
    for law in LAWS:
        original_projections = previous().certify_source(source, reading, law)
        old_names = projected_names(source, scope, law)
        target = fixtures().expected_words(law, len(scope)) if c8_to_p else tuple(range(1 << len(scope)))
        assert old_names == target
        final = source
        cuts = []
        projection_counts = [len(old_names)]
        for age in (1, 2):
            final, step = literal_cut(final, law, age)
            cuts.append(step)
            if step["status"] != "extend":
                break
            read_names = projected_names(final, scope, law)
            assert read_names == old_names
            projection_counts.append(len(read_names))
        if case.shortage:
            assert final == source and cuts[0]["status"] == "stall" and cuts[0]["shortages"] == [(a["p"], 1)]
        else:
            assert len(cuts) == 2 and all(row["status"] == "extend" for row in cuts)
        by_law[law] = {
            "source_projections": original_projections, "cuts": cuts,
            "literal_word_binding": retained_words(reading, cuts),
            "occupied_projection": {"scope": scope, "allowed_words_lsb_first": old_names,
                                    "counts_at_original_and_reached_cuts": projection_counts},
            "recodings": [check_recoding(final, source, reading, cuts, law, seed) for seed in seeds],
        }
    for parity, nae in zip(by_law["parity"]["cuts"], by_law["nae"]["cuts"], strict=True):
        assert (parity["status"], parity["shortages"], parity["births"]) == (nae["status"], nae["shortages"], nae["births"])
    live = {label: k for label, k in p.role_id.items() if k in reading.opens}
    label = {k: role for role, k in live.items()}
    pairs = sorted((tuple(sorted(label[k] for k in pair)), w) for pair, w in reading.witnesses.items())
    sender_map = {k: [r["peer"] for r in c_ports[k].values() if (r["local_count"], r["peer_count"]) in ((2, 4), (6, 4))]
                  for k in reading.sender + reading.reserve}
    mixed = [a["S0"]]
    while True:
        tail, = sender_map[mixed[-1]]
        if tail == a["S0"]:
            break
        assert tail not in mixed
        mixed.append(tail)
    assert len(mixed) == (14 if case.break_sender else 7)
    orbit = None if case.shortage else walk_bound(reading.r_order, reading)
    s_pairs = zip(reading.sender, reading.sender[1:] + reading.sender[:1], strict=True)
    first_missing = next((i for i, (old, new) in enumerate(s_pairs, 1) if sender_map[old] != [new]), None)
    assert first_missing == (4 if case.break_sender else None)
    third_cap = None
    if orbit is not None:
        rmax, smax = orbit["rooted_r_prefix_cap"], first_missing
        if rmax is not None or smax is not None:
            rmax = rmax if rmax is not None else smax + 1
            smax = smax if smax is not None else rmax + 1
            third_cap = 1 + min(rmax, smax + 1) + min(smax, rmax + 1)
    return {
        "case": case.key, "original_stars": source, "live_roles": live, "decoded_roles": a, "edits": edits,
        "original_components": components, "original_distinction_count": len(reading.owners),
        "loose_names": {label[k]: d for k, d in reading.opens.items()},
        "candidate_pairs": [pair for pair, _ in pairs], "candidate_pair_witnesses": pairs,
        "ports": {k: {"ordered_circuit_neighbors": reading.r_order.get(k, ()),
                      "all_paid_ports": sorted(row.values(), key=lambda x: (x["local_count"], x["peer"]))}
                  for k, row in c_ports.items()},
        "occupied_primitive": {role: [{"peer_role": label[v], **row} for v, row in sorted(c_ports[a[role]].items())]
                               for role in ("c8", "p")},
        "c_marked_originals": sorted(reading.marks),
        "seeded_r_orbit": orbit, "registered_strict_s_arm_cap": None if case.shortage else first_missing,
        "third_rank_cap": third_cap,
        "sender_private_return_intact": c_ports[reading.sender[3]].get(reading.sender[4]) is not None,
        "mixed_sender_corridor": None if case.shortage else mixed, "O_and_H_together": reading.o_pair,
        "laws": by_law,
    }


def compare(rows, scope):
    cases_by_name = {r["case"]: r for r in rows}
    changes = {}
    for case, base, kind in (
            ("near", "intact", "circuit_head_exchange"), ("remote", "intact", "circuit_head_exchange"),
            ("near_remote", "intact", "circuit_head_exchange"),
            ("intact_s_break", "intact", "private_head_exchange"), ("near_s_break", "near", "private_head_exchange")):
        x, y = cases_by_name[base], cases_by_name[case]
        assert x["live_roles"] == y["live_roles"] and x["loose_names"] == y["loose_names"]
        a, b = x["original_stars"], y["original_stars"]
        witnesses = [change for edit in y["edits"] if edit["kind"] == kind for change in edit["changes"]]
        diff = {i for i, (old, new) in enumerate(zip(a, b, strict=True)) if old != new}
        assert diff == {edit["witness"] for edit in witnesses} and not diff.intersection(x["live_roles"].values())
        assert tuple(map(len, a)) == tuple(map(len, b))
        for edit in witnesses:
            w = edit["witness"]
            assert set(a[w]) - set(b[w]) == set(edit["removed_names"])
            assert set(b[w]) - set(a[w]) == set(edit["received_names"])
        changes[case] = {"against": base, "changed_spent_holders": sorted(diff), "same_live_rows": True}

    near, retag = (cases_by_name[k] for k in ("near", "near_retag"))
    assert near["loose_names"] == retag["loose_names"] and near["candidate_pairs"] == retag["candidate_pairs"]

    def successors(row):
        port = row["ordered_circuit_neighbors"]
        return dict(zip(port, port[1:] + port[:1], strict=True))

    assert {p: successors(r) for p, r in near["ports"].items()} == {
        p: successors(r) for p, r in retag["ports"].items()
    }
    retag_removed = {d for row in retag["edits"] if row["kind"] == "retag" for d in row["removed_names"]}
    assert tuple(tuple(d for d in row if d not in retag_removed) for row in near["original_stars"]) == retag["original_stars"]

    intact, shortage, erased = (cases_by_name[k] for k in ("intact", "p_shortage", "o_erased"))
    lost, = shortage["edits"][0]["removed_names"]
    assert shortage["ports"] == intact["ports"] and shortage["candidate_pairs"] == intact["candidate_pairs"]
    assert tuple(tuple(d for d in row if d != lost) for row in intact["original_stars"]) == shortage["original_stars"]
    removed, = erased["edits"]
    assert removed["witness"] == len(intact["original_stars"]) - 1
    names_lost = set(removed["removed_shared"]) | set(removed["removed_private"])
    assert tuple(tuple(d for d in row if d not in names_lost) for row in intact["original_stars"][:-1]) == erased["original_stars"]
    assert set(intact["candidate_pairs"]) - set(erased["candidate_pairs"]) == {("H", "O")}

    primitive = {}
    remote = cases_by_name["remote"]
    for donor in ("c8", "p"):
        x = {p["peer_role"]: p for p in intact["occupied_primitive"][donor]}
        y = {p["peer_role"]: p for p in near["occupied_primitive"][donor]}
        assert intact["occupied_primitive"][donor] == remote["occupied_primitive"][donor]
        removed_peer, = x.keys() - y.keys()
        gained_peer, = y.keys() - x.keys()
        assert all(x[p] == y[p] for p in x.keys() & y.keys())
        assert x[removed_peer]["local_names"] == y[gained_peer]["local_names"]
        primitive[donor] = {"intact": x[removed_peer], "near": y[gained_peer]}
    assert primitive["p"]["intact"]["peer_role"] == "c8" and primitive["p"]["near"]["peer_role"] == "u8"
    assert primitive["c8"]["intact"]["peer_role"] == "p" and primitive["c8"]["near"]["peer_role"] == "h"
    assert set(primitive["c8"]["intact"]["local_names"] + primitive["c8"]["intact"]["peer_names"]) == set(scope)
    witnesses = {}
    for law in LAWS:
        before = set(intact["laws"][law]["occupied_projection"]["allowed_words_lsb_first"])
        after = set(near["laws"][law]["occupied_projection"]["allowed_words_lsb_first"])
        assert before < after
        words = sorted(after - before)
        witnesses[law] = {"intact": len(before), "near": len(after),
                          "example_allowed_only_after": tuple(int(bool(words[0] & (1 << k))) for k in range(len(scope)))}
    return {"head_exchange_matches": changes, "retag_removed_shared_names": len(retag_removed),
            "shortage_removed_private_name": lost, "occupied_port_changes": primitive,
            "old_projection_examples": witnesses}


def input_hashes():
    contract = HERE / "contract.json"
    settings = json.loads(contract.read_bytes())
    preregistration = ROOT / settings["preregistration"]
    frozen = {preregistration.with_name(n): h for n, h in settings["scientific_design_sha256"].items()}
    frozen[ROOT / settings["advisor_receipt"]] = settings["advisor_sha256"]
    assert all(sha256(p.read_bytes()).hexdigest() == h for p, h in frozen.items())
    inherited = previous().archive().joint()
    files = [Path(__file__).resolve(), PRIOR, previous().PRIOR, previous().archive().JOINT, inherited.PRIOR,
             inherited.prior().END_OPERATOR, inherited.prior().FIXTURES, contract, preregistration, *frozen]
    return {str(f.relative_to(ROOT)): sha256(f.read_bytes()).hexdigest() for f in files}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    bound = input_hashes()
    baseline, _ = prepare(cases()[0])
    read = read_source(baseline.immutable())
    pair = read.port[read.anchors["c8"]][read.anchors["p"]]
    scope = tuple(pair["local_names"] + pair["peer_names"])
    assert len(scope) == 12
    rows = [run_case(case, tuple(seed + i for seed in SEEDS), scope) for i, case in enumerate(cases())]
    receipt = {"schema": "b283-physical-v1", "cases": rows, "matches": compare(rows, scope),
               "bound_source_hashes": bound, "literal_cap": CAP}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as out, gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as compressed:
        with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as payload:
            json.dump(receipt, payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            payload.write("\n")
    print(sha256(args.output.read_bytes()).hexdigest(), args.output)


if __name__ == "__main__":
    main()
