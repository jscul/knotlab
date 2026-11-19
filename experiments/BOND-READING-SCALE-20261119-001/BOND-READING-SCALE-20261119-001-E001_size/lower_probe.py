"""Bounded weight panel with fixed routes between the split holders."""

import argparse
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from lower import EXTEND_ROUND, ROOT, Arrangement, bond_readings, next_stage, round_replay, start_audit


def core(shields, anchors, dense):
    tests = (2, 3)
    sites = tuple(range(4, 4 + shields))
    weak = tuple(range(4 + shields, 4 + shields + anchors))
    links = [(0, tests[0]), (1, tests[1])]
    groups = [0, 0]
    for a in weak:
        links.extend((x, a) for x in tests)
        groups.extend([int(a == weak[0]) + 1] * 2)
    for x in sites:
        links.extend([(0, x), (1, x)])
        groups.extend([3, 3])
        for a in weak if dense else weak[:1]:
            links.append((x, a))
            groups.append(1)
    phi = [links.index((1, tests[1])), links.index((0, tests[0]))]
    for i in range(2, len(links)):
        u, v = links[i]
        phi.append(links.index((u ^ 1, v)) if u in tests else i)
    new_link = links.index((sites[0], weak[0]))
    return len(sites) + len(weak) + 4, links, groups, phi, new_link


def panels(max_sites):
    for s in range(2, max_sites - 4):
        for a in range(1, min(3, max_sites - 4 - s) + 1):
            for dense in (True,) if a == 1 else (True, False):
                sites, links, classes, phi, unit = core(s, a, dense)
                material = []
                for spoke, strong, shield in product(range(1, 5), range(1, 5), range(1, 9)):
                    weights = [(spoke, 1, strong, shield)[kind] for kind in classes]
                    degree = [sum(w for (u, v), w in zip(links, weights) if j in (u, v)) for j in range(sites)]
                    if min(degree) >= 3 and sum(weights) + 5 < 149:
                        material.append((spoke, strong, shield, weights))
                yield (s, a, dense), (sites, links, phi, unit), material


def pack(sites, links, phi, profiles):
    data = [f"{sites} {len(links)} {len(profiles)}"]
    data.extend(f"{a} {b} {image}" for (a, b), image in zip(links, phi))
    data.extend(" ".join(map(str, profile[-1])) for profile in profiles)
    return data


def literal(sites, links, weights, type_map):
    rows = [[] for _ in range(sites)]
    names = []
    total = 0
    for (a, b), count in zip(links, weights, strict=True):
        name = list(range(total, total + count))
        names.append(name)
        rows[a].extend(name)
        rows[b].extend(name)
        total += count
    phi = {x: y for i, j in enumerate(type_map) for x, y in zip(names[i], names[j], strict=True)}
    return rows, names, phi


def exposed_quartet(stage, bonds, phi, mark_names):
    finite = sorted(bonds, key=lambda b: (b.bit_count(), b))
    through = {x: sum(1 << j for j, b in enumerate(finite) if b & stage.label_bits[x]) for x in mark_names}

    def marks_read(mark):
        candidates = through[mark[0]] & through[mark[1]] & through[mark[2]] & through[mark[3]]
        return finite[(candidates & -candidates).bit_length() - 1] if candidates else None

    best = None
    for mark in combinations(mark_names, 4):
        image = tuple(sorted(phi[x] for x in mark))
        if mark >= image:
            continue
        minima = [marks_read(mark), marks_read(image)]
        values = [x.bit_count() if x is not None else None for x in minima]
        if values[0] == values[1]:
            continue
        best = {"mark": mark, "image": image, "sizes": values,
                "minimizers": [None if b is None else [x for x in stage.labels if b & stage.label_bits[x]] for b in minima]}
        if None in values:
            return best
    return best


def grow_graft(geometry, weights):
    sites, links, type_map, unit = geometry
    rows, names, phi = literal(sites, links, weights, type_map)
    assert weights[unit] == 1 and phi[names[unit][0]] == names[unit][0]
    s, t = links[unit]
    assert not ({a for a, b in links if b == s} | {b for a, b in links if a == s}) & (
        {a for a, b in links if b == t} | {b for a, b in links if a == t})
    rows[t].remove(names[unit][0])
    rows[t].append(len(phi))
    start = Arrangement.parse(rows)
    assert start_audit(start)["census_open_legal"]
    seen = [start, next_stage(start)]
    first = round_replay(*seen)
    seen.append(next_stage(seen[-1]))
    second = round_replay(*seen[1:])
    assert all(len(record["taken"]) == 1 for record in first + second)
    phi |= {x: x for x in seen[-1].labels if x not in phi}
    for stage in seen[1:]:
        assert start_audit(stage)["census_open_legal"]
        assert all(phi[x] == x for j in stage.live for x in stage.stars[j])
    return seen, names, phi


