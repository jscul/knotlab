"""Independent ordinary replay of paid original triples and original-state projections."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR_SCOPE = "LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001B"
PRIOR_PATH = ROOT / "experiments" / PRIOR_SCOPE / f"{PRIOR_SCOPE}-E001_private_pulses" / "physical.py"
LAWS = ("parity", "nae")
SEEDS = (20261121701, 20261121801)
CAP = 1024
TRUE_PREBIRTHS = {
    "selected_I": (0, 1, 3, 5, 7, 10, 13, 72, 80, 81, 83, 85, 87, 89, 91, 108),
    "selected_mixed_I": (0, 1, 3, 5, 7, 10, 13, 72, 80, 81, 83, 85, 94, 95, 97, 101, 103, 105, 108),
}


@cache
def prior():
    spec = spec_from_file_location("b285_b283_physical", PRIOR_PATH)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fixture():
    return prior().fixtures()


@dataclass(frozen=True)
class Case:
    key: str
    mode: str = "M+T"
    near: bool = False
    retag: int = 0
    remote: bool = False
    break_sender: bool = False
    shortage: bool = False

    @property
    def has_z(self):
        return "M" in self.mode

    @property
    def has_w(self):
        return "T" in self.mode


CASES = (
    Case("intact"),
    Case("near", near=True),
    Case("intact_w_disabled", retag=1),
    Case("near_w_enabled", near=True, retag=-1),
    Case("remote", remote=True),
    Case("intact_s_break", break_sender=True),
    Case("near_s_break", near=True, break_sender=True),
    Case("p_shortage", shortage=True),
    Case("m_intact", "M"), Case("m_near", "M", near=True),
    Case("t_intact", "T"), Case("t_near", "T", near=True),
    Case("neither_intact", "neither"), Case("neither_near", "neither", near=True),
)


def bundle(source, left, right):
    return tuple(sorted(set(source[left]).intersection(source[right])))


def add_gate(prep, tail, head, side, common, has_z, has_w, w_width):
    a, b = (prep.role_id[role] for role in (tail, head))
    result = {"common": common, "a_small": None, "b_small": None}
    if has_z:
        z = prep.holder("z" + side)
        prep.new_distinction(z, common)
        for _ in range(2):
            prep.new_distinction(z)
        for donor in (a, b):
            prep.new_distinction(donor)
    if has_w:
        w = prep.holder("w" + side)
        for label, donor, count in (("a_small", a, 2), ("b_small", b, w_width)):
            witness = prep.holder(f"{side} {label}")
            result[label] = witness
            prep.new_distinction(donor, witness)
            for _ in range(count):
                prep.new_distinction(w, witness)
        for _ in range(2):
            prep.new_distinction(w)
    return result


def switch_tails(prep, gates, tail_ids):
    edits = []
    for key in ("common", "a_small"):
        witnesses = [gates[s][key] for s in ("P", "H")]
        if witnesses[0] is None:
            assert witnesses[1] is None
            continue
        names = [bundle(prep.stars, witness, donor)
                 for witness, donor in zip(witnesses, tail_ids, strict=True)]
        assert all(len(row) == (3 if key == "common" else 1) for row in names)
        for j, witness in enumerate(witnesses):
            before, after = names[j], names[1 - j]
            prep.stars[witness] = sorted(set(prep.stars[witness]).difference(before).union(after))
            edits.append({"witness": witness, "old_tail": tail_ids[j], "new_tail": tail_ids[1 - j],
                          "removed_names": before, "received_names": after})
    return edits


def prepare(case):
    old = prior()
    native = old.previous()
    prep, edits = old.prepare(old.Case("intact"))
    c_common = prep.arc_witness["c8", "p"]
    u_common = prep.arc_witness["u8", "h"]
    u8 = prep.role_id["u8"]
    u_removed = bundle(prep.stars, u8, u_common)[-2:]
    assert len(bundle(prep.stars, u8, u_common)) == 5
    for holder in (u8, u_common):
        prep.stars[holder] = [name for name in prep.stars[holder] if name not in u_removed]
    edits.append({"kind": "common_u_tail_width", "witness": u_common, "donor": u8,
                  "removed_names": u_removed})

    gates = {
        "P": add_gate(prep, "c8", "p", "P", c_common, case.has_z, case.has_w, 2),
        "H": add_gate(prep, "u8", "h", "H", u_common, case.has_z, case.has_w, 3),
    }
    if case.near:
        sw = switch_tails(prep, gates, (prep.role_id["c8"], u8))
        edits.append({"kind": "whole_original_tail_bundles", "changes": sw})
    for site in ((10,) if case.near else (15, 17) if case.remote else ()):
        pairs = [(old.original_role(tag, site), old.original_role(tag, site + 1)) for tag in ("c", "u")]
        edits.append({"kind": "circuit_head_exchange", "site": site,
                      "changes": native.exchange(prep, *pairs, 4)})
    if case.retag:
        side = "P" if case.retag > 0 else "H"
        witness = gates[side]["b_small"]
        w = prep.role_id["w" + side]
        if case.retag > 0:
            name = prep.new_name
            prep.new_distinction(w, witness)
            action = "added_names"
        else:
            name = bundle(prep.stars, w, witness)[-1]
            for holder in (w, witness):
                prep.stars[holder].remove(name)
            action = "removed_names"
        edits.append({"kind": "w_width", "holder": w, "witness": witness, action: [name]})
    if case.break_sender:
        edits.append({"kind": "private_head_exchange",
                      "changes": native.exchange(prep, ("S3", "S4"), ("V3", "V4"), 4)})
    if case.shortage:
        p = prep.role_id["p"]
        name = fixture().incidence(prep.immutable())[2][p][-1]
        prep.stars[p].remove(name)
        edits.append({"kind": "private_shortage", "holder": p, "removed_names": [name]})
    return prep, edits


def original_incidence(stars):
    f = fixture()
    owned, ordinary, loose = f.incidence(stars)
    spent = sorted(set(ordinary).difference(loose))
    assert nx.is_connected(ordinary)
    assert all(len(star) >= 3 and len(set(star)) == len(star) for star in stars)
    assert len(set(map(frozenset, stars))) == len(stars)
    assert all(set(ordinary[k]).issubset(loose) for k in spent)
    assert all(set(ordinary[k]).isdisjoint(loose) for k in loose)
    assert all(loose[k] for k in loose)
    assert set().union(*(set(stars[k]) for k in spent)) == {
        d for d, holders in owned.items() if len(holders) == 2
    }
    assert sum(len(stars[k]) for k in spent) == sum(len(holders) == 2 for holders in owned.values())
    return owned, ordinary, loose, spent


def read_source(stars):
    owned, ordinary, loose, spent = original_incidence(stars)
    groups = {}
    ports = {k: {} for k in loose}
    witness_donors = {}
    high_witnesses = {}
    for witness in spent:
        donors = {k: bundle(stars, witness, k) for k in sorted(ordinary[witness])}
        assert len(donors) in (2, 3) and all(donors.values())
        witness_donors[witness] = donors
        high = tuple(k for k, names in donors.items() if len(names) >= 3)
        if len(high) == 2:
            high_witnesses[witness] = high
        for a, b in combinations(donors, 2):
            assert (a, b) not in groups
            groups[a, b] = witness
            for x, y in ((a, b), (b, a)):
                ports[x][y] = {"peer": y, "witness": witness,
                               "local_names": donors[x], "peer_names": donors[y],
                               "local_count": len(donors[x]), "peer_count": len(donors[y]),
                               "circuit": x in high and y in high and len(high) == 2}

    def signed(width_a, width_b):
        return [(k, peer) for k, row in ports.items() for peer, port in row.items()
                if (port["local_count"], port["peer_count"]) == (width_a, width_b)]

    (o, h_entry), = signed(1, 17)
    (same_h, c0), = signed(1, 11)
    (also_h, s0), = signed(1, 13)
    assert h_entry == same_h == also_h
    (o1, v0), = signed(1, 15)
    assert (o, o1) in signed(1, 2)
    o2, = (j for k, j in signed(1, 2) if k == o1)
    o3, = (j for k, j in signed(1, 2) if k == o2)
    assert (o3, o) in signed(1, 2)

    high_graph = nx.Graph()
    high_graph.add_edges_from(high_witnesses.values())
    (c18, u18), = ((a, b) for a, b in signed(1, 2) if a in high_graph and b in high_graph)
    circuit_donors = set().union(*(nx.node_connected_component(high_graph, k) for k in (c0, c18, u18)))
    order = {
        k: tuple(r["peer"] for r in sorted(row.values(), key=lambda r: r["local_count"]) if r["circuit"])
        for k, row in ports.items() if k in circuit_donors
    }
    assert all(len(row) >= 2 and len({ports[k][j]["local_count"] for j in row}) == len(row)
               for k, row in order.items())
    p, = (j for j in order[c0] if len(order[j]) == 8)
    h, = (j for j in order if j != p and len(order[j]) == 8)
    trail = [c0, p]
    for _ in range(7):
        trail.append(prior().previous().successor(order, *trail[-2:])[1])
    q, = {j for j in trail if len(order[j]) == 4}
    k, = (j for j in order if j != q and len(order[j]) == 4)

    s_next, v_next = dict(signed(2, 4)), dict(signed(6, 4))

    def prefix(start, arrows):
        parts = [start]
        for _ in range(3):
            parts.append(arrows[parts[-1]])
        return parts

    sender, reserve = prefix(s0, s_next), prefix(v0, v_next)
    ends = (s_next[sender[-1]], v_next[reserve[-1]])
    s4, = (j for j in ends if j in s_next)
    v4, = (j for j in ends if j in v_next)
    sender.extend((s4, s_next[s4], s_next[s_next[s4]]))
    reserve.extend((v4, v_next[v4], v_next[v_next[v4]]))
    assert s_next[sender[-1]] == s0 and v_next[reserve[-1]] == v0
    roles = dict(O=o, O1=o1, O2=o2, O3=o3, H=h_entry, c0=c0, p=p, h=h, q=q, k=k,
                 c18=c18, u18=u18, c2=trail[2], c4=trail[4], c6=trail[6], c8=trail[8])
    roles.update({f"S{i}": j for i, j in enumerate(sender)})
    roles.update({f"V{i}": j for i, j in enumerate(reserve)})
    gate_rows = {}
    for side in ("P", "H"):
        head = roles["p" if side == "P" else "h"]
        tail, = (j for j in order[head] if ports[head][j]["local_count"] == 9)
        witness = ports[head][tail]["witness"]
        assert ports[tail][head]["local_count"] == 3
        z, = tuple(sorted(set(witness_donors[witness]) - {head, tail})) or (None,)
        overlap = set(ports[tail]).intersection(ports[head]) - set(witness_donors[witness])
        assert len(overlap) <= 1
        w, = tuple(sorted(overlap)) or (None,)
        small = []
        if w is not None:
            assert set(ports[w]) == {tail, head}
            small = [ports[donor][w]["witness"] for donor in (tail, head)]
            assert len(set(small)) == 2 and all(ports[donor][w]["local_count"] == 1 for donor in (tail, head))
            roles["w" + side] = w
        if z is not None:
            assert set(ports[z]) == {tail, head}
            roles["z" + side] = z
        gate_rows[side] = {
            "tail": tail, "head": head, "w": w, "z": z, "common_witness": witness,
            "common_names_by_holder": witness_donors[witness], "small_witnesses": small,
            "w_widths": [ports[w][j]["local_count"] for j in (tail, head)] if w is not None else [],
        }
    assert len(set(roles.values())) == len(roles)
    return {"owned": owned, "loose": loose, "roles": roles, "ports": ports, "order": order,
            "gates": gate_rows, "candidate_pair_witnesses": groups, "spent_supports": witness_donors,
            "sender": sender, "reserve": reserve, "mixed_sender_next": s_next | v_next}


def roster(stars, law):
    f = fixture()
    _, ordinary, loose = f.incidence(stars)
    blocks, candidate = f.witnessed_end(ordinary, loose)
    assert nx.is_connected(ordinary)
    paid = f.multi_groups(blocks, candidate)
    pay_by_holder = Counter(k for parents in paid for k in parents)
    turn = f.step(f.from_stars(stars), law, max_births=CAP)
    witnessed = {k: sorted(blocks[k]) for k in ordinary if len(blocks[k]) >= 2}
    max_groups = []
    for group in sorted(tuple(sorted(group)) for group in nx.find_cliques(candidate) if len(group) >= 2):
        max_groups.append({"members": group, "held_at": [k for k, row in witnessed.items() if set(group) <= set(row)],
                           "chosen_as_group": group in paid})
    direct_shortages = tuple((k, pay_by_holder[k] - len(loose[k])) for k in sorted(loose)
                             if pay_by_holder[k] > len(loose[k]))
    assert direct_shortages == turn.shortages
    if turn.status == "extend":
        unaries = tuple((k,) for k in sorted(loose) for _ in range(len(loose[k]) - pay_by_holder[k]))
        assert turn.parents == paid + unaries
    return turn, {
        "witnessed_sets": witnessed, "maximal_candidate_sets": max_groups,
        "candidate_pairs": sorted(tuple(sorted(row)) for row in candidate.edges),
        "proposed_multiple_groups": paid,
        "proposed_unary_counts": {k: max(0, len(row) - pay_by_holder[k]) for k, row in loose.items()},
        "charges_per_original_live_holder": {
            k: {"available_names": row, "multi_charge": pay_by_holder[k],
                "loose_after_multi": len(row) - pay_by_holder[k]}
            for k, row in loose.items()
        },
        "funded_births": list(zip(turn.parents, turn.demand, turn.fresh, strict=True)),
    }


def literal_cut(stars, law, age):
    f = fixture()
    owned, _, loose = f.incidence(stars)
    turn, plan = roster(stars, law)
    row = {"age": age, "status": turn.status, "shortages": turn.shortages,
           "implied": turn.implied, "forecast": plan, "births": []}
    if turn.status != "extend":
        return stars, row
    status, births, multiple = f.literal_turn(stars, law)
    assert status == "extend" and multiple == plan["proposed_multiple_groups"]
    assert len(births) <= CAP
    used = defaultdict(list)
    fresh = []
    source = prior().previous().archive().joint()
    with source.projector(stars, law) as project:
        for b, (group, demand, grant) in zip(births, plan["funded_births"], strict=True):
            assert b.parents == group and len(b.fresh) == grant
            for k, d in zip(group, b.inputs, strict=True):
                assert owned[d] == [k]
                used[k].append(d)
            fresh.extend(b.fresh)
            input_words = project(b.inputs)
            assert input_words == tuple(range(1 << len(group)))
            fixture().canonical_relation(law, len(b.support))
            row["births"].append({"holder": b.knot, "parents": group, "consumed_names": b.inputs,
                                  "fresh_names": b.fresh, "demand": demand, "grant": grant,
                                  "input_projection": input_words})
    assert set(fresh).isdisjoint(owned) and len(fresh) == len(set(fresh))
    assert {k: sorted(names) for k, names in used.items()} == loose
    grown = stars + tuple(b.support for b in births)
    assert f.incidence(grown)[2] == {b.knot: list(b.fresh) for b in births if b.fresh}
    row.update(paid_names_by_donor={k: names for k, names in used.items()},
               old_assignments_extend=bool(fresh) and all(b.fresh for b in births),
               newborn_knot_counts_by_arity=dict(sorted(Counter(len(b.support) for b in births).items())))
    return grown, row


def law_allows(word, width, law):
    return word.bit_count() % 2 == 0 if law == "parity" else word not in (0, (1 << width) - 1)


def fit_state(stars, loose, spent, fixed, law):
    """Complete each disjoint spent support, then each living holder privately."""
    values = dict(fixed)
    for holder in [*spent, *sorted(loose)]:
        support = stars[holder]
        free = [d for d in support if d not in values]
        values.update(dict.fromkeys(free, 0))
        word = sum(values[d] << i for i, d in enumerate(support))
        if not law_allows(word, len(support), law):
            if not free:
                return None
            values[free[0]] = 1 if law == "parity" else 1 - values[free[0]]
    assert all(values[d] == value for d, value in fixed.items())
    assert all(law_allows(sum(values[d] << i for i, d in enumerate(row)), len(row), law) for row in stars)
    return values


def certify_source(stars, law):
    _, _, loose, spent = original_incidence(stars)
    checks = 0
    for k, support in enumerate(stars):
        width = len(support)
        fixture().canonical_relation(law, width)
        grain = range(1 << width) if width <= 5 else (0, 1, 2, 3, (1 << width) - 1, 1 << (width - 1))
        for word in grain:
            given = {d: (word >> i) & 1 for i, d in enumerate(support)}
            assert (fit_state(stars, loose, spent, given, law) is not None) == law_allows(word, width, law), k
            checks += 1
    return {"spents_are_distinction_disjoint": True, "each_living_holder_has_private_place": True,
            "knot_counts_by_arity": dict(sorted(Counter(map(len, stars)).items())),
            "constructive_word_checks": checks, "whole_support_K1_K2_K3": True}


def projection_scopes(baseline, source, reading):
    scopes = {}
    for side in ("P", "H"):
        fixed = baseline["gates"][side]
        gate = reading["gates"][side]
        w_now = gate["common_witness"]
        own = reading["spent_supports"][w_now]
        scopes[f"physical_{side}_12"] = own[gate["tail"]] + own[gate["head"]]
        scopes[f"physical_{side}_witness"] = tuple(sorted(source[w_now]))
        scopes[f"fixed_{side}_12"] = fixed["common_names_by_holder"][fixed["tail"]] + fixed["common_names_by_holder"][fixed["head"]]
        if gate["z"] is not None:
            scopes[f"fixed_{side}_13"] = scopes[f"fixed_{side}_12"] + fixed["common_names_by_holder"][fixed["z"]]
    return scopes


def projected_words(stars, scopes, law):
    source = prior().previous().archive().joint()
    _, _, loose, spent = original_incidence(stars)
    with source.projector(stars, law) as project:
        words = {scope: project(scope) for scope in dict.fromkeys(scopes.values())}
    results = {}
    for key, names in scopes.items():
        assert len(names) in (12, 13)
        allowed = words[names]
        relevant = [tuple(sorted(stars[w])) for w in spent if set(stars[w]).issubset(names)]
        indices = [[names.index(d) for d in support] for support in relevant]
        assert not any(set(stars[k]).issubset(names) for k in loose)
        predicted = tuple(word for word in range(1 << len(names))
                          if all(law_allows(sum(((word >> j) & 1) << i for i, j in enumerate(row)), len(row), law)
                                 for row in indices))
        assert allowed == predicted
        allowed_set = set(allowed)
        forbidden = next((word for word in range(1 << len(names)) if word not in allowed_set), None)
        if forbidden is not None:
            pins = {d: (forbidden >> i) & 1 for i, d in enumerate(names)}
            assert fit_state(stars, loose, spent, pins, law) is None
        results[key] = {"scope": names, "allowed_words_lsb_first": allowed,
                        "allowed_count": len(allowed), "word_count": 1 << len(names),
                        "first_forbidden_word": forbidden, "wholly_visible_spent_factors": relevant}
    return results


def gate_growth(gate, cuts):
    a, b, w, z = (gate[k] for k in ("tail", "head", "w", "z"))
    pair_or_triple = tuple(sorted(x for x in (a, b, w) if x is not None))
    residuals = [tuple(sorted((x, z))) for x in (a, b)] if z is not None else []
    wanted = [pair_or_triple, *residuals]
    paid = cuts[0]["forecast"]["proposed_multiple_groups"]
    local = {x for x in (a, b, w, z) if x is not None}
    candidates = [row for row in paid if set(row).issubset(local)]
    assert sorted(candidates) == sorted(wanted)
    previous = {tuple(birth["parents"]): birth for birth in cuts[0]["births"] if len(birth["parents"]) >= 2}
    realized = [previous[row] for row in wanted if row in previous]
    second = []
    alternatives = []
    if realized and len(cuts) >= 2:
        local_ids = tuple(sorted(birth["holder"] for birth in realized))
        second = [b for b in cuts[1]["births"] if set(b["parents"]).issubset(local_ids)]
        alternatives = [b for b in cuts[1]["births"] if set(b["parents"]).intersection(local_ids)]
        if z is not None:
            assert len(second) == 1 and second[0]["parents"] == local_ids
    return {"local_original_groups": wanted, "original_crossing": realized[0] if realized else None,
            "local_paid_original_groups": realized, "joint_next_groups": second,
            "all_next_groups_using_a_local_birth": alternatives}


def recode(source, final, reading, cuts, law, seed):
    f = fixture()
    rng = Random(seed)
    old_names = sorted({name for support in final for name in support})
    new_names = rng.sample(range(len(old_names) + 100, 5 * len(old_names) + 100), len(old_names))
    name_map = dict(zip(old_names, new_names, strict=True))
    holders = list(range(len(final)))
    rng.shuffle(holders)
    recoded = tuple(tuple(rng.sample([name_map[d] for d in final[k]], len(final[k]))) for k in holders)
    original, parents, _, depth = f.peel(recoded, law)
    assert depth == sum(cut["status"] == "extend" for cut in cuts)
    positions = sorted(original)
    local_to_old = [holders[k] for k in positions]
    assert set(local_to_old) == set(range(len(source)))
    rebuild = read_source(tuple(recoded[k] for k in positions))
    assert {r: local_to_old[k] for r, k in rebuild["roles"].items()} == reading["roles"]
    assert {local_to_old[k]: tuple(local_to_old[j] for j in neighbors)
            for k, neighbors in rebuild["order"].items()} == reading["order"]
    assert {local_to_old[w]: {local_to_old[k]: set(names) for k, names in donors.items()}
            for w, donors in rebuild["spent_supports"].items()} == {
                w: {k: {name_map[d] for d in names} for k, names in donors.items()}
                for w, donors in reading["spent_supports"].items()
            }
    assert set(parents) == set(range(len(final))).difference(original)
    recovered = {holders[k]: set(map(holders.__getitem__, row)) for k, row in parents.items()}
    expected = {b["holder"]: set(b["parents"]) for cut in cuts for b in cut["births"]}
    assert recovered == expected
    old_pos = {k: i for i, k in enumerate(holders)}
    for cut in cuts:
        for b in cut["births"]:
            support = set(recoded[old_pos[b["holder"]]])
            inputs = {name_map[d] for d in b["consumed_names"]}
            assert support == inputs | {name_map[d] for d in b["fresh_names"]}
            for parent, name in zip(b["parents"], b["consumed_names"], strict=True):
                assert support.intersection(recoded[old_pos[parent]]) == {name_map[name]}
    return {"seed": seed, "recoded_full_stars": recoded, "recoded_to_original_holder": holders,
            "original_to_recoded_names": sorted(name_map.items()), "source_indices_in_recoding": positions,
            "component_depths": [depth], "actual_parent_lists_recovered": len(recovered)}


def verify_continuing_ring(cuts, ring):
    """Find each literal ring-pair birth and verify it pays in the next cut."""
    known = [tuple(ring)]
    for cut in cuts:
        if cut["status"] != "extend":
            break
        previous = known[-1]
        assert len(previous) >= 4
        pairs = {frozenset((previous[i - 1], k)) for i, k in enumerate(previous)}
        inside = [frozenset(row) for row in cut["forecast"]["candidate_pairs"]
                  if set(row).issubset(previous)]
        assert set(inside) == pairs
        members = {frozenset(b["parents"]): b for b in cut["births"] if len(b["parents"]) == 2}
        ring_births = tuple(members[frozenset((previous[i - 1], k))] for i, k in enumerate(previous))
        assert all(b["grant"] >= 1 for b in ring_births)
        known.append(tuple(b["holder"] for b in ring_births))
    return known


def run_case(case, index, baseline):
    prep, edits = prepare(case)
    source = prep.immutable()
    read = read_source(source)
    origins = {r: k for r, k in prep.role_id.items() if k in read["loose"]}
    assert read["roles"] == {r: origins[r] for r in read["roles"]}
    assert read["gates"]["P"]["tail"] == origins["u8" if case.near else "c8"]
    assert read["gates"]["H"]["tail"] == origins["c8" if case.near else "u8"]
    labels = {k: r for r, k in origins.items()}
    scopes = projection_scopes(baseline, source, read)
    laws = {}
    for law in LAWS:
        legality = certify_source(source, law)
        projections = projected_words(source, scopes, law)
        frame = source
        cuts = []
        for age in (1, 2):
            frame, cut = literal_cut(frame, law, age)
            cuts.append(cut)
            if cut["status"] != "extend":
                break
            assert cut["old_assignments_extend"]
        if case.shortage:
            assert len(cuts) == 1 and cuts[0]["status"] == "stall"
            assert cuts[0]["shortages"] == ((origins["p"], 1),)
            assert frame == source
        else:
            assert len(cuts) == 2 and all(cut["status"] == "extend" for cut in cuts)
        laws[law] = {
            "source_projections": legality, "cuts": cuts,
            "gate_growth": {side: gate_growth(gate, cuts) for side, gate in read["gates"].items()},
            "word_projections": projections, "old_word_projections_preserved_through": len(cuts) if not case.shortage else 0,
            "continuing_original_four_return": verify_continuing_ring(cuts, [origins[r] for r in ("O", "O1", "O2", "O3")]),
            "recodings": [recode(source, frame, read, cuts, law, seed + index) for seed in SEEDS],
        }
    assert [(c["status"], c["births"]) for c in laws["parity"]["cuts"]] == [
        (c["status"], c["births"]) for c in laws["nae"]["cuts"]]
    pairs = sorted((tuple(sorted((labels[a], labels[b]))), w)
                   for (a, b), w in read["candidate_pair_witnesses"].items())
    next_sender = read["mixed_sender_next"]
    mixed = [origins["S0"]]
    while next_sender[mixed[-1]] != mixed[0]:
        assert next_sender[mixed[-1]] not in mixed
        mixed.append(next_sender[mixed[-1]])
    assert len(mixed) == (14 if case.break_sender else 7)
    return {
        "case": case.key, "gate_mode": case.mode, "original_stars": source, "live_roles": origins,
        "decoded_roles": read["roles"], "gates": read["gates"], "edits": edits,
        "original_distinction_count": len(read["owned"]),
        "loose_names": {labels[k]: names for k, names in read["loose"].items()},
        "candidate_pairs": [pair for pair, _ in pairs], "candidate_pair_witnesses": pairs,
        "ports": {k: {"ordered_circuit_neighbors": read["order"].get(k, ()),
                      "all_paid_ports": sorted(row.values(), key=lambda x: (x["local_count"], x["peer"]))}
                  for k, row in read["ports"].items()},
        "original_spent_supports": read["spent_supports"],
        "sender_private_return_intact": not case.break_sender, "mixed_sender_corridor": mixed,
        "laws": laws,
    }


def calibration(mode):
    """Use the complete host with a continuing five-pair path from b to a."""
    older = prior().previous()
    prep = older.archive().joint().prior().Preparation([], {}, {})
    older.add_pair(prep, ("a", "b"), (3, 9))
    path = ("b", "x1", "x2", "x3", "x4", "a")
    for a, b in zip(path[:-1], path[1:], strict=True):
        older.add_pair(prep, (a, b), (3, 4))
    gate = add_gate(prep, "a", "b", "P", prep.arc_witness["a", "b"], "M" in mode, "T" in mode, 2)
    source = prep.immutable()
    _, _, loose, _ = original_incidence(source)
    roles = {name: k for name, k in prep.role_id.items() if k in loose}
    gate.update(tail=roles["a"], head=roles["b"], w=roles.get("wP"), z=roles.get("zP"))
    laws = {}
    core = {roles[k] for k in ("a", "b", "wP", "zP") if k in roles}
    for law in LAWS:
        frame = source
        cuts = []
        footprint = {k: frozenset((k,)) for k in loose}
        for age in (1, 2, 3, 4):
            frame, cut = literal_cut(frame, law, age)
            assert cut["status"] == "extend"
            cuts.append(cut)
            by_support = defaultdict(list)
            for b in cut["births"]:
                sites = frozenset().union(*(footprint[k] for k in b["parents"]))
                footprint[b["holder"]] = sites
                by_support[tuple(sorted(sites))].append(b["holder"])
            cut["ancestral_footprints"] = [{"original_donors": sites, "members": newborns}
                                           for sites, newborns in sorted(by_support.items())]
            cut["ancestral_footprints_with_multiple_lifts"] = [
                {"original_donors": sites, "members": newborns} for sites, newborns in sorted(by_support.items())
                if len(newborns) > 1]
        growth = gate_growth(gate, cuts)
        touching = []
        for age, cut in enumerate(cuts, 2):
            containing_core = [b for b in cut["births"] if core.issubset(footprint[b["holder"]])]
            touching.append({"rank": age, "all_member_ids_containing_gate_donors": [b["holder"] for b in containing_core],
                             "parent_tuples": [b["parents"] for b in containing_core]})
        laws[law] = {"cuts": cuts, "gate_growth": growth, "containing_original_core": touching,
                     "source_projections": certify_source(source, law)}
    return {"case": mode, "original_stars": source, "live_roles": roles, "external_path": path,
            "gates": {"P": gate}, "laws": laws}


def projected_factors(stars, donor_ids):
    """Give the exact whole projected relation on the full rows of these living donors."""
    owned, _, loose, spent = original_incidence(stars)
    live = {k: tuple(sorted(stars[k])) for k in sorted(set(donor_ids))}
    assert set(live).issubset(loose)
    scope = set().union(*map(set, live.values()))
    visible = {k: tuple(sorted(stars[k])) for k in spent if set(stars[k]).issubset(scope)}
    return {
        "projected_name_ids": tuple(sorted(scope)), "occupied_original_donors": tuple(live),
        "live_factors": live, "spent_factors": visible,
        "partially_visible_spent_factors": {
            k: tuple(sorted(scope.intersection(stars[k]))) for k in spent
            if k not in visible and scope.intersection(stars[k])
        },
        "complete_name_counts": {"retained": len(scope), "quantified": len(owned) - len(scope)},
    }


def nae_projection_count(factors):
    """Inclusion-exclusion over a donor fixed to zero, fixed to one, or unpinned."""
    live, spent = factors["live_factors"], factors["spent_factors"]
    donor_of = {d: k for k, names in live.items() for d in names}
    unchecked = set(donor_of).difference(d for row in spent.values() for d in row)
    free = Counter(donor_of[d] for d in unchecked)
    tables = [((k,), {(0,): 1 << free[k], (1,): -1, (2,): -1}) for k in live]
    for witness in spent.values():
        sizes = Counter(donor_of[d] for d in witness)
        holders = tuple(sorted(sizes))
        table = {}
        for state in product(range(3), repeat=len(holders)):
            count = 1 << sum(sizes[k] for k, s in zip(holders, state, strict=True) if s == 0)
            table[state] = count - int(2 not in state) - int(1 not in state)
        tables.append((holders, table))

    remaining = set(live)
    scalar = 1
    max_width = 0
    while remaining:
        touching = {k: [(holders, table) for holders, table in tables if k in holders] for k in remaining}
        neighborhoods = {k: set().union(*(set(holders) for holders, _ in rows))
                         for k, rows in touching.items()}
        chosen = min(remaining, key=lambda k: (len(neighborhoods[k]), k))
        scope = tuple(sorted(neighborhoods[chosen]))
        max_width = max(max_width, len(scope))
        assert max_width <= 10
        reduced = tuple(k for k in scope if k != chosen)
        keep = [scope.index(k) for k in reduced]
        terms = [([scope.index(k) for k in holders], table) for holders, table in touching[chosen]]
        updated = defaultdict(int)
        for state in product(range(3), repeat=len(scope)):
            count = 1
            for indices, table in terms:
                count *= table[tuple(state[i] for i in indices)]
            updated[tuple(state[i] for i in keep)] += count
        tables = [(holders, table) for holders, table in tables if chosen not in holders]
        if reduced:
            tables.append((reduced, updated))
        else:
            scalar *= updated[()]
        remaining.remove(chosen)
    assert not tables and scalar > 0
    return scalar, max_width


def count_projected(factors, law):
    width = len(factors["projected_name_ids"])
    if law == "parity":
        rank = len(factors["live_factors"]) + len(factors["spent_factors"])
        return {"allowed_states": str(1 << (width - rank)), "independent_parity_rows": rank}
    count, max_width = nae_projection_count(factors)
    return {"allowed_states": str(count), "largest_elimination_scope_in_donors": max_width}


def compare_projection(first_stars, second_stars, donor_ids, law):
    first, second = (projected_factors(stars, donor_ids) for stars in (first_stars, second_stars))
    domains_match = first["live_factors"] == second["live_factors"]
    result = {"law": law, "same_named_donor_scopes": domains_match,
              "first": first | count_projected(first, law), "second": second | count_projected(second, law)}
    if not domains_match:
        return result | {"literal_identity": None, "mutual_inclusion": None}

    first_rows, second_rows = (set(side["spent_factors"].values()) for side in (first, second))
    result["literal_identity"] = True
    result["same_spent_factors"] = first_rows == second_rows
    inclusion = {}
    for name, accepted, source_rows, target_rows in (
            ("first_in_second", first_stars, first_rows, second_rows),
            ("second_in_first", second_stars, second_rows, first_rows)):
        missing = sorted(target_rows - source_rows)
        if not missing:
            inclusion[name] = {"included": True, "basis": "Every required complete factor is present."}
            continue
        _, _, loose, spent = original_incidence(accepted)
        target = missing[0]
        probes = (1 << j for j in range(len(target))) if law == "parity" else (0,)
        for word in probes:
            pins = {d: (word >> i) & 1 for i, d in enumerate(target)}
            completion = fit_state(accepted, loose, spent, pins, law)
            if completion is not None:
                break
        else:
            raise AssertionError(("No exact failed inclusion certificate", name, missing))
        assert not law_allows(word, len(target), law)
        permitted_ones = tuple(d for d in first["projected_name_ids"] if completion[d])
        inclusion[name] = {"included": False, "missing_spent_factors": missing,
                           "failing_target_factor": target, "target_word": word,
                           "projected_assignment_ones": permitted_ones}
    result["mutual_inclusion"] = inclusion
    result["equal"] = all(check["included"] for check in inclusion.values())
    return result


def whole_state_checks(rows):
    """Use the receiver replay's true original donors for each tested prefix."""
    cases = {row["case"]: row for row in rows}
    matches = []
    comparisons = (
        ("intact", "near"), ("intact", "intact_w_disabled"), ("near", "near_w_enabled"),
        ("intact", "remote"), ("intact_s_break", "near_s_break"),
        ("m_intact", "m_near"), ("t_intact", "t_near"), ("neither_intact", "neither_near"),
    )
    for first_key, second_key in comparisons:
        first, second = cases[first_key], cases[second_key]
        shared_holders = sorted(set(first["live_roles"]).intersection(second["live_roles"]))
        assert all(first["live_roles"][role] == second["live_roles"][role] for role in shared_holders)
        basis = "selected_mixed_I" if first_key.endswith("_s_break") else "selected_I"
        label = {k: name for name, k in first["live_roles"].items()}
        prefix = tuple(label[k] for k in TRUE_PREBIRTHS[basis])
        assert not any(role.startswith(("w", "z")) for role in prefix)
        ablation = first["gate_mode"] != "M+T"
        scope_by_grade = {
            "same_donor_ids_control" if ablation else basis: prefix,
            "all_living_originals": tuple(shared_holders),
        }
        if "zP" in shared_holders:
            scope_by_grade["I_exposing_zP"] = (*prefix, "zP")
        if "wP" in shared_holders:
            scope_by_grade["I_exposing_wP"] = (*prefix, "wP")
        if "zP" in shared_holders and "wP" in shared_holders:
            scope_by_grade["I_exposing_wP_zP"] = (*prefix, "wP", "zP")
        exterior = tuple(role for role in ("wP", "zP", "wH", "zH") if role in shared_holders)
        if exterior:
            scope_by_grade["I_exposing_all_gate_exterior_donors"] = (*prefix, *exterior)
        match = {"first": first_key, "second": second_key, "grades": {}}
        for grade, roles in scope_by_grade.items():
            ids = tuple(first["live_roles"][role] for role in roles)
            match["grades"][grade] = {"roles": roles, "laws": {
                law: compare_projection(first["original_stars"], second["original_stars"], ids, law)
                for law in LAWS}}
        matches.append(match)
    return matches


