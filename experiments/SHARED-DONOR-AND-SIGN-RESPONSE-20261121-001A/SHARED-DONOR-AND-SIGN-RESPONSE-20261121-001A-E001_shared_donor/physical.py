"""Physical witness, payment and positive-cut replay for B278."""

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
from math import prod
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JOINT_SCOPE = "JOINT-PARENTS-AND-ERASURE-20261120-001A"
JOINT = ROOT / "experiments" / JOINT_SCOPE / (JOINT_SCOPE + "-E001_joint_parents") / "physical.py"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "physical.json.gz"
CAP = 8192
SITES = (20, 21, 23, 25)
RNG_SEEDS = (20261121191, 20261121291)
LAWS = ("parity", "nae")


@cache
def joint():
    spec = spec_from_file_location("b278_disjoint_physical_code", JOINT)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Case:
    middle: str
    modes: str
    supply: int | None = None

    @property
    def label(self):
        if self.supply is not None:
            return f"isolated_{self.modes}_h{self.supply}"
        return f"{self.middle}_{self.modes or 'archive'}"


def cases():
    return tuple(
        Case(kind, mode) for kind in ("active", "rewired")
        for mode in ["", *("".join(row) for row in product("CS", repeat=4))]
    ) + tuple(
        Case("isolated", mode, h) for mode in ("CC", "CS", "SC", "SS") for h in range(1, 5)
    )


def prepare(case):
    old = joint()
    if case.supply is None:
        p, _ = old.prior().build(case.middle)
        for i in range(len(case.modes)):
            p.holder(f"w{i + 1}")
        for i, (site, mode) in enumerate(zip(SITES, case.modes), 1):
            u, v = f"c{site}", f"c{site + 1}"
            old.install_gate(p, (u, v, f"w{i}"), p.arc_witness[u, v], mode, original=True)
        return p

    p = old.prior().Preparation([], {}, {})
    for role in ("u", "p", "v", "w1", "w2", "z", "X", "Y", "witness left", "witness right"):
        p.holder(role)
    u, z, x, y = (p.role_id[role] for role in ("u", "z", "X", "Y"))
    for _ in range(2):
        p.new_distinction(u, x)
        p.new_distinction(y, z)
        p.new_distinction(z)
    p.new_distinction(x, y)
    old.install_gate(p, ("u", "p", "w1"), p.role_id["witness left"], case.modes[0], original=False)
    old.install_gate(p, ("p", "v", "w2"), p.role_id["witness right"], case.modes[1], original=False)
    shared = p.role_id["p"]
    _, _, opens = old.prior().fixture().incidence(p.immutable())
    assert len(opens[shared]) == 4
    removed = set(opens[shared][case.supply:])
    p.stars[shared] = [d for d in p.stars[shared] if d not in removed]
    return p


@dataclass
class Reading:
    owners: dict
    ordinary: nx.Graph
    opens: dict
    candidate: nx.Graph
    roles: dict
    gates: dict
    clock_holdings: dict
    route: tuple
    third_spine: tuple


def witness_partitions(stars):
    old = joint()
    f = old.prior().fixture()
    owners, ordinary, loose = f.incidence(stars)
    _, candidate = f.witnessed_end(ordinary, loose)
    assert nx.is_connected(ordinary)
    meetings = Counter(tuple(sorted(at)) for at in owners.values() if len(at) == 2)
    arcs, split = nx.DiGraph(), nx.Graph()
    gated, pair_witness = [], {}
    for holder in sorted(set(ordinary) - loose.keys()):
        live_neighbors = sorted(set(ordinary[holder]) & loose.keys())
        counts = tuple(meetings[tuple(sorted((holder, k)))] for k in live_neighbors)
        if len(live_neighbors) <= 1:
            continue
        if counts == (4, 4, 4):
            gated.append(old.Gate("C", tuple(live_neighbors), (holder,)))
        elif counts == (2, 2):
            assert not split.has_edge(*live_neighbors)
            split.add_edge(*live_neighbors, witness=holder)
        else:
            assert len(live_neighbors) == 2 and min(counts) == 1 and max(counts) <= 4
            tail, head = live_neighbors if counts[0] == 1 else tuple(reversed(live_neighbors))
            arcs.add_edge(tail, head, multiplicity=max(counts))
            pair_witness[tail, head] = holder

    covered = set()
    for row in nx.find_cliques(split):
        assert len(row) == 3
        terminals = tuple(sorted(row))
        pairs = set(combinations(terminals, 2))
        assert not covered.intersection(pairs)
        covered.update(pairs)
        witnesses = tuple(sorted(split[u][v]["witness"] for u, v in pairs))
        gated.append(old.Gate("S", terminals, witnesses))
    assert covered == {tuple(sorted(pair)) for pair in split.edges}
    return owners, ordinary, loose, candidate, meetings, arcs, pair_witness, gated


