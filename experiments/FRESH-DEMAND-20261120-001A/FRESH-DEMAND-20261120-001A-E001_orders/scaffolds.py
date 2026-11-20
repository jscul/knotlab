"""Exact parity and not-all-equal controls for the fixed-parent demand family."""

from argparse import ArgumentParser
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from pathlib import Path
from random import Random
from tempfile import NamedTemporaryFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "scaffolds.json"
OLD = (ROOT / "experiments" / "BOND-CLOSURE-20261120-001A"
       / "BOND-CLOSURE-20261120-001A-E001_proposals")
U, V, S, A, Z = range(5)
LAWS = ("parity", "nae")


def load(role, name):
    spec = spec_from_file_location(role, OLD / name)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def family(m, t, reserve=2, multiplicity=None, destination=None):
    """Packets buy one more live holder each, with the other packets at Z."""
    assert m >= 2 and 2 <= t <= m + 1 and reserve >= 2
    assert destination is None or (m == 2 and destination in ("Z", "W", "B", "deleted"))
    q = m - 1
    branches = [(5 + 2 * i, 6 + 2 * i) for i in range(q)]
    meetings = [(U, S), (V, S), (S, A), (A, Z)]
    for w, b in branches:
        meetings.extend(((S, w), (w, b), (b, A)))
    exterior = 5 + 2 * q
    width = multiplicity if multiplicity is not None else (q + 2) * m + reserve + 1
    assert width >= 2
    links = [(i, j) for i, j in meetings for _ in range(width)]
    classes = {"B_U": tuple(range(width)), "B_V": tuple(range(width, 2 * width))}
    for parent, label in zip((U, V), ("L_U", "L_V"), strict=True):
        lo = len(links)
        links.extend([(parent, exterior)] * m)
        classes[label] = tuple(range(lo, len(links)))
    links.extend([(Z, exterior)] * reserve)
    packets = []
    for i, (w, b) in enumerate(branches):
        if destination == "deleted":
            continue
        holder = w if i < t - 2 else Z
        if destination is not None:
            holder = {"Z": Z, "W": w, "B": b}[destination]
        lo = len(links)
        links.extend([(holder, exterior)] * m)
        packets.append((holder, tuple(range(lo, len(links)))))
    return tuple(links), exterior, width, classes, packets


def minimal_size(bonds, marks):
    return min((len(bond) for bond in bonds if marks <= bond), default=None)


def expected_deck(selection, law, m, M, T):
    bu, bv, lu, lv = (name in selection for name in ("B_U", "B_V", "L_U", "L_V"))
    if law == "nae":
        if not (bu or lu) or not (bv or lv):
            return M + m
        return (m + 2) * M if not (lu or lv) else None
    if not (bu or bv):
        return T
    if bu and bv:
        return None if lu or lv else 2 * M + T - 2 * m
    if lu and lv:
        return None
    if (bu and lv) or (bv and lu):
        return M + T - m
    return M + m


def group_checks(older, local, stars, expected, focus=(U, V), outside_pair=None):
    end = older.from_stars(stars)
    end_graph = older.neighbors(end)
    first_groups = older.proposals(end)
    assert focus in first_groups and all(len(group) == 2 for group in first_groups)
    holder_graph = local.holder_graph(stars)
    assert all(len(holder_graph[a] & holder_graph[b]) <= 1 for a, b in combinations(end.opens, 2))
    assert sum(end.opens.values()) >= 2
    siblings = set(focus) | set.intersection(*(end_graph[parent] for parent in focus))
    assert all(end.opens[parent] == end.opens[focus[0]] for parent in siblings)
    assert expected == 2 * end.opens[focus[0]] - len(siblings)
    witnessed = [block for block in end.blocks if set(focus) <= set(block)]
    assert len(witnessed) == 1 and set(witnessed[0]) == siblings
    visible_holders = {focus[0]} | end_graph[focus[0]]
    end_local = type(end)({v: end.opens[v] for v in visible_holders},
                          tuple(visible_holders.intersection(row) for row in end.blocks))
    assert set(end_local.opens) == siblings

    by_law = {}
    for law in LAWS:
        growth = older.step(end, law)
        assert growth.status == "extend" and not growth.implied and all(growth.fresh)
        assert growth.parents.count(focus) == 1
        i = growth.parents.index(focus)
        assert growth.fresh[i] == growth.demand[i] == expected
        next_parents = growth.parents
        next_triangles = {
            frozenset(next_parents.index(tuple(sorted(pair))) for pair in (focus, (focus[0], w), (focus[1], w)))
            for w in siblings - set(focus)
        }
        residual_pairs = {frozenset((i, j)) for j, row in enumerate(next_parents)
                          if len(row) == 1 and row[0] in focus}
        actual = {frozenset(group) for group in older.proposals(growth.end) if i in group}
        assert actual == next_triangles | residual_pairs
        visible = older.step(end_local, law)
        assert visible.fresh[visible.parents.index(focus)] == expected
        future_graph = older.neighbors(growth.end)
        assert len(local.steps(end_graph, focus[0])) < len(end_graph)
        assert len(local.steps(future_graph, i)) < len(future_graph)
        by_law[law] = {"demand": growth.demand[i], "fresh": growth.fresh[i],
                       "arity": len(focus) + growth.fresh[i], "all_first_births": len(growth.parents),
                       "successor_groups_through_birth": [
                           [next_parents[j] for j in sorted(group)]
                           for group in sorted(actual, key=lambda row: (len(row), sorted(row)))
                       ]}
        if outside_pair is not None:
            j = growth.parents.index(outside_pair)
            assert growth.demand[j] == growth.fresh[j] == 2
            by_law[law]["outside_BZ"] = {"demand": growth.demand[j], "fresh": growth.fresh[j],
                                        "arity": 2 + growth.fresh[j], "loose_each": 2, "owed_each": 1}
    return end, by_law


