"""Check paid ordinary cuts, physical roles and state projections for B277."""

from argparse import ArgumentParser
from collections import Counter
from contextlib import contextmanager
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
PRIOR_SCOPE = "SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001B"
PRIOR_BUNDLE = PRIOR_SCOPE + "-E001_ticks"
PRIOR = ROOT / "experiments" / PRIOR_SCOPE / PRIOR_BUNDLE / "physical.py"
PRIOR_RECEIPT = ROOT / "artifacts" / PRIOR_SCOPE / PRIOR_BUNDLE / "physical.json.gz"
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "physical.json.gz"
CAP = 8192
LAWS = ("parity", "nae")
RENAME_SEEDS = (20261121037, 20261121137)


@cache
def prior():
    spec = spec_from_file_location("b277_b259_originals", PRIOR)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Case:
    middle: str
    panel: str
    gates: tuple[tuple[int, str], ...] = ()
    reserve: int | None = None

    @property
    def identity(self):
        mode = "".join(mode for _, mode in self.gates)
        reserve = f"_c{self.reserve}" if self.reserve is not None else ""
        return f"{self.middle}_{self.panel}{mode}{reserve}"


def panel():
    result = []
    for middle in ("active", "rewired"):
        result.append(Case(middle, "archive"))
        result.extend(Case(middle, "single", ((15, mode),)) for mode in "CS")
        result.extend(Case(middle, "pair", ((20, a), (24, b))) for a in "CS" for b in "CS")
        result.extend(Case(middle, "reserve", ((15, mode),), reserve)
                      for mode in "CS" for reserve in (17, 54))
    result.extend(Case("isolated", "calibration", ((0, mode),)) for mode in "CS")
    return result


def install_gate(p, labels, witness, mode, original):
    terminal_ids = tuple(p.role_id[name] for name in labels)
    old_witness = set(p.stars[witness])
    bundles = []
    for index, knot in enumerate(terminal_ids):
        bundle = sorted(set(p.stars[knot]) & old_witness)
        start = p.new_name
        for _ in range(4 - len(bundle)):
            p.new_distinction(knot)
        bundle.extend(range(start, p.new_name))
        assert len(bundle) == 4
        bundles.append(bundle)
        for _ in range(1 if original and index < 2 else 2):
            p.new_distinction(knot)
    u, v, w = bundles
    if mode == "C":
        p.stars[witness] = u + v + w
    else:
        assert mode == "S"
        p.stars[witness] = u[:2] + v[:2]
        p.stars[p.holder(f"witness {labels[0]} with {labels[2]}")] = u[2:] + w[:2]
        p.stars[p.holder(f"witness {labels[1]} with {labels[2]}")] = v[2:] + w[2:]


def prepare(case):
    if case.middle == "isolated":
        p = prior().Preparation([], {}, {})
        u, _, _, z, x, y = [p.holder(role) for role in ("u", "v", "w", "z", "X", "Y")]
        for _ in range(2):
            p.new_distinction(u, x)
            p.new_distinction(y, z)
            p.new_distinction(z)
        p.new_distinction(x, y)
        place = p.holder("witness isolated donor group")
        install_gate(p, ("u", "v", "w"), place, case.gates[0][1], original=False)
        return p
    p, _ = prior().build(case.middle)
    for site, _ in case.gates:
        p.holder(f"w{site}")
    for site, mode in case.gates:
        u, v = f"c{site}", f"c{site + 1}"
        install_gate(p, (u, v, f"w{site}"), p.arc_witness[u, v], mode, original=True)
    if case.reserve is not None:
        for _ in range(2):
            p.new_distinction(p.role_id[f"c{case.reserve}"])
    return p


@dataclass
class Gate:
    mode: str
    terminals: tuple[int, ...]
    witnesses: tuple[int, ...]


@dataclass
class Reading:
    owners: dict
    ordinary: nx.Graph
    opens: dict
    candidate: nx.Graph
    roles: dict[str, int]
    clock_holdings: dict
    gates: dict[str, Gate]
    candidate_route: tuple[str, ...]