def orient_gates(arcs, gates):
    uses = Counter(k for g in gates for k in g.terminals)
    gaps = nx.Graph()
    for gate in gates:
        private, = (k for k in gate.terminals if k not in arcs and uses[k] == 1)
        left, right = (k for k in gate.terminals if k != private)
        gaps.add_edge(left, right, gate=gate, private=private)
    recovered = {}
    for comp in nx.connected_components(gaps):
        chain = gaps.subgraph(comp)
        origin, = (k for k in chain if k in arcs and arcs.in_degree(k) == 1)
        terminal, = (k for k in chain if k in arcs and arcs.out_degree(k) == 1)
        order = nx.shortest_path(chain, origin, terminal)
        assert len(order) == len(chain) == len(chain.edges) + 1
        for u, v in zip(order, order[1:]):
            arcs.add_edge(u, v, multiplicity=2)
            edge = chain[u][v]
            recovered[u, v] = edge["private"], edge["gate"]
    return recovered


def read_original(stars):
    owners, ordinary, loose, candidate, meetings, arcs, pair_witness, gates = witness_partitions(stars)
    if len(loose) == 6:
        assert len(gates) == 2
        donor_sets = [set(gate.terminals) for gate in gates]
        donors = set.union(*donor_sets)
        shared, = set.intersection(*donor_sets)
        z, = set(loose) - donors
        u, = (k for k in donors if nx.shortest_path_length(ordinary, z, k) == 3)
        _, y, x, _ = nx.shortest_path(ordinary, z, u)
        chain = ((u, x), (x, y), (y, z))
        assert [meetings[tuple(sorted(pair))] for pair in chain] == [2, 1, 2]
        assert len(loose[z]) == 2 and not candidate.degree(z)
        left, = (g for g in gates if u in g.terminals)
        right, = (g for g in gates if u not in g.terminals)
        w1, = set(left.terminals) - {u, shared}
        v, w2 = sorted(set(right.terminals) - {shared})
        assert set(map(frozenset, candidate.edges)) == set(
            frozenset(pair) for gate in gates for pair in combinations(gate.terminals, 2)
        )
        return Reading(owners, ordinary, loose, candidate,
                       dict(u=u, p=shared, v=v, w1=w1, w2=w2, z=z, X=x, Y=y),
                       {"left": left, "right": right}, {}, (), ())

    reattached = orient_gates(arcs, gates)
    old = joint().prior()
    scaffold = old.PhysicalReading(arcs, pair_witness, loose)
    frame = old.decode_frames(scaffold)
    middle, details = old.decode_connectors(scaffold, frame)
    roles = frame | middle
    reverse = {k: label for label, k in roles.items()}
    labelled_gates = {}
    for (u, v), (private, gate) in reattached.items():
        site = int(reverse[u][1:])
        assert reverse[u] == f"c{site}" and reverse[v] == f"c{site + 1}"
        name = f"w{SITES.index(site) + 1}"
        roles[name] = private
        labelled_gates[str(site)] = gate
    assert set(roles.values()) == set(loose)
    reverse = {k: label for label, k in roles.items()}
    mid = candidate.subgraph(set(loose) - set(frame.values()))
    route, = nx.all_shortest_paths(mid, roles["a"], roles["b"])
    assert len(route) == 35
    holdings = {str(k): v for k, v in old.stable_origins(stars, scaffold, frame).items()}
    return Reading(owners, ordinary, loose, candidate, roles, labelled_gates, holdings,
                   tuple(reverse[k] for k in route), tuple(details["pure_c_order"]))