def explicit_scheme(geometry, names, phi, stages):
    _sites, links, _type_map, unit = geometry
    # Take a fixed route with no incidence on the replaced distinction.
    route = links[unit][0] + 1
    mark = tuple(sorted([names[0][0], names[links.index((0, route))][0],
                         *(names[i][0] for i, (u, v) in enumerate(links) if u == route)]))
    image = tuple(sorted(phi[x] for x in mark))
    star = stages[-1].stars[0]
    support_mask = set(star)
    image_star = {phi[x] for x in support_mask}
    anchor = links[unit][1]
    flip = {names[0][0], names[links.index((0, route))][0],
            names[links.index((route, anchor))][0], names[links.index((2, anchor))][0]}
    assert all(len(flip & row) % 2 == 0 for stage in stages for row in stage.stars)
    assert len(flip & support_mask) == 2 and len(flip & image_star) == 1
    bonds = []
    for stage in stages:
        ends, adj, _outside = stage.holder_graph()
        route_index = stage.owners[names[links.index((0, route))][0]][1]
        h1_index = next(j for j in stage.owners[names[1][0]] if j != stage.owners[names[1][0]][-1])
        inside = {route_index, h1_index}
        bond = sorted(x for x, (a, b) in ends.items() if (a in inside) != (b in inside))
        for shore in (inside, set(range(len(adj))) - inside):
            a = next(iter(shore))
            visited = {a}
            pending = [a]
            while pending:
                u = pending.pop()
                others = {v for v in shore - visited if adj[u] & (1 << v)}
                visited.update(others)
                pending.extend(others)
            assert visited == shore
        assert set(image) <= set(bond)
        bonds.append(bond)
    return {"old_mark": mark, "image": image, "old_K": None, "image_K": len(bonds[0]),
            "minimizers_on_literal_stages": bonds, "allowed_flip": sorted(flip)}


def full_replay(geometry, weights):
    seen, names, phi = grow_graft(geometry, weights)
    unit = geometry[-1]
    result = []
    pure_labels = [x for xs in names for x in xs if x != names[unit][0]]
    exposure = explicit_scheme(geometry, names, phi, [seen[0]])
    for stage in seen[1:]:
        tables, bonds, equations = bond_readings(stage)
        assert all(tables[order][tuple(sorted(phi[x] for x in marks))] == value
                   for order in range(3) for marks, value in tables[order].items())
        star = seen[0].stars[0]
        imitation = sorted(phi[x] for x in star)
        assert sum(stage.label_bits[x] for x in star) in bonds
        assert sum(stage.label_bits[x] for x in imitation) not in equations
        a, b = (sum(stage.label_bits[x] for x in marks) for marks in (exposure["old_mark"], exposure["image"]))
        assert not any(a & block == a for block in bonds)
        assert min(block.bit_count() for block in bonds if b & block == b) == exposure["image_K"]
        result.append({"J": len(stage.stars), "n": len(stage.labels), "pair_entries": len(tables[1]),
                       "triple_entries": len(tables[2]), "old_bond": sorted(star), "image": imitation,
                       "direct_quartet": exposed_quartet(stage, bonds, phi, pure_labels)})
    return {"sizes": result, "map": sorted(phi.items()), "explicit_quartet": exposure,
            "support_history": [[sorted(row) for row in z.stars] for z in seen]}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--max-core-sites", type=int, default=13)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    sys.path.insert(0, str(ROOT / "experiments" / EXTEND_ROUND))
    specifications = list(panels(args.max_core_sites))
    tasks = [line for _, (sites, links, phi, _), p in specifications for line in pack(sites, links, phi, p)]
    with tempfile.TemporaryDirectory(prefix="bond-lower-probe-") as temp:
        tool = Path(temp) / "probe"
        subprocess.run(["c++", "-std=c++20", "-O3", str(Path(__file__).with_suffix(".cpp")), "-o", str(tool)], check=True)
        p = subprocess.run([str(tool)], input="\n".join(tasks)+"\n", text=True, capture_output=True, check=True)
    flags = iter(map(int, p.stdout.split()))
    accepted = []
    panel_rows = []
    for parameters, geometry, profiles in specifications:
        wins = [profile for profile in profiles if next(flags)]
        panel_rows.append({"shields_anchors_dense": parameters, "profiles": len(profiles),
                           "preservers": [p[:3] for p in wins]})
        accepted.extend((sum(weights), geometry[0], parameters, geometry, (spoke, strong, shield), weights)
                        for spoke, strong, shield, weights in wins)
    assert next(flags, None) is None
    witness = {}
    if accepted:
        for label, select in [("least_width", min(accepted)),
                              ("least_junctions", min(accepted, key=lambda p: (p[1], p[0], p[2], p[4])))]:
            width, sites, parameters, geometry, weights_profile, weights = select
            witness[label] = {"core_width": width, "core_junctions": sites, "shape": parameters,
                              "weights": weights_profile, "replay": full_replay(geometry, weights)}
    args.output.write_text(json.dumps({"witnesses": witness, "panels": panel_rows}, indent=2)+"\n")


if __name__ == "__main__":
    main()