def read_original(stars):
    f = prior().fixture()
    owners, ordinary, loose = f.incidence(stars)
    blocks, candidate = f.witnessed_end(ordinary, loose)
    assert nx.is_connected(ordinary)
    assert all(n == 1 for n in Counter(tuple(sorted(p)) for row in blocks for p in combinations(row, 2)).values())
    meetings = Counter(tuple(sorted(at)) for at in owners.values() if len(at) == 2)
    arcs, split = nx.DiGraph(), nx.Graph()
    gates, pair_witness = [], {}
    for holder in sorted(set(ordinary) - loose.keys()):
        terminals = sorted(set(ordinary[holder]) & loose.keys())
        counts = tuple(meetings[tuple(sorted((holder, p)))] for p in terminals)
        if len(terminals) <= 1:
            continue
        if counts == (4, 4, 4):
            gates.append(Gate("C", tuple(terminals), (holder,)))
        elif counts == (2, 2):
            split.add_edge(*terminals, witness=holder)
        else:
            assert len(terminals) == 2 and min(counts) == 1 and max(counts) in (2, 3, 4)
            tail, head = terminals if counts[0] == 1 else tuple(reversed(terminals))
            arcs.add_edge(tail, head, multiplicity=max(counts))
            pair_witness[tail, head] = holder
    for component in nx.connected_components(split):
        subgraph = split.subgraph(component)
        assert len(component) == 3 and len(subgraph.edges) == 3
        gates.append(Gate("S", tuple(sorted(component)), tuple(sorted(w for _, _, w in subgraph.edges(data="witness")))))

    if len(loose) == 4:
        gate, = gates
        z, = set(loose) - set(gate.terminals)
        u, = (holder for holder in gate.terminals if nx.shortest_path_length(ordinary, z, holder) == 3)
        z, y, x, u = nx.shortest_path(ordinary, z, u)
        v, w = sorted(set(gate.terminals) - {u})
        roles = dict(u=u, v=v, w=w, z=z, X=x, Y=y)
        assert [meetings[tuple(sorted(p))] for p in ((u, x), (x, y), (y, z))] == [2, 1, 2]
        assert len(loose[z]) == 2 and not candidate.degree(z)
        assert set(map(frozenset, candidate.edges)) == set(map(frozenset, combinations(gate.terminals, 2)))
        return Reading(owners, ordinary, loose, candidate, roles, {}, {"isolated": gate}, ())

    w_by_pair = {}
    for gate in gates:
        third, = set(gate.terminals) - set(arcs)
        ends = set(gate.terminals) - {third}
        u, = (p for p in ends if arcs.in_degree(p) == 1 and arcs.out_degree(p) == 0)
        v, = (p for p in ends if arcs.in_degree(p) == 0 and arcs.out_degree(p) == 1)
        arcs.add_edge(u, v, multiplicity=2)
        w_by_pair[u, v] = third, gate
    scaffold = prior().PhysicalReading(arcs, pair_witness, loose)
    frames = prior().decode_frames(scaffold)
    middle, _ = prior().decode_connectors(scaffold, frames)
    roles = frames | middle
    labels = {k: v for v, k in roles.items()}
    gate_names = {}
    for (u, v), (w, gate) in w_by_pair.items():
        site = int(labels[u][1:])
        assert labels[v] == f"c{site + 1}"
        roles[f"w{site}"] = w
        gate_names[str(site)] = gate
    assert set(roles.values()) == set(loose)
    labels = {k: v for v, k in roles.items()}
    mid = candidate.subgraph(set(loose) - set(frames.values()))
    route, = nx.all_shortest_paths(mid, roles["a"], roles["b"])
    assert len(route) == 35
    core = {str(k): v for k, v in prior().stable_origins(stars, scaffold, frames).items()}
    return Reading(owners, ordinary, loose, candidate, roles, core, gate_names, tuple(labels[k] for k in route))


@contextmanager
def projector(stars, law):
    f = prior().fixture()
    if law == "parity":
        yield lambda scope: f.parity_words(stars, scope)
    else:
        with f.Minisat22() as solver:
            for row in stars:
                f.nae_add(solver, row)
            yield lambda scope: f.nae_words(solver, scope)