def ordinary_forecast(stars, law):
    """Retain the entire proposed plan alongside the paid physical cuts."""
    f = joint().prior().fixture()
    _, ordinary, loose = f.incidence(stars)
    blocks, candidate = f.witnessed_end(ordinary, loose)
    marked = {k: tuple(sorted(block)) for k, block in zip(ordinary, blocks, strict=True) if len(block) >= 2}
    multiple = f.multi_groups(blocks, candidate)
    rosters = Counter(k for group in multiple for k in group)
    turn = f.step(f.from_stars(stars), law, max_births=CAP)
    rivals = []
    for group in sorted(tuple(sorted(row)) for row in nx.find_cliques(candidate) if len(row) >= 2):
        held_at = sorted(k for k, block in marked.items() if set(group) <= set(block))
        rivals.append({"members": group, "held_at": held_at, "chosen_as_group": group in multiple})
    return {
        "status": turn.status, "implied": turn.implied, "shortages": turn.shortages,
        "witnessed_sets": marked, "maximal_candidate_sets": rivals, "proposed_multiple_groups": multiple,
        "charges_per_original_live_holder": {
            k: {"available_names": bits, "multi_charge": rosters[k],
                "loose_after_multi": len(bits) - rosters[k]}
            for k, bits in loose.items()
        },
        "funded_births": [(parents, demand, fresh) for parents, demand, fresh in
                          zip(turn.parents, turn.demand, turn.fresh, strict=True)],
    }


def crossings(reading, cuts, forecasts):
    """Read the two first groups and their actual immediate common child."""
    sites = ("left", "right") if "p" in reading.roles else ("20", "21")
    pair_labels = (("u", "p"), ("p", "v")) if "p" in reading.roles else (("c20", "c21"), ("c21", "c22"))
    gates = [reading.gates[site] for site in sites]
    p, = set(gates[0].terminals).intersection(gates[1].terminals)
    result = {"payer": p, "held_names": reading.opens[p],
              "initial_proposed": forecasts[0]["charges_per_original_live_holder"][p],
              "gate_inputs": [], "actual_through_births": []}
    if cuts[0]["status"] != "extend":
        return result
    result["initial_paid"] = cuts[0]["payments"][str(p)]
    crossing_ids = set()
    label_of = {k: role for role, k in reading.roles.items()}
    for site, labels, gate in zip(sites, pair_labels, gates, strict=True):
        endpoints = {reading.roles[label] for label in labels}
        crossing, = (b for b in cuts[0]["births"] if endpoints <= set(b["parents"]))
        if gate.mode == "S":
            assert set(crossing["parents"]) == set(gate.terminals)
        else:
            assert set(crossing["parents"]) == endpoints
        name = dict(zip(crossing["parents"], crossing["consumed_names"], strict=True))[p]
        crossing_ids.add(crossing["holder"])
        result["gate_inputs"].append(crossing | {
            "gate_site": site, "mode": gate.mode, "original_donor_roles": sorted(label_of[k] for k in crossing["parents"]),
            "actual_name_from_payer": name,
        })
    paid_names = [b["actual_name_from_payer"] for b in result["gate_inputs"]]
    assert len(set(paid_names)) == 2 and set(paid_names) <= set(reading.opens[p])
    assert len(crossing_ids) == 2
    result["first_cut_rivals"] = [group for group in forecasts[1]["maximal_candidate_sets"]
                                  if crossing_ids <= set(group["members"])]
    if len(cuts) < 2:
        return result
    for b in cuts[1]["births"]:
        if crossing_ids <= set(b["parents"]):
            demand_groups = [group for group in forecasts[2]["proposed_multiple_groups"] if b["holder"] in group]
            assert len(demand_groups) == b["demand"]
            result["actual_through_births"].append(b | {
                "gate_sites": sites,
                "demand_groups": demand_groups, "has_exactly_the_two_crossings": set(b["parents"]) == crossing_ids,
                "next_maximal_sets": [group for group in forecasts[2]["maximal_candidate_sets"]
                                      if b["holder"] in group["members"]],
            })
    return result


