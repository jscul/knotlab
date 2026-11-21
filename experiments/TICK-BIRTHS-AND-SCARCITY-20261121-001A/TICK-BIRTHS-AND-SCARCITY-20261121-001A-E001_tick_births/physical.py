"""Literal original holdings, witnessed ports and paid growth for B281."""

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import io
from itertools import combinations, product
import json
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR_SCOPE = "SHARED-DONOR-AND-SIGN-RESPONSE-20261121-001A"
PRIOR = ROOT / "experiments" / PRIOR_SCOPE / (PRIOR_SCOPE + "-E001_shared_donor") / "physical.py"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "physical.json.gz"
LAWS = ("parity", "nae")
CAP = 8192
RENAME_SEEDS = (20261121301, 20261121401)
REPEATED = (1, 5, 13, 21, 29)
SLOW = (2, 3, 11, 16, 19, 23, 26, 27, 34, 38)
FAST_FINITE = (2, 3, 10, 11, 16, 17, 23, 24, 26, 27, 34, 35, 38, 39)


@cache
def archive():
    spec = spec_from_file_location("b281_previous_physical", PRIOR)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Case:
    key: str
    switches: tuple = ()
    retag: bool = False
    prefix: bool = False
    sender_cut: bool = False
    shortage: bool = False


def cases():
    return (
        Case("fast_lasting"), Case("slow_finite", SLOW), Case("fast_finite", FAST_FINITE),
        Case("slow_lasting", SLOW, retag=True), Case("prefix_fast_lasting", prefix=True),
        Case("prefix_slow_finite", SLOW, prefix=True),
        Case("sender_cut_fast_lasting", sender_cut=True), Case("sender_cut_slow_finite", SLOW, sender_cut=True),
        Case("shortage_fast_lasting", shortage=True),
    )


def role(tag, index):
    if index in REPEATED:
        return "p" if tag == "c" else "h"
    if tag == "c" and index in (8, 31):
        return "A"
    if tag == "c" and index in (9, 30):
        return "B"
    return f"{tag}{index}"