def matched_native_controls(rows):
    """Check one coherent physical name transport through both paid cuts."""
    cases = {row["case"]: row for row in rows}
    controls = []
    for first_key, second_key in (("intact", "intact_w_disabled"), ("near", "near_w_enabled")):
        first, second = (cases[key] for key in (first_key, second_key))
        old = set().union(*map(set, first["original_stars"]))
        new = set().union(*map(set, second["original_stars"]))
        assert len(old.symmetric_difference(new)) == 1
        bindings = {}
        for law in LAWS:
            transport = {d: d for d in sorted(old.intersection(new))}
            for a, b in zip(first["laws"][law]["cuts"], second["laws"][law]["cuts"], strict=True):
                for x, y in zip(a["births"], b["births"], strict=True):
                    assert (x["holder"], x["parents"], x["demand"], x["grant"]) == (
                        y["holder"], y["parents"], y["demand"], y["grant"])
                    assert tuple(transport[d] for d in x["consumed_names"]) == y["consumed_names"]
                    transport.update(zip(x["fresh_names"], y["fresh_names"], strict=True))
            assert len(set(transport.values())) == len(transport)
            bindings[law] = sorted(transport.items())
        controls.append({"first": first_key, "second": second_key, "born_rosters_and_funds_equal": True,
                         "first_only_old_names": sorted(old - new), "second_only_old_names": sorted(new - old),
                         "one_transport_through_paid_history": bindings})
    return controls