def measure(older, local, m, t, radius, *, reserve, literal=False, destination=None):
    links, exterior, M, classes, packets = family(
        m, t, reserve=reserve, multiplicity=2 if literal else None, destination=destination
    )
    stars = older.stars_of(links, exterior)
    T = sum(v == exterior for _, v in links)
    assert all(stars) and older.lawful(links, exterior)
    assert len(set(map(frozenset, stars))) == exterior
    assert all(not a < b for a in map(frozenset, stars) for b in map(frozenset, stars))
    written = set(stars)
    if literal:
        actual = local.all_bonds(local.projection_fragments(stars))
        assert actual == written
        literal_check = local.sat_checks(stars, actual)
    else:
        assert M > T and T - 1 > radius
        literal_check = None

    parity = older.all_bonds(links, exterior)
    assert written <= set(map(tuple, map(sorted, parity)))
    nae = list(map(frozenset, written))
    minima = min(map(len, parity)), min(map(len, nae))
    assert minima[1] >= M + 2
    if not literal:
        assert minima[0] == T and minima[1] - 1 > radius
    decks = {law: {} for law in LAWS}
    for k in range(1, len(classes) + 1):
        for query in combinations(classes, k):
            marks = {classes[name][0] for name in query}
            for law, bonds in (("parity", parity), ("nae", nae)):
                cost = minimal_size(bonds, marks)
                if law == "nae" or not literal:
                    assert cost == expected_deck(query, law, m, M, T)
                decks[law]["+".join(query)] = cost

    active = t if destination is None else 3 if destination == "W" else 2
    outside_pair = (Z, 6) if destination == "B" else None
    end, birth = group_checks(older, local, stars, 2 * m - active, outside_pair=outside_pair)
    owners = local.owners(stars)
    distinct = {d: set().union(*(stars[k] for k in row)) - {d} for d, row in owners.items()}
    holder = local.holder_graph(stars)
    end_graph = older.neighbors(end)
    roots = (classes["L_U"][0], classes["L_V"][0])
    packet_readings = []
    for carrier, packet in packets:
        ordinary = [local.steps(holder, u)[carrier] for u in (U, V)]
        through_knots = [local.steps(distinct, a)[packet[0]] for a in roots]
        assert through_knots == [value + 1 for value in ordinary]
        witness = [local.steps(end_graph, u).get(carrier) for u in (U, V)]
        packet_readings.append({"carrier": carrier, "holder_steps": ordinary,
                                "distinction_steps": through_knots, "end_steps": witness,
                                "root_to_packet_bond_sizes": {
                                    law: [minimal_size(bonds, {a, packet[0]}) for a in roots]
                                    for law, bonds in (("parity", parity), ("nae", nae))
                                }})
    output = {"m": m, "live_S_block": active, "source_knots": exterior,
              "ordinary_multiplicity": M, "loose_total": T, "physical_width": len(links),
              "literal_stars": stars, "marked_inputs": roots,
              "parents": (stars[U], stars[V]), "classes": classes,
              "end_opens": end.opens, "end_witnessed_sets": end.blocks,
              "bonds_by_law": {"parity": len(parity), "nae": len(nae)},
              "minimum_bond_sizes": dict(zip(LAWS, minima, strict=True)), "bond_decks": decks,
              "birth": birth, "literal_nae_control": literal_check, "packet_readings": packet_readings}
    if not literal:
        output["radius_checked"] = radius
    return output