def test_recoding(final, original, depth, reading, cuts, law, seed):
    f = joint().prior().fixture()
    renamed, new_to_old = f.rename(final, seed)
    recovered, parents, _, count = f.peel(renamed, law)
    assert count == depth
    ordered = sorted(recovered)
    mapped_original = [new_to_old[k] for k in ordered]
    assert set(mapped_original) == set(range(len(original)))
    observed = read_original(tuple(renamed[k] for k in ordered))
    actual_roles = {role: mapped_original[k] for role, k in observed.roles.items()}
    if "p" in reading.roles:
        symmetric = ("v", "w2")
        assert {actual_roles[k] for k in symmetric} == {reading.roles[k] for k in symmetric}
        actual_roles.update({k: reading.roles[k] for k in symmetric})
    assert actual_roles == reading.roles
    assert observed.gates.keys() == reading.gates.keys()
    for site, g in reading.gates.items():
        recovered_gate = observed.gates[site]
        assert recovered_gate.mode == g.mode
        assert {mapped_original[k] for k in recovered_gate.terminals} == set(g.terminals)
        assert {mapped_original[k] for k in recovered_gate.witnesses} == set(g.witnesses)
    assert observed.route == reading.route and observed.third_spine == reading.third_spine
    target = {b["holder"]: frozenset(b["parents"]) for cut in cuts for b in cut["births"]}
    assert {new_to_old[k]: frozenset(new_to_old[p] for p in row) for k, row in parents.items()} == target
    return {"seed": seed, "depth": depth, "actual_parents_recovered": len(target),
            "recoded_full_stars": renamed, "new_to_old": new_to_old, "original_indices": ordered}


def relations(stars, reading, law):
    old = joint()
    measurements = {site: old.joint_relation(stars, law, reading, gate)
                    for site, gate in sorted(reading.gates.items())}
    if not measurements:
        return {"gate_relations": measurements}
    sites = ("left", "right") if "p" in reading.roles else ("20", "21")
    scopes = [set(measurements[site]["scope"]) for site in sites]
    spent_names = {d for k in set(reading.ordinary) - reading.opens.keys() for d in stars[k]}
    assert not scopes[0] & scopes[1] and set.union(*scopes) <= spent_names
    assert all(set(bits).isdisjoint(spent_names) and bits for bits in reading.opens.values())
    # The spent gate supports are disjoint. The two isolated-control
    # bridge supports can agree on their one common name. Live originals
    # can then complete their own rows using a private name.
    gate_holders = {k for gate in reading.gates.values() for k in gate.witnesses}
    assert all(len(set(reading.owners[d]) & gate_holders) == 1 for k in gate_holders for d in stars[k])
    assert all(len(set(reading.owners[d]) & reading.opens.keys()) == 1 for k in gate_holders for d in stars[k])
    return {"gate_relations": measurements, "two_gate_joint_row_count_by_product": prod(
        len(measurements[site]["allowed_words_lsb_first"]) for site in sites)}


def gate_records(reading, cuts):
    result = {}
    label_of = {k: role for role, k in reading.roles.items()}
    first = cuts[0]["births"]
    for site, gate in sorted(reading.gates.items()):
        record = {"mode": gate.mode, "original_donor_roles": sorted(label_of[k] for k in gate.terminals),
                  "original_donors": gate.terminals, "witness_ids": gate.witnesses}
        if first:
            local = [b for b in first if len(b["parents"]) > 1 and set(b["parents"]) <= set(gate.terminals)]
            assert len(local) == (3 if gate.mode == "C" else 1)
            record["first_births"] = local
            if site not in ("left", "right"):
                ends = {reading.roles[f"c{i}"] for i in (int(site), int(site) + 1)}
                physical, = (b for b in local if ends <= set(b["parents"]))
                record["spine_crossing"] = physical
        result[site] = record
    return result


