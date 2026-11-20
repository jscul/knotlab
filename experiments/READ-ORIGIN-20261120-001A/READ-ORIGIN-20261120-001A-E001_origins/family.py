"""Check all source interpretations of the connected unit-meeting path family."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
import json
from math import comb
from pathlib import Path
from random import Random
from tempfile import NamedTemporaryFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "family.json"
REPAIRS = ROOT / "experiments/SERIAL-REPAIRS-20261120-001A/SERIAL-REPAIRS-20261120-001A-E001_repairs/scaffolds.py"
ROUNDS = ROOT / "experiments/ROUND-FREE-20261119-001B/ROUND-FREE-20261119-001B-E001_serial/serial.py"
LAWS = ("parity", "nae")


def load(name, path):
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_present(controls, m):
    sites = tuple((i, m + i, 2 * m + i, 3 * m + i) for i in range(m))
    meetings = [(i, i + 1) for i in range(m - 1)]
    opens = {}
    for i, (s, u, v, x) in enumerate(sites):
        meetings += [(s, u), (s, v), (u, x)]
        opens.update({u: 1, v: 2 + int(i == 0), x: 2})
    stars = controls.wired_stars(4 * m, meetings, opens, multiplicity=1)
    assert len(set().union(*map(set, stars))) == 9 * m
    return stars, sites


def decode(literal, present):
    """Fixed order from incidence, with the unique three-loose holder at its first end."""
    owners = literal.owners(present)
    holds = Counter(row[0] for row in owners.values() if len(row) == 1)
    graph = literal.holder_graph(present)
    assert sum(len(row) for row in graph) == 2 * sum(len(row) == 2 for row in owners.values())
    assert set(literal.steps(graph, 0)) == set(range(len(present)))
    anchor, = (v for v, h in holds.items() if h == 3)
    center, = graph[anchor]
    spine = {v for v, row in enumerate(graph) if len(row) >= 3}
    assert center in spine
    prev = None
    sites = []
    while True:
        ends = graph[center] - spine
        u, = (v for v in ends if len(graph[v]) == 2)
        v, = (v for v in ends if len(graph[v]) == 1)
        x, = graph[u] - {center}
        assert graph[x] == {u} and not holds[center]
        assert (holds[u], holds[v], holds[x]) == (1, 2 + int(not sites), 2)
        sites.append((center, u, v, x))
        ahead = graph[center] & spine - {prev}
        if not ahead:
            break
        following, = ahead
        prev, center = center, following
    assert len(sites) == len(spine) and 4 * len(sites) == len(present)
    return tuple(sites)


def certify_source(controls, literal, rows, direct_rank=False):
    owners = literal.owners(rows)
    graph = literal.holder_graph(rows)
    exterior = len(rows)
    wired = [set(row) for row in graph] + [set()]
    for owner in owners.values():
        if len(owner) == 1:
            v, = owner
            wired[v].add(exterior)
            wired[exterior].add(v)
    assert all(3 <= len(row) <= 4 for row in rows)
    for omitted in range(len(rows)):
        hold = [row - {omitted} for row in wired]
        assert len(literal.steps(hold, exterior)) == len(rows)
    if direct_rank:
        assert controls.parity_profile(rows) == [1] * len(rows)
    with literal.nae_solver(rows) as solver:
        assert solver.solve()
        for row in rows:
            assert literal.sat_patterns(solver, row) == controls.declared_patterns(len(row), "nae")


def source_and_prefix(literal, present, sites, selected):
    omitted = {sites[i][3] for i in selected}
    source_ids = tuple(v for v in range(len(present)) if v not in omitted)
    source = tuple(present[v] for v in source_ids)
    widths = Counter(d for row in source for d in row)
    prefix = []
    accumulated = dict(zip(source_ids, source, strict=True))
    for i in sorted(selected):
        _, u, _, x = sites[i]
        spent, = (d for d in present[x] if d in present[u])
        other = tuple(d for d in present[x] if d != spent)
        assert widths[spent] == 1 and len(other) == 2 and all(widths[d] == 0 for d in other)
        assert sorted(v for v, row in accumulated.items() if spent in row) == [u]
        prefix.append((u, x, spent, other))
        widths.update(present[x])
        accumulated[x] = present[x]
    assert tuple(accumulated[i] for i in range(len(present))) == present
    assert {d: n for d, n in widths.items()} == {d: len(row) for d, row in literal.owners(present).items()}
    assert len(source) == len(present) - len(selected)
    assert len({d for row in source for d in row}) == 9 * len(sites) - 2 * len(selected)
    return source, source_ids, prefix


def first_roster(controls, operator, rows, source_ids, sites, selected):
    expected = Counter()
    vector = []
    for i, (_, u, v, x) in enumerate(sites):
        hu, hv = 1 + int(i in selected), 2 + int(i == 0)
        d = hu + hv - 2
        expected[(tuple(sorted((u, v))), d, d)] = 1
        vector.append(d)
        if i in selected:
            expected[((u,), 1, 2)] = 1
        else:
            expected[((x,), 1, 2)] = 2
        expected[((v,), hv - 1, 2)] = hv - 1
    for law in LAWS:
        result = controls.plan(operator, rows, law)
        assert result["status"] == "extend" and not result["implied"]
        actual = Counter((tuple(sorted(source_ids[p] for p in parents)), demand, fresh)
                         for parents, demand, fresh in zip(result["parents"], result["demand"],
                                                           result["fresh"], strict=True))
        assert actual == expected
    return tuple(vector), expected.total()


def marked_inputs(literal, present, sites):
    own = literal.owners(present)
    return [tuple(min(d for d in present[k] if len(own[d]) == 1) for k in (u, v))
            for _, u, v, _ in sites]


def check_present_births(controls, literal, present, sites, marks):
    cases = []
    for i, spent in enumerate(marks):
        budgets = (1 + int(i == 0), 2 + int(i == 0))
        laws = {}
        for law in LAWS:
            cases_for_law = []
            for fresh in budgets:
                _, checked = controls.actual_birth(literal, present, spent, fresh, law,
                                                   expected_input="free")
                cases_for_law.append(checked)
            laws[law] = cases_for_law
        cases.append({"parents": sites[i][1:3], "inputs": spent, "births_under_both_laws": laws})
    return cases


def complete_reference(controls, operator, literal, source, source_ids, prefix, present, sites, marks):
    earmarked = {
        tuple(sorted((u, v))): dict(zip((u, v), marked, strict=True))
        for (_, u, v, _), marked in zip(sites, marks, strict=True)
    }
    old_names = {d for row in source for d in row}
    output = {}
    for law in LAWS:
        roster = controls.plan(operator, source, law)
        already = Counter((u,) for u, _, _, _ in prefix)
        pools = defaultdict(set)
        for d, row in literal.owners(present).items():
            if len(row) == 1:
                pools[row[0]].add(d)
        stage = present
        new_supports = []
        for parents, fresh in zip(roster["parents"], roster["fresh"], strict=True):
            holders = tuple(sorted(source_ids[p] for p in parents))
            if already[holders]:
                assert fresh == 2
                already[holders] -= 1
                continue
            pinned = earmarked.get(holders)
            spent = tuple(pinned[v] if pinned is not None else min(pools[v]) for v in holders)
            for v, d in zip(holders, spent, strict=True):
                pools[v].remove(d)
            stage, checked = controls.actual_birth(literal, stage, spent, fresh, law, expected_input="free")
            new_supports.append((holders, (*checked["spent"], *checked["fresh"])))
        assert not any(already.values())
        owners = literal.owners(stage)
        assert all(len(owners[d]) == 2 for d in old_names)
        assert len(stage) == len(source) + len(roster["parents"])
        assert len(owners) == len(old_names) + sum(roster["fresh"])
        assert literal.steps(literal.holder_graph(stage), 0).keys() == set(range(len(stage)))
        if law == "nae":
            assert new_supports == output["parity"]["remaining_supports"]
        output[law] = {"remaining_supports": new_supports, "knots_after": len(stage),
                       "distinctions_after": len(owners)}
    return output


def raw_present(archived, present, sites, marks):
    expected = {tuple(sorted((u, v))) for _, u, v, _ in sites}
    old = archived.S.from_junctions(present)
    # With only unary earlier children, a prior-common-child guard still never excludes a pair.
    for all_newborn in (False, True):
        children = defaultdict(set)
        if all_newborn:
            for _, u, _, x in sites:
                children[u].add(x)
        moves, _, _ = archived.moves(old, children)
        assert set(moves) == expected
    demand = []
    for (_, _, _, x), spent in zip(sites, marks, strict=True):
        trial = archived.S.from_junctions(present)
        new = archived.new_junction(trial, spent)
        live = [j for j in range(len(trial.bits_of)) if trial.loose(j) or j == new]
        through = [set(row) for row in trial.groups_among(live) if new in row]
        assert through == [{x, new}]
        demand.append(len(through))
    return {"admitted_pairs": sorted(expected), "provisional_demand": demand,
            "ordinary_nonimplied_floor_fresh": [max(value, 1) for value in demand]}


def permutation_control(controls, operator, literal, present, sites):
    rng = Random(20261120573 + len(sites))
    holders = list(range(len(present)))
    names = list(range(9 * len(sites)))
    rng.shuffle(holders)
    rng.shuffle(names)
    encoded = [None] * len(present)
    for v, row in enumerate(present):
        encoded[holders[v]] = tuple(sorted(names[d] for d in row))
    encoded = tuple(encoded)
    decoded = decode(literal, encoded)
    assert decoded == tuple(tuple(holders[v] for v in site) for site in sites)
    chosen = frozenset(range(0, len(sites), 2))
    source, ids, _ = source_and_prefix(literal, encoded, decoded, chosen)
    certify_source(controls, literal, source)
    vector, births = first_roster(controls, operator, source, ids, decoded, chosen)
    expected = tuple(1 + int(i == 0) + int(i in chosen) for i in range(len(sites)))
    assert vector == expected
    return {"holder_permutation": holders, "distinction_permutation": names,
            "selected": sorted(chosen), "response_vector": vector, "first_births": births}


def measure(m, controls, operator, literal, archived):
    present, sites = make_present(controls, m)
    assert decode(literal, present) == sites
    marks = marked_inputs(literal, present, sites)
    typed_inputs = set(d for row in marks for d in row)
    by_size = {}
    total = 0
    local_checks = 0
    prior_children = 0
    selected_records = []
    for k in range(m + 1):
        distinct = set()
        total_roster = 0
        for items in combinations(range(m), k):
            selected = frozenset(items)
            source, ids, prefix = source_and_prefix(literal, present, sites, selected)
            certify_source(controls, literal, source, direct_rank=(m <= 6 or not items or k == m))
            vector, roster = first_roster(controls, operator, source, ids, sites, selected)
            assert not (typed_inputs & {birth[2] for birth in prefix})
            distinct.add(vector)
            total += 1
            local_checks += len(source)
            prior_children += len(prefix)
            total_roster += roster
            if not items or items == tuple(range(k)):
                selected_records.append({"selected": items, "source_holder_ids": ids,
                                         "literal_prefix": prefix, "reference_fresh": vector,
                                         "complete_first_reference": complete_reference(
                                             controls, operator, literal, source, ids, prefix, present, sites, marks
                                         )})
        count = comb(m, k)
        assert len(distinct) == count
        by_size[str(k)] = {"source_knots": 4 * m - k, "source_distinctions": 9 * m - 2 * k,
                           "distinct_vectors": count, "first_births_each_law": total_roster}
    assert total == 1 << m
    return {"present_stars": present, "ordered_sites": sites,
            "source_counts": by_size, "source_interpretations": total,
            "local_source_projections_per_law": local_checks,
            "literal_prefix_attachments": prior_children,
            "ready_marked_queries_per_law": total * m,
            "representative_prefixes": selected_records,
            "present_birth_projection_checks": check_present_births(controls, literal, present, sites, marks),
            "raw_current_control": raw_present(archived, present, sites, marks),
            "recoding": permutation_control(controls, operator, literal, present, sites)}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--max-sites", type=int, choices=range(2, 11), default=10)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    controls = load("old_serial_scaffold", REPAIRS)
    operator = controls.load("complete_round_reference", controls.ORDINARY / "end_operator.py")
    literal = controls.load("actual_relation_reader", controls.BOND / "scaffolds.py")
    archived = load("raw_serial_reference", ROUNDS)
    families = {str(m): measure(m, controls, operator, literal, archived) for m in range(2, args.max_sites + 1)}
    result = {
        "families": families, "law_names": LAWS,
        "weights": "One per source interpretation of each named present. No population weighting.",
        "total_source_interpretations": sum(row["source_interpretations"] for row in families.values()),
        "total_local_source_projections_per_law": sum(
            row["local_source_projections_per_law"] for row in families.values()
        ),
        "total_marked_queries_per_law": sum(row["ready_marked_queries_per_law"] for row in families.values()),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.out.parent, delete=False) as out:
        temporary = Path(out.name)
        json.dump(result, out, separators=(",", ":"))
        out.write("\n")
    temporary.replace(args.out)


if __name__ == "__main__":
    main()