def relabel_check(older, local, row):
    rng = Random(20261120479)
    stars = row["literal_stars"]
    ids = list(range(len(stars)))
    names = list(range(row["physical_width"]))
    rng.shuffle(ids)
    rng.shuffle(names)
    new = [None] * len(ids)
    for k, star in enumerate(stars):
        new[ids[k]] = tuple(sorted(names[d] for d in star))
    focus = tuple(sorted((ids[U], ids[V])))
    _, births = group_checks(older, local, new, row["birth"]["nae"]["fresh"], focus)
    assert all(births[law]["arity"] == row["birth"][law]["arity"] for law in LAWS)
    encoded_owners = local.owners(new)
    links = [tuple(encoded_owners[d]) if len(encoded_owners[d]) == 2
             else (*encoded_owners[d], len(ids)) for d in range(len(names))]
    families = {"parity": older.all_bonds(links, len(ids)), "nae": list(map(frozenset, new))}
    for law, bonds in families.items():
        for query, size in row["bond_decks"][law].items():
            marks = {names[row["classes"][name][0]] for name in query.split("+")}
            assert minimal_size(bonds, marks) == size
    return {"physical_name_permutation": names, "holder_permutation": ids}


def failure_controls(older, local):
    links, exterior, M, _, _ = family(2, 3, multiplicity=2)
    underfunded = list(links)
    underfunded.remove((U, exterior))
    assert older.lawful(underfunded, exterior)
    end = older.from_stars(older.stars_of(underfunded, exterior))
    assert all(older.step(end, law).status == "stall" for law in LAWS)
    w, b = 5, 6
    links, exterior, _, _, _ = family(2, 2, multiplicity=M)
    defective = [pair for pair in links if pair != (w, b)]
    assert not older.lawful(defective, exterior)
    source = older.stars_of(defective, exterior)
    assert set(source[w]) < set(source[S])
    pinned = [(d + 1) if d not in source[w] else -(d + 1) for d in source[S]]
    with local.nae_solver(source) as solver:
        assert solver.solve() and not solver.solve(assumptions=pinned)
    return {"underfunded_refused_both_laws": True, "nonconstant_word_on_unlawful_star_rejected": True}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    older, local = load("old_parity_cuts", "radius_check.py"), load("old_nae_bonds", "scaffolds.py")
    radius = 32
    exact = {}
    for m in range(2, 6):
        reserve = max(2, radius + 2 - (m + 1) * m)
        rows = [measure(older, local, m, t, radius, reserve=reserve) for t in range(2, m + 2)]
        baseline = rows[0]
        for row in rows:
            for field in ("parents", "classes", "physical_width", "loose_total", "bond_decks"):
                assert row[field] == baseline[field]
        assert {r["birth"]["parity"]["fresh"] for r in rows} == set(range(m - 1, 2 * m - 1))
        exact[str(m)] = rows
    controls = {place: measure(older, local, 2, 2, 0, reserve=2, destination=place)
                for place in ("W", "Z", "B", "deleted")}
    assert all(controls[k]["bond_decks"] == controls["Z"]["bond_decks"] for k in ("W", "B"))
    assert controls["deleted"]["bond_decks"]["nae"] == controls["Z"]["bond_decks"]["nae"]
    assert controls["deleted"]["bond_decks"]["parity"] != controls["Z"]["bond_decks"]["parity"]
    assert controls["B"]["birth"]["nae"]["outside_BZ"] == {
        "demand": 2, "fresh": 2, "arity": 4, "loose_each": 2, "owed_each": 1
    }
    for place, expected in (("W", (2, 3, 1)), ("Z", (3, 4, None)), ("B", (3, 4, None))):
        read, = controls[place]["packet_readings"]
        assert tuple(read[key][0] for key in ("holder_steps", "distinction_steps", "end_steps")) == expected
    literal = [measure(older, local, m, t, 0, reserve=2, literal=True)
               for m in (2, 3) for t in range(2, m + 2)]
    literal += [measure(older, local, 2, 2, 0, reserve=2, literal=True, destination=place)
                for place in ("B", "deleted")]
    receipt = {"fixed_parent_families": exact, "displacement_controls": controls,
               "independent_nae_literal_small_meetings": literal,
               "relabel": relabel_check(older, local, exact["3"][-1]),
               "negative_controls": failure_controls(older, local),
               "bond_deck_units": "Exact least support size. Null means no containing bond.",
               "coverage": {"same_deck_family_starts": 14, "displacement_starts": 4, "literal_nae_starts": 7,
                            "nonempty_parent_class_queries_per_start_per_law": 15}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.out.parent, delete=False) as out:
        temporary = Path(out.name)
        json.dump(receipt, out, separators=(",", ":"))
        out.write("\n")
    temporary.replace(args.out)


if __name__ == "__main__":
    main()