def physical_case(case, seeds):
    p = prepare(case)
    stars = p.immutable()
    reading = read_original(stars)
    label_of = {h: name for name, h in reading.roles.items()}
    assert reading.roles == {name: p.role_id[name] for name in reading.roles}
    mode_order = ("left", "right") if case.supply is not None else tuple(map(str, SITES))
    assert {site: gate.mode for site, gate in reading.gates.items()} == dict(zip(mode_order, case.modes))
    if case.supply is None:
        assert all(len(bits) == reading.candidate.degree(k) for k, bits in reading.opens.items())
    else:
        assert all(len(bits) == (case.supply if label_of[k] == "p" else 2) for k, bits in reading.opens.items())
    old = joint()
    measured = {}
    for law in LAWS:
        projections = old.prior().projections(stars, 0, law)
        fore = [ordinary_forecast(stars, law)]
        current = stars
        cuts = []
        for age in (1, 2):
            current, cut = old.literal_cut(current, law, age)
            cuts.append(cut)
            if cut["status"] != "extend" or cut["implied"]:
                break
            fore.append(ordinary_forecast(current, law))
        complete = len(cuts) == 2 and all(cut["status"] == "extend" and not cut["implied"] for cut in cuts)
        detail = {"initial_projections": projections, "cuts": cuts, "forecast_at_reached_cuts": fore,
                  "gates": gate_records(reading, cuts),
                  **relations(stars, reading, law)}
        if case.modes:
            detail["shared_donor"] = crossings(reading, cuts, fore)
        if complete:
            detail["recodings"] = [test_recoding(current, stars, 2, reading, cuts, law, seed) for seed in seeds]
        measured[law] = detail
    for l, r in zip(measured["parity"]["cuts"], measured["nae"]["cuts"], strict=True):
        assert l["status"] == r["status"] and l["shortages"] == r["shortages"]
        names = ("holder", "parents", "consumed_names", "fresh_names", "demand")
        assert [[b[k] for k in names] for b in l["births"]] == [[b[k] for k in names] for b in r["births"]]
    pairs = sorted(tuple(sorted((label_of[a], label_of[b]))) for a, b in reading.candidate.edges)
    clock = {k for name, k in reading.roles.items() if name.startswith(("R.", "S."))}
    return {
        "case": case.label, "middle": case.middle, "modes": case.modes, "isolated_supply": case.supply,
        "original_stars": stars, "clock_holdings": reading.clock_holdings, "candidate_pairs": pairs,
        "candidate_route": reading.route, "c_spine": reading.third_spine,
        "original_distinctions": len(reading.owners),
        "live_roles": {name: k for name, k in reading.roles.items() if k in reading.opens},
        "original_loose": {label_of[k]: bits for k, bits in reading.opens.items()},
        "spent_arities": sorted(Counter(len(stars[k]) for k in set(reading.ordinary) - reading.opens.keys()).items()),
        "clock_prefix": old.clock_prefix(measured["parity"]["cuts"], clock),
        "laws": measured,
    }


def checks(rows):
    old = joint()
    with gzip.open(old.PRIOR_RECEIPT, "rt", encoding="utf-8") as source:
        archive = {r["variant"]: r for r in json.load(source)["cases"] if r["d"] == 32}
    clock = [r for r in rows if r["middle"] != "isolated"]
    assert all(r["clock_holdings"] == clock[0]["clock_holdings"] and r["clock_prefix"] == clock[0]["clock_prefix"]
               for r in clock)
    clock_by_case = {(r["middle"], r["modes"]): r for r in clock}
    for kind in ("active", "rewired"):
        base = clock_by_case[kind, ""]
        assert base["original_stars"] == tuple(map(tuple, archive[kind]["original_stars"]))
        changed = [r for r in clock if r["middle"] == kind and r["modes"]]
        assert all(r["candidate_pairs"] == changed[0]["candidate_pairs"] for r in changed)
        assert all(r["original_distinctions"] == changed[0]["original_distinctions"] for r in changed)
        assert all(r["live_roles"] == changed[0]["live_roles"] and r["original_loose"] == changed[0]["original_loose"]
                   for r in changed)
        holders = changed[0]["live_roles"].values()
        assert all(all(r["original_stars"][k] == changed[0]["original_stars"][k] for k in holders) for r in changed)
        for s_count in range(5):
            comparable = [r["spent_arities"] for r in changed if r["modes"].count("S") == s_count]
            assert all(row == comparable[0] for row in comparable)
    for r in clock:
        if r["middle"] == "active":
            other = clock_by_case["rewired", r["modes"]]
            assert r["live_roles"] == other["live_roles"] and r["original_loose"] == other["original_loose"]
            diff = {i for i, (x, y) in enumerate(zip(r["original_stars"], other["original_stars"], strict=True)) if x != y}
            assert diff == {94, 237}
    for supply in range(1, 5):
        iso = [r for r in rows if r["isolated_supply"] == supply]
        assert all(r["candidate_pairs"] == iso[0]["candidate_pairs"] and
                   r["original_stars"][:8] == iso[0]["original_stars"][:8] and
                   r["original_loose"] == iso[0]["original_loose"] for r in iso)
    return {"matched_clock_originals": len(clock[0]["clock_holdings"]),
            "matched_clock_roster_sizes": [len(row) for row in clock[0]["clock_prefix"]],
            "active_to_finite_changed_witness_ids": [94, 237],
            "shortest_candidate_meetings_a_to_b": len(clock[0]["candidate_route"]) - 1}