def input_hashes():
    review = HERE / "advisor_receipt.json"
    approval = next(row for row in json.loads(review.read_bytes())["records"] if row["verdict"] == "approved")
    prereg = HERE / "preregistration.md"
    assert sha256(prereg.read_bytes()).hexdigest() == approval["sha256"]
    b281 = prior().previous()
    b278 = b281.archive()
    b277 = b278.joint()
    files = [Path(__file__), review, prereg, ROOT / approval["candidate_path"], PRIOR_PATH,
             prior().PRIOR, b281.PRIOR, b278.JOINT, b277.PRIOR, b277.prior().FIXTURES, b277.prior().END_OPERATOR]
    return {str(path.resolve().relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in files}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "native.json.gz")
    args = parser.parse_args()
    bound = input_hashes()
    modes = ("M+T", "M", "T", "neither")
    baselines = {mode: read_source(prepare(Case("baseline", mode))[0].immutable()) for mode in modes}
    rows = [run_case(case, i, baselines[case.mode]) for i, case in enumerate(CASES)]
    receipt = {
        "schema": "b285-native-v1", "cases": rows, "calibrations": [calibration(mode) for mode in modes],
        "projected_state_comparisons": whole_state_checks(rows),
        "matched_native_controls": matched_native_controls(rows),
        "bound_source_hashes": bound, "literal_birth_cap": CAP,
    }
    payload = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    tmp = args.output.with_suffix(".tmp")
    tmp.write_bytes(gzip.compress(payload, mtime=0))
    tmp.replace(args.output)
    print(sha256(args.output.read_bytes()).hexdigest(), args.output)


if __name__ == "__main__":
    main()