def local_size(tag, index, leaving, peer):
    here = role(tag, index)
    if here in ("p", "h"):
        counts = (3 if here == "p" else 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
        return counts[2 * REPEATED.index(index) + int(leaving)]
    if here == "A":
        return {"c7": 3, "B": 30, "c32": 31}[peer]
    if here == "B":
        return {"p": 3, "A": 30, "c10": 31}[peer]
    return (3 if tag == "c" else 5) if leaving else 4


def add_pair(p, pair, counts):
    tail, head = pair
    a, b = [p.holder(name) for name in pair]
    assert a != b
    if (head, tail) in p.arc_witness:
        assert set(pair) == {"A", "B"} and counts == (30, 30)
        return
    assert pair not in p.arc_witness
    witness = p.holder(f"witness {tail} → {head}")
    p.arc_witness[pair] = witness
    for owner, amount in zip((a, b), counts, strict=True):
        for _ in range(amount):
            p.new_distinction(owner, witness)
        p.new_distinction(owner)


def exchange(p, first, second, size):
    witness = [p.arc_witness.pop(pair) for pair in (first, second)]
    names = [sorted(set(p.stars[w]) & set(p.stars[p.role_id[pair[1]]]))
             for pair, w in zip((first, second), witness, strict=True)]
    assert all(len(panel) == size for panel in names)
    edits = []
    for i, (tail, head) in enumerate((first, second)):
        j = 1 - i
        w = witness[i]
        removed, added = names[i], names[j]
        other = (second, first)[i][1]
        p.stars[w] = [b for b in p.stars[w] if b not in removed] + added
        p.arc_witness[tail, other] = w
        p.role_id.pop(f"witness {tail} → {head}")
        p.role_id[f"witness {tail} → {other}"] = w
        edits.append({"witness": w, "tail": p.role_id[tail], "old_head": p.role_id[head],
                      "new_head": p.role_id[other], "removed_names": removed, "received_names": added})
    return edits


def prepare(case):
    p = archive().joint().prior().Preparation([], {}, {})
    retag_incidence = []
    for tag in ("c", "u"):
        for i in range(40):
            j = (i + 1) % 40
            u, v = role(tag, i), role(tag, j)
            counts = local_size(tag, i, True, v), local_size(tag, j, False, u)
            add_pair(p, (u, v), counts)
            if tag == "u":
                w = p.arc_witness[u, v]
                if counts[0] == 5:
                    retag_incidence.append((p.role_id[u], w))
                if j == 1:
                    assert v == "h" and counts[1] == 5
                    retag_incidence.append((p.role_id[v], w))
    add_pair(p, ("c36", "u36"), (1, 2))
    for i in range(4):
        add_pair(p, (f"R{i}", f"R{(i + 1) % 4}"), (1, 2))
    for pair, counts in ((("c34", "S1"), (1, 6)), (("S1", "S2"), (1, 2)), (("S2", "B"), (1, 7))):
        add_pair(p, pair, counts)
    if case.prefix:
        for pair, counts in ((("R0", "X"), (1, 9)), (("X", "Y"), (1, 8)), (("Y", "c0"), (1, 10))):
            add_pair(p, pair, counts)
    else:
        add_pair(p, ("R0", "c0"), (1, 9))

    edits = []
    for i in case.switches:
        j = (i + 1) % 40
        rows = exchange(p, (role("c", i), role("c", j)), (role("u", i), role("u", j)), 4)
        edits.append({"kind": "circuit_head_exchange", "site": i, "changes": rows})
    if case.sender_cut:
        rows = exchange(p, ("S1", "S2"), ("R1", "R2"), 2)
        edits.append({"kind": "sender_head_exchange", "changes": rows})
    if case.retag:
        for donor, witness in retag_incidence:
            names = sorted(set(p.stars[donor]) & set(p.stars[witness]))
            assert len(names) == 5
            removed = names[-2:]
            for k in (donor, witness):
                p.stars[k] = [d for d in p.stars[k] if d not in removed]
            edits.append({"kind": "retag", "donor": donor, "witness": witness, "removed_names": removed})
    if case.shortage:
        f = archive().joint().prior().fixture()
        p_id = p.role_id["p"]
        _, _, loose = f.incidence(p.immutable())
        assert len(loose[p_id]) == 10
        removed = loose[p_id][-1]
        p.stars[p_id].remove(removed)
        edits.append({"kind": "private_shortage", "donor": p_id, "removed_names": [removed]})
    return p, edits


@dataclass
class PhysicalRead:
    owners: dict
    ordinary: nx.Graph
    opens: dict
    candidate: nx.Graph
    port: dict
    ordered: dict
    witnesses: dict
    anchors: dict
    marks: set


def successor(ordered, prior, current, direction=1):
    choices = ordered[current]
    return current, choices[(choices.index(prior) + direction) % len(choices)]


def read_source(stars):
    f = archive().joint().prior().fixture()
    owners, ordinary, loose = f.incidence(stars)
    _, candidate = f.witnessed_end(ordinary, loose)
    assert nx.is_connected(ordinary)
    port = {k: {} for k in loose}
    witnesses = {}
    for w in sorted(set(ordinary) - loose.keys()):
        a, b = sorted(ordinary[w])
        assert a in loose and b in loose
        pairs = frozenset((a, b))
        assert pairs not in witnesses
        witnesses[pairs] = w
        left = sorted(set(stars[a]) & set(stars[w]))
        right = sorted(set(stars[b]) & set(stars[w]))
        assert left and right and len(left) + len(right) == len(stars[w])
        for x, y, local, remote in ((a, b, left, right), (b, a, right, left)):
            port[x][y] = {"peer": y, "witness": w, "local_names": local, "peer_names": remote,
                          "local_count": len(local), "peer_count": len(remote),
                          "circuit": min(len(local), len(remote)) >= 3}
    assert set(witnesses) == set(map(frozenset, candidate.edges))
    assert all(set(ordinary[k]).isdisjoint(loose.keys()) for k in loose)
    ordered = {
        k: tuple(row["peer"] for row in sorted(links.values(), key=lambda row: row["local_count"]) if row["circuit"])
        for k, links in port.items() if any(row["circuit"] for row in links.values())
    }
    assert all(len(row) >= 2 and len({port[k][j]["local_count"] for j in row}) == len(row)
               for k, row in ordered.items())
    marks = {k for k, row in ordered.items() if any(port[k][j]["local_count"] == 3 for j in row)}

    def signed(a, b):
        return [(k, j) for k, edges in port.items() for j, row in edges.items()
                if (row["local_count"], row["peer_count"]) == (a, b)]

    (r0, origin_entry), = signed(1, 9)
    anchors = {"R0": r0}
    if signed(1, 8):
        (x, y), = signed(1, 8)
        (y2, c0), = signed(1, 10)
        assert x == origin_entry and y == y2
        anchors.update(X=x, Y=y)
    else:
        c0 = origin_entry
        assert not signed(1, 10)
    p, = (k for k in ordered[c0] if len(ordered[k]) == 10)
    h, = (k for k, row in ordered.items() if k != p and len(row) == 10)
    r1, = (j for k, j in signed(1, 2) if k == r0)
    r3, = (k for k, j in signed(1, 2) if j == r0)
    r2, = (k for k, j in signed(1, 2) if j == r3)
    (s2, b), = signed(1, 7)
    (c34, s1), = signed(1, 6)
    a, = (k for k, j in signed(30, 30) if j == b)
    _, c32 = successor(ordered, b, a)
    _, c33 = successor(ordered, a, c32)
    assert successor(ordered, c32, c33)[1] == c34
    anchors.update(c0=c0, p=p, h=h, R1=r1, R2=r2, R3=r3, A=a, B=b, S1=s1, S2=s2,
                   c32=c32, c33=c33, c34=c34)
    assert len(set(anchors.values())) == len(anchors)
    return PhysicalRead(owners, ordinary, loose, candidate, port, ordered, witnesses, anchors, marks)


def allowed(bits, law):
    return sum(bits) % 2 == 0 if law == "parity" else len(set(bits)) == 2


def extend_original(stars, reading, target, words, law):
    """Construct one actual whole source state for an allowed local row."""
    values = dict(zip(stars[target], words, strict=True))
    for holder in sorted(set(reading.ordinary) - reading.opens.keys()) + sorted(reading.opens):
        support = stars[holder]
        free = [d for d in support if d not in values]
        values.update({d: 0 for d in free})
        state = [values[d] for d in support]
        if not allowed(state, law):
            assert free
            values[free[0]] = 1 if law == "parity" else 1 - state[0]
        assert allowed([values[d] for d in support], law)
    assert tuple(values[d] for d in stars[target]) == words
    assert all(allowed([values[d] for d in star], law) for star in stars)


def relation_size(law, arity):
    assert arity >= 3
    return str(1 << (arity - 1) if law == "parity" else (1 << arity) - 2)


def certify_source(stars, reading, law):
    f = archive().joint().prior().fixture()
    worked = 0
    for k, row in enumerate(stars):
        n = len(row)
        f.canonical_relation(law, n)
        if n <= 5:
            tests = list(product((0, 1), repeat=n))
        else:
            tests = [(0,) * n, (1,) * n, tuple(i % 2 for i in range(n))]
            tests.extend(tuple(int(i in positions) for i in range(n)) for positions in ((0,), (0, 1), (0, n - 1)))
        for bits in tests:
            if allowed(bits, law):
                extend_original(stars, reading, k, bits, law)
                worked += 1
    return {"by_arity": {n: {"holders": k, "allowed_rows": relation_size(law, n)}
                         for n, k in sorted(Counter(map(len, stars)).items())},
            "all_K1_K2_K3": True, "constructive_extension_checks": worked}


def literal_cut(stars, law, age):
    old = archive().joint()
    f = old.prior().fixture()
    owners, _, loose = f.incidence(stars)
    forecast = archive().ordinary_forecast(stars, law)
    result = {"age": age, "status": forecast["status"], "shortages": forecast["shortages"],
              "implied": forecast["implied"], "forecast": forecast, "births": []}
    if forecast["status"] != "extend":
        return stars, result
    planned = forecast["funded_births"]
    assert 1 < len(planned) <= 1024 and not forecast["implied"]
    status, births, multiple = f.literal_turn(stars, law)
    assert status == "extend" and multiple == forecast["proposed_multiple_groups"]
    assert all(len(b.parents) == 2 for b in births)
    fresh_names = [d for b in births for d in b.fresh]
    assert len(set(fresh_names)) == len(fresh_names) and not set(fresh_names).intersection(owners)
    spent = {k: [] for k in loose}
    with old.projector(stars, law) as project:
        for b, (parents, demand, new_count) in zip(births, planned, strict=True):
            assert b.parents == parents and len(b.fresh) == new_count and b.fresh
            for k, d in zip(b.parents, b.inputs, strict=True):
                assert owners[d] == [k]
                spent[k].append(d)
            old_words = project(b.inputs)
            assert old_words == (0, 1, 2, 3)
            result["births"].append(
                {"holder": b.knot, "parents": b.parents, "consumed_names": b.inputs, "fresh_names": b.fresh,
                 "demand": demand, "grant": new_count, "input_projection": old_words,
                 "allowed_rows_on_newborn": relation_size(law, len(b.support)), "newborn_K1_K2_K3": True}
            )
    assert {k: sorted(pay) for k, pay in spent.items()} == loose
    grown = stars + tuple(b.support for b in births)
    assert f.incidence(grown)[2] == {b.knot: list(b.fresh) for b in births}
    result["old_assignments_extend"] = True
    result["paid_names_by_donor"] = spent
    return grown, result


def native_words(reading, stages):
    if stages[0]["status"] != "extend":
        return {}
    by_pair = {frozenset(row["parents"]): row for row in stages[0]["births"]}
    by_children = {frozenset(row["parents"]): row for row in stages[1]["births"]}
    assert by_pair.keys() == reading.witnesses.keys()
    assert len(by_children) == len(stages[1]["births"])
    assert len(by_children) == sum(len(ports) * (len(ports) - 1) // 2 for ports in reading.port.values())
    anchors = reading.anchors

    def descendants(roles):
        ids = [anchors[role] for role in roles]
        first = [by_pair[frozenset((u, v))] for u, v in zip(ids, ids[1:])]
        item = first[0] if len(first) == 1 else by_children[frozenset(row["holder"] for row in first)]
        return {"original_word": roles, "physical": item}

    found = {
        "W1": descendants(("B", "A")),
        "W2": descendants(("B", "A", "c32")),
        "R_seed_to_size_three": descendants(("R0", "X", "Y") if "X" in anchors else ("R0", "c0", "p")),
    }
    assert found["W1"]["physical"]["holder"] in found["W2"]["physical"]["parents"]
    if "X" in anchors:
        found["V"] = descendants(("X", "Y"))
    rotations = []
    for middle, order in sorted(reading.ordered.items()):
        for previous in order:
            _, coming = successor(reading.ordered, previous, middle)
            l = by_pair[frozenset((previous, middle))]
            r = by_pair[frozenset((middle, coming))]
            actual = by_children[frozenset((l["holder"], r["holder"]))]
            rotations.append({"originals": (previous, middle, coming), "first_cut_holders": (l["holder"], r["holder"]),
                              "actual_second_cut_holder": actual["holder"], "parents": actual["parents"],
                              "consumed_names": actual["consumed_names"], "grant": actual["grant"]})
    return {"anchors": found, "all_paid_port_rotations_at_cut_two": rotations}


def ordered_orbits(reading, direction):
    pending = {(p, v) for v, ports in reading.ordered.items() for p in ports}
    seed = reading.anchors["c0"], reading.anchors["p"]
    result = []
    while pending:
        first = seed if seed in pending else min(pending)
        trail = []
        pair = first
        while pair in pending:
            trail.append(pair)
            pending.remove(pair)
            pair = successor(reading.ordered, *pair, direction)
        assert pair == first
        marks = [node in reading.marks for _, node in trail]
        best = None
        if not all(marks):
            runs = []
            length = 0
            for mark in marks + marks:
                length = length + 1 if mark else 0
                runs.append(length)
            best = max(runs)
        result.append({"states": trail, "seeded": first == seed, "period": len(trail), "all_c": all(marks),
                       "longest_c_window": best, "clock_mark_count": sum(k == seed[1] for _, k in trail)})
    return result


def recoding(stars, source, reading, stages, law, seed):
    f = archive().joint().prior().fixture()
    renamed, to_old = f.rename(stars, seed)
    older, parents, _, depth = f.peel(renamed, law)
    expected_depth = sum(c["status"] == "extend" for c in stages)
    assert depth == expected_depth
    original_indices = sorted(older)
    natural = [to_old[k] for k in original_indices]
    assert set(natural) == set(range(len(source)))
    other = read_source(tuple(renamed[k] for k in original_indices))
    assert {name: natural[k] for name, k in other.anchors.items()} == reading.anchors
    assert {natural[k] for k in other.marks} == reading.marks
    assert {natural[k]: tuple(natural[i] for i in row) for k, row in other.ordered.items()} == reading.ordered
    assert {frozenset(natural[k] for k in p): natural[w] for p, w in other.witnesses.items()} == reading.witnesses
    declared = {b["holder"]: frozenset(b["parents"]) for cut in stages for b in cut["births"]}
    assert {to_old[k]: frozenset(to_old[i] for i in p) for k, p in parents.items()} == declared
    return {"seed": seed, "recovered_depth": depth, "parent_lists_recovered": len(declared),
            "original_indices_in_recoding": original_indices, "recoded_to_original_holder": to_old,
            "recoded_full_stars": renamed}


def run_case(case, seeds):
    prepared, edits = prepare(case)
    source = prepared.immutable()
    read = read_source(source)
    assert read.anchors == {name: prepared.role_id[name] for name in read.anchors}
    assert read.witnesses == {
        frozenset((prepared.role_id[a], prepared.role_id[b])): k
        for (a, b), k in prepared.arc_witness.items()
    }
    assert all(n == 0 for n in nx.triangles(read.candidate).values())
    assert all(len(names) >= 2 and len(names) == read.candidate.degree(k) - int(case.shortage and k == read.anchors["p"])
               for k, names in read.opens.items())
    by_law = {}
    for law in LAWS:
        lawful = certify_source(source, read, law)
        final = source
        stages = []
        for age in (1, 2):
            final, stage = literal_cut(final, law, age)
            stages.append(stage)
            if stage["status"] != "extend":
                break
        if case.shortage:
            assert final == source and stages[0]["shortages"] == ((read.anchors["p"], 1),)
            assert stages[0]["status"] == "stall"
        else:
            assert len(stages) == 2 and all(cut["status"] == "extend" for cut in stages)
        by_law[law] = {"source_projections": lawful, "cuts": stages,
                       "literal_word_binding": native_words(read, stages),
                       "recodings": [recoding(final, source, read, stages, law, seed) for seed in seeds]}
    assert by_law["parity"]["cuts"] == by_law["nae"]["cuts"] or all(
        (x["status"], x["shortages"], [(b["parents"], b["consumed_names"], b["fresh_names"]) for b in x["births"]]) ==
        (y["status"], y["shortages"], [(b["parents"], b["consumed_names"], b["fresh_names"]) for b in y["births"]])
        for x, y in zip(by_law["parity"]["cuts"], by_law["nae"]["cuts"], strict=True)
    )
    live = {name: k for name, k in prepared.role_id.items() if k in read.opens}
    label = {k: name for name, k in live.items()}
    pair_witnesses = sorted((tuple(sorted(label[k] for k in pair)), w) for pair, w in read.witnesses.items())
    unmarked_cycles = nx.cycle_basis(read.candidate.subgraph(read.marks))
    return {
        "case": case.key, "live_roles": live, "decoded_roles": read.anchors, "original_stars": source,
        "original_distinction_count": len(read.owners), "loose_names": {label[k]: d for k, d in read.opens.items()},
        "candidate_pairs": [pair for pair, _ in pair_witnesses], "candidate_pair_witnesses": pair_witnesses,
        "ports": {k: {"all_paid_ports": sorted(row.values(), key=lambda v: (v["local_count"], v["peer"])),
                      "ordered_circuit_neighbors": read.ordered.get(k, ())} for k, row in read.port.items()},
        "c_marked_originals": sorted(read.marks), "edits": edits,
        "sender_private_pair_present": read.candidate.has_edge(read.anchors["S1"], read.anchors["S2"]),
        "unrestricted_c_cycle_witness": [label[k] for k in min(unmarked_cycles, key=lambda p: (len(p), p))]
        if unmarked_cycles else None,
        "port_orbits": {"next": ordered_orbits(read, 1), "previous": ordered_orbits(read, -1)},
        "laws": by_law,
    }


def checks(rows):
    known = {r["case"]: r for r in rows}
    matched = {}
    for case, base in (
            ("slow_finite", "fast_lasting"), ("fast_finite", "fast_lasting"),
            ("prefix_slow_finite", "prefix_fast_lasting"),
            ("sender_cut_fast_lasting", "fast_lasting"), ("sender_cut_slow_finite", "slow_finite")):
        a, b = known[base], known[case]
        assert a["live_roles"] == b["live_roles"] and a["loose_names"] == b["loose_names"]
        assert tuple(map(len, a["original_stars"])) == tuple(map(len, b["original_stars"]))
        delta = {k for k, (x, y) in enumerate(zip(a["original_stars"], b["original_stars"], strict=True)) if x != y}
        assert not set(a["live_roles"].values()).intersection(delta)
        matched[case] = {"against": base, "changed_spent_holders": sorted(delta), "same_live_original_rows": True}
    x, y = known["slow_finite"], known["slow_lasting"]
    assert x["live_roles"] == y["live_roles"] and x["loose_names"] == y["loose_names"]
    assert x["candidate_pairs"] == y["candidate_pairs"] and x["candidate_pair_witnesses"] == y["candidate_pair_witnesses"]

    def turns(row):
        order = row["ordered_circuit_neighbors"]
        return dict(zip(order, order[1:] + order[:1], strict=True))

    assert {k: turns(row) for k, row in x["ports"].items()} == {k: turns(row) for k, row in y["ports"].items()}
    erasures = [r for r in y["edits"] if r["kind"] == "retag"]
    removed = {d for r in erasures for d in r["removed_names"]}
    assert tuple(tuple(d for d in row if d not in removed) for row in x["original_stars"]) == y["original_stars"]
    x, y = known["fast_lasting"], known["shortage_fast_lasting"]
    assert x["candidate_pairs"] == y["candidate_pairs"] and x["ports"] == y["ports"]
    gone, = y["edits"][0]["removed_names"]
    assert tuple(tuple(d for d in row if d != gone) for row in x["original_stars"]) == y["original_stars"]
    return {"exchanges": matched, "retag_removed_shared_name_count": len(removed),
            "retag_matches_ordinary_graph_and_local_port_order": True, "one_unpaid_private_name": gone}


def input_hashes():
    contract = HERE / "contract.json"
    settings = json.loads(contract.read_bytes())
    preregistration = ROOT / settings["preregistration"]
    frozen = {preregistration.with_name(name): digest for name, digest in settings["scientific_design_sha256"].items()}
    frozen[ROOT / settings["advisor_receipt"]] = settings["advisor_sha256"]
    assert all(sha256(path.read_bytes()).hexdigest() == digest for path, digest in frozen.items())
    old = archive().joint()
    files = [Path(__file__).resolve(), PRIOR, archive().JOINT, old.PRIOR, old.prior().END_OPERATOR,
             old.prior().FIXTURES, contract, preregistration, *frozen]
    return {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in files}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    sources = input_hashes()
    rows = [run_case(case, tuple(seed + i for seed in RENAME_SEEDS)) for i, case in enumerate(cases())]
    receipt = {"schema": "b281-physical-v1", "bound_source_hashes": sources, "cases": rows,
               "literal_cap": CAP, "matches": checks(rows)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as out, gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as gzipped:
        with io.TextIOWrapper(gzipped, encoding="utf-8", newline="\n") as payload:
            json.dump(receipt, payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            payload.write("\n")
    print(sha256(args.output.read_bytes()).hexdigest(), args.output)


if __name__ == "__main__":
    main()