def joint_relation(stars, law, reading, gate):
    labels = {k: v for v, k in reading.roles.items()}
    by_terminal = {labels[p]: sorted(d for d in stars[p] if set(reading.owners[d]) & set(gate.witnesses))
                   for p in gate.terminals}
    assert sorted(map(len, by_terminal.values())) == [4, 4, 4]
    scope = tuple(d for label in sorted(by_terminal) for d in by_terminal[label])
    with projector(stars, law) as project:
        words = project(scope)
    assert 0 < len(words) < 1 << len(scope)
    single_erasure = [len({w & ~(1 << i) for w in words}) for i in range(len(scope))]
    terminal_erasure = {}
    for name, bits in by_terminal.items():
        mask = sum(1 << scope.index(d) for d in bits)
        terminal_erasure[name] = len({w & ~mask for w in words})
    if gate.mode == "C":
        assert len(words) == (2048 if law == "parity" else 4094)
        assert set(single_erasure) == {2048} and set(terminal_erasure.values()) == {256}
    else:
        assert len(words) == (512 if law == "parity" else 2744)
        assert set(single_erasure) == ({512} if law == "parity" else {1568})
        assert set(terminal_erasure.values()) == ({128} if law == "parity" else {224})
    return {"scope": scope, "terminal_names": by_terminal, "allowed_words_lsb_first": words,
            "K1": True, "K2": min(single_erasure) == 2048, "K3": True,
            "one_name_erased_row_counts_out_of_2048": single_erasure,
            "donor_erased_row_counts_out_of_256": terminal_erasure}


def literal_cut(stars, law, age):
    f = prior().fixture()
    owners, ordinary, loose = f.incidence(stars)
    blocks, graph = f.witnessed_end(ordinary, loose)
    turn = f.step(f.from_stars(stars), law, max_births=CAP)
    multi = f.multi_groups(blocks, graph)
    use = Counter(k for parents in multi for k in parents)
    shared = Counter(tuple(sorted(pair)) for block in blocks for pair in combinations(block, 2))
    assert set(shared) == set(tuple(sorted(pair)) for pair in graph.edges)
    shortages = tuple(sorted((k, n - len(loose[k])) for k, n in use.items() if n > len(loose[k])))
    bound = {"source_cut": age - 1, "ordinary_connected": nx.is_connected(ordinary),
             "S0_funded": not shortages and bool(loose), "S3_no_unheld_multi": not any(len(row) >= 3 for row in multi),
             "S4_unique_witness": max(shared.values(), default=0) <= 1,
             "loose_count": sum(map(len, loose.values())), "at_least_two_loose": sum(map(len, loose.values())) >= 2,
             "unheld_multi_groups": [row for row in multi if len(row) >= 3]}
    result = {"age": age, "status": turn.status, "shortages": shortages, "implied": turn.implied,
              "source_diagnostics": bound, "births": [], "planned_births_lower": turn.planned_births_lower}
    if turn.status != "extend":
        assert turn.status != "stall" or turn.shortages == shortages
        return stars, result
    assert not shortages
    status, births, literal_multi = f.literal_turn(stars, law)
    assert status == "extend" and literal_multi == multi
    next_stars = stars + tuple(b.support for b in births)
    grant_names = [d for b in births for d in b.fresh]
    assert len(grant_names) == len(set(grant_names)) and not set(grant_names) & owners.keys()
    paid = {k: [] for k in loose}
    inputs = {}
    with projector(stars, law) as project:
        for b in births:
            for holder, name in zip(b.parents, b.inputs, strict=True):
                assert owners[name] == [holder]
                paid[holder].append(name)
            rows = project(b.inputs)
            if law == "parity" and turn.implied:
                assert rows == f.expected_words(law, len(b.inputs))
            elif law == "parity":
                assert len(rows) == 1 << len(b.inputs)
            inputs[b.knot] = {"allowed_rows": rows, "all_input_words": len(rows) == 1 << len(b.inputs)}
    assert {k: sorted(bits) for k, bits in paid.items()} == loose
    _, _, evolved_loose = f.incidence(next_stars)
    assert evolved_loose == {b.knot: list(b.fresh) for b in births if b.fresh}
    result.update({
        "births": [{"holder": b.knot, "parents": b.parents, "consumed_names": b.inputs, "fresh_names": b.fresh,
                    "demand": demand, "grant": len(b.fresh), "arity": len(b.support), **inputs[b.knot]}
                   for b, demand in zip(births, turn.demand, strict=True)],
        "payments": {str(k): {"supply": len(bits), "multi": use[k], "unary": len(bits) - use[k],
                              "available_names": bits, "used_names": paid[k]}
                     for k, bits in loose.items()},
        "outputs": prior().projections(next_stars, age, law),
    })
    return next_stars, result