def interaction(rows, law, adjacent):
    by_case = {(r["middle"], r["modes"]): r["laws"][law] for r in rows
               if r["middle"] != "isolated" and r["modes"]}
    contrasts = {}
    for kind in ("active", "rewired"):
        for compensation in ("CC", "CS", "SC", "SS"):
            summary = {}
            for main in ("CC", "CS", "SC", "SS"):
                detail = by_case[kind, main + compensation if adjacent else compensation + main]
                row = detail["shared_donor"]
                actual = row["actual_through_births"]
                payments = detail["cuts"][0]["payments"].values()
                summary[main] = {
                    "shared_multi": row["initial_proposed"]["multi_charge"],
                    "shared_unary": row["initial_paid"]["unary"],
                    "whole_source_multi": sum(p["multi"] for p in payments),
                    "whole_source_unary": sum(p["unary"] for p in payments),
                    "left_first_grant": row["gate_inputs"][0]["grant"],
                    "right_first_grant": row["gate_inputs"][1]["grant"],
                    "site_23_first_grant": detail["gates"]["23"]["spine_crossing"]["grant"],
                    "site_25_first_grant": detail["gates"]["25"]["spine_crossing"]["grant"],
                    "through_grant": actual[0]["grant"] if len(actual) == 1 else None,
                }
            differences = {}
            for var in summary["SS"]:
                four = [summary[m][var] for m in ("CC", "CS", "SC", "SS")]
                differences[var] = None if None in four else four[3] - four[2] - four[1] + four[0]
            contrasts[kind + "|" + compensation] = {"modes": summary, "SS_minus_SC_minus_CS_plus_CC": differences}
    return contrasts


def source_hashes():
    manifest = HERE / "contract.json"
    contract = json.loads(manifest.read_bytes())
    inputs = [manifest, Path(__file__).resolve(), JOINT, joint().PRIOR, joint().PRIOR_RECEIPT,
              joint().prior().FIXTURES, joint().prior().END_OPERATOR]
    if "preregistration" in contract:
        inputs.append(ROOT / contract["preregistration"])
    verified = {HERE.parents[2] / "research" / HERE.parent.name / name: digest
                for name, digest in contract.get("scientific_design_sha256", {}).items()}
    if "advisor_receipt" in contract:
        verified[ROOT / contract["advisor_receipt"]] = contract["advisor_sha256"]
    for path, digest in verified.items():
        assert sha256(path.read_bytes()).hexdigest() == digest
    return {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in [*inputs, *verified]}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    sources = source_hashes()
    rows = [physical_case(case, tuple(seed + i for seed in RNG_SEEDS)) for i, case in enumerate(cases())]
    receipt = {"schema": "b278-physical-v1", "cases": rows, "matches": checks(rows),
               "interaction": {law: {"shared": interaction(rows, law, adjacent=True),
                                     "disjoint": interaction(rows, law, adjacent=False)} for law in LAWS},
               "literal_cap": CAP, "bound_source_hashes": sources}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as out, gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as compressed:
        with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as payload:
            json.dump(receipt, payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            payload.write("\n")
    print(sha256(args.output.read_bytes()).hexdigest(), args.output)


if __name__ == "__main__":
    main()
