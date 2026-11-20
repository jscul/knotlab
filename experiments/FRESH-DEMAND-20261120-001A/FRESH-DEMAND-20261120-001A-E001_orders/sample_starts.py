"""Frozen tree sample for fresh demand under complete and present-state growth."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
import random
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "sample.json"
DESIGN = ROOT / "research/FRESH-DEMAND-20261120-001/preregistration.md"
TREE_SEED = 20261120471
TARGET_SEED = 20261120472
ORDER_SEED = 20261120473
DRAWS_PER_SIZE = 64
MAX_EVENTS = 12
LAWS = ("parity", "nae")
POLICIES = ("uniform", "joins-first")
AGE_ONE_READERS = ("parents", "parents_and_steps", "input_bond", "parents_and_input_bond",
                   "all_parent_bond_distances", "shared_parent")


def load(name, path):
    spec = spec_from_file_location(name, ROOT / "experiments" / path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@cache
def libraries():
    nae = load("fresh_sample_nae", "NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py")
    serial = load("fresh_sample_serial", "ROUND-FREE-20261119-001B/ROUND-FREE-20261119-001B-E001_serial/serial.py")
    source = load("fresh_sample_source", "ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/source_cert.py")
    return nae, serial, source


def draw_sources():
    rng = random.Random(TREE_SEED)
    for n in range(4, 9):
        for i in range(DRAWS_PER_SIZE):
            prufer = [rng.randrange(n) for _ in range(n - 2)]
            tree = nx.from_prufer_sequence(prufer)
            meetings = tuple(sorted(tuple(sorted(edge)) for edge in tree.edges))
            spare = [int(rng.randrange(4) == 0) for _ in range(n)]
            sizes = [max(3, tree.degree(v)) + spare[v] for v in range(n)]
            yield f"{n}/{i:02d}", prufer, spare, sizes, meetings


@cache
def knot_check(width, allowed):
    sys.path.insert(0, str(ROOT / "tools"))
    from knotlab.knots import check_knot
    from knotlab.relations import Relation

    names = tuple(f"d{i}" for i in range(width))
    rows = frozenset(tuple(bool(word >> i & 1) for i in range(width)) for word in allowed)
    return check_knot(Relation(names, rows), names[:-1], names[-1]).is_knot


def source_lawfulness(presentation):
    nae, _, checker = libraries()
    stars = presentation.bits_of
    rows = checker.row_masks(stars)
    projections = dict.fromkeys(LAWS)
    with nae._solver(presentation, len(stars)) as solver:
        for law in LAWS:
            probes = []
            for star in stars:
                width = len(star)
                if width < 3:
                    probes.append({"arity": width, "K1_K2_K3": False})
                    continue
                if law == "parity":
                    observed, _ = checker.parity_read(rows, star)
                    expected = [w for w in range(1 << width) if w.bit_count() % 2 == 0]
                else:
                    observed, _ = checker.nae_read(solver, stars, star)
                    expected = list(range(1, (1 << width) - 1))
                probes.append({"arity": width, "states": len(observed),
                               "K1_K2_K3": observed == expected and knot_check(width, tuple(observed))})
            projections[law] = {"lawful": all(row["K1_K2_K3"] for row in probes), "knots": probes}
    return projections


def connected(vertices, neighbors):
    reached = {min(vertices)}
    pending = list(reached)
    for v in pending:
        add = (neighbors[v] & vertices) - reached
        reached.update(add)
        pending.extend(add)
    return reached == vertices


def minimal_nonzero(supports):
    minimal = []
    for support in sorted(set(supports) - {0}, key=lambda mask: (mask.bit_count(), mask)):
        if not any(support & b == b for b in minimal):
            minimal.append(support)
    return set(minimal)


def tree_bonds(presentation):
    """Enumerate connected holder cuts and independently compare GF(2) support minima."""
    _, _, checker = libraries()
    stars = presentation.bits_of
    row_masks = checker.row_masks(stars)
    support_to_holders = {}
    span = [0] * (1 << len(stars))
    for subset in range(1, len(span)):
        bit = subset & -subset
        span[subset] = span[subset ^ bit] ^ row_masks[bit.bit_length() - 1]
        region = {v for v in range(len(stars)) if subset >> v & 1}
        if not connected(region, presentation.nbr):
            continue
        # Count distinction incidences literally on both sides of the cut.
        boundary = checker.mask(d for d, holders in presentation.owner.items()
                                if sum(v in region for v in holders) == 1)
        assert boundary == span[subset] and boundary not in support_to_holders
        support_to_holders[boundary] = sorted(region)
    assert minimal_nonzero(span) == set(support_to_holders)
    return support_to_holders


def literal_minima(presentation, law):
    """Only used on fixed tiny controls. Enumerate states and all distinct projections."""
    _, _, checker = libraries()
    rows = checker.row_masks(presentation.bits_of)
    extent = 1 << presentation.nbits
    assert extent <= 8192
    if law == "parity":
        models = [word for word in range(extent) if all((word & s).bit_count() % 2 == 0 for s in rows)]
    else:
        models = [word for word in range(extent) if all(word & s not in (0, s) for s in rows)]
    bonds = []
    for support in sorted(range(1, extent), key=lambda mask: (mask.bit_count(), mask)):
        if any(support & b == b for b in bonds):
            continue
        if len({word & support for word in models}) < 1 << support.bit_count():
            bonds.append(support)
    return set(bonds)


class BondRead:
    def __init__(self, presentation):
        self.presentation = presentation
        self.regions = tree_bonds(presentation)
        self.bonds = sorted(self.regions, key=lambda mask: (mask.bit_count(), mask))
        self.resolved = {}
        self.read_supports = set()

    def minimum(self, distinctions):
        _, _, checker = libraries()
        pins = checker.mask(distinctions)
        if pins not in self.resolved:
            self.resolved[pins] = next((b for b in self.bonds if b & pins == pins), None)
        bond = self.resolved[pins]
        assert bond is not None
        self.read_supports.add(bond)
        return bond.bit_count(), bond

    def validate_nae_reads(self):
        """Verify the full literal NAE projection on each distinct chosen minimum."""
        nae, _, _ = libraries()
        p = self.presentation
        patterns = 0
        with nae._solver(p, len(p.bits_of)) as solver:
            for bond in sorted(self.read_supports):
                distinctions = [d + 1 for d in range(p.nbits) if bond >> d & 1]
                width = len(distinctions)
                patterns += 1 << width
                excluded = []
                for word in range(1 << width):
                    probe = [d if word >> i & 1 else -d for i, d in enumerate(distinctions)]
                    if not solver.solve(assumptions=probe):
                        excluded.append(word)
                # Two complementary missing words make every proper projection full.
                assert len(excluded) == 2 and excluded[0] ^ excluded[1] == (1 << width) - 1
        return {"distinct_minimum_supports": sorted(map(hex, self.read_supports)),
                "projection_patterns_queried": patterns}


class ParentBondTypes:
    """Exact isomorphism classes of marked holdings with all their pair bond sizes."""

    def __init__(self):
        self.buckets = defaultdict(list)
        self.types = []

    def add(self, presentation, parents, spent, bonds):
        details = {v: (len(presentation.bits_of[v]), len(presentation.loose(v))) for v in parents}
        distinctions = sorted({d for v in parents for d in presentation.bits_of[v]})
        allocation = set(spent)
        graph = nx.Graph()
        graph.add_nodes_from((("holder", v), {"kind": ("holder", *details[v])}) for v in parents)
        graph.add_nodes_from((("distinction", d), {"kind": ("distinction", len(presentation.owner[d]) == 1, d in allocation)})
                             for d in distinctions)
        graph.add_edges_from((("holder", v), ("distinction", d), {"value": None})
                             for v in parents for d in presentation.bits_of[v])
        sizes = [(u, v, bonds.minimum((u, v))[0]) for u, v in combinations(distinctions, 2)]
        graph.add_edges_from((("distinction", u), ("distinction", v), {"value": size}) for u, v, size in sizes)
        key = (tuple(sorted(details.values())), tuple(sorted(size for _, _, size in sizes)))
        for existing, previous in self.buckets[key]:
            match = nx.algorithms.isomorphism.GraphMatcher(graph, previous,
                        node_match=lambda a, b: a["kind"] == b["kind"],
                        edge_match=lambda a, b: a["value"] == b["value"])
            if match.is_isomorphic():
                f = match.mapping
                assert len(f) == len(set(f.values())) == len(previous) == len(graph)
                assert all(graph.nodes[u] == previous.nodes[f[u]] for u in graph)
                assert all({f[v]: values for v, values in graph[u].items()} == dict(previous[f[u]]) for u in graph)
                return existing
        code = len(self.types)
        addresses = {d: i for i, d in enumerate(distinctions)}
        self.types.append({"holdings": [[addresses[d] for d in presentation.bits_of[v]] for v in parents],
                           "chosen": sorted(addresses[d] for d in spent),
                           "loose": [addresses[d] for d in distinctions if len(presentation.owner[d]) == 1],
                           "pair_sizes": [[addresses[u], addresses[v], size] for u, v, size in sizes]})
        self.buckets[key].append((code, graph))
        return code


def funding(presentation):
    p = presentation
    live = {v for v in range(len(p.bits_of)) if p.loose(v)}
    groups = [tuple(sorted(g)) for g in p.groups_among(live)]
    # Independent tree check: every candidate pair has a unique physical holder witness.
    by_witness = Counter(pair for neighbors in p.nbr for pair in combinations(sorted(neighbors & live), 2))
    assert set(groups) == set(by_witness) and all(witnesses == 1 for witnesses in by_witness.values())
    needed = Counter(v for group in groups for v in group)
    opens = [len(p.loose(v)) for v in range(len(p.bits_of))]
    shortages = {v: needed[v] - opens[v] for v in live if needed[v] > opens[v]}
    spare = [max(0, o - needed[v]) for v, o in enumerate(opens)]
    return groups, {"live": sorted(live), "loose_by_holder": opens, "multi_uses": [needed[v] for v in range(len(opens))],
                    "shortages": shortages, "unary_slots_after_multi_obligations": spare}


def first_layer(stars, law):
    nae, _, _ = libraries()
    p = nae.S.from_junctions(stars)
    n = len(stars)
    underlying = nae.parity_rule(nae.F.fewest) if law == "parity" else nae.nae_rule(nae.F.fewest)
    received = []

    def recorded_rule(state, info, rng):
        fresh = underlying(state, info, rng)
        for item, count in zip(info, fresh, strict=True):
            consumed = state.bits_of[item["j"]][:item["p"]]
            parents = sorted(v for d in consumed for v in state.owner[d] if v < n)
            received.append({"parents": parents, "inputs": list(consumed), "demand": item["d"],
                             "fresh": count, "implied": item["implied"]})
        return fresh

    result = p.step(recorded_rule)
    status = "stall" if result is None else "no_move" if result["new"] == 0 else "formed"
    return {"status": status, "births": received}


def measure_birth(source, birth, bond_read, bond_types):
    parents, inputs = birth["parents"], birth["inputs"]
    p = len(parents)
    parent_read = sorted((len(source.bits_of[v]), len(source.loose(v))) for v in parents)
    sibling_sum = sum(loose - 1 for _, loose in parent_read)
    live = {v for v in range(len(source.bits_of)) if source.loose(v)}
    holder_steps, witnessed_steps = (0, 0) if p == 1 else (2, 1)
    witness, contenders = None, []
    if p == 2:
        u, v = parents
        common = source.nbr[u] & source.nbr[v]
        assert len(common) == 1 and v not in source.nbr[u]
        witness = next(iter(common))
        contenders = sorted((source.nbr[witness] & live) - set(parents))

    bond_size, bond_mask = bond_read.minimum(inputs)
    expected = sum(len(source.bits_of[v]) for v in parents)
    if witness is not None:
        expected += len(source.bits_of[witness]) - 4
    assert expected == bond_size
    assert bond_read.regions[bond_mask] == sorted([*parents] + ([] if witness is None else [witness]))
    bond_type = bond_types.add(source, parents, inputs, bond_read)
    clip = max(1, 3 - p)
    t = len(contenders)
    predicted_demand = sibling_sum - t
    return {"sibling_sum": sibling_sum, "t": t, "witness_holder": witness, "third_live_holders": contenders,
            "ordinary_holder_steps": holder_steps, "witnessed_steps": witnessed_steps,
            "minimum_input_bond_size": bond_size, "minimum_input_bond": hex(bond_mask),
            "predicted_demand": predicted_demand, "predicted_fresh": max(clip, predicted_demand),
            "predicted_fresh_without_t": max(clip, sibling_sum),
            "readings": {"parents": parent_read,
                         "parents_and_steps": (parent_read, holder_steps, witnessed_steps),
                         "input_bond": (p, bond_size), "parents_and_input_bond": (parent_read, bond_size),
                         "all_parent_bond_distances": bond_type, "shared_parent": (parent_read, t)}}


def exact_target(group, target):
    return tuple(group) == target


def serial_trace(stars, law, policy, target, seed):
    """Use the archived move inventory and mutation; update exact implication for NAE."""
    nae, serial, checker = libraries()
    p = serial.S.from_junctions(stars)
    children = defaultdict(set)
    rng = random.Random(seed)
    events = []
    for turn in range(MAX_EVENTS + 1):
        exhausted = [v for v in target if not p.loose(v)]
        common_children = sorted(set.intersection(*(children[v] for v in target)))
        if exhausted or common_children:
            status = "parent_exhausted" if exhausted else "already_covered_by_other_birth"
            return {"status": status, "events": events, "exhausted_parents": exhausted,
                    "prior_common_children": common_children}
        joins, unary, live = serial.moves(p, children)
        listed = [g for g in joins if exact_target(g, target)]
        pool = joins if policy == "joins-first" and joins else joins + unary
        available = bool(listed)
        if not pool:
            return {"status": "no_move", "events": events}
        if turn == MAX_EVENTS:
            return {"status": "eligible_at_cap" if available else "unavailable_at_cap", "events": events}
        if policy == "immediate":
            assert turn == 0 and available and len(listed) == 1
            group = listed[0]
        else:
            group = rng.choice(pool)

        old = len(p.bits_of)
        consumed = [p.loose(v)[0] for v in group]
        if law == "parity":
            implied = p._reduce(p._mask(consumed)) == 0
            assert implied == (sorted(consumed) == sorted(d for v in live for d in p.loose(v)))
            old_states = None if implied else 1 << len(consumed)
        else:
            implied = nae.nae_implied(p, old, consumed)
            # Verify more than the NAE implication check needed for the count.
            # An already restricted proper projection could invalidate a fresh extension.
            with nae._solver(p, old) as solver:
                observed, _ = checker.nae_read(solver, p.bits_of, consumed)
            assert implied == (0 not in observed and (1 << len(consumed)) - 1 not in observed)
            old_states = len(observed)

        child = serial.new_junction(p, consumed)
        assert child == old
        for v in group:
            children[v].add(child)
        live_next = [v for v in range(len(p.bits_of)) if p.loose(v) or v == child]
        demand = sum(child in h for h in p.groups_among(live_next))
        count = nae.F.fewest(p, [{"p": len(group), "d": demand, "implied": implied}], None)[0]
        event = {"parents": group, "inputs": consumed, "fresh": count, "demand": demand,
                 "implied": implied, "input_states": ((1 << (len(group) - 1)) if old_states is None else old_states),
                 "target_listed": available,
                 "choice_count": len(pool), "listed_multi": len(joins), "listed_unary": len(unary)}
        # Refuse a legacy closing write that cannot bind two loops and one contact.
        if len(group) + count < 3:
            return {"status": "subarity_stop", "events": events, "rejected_event": event}
        if law == "nae":
            # Full inputs before a positive fresh count, exactly NAE before a zero count.
            assert old_states == (1 << len(group)) - (0 if count else 2)
        events.append(event)
        for _ in range(count):
            d = p.nbits
            p.nbits += 1
            p.bits_of[child].append(d)
            p.owner[d] = [child]
        p.fresh[child] = count
        p._add_row(child)
        if exact_target(group, target):
            return {"status": "made", "events": events}
    raise AssertionError("the finite decision cap was not observed")


def archive_agreement(sizes, meetings, trace, policy, seed):
    """Replay the parity prefix with the archive itself, including allocation."""
    _, serial, _ = libraries()
    events = trace["events"]
    archived, _, status = serial.grow_serial(sizes, meetings, len(events), seed, policy=policy)
    assert status == "steps"
    n = len(sizes)
    assert len(archived.bits_of) == n + len(events)
    for i, event in enumerate(events, n):
        spent = event["inputs"]
        assert archived.bits_of[i][:len(spent)] == spent and archived.fresh[i] == event["fresh"]
        assert event["parents"] == tuple(sorted(min(archived.owner[d]) for d in spent))


def observe(stars, bond_types):
    nae, _, _ = libraries()
    p = nae.S.from_junctions(stars)
    lawfulness = source_lawfulness(p)
    if not all(observer["lawful"] for observer in lawfulness.values()):
        return {"lawfulness": lawfulness, "funding": {"status": "unlawful"}, "layers": {}}
    groups, funds = funding(p)
    bonds = BondRead(p)
    layers = {law: first_layer(stars, law) for law in LAWS}
    by_input = {}
    for result in layers.values():
        expected = "stall" if funds["shortages"] else "formed" if funds["live"] else "no_move"
        assert result["status"] == expected
        if result["status"] != "formed":
            assert not result["births"]
            continue
        actual = Counter(tuple(b["parents"]) for b in result["births"])
        expected_roster = Counter(groups) + Counter({(v,): n for v, n in enumerate(funds["unary_slots_after_multi_obligations"])})
        assert actual == expected_roster
        assert sorted(d for b in result["births"] for d in b["inputs"]) == sorted(d for v in funds["live"] for d in p.loose(v))
        for birth in result["births"]:
            key = tuple(birth["inputs"])
            if key not in by_input:
                by_input[key] = measure_birth(p, birth, bonds, bond_types)
                assert birth["fresh"] >= 1 and not birth["implied"]
            reading = by_input[key]
            assert (reading["predicted_demand"], reading["predicted_fresh"]) == (birth["demand"], birth["fresh"])
            birth.update(reading)
    return {"lawfulness": lawfulness, "funding": {**funds, "proposed_multi": groups}, "layers": layers,
            "bond_checks": {"connected_cut_bonds": len(bonds.bonds), **bonds.validate_nae_reads()}}


def run_draw(spec, target_rng, order_rng, bond_types):
    nae, _, _ = libraries()
    key, prufer, spare, sizes, meetings = spec
    stars = nae.J.stars_from(sizes, meetings)
    observed = observe(stars, bond_types)
    actual = [tuple(b["parents"]) for b in observed.get("layers", {}).get("parity", {}).get("births", ())
              if len(b["parents"]) > 1]
    result = {"draw": key, "source_size": len(sizes), "prufer": prufer, "spare": spare,
              "meetings": meetings, "stars": stars, **observed, "target": None}
    if not actual:
        return result
    target = target_rng.choice(actual)
    seeds = {policy: order_rng.getrandbits(64) for policy in POLICIES}
    result.update(target=target, target_opportunities=len(actual), schedule_seeds=seeds)
    result["serial"] = {law: {policy: serial_trace(stars, law, policy, target, seeds.get(policy, 0))
                             for policy in (*POLICIES, "immediate")} for law in LAWS}
    for policy in POLICIES:
        archive_agreement(sizes, meetings, result["serial"]["parity"][policy], policy, seeds[policy])
    return result


def controls(bond_types):
    nae, _, _ = libraries()
    meetings = [(0, 1), (0, 2), (0, 3)]
    expanded = [*meetings, (3, 4), (3, 5)]
    samples = {
        "funded_fan": nae.J.stars_from([3] * 4, meetings),
        "funded_fan_with_nonlive_third": nae.J.stars_from([3] * 6, expanded),
        "unfunded_chain": nae.J.stars_from([3] * 5, [(i, i + 1) for i in range(4)]),
        "unlawful_two_place": nae.J.stars_from([2, 3, 3, 3], [(i, i + 1) for i in range(3)]),
    }
    checked = {label: observe(stars, bond_types) for label, stars in samples.items()}
    assert checked["unlawful_two_place"]["funding"]["status"] == "unlawful"
    assert all(checked["unfunded_chain"]["layers"][law]["status"] == "stall" for law in LAWS)
    pair = (1, 2)
    assert not exact_target((1, 2, 3), pair)
    comparisons = {}
    for law in LAWS:
        arms = [next(b for b in checked[k]["layers"][law]["births"] if exact_target(b["parents"], pair))
                for k in ("funded_fan", "funded_fan_with_nonlive_third")]
        assert [b["fresh"] for b in arms] == [1, 2]
        assert arms[0]["readings"]["all_parent_bond_distances"] == arms[1]["readings"]["all_parent_bond_distances"]
        immediate = [serial_trace(samples[k], law, "immediate", pair, 0)
                     for k in ("funded_fan", "funded_fan_with_nonlive_third")]
        assert all(r["status"] == "made" and r["events"][0]["fresh"] > 0 for r in immediate)
        comparisons[law] = {"complete_births": arms, "immediate": immediate}
    # Direct exhaustive all-state, all-support controls, independent of the cut enumeration.
    literal_checks = []
    for stars in (samples["funded_fan"], nae.J.stars_from([3, 4, 3, 3], [(i, i + 1) for i in range(3)])):
        p = nae.S.from_junctions(stars)
        expected = set(tree_bonds(p))
        for law in LAWS:
            assert literal_minima(p, law) == expected
        literal_checks.append({"stars": stars, "bond_supports": sorted(map(hex, expected)), "checked_laws": LAWS})
    original = samples["funded_fan_with_nonlive_third"]
    last_distinction = max(d for support in original for d in support)
    recoded = [sorted(last_distinction - d for d in support) for support in reversed(original)]
    recheck = observe(recoded, bond_types)
    for law in LAWS:
        before = checked["funded_fan_with_nonlive_third"]["layers"][law]["births"]
        after = recheck["layers"][law]["births"]

        def outcomes(births, *, reverse_knots=False):
            return Counter((tuple(sorted(len(original) - 1 - v if reverse_knots else v for v in b["parents"])),
                            b["demand"], b["fresh"], b["t"], b["minimum_input_bond_size"],
                            b["readings"]["all_parent_bond_distances"]) for b in births)

        assert outcomes(before, reverse_knots=True) == outcomes(after)
    return {"stars": samples, "results": checked, "comparison": comparisons,
            "exhaustive_allowed_state_controls": literal_checks,
            "recoded_control": {"stars": recoded, "verified_laws": LAWS}}


def ambiguity(rows, reading, output):
    groups = defaultdict(list)
    for draw, birth in rows:
        key = json.dumps(birth["readings"][reading], separators=(",", ":"))
        groups[key].append((draw, birth))
    nonconstant = []
    for key, examples in sorted(groups.items()):
        counts = Counter(b[output] for _, b in examples)
        if len(counts) > 1:
            representatives = {}
            for draw, birth in examples:
                representatives.setdefault(birth[output], {"draw": draw, "parents": birth["parents"], "inputs": birth["inputs"]})
            nonconstant.append({"reading": json.loads(key), "values": dict(sorted(counts.items())),
                                "representatives": representatives})
    return {"births": len(rows), "observed_readings": len(groups), "ambiguous_readings": len(nonconstant),
            "births_in_ambiguous_readings": sum(sum(x["values"].values()) for x in nonconstant),
            "minimum_lookup_errors_in_sample": sum(sum(x["values"].values()) - max(x["values"].values())
                                                    for x in nonconstant),
            "ambiguous_classes": nonconstant}


def complete_summary(draws, law):
    rows = [(d["draw"], b) for d in draws for b in d.get("layers", {}).get(law, {}).get("births", ())]
    cells = {"all": rows, "multi": [(d, b) for d, b in rows if len(b["parents"]) > 1],
             "unary": [(d, b) for d, b in rows if len(b["parents"]) == 1]}
    counts = {}
    for name, entries in cells.items():
        counts[name] = {"births": len(entries), "fresh_counts": dict(sorted(Counter(b["fresh"] for _, b in entries).items())),
                        "demand_counts": dict(sorted(Counter(b["demand"] for _, b in entries).items())),
                        "formula_demand_agrees": sum(b["demand"] == b["predicted_demand"] for _, b in entries),
                        "formula_fresh_agrees": sum(b["fresh"] == b["predicted_fresh"] for _, b in entries),
                        "without_t_fresh_agrees": sum(b["fresh"] == b["predicted_fresh_without_t"] for _, b in entries),
                        "readers": {reader: {k: ambiguity(entries, reader, k) for k in ("fresh", "demand")}
                                    for reader in AGE_ONE_READERS}}
    return counts


def serial_summary(draws, law):
    by_policy = {}
    for policy in (*POLICIES, "immediate"):
        traces = [d["serial"][law][policy] for d in draws]
        made = [t["events"][-1] for t in traces if t["status"] == "made"]
        by_policy[policy] = {
            "trials": len(traces), "outcomes": dict(sorted(Counter(t["status"] for t in traces).items())),
            "firing_position": dict(sorted(Counter(len(t["events"]) for t in traces if t["status"] == "made").items())),
            "realized_fresh": dict(sorted(Counter(e["fresh"] for e in made).items())),
            "realized_demand": dict(sorted(Counter(e["demand"] for e in made).items())),
            "transient_disappearance_then_fired": sum(t["status"] == "made" and any(not e["target_listed"] for e in t["events"])
                                                         for t in traces),
        }
    comparisons = {}
    for a, b in (("uniform", "joins-first"), ("uniform", "immediate"), ("joins-first", "immediate")):
        traces = [(d["serial"][law][a], d["serial"][law][b]) for d in draws]
        realized = [(left["events"][-1], right["events"][-1]) for left, right in traces if left["status"] == right["status"] == "made"]
        comparisons[f"{a}/{b}"] = {
            "both_made": len(realized), "different_fresh": sum(x["fresh"] != y["fresh"] for x, y in realized),
            "different_demand": sum(x["demand"] != y["demand"] for x, y in realized),
            "joint_status_counts": [[l, r, n] for (l, r), n in sorted(Counter((x["status"], y["status"]) for x, y in traces).items())],
        }
    for policy in by_policy:
        compared = []
        for draw in draws:
            trace = draw["serial"][law][policy]
            if trace["status"] == "made":
                complete = next(b for b in draw["layers"][law]["births"] if exact_target(b["parents"], draw["target"]))
                compared.append((trace["events"][-1], complete))
        by_policy[policy]["different_from_complete_fresh"] = sum(a["fresh"] != b["fresh"] for a, b in compared)
        by_policy[policy]["different_from_complete_demand"] = sum(a["demand"] != b["demand"] for a, b in compared)
    return {"schedules": by_policy, "paired": comparisons}


def summarize(draws):
    strata = {}
    for n in range(4, 9):
        sources = [d for d in draws if d["source_size"] == n]
        strata[n] = {"draws": len(sources), "target_draws": sum(d["target"] is not None for d in sources),
                     "proposed_multi": sum(len(d["funding"].get("proposed_multi", ())) for d in sources),
                     "available_unary_slots_after_multi_obligations": sum(sum(d["funding"].get("unary_slots_after_multi_obligations", ())) for d in sources),
                     "laws": {law: {"lawful": sum(d["lawfulness"][law]["lawful"] for d in sources),
                                    "statuses": dict(sorted(Counter(d.get("layers", {}).get(law, {}).get("status", "unlawful") for d in sources).items())),
                                    "births": sum(len(d.get("layers", {}).get(law, {}).get("births", ())) for d in sources),
                                    "funded_multi": sum(len(b["parents"]) > 1 for d in sources for b in d.get("layers", {}).get(law, {}).get("births", ())),
                                    "funded_unary": sum(len(b["parents"]) == 1 for d in sources for b in d.get("layers", {}).get(law, {}).get("births", ()))}
                              for law in LAWS}}
    marked = [d for d in draws if d["target"] is not None]
    serial_differences = []
    for d in marked:
        for policy in (*POLICIES, "immediate"):
            parity, nae = (d["serial"][law][policy] for law in LAWS)
            if parity != nae:
                serial_differences.append({"draw": d["draw"], "schedule": policy,
                    "event_indices_one_based": [i for i, (p, n) in enumerate(zip(parity["events"], nae["events"]), 1)
                                                if p != n]})
    matrix_by_size = {}
    for law in LAWS:
        matrix_by_size[law] = {}
        for n in strata:
            rows = [(d["draw"], b) for d in draws if d["source_size"] == n
                    for b in d.get("layers", {}).get(law, {}).get("births", ()) if len(b["parents"]) > 1]
            matrix_by_size[law][n] = ambiguity(rows, "all_parent_bond_distances", "fresh")
    return {"source_by_size": strata,
            "marked_draws": len(marked), "complete_layer": {law: complete_summary(draws, law) for law in LAWS},
            "serial": {law: serial_summary(marked, law) for law in LAWS},
            "matrix_ambiguity_by_source_size": matrix_by_size, "cross_law_serial_differences": serial_differences,
            "cross_law_complete_agreement": sum(d.get("layers", {}).get("parity") == d.get("layers", {}).get("nae") for d in draws),
            "cross_law_serial_agreement": {policy: sum(d["serial"]["parity"][policy] == d["serial"]["nae"][policy] for d in marked)
                                           for policy in (*POLICIES, "immediate")}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--limit", type=int, help="Disposable smoke only: take this many initial draws")
    args = parser.parse_args()
    if args.limit is not None and args.output == OUT:
        parser.error("use a scratch output with --limit")
    target_rng = random.Random(TARGET_SEED)
    order_rng = random.Random(ORDER_SEED)
    bond_types = ParentBondTypes()
    control = controls(bond_types)
    draws = []
    for index, spec in enumerate(draw_sources()):
        if args.limit is not None and index >= args.limit:
            break
        draws.append(run_draw(spec, target_rng, order_rng, bond_types))
    receipt = {"schema_version": 1, "design_sha256": sha256(DESIGN.read_bytes()).hexdigest(),
               "tree_seed": TREE_SEED, "target_seed": TARGET_SEED, "schedule_seed": ORDER_SEED,
               "per_size": DRAWS_PER_SIZE, "max_serial_events": MAX_EVENTS,
               "controls": control, "draws": draws, "all_parent_bond_types": bond_types.types,
               "summary": summarize(draws)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as target:
        json.dump(receipt, target, separators=(",", ":"), sort_keys=True)
        target.write("\n")


if __name__ == "__main__":
    main()