def local_gate_checks(cuts, reading, gate, exact_pair):
    terminal_set = set(gate.terminals)
    own = [b for b in cuts[0]["births"] if set(b["parents"]) <= terminal_set]
    expected = list(combinations(gate.terminals, 2)) if gate.mode == "C" else [
        gate.terminals, *((donor,) for donor in gate.terminals)]
    assert {tuple(sorted(b["parents"])) for b in own} == {tuple(sorted(row)) for row in expected}
    target, = (b for b in own if set(exact_pair) <= set(b["parents"]))
    assert target["all_input_words"]
    if gate.mode == "S":
        assert len(target["parents"]) == 3 and target["arity"] == 3 + target["grant"]
    area = {b["holder"] for b in own}
    following = [b for b in cuts[1]["births"] if area & set(b["parents"])]
    first_unheld = [group for group in cuts[1]["source_diagnostics"]["unheld_multi_groups"]
                    if set(group) <= area]
    assert len(first_unheld) == int(gate.mode == "C")
    return {"mode": gate.mode, "terminals": gate.terminals, "witnesses": gate.witnesses, "crossing": target,
            "first_local_births": own, "second_births_using_first_local": following,
            "first_cut_unheld_groups_on_these_births": first_unheld,
            "initial_terminal_payments": {str(p): cuts[0]["payments"][str(p)] for p in gate.terminals}}


def check_recoding(stars, reading, n, cuts, law, seed):
    f = prior().fixture()
    renamed, given = f.rename(stars, seed)
    originals, parents, _, depth = f.peel(renamed, law)
    assert depth == 2
    old_recoded = sorted(originals)
    original_map = [given[k] for k in old_recoded]
    assert set(original_map) == set(range(n))
    restored = read_original(tuple(renamed[k] for k in old_recoded))
    observed = {role: original_map[k] for role, k in restored.roles.items()}
    if "z" in restored.roles:
        assert {observed[k] for k in ("v", "w")} == {reading.roles[k] for k in ("v", "w")}
        observed.update({k: reading.roles[k] for k in ("v", "w")})
    assert observed == reading.roles
    for site, gate in restored.gates.items():
        original = reading.gates[site]
        assert gate.mode == original.mode
        assert {original_map[k] for k in gate.terminals} == set(original.terminals)
        assert {original_map[k] for k in gate.witnesses} == set(original.witnesses)
    actual = {b["holder"]: frozenset(b["parents"]) for cut in cuts for b in cut["births"]}
    assert {given[k]: frozenset(given[p] for p in row) for k, row in parents.items()} == actual
    return {"seed": seed, "depth": depth, "recoded_holder_to_original": given,
            "recovered_original_indices": old_recoded, "recovered_actual_parent_lists": len(actual),
            "recoded_full_stars": renamed}


def clock_prefix(cuts, clock_live):
    first = {b["holder"]: b for b in cuts[0]["births"] if set(b["parents"]) <= clock_live}
    first_rows = [(b["parents"], b["consumed_names"], b["grant"]) for b in first.values()]
    second = [] if len(cuts) < 2 else [
        (sorted(first[p]["parents"] for p in b["parents"]), b["grant"])
        for b in cuts[1]["births"] if set(b["parents"]) <= first.keys()
    ]
    return sorted(first_rows), sorted(second)


def run_case(case, seeds):
    p = prepare(case)
    source = p.immutable()
    read = read_original(source)
    labels = {k: v for v, k in read.roles.items()}
    if case.middle == "isolated":
        assert len(read.gates) == 1
        assert min(map(len, read.opens.values())) == 2
    else:
        assert all(p.role_id[label] == k for label, k in read.roles.items())
        expected_gates = {str(site): mode for site, mode in case.gates}
        assert {site: gate.mode for site, gate in read.gates.items()} == expected_gates
        assert all(len(bits) == read.candidate.degree(k) + (2 if labels[k] == f"c{case.reserve}" else 0)
                   for k, bits in read.opens.items())
    by_law = {}
    for law in LAWS:
        projections = prior().projections(source, 0, law)
        current = source
        cuts = []
        for age in (1, 2):
            current, cut = literal_cut(current, law, age)
            cuts.append(cut)
            if cut["status"] != "extend" or cut["implied"]:
                break
        complete = len(cuts) == 2 and all(cut["status"] == "extend" and not cut["implied"] for cut in cuts)
        item = {"initial_projections": projections, "cuts": cuts, "gate_relations": {}}
        for site, gate in read.gates.items():
            exact_pair = (read.roles["u"], read.roles["v"]) if site == "isolated" else (
                read.roles[f"c{site}"], read.roles[f"c{int(site) + 1}"])
            g = joint_relation(source, law, read, gate)
            if complete:
                g["rosters"] = local_gate_checks(cuts, read, gate, exact_pair)
            item["gate_relations"][site] = g
        if complete:
            item["recodings"] = [check_recoding(current, read, len(source), cuts, law, seed) for seed in seeds]
        by_law[law] = item
    for parity_cut, nae_cut in zip(by_law["parity"]["cuts"], by_law["nae"]["cuts"], strict=True):
        assert parity_cut["status"] == nae_cut["status"]
        assert parity_cut["payments"] == nae_cut["payments"]
        names = ("holder", "parents", "consumed_names", "fresh_names", "demand")
        assert [[b[k] for k in names] for b in parity_cut["births"]] == [
            [b[k] for k in names] for b in nae_cut["births"]
        ]
    candidate_pairs = sorted(tuple(sorted((labels[a], labels[b]))) for a, b in read.candidate.edges)
    clock_live = {k for k, label in labels.items() if label.startswith(("R.", "S."))}
    return {"case": case.identity, "middle": case.middle, "panel": case.panel, "gates": dict(case.gates),
            "reserve": case.reserve, "physical_originals": len(source), "original_distinctions": len(read.owners),
            "original_stars": source, "live_roles": {label: k for label, k in read.roles.items() if k in read.opens},
            "original_loose": {labels[k]: bits for k, bits in read.opens.items()},
            "candidate_pairs": candidate_pairs, "shortest_candidate_route": read.candidate_route,
            "clock_holdings": read.clock_holdings,
            "clock_prefix": clock_prefix(by_law["parity"]["cuts"], clock_live),
            "spent_arities": sorted(Counter(len(source[h]) for h in set(range(len(source))) - read.opens.keys()).items()),
            "laws": by_law}


def check_matches(cases):
    clock = [row for row in cases if row["middle"] != "isolated"]
    assert all(row["clock_holdings"] == clock[0]["clock_holdings"] and
               row["clock_prefix"] == clock[0]["clock_prefix"] for row in clock)
    cal_c, cal_s = (row for row in cases if row["middle"] == "isolated")
    assert cal_c["live_roles"] == cal_s["live_roles"]
    assert cal_c["original_loose"] == cal_s["original_loose"]
    assert cal_c["candidate_pairs"] == cal_s["candidate_pairs"]
    assert cal_c["original_stars"][:6] == cal_s["original_stars"][:6]
    keyed = {(r["middle"], r["panel"], tuple(r["gates"].values()), r["reserve"]): r for r in clock}
    reference = {r["middle"]: r for r in clock if r["panel"] == "archive"}
    with gzip.open(PRIOR_RECEIPT, "rt", encoding="utf-8") as receipt:
        archive = {r["variant"]: r for r in json.load(receipt)["cases"] if r["d"] == 32}
    for middle, control in reference.items():
        assert control["original_stars"] == tuple(map(tuple, archive[middle]["original_stars"]))
        assert control["candidate_pairs"] == list(map(tuple, archive[middle]["candidate_pairs"]))

    for middle in ("active", "rewired"):
        for group in (("single", None, ("C",), ("S",)), ("reserve", 17, ("C",), ("S",)),
                      ("reserve", 54, ("C",), ("S",)), ("pair", None, ("C", "S"), ("S", "C")),
                      ("pair", None, ("C", "C"), ("S", "S"))):
            p, reserve, a, b = group
            x = keyed[middle, p, a, reserve]
            y = keyed[middle, p, b, reserve]
            assert x["live_roles"] == y["live_roles"] and x["original_loose"] == y["original_loose"]
            assert x["candidate_pairs"] == y["candidate_pairs"] and x["original_distinctions"] == y["original_distinctions"]
            assert all(x["original_stars"][i] == y["original_stars"][i] for i in x["live_roles"].values())
            if a == ("C", "S"):
                assert x["spent_arities"] == y["spent_arities"]
        for mode in "CS":
            x, y = [keyed[middle, "reserve", (mode,), site] for site in (17, 54)]
            left = set(x["original_loose"]["c17"]) - set(y["original_loose"]["c17"])
            right = set(y["original_loose"]["c54"]) - set(x["original_loose"]["c54"])
            assert left == right and len(left) == 2
            assert x["candidate_pairs"] == y["candidate_pairs"]
            assert all(tuple(d for d in x["original_stars"][i] if d not in left) ==
                       tuple(d for d in y["original_stars"][i] if d not in left)
                       for i in range(x["physical_originals"]))
    for row in clock:
        if row["middle"] == "active":
            others = keyed["rewired", row["panel"], tuple(row["gates"].values()), row["reserve"]]
            assert row["live_roles"] == others["live_roles"]
            assert row["original_loose"] == others["original_loose"]
            changed = {i for i, (a, b) in enumerate(zip(row["original_stars"], others["original_stars"], strict=True))
                       if a != b}
            assert changed == {94, 237}
    return {"identical_clock_holdings": len(clock[0]["clock_holdings"]),
            "common_clock_first_births": len(clock[0]["clock_prefix"][0]),
            "common_clock_second_births": len(clock[0]["clock_prefix"][1]),
            "middle_route_meetings": len(clock[0]["shortest_candidate_route"]) - 1,
            "active_rewired_changed_witness_ids": [94, 237],
            "transfer_sites": ["c17", "c54"], "reserve_names": 2}


def input_hashes():
    contract = HERE / "contract.json"
    manifest = json.loads(contract.read_bytes())
    scope = ROOT / manifest["preregistration"]
    exact = {scope.with_name(name): digest for name, digest in manifest["scientific_design_sha256"].items()}
    exact[ROOT / manifest["advisor_receipt"]] = manifest["advisor_sha256"]
    for path, digest in exact.items():
        assert sha256(path.read_bytes()).hexdigest() == digest
    paths = [Path(__file__).resolve(), PRIOR, PRIOR_RECEIPT, prior().FIXTURES, prior().END_OPERATOR, contract, scope, *exact]
    return {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in paths}


def law_totals(cases, law):
    measurements = [r["laws"][law] for r in cases]
    cuts = [cut for r in measurements for cut in r["cuts"]]
    births = [b for cut in cuts for b in cut["births"]]
    return {
        "statuses": dict(Counter(cut["status"] for cut in cuts)),
        "implied_cuts": sum(cut["implied"] for cut in cuts),
        "births": len(births), "max_births_in_one_cut": max(len(cut["births"]) for cut in cuts),
        "unconstrained_input_scopes": sum(b["all_input_words"] for b in births),
        "physical_recodings": sum(len(r.get("recodings", ())) for r in measurements),
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    hashes = input_hashes()
    cases = [run_case(case, tuple(s + i for s in RENAME_SEEDS)) for i, case in enumerate(panel())]
    receipt = {"schema": "b277-physical-v1", "source_hashes": hashes, "cases": cases,
               "law_codes": LAWS, "literal_cut_cap": CAP, "literal_horizon": 2, "matches": check_matches(cases),
               "law_totals": {law: law_totals(cases, law) for law in LAWS}}
    args.output.parent.mkdir(exist_ok=True, parents=True)
    with args.output.open("wb") as out, gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as compressed:
        with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as payload:
            json.dump(receipt, payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            payload.write("\n")
    print(sha256(args.output.read_bytes()).hexdigest(), args.output)


if __name__ == "__main__":
    main()
